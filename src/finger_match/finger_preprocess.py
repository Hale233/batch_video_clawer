from re import X
import matplotlib.pyplot as plt
import numpy as np
class Chunk():
    def __init__(self,finger_list,labels,file_path='') -> None:
        self.finger_list=finger_list
        self.labels=labels
        self.file_path=file_path

class data_Process():
    def __init__(self,online_file,offline_file,audio_thd=600000) -> None:
        self.online_file=online_file
        self.offline_file=offline_file
        self.audio_thd=audio_thd
        self.offline_chunk_list=[]
        self.online_chunk_list=[]
        self.get_offline_finger()
        self.get_online_finger()
        self.small_chunk_clean(self.online_chunk_list)
        self.small_chunk_clean(self.offline_chunk_list)

    def get_offline_finger(self):
        offline_file=open(self.offline_file,mode='r',encoding='utf-8')
        offline_data=offline_file.read()
        offline_datas=offline_data.split('\n')
        for lines in offline_datas:
            if lines=='':
                continue
            vals=lines.split(',')
            file_path=vals[0]#视频文件源路径
            stream_type=vals[2]#video or audio
            finger=vals[3].split('/')[1:]#指纹
            tuples=vals[4].split('/')[1:]#五元组
            if stream_type=='video':
                self.offline_chunk_list.append(Chunk(list(map(int,finger)),tuples,file_path))
            if stream_type=='audio':
                pass
        
    def get_online_finger(self):
        online_file=open(self.online_file,mode='r',encoding='utf-8')
        online_data=online_file.read()
        online_datas=online_data.split('\n')
        for lines in online_datas:
            if lines=='':
                continue
            vals=lines.split(',')
            finger=vals[1].split('/')[:-1]#指纹
            tuples=[vals[0]]#五元组
            self.online_chunk_list.append(Chunk(list(map(int,finger)),tuples))
    
    #过滤掉指纹序列中小于阈值的块
    def small_chunk_clean(self,chunk_list):
        for chunk in chunk_list:
            clean_finger=[]
            for val in chunk.finger_list:
                if val>self.audio_thd:
                    clean_finger.append(val)
            chunk.finger_list=clean_finger

    #分析音视频块的大小分布
    def chunk_plt(self,video_fingers,audio_fingers):
        offline_file=open(self.offline_file,mode='r',encoding='utf-8')
        offline_data=offline_file.read()
        offline_datas=offline_data.split('\n')
        video_fingers=[]
        audio_fingers=[]
        for lines in offline_datas:
            if lines=='':
                continue
            vals=lines.split(',')
            stream_type=vals[2]#video or audio
            finger=vals[3].split('/')[1:]#指纹
            #tuples=vals[4].split('/')[1:]#五元组
            if stream_type=='video':
                video_fingers +=finger
            if stream_type=='audio':
                audio_fingers +=finger
        video_fingers=list(map(int,video_fingers))
        audio_fingers=list(map(int,audio_fingers))
        video_fingers.sort()
        audio_fingers.sort()
        X_v=np.arange(0,len(video_fingers),1)
        X_a=np.arange(0,len(audio_fingers),1)
        plt.plot(X_v,video_fingers)
        plt.plot(X_a,audio_fingers)
        plt.show()

#finger_data=data_Process('/Users/hale/PycharmProjects/batch_video_clawer/data/res/online_encrypted_finger.csv','/Users/hale/PycharmProjects/batch_video_clawer/data/res/finger_store.csv')
