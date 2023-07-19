#from Jun25_ideal_trace import bins_list
import matplotlib.pyplot as plt
import math
import pyabf
import numpy as np
from statistics import mean, stdev
import matplotlib.transforms as tfrms
from matplotlib.widgets import Slider

#formatting for making a graph
def abf_make_a_graph(window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list):
    #for the scrollbar 
    fig, ax = plt.subplots(figsize=(14,4))
    plt.subplots_adjust(bottom=0.25)
    
    #the maximum Y value of the graph
    top_Yvalue= 400
    
    #generates a list of x_values from 0 to 120, for plotting bin junctions(if desired)
    x_values=[]
    x=0
    while x <= duration:
        x_values.append(x)
        x=x+1
    #for each value in the bins_list (the junction between bins), creates a list 0f that number, then plots it with the x_values list
    #the plt command can be commented in and out as necessary
    i=0
    while i < len(bins_list):
        y_values=[]
        y=0
        while y <= duration:
            y_values.append(bins_list[i])
            y=y+1
        plt.plot(x_values, y_values, 'g--')
        i=i+1

    #can plots the unfiltered data or filtered data and the idealized trace
        
    #plt.plot(abf.sweepX, abf.sweepY, 'b', linewidth= 0.5)
    plt.plot(abf.sweepX, filtered_sweepY, 'k', linewidth= 0.75)
    plt.plot(abf.sweepX, ideal_Y, 'r', linewidth=1.25)
    plt.axis([0, max(abf.sweepX), min(ideal_Y)-1, top_Yvalue])
    #scrollbar
    plt.axis([0, window_width, min(ideal_Y)-1, top_Yvalue])
    axpos = plt.axes([.2, 0.1, 0.65, 0.03]) #size of scroll bar--do not mess with
    spos = Slider(axpos, 'Pos', 0, duration-window_width) #starting position and length of scroll
    def update(val):
        pos = spos.val
        ax.axis([pos,pos+window_width, min(ideal_Y)-1, top_Yvalue])
    spos.on_changed(update)
    plt.grid
    return plt.show()


