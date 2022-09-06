import os

class Finger():
    def __init__(self,analysis_record_path,finger_record_path) -> None:
        #存储每一个视频的finger_valid_dict,key为文件路径
        self.finger_valid_dict_list={}
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
        Filelist,_=self.get_filelist(root_path+"\\mitm")
        for path in Filelist:
            #print(path)
            self.finger_extract(path)

    def finger_extract(self,path):
        #key为itag，value为list，list中每一个元素为[range_beg,range_end,len,4tuple]
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
                    base_data=[video_range_beg,video_range_end,int(lines[0]),file_names[i],"video"]
                elif response_head.find("'Content-Type', b'audio")!=-1:
                    base_data=[video_range_beg,video_range_end,int(lines[0]),file_names[i],"audio"]
                else:
                    #print(response_head)
                    print ("\n error!!!!!!!!!!!!!!!!!\n")
                    continue

                if itag not in video_itag_dict:
                    video_itag_dict[itag]=[base_data]
                else:
                    video_itag_dict[itag].append(base_data)
        video_itag_dict=self.chunk_sort(video_itag_dict)
        finger_valid_dict=self.finger_valid(video_itag_dict)
        finger_dick=self.get_finger(video_itag_dict)
        self.finger_valid_dict_list[path]=finger_valid_dict
        self.record_finger(path,video_itag_dict)
    
    #记录指纹值
    def record_finger(self,path,video_itag_dict):
        recoed_file=open(self.finger_record_path,mode='a+',encoding='utf-8')
        for itag,chunk_list in video_itag_dict.items():
            if len(chunk_list)<=2:
                continue
            recoed_file.write(str(path)+","+str(itag)+",")
            tuple_dict={}
            chunk_type={}
            for data in chunk_list:
                chunk_type[data[4]]=1
            if len(chunk_type)!=1:
                print ("type error!!!!!!!!!!!!!!!!!!!!!!!!!")
                return
            recoed_file.write(str(chunk_list[0][4])+",")
            for data in chunk_list:
                tuple_dict[data[3]]=1
                recoed_file.write("/"+str(data[2]))
            recoed_file.write(",")
            for key,_ in tuple_dict.items():
                recoed_file.write("/"+str(key).replace(",",".").replace("-",">"))
            recoed_file.write("\n")


    #统计分析
    def analysis_record(self):
        finger_valid_dict_list=self.finger_valid_dict_list
        recoed_file=open(self.analysis_record_path,mode='a+',encoding='utf-8')
        miss_first_chunk_count=0
        miss_chunk_count=0
        stream_count=0
        mix_stream_count=0
        video_stream_count=0
        for video_key,video_dict in finger_valid_dict_list.items():
            for itag in video_dict:
                if video_dict[itag][4]>5:
                    recoed_file.write(video_key)
                    #输出累计信息
                    recoed_file.write(str(video_dict[itag][0])+","+str(video_dict[itag][1])+","+str(video_dict[itag][2])+","+str(video_dict[itag][3])+","+str(video_dict[itag][4]))
                    #输出连续块列表
                    for val in video_dict[itag][5]:
                        recoed_file.write(","+str(val))
                    recoed_file.write("\n")
                    #统计
                    video_stream_count +=1
                    if video_dict[itag][0]!=0:
                        miss_first_chunk_count +=1
                    if video_dict[itag][1]!=0:
                        miss_chunk_count +=1
                    if video_dict[itag][2]!=1:
                        stream_count +=1
                    if video_dict[itag][3]!=0:
                        mix_stream_count +=1
        print ("总流数：{}，缺首块的个数{}，多流传输的个数{}，流出现混合的个数{}，缺块流的个数{}".format(video_stream_count,miss_first_chunk_count,stream_count,mix_stream_count,miss_chunk_count))
    
    #提取视频指纹序列
    def get_finger(self,video_itag_dict):
        finger_dick={}
        for itag in video_itag_dict:
            chunk_list=[]
            for i in range(0,len(video_itag_dict[itag])):
                chunk_list.append(video_itag_dict[itag][i][2])
            finger_dick[itag]=chunk_list
        return finger_dick

    #对视频指纹进行排序
    def chunk_sort(self,video_itag_dict):
        for itag in video_itag_dict:
            tuple_dist={}
            tmp_list=[]
            #统计各五元组出现的次数，用于后续去重
            for k in range(0,len(video_itag_dict[itag])):
                if video_itag_dict[itag][k][3] not in tuple_dist:
                    tuple_dist[video_itag_dict[itag][k][3]]=1
                else:
                    tuple_dist[video_itag_dict[itag][k][3]] +=1
            #排序
            for i in range(0,len(video_itag_dict[itag])):
                for j in range(i,len(video_itag_dict[itag])):
                    if video_itag_dict[itag][i][0]>video_itag_dict[itag][j][0]:
                        video_itag_dict[itag][i],video_itag_dict[itag][j]=video_itag_dict[itag][j],video_itag_dict[itag][i]
            #去重,根据五元组出现的次数，保留出现次数多的重复块
            for i in range(0,len(video_itag_dict[itag])-1):
                if video_itag_dict[itag][i][0]==video_itag_dict[itag][i+1][0]:
                    if tuple_dist[video_itag_dict[itag][i][3]]>tuple_dist[video_itag_dict[itag][i+1][3]]:
                        video_itag_dict[itag][i],video_itag_dict[itag][i+1]=video_itag_dict[itag][i+1],video_itag_dict[itag][i]
                else:
                    tmp_list.append(video_itag_dict[itag][i])
            tmp_list.append(video_itag_dict[itag][len(video_itag_dict[itag])-1])
            video_itag_dict[itag]=tmp_list
        return video_itag_dict
    
    #验证视频指纹是否出现缺块或者交叉传输
    def finger_valid(self,video_itag_dict):
        #指纹验证结果字典,key为itag，值为[是否缺首块，块断开的次数，使用流的数量，交叉流数量，块的数量，连续块列表]
        finger_valid_dict={}
        for itag in video_itag_dict:
            tuple_dict={}
            chunk_miss_flag=0
            miss_beg_flag=0
            pre_tuple=video_itag_dict[itag][0][3]
            mix_count=0
            cons_chunk_count=0
            cons_chunk_list=[]
            for i in range(0,len(video_itag_dict[itag])):
                if video_itag_dict[itag][i][3]!=pre_tuple:
                    #记录连续块数量
                    cons_chunk_list.append(cons_chunk_count)
                    cons_chunk_count=0
                    #记录混合流的数量
                    if video_itag_dict[itag][i][3] in tuple_dict:
                        mix_count +=1
                cons_chunk_count +=1
                pre_tuple=video_itag_dict[itag][i][3]
                #记录该视频采用传输流的数量
                tuple_dict[video_itag_dict[itag][i][3]]=1

                if i!=0:
                    if video_itag_dict[itag][i-1][1]+1 != video_itag_dict[itag][i][0]:
                        chunk_miss_flag +=1
            if video_itag_dict[itag][0][0]!=0:
                miss_beg_flag=1

            #记录最后一个chunk
            cons_chunk_list.append(cons_chunk_count)
            finger_valid_dict[itag]=[miss_beg_flag,chunk_miss_flag,len(tuple_dict),mix_count,len((video_itag_dict[itag])),cons_chunk_list]
        return finger_valid_dict
            
if __name__ == '__main__':
    finger=Finger("E:\\code_project\\video_title_classification\\batch_video_clawer\\analysis2.csv","E:\\code_project\\video_title_classification\\batch_video_clawer\\finger.csv")
    finger.from_root_path_get_finger("E:\\pcap_data\\xxg146\\liuxing")
    