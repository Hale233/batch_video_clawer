import numpy as np
def mydtw(x, y, dist=lambda a, b: abs(a - b)):
    len_x = len(x)
    len_y = len(y)
    d = np.ones((len_x, len_y))
    de_val=0
    for i in range(len_x):
        for j in range(len_y):
            if i == 0 and j == 0:
                d[i][j] = dist(x[i], y[j])
            elif i == 0 and j != 0:
                d[i][j] = d[i][j - 1] + dist(x[i], y[j])
            elif i != 0 and j ==0:
                d[i][j] = d[i - 1][j] + dist(x[i], y[j])
            else:
                choice = [d[i - 1][j - 1], d[i][j - 1], d[i - 1][j]]
                #if min(choice)==d[i][j-1]:
                #    de_val +=min(choice)
                #    print (min(choice))
                #choice = [d[i - 1][j - 1], d[i][j - 1]]
                # choice = [d[i - 1][j - 1], d[i - 1][j]]
                d[i][j] = min(choice) + dist(x[i], y[j])
    return d

def dtw_sp(x, y, dist=lambda a, b: abs(a - b)):
    len_x = len(x)
    len_y = len(y)
    d = np.zeros((len_x, len_y))
    res=0
    for i in range(len_x):
        for j in range(len_y):
            d[i][j]=dist(x[i], y[j])
    print (d)
    i=0
    j=0
    while (i!=len_x-1 or j!=len_y-1):
        print(str(i)+' '+str(j)+' '+str(res))
        if j==len_y-1:
            #res +=d[i+1][j]
            i +=1
            #continue
            return res
        if i==len_x-1:
            res +=d[i][j+1]
            j +=1
            continue
        choice = [d[i][j], d[i][j + 1], d[i + 1][j]]
        min_r=min(choice)
        if min_r==d[i][j]:
            i +=1
            j +=1
            res +=min_r
            continue
        if min_r==d[i][j + 1]:
            j +=1
            res +=min_r
            continue
        if min_r==d[i+1][j]:
            i +=1
            res +=min_r
            continue
    res +=d[i][j]
    return res

x=[1,2,3,4,5,6,7]
y=[3,4,5]
#print(mydtw(x,y))
print(dtw_sp(x,y))