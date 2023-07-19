import matplotlib.pyplot as plt
import math
import numpy as np
import pyabf
from statistics import mean, stdev
import pandas as pd
# pip install XlsxWriter
import xlsxwriter
# python -m pip install scipy
from scipy.stats import sem


# functions needed to be inculded 
from ideal_trace_make_ideal_Y_list_version2 import make_ideal_Y
from Ideal_trace_graph_formatting_version2 import abf_make_a_graph
from Create_ideal_trace_abf_set_levels_version2 import (
    voltage,
    duration,
    abf,
    window_width,
    yes,
    no,
    level,
    bin_mean,
    bin_index,
    bin_length,
    filtered_sweepY,
    net_mean,
    bins_list,
    time_step,
)


ideal_Y= make_ideal_Y(bin_length, net_mean, level)
abf_make_a_graph(window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list)


#delete data 
move_forward = input("Do you want to remove data? ")
while move_forward == "yes":
    copy_filtered_sweepy=filtered_sweepY
    copy_sweepx = abf.sweepX
    #need an input to remove data while to keep going 
    start = int(input("Enter starting value: "))    
    stop = int(input("Enter ending value: "))
    start_index= np.where(abf.sweepX == start)[0][0]
    stop_index = np.where(abf.sweepX == stop)[0][0]
    x=start_index
    while x<=stop_index:
        filtered_sweepY[x] = -1
        x+=1
    move_forward = input("Do you want to remove data? ")


abf_make_a_graph(window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list)

#create histogram 
plt.hist(filtered_sweepY,bins=1000, range=(-10,600))
plt.ylim(0, 1000)
plt.title("File: 009")
plt.show()





