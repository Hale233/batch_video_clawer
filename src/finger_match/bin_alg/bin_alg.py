class Bin_alg():
    def __init__(self,online_chunk_path,offline_chunk_path) -> None:
        self.online_chunk_dict={}
        self.offline_chunk_dict={}
        self.on_off_twain_list=[]
        self.online_chunk_dict=self.get_dict_data(online_chunk_path)
        self.offline_chunk_dict=self.get_dict_data(offline_chunk_path)
    
    def get_dict_data(self,path):
        chunk_file=open(path,mode='r',encoding='utf-8')
        chunk_dict={}
        repeat_tuple={}
        online_data=chunk_file.read()
        online_datas=online_data.split('\n')
        for lines in online_datas:
            if lines=='':
                continue
            vals=lines.split(',')
            finger=vals[1].split('/')[:-1]#指纹
            tuples=str(vals[0])#五元组
            if tuples not in chunk_dict:
                chunk_dict[tuples]=list(map(int,finger))
            else :
                repeat_tuple[tuples]=1
        
        #去除重复的五元组
        for repeat_key,_ in repeat_tuple.items():
            del chunk_dict[repeat_key]
        
        return chunk_dict

if __name__ == '__main__':
    bin_alg=Bin_alg("/home/local/data1/xuminchao/batch_video_clawer/data/result/online_encrypted_finger.csv","/home/local/data1/xuminchao/batch_video_clawer/data/result/offline_chunk_list.csv")
    print("pass")