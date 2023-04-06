from time import sleep
from mitmproxy import ctx
import os.path
import m_ping
import multiprocessing
import configparser

class label_core:
    def __init__(self) -> None:
        conf_path= "E:\\code_project\\video_title_classification\\batch_video_clawer\\bin\\video_title_clawer.conf"
        conf= configparser.ConfigParser()
        conf.read(conf_path,encoding='UTF-8')
        self.video_streams={}
        self.mitm_record_path=conf.get("record_path","mitm_record_path") #mitm记录的文件位置
        self.ping_record_path=conf.get("record_path","ping_record_path")  #ping文件记录位置
 
        self.ping_record_flag=int(conf.get("ping","ping_record_flag"))
        self.ping_timeout=float(conf.get("ping","ping_timeout"))
        self.ping_interval=float(conf.get("ping","ping_interval"))
        self.ping_count=int(conf.get("ping","ping_count"))
        self.ping_size=int(conf.get("ping","ping_size"))
        video_parse_conf_file_path=conf.get("clawer","video_parse_conf_file_path")
        
        conf.read(video_parse_conf_file_path,encoding='UTF-8')
        self.video_request_fea =str(conf.get("mitm","video_request_fea")).split(',')
        self.content_len=conf.get("mitm","content_lenth")

        if not os.path.exists(self.mitm_record_path):
            os.makedirs(self.mitm_record_path)
        if not os.path.exists(self.ping_record_path) and self.ping_record_flag==1:
            os.makedirs(self.ping_record_path)

    #记录URL、响应头部、长度到文件中，文件名为五元组
    def record_txt(self,flow,record_file_path):
        request = flow.request
        response=flow.response
        record_file=open(record_file_path,mode='a+',encoding='utf-8')
        if self.content_len!='':
            record_file.write(str(response.headers[self.content_len])+'\n')
        else:
            record_file.write('-1\n')
        record_file.write(str(request.url)+'\n')#请求头
        record_file.write(str(response.headers)+'\n')#响应头
        record_file.write('------------------------\n')

    def response(self,flow):
        # 获取请求和响应对象
        request = flow.request
        #response=flow.response
        video_flag=1
        #info = ctx.log.info # 实例化输出类

        #视频流标注
        for i in range(len(self.video_request_fea)):
            if str(request.url).__contains__(self.video_request_fea[i]):
                pass
            else :
                video_flag=0
        
        if video_flag==1:
            #info('---------------------response---------------------')
            #info(flow.server_conn.sockname)#source IP+port
            #info(flow.server_conn.peername)#destination IP+port
            #info(request.host)
            #info(str(response.headers))
            tuple=str(flow.server_conn.sockname)[2:-1].replace("\', ",",")+"-"+str(flow.server_conn.peername)[2:-1].replace("\', ",",")#such as 172.16.9.38,58163-59.44.45.201,4483
            #info(tuple)
            mitm_record_file_path=self.mitm_record_path+tuple
            if self.ping_record_flag==1:
                ping_record_file_path=self.ping_record_path+tuple
                if tuple not in self.video_streams:
                    self.video_streams[tuple]=1
                    #获取待测量的IP
                    dst_ip=str(flow.server_conn.peername).split(',')[0][2:-1]
                    #ping 多进程
                    ping_process=multiprocessing.Process(target=m_ping.m_ping_fun,kwargs={"record_path":ping_record_file_path,"dest_addr":dst_ip,"timeout":self.ping_timeout,"interval":self.ping_interval,"count":self.ping_count,"size":self.ping_size})
                    ping_process.start()
                    #m_ping.m_ping_fun (record_path=ping_record_file_path,dest_addr=dst_ip ,timeout=0.1 ,interval = 0.001 ,count=10,size=1)
            #创建文件，并把请求URL、响应头部、长度写入
            self.record_txt(flow,mitm_record_file_path)
    
addons = [label_core()]
