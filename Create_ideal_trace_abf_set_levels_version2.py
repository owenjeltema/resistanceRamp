import matplotlib.pyplot as plt
import math
import numpy as np
import pyabf
from statistics import mean, stdev
import pandas as pd

#function to determin if two values are in the same bin
from ideal_trace_same_bin_version2 import same_bin
yes=1
no=0
cutoff= 2000
#window_width= 59.999
window_width = 10

#the abf file
abf = pyabf.ABF(r"C:\Users\dcmou\Downloads\work\resistanceRamp\ion_data\23714009.abf")
duration=abf.sweepLengthSec
voltage= 135
#manualy look at the graph and find values that are inbetween the levels
# Bins must be set such that there is at least 1 event in each bin. If any are empty, the code will not function
bins_list=[90, 200, 300]
#do you want to just display the graph with just the filtered data and horizontal lines at bin juctions? (to check if the bin locations are appropriate) (yes/no)
bins_check=no

time_step= duration/ len(abf.sweepY)
abf.sweepY = -1.0*abf.sweepY

#low pass filter
#from low_pass_filter_abf_version2 import low_pass
from low_pass_filter_abf_version1 import low_pass
filtered_sweepY= low_pass(abf.sweepY, abf.sweepX, cutoff, time_step)
#filtered_sweepY = abf.sweepY  # turn off low pass filtering by adding this line and commenting out previous two

if bins_check==1: #yes
#plot the filtered data
    plt.plot(abf.sweepX, filtered_sweepY, linewidth= 0.5)
#create a list of x values, from 0 to duration (120 for abf files)    
    x_values=[]
    x=0
    while x < duration:
        x_values.append(x)
        x=x+1
#runs through loop for for each bin junction
    bin_number=0
    while bin_number < len(bins_list):
        y_values=[]
#creates a list of the y value for that junction that is the appropriate length        
        y=0
        while y < duration:
            y_values.append(bins_list[bin_number])
            y=y+1
#and plots it
        plt.plot(x_values, y_values, 'k', linewidth= 1)
        bin_number=bin_number+1
    plt.axis([0, duration, -4, 4])
    plt.grid()
    plt.show()

#defining lists
level_list=[]
level=[]
bin_index=[]
bin_mean=[]
bin_length=[]
bin_current=[]
#if it isn't checking the bin locations, then it does the rest of the program
if bins_check==0: #no
#v is the index location in the larger list, 0 through 600,000
    v=0
    while v < len(filtered_sweepY):
        # print(v)
#w is the bin number
        w=1
        while w <= len(bins_list) and v < len(filtered_sweepY):
            # print(w)
#runs loop if v less than the first bin junction (closed current), or if it is in bin w. If it is not, then w is increased by one and it tries again until the correct bin has been found
            while v < len(filtered_sweepY) and ((filtered_sweepY[v] <= bins_list[0]) or (w == len(bins_list) and filtered_sweepY[v] >= bins_list[w-1]) or (filtered_sweepY[v] > bins_list[w-1] and filtered_sweepY[v] <= bins_list[w])):
#when t equals 0 it indicates that the list for a certain level is not yet complete
                t=0
#creates a list (bin_current) of all the values in a row in the same bin
                bin_current.append(filtered_sweepY[v])            
                v=v+1              
#if the value at location v is not in the same bin as the one at location v-1, then that is either the start of a new event or noise
#if the length of bin current is greater than (1/ cutoff* 1/time_step), then it follows this piece of code
                if v == len(filtered_sweepY) or len(bin_mean) == 0 or (same_bin(filtered_sweepY[v], filtered_sweepY[v-1], bins_list)!=True and ((same_bin(filtered_sweepY[v], bin_mean[-1], bins_list)==True and len(bin_current) >= (1/cutoff)*(1/time_step)) or same_bin(filtered_sweepY[v], bin_mean[-1], bins_list)!=True and len(bin_current) >= 2*(1/cutoff)*(1/time_step))) and t==0:
#adds the length, mean, index, and level number of that section of code onto a list
                    bin_length.append(len(bin_current))
                    bin_mean.append(mean(bin_current))
                    bin_index.append(v-len(bin_current))
                    if (filtered_sweepY[v-1] <= bins_list[0]):
                        # print("appended 0 to level")
                        level.append(0)
                    if w < len(bins_list) and (filtered_sweepY[v-1] > bins_list[w-1] and filtered_sweepY[v-1] <= bins_list[w]):
                        # print("appended w to level, version 1")
                        level.append(w)
                    if (w == len(bins_list) and filtered_sweepY[v-1] >= bins_list[w-1]):
                        # print("appended w to level, version 2")
                        level.append(w)
#t=1 indicates that the list for a level has been completed
                    t=1                 
                    
#runs this bit of code if there has been a transition that is less than ____ and after the event it returns to the same level (a simple noise spike)                    
                if v < len(filtered_sweepY) and ((len(bin_current) < ((1/cutoff)*(1/time_step))) and (same_bin(filtered_sweepY[v], filtered_sweepY[v-1], bins_list) != True) and (same_bin(filtered_sweepY[v], bin_mean[-1], bins_list)==True)) and (t == 0):
#adds the length and means from the last section to the length and mean from the most recent section (with weighting for the mean)                    
#then removes the previous values from the lists and adds the new ones instead                    
                    new_length= bin_length[-1]+ len(bin_current)
                    bin_length.pop()
                    bin_length.append(new_length)
                    if len(bin_current) > 1:
                        mean_bin= mean(bin_current)
                    if len(bin_current)==1:
                        mean_bin=bin_current[0]
                    new_mean= (bin_mean[-1]*bin_length[-1] + mean_bin*len(bin_current))/ (bin_length[-1] + len(bin_current))
                    bin_mean.pop()
                    bin_mean.append(new_mean)
                    t=1
#if the potential event is less than the decided length and the level before it is not the same as the level after it, then it follows this code
                if v < len(filtered_sweepY) and ((len(bin_current) < (2*(1/cutoff)*(1/time_step))) and (same_bin(filtered_sweepY[v], filtered_sweepY[v-1], bins_list)!=True)) and (same_bin(filtered_sweepY[v], bin_mean[-1], bins_list) != True) and (t == 0):                 
#the are left in th list to be added to the next event
                    t=0
#if t==1, then that list is completed and the mean and length are recorded, so it is cleared for the next event
                if t==1:
                    bin_current=[]              
            w=w+1

#this section of code checks for when the same level is recorded a few times in a row, then adds them together
#it returns the mean, length, index, and levels lists as a list
    # print(level)
    from ideal_trace_combine_repeates_version2 import combine_repeates
    
    result= combine_repeates(bin_mean, bin_length, bin_index, level)
    bin_mean= result[0]
    bin_length= result[1]
    bin_index= result[2]
    level= result[3]

#this finds the average length and weighted mean for each level        
    from ideal_trace_calculate_mean_version2 import find_means
    result= find_means(bins_list, level, bin_mean, bin_length)
    net_mean= result[0]
    avg_length= result[1]
