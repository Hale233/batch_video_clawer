#将指纹库与在线指纹进行清理（去除音频块），标注，并构建为类，用于后续的匹配算法
from re import X
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

#记录流信息，分别是：指纹序列、五元组序列、视频URL、mitm文件路径(用于验证)
class Video_flow():
    def __init__(self,finger_list,tuple_list,video_url='',mitm_path='',streamID=-1,state_transition_matrix='') -> None:
        #指纹列表
        self.finger_list=finger_list
        #传输使用的五元组列表
        self.tuple_list=tuple_list
        #视频对应的URL
        self.video_url=video_url
        self.mitm_path=mitm_path
        self.state_transition_matrix=state_transition_matrix
        self.streamID=streamID

#记录原始流、ground truth流、预测流之间的关系
class O_g_p_relation():
    def __init__(self,original_stream=None,ground_truth_stream=None,pred_stream=None,zero_prob=0) -> None:
        #在线指纹
        self.original_stream=original_stream
        #对应的真实指纹
        self.ground_truth_stream=ground_truth_stream
        #算法匹配指纹
        self.pred_stream=pred_stream
        self.zero_prob=zero_prob

class data_Process():
    def __init__(self,online_file,offline_file,offline_audio_thd=700000) -> None:
        self.online_file=online_file
        self.offline_file=offline_file
        self.offline_audio_thd=offline_audio_thd
        self.offline_chunk_list=[]
        self.online_chunk_list=[]
        self.o_g_p_relation_list=[]
        self.get_offline_finger()
        self.get_online_finger()
        self.small_chunk_clean(self.online_chunk_list,offline_audio_thd*1.00135177+1119)
        self.small_chunk_clean(self.offline_chunk_list,offline_audio_thd)
        self.stream_label_match()

    #获取离线指纹
    def get_offline_finger(self):
        offline_file=open(self.offline_file,mode='r',encoding='utf-8')
        offline_data=offline_file.read()
        offline_datas=offline_data.split('\n')
        streamID=-1
        for lines in offline_datas:
            if lines=='':
                continue
            vals=lines.split(',')
            video_url=vals[3]#视频URL
            stream_type=vals[2]#video or audio
            finger=vals[4].split('/')[1:]#指纹
            tuples=vals[5].split('/')[1:]#五元组
            mitm_path=vals[0]#mitm_path路径
            if stream_type=='video':
                streamID +=1
                video_flow=Video_flow(list(map(int,finger)),tuples,video_url,mitm_path,streamID)
                self.offline_chunk_list.append(video_flow)
            if stream_type=='audio':
                pass
    
    #获取在线指纹
    def get_online_finger(self):
        online_file=open(self.online_file,mode='r',encoding='utf-8')
        online_data=online_file.read()
        online_datas=online_data.split('\n')
        for lines in online_datas:
            if lines=='':
                continue
            vals=lines.split(',')
            finger=vals[1].split('/')[:-1]#指纹
            tuples=[vals[0]]#五元组
            video_flow=Video_flow(list(map(int,finger)),tuples)
            self.online_chunk_list.append(video_flow)
    
    #过滤掉指纹序列中小于阈值的块
    def small_chunk_clean(self,chunk_list,audio_thd):
        for chunk in chunk_list:
            clean_finger=[]
            for val in chunk.finger_list:
                if val>audio_thd:
                    clean_finger.append(val)
            chunk.finger_list=clean_finger

    #获取待匹配流的真实标签
    def stream_label_match(self):
        j=0
        for online_chunk in self.online_chunk_list:
            tmp=[online_chunk]
            for offline_chunk in self.offline_chunk_list:
                for offline_tuples in offline_chunk.tuple_list:
                    if online_chunk.tuple_list[0]==offline_tuples:
                        o_g_p_relation=O_g_p_relation(original_stream=online_chunk,ground_truth_stream=offline_chunk)
                        tmp.append(offline_chunk)#用于debug分析
            #验证是否出现在线流五元组对应多个目标流五元组的情况,仅记录一对一的情况
            if len(tmp)==2:
                self.o_g_p_relation_list.append(o_g_p_relation)
                #统计仅用一条流传输视频的数量
                #if len(o_g_p_relation.ground_truth_stream.tuple_list)==1:
                #    j +=1
        #print (len(self.offline_chunk_list))
        #print (j)

    #分析音视频块的大小分布
    def chunk_plt(self,video_fingers,audio_fingers):
        offline_file=open(self.offline_file,mode='r',encoding='utf-8')
        offline_data=offline_file.read()
        offline_datas=offline_data.split('\n')
        video_fingers=[]
        audio_fingers=[]
        for lines in offline_datas:
            if lines=='':
                continue
            vals=lines.split(',')
            stream_type=vals[2]#video or audio
            finger=vals[3].split('/')[1:]#指纹
            #tuples=vals[4].split('/')[1:]#五元组
            if stream_type=='video':
                video_fingers +=finger
            if stream_type=='audio':
                audio_fingers +=finger
        video_fingers=list(map(int,video_fingers))
        audio_fingers=list(map(int,audio_fingers))
        video_fingers.sort()
        audio_fingers.sort()
        X_v=np.arange(0,len(video_fingers),1)
        X_a=np.arange(0,len(audio_fingers),1)
        plt.plot(X_v,video_fingers)
        plt.plot(X_a,audio_fingers)
        plt.show()
    
    #分析指纹库的冲突概率
    def conflict_prob_analysis(self,win_size,bins_count):
        url_dict={}
        index_i=-1
        video_chunk_size_max=2200000.0
        video_chunk_size_min=self.offline_audio_thd
        bin_size=(video_chunk_size_max-video_chunk_size_min)/bins_count

        for offline_chunk in self.offline_chunk_list:
            index_i +=1
            #URL去重
            if offline_chunk.video_url in url_dict:
                continue
            else :
                url_dict[offline_chunk.video_url]=1
            bin_relation_que=deque()
            state_transition_dict={}
            for chunk in offline_chunk.finger_list:
                #离线 等分分桶
                #获得桶的编号
                if chunk>=video_chunk_size_max:
                    bin_index_cur=bins_count-1
                elif chunk<=video_chunk_size_min:
                    bin_index_cur=0
                else:
                    bin_index_cur=int((chunk-video_chunk_size_min)/bin_size)
                #记录转移序列
                bin_relation_que.append(bin_index_cur)
                if len (bin_relation_que)<win_size:
                    continue
                relation_key=''
                for val in bin_relation_que:
                    relation_key +=str(val)+'-'
                if relation_key not in state_transition_dict:
                    state_transition_dict[relation_key]=1
                else:
                    state_transition_dict[relation_key] +=1
                bin_relation_que.popleft()
            self.offline_chunk_list[index_i].state_transition_matrix=state_transition_dict
        '''
        conflict_count=0
        all_count=0
        for cur_chunk in self.offline_chunk_list:
            cur_state_transition_matrix=cur_chunk.state_transition_matrix
            if cur_state_transition_matrix=='' or len(cur_state_transition_matrix)==0:
                continue
            all_count +=1
            match_count=0
            for offline_chunk in self.offline_chunk_list:
                for on_key,on_val in cur_state_transition_matrix.items():
                    if on_key in offline_chunk.state_transition_matrix:
                        match_count +=1
                        break
            if match_count>=2:
                conflict_count +=1
        '''
        conflict_count=0
        all_count=0
        for cur_chunk in self.offline_chunk_list:
            cur_state_transition_matrix=cur_chunk.state_transition_matrix
            if cur_state_transition_matrix=='' or len(cur_state_transition_matrix)==0:
                continue
            for cur_key,cur_val in cur_state_transition_matrix.items():
                all_count +=1
                match_count=0
                for offline_chunk in self.offline_chunk_list:
                    if cur_key in offline_chunk.state_transition_matrix:
                        match_count +=1
                        continue
                if match_count>=2:
                    conflict_count +=1
        return all_count,conflict_count

if __name__ == '__main__':
    offline_audio_thd=700000
    finger_data=data_Process('./data/chunk_list/online_encrypted_finger_seq.csv','./data/chunk_list/finger_store_3.csv',offline_audio_thd)
    bin_count=[100,200,300,400,500,600,700,800,900,1000,2000,3000,4000,5000]
    for i in range(1,11,1):
        for j in bin_count:
            all_count,conflict_count=finger_data.conflict_prob_analysis(i,j)
            print ("{},{},{},{},{}".format(i,j,all_count,conflict_count,1-(conflict_count/all_count)))
    