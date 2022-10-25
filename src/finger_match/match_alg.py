from nis import match
import queue
from symbol import small_stmt
from collections import deque
from numpy import matrix
from finger_preprocess import data_Process,Video_flow,O_g_p_relation

class Match_alg():
    def __init__(self,online_file,offline_file) -> None:
        self.offline_chunk_list=[]
        self.online_chunk_list=[]
        self.video_chunk_size_max=2200000.0
        self.video_chunk_size_min=600000.0
        #获取指纹数据
        finger_data=data_Process(online_file,offline_file)
        self.offline_chunk_list=finger_data.offline_chunk_list
        self.online_chunk_list=finger_data.online_chunk_list
        self.o_g_p_relation_list=finger_data.o_g_p_relation_list
    
    #滑动窗口匹配
    def slide_wind(self,wind_size):
        index=-1
        small_count=0
        for o_g_p_relation in self.o_g_p_relation_list:
            index +=1
            # 仅统计用一条流传输的视频
            if len(o_g_p_relation.ground_truth_stream.tuple_list)!=1:
                continue
            if len(o_g_p_relation.original_stream.finger_list)<wind_size:
                small_count +=1
                continue
            min_dis=99999999999
            min_chunk=None
            online_chunk=o_g_p_relation.original_stream
            for offline_chunk in self.offline_chunk_list:
                if len(offline_chunk.finger_list)<wind_size:# or len(offline_chunk.finger_list)<len(online_chunk.finger_list):
                    continue
                for i in range(0,(len(offline_chunk.finger_list)-wind_size)):
                #for i in range(0,(len(offline_chunk.finger_list)-len(online_chunk.finger_list)+1)):
                    cur_dis=0
                    for j in range(0,wind_size):
                        #在线一定是要大于离线指纹库的
                        if online_chunk.finger_list[j]<offline_chunk.finger_list[j+i]:
                            cur_dis=99999999999
                            break
                        cur_dis +=abs(online_chunk.finger_list[j]-offline_chunk.finger_list[j+i])
                    if cur_dis<min_dis:
                        min_dis=cur_dis
                        min_chunk=offline_chunk
            if min_chunk == None:
                #print("error")
                continue
            self.o_g_p_relation_list[index].pred_stream=min_chunk
        print(small_count)
    
    #一阶马尔可夫
    def markov_1order(self,bins_count):
        #计算离线指纹的一阶概率转移矩阵
        index_i=-1
        bin_size=(self.video_chunk_size_max-self.video_chunk_size_min)/bins_count
        for offline_chunk in self.offline_chunk_list:
            res_matrix=[[0]*bins_count for i in range(0,bins_count)]
            index_i +=1
            bin_index_pre=-1
            for chunk in offline_chunk.finger_list:
                #等分分桶
                if chunk>=self.video_chunk_size_max:
                    bin_index_cur=bins_count-1
                elif chunk<=self.video_chunk_size_min:
                    bin_index_cur=0
                else:
                    bin_index_cur=int((chunk-self.video_chunk_size_min)/bin_size)

                if bin_index_pre==-1:
                    bin_index_pre=bin_index_cur
                    continue
                #print(bin_index_pre,bin_index_cur)
                res_matrix[bin_index_pre][bin_index_cur] +=1
                bin_index_pre=bin_index_cur
            self.offline_chunk_list[index_i].state_transition_matrix=res_matrix
        
        #在线指纹匹配
        index_j=-1
        for o_g_p_relation in self.o_g_p_relation_list:
            index_j +=1
            online_chunk=o_g_p_relation.original_stream
            bin_index_pre=-1
            online_metrix_index=[]  #后续可用字典进一步压缩
            #构建在线的转移矩阵索引
            for on_chunk in online_chunk.finger_list:
                if on_chunk>=self.video_chunk_size_max:
                    bin_index_cur=bins_count-1
                elif on_chunk<=self.video_chunk_size_min:
                    bin_index_cur=0
                else:
                    bin_index_cur=int((on_chunk-self.video_chunk_size_min)/bin_size)
                
                if bin_index_pre==-1:
                    bin_index_pre=bin_index_cur
                    continue
                online_metrix_index.append([bin_index_pre,bin_index_cur])
                bin_index_pre=bin_index_cur
        
            #找到最大的转移概率指纹
            max_prob=0
            target_chunk=None
            for offline_chunk in self.offline_chunk_list:
                cur_prob=0
                off_chunk_len=len(offline_chunk.finger_list)-1
                #离线小于5块不进行匹配
                if off_chunk_len<5:
                    continue
                #统计转移概率
                for i in range(0,len(online_metrix_index)):
                    #print (online_metrix_index[i][0],online_metrix_index[i][1])
                    cur_prob +=offline_chunk.state_transition_matrix[online_metrix_index[i][0]][online_metrix_index[i][1]]
                cur_prob=cur_prob/off_chunk_len
                if cur_prob>max_prob:
                    max_prob=cur_prob
                    target_chunk=offline_chunk
            if target_chunk == None:
                #print("error")
                continue
            self.o_g_p_relation_list[index_j].pred_stream=target_chunk

    #高阶马尔可夫
    #bins_count:桶个数、orders:马尔可夫的阶数、win_size:取在线指纹的前若干个块进行匹配
    def markov_hight_order(self,bins_count,orders,win_size):
        orders +=1
        #计算离线指纹的order阶概率转移矩阵
        index_i=-1
        bin_size=(self.video_chunk_size_max-self.video_chunk_size_min)/bins_count
        for offline_chunk in self.offline_chunk_list:
            #当序列小于多少时不参与匹配

            #用一个队列记录n阶的桶关系
            bin_relation_que=deque()
            index_i +=1
            state_transition_dict={}
            for chunk in offline_chunk.finger_list:
                #等分分桶
                #获得桶的编号
                if chunk>=self.video_chunk_size_max:
                    bin_index_cur=bins_count-1
                elif chunk<=self.video_chunk_size_min:
                    bin_index_cur=0
                else:
                    bin_index_cur=int((chunk-self.video_chunk_size_min)/bin_size)
                #记录转移序列
                bin_relation_que.append(bin_index_cur)
                if len (bin_relation_que)<orders:
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
        
        #在线指纹匹配
        index_j=-1
        error_count=0
        #长度太短而不参与匹配的在线指纹数量
        online_short_count=0
        for o_g_p_relation in self.o_g_p_relation_list:
            index_j +=1
            online_chunk=o_g_p_relation.original_stream
            bin_index_pre=-1
            online_bin_relation_que=deque()
            online_state_transition_dict={}
            #长度太短而不参与匹配
            if len(online_chunk.finger_list)<orders + 1:
                online_short_count +=1
                continue
            #构建在线的转移关系字典
            on_chunk_count=0
            for on_chunk in online_chunk.finger_list:
                if on_chunk>=self.video_chunk_size_max:
                    bin_index_cur=bins_count-1
                elif on_chunk<=self.video_chunk_size_min:
                    bin_index_cur=0
                else:
                    bin_index_cur=int((on_chunk-self.video_chunk_size_min)/bin_size)
                
                #记录转移序列
                online_bin_relation_que.append(bin_index_cur)
                if len (online_bin_relation_que)<orders:
                    continue
                relation_key=''
                for val in online_bin_relation_que:
                    relation_key +=str(val)+'-'
                if relation_key not in online_state_transition_dict:
                    online_state_transition_dict[relation_key]=1
                else:
                    online_state_transition_dict[relation_key] +=1
                online_bin_relation_que.popleft()
                #控制在线匹配指纹的长度
                on_chunk_count +=1
                if on_chunk_count>=win_size:
                    break
        
            #找到最大的转移概率指纹
            max_prob=0
            target_chunk=None
            for offline_chunk in self.offline_chunk_list:
                cur_prob=0
                off_chunk_len=len(offline_chunk.finger_list)-1
                #离线小于5块不进行匹配
                if off_chunk_len<5:
                    continue
                #当阶数大于指纹长度时会出现没有转移状态的情况，此时直接跳过
                if len(offline_chunk.state_transition_matrix)==0:
                    continue
                #统计转移概率
                for on_key,on_val in online_state_transition_dict.items():
                    if on_key in offline_chunk.state_transition_matrix:
                        cur_prob +=offline_chunk.state_transition_matrix[on_key]*on_val
                cur_prob=cur_prob/off_chunk_len
                if cur_prob>max_prob:
                    max_prob=cur_prob
                    target_chunk=offline_chunk
            if target_chunk == None:
                #print("error")
                error_count +=1
                continue
            self.o_g_p_relation_list[index_j].pred_stream=target_chunk
        print (error_count,online_short_count)
        
    #计算预测结果指标
    def pred_performance(self):
        true_count=0
        all_count=0
        for o_g_p_relation in self.o_g_p_relation_list:
            if o_g_p_relation.pred_stream==None:
                continue
            all_count +=1
            if o_g_p_relation.ground_truth_stream.video_url == o_g_p_relation.pred_stream.video_url:
                true_count +=1
        print ('all count {}; true count {}; acc {}'.format(all_count,true_count,true_count/all_count))

if __name__ == '__main__':
    match_alg=Match_alg('/Users/hale/PycharmProjects/batch_video_clawer/data/result/online_encrypted_finger.csv','/Users/hale/PycharmProjects/batch_video_clawer/data/result/finger_store.csv')
    #match_alg.slide_wind(10)
    match_alg.markov_hight_order(60,4,10)
    match_alg.pred_performance()