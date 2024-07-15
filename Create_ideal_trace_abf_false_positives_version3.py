import matplotlib.pyplot as plt
import math
import numpy as np
import pyabf
from statistics import mean, stdev
import pandas as pd
import os
import xlsxwriter
import glob

# pip install glob

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

'''
Notes:
- I do not believe this program will work in it's current state unless sampling time is 20 kHz. Must be altered eventually to include other sampling frequencies.
- for MacOS or LINUX replace ( rf'blah [backslash] blah [backslash] blah' ) with ( f'blah/blah/blah' )
'''

# Global varables
# set the filter level
cutoff = 5000 # 5000 Hz ideal unless significant noise in sample (based on tests on DOPE data from May 16, 2024)
sampling_frequency = 20000 #Hz
bins_list = [0, 100, 200, 300, 400, 500]

#######################################################################################
#######################################################################################
#######################################################################################


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


def adjustData(start,stop):
    for i in range(len(start)):
        start_index = int(start[i])
        stop_index = int(stop[i]) #this is missing vals for some reason?
        
        x = start_index
        for x in range(stop_index-start_index-1):
            try:
                filtered_sweepY[start_index+x] = -100
            except:
                break


def histogram(start, stop, location, cutoff, lowVal:int=-10, highVal:int=1000,binSize=1):
    #try:
    if not (len(start) == len(stop)):
        raise ValueError("The start and stop lists must be of the same length.")
    for i in range(len(start)):
        try:
            # Ensure start and stop times are within the range of abf.sweepX
            start_index = int(start[i])
            stop_index = int(stop[i])

            # Ensure indices are in the correct order
            if start_index > stop_index:
                raise ValueError(
                    f"Start index {start_index} is greater than stop index {stop_index}"
                )

            # Mark the filtered values within the specified range
            filtered_sweepY[start_index : stop_index] = -100
        except ValueError as ve:
            print(f"Error processing interval {i}: {ve}")

    # Create histogram
    numberOfBins = round((highVal - lowVal)/binSize)
    plt.hist(filtered_sweepY, bins=numberOfBins,range=(lowVal, highVal))
    plt.ylim(0, 1000)
    plt.title(lipid)
    plt.xlabel("pA")
    plt.ylabel(
        "Occurrences with " + str(cutoff) + " Hz Filtering"
    )  # + str(cutoff)
    plt.legend(prop={"size": 10})
    plt.show()

    #except Exception as e:
        #print(f"An error occurred: {e}")

# large spike
spike_start = []
spike_stop = []


# runs this code if there is a large noise spike
def large_spike(spike_start, spike_stop):
    global level, filtered_sweepY

    try:
        if len(spike_start) != len(spike_stop):
            raise ValueError(
                "The spike_start and spike_stop arrays must be of the same length."
            )

        d = 0
        bin_index_set = set(bin_index)  # Convert bin_index to a set for faster lookup

        # Find nearest indices for spike start and stop values, and update filtered_sweepY
        for e in range(len(spike_start)):
            start_value = spike_start[e]
            if start_value < 0:
                spike_start[e] = 0
            elif start_value > (len(filtered_sweepY)-1):
                spike_start[e] = len(filtered_sweepY)-1
            
            stop_value = spike_stop[e]
            if stop_value < 0:
                spike_stop[e] = 0
            elif stop_value > (len(filtered_sweepY)-1):
                spike_stop[e] = len(filtered_sweepY)-1
        
        counter = 0
        for spike in range(len(spike_start)):
            if spike_start[spike-counter] >= spike_stop[spike-counter]:
                spike_start.pop(spike-counter)
                spike_stop.pop(spike-counter)
                counter += 1

            '''start_value = spike_start[e]
            start_index = np.abs(abf.sweepX - start_value).argmin()
            print(start_index)
            spike_start[e] = abf.sweepX[
                start_index
            ]  # Update spike_start with approximate value

            stop_value = spike_stop[e]
            stop_index = np.abs(abf.sweepX - stop_value).argmin()
            spike_stop[e] = abf.sweepX[
                stop_index
            ]  # Update spike_stop with approximate value

            # Update filtered_sweepY and level
            for v in range(start_index, stop_index + 1):
                if v in bin_index_set:  # Check if v is in bin_index set
                    false_index = bin_index.index(v)
                    level[false_index] = -1
                    d += 1

                if abf.sweepX[v] < spike_start[0] or abf.sweepX[v] > spike_stop[-1]:
                    filtered_sweepY[v] = abf.sweepY[
                        v
                    ]  # Substitute values outside the spikes'''
            
        # Update levels to correct false spikes
        for c in range(len(bin_index) - 1):
            if level[c] == -1 and level[c + 1] != -1:
                level[c] = 0

    except Exception as e:
        print(f"An error occurred: {e}")


