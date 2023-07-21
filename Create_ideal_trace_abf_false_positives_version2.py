import matplotlib.pyplot as plt
import math
import numpy as np
import pyabf
from statistics import mean, stdev
import pandas as pd
import os
# # pip install XlsxWriter
import xlsxwriter

# python -m pip install scipy
from scipy.stats import sem

from Ideal_trace_graph_formatting_version2 import abf_make_a_graph

from low_pass_filter_abf_version1 import low_pass

from ideal_trace_same_bin_version2 import same_bin
from ideal_trace_combine_repeates_version2 import combine_repeates
from ideal_trace_calculate_mean_version2 import find_means
from ideal_trace_make_ideal_Y_list_version2 import make_ideal_Y


#Global varables
#set the filter level
cutoff = 500
bins_list = [90, 200, 300]
voltage = 123.1


#####################################################################################
#######################################################################################
#######################################################################################



def set_level(abf_file):
# function to determin if two values are in the same bin
    # window_width= 59.999
    global window_width
    window_width = 10

    # the abf file
    global abf
    abf = pyabf.ABF(abf_file)
    global duration
    duration = abf.sweepLengthSec
   

    # do you want to just display the graph with just the filtered data and horizontal lines at bin juctions? (to check if the bin locations are appropriate) (yes/no)
    global time_step
    time_step = duration / len(abf.sweepY)
    abf.sweepY = -1.0 * abf.sweepY

    # low pass filter


    global filtered_sweepY
    filtered_sweepY = low_pass(abf.sweepY, abf.sweepX, cutoff, time_step)
    
    # defining lists
    global level
    level = []
    global bin_index
    bin_index = []
    global bin_mean
    bin_mean = []
    global bin_length 
    bin_length = []
    bin_current = []
    # if it isn't checking the bin locations, then it does the rest of the program
    # v is the index location in the larger list, 0 through 600,000
    v = 0
    while v < len(filtered_sweepY):
        # print(v)
        # w is the bin number
        w = 1
        while w <= len(bins_list) and v < len(filtered_sweepY):
            # print(w)
            # runs loop if v less than the first bin junction (closed current), or if it is in bin w. If it is not, then w is increased by one and it tries again until the correct bin has been found
            while v < len(filtered_sweepY) and (
                (filtered_sweepY[v] <= bins_list[0])
                or (w == len(bins_list) and filtered_sweepY[v] >= bins_list[w - 1])
                or (
                    filtered_sweepY[v] > bins_list[w - 1]
                    and filtered_sweepY[v] <= bins_list[w]
                )
            ):
                # when t equals 0 it indicates that the list for a certain level is not yet complete
                t = 0
                # creates a list (bin_current) of all the values in a row in the same bin
                bin_current.append(filtered_sweepY[v])
                v = v + 1
                # if the value at location v is not in the same bin as the one at location v-1, then that is either the start of a new event or noise
                # if the length of bin current is greater than (1/ cutoff* 1/time_step), then it follows this piece of code
                if (
                    v == len(filtered_sweepY)
                    or len(bin_mean) == 0
                    or (
                        same_bin(filtered_sweepY[v], filtered_sweepY[v - 1], bins_list)
                        != True
                        and (
                            (
                                same_bin(filtered_sweepY[v], bin_mean[-1], bins_list)
                                == True
                                and len(bin_current) >= (1 / cutoff) * (1 / time_step)
                            )
                            or same_bin(filtered_sweepY[v], bin_mean[-1], bins_list)
                            != True
                            and len(bin_current) >= 2 * (1 / cutoff) * (1 / time_step)
                        )
                    )
                    and t == 0
                ):
                    # adds the length, mean, index, and level number of that section of code onto a list
                    bin_length.append(len(bin_current))
                    bin_mean.append(mean(bin_current))
                    bin_index.append(v - len(bin_current))
                    if filtered_sweepY[v - 1] <= bins_list[0]:
                        # print("appended 0 to level")
                        level.append(0)
                    if w < len(bins_list) and (
                        filtered_sweepY[v - 1] > bins_list[w - 1]
                        and filtered_sweepY[v - 1] <= bins_list[w]
                    ):
                        # print("appended w to level, version 1")
                        level.append(w)
                    if (
                        w == len(bins_list)
                        and filtered_sweepY[v - 1] >= bins_list[w - 1]
                    ):
                        # print("appended w to level, version 2")
                        level.append(w)
                    # t=1 indicates that the list for a level has been completed
                    t = 1

                # runs this bit of code if there has been a transition that is less than ____ and after the event it returns to the same level (a simple noise spike)
                if (
                    v < len(filtered_sweepY)
                    and (
                        (len(bin_current) < ((1 / cutoff) * (1 / time_step)))
                        and (
                            same_bin(
                                filtered_sweepY[v], filtered_sweepY[v - 1], bins_list
                            )
                            != True
                        )
                        and (
                            same_bin(filtered_sweepY[v], bin_mean[-1], bins_list)
                            == True
                        )
                    )
                    and (t == 0)
                ):
                    # adds the length and means from the last section to the length and mean from the most recent section (with weighting for the mean)
                    # then removes the previous values from the lists and adds the new ones instead
                    new_length = bin_length[-1] + len(bin_current)
                    bin_length.pop()
                    bin_length.append(new_length)
                    if len(bin_current) > 1:
                        mean_bin = mean(bin_current)
                    if len(bin_current) == 1:
                        mean_bin = bin_current[0]
                    new_mean = (
                        bin_mean[-1] * bin_length[-1] + mean_bin * len(bin_current)
                    ) / (bin_length[-1] + len(bin_current))
                    bin_mean.pop()
                    bin_mean.append(new_mean)
                    t = 1
                # if the potential event is less than the decided length and the level before it is not the same as the level after it, then it follows this code
                if (
                    v < len(filtered_sweepY)
                    and (
                        (len(bin_current) < (2 * (1 / cutoff) * (1 / time_step)))
                        and (
                            same_bin(
                                filtered_sweepY[v], filtered_sweepY[v - 1], bins_list
                            )
                            != True
                        )
                    )
                    and (same_bin(filtered_sweepY[v], bin_mean[-1], bins_list) != True)
                    and (t == 0)
                ):
                    # the are left in th list to be added to the next event
                    t = 0
                # if t==1, then that list is completed and the mean and length are recorded, so it is cleared for the next event
                if t == 1:
                    bin_current = []
            w = w + 1

        # this section of code checks for when the same level is recorded a few times in a row, then adds them together
        # it returns the mean, length, index, and levels lists as a list

        

        result = combine_repeates(bin_mean, bin_length, bin_index, level)
        bin_mean = result[0]
        bin_length = result[1]
        bin_index = result[2]
        level = result[3]

        # this finds the average length and weighted mean for each level
        

        result = find_means(bins_list, level, bin_mean, bin_length)
        global net_mean
        net_mean = result[0]
    
    #Histogram code 

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




