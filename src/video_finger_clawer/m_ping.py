import pandas as pd
from  ping3  import  ping , verbose_ping
import time
import matplotlib.pyplot as plt

def m_ping_fun(record_path,dest_addr: str, count: int = 4, interval: float = 0, *args, **kwargs):
    timeout = kwargs.get("timeout")
    src = kwargs.get("src")
    unit = kwargs.setdefault("unit", "ms")
    i = 0
    time_list=[]
    delay_list=[]
    while i < count or count == 0:
        if interval > 0 and i > 0:
            time.sleep(interval)
        cur_time_sec=time.time()
        delay = ping(dest_addr, seq=i, *args, **kwargs)
        if delay is None:
            time_list.append(cur_time_sec)
            delay_list.append(-1)
        elif delay is False:
            time_list.append(cur_time_sec)
            delay_list.append(-1)
        else:
            time_list.append(cur_time_sec)
            delay_list.append(float(delay)/1000)
            #print("cur_time:{time} {value}{unit}".format(time=cur_time_sec,value=float(delay)/1000, unit=unit))
        i += 1
        #print(i)
    time_list_pd=pd.DataFrame(time_list)
    delay_list_pd=pd.DataFrame(delay_list)
    result= pd.concat([time_list_pd,delay_list_pd],axis=1)
    result.to_csv(record_path,mode='a+',header=False,index=False)
    #return time_list,delay_list

def plt_pic(x,y):
    #plt.title("网线接入")
    plt.xlabel("time")
    plt.ylabel("rtt")
    plt.plot(x, y)
    plt.show()
'''
timeout:丢包时间
interval:发包间隔
count:发包数量
size:icmp包负载大小
'''
#time_list,delay_list=m_ping (record_path= 'E:\\code_project\\batch_video_clawer\\data\\ping\\test.csv',dest_addr='59.44.45.199' ,timeout=0.1 ,interval = 0.001 ,count=1000,size=1)