def findLevels(start,stop,lowVal,highVal,dynamic_levels:bool):
    adjustData(start,stop)

    #---------------------------------------------------------- These variables should be changed based on file for best performance ----------------------------------------------------------
    min_frequency = 3               # between 3-10 depending on how noisy file is. lower for nice data with less noise.                                                                       |
    reduced_buffer = 5              # 5 for narrow peaks or normally, 10 for wider peaks.                                                                                                     |
    ground_level_max = 15           # maximum that ground level bin is allowed in file.                                                                                                       |
    level_0_max = 60                # maximum that level 0 bin is allowed in file.                                                                                                            |
    level_difference_min = 100      # minimum levels can be seperated by. Set with level 0-1 gap on lowest-temp file (should be slightly smaller than actual gap, maybe 10 pA?).              |
    level_difference_max = 250      # maximum levels can be seperated by. Set with higher level gap on high-temp files (should be slightly larger than actual gap).                           |
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    # For each pA val, find frequency of occurrences

    positiveCapacitanceFrequency = []
    negativeCapacitanceFrequency = []
    for i in range(highVal + 1):
        positiveCapacitanceFrequency.append([i,0]) #gives [val,quant]
    if lowVal < 0:
        for i in range(-lowVal):
            negativeCapacitanceFrequency.append([-1-i,0])
    for i in filtered_sweepY:
        try:
            if round(i) < 0:
                negativeCapacitanceFrequency[-round(i)-1][1] += 1
            else:
                positiveCapacitanceFrequency[round(i)][1] += 1
        except:
            pass

    lipidCapacitanceFrequency = negativeCapacitanceFrequency[::-1] + positiveCapacitanceFrequency

    level_bins = []

    levels = [1,2,3,4,5] # does not include ground or zero
    reduced_levels = [1,2,3,4,5]

    level_maxima = [] # does include ground and zero
    reduced_level_maxima = [] 

    lipid_levels = []
    default_peak = -100


    # ground level
    ground_level_vals = [capacitances[1] for capacitances in lipidCapacitanceFrequency[:(ground_level_max-lowVal)]]
    try:
        ground_level_center = lowVal + ground_level_vals.index(max(ground_level_vals))
    except:
        ground_level_center = lowVal
    level_maxima.append(ground_level_center)

    # level 0
    level_0_vals = [capacitances[1] for capacitances in lipidCapacitanceFrequency[(ground_level_max-lowVal):(level_0_max-lowVal)]]
    try:
        level_0_center = ground_level_max + level_0_vals.index(max(level_0_vals))
    except:
        raise ValueError('Increase level_0_max. Must be greater than ground_level_max.')
    level_maxima.append(level_0_center)

    low_value_buffer = reduced_buffer + level_maxima[1]-level_maxima[0] # this gets rid of second level 0 occurance
    
    # higher levels
    for level in levels:
        if level_maxima[-1] < lowVal:
            level_center = default_peak
        else:
            level_vals = [capacitances[1] for capacitances in lipidCapacitanceFrequency[(level_maxima[-1]+level_difference_min-lowVal):(level_maxima[-1]+level_difference_max-lowVal)]]
            try:
                level_center = level_maxima[-1] + level_difference_min + level_vals.index(max(level_vals))
                if max(level_vals) < min_frequency:
                    level_center = default_peak
            except:
                level_center = default_peak
        level_maxima.append(level_center)

    for reduced_level in reduced_levels:
        reduced_level_vals = [capacitances[1] for capacitances in lipidCapacitanceFrequency[(level_maxima[reduced_level]-lowVal):(level_maxima[reduced_level + 1]-lowVal)]]
        min_reduced_range = default_peak
        max_reduced_range = default_peak
        for occurances in reduced_level_vals:
            if occurances < min_frequency:
                min_reduced_range = level_maxima[reduced_level]-lowVal+reduced_level_vals.index(occurances)+low_value_buffer
                break
        if min_reduced_range != min_frequency:
            for occurances in reduced_level_vals[::-1]:
                if occurances < min_frequency:
                    max_reduced_range = level_maxima[reduced_level + 1]-lowVal-reduced_level_vals.index(occurances)-reduced_buffer
                    break

        if (min_reduced_range == default_peak) or (min_reduced_range >= max_reduced_range):
            try:
                try:
                    min_quantity = min(reduced_level_vals)
                    min_reduced_range = level_maxima[reduced_level]-lowVal+reduced_level_vals.index(min_quantity)
                except:
                    min_quantity = -1
                    min_reduced_range = level_maxima[reduced_level]-lowVal+(level_maxima[reduced_level+1] - level_maxima[reduced_level])
                try:
                    max_range_new = [capacitances[1] for capacitances in lipidCapacitanceFrequency[min_reduced_range+reduced_buffer*2:(level_maxima[reduced_level + 1]-lowVal)]]
                    for capacitance in max_range_new[:]:
                        temp_min_val = 1.5*min_quantity
                        if temp_min_val < min_frequency:
                            temp_min_val = (min_frequency + max(reduced_level_vals))//3
                        if capacitance < temp_min_val:
                            max_reduced_range = (level_maxima[reduced_level + 1]-lowVal)-max_range_new[:].index(capacitance)
                            break
                except:
                    pass
                temp_min_reduced_range = default_peak
                temp_max_reduced_range = min_reduced_range
                try:
                    min_range_new = [capacitances[1] for capacitances in lipidCapacitanceFrequency[(level_maxima[reduced_level]-lowVal):temp_max_reduced_range-reduced_buffer*2]]
                    for capacitance in min_range_new:
                        temp_min_val = 1.5*min_quantity
                        if temp_min_val < min_frequency:
                            temp_min_val = (min_frequency + max(reduced_level_vals))//3
                        if capacitance < temp_min_val:
                            temp_min_reduced_range = (level_maxima[reduced_level]-lowVal)+min_range_new.index(capacitance)
                            break
                except:
                    pass
                temp_max_max = -1
                if max_reduced_range != default_peak:
                    if max_reduced_range == min_reduced_range:
                        max_reduced_range += 1
                    try:
                        new_max_reduced_range = [capacitances[1] for capacitances in lipidCapacitanceFrequency[min_reduced_range+reduced_buffer*2:max_reduced_range]]
                        temp_max_max = max(new_max_reduced_range)
                    except:
                        pass
                temp_min_max = -1
                if temp_min_reduced_range != default_peak:
                    if temp_max_reduced_range == temp_min_reduced_range:
                        temp_max_reduced_range += 1
                    try:
                        new_min_reduced_range = [capacitances[1] for capacitances in lipidCapacitanceFrequency[temp_min_reduced_range:temp_max_reduced_range-reduced_buffer*2]]
                        temp_min_max = max(new_min_reduced_range)
                    except:
                        pass
                if (temp_max_max<0) and (temp_min_max<0):
                    min_reduced_range = default_peak
                    max_reduced_range = default_peak
                    reduced_level_maxima.append(default_peak)
                else:
                    if temp_max_max >= temp_min_max:
                        reduced_level_max = (max_reduced_range-new_max_reduced_range[:].index(temp_max_max))+lowVal
                        reduced_level_maxima.append(reduced_level_max)
                        continue
                    else:
                        reduced_level_max = (temp_min_reduced_range+new_min_reduced_range.index(temp_min_max))+lowVal
                        reduced_level_maxima.append(reduced_level_max)
                        continue
            except:
                reduced_range = [capacitances[1] for capacitances in lipidCapacitanceFrequency[(min_reduced_range-lowVal):(max_reduced_range-lowVal)]]
                try:
                    reduced_max = min_reduced_range+reduced_range.index(max(reduced_range))
                except:
                    reduced_max = default_peak
                reduced_level_maxima.append(reduced_max)
        elif min_reduced_range == default_peak:
            reduced_level_maxima.append(default_peak)
        else:
            reduced_range = [capacitances[1] for capacitances in lipidCapacitanceFrequency[(min_reduced_range-lowVal):(max_reduced_range-lowVal)]]
            try:
                reduced_max = min_reduced_range+reduced_range.index(max(reduced_range))
            except:
                reduced_max = default_peak
            reduced_level_maxima.append(reduced_max)
    
    for maximum in level_maxima:
        level_bin_minimum = maximum
        under_min_frequency = 0
        under_min_quantity = 0
        if (lipidCapacitanceFrequency[maximum-lowVal][1]) < 15:
            under_min_quantity = 1
        while True:
            level_bin_minimum -= 1
            try:
                if lipidCapacitanceFrequency[level_bin_minimum-lowVal][1] < min_frequency:
                    under_min_frequency += 1
                else:
                    under_min_frequency = 0
            except:
                under_min_frequency = 100
            if under_min_frequency > under_min_quantity:
                level_bins.append(level_bin_minimum+1)
                break

        level_bin_maximum = maximum
        under_min_frequency = 0
        while True:
            level_bin_maximum += 1
            try:
                if lipidCapacitanceFrequency[level_bin_maximum-lowVal][1] < min_frequency:
                    under_min_frequency += 1
                else:
                    under_min_frequency = 0
            except:
                under_min_frequency = 100
            if under_min_frequency > under_min_quantity:
                level_bins.append(level_bin_maximum-1)
                break
    
    for maximum in reduced_level_maxima:
        level_bin_minimum = maximum
        under_min_frequency = 0
        under_min_quantity = 0
        if (lipidCapacitanceFrequency[maximum-lowVal][1]) < 15:
            under_min_quantity = 1
        while True:
            level_bin_minimum -= 1
            try:
                if lipidCapacitanceFrequency[level_bin_minimum-lowVal][1] < min_frequency:
                    under_min_frequency += 1
                else:
                    under_min_frequency = 0
            except:
                under_min_frequency = 100
            if under_min_frequency > under_min_quantity:
                level_bins.append(level_bin_minimum+1)
                break

        level_bin_maximum = maximum
        under_min_frequency = 0
        while True:
            level_bin_maximum += 1
            try:
                if lipidCapacitanceFrequency[level_bin_maximum-lowVal][1] < min_frequency:
                    under_min_frequency += 1
                else:
                    under_min_frequency = 0
            except:
                under_min_frequency = 100
            if under_min_frequency > under_min_quantity:
                level_bins.append(level_bin_maximum-1)
                break

    level_bin_minima = level_bins[0::2]
    level_bin_maxima = level_bins[1::2]
    level_maxima = level_maxima + reduced_level_maxima

    if level_bin_minima[1] < level_bin_maxima[0]:
        level_range_min = level_maxima[0]-lowVal
        level_range_max = level_maxima[1]-lowVal
        level_range = [capacitances[1] for capacitances in lipidCapacitanceFrequency[level_range_min:level_range_max]]
        try:
            minimum_point = level_maxima[0] + level_range.index(min(level_range))
        except:
            minimum_point = level_maxima[0]
        level_bin_minima[1] = minimum_point
        level_bin_maxima[0] = minimum_point
    
    for reduced_level in reduced_levels:
        if level_bin_minima[1+len(levels)+reduced_level] > (lowVal+default_peak)/2:
            if level_bin_minima[1+len(levels)+reduced_level] < level_bin_maxima[reduced_level]:
                level_range_min = level_maxima[reduced_level]-lowVal-1
                level_range_max = level_maxima[1+len(levels)+reduced_level]-lowVal
                level_range = [capacitances[1] for capacitances in lipidCapacitanceFrequency[level_range_min:level_range_max]]
                #-------------------------------------------------------
                try:
                    minimum_point = level_range_min + lowVal + level_range.index(min(level_range))
                except:
                    minimum_point = (level_maxima[1+len(levels)+reduced_level] + level_maxima[reduced_level])//2
                #-------------------------------------------------------
                level_bin_minima[1+len(levels)+reduced_level] = minimum_point
                level_bin_maxima[reduced_level] = minimum_point

            if level_bin_maxima[1+len(levels)+reduced_level] > level_bin_minima[reduced_level+1]:
                level_range_min = level_maxima[1+len(levels)+reduced_level]-lowVal-1
                level_range_max = level_maxima[reduced_level+1]-lowVal
                level_range = [capacitances[1] for capacitances in lipidCapacitanceFrequency[level_range_min:level_range_max]]
                #-------------------------------------------------------
                try:
                    minimum_point = level_range_min + lowVal + level_range.index(min(level_range))
                except:
                    minimum_point = (level_maxima[1+len(levels)+reduced_level] + level_maxima[reduced_level+1])//2
                #-------------------------------------------------------
                level_bin_maxima[1+len(levels)+reduced_level] = minimum_point
                level_bin_minima[reduced_level+1] = minimum_point
    
    for level in levels:
        if (level_bin_minima[level+1] > (lowVal+default_peak)/2) and (level_bin_maxima[level] > lowVal):
            overlap_min = level_bin_minima[level+1]
            overlap_max = level_bin_maxima[level]
            if overlap_min < overlap_max:
                level_range_min = level_maxima[level]-lowVal
                level_range_max = level_maxima[level+1]-lowVal
                level_range = [capacitances[1] for capacitances in lipidCapacitanceFrequency[level_range_min:level_range_max]]
                try:
                    minimum_point = level_range_min + lowVal + level_range.index(min(level_range))
                except:
                    minimum_point = level_range_min + lowVal
                level_bin_minima[level+1] = minimum_point
                level_bin_maxima[level] = minimum_point

    
    for level in range(len(level_bin_maxima)):
        if (level_bin_maxima[level] < lowVal) and (level_bin_minima[level] < lowVal):
            level_bin_maxima[level] = default_peak
            level_bin_minima[level] = default_peak
    
    level_bins = []
    for level in range(len(level_bin_maxima)):
        level_bins.append(level_bin_minima[level])
        level_bins.append(level_bin_maxima[level])

    seperator = '     '
    levels_string = 'Levels:' + seperator*3 + '  ' + str(level_bins[0]) + ' < ground < ' + str(level_bins[1]) + seperator + str(level_bins[2]) + ' < level 0 < ' + str(level_bins[3]) + seperator + str(level_bins[4]) + ' < level 1 < ' + str(level_bins[5]) + seperator + str(level_bins[6]) + ' < level 2 < ' + str(level_bins[7])  + '\n' + seperator*4 + '    ' + str(level_bins[8]) + ' < level 3 < ' + str(level_bins[9])  + seperator + str(level_bins[10]) + ' < level 4 < ' + str(level_bins[11])
    levels_string = levels_string + seperator + str(level_bins[12]) + ' < level 5 < ' + str(level_bins[13])
    levels_string = levels_string + '\nReduced levels:' + '         ' + str(level_bins[14]) + ' < level 1r < ' + str(level_bins[15]) + seperator + str(level_bins[16]) + ' < level 2r < ' + str(level_bins[17]) + seperator + str(level_bins[18]) + ' < level 3r < ' + str(level_bins[19]) + seperator + str(level_bins[20]) + ' < level 4r < ' + str(level_bins[21]) 

    levels_string = levels_string + seperator + str(level_bins[22]) + ' < level 5r < ' + str(level_bins[23])
    levels_string = levels_string + '\n'
    print(levels_string)

    return(level_bins)


    '''
    for i in range(len(lipidLevels)-1):
        peakCapacitanceFrequency = [] # List of values a peak can be found within
        negative_correction_coefficient = 0
        if lipidLevels[i] < 0:
            negative_correction_coefficient = -lipidLevels[i]
        for j in range(lipidLevels[i+1]-lipidLevels[i]-negative_correction_coefficient): #CURRENTLY ONLY WORKS FOR BIN LENGTH == 1
            if (lipidLevels[i] + j) >= 0:
                peakCapacitanceFrequency.append(lipidCapacitanceFrequency[lipidLevels[i] + j][1])
            else:
                peakCapacitanceFrequency.append(negativeCapacitanceFrequency[-lipidLevels[i] - j - 1][1])
        peak_center = max(peakCapacitanceFrequency)
        if peak_center < 3: # sets a point where the maximum is too low to claim a minimum
            if i == 0:
                print('Please manually adjust ground level')
            else:
                print('Please manually adjust level '+ str(i-1))
            levels[2*i] = -100
            levels[2*i+1] = -100
            peak_list.append(-100)
        else:
            peak_center_index = peakCapacitanceFrequency.index(peak_center)
            peak = lipidLevels[i] + peak_center_index #sets a center value for what can be considered the peak
            peak_list.append(peak)
            levels[2*i] = peak - 10
            levels[2*i+1] = peak + 10
        if dynamic_levels and (i > 0):
            try:
                if peak_list[i] == -100:
                    continue
                else:
                    dynamic_maximum = 175 #max in range for DOPC
                    if lipid == 'DOPE':
                        dynamic_maximum = 250 #max in range for DOPE
                    next_level = peak_list[i] + dynamic_maximum
                    if next_level > highVal:
                        next_level = highVal
                    lipidLevels[i+2] = next_level
            except:
                pass
    if levels[0] < lowVal:
        adjusted_lowVal = lowVal-levels[0]
        levels[0] = lowVal #Not sure what we want for minimum
        levels[1] += adjusted_lowVal
    levels[1] = peak_list[1] #Forces difference from ground to level 0 to minimum between the two.
    levels[2] = peak_list[0]
    level_0_max_selection_bins = []
    for i in range(21):
        level_0_max_selection_bins.append(lipidCapacitanceFrequency[peak_list[1] + i][1])
    level_0_max_index = level_0_max_selection_bins.index(min(level_0_max_selection_bins))
    levels[3] = peak_list[1] + level_0_max_index
    for i in range(len(levels)//2-1):
        if (levels[2*i+1] >= levels[2*i+2]) and (levels[2*i+2] != -100):
            level_range = levels[2*i+1] - levels[2*i+2] + 1
            lipid_occurrences = []
            for j in range(level_range):
                lipid_occurrences.append(lipidCapacitanceFrequency[levels[2*i+2]+j][1])
            localMinimum = min(lipid_occurrences)
            levels[2*i+1] = levels[2*i+2] + lipid_occurrences.index(localMinimum)
            levels[2*i+2] = levels[2*i+2] + lipid_occurrences.index(localMinimum)
    for i in reducedLevels:
        level_0_offset = peak_list[1] - peak_list[0]
        reduced_floor = peak_list[i] + level_0_offset + 10 # Avoids second level 0, could be changed to not do so
        reduced_ceiling = peak_list[i+1] - 20
        lipid_occurrences = []
        try:
            for j in range(reduced_ceiling-reduced_floor+1):
                lipid_occurrences.append(lipidCapacitanceFrequency[reduced_floor + j][1])
            reduced_peak = max(lipid_occurrences)
            reduced_peak_index = lipid_occurrences.index(reduced_peak)
            levels.append(reduced_floor+reduced_peak_index-5)
            levels.append(reduced_floor+reduced_peak_index+5)
        except:
            levels.append(-100)
            levels.append(-100)
            print('Please use manual input for reduced level ' + str(i) + '.')
    if lipid == 'DOPC':
        levels.insert(12,-100)
        levels.insert(12,-100)
        levels.append(-100)
        levels.append(-100)
    '''


