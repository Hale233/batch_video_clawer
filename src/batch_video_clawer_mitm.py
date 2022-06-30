# -*- coding: utf-8 -*-
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
import subprocess
import os.path
from lxml import etree
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
        self.ping_record_flag=int(conf.get("ping","ping_record_flag"))

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'}
        self.driver=self.chrome_driver_init()
        self.video_url=[]   #一批视频爬取URL

    def __del__(self):
        self.driver.close()

    #初始化chrom driver
    def chrome_driver_init(self):
        options=webdriver.ChromeOptions()
        #options.add_argument('--disable-gpu')
        #options.add_argument("--user-data-dir=C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\selenium_data")
        driver = webdriver.Chrome(executable_path=self.chrome_driver_path,chrome_options=options)
        driver.set_window_size(1000,30000)
        wait = WebDriverWait(driver, 100)
        return driver

    #从主页面获取待爬取的视频URL
    def get_url(self,video_class,main_url):
        batch_size=self.batch_size
        batch_count=self.batch_count
        #受局域网代理不会自动开启关闭影响，每次浏览时都应保证mitmproxy已运行
        mitmCall=[self.mitmproxy_path]
        mitmProc=subprocess.Popen(mitmCall,executable=self.mitmproxy_path)
        self.driver.get(main_url)
        time.sleep(5)
        #driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        for i in range(0,20):
            self.driver.execute_script('window.scrollBy(0,1000)')
            time.sleep(1)
        html=self.driver.page_source.encode("utf-8", "ignore")
        parseHtml = etree.HTML(html)

        if self.video_server=='bilibili':
            #video_urls =driver.find_element_by_xpath('//div[@class="spread-module"]/a').get_attribute("href")
            video_urls = parseHtml.xpath('//div[@class="spread-module"]/a/@href')#bilibili
        elif self.video_server=='tencent':
            video_urls = parseHtml.xpath('//div[@class="list_item"]/a/@href')#tencent
        elif self.video_server=='youtube':
            video_urls = parseHtml.xpath('//a[@id="thumbnail"]/@href')#youtube

        mitmProc.kill()

        if int(len(video_urls)/batch_size) <batch_count:
            batch_count=int(len(video_urls)/batch_size)

        for i in range(0,batch_count):
            self.video_url.clear()
            self.video_url=video_urls[i*batch_size:((i+1)*batch_size)]
            self.batch_down(i,video_class)

    #批量播放视频URL并记录pcap、ping、指纹信息
    def batch_down(self,number,video_name):
        t_time = time.strftime("%H_%M_%S")
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        # create video folder
        video_path = self.root_path + video_name + "\\pcap\\"
        if not os.path.exists(video_path):
            os.makedirs(video_path)
        
        url_path=self.root_path+video_name+"\\url\\"
        if not os.path.exists(url_path):
            os.makedirs(url_path)

        time_name=str(number) + "_" + t_time
        pcap_filename=time_name+".pcap"
        pcap_file_path = video_path +pcap_filename
        url_file_path=url_path+time_name
        url_file=open(url_file_path,mode='a+',encoding='utf-8')
        
        tsharkOut = open(pcap_file_path, "wb")
        tsharkCall = [self.tshark_path, "-F","pcap","-i",self.tshark_interface_number, "-w",
                    pcap_file_path]
        tsharkProc = subprocess.Popen(tsharkCall, stdout=tsharkOut, executable=self.tshark_path)

        mitmCall=[self.mitmproxy_path,"-s",self.mitm_py]
        mitmProc=subprocess.Popen(mitmCall,executable=self.mitmproxy_path)

        for video_url in self.video_url:
            wait = WebDriverWait(self.driver, 100)
            if self.video_server=='bilibili':
                video_url="https:"+video_url#bilibili
                #video_url="https://www.bilibili.com"+video_url#bilibili
                try:
                    self.driver.get(video_url)
                    time.sleep(5)
                    self.driver.find_element_by_class_name("player").click() #点击开始播放
                    html=self.driver.page_source.encode("utf-8", "ignore")
                    parseHtml = etree.HTML(html)
                    video_duration = parseHtml.xpath('//span[@class="bilibili-player-video-time-total"]/text()')
                except:
                    continue

            elif self.video_server=='tencent':
                video_url=video_url
                self.driver.get(video_url)
                time.sleep(5)
                html=self.driver.page_source.encode("utf-8", "ignore")
                parseHtml = etree.HTML(html)
                video_duration = parseHtml.xpath('//txpdiv[@class="txp_time_duration"]/text()')
                #video_duration=driver.find_element_by_xpath('//span[@class="bilibili-player-video-time-total"]').get_attribute() #关闭弹幕
                
            elif self.video_server=='youtube':
                video_url="https://www.youtube.com/"+video_url
                self.driver.get(video_url)
                time.sleep(5)
                html=self.driver.page_source.encode("utf-8", "ignore")
                parseHtml = etree.HTML(html)
                video_duration = parseHtml.xpath('//span[@class="ytp-time-duration"]/text()')#获取视频时长
                duration_of_the_video=self.time_duration

            print (number)
            print(video_url)
            url_file.write(video_url+"\n")
            #获取视频时长
            if len(video_duration)>0:
                time_data=str(video_duration[0]).split(':')
                if len(time_data)==2:
                    video_duration_s=int(time_data[0])*60+int(time_data[1])
                else:
                    video_duration_s=int(time_data[0])*3600+int(time_data[1])*60+int(time_data[2])
            else:
                video_duration_s=-1            
            duration_of_the_video=self.time_duration
            if (video_duration_s<self.time_duration and video_duration_s>0):
                duration_of_the_video=video_duration_s-10

            time.sleep(duration_of_the_video)
        
        mitmProc.kill()
        time.sleep(30)
        tsharkProc.kill()
        time.sleep(5)
        #整理文件
        new_mitm_path=self.root_path + video_name + "\\mitm\\"+time_name+"\\"
        if not os.path.exists(self.root_path + video_name + "\\mitm\\"):
            os.makedirs(self.root_path + video_name + "\\mitm\\")
        os.rename(self.mitm_record_path,new_mitm_path)
        
        if self.ping_record_flag==1:
            new_ping_path=self.root_path + video_name + "\\ping\\"+time_name+"\\"
            if not os.path.exists(self.root_path + video_name + "\\ping\\"):
                os.makedirs(self.root_path + video_name + "\\ping\\")
                os.rename(self.ping_record_path,new_ping_path)
        
    def from_index_get_url(index_path):
        url=[]
        label=[]
        duration=[]
        index_file=open(index_path,mode='r',encoding='utf-8')
        index_datas=index_file.read().split('\n')
        for index_data in index_datas:
            lines=index_data.split('----')
            count=-1
            for line in lines:
                count=count+1
                if count==0:
                    url.append(line)
                if count==1:
                    label.append(line)
                if count==3:
                    duration.append(line)
        return url,label,duration

