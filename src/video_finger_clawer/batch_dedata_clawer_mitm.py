# -*- coding: utf-8 -*-
from selenium import webdriver
import time
import datetime
from selenium.webdriver.support.ui import WebDriverWait
import subprocess
import os.path
import json
from lxml import etree
import pyautogui
import shutil
#import hashlib


class batch_clawer_mitm():
    def __init__(self) -> None:
        self.tshark_interface_number ="iphone_4g"#"localnet1"   #tshark捕包的网络接口名字
        self.root_path = "E:\\pcap_data\\"  #记录根目录
        self.chrome_driver_path = "E:\\code_project\\auto_video_player\\chromedriver.exe"   #chrom_driver位置
        self.tshark_path = "D:\\Wireshark\\tshark.exe"  #TSHARK位置
        self.mitmproxy_path="C:\\Users\\admin\\AppData\\Local\\Programs\\Python\\Python39\\Scripts\\mitmdump.exe"#mitmddump 可执行文件位置
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'}
        self.mitm_record_path='E:\\code_project\\batch_video_clawer\\data\\mitm_label_record\\' #mitm记录的文件位置
        self.ping_record_path='E:\\code_project\\batch_video_clawer\\data\\ping\\'  #ping文件记录位置
        #self.driver=self.chrome_driver_init()

    def __del__(self):
        pass
        #self.driver.close()

    #初始化chrom driver
    def chrome_driver_init(self):
        options=webdriver.ChromeOptions()
        driver = webdriver.Chrome(executable_path=self.chrome_driver_path)
        wait = WebDriverWait(driver, 5)
        return driver

    def browse_58(self,driver,main_url):
        max_num_per_type=100
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,10):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//em/a/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url="https://dg.58.com"+video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue
    
    def browse_csdn(self,driver,main_url):
        max_num_per_type=100
        #刷出首页所有商品url
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,30):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//div[@class="active "]/div/a/@href')
        count=0
        print(video_urls)
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url=video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue

    def browse_douban(self,driver,main_url):
        max_num_per_type=200
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,30):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//a[@class="item"]/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url=video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue

    def browse_huanqiu(self,driver,main_url):
        max_num_per_type=30
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,30):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//p[@class="listp"]/a/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url=video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue
        
        video_urls = parseHtml.xpath('//dl[@class="thrNewsList"]/dd/a/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url="https:"+video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue

        video_urls = parseHtml.xpath('//dl[@class="thrNewsList"]/dt/a/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url="https:"+video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue

    def browse_JD(self,driver,main_url):
        max_num_per_type=300
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,30):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//a[@class="more2_lk"]/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url="https:"+video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue

    def browse_taobao(self,driver,main_url):
        max_num_per_type=30
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,30):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//div[@role="listitem"]/a/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url="https:"+video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue
        
    def browse_tieba(self,driver,main_url):
        max_num_per_type=200
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,30):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//div[@class="thread-name-wraper"]/a/@href')
        count=0
        wait = WebDriverWait(driver,3)
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url="https://tieba.baidu.com"+video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue

    def browse_Tmall(self,driver,main_url):
        max_num_per_type=30
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,30):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//li[@class="wonderful-item "]/a/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url="https:"+video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue

    def browse_weibo(self,driver,main_url):
        max_num_per_type=100
        #主页推荐
        driver.get(main_url)
        for i in range(0,100):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        
        #头条推荐
        driver.get("https://weibo.com/?category=1760")
        #time.sleep(20)
        for i in range(0,100):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #每一个头条
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//div[@class="UG_list_b"]/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url=video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            try:
                driver.get(video_url)
                for i in range(0,10):
                    driver.execute_script('window.scrollBy(0,300)')
                    time.sleep(1)
            except:
                continue
    
    def browse_qq(self,driver,main_url):
        max_num_per_type=300
        driver.get(main_url)
        #time.sleep(20)
        for i in range(0,30):
            driver.execute_script('window.scrollBy(0,300)')
            time.sleep(1)
        html=driver.page_source.encode("utf-8", "ignore")
        
        #针对每一个url进行爬取
        parseHtml = etree.HTML(html)
        video_urls = parseHtml.xpath('//ul/li/a/@href')
        count=0
        if len(video_urls)<max_num_per_type:
            max_num_per_type=len(video_urls)-1
        for video_url in video_urls:
            video_url=video_url
            count=count+1
            if count>max_num_per_type:
                break
            print(count)
            print(video_url)
            
            if count>330 and video_url.find("https://new.qq.com/")>=0:
                try:
                    driver.get(video_url)
                    for i in range(0,10):
                        driver.execute_script('window.scrollBy(0,300)')
                        time.sleep(1)
                except:
                    continue

    def browse_download(self):
        time.sleep(100)

    def clawer_main(self,number,type_name,main_url):
        t_time = time.strftime("%H_%M_%S")
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        # create video folder
        pcap_path = self.root_path + type_name + "\\pcap\\"
        if not os.path.exists(pcap_path):
            os.makedirs(pcap_path)

        time_name=str(number) + "_" + t_time
        pcap_filename=str(number) + "_" + t_time+".pcap"
        pcap_file_path = pcap_path +pcap_filename
        
        tsharkOut = open(pcap_file_path, "wb")
        tsharkCall = [self.tshark_path, "-F","pcap","-i",self.tshark_interface_number, "-w",
                    pcap_file_path]
        tsharkProc = subprocess.Popen(tsharkCall, stdout=tsharkOut, executable=self.tshark_path)

        mitmCall=[self.mitmproxy_path,"--rawtcp","--tcp-hosts","\".*\"","-s","E:\\code_project\\batch_video_clawer\\src\\mitmproxy_count.py"]
        mitmCall=self.mitmproxy_path+" --rawtcp --tcp-hosts \".*\" -s E:\\code_project\\batch_video_clawer\\src\\mitmproxy_count.py"
        mitmProc=subprocess.Popen(mitmCall,executable=self.mitmproxy_path)

        driver=self.chrome_driver_init()

        if type_name=="58":
            self.browse_58(driver,main_url)
        elif type_name=="csdn":
            self.browse_csdn(driver,main_url)
        elif type_name=="douban":
            self.browse_douban(driver,main_url)
        elif type_name=="huanqiu":
            self.browse_huanqiu(driver,main_url)
        elif type_name=="JD":
            self.browse_JD(driver,main_url)
        elif type_name=="taobao":
            self.browse_taobao(driver,main_url)
        elif type_name=="tieba":
            self.browse_tieba(driver,main_url)
        elif type_name=="Tmall":
            self.browse_Tmall(driver,main_url)
        elif type_name=="weibo":
            self.browse_weibo(driver,main_url)
        elif type_name=="qq":
            self.browse_qq(driver,main_url)
        elif type_name=="download":
            self.browse_download()
        else:
            self.browse_download()
        
        driver.close()
        mitmProc.kill()
        time.sleep(10)
        tsharkProc.kill()
        time.sleep(5)
        #整理文件
        new_ping_path=self.root_path + type_name + "\\ping\\"+time_name+"\\"
        if not os.path.exists(self.root_path + type_name + "\\ping\\"):
            os.makedirs(self.root_path + type_name + "\\ping\\")
        os.rename(self.ping_record_path,new_ping_path)


clawer=batch_clawer_mitm()
#clawer.clawer_main(1,'58',"https://dg.58.com/")
#clawer.clawer_main(1,"csdn","https://www.csdn.net/")#bad
#clawer.clawer_main(1,"douban","https://movie.douban.com/")
#clawer.clawer_main(1,"huanqiu","https://www.huanqiu.com/")
#clawer.clawer_main(1,"JD","https://www.jd.com/")
#clawer.clawer_main(1,"tieba","https://tieba.baidu.com/")
#clawer.clawer_main(4,"wangyiyun","")
clawer.clawer_main(6,"download","")
#clawer.clawer_main(2,"GIF","")