def calculate_histogram_times():
    num_of_levels = len(allowed_levels)
    noise_index = num_of_levels-1
    histogram_level_times = [0] * num_of_levels
    for val in filtered_sweepY:
        histogram_level_times[noise_index] += 1
        for level_index in range(noise_index): # ignores noise level
            if (val >= allowed_levels[level_index][1]) and (val < allowed_levels[level_index][2]):
                histogram_level_times[noise_index] -= 1
                histogram_level_times[level_index] += 1
    return(histogram_level_times)


level_dwells = {}

def find_dwell_times(min_time:float): #min_time in ms
    min_occurances = round(min_time*20) #currently 20 readings/ms
    dwell_time_list = [] # [index,dwell length]
    temp_levels = levels_list[:]
    allowed_levels = []
    for i in range(len(temp_levels)):
        allowed_levels.append([temp_levels[i],pA_levels[2*i],pA_levels[2*i+1]])
    allowed_levels.append(['n',-100,-100])

    x = 0
    dwell_length = 0
    noise_index = len(allowed_levels)-1
    noise_bool = False
    num_of_levels = len(filtered_sweepY)
    
    while x < num_of_levels:
        level_index = noise_index
        for i in allowed_levels:
            if (filtered_sweepY[x] >= i[1]) and (filtered_sweepY[x] < i[2]):
                if noise_bool:
                    dwell_time_list.append([level_index,dwell_length])
                    noise_bool = False

                level_index = allowed_levels.index(i)
                dwell_length = 1
                break
                '''
                if len(dwell_time_list) == 0:
                    pass
                elif dwell_time_list[-1][1] < min_occurances:
                    small_spikes_previous += 1
                elif small_spikes_previous > 0:
                    if (len(dwell_time_list) < 2+small_spikes_previous) and (small_spikes_previous == 1):
                        small_spikes_previous = 0
                        else:
                            dwell_length = 0
                            for small_spikes in range(small_spikes_previous-1):
                                dwell_length += dwell_time_list[len(dwell_time_list)-1][1]
                                dwell_time_list.pop(len(dwell_time_list)-1)
                            dwell_time_list.append([noise_index,dwell_length])
                            small_spikes_previous = 0
                            
                    elif dwell_time_list[:-1-small_spikes_previous][0] == dwell_time_list[:-1][0]:
                        dwell_time_list.pop(len(dwell_time_list)-1)
                        if len(dwell_time_list) < 100:
                            print(small_spikes_previous)
                        for small_spikes in range(small_spikes_previous+1):
                            if len(dwell_time_list) < 100:
                                print(dwell_time_list)
                            dwell_length += dwell_time_list[len(dwell_time_list)-1][1]
                            dwell_time_list.pop(len(dwell_time_list)-1)
                        dwell_time_list.append([level_index,dwell_length])
                    else:
                        dwell_length = 0
                        for small_spikes in range(small_spikes_previous):
                            dwell_length += dwell_time_list[len(dwell_time_list)-2][1]
                            dwell_time_list.pop(len(dwell_time_list)-2)
                        if dwell_time_list[len(dwell_time_list)-2][0] == noise_index:
                            dwell_length += dwell_time_list[len(dwell_time_list)-2][1]
                            dwell_time_list.pop(len(dwell_time_list)-2)
                            dwell_time_list.insert(len(dwell_time_list)-1,[noise_index,dwell_length])
                        elif dwell_time_list[len(dwell_time_list)-1][0] == noise_index:
                            dwell_length += dwell_time_list[len(dwell_time_list)-1][1]
                            dwell_time_list.pop(len(dwell_time_list)-1)
                            dwell_time_list.append([noise_index,dwell_length])
                        else:
                            dwell_time_list.insert(len(dwell_time_list)-1,[noise_index,dwell_length])
                    small_spikes_previous = 0'''
                
        if level_index == noise_index:
            if not noise_bool:
                dwell_length = 0
                noise_bool = True
            dwell_length += 1
            x+=1
        else:
            x+=1
            if x >= num_of_levels:
                break
            while (filtered_sweepY[x] >= allowed_levels[level_index][1]) and (filtered_sweepY[x] < allowed_levels[level_index][2]):
                dwell_length+=1
                x+=1
                if x >= num_of_levels:
                    dwell_time_list.append([level_index,dwell_length])
                    break
            if x < num_of_levels:
                dwell_time_list.append([level_index,dwell_length])

    filtered_dwell_times = []

    #prep filter by checking first element

    x=0
    dwell_length=0
    first_element_small = False
    if len(dwell_time_list) < 4:
        return([],allowed_levels) 
    while dwell_time_list[x][1] < min_occurances:
        dwell_length+=dwell_time_list[x][1]
        x+=1
        first_element_small = True
    if first_element_small:
        filtered_dwell_times.append([noise_index,dwell_length])

    # filter out small spikes

    while x < len(dwell_time_list):
        if dwell_time_list[x][1] >= min_occurances:
            filtered_dwell_times.append(dwell_time_list[x])
            #if(len(filtered_dwell_times) < 20):
              #  print(dwell_time_list[x])
            x+=1
        else: # combine with surrounding elements depending on levels
            dwell_length = 0
            level_index = filtered_dwell_times[-1][0]

            while dwell_time_list[x][1] < min_occurances:
                dwell_length += dwell_time_list[x][1]
                x+=1
                if x >= len(dwell_time_list):
                    break
            try:
                if level_index == dwell_time_list[x][0]:
                    filtered_dwell_times[-1][1] += (dwell_length + dwell_time_list[x][1])
                    x+=1
                elif level_index == noise_index:
                    filtered_dwell_times[-1][1] += dwell_length
                elif dwell_time_list[x][0] == noise_index:
                    filtered_dwell_times.append([noise_index,dwell_length + dwell_time_list[x][1]])
                    x+=1
                else:
                    filtered_dwell_times.append([noise_index,dwell_length])
                    filtered_dwell_times.append(dwell_time_list[x])
                    x+=1
            except:
                pass
    return(filtered_dwell_times,allowed_levels)


