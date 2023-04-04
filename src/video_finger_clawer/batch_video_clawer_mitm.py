# -*- coding: utf-8 -*-
from lib2to3.pgen2 import driver
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
import subprocess
import os.path
from lxml import etree
import configparser
from selenium.webdriver.common.by import By

class batch_clawer_mitm():
    def __init__(self,conf_path) -> None:
        conf= configparser.ConfigParser()
        conf.read(conf_path,encoding='UTF-8')
        self.tshark_interface_number =conf.get("sofware_path","tshark_interface_number") #"iphone_4g"  #tshark捕包的网络接口名字
        self.chrome_driver_path =conf.get("sofware_path","chrome_driver_path")   #chromdriver位置 
        self.tshark_path =conf.get("sofware_path","tshark_path")  #TSHARK位置
        self.mitmproxy_path=conf.get("sofware_path","mitmproxy_path") #mitmdump 可执行文件位置
        self.mitm_py=conf.get("sofware_path","mitm_py")#mitm.py文件存放位置
        self.chrome_user_data_path=conf.get("sofware_path","chrome_user_data_path")

        self.root_path =conf.get("record_path","root_path")  #记录根目录
        self.mitm_record_path=conf.get("record_path","mitm_record_path") #mitm记录的文件位置
        self.ping_record_path=conf.get("record_path","ping_record_path")  #ping文件记录位置
        
        self.time_duration=int(conf.get("clawer","time_duration"))    #每一个视频播放时长，单位秒
        self.batch_size=int(conf.get("clawer","batch_size"))     #每一个pcap文件中包含的视频个数,称为一个batch
        self.batch_count=int(conf.get("clawer","batch_count"))      #总共播放多少个batch
        self.video_server=conf.get("clawer","video_server")#tencent bilibili youtube
        self.player_click=int(conf.get("clawer","player_click"))
        self.ping_record_flag=int(conf.get("ping","ping_record_flag"))#是否采集时延信息
        self.mitm_flag=int(conf.get("clawer","mitm_flag"))#是否记录mitm解密后的信息
        self.tshark_flag=int(conf.get("clawer","tshark_flag"))#是否记录流量数据
        self.screenshot_flag=int(conf.get("clawer","screenshot_flag"))#是否记录截图
        self.url_csv_path=conf.get("clawer","url_csv_path")
        self.clawer_video_resolution=str(conf.get("clawer","clawer_video_resolution")).split(',')

        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'}
        self.driver=self.chrome_driver_init()
        self.video_url=[]   #一批视频爬取URL

    def __del__(self):
        self.driver.close()

    #初始化chrom driver
    def chrome_driver_init(self):
        options=webdriver.ChromeOptions()
        #options.add_argument('--disable-gpu')
        options.add_argument("--user-data-dir="+self.chrome_user_data_path)
        driver = webdriver.Chrome(executable_path=self.chrome_driver_path,chrome_options=options)
        driver.set_window_size(1000,30000)
        wait = WebDriverWait(driver, 100)
        return driver

    #持续访问直到成功
    def loop_get_url(self,video_url):
        while True:
            try:
                time.sleep(3)
                self.driver.get(video_url)
                break
            except:
                continue

    #点击视频开始播放
    def player_click_fun(self):
        if self.player_click!=1:
            return
        player_xpath=''
        try:
            if self.video_server=='bilibili':
                player_xpath="player"
            elif self.video_server=='tencent':
                pass
            elif self.video_server=='youtube':
                player_xpath="ytp-play-button"
            else:
                pass
            if player_xpath!='':
                self.driver.find_element_by_class_name(player_xpath).click()
        except:
            print("player click error")

    #获取视频时长
    def get_video_duration(self):
        duration_xpath=''
        if self.video_server=='bilibili':
            duration_xpath='//span[@class="bilibili-player-video-time-total"]/text()'
        elif self.video_server=='tencent':
            duration_xpath='//txpdiv[@class="txp_time_duration"]/text()'
        elif self.video_server=='youtube':
            #duration_xpath='//span[@class="ytp-time-duration"]/text()'
            duration_xpath='//span[starts-with(@class,"ytp-time-duration")]/text()'
        else:
            pass
        
        try:
            if duration_xpath!='':
                #video_duration=self.driver.find_element_by_xpath(duration_xpath).text
                html=self.driver.page_source.encode("utf-8", "ignore")
                parseHtml = etree.HTML(html)
                video_duration=parseHtml.xpath(duration_xpath)
        except:
            video_duration=-1
            print('get video duration error')
        
        #video_duration=self.driver.find_element_by_xpath(duration_xpath).text
        return video_duration

    #确定视频实际播放时长
    def clawer_video_duration(self,video_duration):
        if len(video_duration)>0:
            time_data=str(video_duration[0]).split(':')
            if len(time_data)==2:
                video_duration_s=int(time_data[0])*60+int(time_data[1])
            else:
                video_duration_s=int(time_data[0])*3600+int(time_data[1])*60+int(time_data[2])           
        duration_of_the_video=self.time_duration
        if (video_duration_s<self.time_duration and video_duration_s>0):
            duration_of_the_video=video_duration_s-10
        return duration_of_the_video

    #单个URL爬取
    def clawer_from_url(self,video_class,url):
        self.batch_size=1
        self.batch_count=1
        self.video_url.clear()
        self.video_url.append(url)
        self.video_fingerprint_down(0,video_class)

    #从csv文件中读取url并依次访问
    def clawer_from_csv(self,video_class):
        batch_size=self.batch_size
        batch_count=self.batch_count
        csv_file=open(self.url_csv_path,mode='r',encoding='utf-8')
        csv_data=csv_file.read()
        video_urls=csv_data.split('\n')
        if int(len(video_urls)/batch_size) <batch_count:
            batch_count=int(len(video_urls)/batch_size)

        for i in range(0,batch_count):
            self.video_url.clear()
            self.video_url=video_urls[i*batch_size:((i+1)*batch_size)]
            self.batch_down(i,video_class)

    #从主页面获取待爬取的视频URL
    def get_url(self,video_class,main_url):
        batch_size=self.batch_size
        batch_count=self.batch_count
        #受局域网代理不会自动开启关闭影响，每次浏览时都应保证mitmproxy已运行
        if self.mitm_flag==1:
            mitmCall=[self.mitmproxy_path]
            mitmProc=subprocess.Popen(mitmCall,executable=self.mitmproxy_path)
        self.loop_get_url(main_url)
        time.sleep(5)
        #driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        for i in range(0,2):
            self.driver.execute_script('window.scrollBy(0,1000)')
            time.sleep(1)
        html=self.driver.page_source.encode("utf-8", "ignore")
        parseHtml = etree.HTML(html)

        video_urls=[]
        if self.video_server=='bilibili':
            #video_urls =driver.find_element_by_xpath('//div[@class="spread-module"]/a').get_attribute("href")
            raw_video_urls = parseHtml.xpath('//div[@class="bili-video-card__wrap __scale-wrap"]/a/@href')#bilibili
            for url in raw_video_urls:
                video_urls.append("https:"+str(url))
                #video_urls.append("https://www.bilibili.com"+str(url))
        elif self.video_server=='tencent':
            video_urls = parseHtml.xpath('//div[@class="list_item"]/a/@href')#tencent
        elif self.video_server=='youtube':
            raw_video_urls = parseHtml.xpath('//a[@id="thumbnail"]/@href')#youtube
            #跳过短视频
            for url in raw_video_urls:
                if str(url).__contains__('watch'):
                    video_urls.append("https://www.youtube.com/"+str(url))
        if self.mitm_flag==1:
            mitmProc.kill()

        if int(len(video_urls)/batch_size) <batch_count:
            batch_count=int(len(video_urls)/batch_size)

        for i in range(0,batch_count):
            self.video_url.clear()
            self.video_url=video_urls[i*batch_size:((i+1)*batch_size)]
            self.batch_down(i,video_class)

    #获取视频分辨率信息
    def get_video_resolution(self):
        video_resolution=[]
        try:
            if self.video_server=='youtube':
                #点击设置
                self.driver.find_element_by_xpath('//*[@aria-controls="ytp-id-18"]').click()
                #点击画质
                self.driver.find_element_by_xpath('//*[@id="ytp-id-18"]//*[@class="ytp-menu-label-secondary"]').click()
                time.sleep(0.5)
                #获取分辨率信息
                #info=self.driver.find_element_by_xpath('//*[@id="ytp-id-18"]//*[@class="ytp-menuitem-label"]/div/span').text
                html=self.driver.page_source.encode("utf-8", "ignore")
                parseHtml = etree.HTML(html)
                video_resolution = parseHtml.xpath('//*[@id="ytp-id-18"]//*[@class="ytp-menuitem-label"]/div/span/text()')
                #复原
                self.driver.find_element_by_xpath('//*[@aria-controls="ytp-id-18"]').click()
            else:
                pass
        except:
            print('get resolution error')

        return video_resolution

    #切换视频分辨率
    def video_resolution_switch(self,video_resolution):
        if self.video_server=='youtube':
            #点击设置
            self.driver.find_element_by_xpath('//*[@aria-controls="ytp-id-18"]').click()
            #点击画质
            self.driver.find_element_by_xpath('//*[@id="ytp-id-18"]//*[@class="ytp-menu-label-secondary"]').click()
            time.sleep(0.5)
            #切换分辨率
            element_path='//*[@id="ytp-id-18"]//*[@class="ytp-menuitem-label"]/div/span[text()=\''+str(video_resolution).strip()+'\']'
            self.driver.find_element_by_xpath(element_path).click()
            #复原
            self.driver.find_element_by_xpath('//*[@aria-controls="ytp-id-18"]').click()

    #目标分辨率与存在视频本身包含的分辨率取交集，作为最后的捕获分辨率
    def clawer_resolution_intersection(self,online_video_resolution):
        target_resolution=[]
        res=[]
        for i in range(0,len(self.clawer_video_resolution)):
            resolution_val=int(self.clawer_video_resolution[i])
            if resolution_val==0:
                target_resolution=[]
                target_resolution=online_video_resolution[0:-1]
                break
            elif resolution_val==1:
                target_resolution.append('360')
            elif resolution_val==2:
                target_resolution.append('480')
            elif resolution_val==3:
                target_resolution.append('720')
            elif resolution_val==4:
                target_resolution.append('1080')
        for k in range(0,len(online_video_resolution)):
            for j in range(0,len(target_resolution)):
                if str(online_video_resolution[k]).__contains__(str(target_resolution[j])):
                    res.append(str(online_video_resolution[k]).strip())
                    break
        return res

    #批量播放视频URL并记录pcap、ping、指纹信息
    def video_fingerprint_down(self,number,video_name):
        #创建目录
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        video_path = self.root_path + video_name + "\\pcap\\"
        if not os.path.exists(video_path) and self.tshark_flag==1:
            os.makedirs(video_path)
        url_path=self.root_path+video_name+"\\url\\"
        if not os.path.exists(url_path):
            os.makedirs(url_path)
        screenshot_path=self.root_path+video_name+"\\screenshot\\"
        if not os.path.exists(screenshot_path) and self.screenshot_flag==1:
            os.makedirs(screenshot_path)
        
        #获取视频时长以及分辨率信息
        video_url=self.video_url[0]
        self.loop_get_url(video_url)
        time.sleep(3)
        self.player_click_fun()
        video_duration=-1
        #循环访问loop_count次，直至成功
        loop_count=10
        for i1 in range(0,loop_count):
            if video_duration==-1 or len(video_duration)==0:
                video_duration=self.get_video_duration()
                time.sleep(1)
            else:
                print(video_duration[0])
                break

        video_resolution=[]
        for i2 in range(0,loop_count):
            if len(video_resolution)==0:
                video_resolution=self.get_video_resolution()
                time.sleep(1)
        print (video_resolution)

        if video_duration==-1 or len(video_resolution)==0:
            print ('duration or resolution error')
            return

        target_resolution=self.clawer_resolution_intersection(video_resolution)
        print (target_resolution)
        #确定视频实际播放时长
        duration_of_the_video=self.clawer_video_duration(video_duration)

        for cur_resolution in target_resolution:
            #新建文件名
            t_time = time.strftime("%Y_%m_%d_%H_%M_%S")
            time_name=str(number) + "_" + t_time
            pcap_filename=time_name+".pcap"
            pcap_file_path = video_path +pcap_filename
            url_file_path=url_path+time_name
            url_file=open(url_file_path,mode='a+',encoding='utf-8')

            self.loop_get_url(video_url)
            time.sleep(5)

            if self.tshark_flag==1:
                tsharkOut = open(pcap_file_path, "wb")
                tsharkCall = [self.tshark_path, "-F","pcap","-i",self.tshark_interface_number, "-w", pcap_file_path]
                tsharkProc = subprocess.Popen(tsharkCall, stdout=tsharkOut, executable=self.tshark_path)

            if self.mitm_flag==1:
                mitmCall=[self.mitmproxy_path,"-s",self.mitm_py]
                mitmProc=subprocess.Popen(mitmCall,executable=self.mitmproxy_path)
            
            self.video_resolution_switch(cur_resolution)
            self.player_click_fun()

            url_file.write(str(video_url)+','+str(cur_resolution)+','+str(duration_of_the_video)+"\n")
            
            #播放前截图
            if self.screenshot_flag==1:
                screenshot_png_path=screenshot_path+time_name+'beg.png'
                self.driver.save_screenshot(screenshot_png_path)

            #等待视频播放
            time.sleep(duration_of_the_video)

            #播放后截图
            if self.screenshot_flag==1:
                screenshot_png_path=screenshot_path+time_name+'end.png'
                self.driver.save_screenshot(screenshot_png_path)

            if self.mitm_flag==1:
                mitmProc.kill()
            if self.tshark_flag==1:
                time.sleep(15)
                tsharkProc.kill()
                time.sleep(5)
            #整理文件
            if self.mitm_flag==1:
                new_mitm_path=self.root_path + video_name + "\\mitm\\"+time_name+"\\"
                if not os.path.exists(self.root_path + video_name + "\\mitm\\"):
                    os.makedirs(self.root_path + video_name + "\\mitm\\")
                os.rename(self.mitm_record_path,new_mitm_path)
            
            if self.ping_record_flag==1:
                new_ping_path=self.root_path + video_name + "\\ping\\"+time_name+"\\"
                if not os.path.exists(self.root_path + video_name + "\\ping\\"):
                    os.makedirs(self.root_path + video_name + "\\ping\\")
                    os.rename(self.ping_record_path,new_ping_path)
    
    def batch_down(self,number,video_name):
        t_time = time.strftime("%H_%M_%S")
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        # create video folder
        video_path = self.root_path + video_name + "\\pcap\\"
        if not os.path.exists(video_path) and self.tshark_flag==1:
            os.makedirs(video_path)
        
        url_path=self.root_path+video_name+"\\url\\"
        if not os.path.exists(url_path):
            os.makedirs(url_path)

        time_name=str(number) + "_" + t_time
        pcap_filename=time_name+".pcap"
        pcap_file_path = video_path +pcap_filename
        url_file_path=url_path+time_name
        url_file=open(url_file_path,mode='a+',encoding='utf-8')
        
        #获取视频时长以及分辨率信息
        self.loop_get_url(video_url)
        time.sleep(5)
        self.player_click()
        video_duration=self.get_video_duration()
        video_resolution=self.get_video_resolution()
        target_resolution=self.clawer_resolution_intersection(video_resolution)

        if self.tshark_flag==1:
            tsharkOut = open(pcap_file_path, "wb")
            tsharkCall = [self.tshark_path, "-F","pcap","-i",self.tshark_interface_number, "-w", pcap_file_path]
            tsharkProc = subprocess.Popen(tsharkCall, stdout=tsharkOut, executable=self.tshark_path)

        if self.mitm_flag==1:
            mitmCall=[self.mitmproxy_path,"-s",self.mitm_py]
            mitmProc=subprocess.Popen(mitmCall,executable=self.mitmproxy_path)

        #try:
        m=1
        if m==1:
            for video_url in self.video_url:
                wait = WebDriverWait(self.driver, 100)
                if self.video_server=='bilibili':
                    video_url="https:"+video_url#bilibili
                    #video_url="https://www.bilibili.com"+video_url#bilibili
                    while True:
                        try:
                            time.sleep(3)
                            self.driver.get(video_url)
                            break
                        except:
                            continue
                    time.sleep(5)
                    self.driver.find_element_by_class_name("player").click() #点击开始播放
                    html=self.driver.page_source.encode("utf-8", "ignore")
                    parseHtml = etree.HTML(html)
                    video_duration = parseHtml.xpath('//span[@class="bilibili-player-video-time-total"]/text()')

                elif self.video_server=='tencent':
                    video_url=video_url
                    while True:
                        try:
                            time.sleep(3)
                            self.driver.get(video_url)
                            break
                        except:
                            continue
                    time.sleep(5)
                    html=self.driver.page_source.encode("utf-8", "ignore")
                    parseHtml = etree.HTML(html)
                    video_duration = parseHtml.xpath('//txpdiv[@class="txp_time_duration"]/text()')
                    #video_duration=driver.find_element_by_xpath('//span[@class="bilibili-player-video-time-total"]').get_attribute() #关闭弹幕
                    
                elif self.video_server=='youtube':
                    #video_url="https://www.youtube.com/"+video_url
                    while True:
                        try:
                            time.sleep(3)
                            self.driver.get(video_url)
                            break
                        except:
                            continue
                    time.sleep(5)
                    try:
                        #self.driver.find_element(by=By.CLASS_NAME, value="ytp-play-button").click()
                        if self.player_click==1:
                            self.driver.find_element_by_class_name("ytp-play-button").click()
                    except:
                        print("player error")
                    html=self.driver.page_source.encode("utf-8", "ignore")
                    parseHtml = etree.HTML(html)
                    video_duration = parseHtml.xpath('//span[@class="ytp-time-duration"]/text()')#获取视频时长
                    duration_of_the_video=self.time_duration
                    self.video_resolution_switch()

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
        #except:
        else:
            print("URL error")
        
        if self.mitm_flag==1:
            mitmProc.kill()
        if self.tshark_flag==1:
            time.sleep(30)
            tsharkProc.kill()
            time.sleep(5)
        #整理文件
        if self.mitm_flag==1:
            new_mitm_path=self.root_path + video_name + "\\mitm\\"+time_name+"\\"
            if not os.path.exists(self.root_path + video_name + "\\mitm\\"):
                os.makedirs(self.root_path + video_name + "\\mitm\\")
            os.rename(self.mitm_record_path,new_mitm_path)
        
        if self.ping_record_flag==1:
            new_ping_path=self.root_path + video_name + "\\ping\\"+time_name+"\\"
            if not os.path.exists(self.root_path + video_name + "\\ping\\"):
                os.makedirs(self.root_path + video_name + "\\ping\\")
                os.rename(self.ping_record_path,new_ping_path)

