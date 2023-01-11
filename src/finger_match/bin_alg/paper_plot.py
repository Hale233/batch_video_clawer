from matplotlib import pyplot as plt
from matplotlib import font_manager

def hist_plt():
        file=open("/Users/hale/PycharmProjects/batch_video_clawer/data/paper_plt/size_res.csv",mode='r',encoding='utf-8')
        file_datas=file.read()
        datas=file_datas.split('\n')
        Y=[]
        for data in datas:
            Y.append(float(data))
        d = 1  
        num_bins = int((max(Y)-min(Y))//d)

        fig,axes=plt.subplots(1,1)
        axes.set_ylabel("PDF")
        axes.set_xlabel(r"$ Chunk_{pred\_size} - Chunk_{real\_size} $"+' (bytes)')
        #axes.set_xlabel("The length different between predicted chunk and real chunk (bytes)")
        plt.hist(Y,num_bins,density=True)
        plt.xticks(range(int(min(Y)),int(max(Y))+10,10))
        plt.grid(alpha=0.4)
        plt.savefig('res_hist.pdf')
        #plt.show()

def zhe_plt():
    file=open("/Users/hale/PycharmProjects/batch_video_clawer/data/paper_plt/chunk_error.csv",mode='r',encoding='utf-8')
    file_datas=file.read()
    datas=file_datas.split('\n')
    finger=[]
    res=[]
    pre_datas=1928
    for data in datas:
        if pre_datas-int(data.split('\t')[1])>200:
            continue
        pre_datas=int(data.split('\t')[1])
        finger.append(int(data.split('\t')[0]))
        res.append(int(data.split('\t')[1]))
    fig,axes=plt.subplots(1,1)
    #axes.set_ylabel("$\sin (x)$ The length different between TCP payload and real chunk (bytes)")
    axes.set_ylabel(r"$ TCP_{p\_len} - Chunk_{real\_size} $"+' (bytes)')
    axes.set_xlabel(r"$ TCP_{p\_len} $"+' (bytes)')
    plt.plot(finger,res)
    plt.grid(alpha=0.4)
    plt.savefig('res_TCP.pdf')
    #plt.show()

def multi_zhe_plt():
    file=open("/Users/hale/PycharmProjects/batch_video_clawer/data/paper_plt/bins_orders.csv",mode='r',encoding='utf-8')
    file_datas=file.read()
    datas=file_datas.split('\n')
    X=[]
    Y3,Y4,Y5,Y6=[],[],[],[]
    for data in datas:
        X.append(int(data.split('\t')[0]))
        Y3.append(float(data.split('\t')[2]))
        Y4.append(float(data.split('\t')[3]))
        Y5.append(float(data.split('\t')[4]))
        Y6.append(float(data.split('\t')[5]))
    fig,axes=plt.subplots(1,1)
    axes.set_ylabel('Acc')
    axes.set_xlabel('Number of symbols')
    plt.plot(X,Y3,marker='*',label='3')
    plt.plot(X,Y4,marker='*',label='4')
    plt.plot(X,Y5,marker='*',label='5')
    plt.plot(X,Y6,marker='*',label='6')

    plt.legend(loc="upper right", title=r"$ {win}_{size\_long} $",
           fancybox=True)
    plt.grid(alpha=0.4)
    plt.savefig('bins_orders.pdf')
    #plt.show()

#multi_zhe_plt()