def analyze_dwell_times(dwell_times:list,allowed_levels:list):
    level_values = [] # ['level',occurences,total time]
    grouped_levels = []
    for i in allowed_levels:
        level_values.append([i[0],0,0])
        grouped_levels.append([])
    for i in dwell_times:
        level_values[i[0]][1] += 1
        level_values[i[0]][2] += i[1]
        grouped_levels[i[0]].append(i[1]/20) # in ms
    
    important_levels = ['0','1','2','3','4','5','1r','2r','3r','4r','5r']
    combined_levels = []
    for i in important_levels:
        for j in important_levels:
            if (i+'r' == j):
                combined_levels.append([i,j])
    allowed_levels_list = []
    for i in allowed_levels:
        allowed_levels_list.append(i[0])
    for i in combined_levels:
        level_index = allowed_levels_list.index(i[0])
        level_index_reduced = allowed_levels_list.index(i[1])
        level_values[level_index][1] += level_values[level_index_reduced][1]
        level_values[level_index][2] += level_values[level_index_reduced][2]
        grouped_levels[level_index] = grouped_levels[level_index] + grouped_levels[level_index_reduced]
        level_values.pop(level_index_reduced)
        allowed_levels_list.pop(level_index_reduced)
        grouped_levels.pop(level_index_reduced)

    '''print('level 0:')
    temp = []
    for i in grouped_levels[0]:
        temp.append(i)
    print(temp)

    print('level 1')
    temp = []
    for i in grouped_levels[2]:
        temp.append(i)
    print(temp)'''

    for i in range(len(grouped_levels)):
        level_values[i].append(np.std(grouped_levels[i]))

    level_data = {} # 'level':[T,N,tau,dtau,dT/T]
    
    for i in level_values:
        if i[0] not in important_levels:
            continue
        temp_data = []
        T_val = i[2]/20
        N_val = i[1]
        try: # if N == 0 set to 0
            tau_val = T_val/N_val
        except:
            tau_val = 0
        temp_data.append(T_val)
        temp_data.append(N_val)
        temp_data.append(tau_val)
        sqrt_N = math.sqrt(N_val)
        d_tau_val = i[3]/sqrt_N
        temp_data.append(d_tau_val)
        #temp_data.append(i[3])
        try:
            temp_data.append(math.sqrt((1/N_val)+(d_tau_val/tau_val)**2)) # for error bars
        except:
            temp_data.append(0)
        level_data[i[0]] = temp_data
    return level_data,grouped_levels


