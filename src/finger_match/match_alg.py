#指纹匹配算法
from nis import match
import queue
from symbol import small_stmt
from collections import deque
from numpy import matrix
from finger_preprocess import data_Process,Video_flow,O_g_p_relation
from bin_alg import bin_alg
import time

class Match_alg():
    def __init__(self,online_file,offline_file,offline_audio_thd) -> None:
        self.offline_chunk_list=[]
        self.online_chunk_list=[]
        self.video_chunk_size_max=2200000.0
        self.video_chunk_size_min=offline_audio_thd
        #获取指纹数据
        finger_data=data_Process(online_file,offline_file,offline_audio_thd)
        self.offline_chunk_list=finger_data.offline_chunk_list
        self.online_chunk_list=finger_data.online_chunk_list
        self.o_g_p_relation_list=finger_data.o_g_p_relation_list
    
    def P_dtw(self):
        # # 变换指纹库流
        for i in range(len(self.offline_chunk_list)):
            R = [0]
            for j in range(1, len(self.offline_chunk_list[i].finger_list)):
                r = (self.offline_chunk_list[i].finger_list[j] - self.offline_chunk_list[i].finger_list[j - 1]) / self.offline_chunk_list[i].finger_list[j - 1]
                R.append(r)
            if R != [0]:
                self.offline_chunk_list[i].finger_list = R

        # 变换待匹配流
        for i in range(len(self.o_g_p_relation_list)):
            R = [0]
            for j in range(1, len(self.o_g_p_relation_list[i].original_stream.finger_list)):
                pre=(self.o_g_p_relation_list[i].original_stream.finger_list[j - 1]-1119)/1.00135177
                cur=(self.o_g_p_relation_list[i].original_stream.finger_list[j]-1119)/1.00135177
                r = (cur - pre) / pre
                R.append(r)
            if R != [0]:
                self.o_g_p_relation_list[i].original_stream.finger_list = R

        time_start=time.time()
        ind = -1
        for sub_que in self.o_g_p_relation_list:
            ind += 1
            if len(sub_que.ground_truth_stream.tuple_list)!=1:
                continue
            n = len(sub_que.original_stream.finger_list)
            if n > 0:
                min_tem = []
                min_d = float('inf')
                for sub_tem in self.offline_chunk_list:
                    m = len(sub_tem.finger_list)
                    if m > 0:
                        M = [[float('inf') for i in range(m)] for j in range(n)]
                        M[0][0] = 0
                        for i in range(1, n):
                            for j in range(1, m):
                                cost = abs(sub_tem.finger_list[j] - sub_que.original_stream.finger_list[i])
                                M[i][j] = cost  + min(M[i - 1][j], M[i - 1][j - 1], M[i - 1][j - 2])
                        if min_d > M[-1][-1] / n:
                            min_d = M[-1][-1] / n
                            min_tem = sub_tem
                self.o_g_p_relation_list[ind].pred_stream = min_tem
        time_end=time.time()
        print (time_end-time_start)


    #滑动窗口匹配
    def slide_wind(self,wind_size):
        index=-1
        time_sum=0
        time_count=0
        small_count=0
        for o_g_p_relation in self.o_g_p_relation_list:
            index +=1
            self.o_g_p_relation_list[index].pred_stream=None
            # 仅统计用一条流传输的视频
            if len(o_g_p_relation.ground_truth_stream.tuple_list)!=1:
                continue
            if len(o_g_p_relation.original_stream.finger_list)<wind_size:
                small_count +=1
                continue
            min_dis=99999999999
            min_chunk=None
            online_chunk=o_g_p_relation.original_stream
            time_start=time.time()
            for offline_chunk in self.offline_chunk_list:
                if len(offline_chunk.finger_list)<wind_size:# or len(offline_chunk.finger_list)<len(online_chunk.finger_list):
                    continue
                for i in range(0,(len(offline_chunk.finger_list)-wind_size)):
                #for i in range(0,(len(offline_chunk.finger_list)-len(online_chunk.finger_list)+1)):
                    cur_dis=0
                    for j in range(0,wind_size):
                        online_chunk_size=(online_chunk.finger_list[j]-1119)/1.00135177
                        #在线一定是要大于离线指纹库的
                        #if online_chunk.finger_list[j]<offline_chunk.finger_list[j+i]:
                        #    cur_dis=99999999999
                        #    break
                        cur_dis +=abs(online_chunk_size-offline_chunk.finger_list[j+i])
                    if cur_dis<min_dis:
                        min_dis=cur_dis
                        min_chunk=offline_chunk
            if min_chunk == None:
                #print("error")
                time_end=time.time()
                time_sum +=time_end-time_start
                time_count +=1
                continue
            self.o_g_p_relation_list[index].pred_stream=min_chunk
            time_end=time.time()
            time_sum +=time_end-time_start
            time_count +=1
        #print (time_sum,time_count,time_sum/time_count)
        return small_count
    
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

    #网格搜索时每次用新的参数需要把上次预测的结果清空
    def pred_clean(self):
        index_j=-1
        for o_g_p_relation in self.o_g_p_relation_list:
            index_j +=1
            self.o_g_p_relation_list[index_j].pred_stream=None

    #高阶马尔可夫
    #bins_count:桶个数、orders:马尔可夫的阶数、win_size:转移的次数、de_mix_stream_flag:匹配仅用一条流传输的指纹
    def markov_hight_order(self,bins_count,orders,win_size,de_mix_stream_flag=0,mutil_order_flag=0,bias=3000,error_bins_tuples_dict={}):
        time_sum=0
        time_count=0
        orders +=1
        #计算离线指纹的order阶概率转移矩阵
        index_i=-1
        bin_size=(self.video_chunk_size_max-self.video_chunk_size_min)/bins_count
        for offline_chunk in self.offline_chunk_list:
            index_i +=1

            #去除分桶错误的块所在的指纹,非必需
            for tuples in offline_chunk.tuple_list:
                if tuples in error_bins_tuples_dict:
                    self.offline_chunk_list[index_i].state_transition_matrix={}
                    break

            #当序列小于多少时不参与匹配

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
        
        #在线指纹匹配
        index_j=-1
        error_count=0
        #长度太短而不参与匹配的在线指纹数量
        online_short_count=0
        for o_g_p_relation in self.o_g_p_relation_list:
            index_j +=1

            #马尔可夫降阶
            if mutil_order_flag==1:
                if self.o_g_p_relation_list[index_j].zero_prob==0:
                    continue
            else:
                self.o_g_p_relation_list[index_j].pred_stream=None

            #仅用一条流进行传输的指纹
            if de_mix_stream_flag==1:
                if len(o_g_p_relation.ground_truth_stream.tuple_list)!=1:
                    continue
            
            #去除分桶错误的块所在的指纹,非必需
            if o_g_p_relation.original_stream.tuple_list[0] in error_bins_tuples_dict:
                continue

            online_chunk=o_g_p_relation.original_stream
            online_bin_relation_que=deque()
            online_state_transition_dict={}
            #长度太短而不参与匹配,+n则保证至少有n次转移
            if len(online_chunk.finger_list)<orders + 1:
                online_short_count +=1
                continue
            time_start=time.time()
            #构建在线的转移关系字典
            #在线偏置等分分桶
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
                #静态偏置
                '''
                if on_chunk-bias>=self.video_chunk_size_max:
                    bin_index_cur=bins_count-1
                elif on_chunk-bias<=self.video_chunk_size_min:
                    bin_index_cur=0
                else:
                    bin_index_cur=int((on_chunk-bias-self.video_chunk_size_min)/bin_size)
                '''
                
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
                off_chunk_len=len(offline_chunk.finger_list)
                #离线小于阶数+1不进行匹配
                if off_chunk_len<orders + 1:
                    continue
                #当阶数大于指纹长度时会出现没有转移状态的情况，此时直接跳过
                if len(offline_chunk.state_transition_matrix)==0:
                    continue
                #统计转移概率
                for on_key,on_val in online_state_transition_dict.items():
                    if on_key in offline_chunk.state_transition_matrix:
                        cur_prob +=offline_chunk.state_transition_matrix[on_key]*on_val
                cur_prob=cur_prob/(off_chunk_len+1-orders)
                if cur_prob>max_prob:
                    max_prob=cur_prob
                    target_chunk=offline_chunk

            #print(time_end-time_start)
            if target_chunk == None:
                #print("error")
                error_count +=1
                self.o_g_p_relation_list[index_j].zero_prob=1
                time_end=time.time()
                time_sum +=time_end-time_start
                time_count +=1
                continue
            self.o_g_p_relation_list[index_j].pred_stream=target_chunk
            time_end=time.time()
            time_sum +=time_end-time_start
            time_count +=1

        #print (time_sum,time_count,time_sum/time_count)
        return error_count,online_short_count
    
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
            else :
                _=1
        #print ('all count {}; true count {}; acc {}'.format(all_count,true_count,true_count/all_count))
        if all_count==0:
            return all_count,true_count,0
        else :
            return all_count,true_count,true_count/all_count
    
    #去除错误分桶所在的流后进行匹配性能评估
    def pred_performance_deFalseStream():
        bin_alg_class=bin_alg.Bin_alg("./data/chunk_list/online_encrypted_finger.csv","./data/chunk_list/offline_chunk_list.csv")
        on_off_bin_list=bin_alg_class.dynamic_res_average_bins_div(90)
        error_bins_tuples_dict=bin_alg_class.get_error_tuple_dict(on_off_bin_list)

        match_alg=Match_alg('./data/chunk_list/online_encrypted_finger_seq.csv','./data/chunk_list/finger_store.csv')
        error_count,online_short_count=match_alg.markov_hight_order(90,4,1000,3000,error_bins_tuples_dict)
        all_count,true_count,acc=match_alg.pred_performance()
        print('{},{},{},{},{},{}'.format(error_count,online_short_count,all_count,true_count,acc,true_count/(error_count+all_count)))

