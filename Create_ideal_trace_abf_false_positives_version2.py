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
from ideal_trace_same_bin_version2 import same_bin
from ideal_trace_combine_repeates_version2 import combine_repeates
from ideal_trace_calculate_mean_version2 import find_means
from ideal_trace_make_ideal_Y_list_version2 import make_ideal_Y

#the location on your computer where you want the file and the name of the file
location= r"C:\Users\dcmou\Downloads\work\resistanceRamp\23714000.xlsx"

# large spike
spike_start = []
spike_stop = []

# negative spike-- goes down from closed and does not change level
neg_spike_start = []
neg_spike_stop = []


# false_pos
false_pos_start = [10]
section_start = [10]
section_stop = [20]
# the level at the start of the section will be filled in for the whole range

# if yes, this will just display the idealized trace (without accounding for false positives) and the filtered data
# it then gives the option to change the scale in order to identify the locations of false positives
# if no, it runs the false positives, shows the graph and generates the excel file
find_false_values = no

ideal_Y= make_ideal_Y(bin_length, net_mean, level)
#log, yLim, bin?? as varible
#plt.hist(filtered_sweepY,bins=1000, range=(-10,600))
#plt.ylim(0, 1000)
#plt.title("File: 009")
#plt.show()

if find_false_values == 1:  # yes
    abf_make_a_graph(window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list)
    # change_scale=input("change scale? (yes/no): ")
    change_scale = "yes"
    if change_scale == "yes":
        new_window_width = float(input("new window width: "))
        abf_make_a_graph(
            new_window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list
        )