def record_dwell_times(level_data,mdt):
    for level,data in level_data.items():
        for output_index in range(len(error_bar_data_kept)):
            output_data[f'{error_bar_data_kept[output_index]}_{level} ({mdt} ms)'].append(data[output_index])
    for i in i_vs_0_list:
        try:
            R_i_0 = level_data[i][0]/level_data['0'][0]
        except:
            R_i_0 = 'inf'
        try:
            output_data[f'R_{i}_vs_0 ({mdt} ms)'].append(R_i_0)
        except:
            output_data[f'R_{i}_vs_0 ({mdt} ms)'].append('inf')
        try:
            output_data[f'dR_{i}_vs_0 ({mdt} ms)'].append(R_i_0*level_data[i][4])
        except:
            output_data[f'dR_{i}_vs_0 ({mdt} ms)'].append('inf')
    for i in i_vs_1_list:
        try:
            R_i_1 = level_data[i][0]/level_data['1'][0]
        except:
            R_i_1 = 'inf'
        try:
            output_data[f'R_{i}_vs_1 ({mdt} ms)'].append(R_i_1)
        except:
            output_data[f'R_{i}_vs_1 ({mdt} ms)'].append('inf')
        try:
            output_data[f'dR_{i}_vs_1 ({mdt} ms)'].append(R_i_1*math.sqrt((level_data[i][4])**2+(level_data['1'][4])**2))
        except:
            output_data[f'dR_{i}_vs_1 ({mdt} ms)'].append('inf')


