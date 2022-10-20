from nis import match
from symbol import small_stmt
from finger_preprocess import data_Process,Video_flow,O_g_p_relation

class Match_alg():
    def __init__(self,online_file,offline_file) -> None:
        self.offline_chunk_list=[]
        self.online_chunk_list=[]
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
            #if len(o_g_p_relation.ground_truth_stream.tuple_list)!=1:
            #    continue
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

match_alg=Match_alg('/Users/hale/PycharmProjects/batch_video_clawer/data/result/online_encrypted_finger.csv','/Users/hale/PycharmProjects/batch_video_clawer/data/result/finger_store.csv')
match_alg.slide_wind(10)
match_alg.pred_performance()
                