# large spike
spike_start = []
spike_stop = []


    # runs this code if there is a large noise spike
def large_spike():
    d = 0
    e = 0
    while e < len(spike_start):
        false_index = 0
        v = round((spike_start[e] / time_step))
        while v < round(spike_stop[e] / time_step):
            c = 0
            # if the index is equal to any number in the bin_index, that means that there is a change of level there
            # while it is within the defined noise spike, that change of level is incorrect, and the value in the level list is replaced by -1
            while c < len(bin_index):
                if bin_index[c] == v:
                    false_index = c
                    level.pop(c)
                    level.insert(c, -1)
                    d = d + 1
                c = c + 1
            v = v + 1

        # the above process also replaces the level for the stretch of closed current after the spike with -1, when it should remain 0
        # the following couple lines of code find the last level changed to -1 in the spike and return it to 0, indicating a closed level
        c = 0
        while c < len(bin_index) - 1:
            if level[c] == -1 and level[c + 1] != -1:
                level.pop(c)
                level.insert(c, 0)
            c = c + 1
        e = e + 1
        

#the location on your computer where you want the file and the name of the file
files = os.listdir()
filesPath = os.getcwd()


for file in files:
    if(file.endswith(".xlsx")):
       continue
    location = rf"{filesPath}\{file.split('.')[0]}.xlsx"
    abf = rf"{filesPath}\{file}"
    set_level(abf)
    spike_start.clear()
    spike_stop.clear()
    while True:
        print(file)
        userResponse =input("What would you like to do?")
        if userResponse == "done":
            break
        if userResponse == "dr":
            while True:
                ur2 = input("Want to remove noise? ")
                if ur2 == "done":
                    break
                spike_start.append(int(input("Enter Starting Value: ")))
                spike_stop.append(int(input("Enter Ending Value: ")))
                large_spike()
            
        if userResponse == "graph":
            histogram(spike_start,spike_stop, location, cutoff)
            ideal_Y= make_ideal_Y(bin_length, net_mean, level)
            abf_make_a_graph(window_width,ideal_Y, abf, filtered_sweepY, duration, bins_list)

        if userResponse == "file":
            ur2 = input("how would you like to search? ")
            if ur2 == "index":
                ur3 = input("what index would you like to go to? ")
                if files[int(ur3)].endswith(".abf"):
                    location = rf"{filesPath}\{files[int(ur3)].split('.')[0]}.xlsx"
                    abf = rf"{filesPath}\{files[int(ur3)]}"
                    set_level(abf)
                    file = files[int(ur3)]
            elif ur2 == "fn":
                ur3 = input("what file would you like to go to? (year, month, day, file num )")
                location = rf"{filesPath}\{ur3}.xlsx"
                abf = rf"{filesPath}\{ur3}.abf"
                set_level(abf)
                file = ur3 + ".abf"


    # all the variables that will be displayed in the excel files
    abf_data = {
        "level": level,
        "index": bin_index,
        "Removed data start": spike_start,
        "Removed data stop": spike_stop,
    }
    #    abf_data_zero = {'level': level_zero, 'index':index_zero, 'length (s)': length_zero, 'mean (pA)': mean_zero, 'levels': list_of_levels_zero, 'average length (s)': avg_length_zero, 'level means (pA)': net_mean_zero, 'level amplitude': level_amplitude_zero, 'occurrences': occurrences_zero}
    df1 = pd.DataFrame(
        abf_data,
        columns=[
            "level",
            "index",
            "start time (s)",
            "length (s)",
            "end time (s)",
            "mean (pA)",
            "transition from",
            "transition to",
        ],
    )
    # here you will need to put the location on your computer where you want the file and the name of the file
    with pd.ExcelWriter(location, engine="xlsxwriter") as writer:
        df1.to_excel(writer, sheet_name="data", index=False)

    print("done")