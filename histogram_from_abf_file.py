# Dylan & Sebastian
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

from Create_ideal_trace_abf_set_levels_version2 import (
    abf,
    filtered_sweepY,
)



#delete data Start and stop are arrays 
def histogram(start,stop, location, cutoff):
    i=0
    while i < len(start):
        start_index= np.where(abf.sweepX == start[i])[0][0]
        stop_index = np.where(abf.sweepX == stop[i])[0][0]
        x=start_index
        while x<=stop_index:
            filtered_sweepY[x] = -1
            x+=1
        i+=1

        #create histogram 
    plt.hist(filtered_sweepY,bins=1000, range=(-10,600))
    plt.ylim(0, 1000)
    plt.title("file: " + location.split("\\")[-1].split(".")[0])
    plt.xlabel("Occurances with " + str(cutoff) + "Hz Filtering")
    plt.ylabel("pA")
    plt.show()








