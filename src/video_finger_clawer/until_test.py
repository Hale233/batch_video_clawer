import configparser

class batch_clawer_mitm():
    def __init__(self,conf_path) -> None:
        conf= configparser.ConfigParser()
        conf.read(conf_path,encoding='UTF-8')
        self.tshark_interface_number =conf.get("sofware_path","tshark_interface_number") #"iphone_4g"  #tshark捕包的网络接口名字
        self.chrome_driver_path =conf.get("sofware_path","chrome_driver_path")   #chrom_driver位置
        self.tshark_path =conf.get("sofware_path","tshark_path")  #TSHARK位置
        self.mitmproxy_path=conf.get("sofware_path","mitmproxy_path") #mitmdump 可执行文件位置
        self.mitm_py=conf.get("sofware_path","mitm_py")#mitm.py文件存放位置

        self.root_path =conf.get("record_path","root_path")  #记录根目录
        self.mitm_record_path=conf.get("record_path","mitm_record_path") #mitm记录的文件位置
        self.ping_record_path=conf.get("record_path","ping_record_path")  #ping文件记录位置
        
        self.time_duration=int(conf.get("clawer","time_duration"))    #每一个视频播放时长，单位秒
        self.batch_size=int(conf.get("clawer","batch_size"))     #每一个pcap文件中包含的视频个数,称为一个batch
        self.batch_count=int(conf.get("clawer","batch_count"))      #总共播放多少个batch
        self.video_server=conf.get("clawer","video_server")#tencent bilibili youtube
        self.ping_interval=float(conf.get("ping","ping_interval"))

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'}
        #self.driver=self.chrome_driver_init()
        self.video_url=[]   #一批视频爬取URL
    
    def out_put(self):
        print(self.ping_interval)

clawer=batch_clawer_mitm("E:\\code_project\\video_title_classification\\batch_video_clawer\\bin\\vdieo_title_clawer.conf")
clawer.out_put()