import os
import csv
import time

def get_filelist(path):
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

#从腾讯mitm记录数据中清洗数据并提取指纹序列
def Fiddler_record_clean_tencent(record_file_name,raw_path,file_name):
    source_file=open(raw_path,mode='r',encoding='utf-8')
    clean_file=open(record_file_name,mode='a',encoding='utf-8')
    fiddler_file=source_file.read()
    datas=fiddler_file.split('------------------------')
    streams={}
    stream_index = -1
    text_index=0
    match_flag=0
    for data in datas:
        lines=data.split('\n')
        for line in lines:
            index_beg=line.find("index=")
            index_end=line.find("&start=")
            content_index=line.find("Content-Length: ")
            if index_beg!=-1:
                text_index=int(line[int(index_beg+6):int(index_end)])
            if content_index!=-1:
                stream_index = stream_index + 1
                streams[stream_index]=int(line[16:])
    if abs(stream_index-text_index)<5:
        match_flag=1
        print("math_success")
        clean_file.write(file_name+ "\n")
        with open('fingerpint.csv', 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(file_name)
            streams_list = [i for i in streams.values()]
            writer.writerow(streams_list)
            for i in streams:
                if i==0:
                    clean_file.write(str(streams[i]))
                else:
                    clean_file.write(","+str(streams[i]))
            clean_file.write("\n")

    else:
        print("math_failed")
    source_file.close()
    clean_file.close()
    return match_flag

#从B站mitm记录数据中清洗数据并提取指纹序列
def Fiddler_record_clean_Blibili(record_file_name,raw_path,file_name,ip_file_name):
    source_file=open(raw_path,mode='r',encoding='utf-8')
    clean_file=open(record_file_name,mode='a',encoding='utf-8')
    ip_file=open(ip_file_name,mode='a',encoding='utf-8')
    fiddler_file=source_file.read()
    datas=fiddler_file.split('------------------------')
    streams={}
    range_list={}
    stream_index = -1
    range_list_index= -1
    video_stream_id=-1
    audio_stream_id=-1
    va_list=[]
    video_stream=[]
    audio_stream=[]
    ip_list={}
    video_ip_list=[]
    ip_val=''
    #获取Content-Range字段值
    flag=0
    for data in datas:
        if data=='':
            continue
        lines=data.split('\n')
        if flag==0:
            ip_val=lines[0][:lines[0].find(':')]
            flag=1
        else:
            ip_val=lines[1][:lines[1].find(':')]
        for line in lines:
            Range_index=line.find("Content-Range: bytes")
            if Range_index!=-1:
                range_list_index=range_list_index+1
                range_list[range_list_index]=line[21:]
                ip_list[range_list_index]=ip_val

    #获取视频和音频id号
    for i in range_list:
        va_id = int(range_list[i].split('/')[1])#得到视频id号
        if (va_id not in va_list):
            va_list.append(va_id)
        if len(va_list)==2:
            video_stream_id=int(va_list[0])
            audio_stream_id=int(va_list[1])
            if audio_stream_id>video_stream_id:
                temp=video_stream_id
                video_stream_id=audio_stream_id
                audio_stream_id=temp
            break
    #print(str(video_stream_id)+' '+str(audio_stream_id))

    #根据id划分音频和视频流
    for i in range_list:
        va_id=int(range_list[i].split('/')[1])#获取id号
        if va_id==video_stream_id:
            video_stream.append(range_list[i])
            video_ip_list.append(ip_list[i])
            #print(ip_list[i])

        elif va_id==audio_stream_id:
            audio_stream.append(range_list[i])
        else:
            return -1

    #删除前两块
    del video_ip_list[0:2]
    del video_stream[0:2]
    del audio_stream[0:2]

    #视频流ip去重
    video_ip_list=list(set(video_ip_list))
    print(video_ip_list)

    #验证块索引是否连续或缺失
    second_len=int(video_stream[0].split('/')[0].split('-')[1])
    for l in range(1,len(video_stream)):
        len_count = video_stream[l].split('/')[0].split('-')  # 获取起始和终止字节
        if(int(len_count[0])>second_len):#判断是否乱序
            if(int(len_count[0])!=(second_len+1)):
                print('却块'+' '+str(second_len))
                return -1#缺块
        else:
            print('乱序'+' '+str(second_len))
            return -1#乱序
        second_len=int(len_count[1])

    #记录视频流的块指纹
    clean_file.write(file_name + "\n")
    ip_file.write(file_name + "\n")
    for j in range(len(video_ip_list)):
        ip_file.write(video_ip_list[j]+',')
    ip_file.write('\n')

    for k in range(len(video_stream)):
        len_count = video_stream[k].split('/')[0].split('-')  # 获取起始和终止字节
        if k==0:
            #clean_file.write(str(video_stream[k]) + ' ' + str(int(len_count[1]) - int(len_count[0])))
            clean_file.write(str(int(len_count[1])-int(len_count[0])))
        else:
            #clean_file.write("," + str(video_stream[k]) + ' ' + str(int(len_count[1]) - int(len_count[0])))
            clean_file.write(","+str(int(len_count[1])-int(len_count[0])))
    clean_file.write("\n")
    source_file.close()
    ip_file.close()
    return 1

#从单个index文件匹配以title命名的指纹，将指纹库中的title改为时间戳
def rename_title2timestamp(index_file_path,finger_file_path,rename_file_path):
    if os.path.exists(rename_file_path):
        time.sleep(1)
        os.unlink(rename_file_path)

    index_file=open(index_file_path,mode='r',encoding='utf-8')
    finger_file=open(finger_file_path,mode='r',encoding='utf-8')
    rename_file=open(rename_file_path,mode='w',encoding='utf-8')
    index_datas=index_file.read().split('\n')
    finger_datas=finger_file.read().split('\n')
    count=0
    video_name=[]
    finger_list=[]
    for finger_data in finger_datas:
        count=count+1
        if count%2==0:
            finger_list.append(finger_data)
            continue
        for index_data in index_datas:
            if index_data.find(finger_data)!=-1:
                video_name.append(index_data[(int(index_data.find('----'))+4):(int(index_data.find(finger_data))-4)])
                #video_name.append(index_data)
    for i in range(0,len(finger_list)):
        rename_file.write(video_name[i][:-5]+'\n')
        rename_file.write(finger_list[i]+'\n')
    index_file.close()
    finger_file.close()
    rename_file.close()

#从YouTube mitm记录数据中清洗数据并提取指纹序列
def Fiddler_record_clean_youtube(record_file_name,raw_path,file_name):
    source_file=open(raw_path,mode='r',encoding='utf-8')
    clean_file=open(record_file_name,mode='a',encoding='utf-8')
    chunk_analysis_file=open('./data/finger/youtube/chunk_analysis_video.csv',mode='a',encoding='utf-8')
    writer = csv.writer(chunk_analysis_file)
    fiddler_file=source_file.read()
    datas=fiddler_file.split('------------------------')
    range_list=[]
    #获取Range字段值和
    for data in datas:#划分请求块
        lines=data.split('\n')
        range_value=""
        for line in lines:#划分块内的每一行
            index_beg = line.find("&range=")
            index_end = line.find("&rn=")
            va_value=line.find("Content-Type: video/")
            #va_value = line.find("Content-Type: audio/")
            if index_beg != -1:
                range_value = line[int(index_beg + 7):int(index_end)]
                #print(range_value)
            if va_value !=-1 and range_value.find('-')!=-1:
                range_list.append(range_value)
                #print(range_value)

    #验证块索引是否连续或缺失
    if len(range_list)<=0:
        print("无指纹")
        return -1
    second_len=int(range_list[0].split('-')[1])
    for l in range(1,len(range_list)):
        len_count = range_list[l].split('-')  # 获取起始和终止字节
        if(int(len_count[0])>second_len):#判断是否乱序
            if(int(len_count[0])!=(second_len+1)):
                print('缺块'+' '+str(second_len))
                return -1#缺块
        else:
            print('乱序'+' '+str(second_len))
            return -1#乱序
        second_len=int(len_count[1])

    #记录视频流的块指纹
    clean_file.write(file_name + "\n")
    for k in range(len(range_list)):
        len_count = range_list[k].split('-')  # 获取起始和终止字节
        writer.writerow([str(int(len_count[1])-int(len_count[0]))])
        if k==0:
            #clean_file.write(str(video_stream[k]) + ' ' + str(int(len_count[1]) - int(len_count[0])))
            clean_file.write(str(int(len_count[1])-int(len_count[0])))
        else:
            #clean_file.write("," + str(video_stream[k]) + ' ' + str(int(len_count[1]) - int(len_count[0])))
            clean_file.write(","+str(int(len_count[1])-int(len_count[0])))
    clean_file.write("\n")
    source_file.close()
    chunk_analysis_file.close()
    return 1

#腾讯、YouTube、B站提取指纹的主函数
def get_finger_main():
    # rootpath='./data/finger/bilibili/wudao/'
    # rename_title2timestamp(rootpath+'index.txt',rootpath+'fingerpint.txt',rootpath+'fingerpint2.txt')

    #path = './data/finger/tencent/jilupian/'
    #path = './data/finger/bilibili/wudao/'
    path = './data/finger/youtube/youxi/'
    Filelist, filenames = get_filelist(path)
    # mkdir(path+'/feature/')
    count_success = 0
    count_faild = 0
    match_flag = 0

    if os.path.exists(path + "fingerpint_audio.txt"):
        time.sleep(1)
        os.unlink(path + "fingerpint_audio.txt")

    for file_path, filename in zip(Filelist, filenames):
        print(filename[:-4])
        if filename[:-4] == "index" or filename[-4:] != ".txt" or filename[:-4] == "fingerpint2"or filename[:-4] == "fingerpint"or filename[:-4] == "fingerpint_audio":
            print("read file error")
            continue

        #match_flag = Fiddler_record_clean_Blibili(path + "fingerpint2.txt", file_path, filename[:-4],path+'ip_list.txt')
        match_flag = Fiddler_record_clean_youtube(path + "fingerpint_audio.txt", file_path, filename[:-4])
        if match_flag == 1:
            count_success = count_success + 1
        else:
            count_faild = count_faild + 1
        # write_name=path+'/feature/'+filename+'.csv'
    print("success={}  faild={}".format(count_success, count_faild))

#从index文件中获取所有的时间戳名并存为为sapp批处理文件
def from_index_get_pcapname(index_path,record_path,type):
    index_file = open(index_path, mode='r', encoding='utf-8')
    record_file=open(record_path, mode='a+', encoding='utf-8')
    index_datas=index_file.read().split('\n')
    for index_data in index_datas:
        beg=index_data.find('----')
        end=index_data.find('pcap----')
        if beg!=-1:
            record_file.write('./sapp -d -r ../video_title_classification/data/tencent/{}/{} --dumpfile-speed top-speed\n'.format(type,index_data[beg+4:end+4]))
        #print('./sapp -d -r ../video_title_classification/data/tencent/dianshiju/{} --dumpfile-speed top-speed'.format(index_data[beg+4:end+4]))
    index_file.close()
    record_file.close()

#从指纹库文件中提取所有的时间戳名并存为为sapp批处理文件
def from_finger_get_pcapname(finger_path,record_path,type,web):
    index_file = open(finger_path, mode='r', encoding='utf-8')
    record_file = open(record_path, mode='a+', encoding='utf-8')
    index_datas = index_file.read().split('\n')
    count=1
    for index_data in index_datas:
        count = count + 1
        if count % 2 == 1:
            continue
        if index_data=="":
            continue
        record_file.write(
                './sapp -d -r ../video_title_classification/data/{}/{}/{}.pcap --dumpfile-speed top-speed\n'.format(web,
                    type, index_data))
        # print('./sapp -d -r ../video_title_classification/data/tencent/dianshiju/{} --dumpfile-speed top-speed'.format(index_data[beg+4:end+4]))
    index_file.close()
    record_file.close()

def evaluate(csv_root_path,finger_path,csv_manifest_path,distance_path):
    finger_file=open(finger_path,mode='r',encoding='utf-8')
    csv_manifest_file=open(csv_manifest_path,mode='r',encoding='utf-8')
    csvfile=open(distance_path, 'a')
    writer = csv.writer(csvfile)
    csv_filename_list=[]
    label_list=[]
    true_count=0
    false_count=0
    true_distance_mean=0
    false_distance_mean=0
    finger_datas=finger_file.read().split('\n')
    csv_manifest_datas=csv_manifest_file.read().split('\n')
    count=1
    for finger_data in finger_datas:
        count=count+1
        if finger_data=="":
            continue
        if count % 2 == 1:
            continue
        label_list.append(finger_data)

    for csv_manifest_data in csv_manifest_datas:
        csv_filename_list.append(csv_manifest_data[csv_manifest_data.find('TI_2021'):])

    if len(label_list)!=len(csv_filename_list):
        print('长度匹配失败')
        return

    for i in range(0,len(label_list)):
        csv_path=csv_root_path+csv_filename_list[i]

        csv_file=open(csv_path,mode='r',encoding='utf-8')
        csv_datas=csv_file.read().split('\n')
        for csv_data in csv_datas:
            if csv_data=="":
                break
            csv_line=csv_data[csv_data.find('finger_len:')+11:-1]
            finger_len=float(csv_line[:csv_line.find(',')])

            distance=float(csv_data[csv_data.find('distance:')+9:csv_data.find(',finger_len:')])
            #print(distance)
            pre=csv_line[csv_line.find(',')+1:]
            if pre==label_list[i]:
                #writer.writerow([distance/finger_len])
                true_distance_mean=true_distance_mean+distance/finger_len
                true_count=true_count+1
            else:
                writer.writerow([distance/finger_len])
                false_distance_mean=false_distance_mean+distance/finger_len
                false_count=false_count+1
                #print(pre)
                #print('{} {}'.format(csv_path,label_list[i]))
        csv_file.close()

    #print('true={} false={} accuracy={} true_distance_mean={} false_distance_mean={}'.format(true_count,false_count,(true_count/(true_count+false_count)),(true_distance_mean/true_count),(false_distance_mean/false_count)))
    print('true={} false={} accuracy={}'.format(true_count, false_count,(true_count/(true_count+false_count))))
    csvfile.close()
    finger_file.close()
    csv_manifest_file.close()

#结合明文中的ip信息进行过滤音频流后进行评估
def evaluate_ip_filter(csv_root_path,finger_path,csv_manifest_path,ip_list_path):
    finger_file=open(finger_path,mode='r',encoding='utf-8')
    csv_manifest_file=open(csv_manifest_path,mode='r',encoding='utf-8')
    ip_list_file=open(ip_list_path,mode='r',encoding='utf-8')
    #csvfile=open('evaluate_true.csv', 'a')
    #writer = csv.writer(csvfile)
    csv_filename_list=[]
    label_list=[]
    true_count=0
    false_count=0
    ip_list=[]
    finger_datas=finger_file.read().split('\n')
    csv_manifest_datas=csv_manifest_file.read().split('\n')
    ip_list_datas=ip_list_file.read().split('\n')
    count=1
    for finger_data in finger_datas:
        count=count+1
        if finger_data=="":
            continue
        if count % 2 == 1:
            continue
        label_list.append(finger_data)

    count=1
    for ip_list_data in ip_list_datas:
        count=count+1
        if ip_list_data=="":
            continue
        if count % 2 == 0:
            continue
        ip_list.append(ip_list_data)

    for csv_manifest_data in csv_manifest_datas:
        csv_filename_list.append(csv_manifest_data[csv_manifest_data.find('TI_2021'):])

    if len(label_list)!=len(csv_filename_list):
        print('长度匹配失败')
        return

    for i in range(0,len(label_list)):
        csv_path=csv_root_path+csv_filename_list[i]

        csv_file=open(csv_path,mode='r',encoding='utf-8')
        csv_datas=csv_file.read().split('\n')
        for csv_data in csv_datas:
            if csv_data=="":
                break
            dest_ip=csv_data[csv_data.find('>')+1:csv_data.find(',distance:')]
            dest_ip=dest_ip[:dest_ip.rfind('.')]
            video_ip_datas=ip_list[i].split(',')
            video_stream_flag=0
            for video_ip_data in video_ip_datas:
                #print(video_ip_data+' '+dest_ip)
                if video_ip_data==dest_ip:
                    video_stream_flag=1

            if video_stream_flag==0:
                continue

            csv_line=csv_data[csv_data.find('finger_len:')+11:-1]
            #finger_len=float(csv_line[:csv_line.find(',')])

            #distance=float(csv_data[csv_data.find('distance:')+9:csv_data.find(',finger_len:')])
            #print(distance)
            pre=csv_line[csv_line.find(',')+1:]
            if pre==label_list[i]:
                #writer.writerow([distance/finger_len])
                #true_distance_mean=true_distance_mean+distance/finger_len
                true_count=true_count+1
            else:
                #writer.writerow([distance/finger_len])
                #false_distance_mean=false_distance_mean+distance/finger_len
                false_count=false_count+1
                #print('{} {}'.format(csv_path,label_list[i]))
        csv_file.close()

    #print('true={} false={} accuracy={} true_distance_mean={} false_distance_mean={}'.format(true_count,false_count,(true_count/(true_count+false_count)),(true_distance_mean/true_count),(false_distance_mean/false_count)))
    print('true={} false={} accuracy={}'.format(true_count, false_count,(true_count/(true_count+false_count))))
    #csvfile.close()
    finger_file.close()
    csv_manifest_file.close()

if __name__ == "__main__":
   get_finger_main()

