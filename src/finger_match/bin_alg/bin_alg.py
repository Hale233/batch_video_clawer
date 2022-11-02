import matplotlib.pyplot as plt
class Bin_alg():
    def __init__(self,online_chunk_path,offline_chunk_path,record_path) -> None:
        self.online_chunk_dict={}
        self.offline_chunk_dict={}
        self.on_off_twain_list=[]
        self.record_path=record_path
        self.video_chunk_size_max=2500000.0
        self.video_chunk_size_min=600000.0
        self.online_chunk_dict=self.get_dict_data(online_chunk_path)
        self.offline_chunk_dict=self.get_dict_data(offline_chunk_path)
        self.on_off_chunk_match()
        #self.on_off_chunk_record()
        #self.on_off_chunk_diffvall_record()
        
        self.res_avg_bin_analysis()

        #self.chunksize_res_relation_analysis()
        #on_off_bin_list=self.dynamic_res_average_bins_div(100)
        #match_success_count=self.bin_alg_eval(on_off_bin_list)
        #print(match_success_count)
    
    #按五元组获取块信息
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
            tuples=str(vals[0])#五元组
            finger=vals[1].split('/')[:-1]#指纹
            finger=list(map(int,finger))
            finger=self.small_chunk_clean(finger,6000)
            if tuples not in chunk_dict:
                chunk_dict[tuples]=finger
            else :
                repeat_tuple[tuples]=1
        
        #去除重复的五元组
        for repeat_key,_ in repeat_tuple.items():
            del chunk_dict[repeat_key]
        
        return chunk_dict
    
    #过滤掉指纹序列中小于阈值的块，主要是针对离线情况，因为在线在过滤证书的同时会把小的音视频块也过滤掉
    def small_chunk_clean(self,chunk_list,audio_thd):
        new_list=[]
        for chunk in chunk_list:
            if chunk >audio_thd:
                new_list.append(chunk)
        return new_list

    #在线离线块对应，并记录到on_off_twain_list类中
    def on_off_chunk_match(self):
        all_count=0
        no_match_count=0
        match_count=0
        for tuples,on_chunk_list in self.online_chunk_dict.items():
            if tuples not in self.offline_chunk_dict:
                continue
            off_chunk_list=self.offline_chunk_dict[tuples]
            on_chunk_len=len(on_chunk_list)
            off_chunk_len=len(off_chunk_list)
            all_count +=1
            if on_chunk_len!=off_chunk_len:
                no_match_count +=1
                continue
            flag=0
            #排除错误匹配的流
            for i in range(0,on_chunk_len):
                if (on_chunk_list[i]/off_chunk_list[i]>=1 and on_chunk_list[i]/off_chunk_list[i]<=1.3)==False:
                    flag=1
            #记录正确匹配的流
            if flag==0:
                match_count +=1
                for i in range(0,on_chunk_len):
                    self.on_off_twain_list.append([on_chunk_list[i],off_chunk_list[i]])
        
        print(all_count,all_count-no_match_count,match_count)
    
    #记录在线与离线块的差值
    def on_off_chunk_diffvall_record(self):
        record_path="/Users/hale/PycharmProjects/batch_video_clawer/data/chunk_list/on_off_diffval_analysis.csv"
        record_file=open(record_path,mode='w',encoding='utf-8')
        for datas in self.on_off_twain_list:
            record_file.write(str(datas[0]-datas[1])+'\n')

    #记录在线与离线块的对应关系
    def on_off_chunk_record(self):
        record_file=open(self.record_path,mode='w',encoding='utf-8')
        for datas in self.on_off_twain_list:
            if datas[1]>600000:
                record_file.write(str(datas[0])+','+str(datas[1])+'\n')

    #评估分桶算法的性能            
    def bin_alg_eval(self,on_off_bin_list):
        bin_count={}
        match_success_count=0
        for datas in on_off_bin_list:
            bin_count[datas[0]]=1
            if datas[0]==datas[1]:
                match_success_count +=1
        #print('all count={},match_success_count={},bin_count={}'.format(len(on_off_bin_list),match_success_count,len(bin_count)))
        return match_success_count
    
    #静态偏置等分分桶
    def static_res_average_bins_div(self,bins_count,bias):
        bin_size=(self.video_chunk_size_max-self.video_chunk_size_min)/bins_count
        on_off_bin_list=[]
        for chunk in self.on_off_twain_list:
            if chunk[1]<=600000:
                continue
            #获得在线块的分桶号
            if chunk[0]-bias>=self.video_chunk_size_max:
                bin_index_on=bins_count-1
            elif chunk[0]-bias<=self.video_chunk_size_min:
                bin_index_on=0
            else:
                bin_index_on=int((chunk[0]-bias-self.video_chunk_size_min)/bin_size)
            #获得离线块的分桶号
            if chunk[1]>=self.video_chunk_size_max:
                bin_index_off=bins_count-1
            elif chunk[1]<=self.video_chunk_size_min:
                bin_index_off=0
            else:
                bin_index_off=int((chunk[1]-self.video_chunk_size_min)/bin_size)
            
            on_off_bin_list.append([bin_index_on,bin_index_off])
        return on_off_bin_list
    
    #动态偏置等分分桶
    def dynamic_res_average_bins_div(self,bins_count):
        bin_size=(self.video_chunk_size_max-self.video_chunk_size_min)/bins_count
        on_off_bin_list=[]
        for chunk in self.on_off_twain_list:
            if chunk[1]<=600000:
                continue
            #获得在线块的分桶号
            chunk_bias=(chunk[0]-1119)/1.00135177
            if chunk_bias>=self.video_chunk_size_max:
                bin_index_on=bins_count-1
            elif chunk_bias<=self.video_chunk_size_min:
                bin_index_on=0
            else:
                bin_index_on=int((chunk_bias-self.video_chunk_size_min)/bin_size)
            #获得离线块的分桶号
            if chunk[1]>=self.video_chunk_size_max:
                bin_index_off=bins_count-1
            elif chunk[1]<=self.video_chunk_size_min:
                bin_index_off=0
            else:
                bin_index_off=int((chunk[1]-self.video_chunk_size_min)/bin_size)
            
            on_off_bin_list.append([bin_index_on,bin_index_off])
        return on_off_bin_list

    #不同桶大小以及偏置值下统计桶匹配成功的个数
    def res_avg_bin_analysis(self):
        record_path="/Users/hale/PycharmProjects/batch_video_clawer/data/chunk_list/dynamic_res_avg_bin_analysis.csv"
        record_file=open(record_path,mode='w',encoding='utf-8')
        for i in range(1000,100000,100):
            print(i)
            on_off_bin_list=self.dynamic_res_average_bins_div(i)
            match_success_count=self.bin_alg_eval(on_off_bin_list)
            record_file.write(str(match_success_count)+',')
            record_file.write('\n')
            '''static
            for j in range(0,6000,1000):
                on_off_bin_list=self.static_res_average_bins_div(i,j)
                match_success_count=self.bin_alg_eval(on_off_bin_list)
                record_file.write(str(match_success_count)+',')
            record_file.write('\n')
            '''

    #分析块大小与视频块对差值之间的关系
    def chunksize_res_relation_analysis(self):
        X=[]
        Y=[]
        res=[]
        for chunk in self.on_off_twain_list:
            if chunk[1]<=600000:
                continue
            diff=chunk[0]-chunk[1]
            if diff>4350:
                continue
            res.append([chunk[0],diff])
        res.sort(key=lambda i:i[0],reverse=False)
        for datas in res:
            X.append(datas[0])
            Y.append(datas[1])
        plt.plot(X,Y)
        plt.show()
        #bias=0.00135177*offline_chunk+1119

if __name__ == '__main__':
    bin_alg=Bin_alg("/Users/hale/PycharmProjects/batch_video_clawer/data/chunk_list/online_encrypted_finger.csv","/Users/hale/PycharmProjects/batch_video_clawer/data/chunk_list/offline_chunk_list.csv","/Users/hale/PycharmProjects/batch_video_clawer/data/chunk_list/on_off_analysis.csv")
    