#从离线的mitm文件中按流提取出音视频块信息，并记录
import os 

#记录每一个块的信息
class Chunk_data():
    def __init__(self,chunk_len,chunk_type) -> None:
        self.chunk_len=chunk_len
        self.chunk_type=chunk_type

class Get_offchunk():
    def __init__(self,record_path) -> None:
        #记录所有流的信息，key为五元组，val为chunk_data list
        self.chunk_dict={}
        self.record_path=record_path
    
    def get_filelist(self,path):
        Filelist = []
        dirs = os.listdir(path)
        for dir in dirs:
            Filelist.append(os.path.join(path, dir))
        return Filelist,dirs
    
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
    def chunk_extract(self,path):
        #
        #key为itag，value为list，list中每一个元素为[range_beg,range_end,len,5tuple,video/audio]
        chunk_dict={}
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
                #itag=request_head[itag_index_beg+5:itag_index_end]
                #video_range=request_head[range_index_beg+6:range_index_end]
                #video_range_beg=int(video_range.split("-")[0])
                #video_range_end=int(video_range.split("-")[1])
                if response_head.find("'Content-Type', b'video")!=-1:
                    video_itag_val=Chunk_data(int(lines[0]),"video")
                elif response_head.find("'Content-Type', b'audio")!=-1:
                    video_itag_val=Chunk_data(int(lines[0]),"audio")
                else:
                    #print(response_head)
                    #print ("\n error!!!!!!!!!!!!!!!!!\n")
                    continue

                if file_names[i] not in chunk_dict:
                    chunk_dict[file_names[i]]=[video_itag_val]
                else:
                    chunk_dict[file_names[i]].append(video_itag_val)
        return chunk_dict
    
    def recrod_chunk(self,chunk_dict):
        record_file=open(self.record_path,mode='a+',encoding='utf-8')
        for tuple,chunk_list in chunk_dict.items():
            record_file.write(str(tuple).replace(",",".").replace("-",">")+',')
            for chunk in chunk_list:
                record_file.write(str(chunk.chunk_len)+'/')
            record_file.write('\n')
    
    def work_stream(self,path):
        chunk_dict=self.chunk_extract(path)
        self.recrod_chunk(chunk_dict)

if __name__ == '__main__':
    get_offchunk=Get_offchunk("/home/local/data1/xuminchao/batch_video_clawer/data/result/analysis2.csv")
    get_offchunk.from_path_file_get_finger("/home/local/data1/xuminchao/batch_video_clawer/data/mitm_file_path")