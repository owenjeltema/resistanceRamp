import math
import numpy as np
from statistics import mean, stdev
from scipy.stats import sem

#for all the data at the same level, finds the weighted mean current and average length
def find_means(bins_list, level, bin_mean, bin_length):
    w=0
    net_mean=[]
    avg_length=[]
    mean_length = []
    stdev_length = []
    sterrmean_length = []
    lengthlist1 = []
    lengthlist2 = []
    lengthlist3 = []
    lengthlist4 = []
    lengthlist5 = []
    lengthlist6 = []
    lengthlist7 = []
    
    while w <= len(bins_list):
        v=0
        meann=[]                  # creates list of mean currents (pA) for given level "w"
        length=[]                # creates list of dwell times (s) for a given level "w"
        mult_mean=[]
        while v < len(level):
#when the level is equal to a certain value, it adds the mean current and length of that level to a list, this first creates a list of all the means and lengths for a closed channel, then level one, etc
            if level[v] ==w:
                meann.append(bin_mean[v])
                length.append(bin_length[v])
            v=v+1
#then it multiplies the mean current*length of that opening and divides by the total length of time to find the weighted mean current and adds that to a list of all the means          
            if v == len(level):
                for (a, b) in zip(meann, length):
                    mult_mean.append((a*b))
            
                if len(length) > 0:
                    net_mean.append(sum(mult_mean) / (sum(length)))
 #                   print(w,sum(length),len(length))
                    avg_length.append(sum(length) / len(length))
                    
                    mean_length.append(mean(length))
                else:
                    net_mean.append(0)
                    avg_length.append(0)
                    mean_length.append(0)
                    
                if len(length) > 1:
                    stdev_length.append(stdev(length))
                    sterrmean_length.append(sem(length))
                else:                
                    stdev_length.append(0)
                    sterrmean_length.append(0)
                    
                if w == 1:
                    lengthlist1 = length
                if w == 2:
                    lengthlist2 = length
                if w == 3:
                    lengthlist3 = length
                if w == 4:
                    lengthlist4 = length
                if w == 5:
                    lengthlist5 = length
                if w == 6:
                    lengthlist6 = length
                if w == 7:
                    lengthlist7 = length

        w=w+1
        v=0
        meann=[]
        length=[]
        mult_mean=[]
        
    return [net_mean, avg_length, mean_length, stdev_length, sterrmean_length, lengthlist1, lengthlist2, lengthlist3, lengthlist4, lengthlist5, lengthlist6, lengthlist7]