from nis import match
from finger_preprocess import data_Process,Chunk

class Match_alg():
    def __init__(self,online_file,offline_file) -> None:
        self.offline_chunk_list=[]
        self.online_chunk_list=[]
        #获取指纹数据
        finger_data=data_Process(online_file,offline_file)
        self.offline_chunk_list=finger_data.offline_chunk_list
        self.online_chunk_list=finger_data.offline_chunk_list
    
    #滑动窗口匹配
    def slide_wind(self,wind_size):
        no_match_count=0#长度太短而没有参与匹配的指纹数量
        res_chunk=[]
        for online_chunk in self.online_chunk_list:
            if len(online_chunk.finger_list)<wind_size:
                no_match_count +=1
                continue
            min_dis=99999999999
            min_chunk=None
            for offline_chunk in self.offline_chunk_list:
                if len(offline_chunk.finger_list)<wind_size:
                    continue
                for i in range(0,len(offline_chunk.finger_list)-len(online_chunk.finger_list)):
                    cur_dis=0
                    for j in range(0,wind_size):
                        cur_dis +=abs(online_chunk.finger_list[j]-offline_chunk.finger_list[j+i])
                    if cur_dis<min_dis:
                        min_dis=cur_dis
                        min_chunk=offline_chunk
            if min_chunk == None:
                print("error")
                continue
            res_chunk.append([online_chunk,min_chunk])
        
        match_sucess_count=0
        for match_chunk in res_chunk:
            for match_off_chunk in match_chunk[1].labels:
                if str(match_chunk[0].labels[0]).strip()==str(match_off_chunk).strip():
                    print (str(match_chunk[0].labels[0])+' '+str(match_off_chunk))
                    match_sucess_count +=1
        print (match_sucess_count)

match_alg=Match_alg('/Users/hale/PycharmProjects/batch_video_clawer/data/res/online_encrypted_finger.csv','/Users/hale/PycharmProjects/batch_video_clawer/data/res/finger_store.csv')
match_alg.slide_wind(20)
                

