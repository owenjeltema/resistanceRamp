import matplotlib.pyplot as plt
import math
import numpy as np
import pyabf
from statistics import mean, stdev
import pandas as pd
import os
import xlsxwriter
import glob

# pip install glob2
# pip install XlsxWriter
# pip install openpyxl
# pip install scipy
from scipy.stats import sem

from Ideal_trace_graph_formatting_version2 import abf_make_a_graph

from low_pass_filter_abf_version1 import low_pass

from ideal_trace_same_bin_version2 import same_bin
from ideal_trace_combine_repeates_version2 import combine_repeates
from ideal_trace_calculate_mean_version2 import find_means
from ideal_trace_make_ideal_Y_list_version2 import make_ideal_Y


# Global varables
# set the filter level
cutoff = 1000
bins_list = [90, 200, 300]

voltage = 123.1
tempature = 26
lipid = ["DOPE"]
pA_levels = [
    0,  # closed
    10,  # closed
    10,  # level 0
    16,  # level 0
    63,  # level 1
    77,  # level 1
    178,  # level 2
    190,  # level 2
    297,  # level 3
    307,  # level 3
    420,  # level 4
    436,  # level 4
    130,  # level reduced 2
    144,  # level reduced 2
    240,  # level reduced 3
    260,  # level reduced 3
    368,  # level reduced 4
    382,  # level reduced 4
]


#####################################################################################
#######################################################################################
#######################################################################################


import numpy as np


def set_level(abf_file):
    global window_width, abf, duration, time_step, filtered_sweepY, net_mean
    global level, bin_index, bin_mean, bin_length

    window_width = 10

    # Load the ABF file and process it
    abf = pyabf.ABF(abf_file)
    duration = abf.sweepLengthSec
    time_step = duration / len(abf.sweepY)
    abf.sweepY = -1.0 * abf.sweepY

    # Apply a low-pass filter
    filtered_sweepY = low_pass(abf.sweepY, abf.sweepX, cutoff, time_step)

    # Initialize result lists
    level, bin_index, bin_mean, bin_length = [], [], [], []

    # Determine bin indices using vectorized operations
    bins_list_np = np.array(bins_list)
    bin_indices = np.digitize(filtered_sweepY, bins_list_np)

    # Track the current bin
    bin_start = 0
    bin_current = []

    def append_bin_data(bin_current, bin_start):
        """Append current bin data to result lists."""
        if bin_current:
            bin_length.append(len(bin_current))
            bin_mean.append(np.mean(bin_current))
            bin_index.append(bin_start)
            level.append(
                bin_indices[bin_start]
                if bin_indices[bin_start] < len(bins_list)
                else len(bins_list)
            )
            return []

    for v, val in enumerate(filtered_sweepY):
        if not bin_current or bin_indices[v] == bin_indices[bin_start]:
            bin_current.append(val)
        else:
            # Handle completed bin
            bin_current = append_bin_data(bin_current, bin_start)
            bin_start = v
            bin_current.append(val)

        # Handle last value
        if v == len(filtered_sweepY) - 1:
            bin_current = append_bin_data(bin_current, bin_start)

    # Combine repeated levels
    result = combine_repeates(bin_mean, bin_length, bin_index, level)
    bin_mean, bin_length, bin_index, level = result

    # Calculate average length and weighted mean for each level
    result = find_means(bins_list, level, bin_mean, bin_length)
    net_mean = result[0]

    # Histogram code


def histogram(start, stop, location, cutoff):
    i = 0
    while i < len(start):
        start_index = np.where(abf.sweepX == start[i])[0][0]
        stop_index = np.where(abf.sweepX == stop[i])[0][0]
        x = start_index
        while x <= stop_index:
            filtered_sweepY[x] = -1
            x += 1
        i += 1

        # create histogram
    plt.hist(filtered_sweepY, bins=1000, range=(-10, 600))
    plt.ylim(0, 1000)
    # plt.title("file: " + location.split("\\")[-1].split(".")[0])
    plt.legend(prop={"size": 10})
    plt.title("DOPE")
    plt.xlabel("pA")
    plt.ylabel("Occurances with 1 kHz Filtering")  # + str(cutoff)
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


