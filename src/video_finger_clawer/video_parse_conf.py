import configparser

class Video_parse():
    def __init__(self,video_server_conf) -> None:
        conf= configparser.ConfigParser()
        conf.read(video_server_conf,encoding='UTF-8')
        #info
        self.video_server_name =conf.get("info","video_server_name") 
        #index_page
        self.index_page_xpath =conf.get("index_page","index_page_xpath") 
        #video_page
        self.duration_xpath =conf.get("video_page","duration_xpath") 
        self.video_player_button =conf.get("video_page","video_player_button") 
        