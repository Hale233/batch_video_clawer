import sys
import numpy as np

max_val = sys.maxsize

def find_trace(dis):
    m = np.size(dis, 0)
    n = np.size(dis, 1)
    W = []
    i = m - 1
    j = n - 1
    while i > 0 or j > 0:
        W.append((i, j))

        if i > 0 and j > 0:
            left_down = dis[i-1, j-1]
        else:
            left_down = max_val

        if i > 0:
            down = dis[i-1, j]
        else:
            down = max_val
        
        if j > 0:
            left = dis[i, j-1]
        else:
            left = max_val
        
        min_dis = min(left_down, down, left)

        if min_dis == left_down:
            i -= 1
            j -= 1
        elif min_dis == down:
            i -= 1
        else:
            j -= 1
    W.append((0, 0))
    W = W[::-1]
    return W

def dtw(C, Q):
    assert np.size(C, 1) == np.size(Q, 1)

    m = np.size(C, 0)
    n = np.size(Q, 0)
    dim = np.size(C, 1)

    point_dis = np.zeros((m, n), dtype="float64")
    for i in range(m):
        for j in range(n):
            point_dis[i, j] = np.sqrt(sum([(C[i, k] - Q[j, k]) ** 2 for k in range(dim)]))
    
    warping_dis = np.ones((m, n), dtype="float64") * max_val
    
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                warping_dis[0, 0] = point_dis[0, 0]
                continue

            if i > 0 and j > 0:
                left_down = warping_dis[i-1, j-1]
            else:
                left_down = max_val

            if i > 0:
                down = warping_dis[i-1, j]
            else:
                down = max_val

            if j > 0:
                left = warping_dis[i, j-1]
            else:
                left = max_val

            warping_dis[i, j] = point_dis[i, j] + min(left_down, down, left)

    dis = warping_dis[m-1, n-1]
    W = find_trace(warping_dis)

    return dis, W

if __name__ == "__main__":
    C = np.array([[1, 1], [2, 1]])
    Q = np.array([[1, 1], [2, 1], [2, 1]])
    dis, W = dtw(C, Q)
    print(dis)
    print(W)