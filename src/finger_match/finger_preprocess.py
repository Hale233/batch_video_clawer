from re import X
import matplotlib.pyplot as plt
import numpy as np

#记录流信息，分别是：指纹序列、五元组序列、视频URL、mitm文件路径(用于验证)
class Video_flow():
    def __init__(self,finger_list,tuple_list,video_url='',mitm_path='',state_transition_matrix='') -> None:
        self.finger_list=finger_list
        self.tuple_list=tuple_list
        self.video_url=video_url
        self.mitm_path=mitm_path
        self.state_transition_matrix=state_transition_matrix

#记录原始流、ground truth流、预测流之间的关系
class O_g_p_relation():
    def __init__(self,original_stream=None,ground_truth_stream=None,pred_stream=None) -> None:
        self.original_stream=original_stream
        self.ground_truth_stream=ground_truth_stream
        self.pred_stream=pred_stream

class data_Process():
    def __init__(self,online_file,offline_file,audio_thd=600000) -> None:
        self.online_file=online_file
        self.offline_file=offline_file
        self.audio_thd=audio_thd
        self.offline_chunk_list=[]
        self.online_chunk_list=[]
        self.o_g_p_relation_list=[]
        self.get_offline_finger()
        self.get_online_finger()
        self.small_chunk_clean(self.online_chunk_list,audio_thd+10000)
        self.small_chunk_clean(self.offline_chunk_list,audio_thd)
        self.stream_label_match()

    #获取离线指纹
    def get_offline_finger(self):
        offline_file=open(self.offline_file,mode='r',encoding='utf-8')
        offline_data=offline_file.read()
        offline_datas=offline_data.split('\n')
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
                video_flow=Video_flow(list(map(int,finger)),tuples,video_url,mitm_path)
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

#finger_data=data_Process('/Users/hale/PycharmProjects/batch_video_clawer/data/result/online_encrypted_finger.csv','/Users/hale/PycharmProjects/batch_video_clawer/data/result/finger_store.csv')
