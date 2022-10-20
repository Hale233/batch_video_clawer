import os

#记录每一个块的信息,[range_beg,range_end,len,5tuple,video/audio]
class Video_itag_val():
    def __init__(self,range_beg,range_end,chunk_len,stream_tuple,chunk_type) -> None:
        self.range_beg=range_beg
        self.range_end=range_end
        self.chunk_len=chunk_len
        self.stream_tuple=stream_tuple
        self.chunk_type=chunk_type

#记录每一条验证流的信息,值为[是否缺首块，块断开的次数，使用流的数量，交叉流数量，块的数量，连续块列表，连续块对应的5元组]
class Finger_valid_val():
    def __init__(self,loss_first_chunk_flag,break_count,stream_count,mix_count,chunk_count,seq_video_itag_val,seq_video_itag_tuple_val) -> None:
        self.loss_first_chunk_flag=loss_first_chunk_flag
        self.break_count=break_count
        self.stream_count=stream_count
        self.mix_count=mix_count
        self.chunk_count=chunk_count
        self.seq_video_itag_val=seq_video_itag_val
        self.seq_video_itag_tuple_val=seq_video_itag_tuple_val

class Finger():
    def __init__(self,analysis_record_path,finger_record_path) -> None:
        #存储每一个视频的finger_valid_dict,key为文件路径
        self.finger_valid_dict_list={}
        #存储每一个视频的video_itag_dict,key为文件路径
        self.video_itag_dict_list={}
        #记录每一个视频的URL,key为文件路径
        self.path2url={}
        self.analysis_record_path=analysis_record_path
        self.finger_record_path=finger_record_path
        
    def get_filelist(self,path):
        Filelist = []
        dirs = os.listdir(path)
        for dir in dirs:
            Filelist.append(os.path.join(path, dir))
        return Filelist,dirs

    def mkdir(path):
        path = path.strip()
        path = path.rstrip("/")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            print(' 目录已存在')
            return False

    def from_root_path_get_finger(self,root_path):
        Filelist,_=self.get_filelist(root_path+"/mitm")
        for path in Filelist:
            #print(path)
            self.finger_extract(path)
    
    #从记录文件路径的文件中依次读取文件处理指纹
    def from_path_file_get_finger(self,path_file):
        path_file=open(path_file,mode='r',encoding='utf-8')
        path_datas=path_file.read().split('\n')
        for root_path in path_datas:
            Filelist,_=self.get_filelist(root_path)
            #对每一个视频的mitm文件进行处理
            for path in Filelist:
                #print(path)
                self.work_stream(path)

    #提取指纹信息，处理单位是一个视频的文件
    def finger_extract(self,path):
        #
        #key为itag，value为list，list中每一个元素为[range_beg,range_end,len,5tuple,video/audio]
        video_itag_dict={}
        file_paths,file_names=self.get_filelist(path)
        #从每个mitm文件中提取指纹元信息
        for i in range(0,len(file_paths)):
            mitm_file=open(file_paths[i],mode='r',encoding='utf-8')
            mitm_file_data=mitm_file.read()
            info_chunks=mitm_file_data.split('------------------------\n')[:-1]
            for chunk in info_chunks:
                lines=chunk.split('\n')
                request_head=lines[1]
                response_head=lines[2]
                #提取itag 和 range
                itag_index_beg=int(request_head.find("itag="))
                itag_index_end=int(request_head.find("&",itag_index_beg))
                range_index_beg=int(request_head.find("range="))
                range_index_end=int(request_head.find("&",range_index_beg))
                if itag_index_beg==-1 or range_index_beg==-1:
                    print("itag or range not found")
                    return
                itag=request_head[itag_index_beg+5:itag_index_end]
                video_range=request_head[range_index_beg+6:range_index_end]
                video_range_beg=int(video_range.split("-")[0])
                video_range_end=int(video_range.split("-")[1])
                if response_head.find("'Content-Type', b'video")!=-1:
                    video_itag_val=Video_itag_val(video_range_beg,video_range_end,int(lines[0]),file_names[i],"video")
                    #base_data=[video_range_beg,video_range_end,int(lines[0]),file_names[i],"video"]
                elif response_head.find("'Content-Type', b'audio")!=-1:
                    video_itag_val=Video_itag_val(video_range_beg,video_range_end,int(lines[0]),file_names[i],"audio")
                    #base_data=[video_range_beg,video_range_end,int(lines[0]),file_names[i],"audio"]
                else:
                    #print(response_head)
                    #print ("\n error!!!!!!!!!!!!!!!!!\n")
                    continue

                if itag not in video_itag_dict:
                    video_itag_dict[itag]=[video_itag_val]
                else:
                    video_itag_dict[itag].append(video_itag_val)
        return video_itag_dict
    
    #获取视频路径与URL的对应关系
    def get_video_url(self,path):
        url_path=str(path).replace('/mitm/','/url/')
        url_file=open(url_path,mode='r',encoding='utf-8')
        url_data=url_file.read()
        self.path2url[path]=url_data.strip()
        url_file.close()
        
    #记录指纹值
    def record_finger(self,path,video_itag_dict):
        recoed_file=open(self.finger_record_path,mode='a+',encoding='utf-8')
        for itag,video_itag_val_list in video_itag_dict.items():
            if len(video_itag_val_list)<=2:
                continue
            recoed_file.write(str(path)+","+str(itag)+",")
            tuple_dict={}
            chunk_type={}
            for video_itag_val in video_itag_val_list:
                chunk_type[video_itag_val.chunk_type]=1
            if len(chunk_type)!=1:
                print ("type error!!!!!!!!!!!!!!!!!!!!!!!!!")
                return
            recoed_file.write(str(video_itag_val_list[0].chunk_type)+",")
            for video_itag_val in video_itag_val_list:
                tuple_dict[video_itag_val.stream_tuple]=1
                recoed_file.write("/"+str(video_itag_val.chunk_len))
            recoed_file.write(",")
            for key,_ in tuple_dict.items():
                recoed_file.write("/"+str(key).replace(",",".").replace("-",">"))
            recoed_file.write("\n")

    #记录指纹值与统计分析值
    def analysis_record(self):
        finger_valid_dict_list=self.finger_valid_dict_list
        video_itag_dict_list=self.video_itag_dict_list
        recoed_file=open(self.analysis_record_path,mode='a+',encoding='utf-8')
        miss_first_chunk_count=0
        miss_chunk_count=0
        stream_count=0
        mix_stream_count=0
        video_stream_count=0
        for path,finger_valid_dict in finger_valid_dict_list.items():
            for itag in finger_valid_dict:
                video_itag_val_list=video_itag_dict_list[path][itag]
                if finger_valid_dict[itag].chunk_count >5:
                    tuple_dict={}
                    chunk_type={}
                    #防止指纹信息提取错误
                    for video_itag_val in video_itag_val_list:
                        chunk_type[video_itag_val.chunk_type]=1
                    if len(chunk_type)!=1:
                        print ("type error!!!!!!!!!!!!!!!!!!!!!!!!!")
                        break

                    recoed_file.write(str(path)+","+str(itag)+","+str(video_itag_val_list[0].chunk_type)+",")
                    recoed_file.write(str(self.path2url[path])+",")
                    for video_itag_val in video_itag_val_list:
                        tuple_dict[video_itag_val.stream_tuple]=1
                        recoed_file.write("/"+str(video_itag_val.chunk_len))
                    recoed_file.write(",")
                    for key,_ in tuple_dict.items():
                        recoed_file.write("/"+str(key).replace(",",".").replace("-",">"))
                    
                    #输出累计信息
                    recoed_file.write(","+str(finger_valid_dict[itag].loss_first_chunk_flag)+","+str(finger_valid_dict[itag].break_count)+","+str(finger_valid_dict[itag].stream_count)+","+str(finger_valid_dict[itag].mix_count)+","+str(finger_valid_dict[itag].chunk_count)+",")
                    #输出连续块列表
                    for val in finger_valid_dict[itag].seq_video_itag_val:
                        recoed_file.write("/"+str(val))
                    recoed_file.write(",")
                    for val in finger_valid_dict[itag].seq_video_itag_tuple_val:
                        recoed_file.write("/"+str(val).replace(",",".").replace("-",">"))
                    recoed_file.write("\n")

                    #统计
                    video_stream_count +=1
                    if finger_valid_dict[itag].loss_first_chunk_flag!=0:
                        miss_first_chunk_count +=1
                    if finger_valid_dict[itag].break_count!=0:
                        miss_chunk_count +=1
                    if finger_valid_dict[itag].stream_count!=1:
                        stream_count +=1
                    if finger_valid_dict[itag].mix_count!=0:
                        mix_stream_count +=1
        print ("总流数：{}，缺首块的个数{}，多流传输的个数{}，流出现混合的个数{}，缺块流的个数{}".format(video_stream_count,miss_first_chunk_count,stream_count,mix_stream_count,miss_chunk_count))
    
    '''
    #提取视频指纹序列
    def get_finger(self,video_itag_dict):
        finger_dick={}
        for itag in video_itag_dict:
            video_itag_val=[]
            for i in range(0,len(video_itag_dict[itag])):
                video_itag_val.append(video_itag_dict[itag][i][2])
            finger_dick[itag]=video_itag_val
        return finger_dick
    '''
    #对乱序的视频指纹块进行排序,处理单位是一个视频的文件
    def chunk_sort(self,video_itag_dict):
        for itag in video_itag_dict:
            tuple_dist={}
            tmp_list=[]
            #统计各五元组出现的次数，用于后续去重
            for k in range(0,len(video_itag_dict[itag])):
                if video_itag_dict[itag][k].stream_tuple not in tuple_dist:
                    tuple_dist[video_itag_dict[itag][k].stream_tuple]=1
                else:
                    tuple_dist[video_itag_dict[itag][k].stream_tuple] +=1
            #排序
            for i in range(0,len(video_itag_dict[itag])):
                for j in range(i,len(video_itag_dict[itag])):
                    if video_itag_dict[itag][i].range_beg>video_itag_dict[itag][j].range_beg:
                        video_itag_dict[itag][i],video_itag_dict[itag][j]=video_itag_dict[itag][j],video_itag_dict[itag][i]
            #去重,根据五元组出现的次数，保留出现次数多的重复块
            for i in range(0,len(video_itag_dict[itag])-1):
                if video_itag_dict[itag][i].range_beg==video_itag_dict[itag][i+1].range_beg:
                    if tuple_dist[video_itag_dict[itag][i].stream_tuple]>tuple_dist[video_itag_dict[itag][i+1].stream_tuple]:
                        video_itag_dict[itag][i],video_itag_dict[itag][i+1]=video_itag_dict[itag][i+1],video_itag_dict[itag][i]
                else:
                    tmp_list.append(video_itag_dict[itag][i])
            tmp_list.append(video_itag_dict[itag][len(video_itag_dict[itag])-1])
            video_itag_dict[itag]=tmp_list
        return video_itag_dict
    
    #验证视频指纹是否出现缺块或者交叉传输,并获得分析数据,处理单位是一个视频的文件
    def finger_valid(self,video_itag_dict):
        #指纹验证结果字典,key为itag，值为[是否缺首块，块断开的次数，使用流的数量，交叉流数量，块的数量，连续块列表]
        finger_valid_dict={}
        for itag in video_itag_dict:
            #不统计音频流
            #if video_itag_dict[itag][0].chunk_type=='audio':
            #    continue
            tuple_dict={}
            chunk_miss_flag=0
            miss_beg_flag=0
            pre_tuple=video_itag_dict[itag][0].stream_tuple
            mix_count=0
            cons_chunk_count=0
            cons_video_itag_val=[]
            cons_video_itag_tuple_val=[]
            for i in range(0,len(video_itag_dict[itag])):
                if video_itag_dict[itag][i].stream_tuple!=pre_tuple:
                    #记录连续块数量
                    cons_video_itag_val.append(cons_chunk_count)
                    cons_video_itag_tuple_val.append(pre_tuple)
                    cons_chunk_count=0
                    #记录混合流的数量
                    if video_itag_dict[itag][i].stream_tuple in tuple_dict:
                        mix_count +=1
                cons_chunk_count +=1
                pre_tuple=video_itag_dict[itag][i].stream_tuple
                #记录该视频采用传输流的数量
                tuple_dict[video_itag_dict[itag][i].stream_tuple]=1

                if i!=0:
                    if video_itag_dict[itag][i-1].range_end+1 != video_itag_dict[itag][i].range_beg:
                        chunk_miss_flag +=1
            if video_itag_dict[itag][0].range_beg!=0:
                miss_beg_flag=1

            #记录最后一个chunk
            cons_video_itag_val.append(cons_chunk_count)
            cons_video_itag_tuple_val.append(pre_tuple)
            finger_valid_val=Finger_valid_val(miss_beg_flag,chunk_miss_flag,len(tuple_dict),mix_count,len((video_itag_dict[itag])),cons_video_itag_val,cons_video_itag_tuple_val)
            finger_valid_dict[itag]=finger_valid_val
        return finger_valid_dict

    def work_stream(self,path):
        video_itag_dict=self.finger_extract(path)
        video_itag_dict=self.chunk_sort(video_itag_dict)
        finger_valid_dict=self.finger_valid(video_itag_dict)
        self.get_video_url(path)
        #finger_dick=self.get_finger(video_itag_dict)
        self.video_itag_dict_list[path]=video_itag_dict
        self.finger_valid_dict_list[path]=finger_valid_dict
        #self.record_finger(path,video_itag_dict)

if __name__ == '__main__':
    finger=Finger("/home/local/data1/xuminchao/batch_video_clawer/data/mitm/analysis2.csv","/home/local/data1/xuminchao/batch_video_clawer/data/mitm/finger.csv")
    #finger.from_root_path_get_finger("/home/local/data1/pcap/NAS_40_99/collect_video_fingerprint/chengsiyuan/game")
    finger.from_path_file_get_finger("/home/local/data1/xuminchao/batch_video_clawer/data/mitm_file_path")
    finger.analysis_record()
    