def record_general_data(level_frequency):
    output_data['time_noise'].append(level_frequency[-1])
    for i in levels_list:
        level_index = levels_list.index(i)
        output_data[f'time_level_{i}'].append(level_frequency[level_index])
        try:
            reduced_level_index = levels_list.index(f'{i}r')
            output_data[f'time_level_{i}_total'].append(level_frequency[level_index]+level_frequency[reduced_level_index])
        except:
            pass
    calc_open_levels = "; ".join(
            f"{pA_levels[i]}, {pA_levels[i+1]}"
            for i in range(0, len(pA_levels), 2)
        )
    
    starts = []
    stops = []
    for start,stop in zip(spike_start, spike_stop):
        starts.append(start)
        stops.append(stop)
    while True:
        for start in starts:
            temp_starts = starts[:]
            temp_stops = stops[:]
            temp_index = starts.index(start)
            temp_starts.pop(temp_index)
            temp_stops.pop(temp_index)
            for temp_start,temp_stop in zip(temp_starts,temp_stops):
                try:
                    if ((temp_start >= start) and (temp_start < stops[temp_index])) or ((temp_stop >= start) and (temp_stop < stops[temp_index])):
                        second_temp_index = starts.index(temp_start)
                        overlapping_starts = [starts[temp_index],starts[second_temp_index]]
                        overlapping_stops = [stops[temp_index],stops[second_temp_index]]
                        if second_temp_index > temp_index:
                            second_temp_index -= 1
                        starts.pop(temp_index)
                        starts.pop(second_temp_index)
                        stops.pop(temp_index)
                        stops.pop(second_temp_index)
                        starts.append(min(overlapping_starts))
                        stops.append(max(overlapping_stops))
                except:
                    pass
        break

    calc_data_removed = ", ".join(
            f"{start}-{stop}" for start, stop in zip(starts, stops)
        )
    calc_total_time = 60 - sum(
            stop - start for start, stop in zip(starts, stops)
        )
    
    output_data['abf_file'].append(abf_file_number)
    output_data['voltage'].append(0) # placeholder
    output_data['tempature'].append(0) # placeholder
    output_data['lipid_list'].append(lipid)
    output_data['cutoff_used'].append(cutoff)
    output_data['total_time'].append(calc_total_time)
    output_data['data_removed'].append(calc_data_removed)
    output_data['open_levels'].append(calc_open_levels)

    spike_start.clear()
    spike_stop.clear()
    pA_levels.clear()


# the location on your computer where you want the file and the name of the file
files = os.listdir()
filesPath = os.getcwd()
lipid = ""
breakFileBool = False
pA_levels = []


while True: #user selects lipid
    userinput = input('\nselect lipid:\n1: DOPE\n2: DOPC\n3: POPC\n')
    if userinput == '2':
        lipid = 'DOPC'
        break
    elif userinput == '1':
        lipid = 'DOPE'
        break
    elif userinput == '3':
        lipid = 'POPC'
        break

levels_list = ['g','0','1','2','3','4','5','1r','2r','3r','4r','5r']


# ------------------------ For excel sheet -----------------------
output_data = {}

output_data_list = [
    'abf_file',
    'voltage',
    'tempature',
    'lipid_list',
    'cutoff_used',
    'total_time',
    'data_removed',
    'open_levels'
]

general_data_list = []
general_data_list = general_data_list + output_data_list

# choose minimum dwell times (list form for testing purposes if required)
min_dwell_time_list = [0.05,0.2]
# compare dwell times
i_vs_0_list = ['1','2']
i_vs_1_list = ['2','3','4']

error_bar_data_kept = ['T','N','tau','dtau','dT/T']
error_bar_levels = []

for i in levels_list: # only take full quantized levels (should be changed if we want to get reduced data)
    try:
        error_bar_levels.append(str(int(i)))
    except:
        pass