if __name__ == '__main__':
    conf_path="E:\\code_project\\video_title_classification\\batch_video_clawer\\bin\\vdieo_title_clawer.conf"
    clawer=batch_clawer_mitm(conf_path)

    #clawer.get_url("donghua","https://www.bilibili.com/v/douga/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.1")
    #clawer.get_url("yinyue","https://www.bilibili.com/v/music/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.9")
    #clawer.get_url("zhishi","https://www.bilibili.com/v/knowledge/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.51")
    #clawer.get_url("shishang","https://www.bilibili.com/v/fashion/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.73")
    #clawer.get_url("yule","https://www.bilibili.com/v/ent/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.83")
    #clawer.get_url("fanju","https://www.bilibili.com/anime/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.8")#url+www.bilibili
    #clawer.get_url("guochuang","https://www.bilibili.com/guochuang/?spm_id_from=666.4.b_7072696d6172794368616e6e656c4d656e75.26")#url+www.bilibili
    #clawer.get_url("youxi","https://www.bilibili.com/v/game/?spm_id_from=666.5.b_7072696d6172794368616e6e656c4d656e75.41")
    #clawer.get_url("keji","https://www.bilibili.com/v/tech/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.50")
    clawer.get_url("guichu","https://www.bilibili.com/v/kichiku/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.72")
    clawer.get_url("zixun","https://www.bilibili.com/v/information/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.82")
    #clawer.get_url("wudao","https://www.bilibili.com/v/dance/?spm_id_from=333.851.b_7072696d6172794368616e6e656c4d656e75.24")
    #clawer.get_url("shenghuo","https://www.bilibili.com/v/life/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.54")

    #clawer.get_url("jilupian","https://v.qq.com/channel/doco?listpage=1&channel=doco&sort=18&_all=1")
    #clawer.get_url("dongman","https://v.qq.com/channel/cartoon?listpage=1&channel=cartoon&sort=18&_all=1")
    #clawer.get_url("shaoer","https://v.qq.com/channel/child?listpage=1&channel=child&sort=18&_all=1")
    #clawer.get_url("dianshiju","https://v.qq.com/channel/tv?listpage=1&channel=tv&sort=18&_all=1")
    #clawer.get_url("zongyi","https://v.qq.com/channel/variety?listpage=1&channel=variety&sort=4&_all=1")
    #clawer.get_url("yinyue","https://v.qq.com/channel/music?listpage=1&channel=music&sort=4&_all=1")
    #clawer.get_url("NBA","https://v.qq.com/channel/nba?listpage=1&channel=nba&sort=1")

    #clawer.get_url("liuxing","https://www.youtube.com/feed/trending?bp=6gQJRkVleHBsb3Jl")
    #get_url("shishang","https://www.youtube.com/channel/UCrpQ4p1Ql_hG8rKXIKM1MOQ")
    #get_url("xuexi","https://www.youtube.com/channel/UCtFRv9O2AHqOZjjynzrv-xg")
    #get_url("tiyu","https://www.youtube.com/channel/UCEgdi0XIXXZ-qJOFPf4JSKw")
    #get_url("xinwen","https://www.youtube.com/channel/UCEl0qh9X3kuL1RdFHng497Q")
    #get_url("remen","https://www.youtube.com/feed/explore")
    #get_url("lvyou","https://www.youtube.com/results?search_query=%E6%97%85%E6%B8%B8")
    #get_url("shuma","https://www.youtube.com/results?search_query=%E6%95%B0%E7%A0%81")
    #get_url("wudao","https://www.youtube.com/results?search_query=%E8%88%9E%E8%B9%88")
    #get_url("dongman","https://www.youtube.com/results?search_query=%E5%8A%A8%E6%BC%AB")