if __name__ == '__main__':
    conf_path="E:\\code_project\\video_title_classification\\batch_video_clawer\\bin\\video_title_clawer.conf"
    clawer=batch_clawer_mitm(conf_path)
    clawer.clawer_from_url('test3.20','https://www.youtube.com/watch?v=gcShBujgsIQ')
    '''
    #clawer.clawer_from_csv("QUIC")
    #clawer.get_url("donghua","https://www.bilibili.com/v/douga/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.1")
    #clawer.get_url("yinyue","https://www.bilibili.com/v/music/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.9")
    #clawer.get_url("zhishi","https://www.bilibili.com/v/knowledge/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.51")
    #clawer.get_url("shishang","https://www.bilibili.com/v/fashion/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.73")
    #clawer.get_url("yule","https://www.bilibili.com/v/ent/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.83")
    #clawer.get_url("fanju","https://www.bilibili.com/anime/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.8")#url+www.bilibili
    #clawer.get_url("guochuang","https://www.bilibili.com/guochuang/?spm_id_from=666.4.b_7072696d6172794368616e6e656c4d656e75.26")#url+www.bilibili
    #clawer.get_url("youxi","https://www.bilibili.com/v/game/?spm_id_from=666.5.b_7072696d6172794368616e6e656c4d656e75.41")
    #clawer.get_url("keji","https://www.bilibili.com/v/tech/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.50")
    #clawer.get_url("guichu","https://www.bilibili.com/v/kichiku/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.72")
    #clawer.get_url("zixun","https://www.bilibili.com/v/information/?spm_id_from=333.5.b_7072696d6172794368616e6e656c4d656e75.82")
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
    #clawer.get_url("shishang","https://www.youtube.com/channel/UCrpQ4p1Ql_hG8rKXIKM1MOQ")
    #clawer.get_url("xuexi","https://www.youtube.com/channel/UCtFRv9O2AHqOZjjynzrv-xg")
    #clawer.get_url("tiyu","https://www.youtube.com/channel/UCEgdi0XIXXZ-qJOFPf4JSKw")
    #clawer.get_url("game","https://www.youtube.com/gaming/trending")
    #clawer.get_url("xinwen","https://www.youtube.com/channel/UCEl0qh9X3kuL1RdFHng497Q")
    #clawer.get_url("remen","https://www.youtube.com/feed/explore")
    #clawer.get_url("lvyou","https://www.youtube.com/results?search_query=%E6%97%85%E6%B8%B8")
    #clawer.get_url("shuma","https://www.youtube.com/results?search_query=%E6%95%B0%E7%A0%81")
    #clawer.get_url("wudao","https://www.youtube.com/results?search_query=%E8%88%9E%E8%B9%88")
    #clawer.get_url("dongman","https://www.youtube.com/results?search_query=%E5%8A%A8%E6%BC%AB")
    '''