for i in output_data_list:
    output_data[f'{i}'] = []

for i in levels_list:
    output_data[f'time_level_{i}'] = []
    output_data_list.append(f'time_level_{i}')
    general_data_list.append(f'time_level_{i}')

output_data['time_noise'] = []
output_data_list.append('time_noise')

temp_output_copy = []
for i in output_data.keys():
    temp_output_copy.append(i)

for i in temp_output_copy:
    for j in temp_output_copy:
        if (i+'r' == j):
            output_data[f'{i}_total'] = []
            output_data_list.append(f'{i}_total')
            general_data_list.append(f'{i}_total')

for mdt in min_dwell_time_list:
    for i in error_bar_data_kept:
        for j in error_bar_levels:
            output_data[f'{i}_{j} ({mdt} ms)'] = []
            output_data_list.append(f'{i}_{j} ({mdt} ms)')
    # ratios
    for i in i_vs_0_list:
        output_data[f'R_{i}_vs_0 ({mdt} ms)'] = []
        output_data_list.append(f'R_{i}_vs_0 ({mdt} ms)')
    for i in i_vs_1_list:
        output_data[f'R_{i}_vs_1 ({mdt} ms)'] = []
        output_data_list.append(f'R_{i}_vs_1 ({mdt} ms)')
    # SEM ratios
    for i in i_vs_0_list:
        output_data[f'dR_{i}_vs_0 ({mdt} ms)'] = []
        output_data_list.append(f'dR_{i}_vs_0 ({mdt} ms)')
    for i in i_vs_1_list:
        output_data[f'dR_{i}_vs_1 ({mdt} ms)'] = []
        output_data_list.append(f'dR_{i}_vs_1 ({mdt} ms)')

# ----------------------------------------------------------------

#adjustable in code for graph readability
lowVal = -10
highVal = 1000

pA_min = -10
pA_max = 1000

histogram_min = -10
histogram_max = 1000

x = 0

####################### USER INTERFACE ########################