# the location on your computer where you want the file and the name of the file
files = os.listdir()
filesPath = os.getcwd()


for file in files:
    if not file.endswith(".abf"):
        continue
    u = input("skip?")
    print(file)
    if u == "yes":
        continue
    location = rf"{filesPath}\{file.split('.')[0]}.xlsx"
    abf_file_number = file.split(".")[0]
    abf = rf"{filesPath}\{file}"
    set_level(abf)
    spike_start.clear()
    spike_stop.clear()
    while True:
        print(file)
        print(len(abf.sweepY))
        userResponse = input("What would you like to do?")
        if userResponse == "done":
            break
        if userResponse == "dr":
            while True:
                ur2 = input("Want to remove noise? ")
                if ur2 == "done":
                    break
                spike_start.append(float(input("Enter Starting Value: ")))
                spike_stop.append(float(input("Enter Ending Value: ")))
                large_spike()

        if userResponse == "graph":
            histogram(spike_start, spike_stop, location, cutoff)
            ideal_Y = make_ideal_Y(bin_length, net_mean, level)
            abf_make_a_graph(
                window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list
            )

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
                ur3 = input(
                    "what file would you like to go to? (year, month, day, file num )"
                )
                location = rf"{filesPath}\{ur3}.xlsx"
                abf = rf"{filesPath}\{ur3}.abf"
                set_level(abf)
                file = ur3 + ".abf"

        if userResponse == "data":
            closed_start = float(input("The lower value for closed: "))
            pA_levels[0] = closed_start
            closed_end = float(input("The upper value for closed: "))
            pA_levels[1] = closed_end

            L0_start = float(input("The lower value for level 0: "))
            pA_levels[2] = L0_start
            L0_end = float(input("The upper value for level 0: "))
            pA_levels[3] = L0_end

            L1_start = float(input("The lower value for level 1: "))
            pA_levels[4] = L1_start
            L1_end = float(input("The upper value for level 1: "))
            pA_levels[5] = L1_end

            L2_start = float(input("The lower value for level 2: "))
            pA_levels[6] = L2_start
            L2_end = float(input("The upper value for level 2: "))
            pA_levels[7] = L2_end

            L3_start = float(input("The lower value for level 3: "))
            pA_levels[8] = L3_start
            L3_end = float(input("The upper value for level 3: "))
            pA_levels[9] = L3_end

            L4_start = float(input("The lower value for level 4: "))
            pA_levels[10] = L4_start
            L4_end = float(input("The upper value for level 4: "))
            pA_levels[11] = L4_end

            R2_start = float(input("The lower value for reduced level 2: "))
            pA_levels[12] = R2_start
            R2_end = float(input("The upper value for reduced level 2: "))
            pA_levels[13] = R2_end

            R3_start = float(input("The lower value for reduced level 3: "))
            pA_levels[14] = R3_start
            R3_end = float(input("The upper value for reduced level 3: "))
            pA_levels[15] = R3_end

            R4_start = float(input("The lower value for reduced level 4: "))
            pA_levels[16] = R4_start
            R4_end = float(input("The upper value for reduced level 4: "))
            pA_levels[17] = R4_end

    ##############################################################################
    #############################################################################
    # Code below works on the excel file
    #
    # varables
    time_closed = 0
    time_level0 = 0
    time_level1 = 0
    time_level2 = 0
    time_level3 = 0
    time_level4 = 0
    time_level_r_2 = 0
    time_level_r_3 = 0
    time_level_r_4 = 0
    total_time = 60
    data_removed = " "
    open_levels = " "

    # calcuates the total time
    # total time is the amount of time in the file - the amount taken out in noise in seconds
    i = 0
    while i < len(spike_start):
        total_time = total_time - (spike_stop[i] - spike_start[i])
        i += 1

    # creates the varable that stores what times were removed
    i = 0
    while i < len(spike_start):
        start = str(spike_start[i])
        end = str(spike_stop[i])
        data_removed = data_removed + start + "-" + end + ", "
        i += 1

    # adds the values that were used in pA_level
    i = 0
    while i < len(pA_levels):
        start = str(pA_levels[i])
        i += 1
        end = str(pA_levels[i])
        i += 1
        open_levels += start + ", " + end + "; "

    # sums up the number of times that each value occurs in the file
    for y in abf.sweepY:
        if y >= pA_levels[0] and y < pA_levels[1]:
            time_closed += 1

        if y >= pA_levels[2] and y <= pA_levels[3]:
            time_level0 += 1

        if y >= pA_levels[4] and y <= pA_levels[5]:
            time_level1 += 1

        if y >= pA_levels[6] and y <= pA_levels[7]:
            time_level2 += 1

        if y >= pA_levels[8] and y <= pA_levels[9]:
            time_level3 += 1

        if y >= pA_levels[10] and y <= pA_levels[11]:
            time_level4 += 1

        if y >= pA_levels[12] and y <= pA_levels[13]:
            time_level_r_2 += 1

        if y >= pA_levels[14] and y <= pA_levels[15]:
            time_level_r_3 += 1

        if y >= pA_levels[16] and y <= pA_levels[17]:
            time_level_r_4 += 1

    time_closed /= 20
    time_level0 /= 20
    time_level1 /= 20
    time_level2 /= 20
    time_level3 /= 20
    time_level4 /= 20
    time_level_r_2 /= 20
    time_level_r_3 /= 20
    time_level_r_4 /= 20

    # all the variables that will be displayed in the excel files

    abf_data = {
        "ABF file number": abf_file_number,
        "tempature(C)": tempature,
        "lipid": lipid,
        "Total Time(s)": total_time,
        "Voltage(mV)": voltage,
        "Time closed(ms)": time_closed,
        "Level 0 time(ms)": time_level0,
        "Level 1 time(ms)": time_level1,
        "Level 2 time(ms)": time_level2,
        "Level 3 time(ms)": time_level3,
        "Level 4 time(ms)": time_level4,
        "Level 2 reduced time(ms)": time_level_r_2,
        "Level 3 reduced time(ms)": time_level_r_3,
        "Level 4 reduced time(ms)": time_level_r_4,
        "Data Removed(s)": data_removed,
        "Limits of open levels currents (pA)": open_levels,
    }

    #    abf_data_zero = {'level': level_zero, 'index':index_zero, 'length (s)': length_zero, 'mean (pA)': mean_zero, 'levels': list_of_levels_zero, 'average length (s)': avg_length_zero, 'level means (pA)': net_mean_zero, 'level amplitude': level_amplitude_zero, 'occurrences': occurrences_zero}

    df1 = pd.DataFrame(
        abf_data,
        columns=[
            "ABF file number",
            "tempature(C)",
            "lipid",
            "Total Time(s)",
            "Voltage(mV)",
            "Time closed(ms)",
            "Level 0 time(ms)",
            "Level 1 time(ms)",
            "Level 2 time(ms)",
            "Level 3 time(ms)",
            "Level 4 time(ms)",
            "Level 2 reduced time(ms)",
            "Level 3 reduced time(ms)",
            "Level 4 reduced time(ms)",
            "Data Removed(s)",
            "Limits of open levels currents (pA)",
        ],
    )

    # here you will need to put the location on your computer where you want the file and the name of the file

    with pd.ExcelWriter(location, engine="xlsxwriter") as writer:
        df1.to_excel(writer, sheet_name="data", index=False)

    print("done")

# goes through director currently in and compiles all excel files in user directory together
path = rf"{os.getcwd()}\\"
filenames = [file for file in os.listdir(path) if file.endswith(".xlsx")]

df = pd.concat(
    [pd.read_excel(path + file) for file in filenames],
    ignore_index=True,
)
df.to_excel("output.xlsx")