if __name__ == '__main__':
    offline_audio_thd=700000
    match_alg=Match_alg('./data/chunk_list/online_encrypted_finger_seq.csv','./data/chunk_list/finger_store_3.csv',offline_audio_thd)
    match_alg.P_dtw()
    all_count,true_count,acc=match_alg.pred_performance()
    print('{},{},{}'.format(all_count,true_count,acc))
    '''
    for i in range(3,11):
        match_alg=Match_alg('./data/chunk_list/online_encrypted_finger_seq.csv','./data/chunk_list/finger_store_3.csv',offline_audio_thd)
        online_short_count=match_alg.slide_wind(i)
        all_count,true_count,acc=match_alg.pred_performance()
        print('{},{},{},{}'.format(online_short_count,all_count,true_count,acc))
    
    
    for i in range(1,6,1):
        for j in range(4000,7000,1000):
            #match_alg.pred_clean()
            match_alg=Match_alg('./data/chunk_list/online_encrypted_finger_seq.csv','./data/chunk_list/finger_store_3.csv',offline_audio_thd)
            error_count,online_short_count=match_alg.markov_hight_order(bins_count=j,orders=i,win_size=1,de_mix_stream_flag=1)
            all_count,true_count,acc=match_alg.pred_performance()
            #print('{},{},{},{},{},{},{},{}'.format(i,j,error_count,online_short_count,all_count,true_count,acc,true_count/(error_count+all_count)))
            error_count,online_short_count=match_alg.markov_hight_order(bins_count=j,orders=1,win_size=3,mutil_order_flag=1,de_mix_stream_flag=1)
            all_count,true_count,acc=match_alg.pred_performance()
            print('{},{},{},{},{},{},{},{}'.format(i,j,error_count,online_short_count,all_count,true_count,acc,true_count/(error_count+all_count)))
    '''
    
    '''
    bin_count=[100,200,300,400,500,600,700,800,900,1000,2000,3000,4000,5000]
    for i in bin_count:
        for j in range(1,11,1):
            for k in range(1,10,1):
                #for k in win_size:
                match_alg=Match_alg('./data/chunk_list/online_encrypted_finger_seq.csv','./data/chunk_list/finger_store_3.csv',offline_audio_thd)
                #match_alg.slide_wind(10)
                error_count,online_short_count=match_alg.markov_hight_order(bins_count=i,orders=j,win_size=k)
                all_count,true_count,acc=match_alg.pred_performance()
                print('{},{},{},{},{},{},{},{},{}'.format(i,j,k,error_count,online_short_count,all_count,true_count,acc,true_count/(error_count+all_count)))
    '''