if find_false_values == 0:  # no
    # runs this code if there is a large noise spike
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

    # negative spike
    # a negative spike does not switch levels, however it would change the average value of the closed current
    # once a person identifies the start and stop location of the spike, this code disregards everything between those values
    e = 0
    while e < len(neg_spike_start):
        v = round((neg_spike_start[e] / time_step))
        c = 0
        while c < len(bin_index) - 1:
            # c is the position in the list of levels
            if v > bin_index[c] and v < bin_index[c + 1]:
                bin_index.insert(c + 1, round((neg_spike_start[e] / time_step)))
                bin_index.insert(c + 2, round(neg_spike_stop[e] / time_step))
                level.insert(c + 1, -1)
                level.insert(c + 2, 0)

                new_len_a = round((neg_spike_start[e] / time_step)) - bin_index[c]
                new_len_b = round(neg_spike_stop[e] / time_step) - round(
                    (neg_spike_start[e] / time_step)
                )
                new_len_c = bin_index[c + 3] - round(neg_spike_stop[e] / time_step)
                bin_length.pop(c)
                bin_length.insert(c, new_len_a)
                bin_length.insert(c + 1, new_len_b)
                bin_length.insert(c + 2, new_len_c)

                bin_mean.pop(c)
                bin_current = []
                a = bin_index[c]
                while a < bin_index[c + 1]:
                    bin_current.append(filtered_sweepY[a])
                    a = a + 1
                    if a == bin_index[c + 1]:
                        new_mean = mean(bin_current)
                        bin_mean.insert(c, new_mean)
                        bin_current = []
                while a < bin_index[c + 2]:
                    a = a + 1
                    if a == bin_index[c + 2]:
                        new_mean = bin_mean[c] - 0.5
                        bin_mean.insert(c + 1, new_mean)
                while a < bin_index[c + 3]:
                    bin_current.append(filtered_sweepY[a])
                    a = a + 1
                    if a == bin_index[c + 3]:
                        new_mean = mean(bin_current)
                        bin_mean.insert(c + 2, new_mean)
                        bin_current = []
            c = c + 1
        e = e + 1

    # false positives
    # e counts up from zero, it is the index of the starting location in the false_pos_start list, when e == len(false_pos_start), it will have completed dealing eith the false positives
    e = 0
    while e < len(false_pos_start):
        done = "no"
        v = round((false_pos_start[e]) / time_step)
        # starting at the index of the start time
        while v < (round((false_pos_start[e]) / time_step) + 5 / time_step) and v < len(
            abf.sweepY
        ):
            c = 0
            while c < len(bin_index):
                # if the index (v) equals any number in the bin_index, then that is the start or end of the false event
                if bin_index[c] == v and done == "no":
                    false_event = c
                    false_index = v
                    level.pop(false_event)
                    level.insert(false_event, level[false_event - 1])
                    # because there is just one event, once this code has been run once, done is changed to yes and it will not be run at the end of the event
                    done = "yes"
                c = c + 1
            v = v + 1
        e = e + 1
    e = 0
    while e < len(section_start):
        started = no
        v = round((section_start[e] / time_step))
        false_index = 0
        while v < round(section_stop[e] / time_step):
            c = 0
            # if the index is equal to any number in the bin_index, that means that there is a change of level there
            # while it is within the defined noise spike, that change of level is incorrect, and the value in the level list is replaced by -1
            while c < len(bin_index):
                if bin_index[c] == v:
                    if started == no:
                        correct_level = level[c - 1]
                    false_index = c
                    level.pop(c)
                    level.insert(c, correct_level)
                    started = yes
                if false_index == 0:
                    correct_level = c
                c = c + 1
            v = v + 1
        e = e + 1

    # removing false events creates more instances where several "events" in a row are the same event, at the same level, this calls the routine to combine those
    result = combine_repeates(bin_mean, bin_length, bin_index, level)
    # the rountine returns a list of results, the bin_mean, bin_length, bin_index, and level lists
    bin_mean = result[0]
    bin_length = result[1]
    bin_index = result[2]
    level = result[3]

    # with the false events reassigned to their appropriate level, the weighted mean has to be recalculated
    result = find_means(bins_list, level, bin_mean, bin_length)
    net_mean = result[0]
    avg_length = result[1]
    mean_length = result[2]
    stdev_length = result[3]
    sterrmean_length = result[4]
    opendwelltimes1 = result[5]
    opendwelltimes2 = result[6]
    opendwelltimes3 = result[7]
    opendwelltimes4 = result[8]
    opendwelltimes5 = result[9]
    opendwelltimes6 = result[10]
    opendwelltimes7 = result[11]

    #    print(opendwelltimes1)

    #    print(net_mean)
    #    print(avg_length)
    #    print(mean_length)
    #    print(stdev_length)
    #    print(sterrmean_length)

    # print(level)

    # and the ideal_Y list remade
    ideal_Y = make_ideal_Y(bin_length, net_mean, level)

    abf_make_a_graph(window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list)

    # rest of code is formatting for the excel files

    # convert bin_length and avg_length into seconds
    bin_length_sec = []
    for i in bin_length:
        bin_length_sec.append(i * time_step)

    avg_length_sec = []
    for i in avg_length:
        avg_length_sec.append(round((i * time_step), 5))

    mean_length_sec = []
    for i in mean_length:
        mean_length_sec.append(i * time_step)

    stdev_length_sec = []
    for i in stdev_length:
        stdev_length_sec.append(i * time_step)

    sterrmean_length_sec = []
    for i in sterrmean_length:
        sterrmean_length_sec.append(i * time_step)

    opendwelltimes1_sec = []
    for i in opendwelltimes1:
        opendwelltimes1_sec.append(i * time_step)
    opendwelltimes2_sec = []
    for i in opendwelltimes2:
        opendwelltimes2_sec.append(i * time_step)
    opendwelltimes3_sec = []
    for i in opendwelltimes3:
        opendwelltimes3_sec.append(i * time_step)
    opendwelltimes4_sec = []
    for i in opendwelltimes4:
        opendwelltimes4_sec.append(i * time_step)
    opendwelltimes5_sec = []
    for i in opendwelltimes5:
        opendwelltimes5_sec.append(i * time_step)
    opendwelltimes6_sec = []
    for i in opendwelltimes6:
        opendwelltimes6_sec.append(i * time_step)
    opendwelltimes7_sec = []
    for i in opendwelltimes7:
        opendwelltimes7_sec.append(i * time_step)

    #    print(mean_length_sec)
    #    print(stdev_length_sec)
    #    print(sterrmean_length_sec)

    # creates a list starting at zero up to the number of levels
    list_of_levels = []
    f = 0
    while f <= max(level):
        list_of_levels.append(f)
        f = f + 1

    # lists of start and end times for each event
    start_time = []
    for i in bin_index:
        start_time.append(i * time_step)

    end_time = []
    for i in start_time:
        end_time.append(i)
    end_time.pop(0)
    end_time.append(duration)

    # lists of what level the event transitioned from and to
    transition_from = []
    transition_to = []

    for i in level:
        transition_from.append(i)
        transition_to.append(i)

    transition_from.insert(0, None)
    transition_from.pop(-1)

    transition_to.pop(0)
    transition_to.append(None)

    # rounds the mean to two places
    net_mean_round = []
    for i in net_mean:
        r = round(i, 2)
        net_mean_round.append(r)
    net_mean = net_mean_round

    # the amplitude is the difference in current from the event to the closed level
    level_amplitude = []
    for i in net_mean:
        level_amplitude.append(i - net_mean[0])

    # counts the number of times an event occured
    occurrences = []
    w = 0
    while w <= max(level):
        a = level.count(w)
        occurrences.append(a)
        w = w + 1

    # Calculates the average dwell time for channel opening for each level
    total_dwell_time = []
    for a, b in zip(occurrences, avg_length_sec):
        total_dwell_time.append((a * b))

    # Calculate the "uncertainty" in total dwell time assuming a random process.  (That is, if you re-ran it again, expected scatter of stdev in that number)
    # If there are N events on average during an interval, but it is a random process, uncertainty (stdev) = sqrt(N)
    # N = number of timesteps in total_dwell_time = total_dwell_time / timestep
    # "uncertainty" in number of timesteps = sqrt(N)
    # uncertainty in total dwell time = sqrt(N) * timestep = sqrt(total_dwell_time * timestep

    uncert_total_dwell_time = [math.sqrt(x * time_step) for x in total_dwell_time]

    #    print(total_dwell_time)
    #    print(uncert_total_dwell_time)

    # Calculates the relative probability of being in level N to being in level 1.
    # Uncertainty in that = sqrt ( (relativive uncertainty probability being in level N)^2 + (relative uncertainty probability being in level 1)^2 ) * probability being in level N

    a = total_dwell_time[1]
    relative_prob_to_level_1 = [x / a for x in total_dwell_time]

    #    print(relative_prob_to_level_1)

    uasq = (uncert_total_dwell_time[1] / total_dwell_time[1]) ** 2

    relative_uncert_level_N_sq = []
    for a, b in zip(uncert_total_dwell_time, total_dwell_time):
        relative_uncert_level_N_sq.append(((a / b) ** 2))

    relative_uncert_level_N = [math.sqrt(x + uasq) for x in relative_uncert_level_N_sq]

    uncert_relative_prob_to_level_1 = []
    for a, b in zip(relative_uncert_level_N, relative_prob_to_level_1):
        uncert_relative_prob_to_level_1.append((a * b))

    #    print(uncert_relative_prob_to_level_1)

    #    print(total_dwell_time)
    #    print(uncert_total_dwell_time)

    # creates a list for each level of event of all the events that were transitioned from and all the events that that level transitioned to
    levels_from_list = []
    levels_from = []
    levels_to_list = []
    levels_to = []

    h = 0
    while h < len(list_of_levels):
        g = 0
        while g < len(level):
            if level[g] == h:
                levels_from.append(transition_from[g])
                levels_to.append(transition_to[g])
            g = g + 1

        if levels_from.count(None) == 0:
            levels_from.sort()
        if levels_to.count(None) == 0:
            levels_to.sort()

        j = 1
        while j < len(levels_from):
            if levels_from[j] == levels_from[j - 1]:
                levels_from.pop(j)
            if j == len(levels_from) or levels_from[j] != levels_from[j - 1]:
                j = j + 1

        j = 1
        while j < len(levels_to):
            if levels_to[j] == levels_to[j - 1]:
                levels_to.pop(j)
            if j == len(levels_to) or levels_to[j] != levels_to[j - 1]:
                j = j + 1

        levels_from_list.append(levels_from)
        levels_from = []
        levels_to_list.append(levels_to)
        levels_to = []
        h = h + 1

    # for the list of levels that were transitioned to and from, calculates what the change in current was for each of those transitions and makes a list
    trans_amp_from_list = []
    trans_amp_from = []
    trans_amp_to_list = []
    trans_amp_to = []

    h = 0
    while h < len(levels_from_list):
        g = 0
        while g < len(levels_from_list[h]):
            if levels_from_list[h][g] == None:
                amp = None
            if levels_from_list[h][g] != None:
                amp = abs(
                    round(
                        (level_amplitude[levels_from_list[h][g]] - level_amplitude[h]),
                        3,
                    )
                )
            trans_amp_from.append(amp)
            g = g + 1
        trans_amp_from_list.append(trans_amp_from)
        trans_amp_from = []
        h = h + 1

    h = 0
    while h < len(levels_to_list):
        g = 0
        while g < len(levels_to_list[h]):
            if levels_to_list[h][g] == None:
                amp = None
            if levels_to_list[h][g] != None:
                amp = abs(
                    round(
                        (level_amplitude[levels_to_list[h][g]] - level_amplitude[h]), 3
                    )
                )
            trans_amp_to.append(amp)
            g = g + 1
        trans_amp_to_list.append(trans_amp_to)
        trans_amp_to = []
        h = h + 1

    trans_amp_from_list.pop(0)
    trans_amp_from_list.insert(0, None)
    levels_from_list.pop(0)
    levels_from_list.insert(0, None)

    trans_amp_to_list.pop(0)
    trans_amp_to_list.insert(0, None)
    levels_to_list.pop(0)
    levels_to_list.insert(0, None)

    # conductance
    conductance = []
    for i in level_amplitude:
        conductance.append(i / voltage)

    # sorts out the events that transitioned to and from closed
    k = 0
    level_zero = []
    index_zero = []
    length_zero = []
    mean_zero = []
    while k < len(transition_from):
        if transition_from[k] == 0 and transition_to[k] == 0:
            level_zero.append(level[k])
            index_zero.append(bin_index[k])
            length_zero.append(bin_length_sec[k])
            mean_zero.append(bin_mean[k])
        k = k + 1

    # and finds the means of just those events
    result = find_means(bins_list, level_zero, mean_zero, length_zero)
    net_mean_zero = result[0]
    avg_length_zero = result[1]

    # and some of the same formatting to display them
    list_of_levels_zero = []
    for i in range(len(bins_list) + 1):
        list_of_levels_zero.append(i)
    # for i in level_zero:
    #     list_of_levels_zero.append(i)
    list_of_levels_zero.sort()

    l = 1
    while l < len(list_of_levels_zero):
        if list_of_levels_zero[l] == list_of_levels_zero[l - 1]:
            list_of_levels_zero.pop(l)
        if (
            l == len(list_of_levels_zero)
            or l > len(list_of_levels_zero)
            or list_of_levels_zero[l] != list_of_levels_zero[l - 1]
        ):
            l = l + 1
    # if list_of_levels_zero[0] == -1:
    #     list_of_levels_zero.pop(0)

    level_amplitude_zero = []

    for i in net_mean_zero:
        level_amplitude_zero.append(i - net_mean[0])

    occurrences_zero = []
    m = 0
    while len(occurrences_zero) < len(list_of_levels_zero):
        occurrences_zero.append(level_zero.count(list_of_levels_zero[m]))
        m = m + 1

    # all the variables that will be displayed in the excel files
    abf_data = {
        "level": level,
        "index": bin_index,
        "start time (s)": start_time,
        "length (s)": bin_length_sec,
        "end time (s)": end_time,
        "mean (pA)": bin_mean,
        "transition from": transition_from,
        "transition to": transition_to,
        "levels": list_of_levels,
        "level means (pA)": net_mean,
        "average length (s)": avg_length_sec,
        "level amplitude": level_amplitude,
        "conductance": conductance,
        "bins_list": bins_list,
        "occurrences": occurrences,
        "levels transition from": levels_from_list,
        "levels transitioned to": levels_to_list,
        "amplitude from transition": trans_amp_from_list,
        "amplitude to transition": trans_amp_to_list,
        "total dwell time (s)": total_dwell_time,
        "uncertainty total dwell time (s)": uncert_total_dwell_time,
        "relative probability to level 1": relative_prob_to_level_1,
        "uncertainty relative probability to level 1": uncert_relative_prob_to_level_1,
        "mean dwell time (s)": mean_length_sec,
        "stdev dwell time (s)": stdev_length_sec,
        "S.E.M. dwell time (s)": sterrmean_length_sec,
        "Level_1 dwell times (s)": opendwelltimes1_sec,
        "Level_2 dwell times (s)": opendwelltimes2_sec,
        "Level_3 dwell times (s)": opendwelltimes3_sec,
        "Level_4 dwell times (s)": opendwelltimes4_sec,
        "Level_5 dwell times (s)": opendwelltimes5_sec,
        "Level_6 dwell times (s)": opendwelltimes6_sec,
        "Level_7 dwell times (s)": opendwelltimes7_sec,
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
    df2 = pd.DataFrame(
        abf_data,
        columns=[
            "levels",
            "average length (s)",
            "level means (pA)",
            "level amplitude",
            "conductance",
            "occurrences",
            "levels transition from",
            "levels transitioned to",
            "amplitude from transition",
            "amplitude to transition",
            "total dwell time (s)",
            "uncertainty total dwell time (s)",
            "relative probability to level 1",
            "uncertainty relative probability to level 1",
            "mean dwell time (s)",
            "stdev dwell time (s)",
            "S.E.M. dwell time (s)",
        ],
    )
    df3 = pd.DataFrame(abf_data, columns=["bins_list"])
    #    df4 = pd.DataFrame(abf_data_zero, columns = ['level', 'index', 'length (s)', 'mean (pA)' ])
    #    df5 = pd.DataFrame(abf_data_zero, columns = ['levels', 'average length (s)', 'level means (pA)', 'level amplitude', 'occurrences'])
    #   df4 and df5 are legacy code from gramacidin, where we only wanted to analyze "single channel" "level 1" openings only
    df6 = pd.DataFrame(abf_data, columns=["Level_1 dwell times (s)"])
    df7 = pd.DataFrame(abf_data, columns=["Level_2 dwell times (s)"])
    df8 = pd.DataFrame(abf_data, columns=["Level_3 dwell times (s)"])
    df9 = pd.DataFrame(abf_data, columns=["Level_4 dwell times (s)"])
    df10 = pd.DataFrame(abf_data, columns=["Level_5 dwell times (s)"])
    df11 = pd.DataFrame(abf_data, columns=["Level_6 dwell times (s)"])
    df12 = pd.DataFrame(abf_data, columns=["Level_7 dwell times (s)"])

    # here you will need to put the location on your computer where you want the file and the name of the file
    with pd.ExcelWriter(location, engine="xlsxwriter") as writer:
        df1.to_excel(writer, sheet_name="data", index=False)
        df2.to_excel(writer, sheet_name="avg", index=False)
        #       df4.to_excel(writer, sheet_name= 'single event', index = False)
        #       df5.to_excel(writer, sheet_name= 'single event avg', index = False)
        df3.to_excel(writer, sheet_name="bins", index=False)

        df6.to_excel(writer, sheet_name="Level_1 times", index=False)
        df7.to_excel(writer, sheet_name="Level_2 times", index=False)
        df8.to_excel(writer, sheet_name="Level_3 times", index=False)
        df9.to_excel(writer, sheet_name="Level_4 times", index=False)
        df10.to_excel(writer, sheet_name="Level_5 times", index=False)
        df11.to_excel(writer, sheet_name="Level_6 times", index=False)
        df12.to_excel(writer, sheet_name="Level_7 times", index=False)

    print("done")
