#takes a list of the average mean of each level, the length of each event and a list of what level each event is at
#to create a list of values for the idealized trace
def make_ideal_Y(bin_length, net_mean, level):
    ideal_Y=[]
    a=0
    b=0
    while a < len(bin_length):
        while b < bin_length[a]:
            if level[a] != -1:
                # print("a", a)
                # print("level[a]", level[a])
                # print("net_mean[level[a]]", net_mean[level[a]])
                ideal_Y.append(net_mean[level[a]])
#if it is at level -1 (the noise level) then it dives it a values slightly lower than the closed current
            if level[a] == -1:
                ideal_Y.append((net_mean[0])-0.5)
            b=b+1
        a=a+1
        b=0
    return ideal_Y