while x < len(files):
    file = files[x]
    if file.endswith(".abf"):
        if breakFileBool:
            break
        abf_file_number = str(file.split(".")[0][-3:])
        location = rf"{filesPath}\{file.split('.')[0]}.xlsx"
        abf = rf"{filesPath}\{file}"
        set_level(abf)

        print("@@@@@@@@@@@@@@@@@@", file, "@@@@@@@@@@@@@@@@@@\n")

        spike_start.clear()
        spike_stop.clear()
        
        pA_levels = findLevels(spike_start,spike_stop,pA_min,pA_max,True) # Automatically find bins

        while True:
            print(abf_file_number)
            try:
                u = input(
                    "1: Next file and record data\n2: Remove noise\n3: Graph\n4: Manually set pA level\n5: Change file\n6: Change settings\n7: Export raw data in time range\n8: End analysis and export excel\n"
                )
                if u == '1':
                    #try:
                    for mdt in min_dwell_time_list:
                        dwell_time_list,allowed_levels = find_dwell_times(mdt)
                        num = 0
                        level_data,grouped_levels = analyze_dwell_times(dwell_time_list,allowed_levels)
                        record_dwell_times(level_data,mdt)
                    record_general_data(calculate_histogram_times())
                    x += 1
                    break
                    #except:
                    #    print('An error occurred. Terminating program.')
                    #    breakFileBool = True
                    #    break
                elif u == '2':
                    user_input = input(
                        "Enter spike ranges as [low high low high ...]: "
                    ).strip()
                    try:
                        user_values = list(map(float, user_input.split()))
                        if len(user_values) % 2 != 0:
                            raise ValueError("You must provide an even number of values.")
                        
                        # Appends ranges for removal
                        for i in range(0, len(user_values), 2):
                            spike_start.append(user_values[i]*sampling_frequency)
                            spike_stop.append(user_values[i + 1]*sampling_frequency)

                        # Process the specified spike ranges
                        large_spike(spike_start, spike_stop)

                        #reAnalyze pA_levels
                        print('pA levels are being reset, any manual changes have been overwritten.')
                        pA_levels = findLevels(spike_start,spike_stop,pA_min,pA_max,True)
                    except ValueError as ve:
                        print(f"Invalid input: {ve}")
                    continue
                elif u == '3':
                    histogram(spike_start, spike_stop, location, cutoff,lowVal=histogram_min, highVal=histogram_max)
                    ideal_Y = make_ideal_Y(bin_length, net_mean, level)
                    abf_make_a_graph(
                        window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list
                    )
                    continue
                elif u == "4":
                    allowed_responses = levels_list
                    while True:
                        user_input = input("1: Individual\n2: All\n")
                        if user_input == '1':
                            while True:
                                user_input = input("g: Ground\n0-5: level 0-5\n2r-5r: reduced level 1-5\n")
                                if user_input in allowed_responses:
                                    response_index = allowed_responses.index(user_input)
                                    while True:
                                        try:
                                            lower_bound = int(input("Level " + user_input + " lower bound: "))
                                            pA_levels[response_index*2] = lower_bound
                                            break
                                        except:
                                            pass
                                    while True:
                                        try:
                                            upper_bound = int(input("Level " + user_input + " upper bound: "))                                        
                                            if (upper_bound < pA_levels[response_index*2]):
                                                raise ValueError('Upper bound must be greater than lower bound.')
                                            pA_levels[response_index*2+1] = upper_bound
                                            break
                                        except ValueError as ve:
                                            print(f"Invalid input: {ve}")
                                    break
                            print(pA_levels)
                            break
                        elif user_input == '2':
                            for i in allowed_responses:
                                response_index = allowed_responses.index(i)
                                while True:
                                    try:
                                        lower_bound = int(input("Level " + i + " lower bound: "))
                                        pA_levels[response_index*2] = lower_bound
                                        break
                                    except:
                                        pass
                                while True:
                                    try:
                                        upper_bound = int(input("Level " + i + " upper bound: "))
                                        if (upper_bound < pA_levels[response_index*2]):
                                            raise ValueError('Upper bound must be greater than lower bound.')
                                        pA_levels[response_index*2+1] = upper_bound
                                        break
                                    except ValueError as ve:
                                        print(f"Invalid input: {ve}")
                            break
                elif u == "5":
                    while True:
                        continueBool = False
                        user_input = input("1: Rerun last file\n2: Select file number\n")
                        if user_input == '1':
                            current_file_index = files.index(file)
                            found_file_bool = False
                            for i in range(current_file_index):
                                if files[current_file_index - 1 - i].endswith('.abf'):
                                    x = current_file_index - 1 - i
                                    found_file_bool = True
                                    continueBool = True
                                    break
                            if not found_file_bool:                        
                                print("Already at the first file. Cannot rerun previous file.")
                            continueBool = True
                        elif user_input == '2':
                            while True:
                                user_input = input('Select 3-digit file code i.e. 005 (done to abort):\n')
                                if user_input == 'done':
                                    continueBool = True
                                    break
                                try:
                                    for i in files:
                                        temp_file_number = str(i.split(".")[0][-3:])
                                        if (temp_file_number == user_input) and i.endswith('.abf'):
                                            next_file_index = files.index(i)
                                            x = next_file_index
                                            continueBool = True
                                            break
                                    break
                                except:
                                    pass
                        if continueBool:
                            break
                    break
                elif u == "6":
                    while True:
                        user_input = input("1: Cutoff\n2: Histogram range\n")
                        if user_input == '1':
                            while True:
                                try:
                                    print("Note that cutoff will not be used until next file.")
                                    cutoff = float(input("Enter cutoff pA value: ").strip())
                                    break
                                except ValueError as ve:
                                    print(f"Invalid input for cutoff pA: {ve}")
                            break
                        elif user_input == '2':
                            while True:
                                try:
                                    histogram_min = int(input("Minimum histogram range: "))
                                    if histogram_min > 0:
                                        raise ValueError('Please set histogram minimum <= 0.')
                                    break
                                except ValueError as ve:
                                    print(f"Invalid input for histogram minimum: {ve}")
                            while True:
                                try:
                                    histogram_max = int(input("Maximum histogram range: "))
                                    if histogram_max < 600:
                                        raise ValueError('Please set histogram maximum >= 600.')
                                    break
                                except ValueError as ve:
                                    print(f"Invalid input for histogram maximum: {ve}")
                elif u == '7':
                    sampling_frequency = 20000 #Hz
                    user_input = input('1: Export Dwell times\n2: Export capacitance levels\n')
                    '''print('level 0:')
                    temp = []
                    for i in grouped_levels[0]:
                        temp.append(i)
                    print(temp)

                    print('level 1')
                    temp = []
                    for i in grouped_levels[2]:
                        temp.append(i)
                    print(temp)'''
                    while True:
                        if user_input == '1':
                            dwell_time_list,allowed_levels = find_dwell_times(mdt)
                            num = 0
                            level_data,grouped_levels = analyze_dwell_times(dwell_time_list,allowed_levels)
                            grouped_levels.pop(len(grouped_levels)-1)
                            grouped_levels.pop(0)
                            raw_data_export = {}
                            data_columns = []
                            lengths_of_grouped_level = []
                            for grouped_level in grouped_levels:
                                lengths_of_grouped_level.append(len(grouped_level))
                            try:
                                max_length = max(lengths_of_grouped_level)
                            except:
                                max_length = 0
                            for grouped_level in grouped_levels:
                                grouped_level_copy = grouped_level[:]
                                for i in range(max_length-len(grouped_level)):
                                    grouped_level_copy.append(None)
                                grouped_level_index = grouped_levels.index(grouped_level)
                                raw_data_export[grouped_level_index] = grouped_level_copy
                                data_columns.append(grouped_level_index)
                            df2 = pd.DataFrame(
                                raw_data_export,
                                columns=data_columns
                            )
                            while True:
                                try:
                                    excel_loc = os.path.join(filesPath, f"dwell_times_{abf_file_number}.xlsx")
                                    with pd.ExcelWriter(excel_loc, engine="xlsxwriter") as writer:
                                        df2.to_excel(writer, sheet_name="data", index=False)
                                    break
                                except:
                                    pass
                            allowed_levels = []
                            break
                        elif user_input == '2':
                            while True:
                                try:
                                    time_min = float(input('Minimum time to export: '))
                                    index_min = int(time_min*sampling_frequency)
                                    if (index_min > len(filtered_sweepY)) or (index_min < 0):
                                        raise ValueError('Out of range.')
                                    break
                                except:
                                    pass
                            while True:
                                try:
                                    time_max = float(input('Maximum time to export: '))
                                    index_max = int(time_max*sampling_frequency)
                                    if index_max > len(filtered_sweepY)or (index_max < index_min):
                                        raise ValueError('Out of range.')
                                    break
                                except:
                                    pass
                            
                            time_list = []
                            pA_list = []
                            for sample in range(index_max-index_min):
                                index_sample = index_min+sample
                                time_list.append((index_sample)/sampling_frequency)
                                pA_list.append(filtered_sweepY[index_sample])
                            raw_data_export = {
                                'Time [s]': time_list,
                                'Capacitance [pF]': pA_list
                            }
                            df2 = pd.DataFrame(
                                raw_data_export,
                                columns=['Time [s]','Capacitance [pF]']
                            )
                            while True:
                                try:
                                    excel_loc = os.path.join(filesPath, f"raw_data_{abf_file_number}.xlsx")
                                    with pd.ExcelWriter(excel_loc, engine="xlsxwriter") as writer:
                                        df2.to_excel(writer, sheet_name="data", index=False)
                                    break
                                except:
                                    input('When excel sheet is closed please press enter')
                        print('File exported.')
                        break
                elif u == '8': 
                    breakFileBool = True
                    break
            except ValueError as ve:
                print(f'An error occured: {ve}\nTerminating program and recording data.')
                breakFileBool = True
                break
    else:
        x += 1

################################################################################### EXPORT FILE ##################################################################################################

df1 = pd.DataFrame(
    output_data,
    columns=output_data_list
)

df1 = df1.groupby("abf_file", as_index=False).last()

# changes excel file name and gives it a path then outputs
while True:
    try:
        excel_loc = os.path.join(filesPath, "output.xlsx")
        with pd.ExcelWriter(excel_loc, engine="xlsxwriter") as writer:
            df1.to_excel(writer, sheet_name="data", index=False)
        break
    except:
        input('When excel sheet is closed please press enter')

print("done")

##################################################################################################################################################################################################
