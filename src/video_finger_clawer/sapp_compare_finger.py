
def finger_extract(path,analysis_record_path):
    # key为itag，value为list，list中每一个元素为[range_beg,range_end,len,4tuple]
    recoed_file=open(analysis_record_path,mode='a+',encoding='utf-8')
    i=1
    if (i==1):
        mitm_file = open(path, mode='r', encoding='utf-8')
        mitm_file_data = mitm_file.read()
        info_chunks = mitm_file_data.split('------------------------\n')[:-1]
        for chunk in info_chunks:
            lines = chunk.split('\n')
            request_head = lines[1]
            content_len=lines[0]
            recoed_file.write(content_len)
            recoed_file.write("\n")
            # 提取itag 和 range
            itag_index_beg = int(request_head.find("itag="))
            itag_index_end = int(request_head.find("&", itag_index_beg))
            range_index_beg = int(request_head.find("range="))
            range_index_end = int(request_head.find("&", range_index_beg))
            if itag_index_beg == -1 or range_index_beg == -1:
                print("itag or range not found")
                return
            itag = request_head[itag_index_beg+5:itag_index_end]
            video_range = request_head[range_index_beg+6:range_index_end]
            video_range_beg = int(video_range.split("-")[0])
            video_range_end = int(video_range.split("-")[1])


finger_extract("E:\\pcap_data\\xxg146\\liuxing\\mitm\\14_21_06_48\\192.168.100.47,52268-74.125.98.6,443","finger_52268.csv")