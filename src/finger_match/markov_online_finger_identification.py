from collections import deque
from numpy import matrix
from finger_preprocess import data_Process,Video_flow,O_g_p_relation
from bin_alg import bin_alg
import time

#在线模式马尔可夫
class Markov_alg():
    def __init__(self,online_file,offline_file,offline_audio_thd,high_orders,high_bins_count,high_win_size,low_orders,low_bins_count,low_win_size) -> None:
        self.offline_chunk_list=[]
        self.online_chunk_list=[]
        self.video_chunk_size_max=2200000.0
        self.video_chunk_size_min=offline_audio_thd
        #获取指纹数据
        finger_data=data_Process(online_file,offline_file,offline_audio_thd)
        self.offline_chunk_list=finger_data.offline_chunk_list
        self.online_chunk_list=finger_data.online_chunk_list
        self.o_g_p_relation_list=finger_data.o_g_p_relation_list
        
        self.state_transition_calculate(high_bins_count,high_orders)
        self.high_state_transition_table=self.state_transition_table_generate(high_orders)
        self.state_transition_calculate(low_bins_count,low_orders)
        self.low_state_transition_table=self.state_transition_table_generate(low_orders)
        error_count,online_short_count=self.online_match(high_orders,high_bins_count,high_win_size,0)
        error_count,online_short_count=self.online_match(low_orders,low_bins_count,low_win_size,1)
        all_count,true_count,acc=self.pred_performance()
        print('{},{},{},{},{},{}'.format(error_count,online_short_count,all_count,true_count,acc,true_count/(error_count+all_count)))

    #记录指纹库的所有转移概率
    def state_transition_calculate(self,bins_count,orders):
        orders +=1
        #计算离线指纹的order阶概率转移矩阵
        index_i=-1
        bin_size=(self.video_chunk_size_max-self.video_chunk_size_min)/bins_count
        for offline_chunk in self.offline_chunk_list:
            index_i +=1
            self.offline_chunk_list[index_i].state_transition_matrix=''
            #用一个队列记录n阶的桶关系
            bin_relation_que=deque()
            state_transition_dict={}
            for chunk in offline_chunk.finger_list:
                #离线 等分分桶
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
    
    #生成指纹库的转移概率表
    def state_transition_table_generate(self,orders):
        state_transition_table={}
        for offline_chunk in self.offline_chunk_list:
            cur_state_transition_dict=offline_chunk.state_transition_matrix
            off_chunk_len=len(offline_chunk.finger_list)
            if cur_state_transition_dict=='' or len(cur_state_transition_dict)==0:
                continue
            cur_streamID=offline_chunk.streamID
            for transition,transition_prob in cur_state_transition_dict.items():
                transition_prob=transition_prob/(off_chunk_len+1-orders)
                if transition in state_transition_table:
                    state_transition_table[transition].append([cur_streamID,transition_prob])
                else :
                    state_transition_table[transition]=[[cur_streamID,transition_prob]]
        return state_transition_table

    #在线匹配
    def online_match(self,orders,bins_count,win_size,mutil_order_flag):
        time_sum=0
        time_count=0
        index_j=-1
        orders +=1
        bin_size=(self.video_chunk_size_max-self.video_chunk_size_min)/bins_count
        error_count=0
        #长度太短而不参与匹配的在线指纹数量
        online_short_count=0
        if mutil_order_flag==0:
            state_transition_table=self.high_state_transition_table
        else :
            state_transition_table=self.low_state_transition_table

        for o_g_p_relation in self.o_g_p_relation_list:
            index_j +=1
            #马尔可夫降阶
            if mutil_order_flag==1:
                if self.o_g_p_relation_list[index_j].zero_prob==0:
                    continue

            online_chunk=o_g_p_relation.original_stream
            online_bin_relation_que=deque()
            online_state_transition_dict={}
            #长度太短而不参与匹配,+n则保证至少有n次转移
            if len(online_chunk.finger_list)<orders + 1:
                online_short_count +=1
                continue
            time_start=time.time()
            ##在线指纹预处理：计算转移过程
            on_chunk_count=0
            for on_chunk in online_chunk.finger_list:
                #动态偏置
                chunk_bias=(on_chunk-1119)/1.00135177
                if chunk_bias>=self.video_chunk_size_max:
                    bin_index_cur=bins_count-1
                elif chunk_bias<=self.video_chunk_size_min:
                    bin_index_cur=0
                else:
                    bin_index_cur=int((chunk_bias-self.video_chunk_size_min)/bin_size)
                
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
            
            #计算最大概率值对应的streamID
            state_dict={}
            for on_key,on_val in online_state_transition_dict.items():
                if on_key in state_transition_table:
                    for val in state_transition_table[on_key]:
                        if val[0] in state_dict:
                            state_dict[val[0]] +=on_val*val[1]
                        else :
                            state_dict[val[0]]=on_val*val[1]

            max_prob=0
            target_id=-1
            if len(state_dict)==0:
                error_count +=1
                self.o_g_p_relation_list[index_j].zero_prob=1
            else :
                for stream_id,prob in state_dict.items():
                    if prob>max_prob:
                        max_prob=prob
                        target_id=stream_id
            self.o_g_p_relation_list[index_j].pred_stream=target_id
            time_end=time.time()
            time_sum +=time_end-time_start
            time_count +=1

        print (time_sum,time_count,time_sum/time_count)
        return error_count,online_short_count

    #在线匹配过程中streamID与指纹库类的对应关系
    def streamID2video_flow_class(self):
        index_j=-1
        for o_g_p_relation in self.o_g_p_relation_list:
            index_j +=1
            if o_g_p_relation.pred_stream==-1:
                continue
            for offline_chunk in self.offline_chunk_list:
                if offline_chunk.streamID==o_g_p_relation.pred_stream:
                    self.o_g_p_relation_list[index_j].pred_stream=offline_chunk
                    break
    
    #计算预测结果指标
    def pred_performance(self):
        self.streamID2video_flow_class()
        true_count=0
        all_count=0
        for o_g_p_relation in self.o_g_p_relation_list:
            if o_g_p_relation.pred_stream==-1 or o_g_p_relation.pred_stream==None:
                continue
            all_count +=1
            if o_g_p_relation.ground_truth_stream.video_url == o_g_p_relation.pred_stream.video_url:
                true_count +=1
        if all_count==0:
            return all_count,true_count,0
        else :
            return all_count,true_count,true_count/all_count

if __name__ == '__main__':
    online_file='./data/chunk_list/online_encrypted_finger_seq.csv'
    offline_file='./data/chunk_list/finger_store_3.csv'
    offline_audio_thd=700000
    high_orders,high_bins_count,high_win_size=3,5000,1
    low_orders,low_bins_count,low_win_size=1,4000,3
    markov_alg=Markov_alg(online_file,offline_file,offline_audio_thd,high_orders,high_bins_count,high_win_size,low_orders,low_bins_count,low_win_size)