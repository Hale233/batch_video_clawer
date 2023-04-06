# 指纹采集

## 一、程序设计：

该程序通过selenium控制chrome流量器从视频网址首页爬取视频URL列表，并依次对列表中的URL进行浏览。在浏览过程中通过tshark记录原始pcap数据包、通过mitmproxy对数据包进行解密后使用DPI技术识别出视频流并记录指纹信息、通过对视频流ip发icmp包记录实时的链路rtt信息。具体流程如下：

![Untitled](https://user-images.githubusercontent.com/49126608/230307683-8f4de303-9f64-44ba-868d-fa806a5374f9.png)

## 二、python环境需求：

- selenium 4.1.3
- lxml 4.8.0
- ping3 4.0.3
- mitmproxy 8.1.0

## 三、Windows软件需求：

- chromedriver
1. 该驱动能被python程序调用，实现基于chrome的网页爬虫。可通过该网址进行下载：[http://chromedriver.storage.googleapis.com/index.html](http://chromedriver.storage.googleapis.com/index.html)。下载前先查看本机的chrome版本，并在该网址中找到相应的版本进行下载。
2. 在完成安装后需在C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\目录下创建一个driver的用户浏览目录（目录名字自定义），用于每次爬虫过程中记录cookie信息以及浏览器设置信息，避免每次爬虫前都需重复设置。
3. 由于基于该爬虫程序是基于TCP破密，因此需要在浏览器设置中禁用QUIC协议，具体禁用步骤为：打开chrome浏览器-在地址栏输入chrome://flags/#enable-quic -找到expermentalQUIC protocol 项选择disabled- 重启浏览器（注意：该步骤应在第一次运行主程序的时候进行。在运行主程序时会弹出爬虫驱动的浏览器界面，在该界面中执行该步骤，后续浏览器记录后便无需再执行该步骤）

![Untitled 1](https://user-images.githubusercontent.com/49126608/230307773-6d29e54a-8d7e-4f65-b4a5-00b969d54032.png)


- tshark

该软件用于捕获播放视频过程中产生的流量包。可通过wireshark安装，安装完成后在安装目录下能找到tshark.exe程序。

- mitmproxy

该软件用于代理http流量并进行解密。可通过[https://mitmproxy.org/](https://mitmproxy.org/) 进行安装，建议安装最新的8.0版本。在安装完成后进行如下步骤配置：具体可参考：[https://docs.mitmproxy.org/stable/overview-installation/](https://docs.mitmproxy.org/stable/overview-installation/)

1. 输入mitmproxy –version检查是否安装成功；
2. 通过命令行输入mitmproxy运行代理；
3. 设置局域网代理，具体步骤为：控制面板-internet选项-连接-局域网设置-勾选代理服务器，并设置地址为127.0.0.1，端口8080-确定-应用。具体如下图：
![Untitled 2](https://user-images.githubusercontent.com/49126608/230307835-fcb579a8-3653-44a7-9109-a8ca9837b217.png)


1. 打开[http://mitm.it/](http://mitm.it/)，下载对应的证书并安装。
2. 打开一个网页，检查mitmproxy运行界面是否能捕获到数据包，正常捕获如下图所示：
![Untitled 3](https://user-images.githubusercontent.com/49126608/230307885-a1f2cb7f-b67d-4b5f-b920-1ac8212cb093.png)


## 四、python程序设置

- 配置文件：

配置文件存放于 \batch_video_clawer\bin\vdieo_title_clawer.conf中。具体配置说明如下：
![Untitled 4](https://user-images.githubusercontent.com/49126608/230307939-83f14949-784f-4219-8985-8807cf240965.png)


其中tshark_interface_number为捕包的网络接口名字可通过网络连接界面查看，如下图所示网络接口名为localnet1。注意有多个网络接口时应选择当前正在使用的接口。
![Untitled 5](https://user-images.githubusercontent.com/49126608/230308016-aa874873-2305-45be-b6f5-898e15dca44d.png)


- batch_video_clawer_mitm.py文件设置

在main函数中需要指定配置文件的绝对路径conf_path，以及通过 clawr.get_url(“类别名”,”某分区首页URL”) 来调用函数进行数据采集。该程序会在root_path目录下创建类别名目录，并通过浏览传入的某分区首页URL来批量采集视频列表。
![Untitled 6](https://user-images.githubusercontent.com/49126608/230308069-e9c7e38e-107e-40c6-9906-161073e60413.png)


- mitmproxy_video_label.py 文件设置

需在init函数中定义conf_path的路径。
![Untitled 7](https://user-images.githubusercontent.com/49126608/230308139-be868cea-04fa-4919-9197-718c6febbee6.png)

## 五、运行过程

在完成上述配置步骤后，运行batch_video_clawer_mitm.py文件。

最后运行成功后数据会被记录于root_path目录下，其中每个类别将包含三个文件夹，分别是mitm、pcap、url，具体解释如下：

[Untitled](https://www.notion.so/d5cc309742174462ac855f1f90cccd6a)

同一个视频将对应相同的三个文件夹下相同的文件名

## 六、注意事项

- 在视频开始播放后应关闭自动连播功能，如下图所示：

![Untitled 8](https://user-images.githubusercontent.com/49126608/230308267-dad4e834-55d4-4d39-bc90-ca5e90df767f.png)


- 在运行程序时应保证局域网8080代理开启
- chrome浏览器会自动更新，每次更新后应下载对应版本的chromedriver，否则将无法使用
- 第一次运行主程序时应执行关闭QUIC的操作，以及在播放视频时选择相应的分辨率（后续的视频都会以该分辨率播放）
- 由于chromedriver采用用户自定义存储目录的模式，因此每次浏览的记录都会被保存下来，包括视频的缓存。因此，每次进行爬取时应及时清空浏览器缓存，防止由于存在缓存而导致视频没有按顺序请求的情况
- 当观察到视频网页打开后暂停播放时，应调整配置文件中play_click的值
- 在播放视频时选择1080p的分辨率

[batch_video_clawer](https://www.notion.so/batch_video_clawer-3c87b401b746484aadd5f2c6c340fa72)
