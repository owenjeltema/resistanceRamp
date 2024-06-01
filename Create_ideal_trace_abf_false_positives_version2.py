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

voltage = []
lipid_list = []
tempature = []
pA_levels = [0] * 22
time_closed = []
time_level0 = []
time_level1 = []
time_level2 = []
time_level3 = []
time_level4 = []
time_level5 = []
time_level_r_2 = []
time_level_r_3 = []
time_level_r_4 = []
time_level_r_5 = []
total_time = []
data_removed = []
open_levels = []
abf_file = []


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


def histogram(start, stop, location, cutoff):
    try:
        if not (len(start) == len(stop)):
            raise ValueError("The start and stop lists must be of the same length.")
        for i in range(len(start)):
            try:
                # Ensure start and stop times are within the range of abf.sweepX
                if start[i] not in abf.sweepX or stop[i] not in abf.sweepX:
                    raise ValueError(
                        f"Start or stop time {start[i]}, {stop[i]} not in abf.sweepX"
                    )

                start_index = np.where(abf.sweepX == start[i])[0][0]
                stop_index = np.where(abf.sweepX == stop[i])[0][0]

                # Ensure indices are in the correct order
                if start_index > stop_index:
                    raise ValueError(
                        f"Start index {start_index} is greater than stop index {stop_index}"
                    )

                # Mark the filtered values within the specified range
                filtered_sweepY[start_index : stop_index + 1] = -1
            except ValueError as ve:
                print(f"Error processing interval {i}: {ve}")

        # Create histogram
        plt.hist(filtered_sweepY, bins=1000, range=(-10, 600))
        plt.ylim(0, 1000)
        plt.title(lipid)
        plt.xlabel("pA")
        plt.ylabel(
            "Occurrences with " + str(cutoff) + " kHz Filtering"
        )  # + str(cutoff)
        plt.legend(prop={"size": 10})
        plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")


# large spike
spike_start = []
spike_stop = []


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
            start_index = np.abs(abf.sweepX - start_value).argmin()
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
                    ]  # Substitute values outside the spikes

        # Update levels to correct false spikes
        for c in range(len(bin_index) - 1):
            if level[c] == -1 and level[c + 1] != -1:
                level[c] = 0

    except Exception as e:
        print(f"An error occurred: {e}")


# the location on your computer where you want the file and the name of the file
files = os.listdir()
filesPath = os.getcwd()
lipid = input("What Lipid are you using? ")
x = 0
while x < len(files):
    file = files[x]
    if file.endswith(".abf"):
        abf_file_number = str(file.split(".")[0][-3:])
        location = rf"{filesPath}\{file.split('.')[0]}.xlsx"
        abf = rf"{filesPath}\{file}"
        set_level(abf)
        print("@@@@@@@@@@@@@@@@@@", file, "@@@@@@@@@@@@@@@@@@\n")
        u = input(
            "1: Remove Noise\n2: Graph\n3: Re-run\n4: Change low-pass\n5: Add to Excel\n6: Export Excel\n"
        )
        if u == "1":
            user_input = input(
                "Enter spike ranges as [low high low high ...]: "
            ).strip()
            try:
                user_values = list(map(float, user_input.split()))
                if len(user_values) % 2 != 0:
                    raise ValueError("You must provide an even number of values.")

                # Appends ranges for removal
                for i in range(0, len(user_values), 2):
                    spike_start.append(user_values[i])
                    spike_stop.append(user_values[i + 1])

                # Process the specified spike ranges
                large_spike(spike_start, spike_stop)
                continue
            except ValueError as ve:
                print(f"Invalid input: {ve}")
            continue
        elif u == "2":
            histogram(spike_start, spike_stop, location, cutoff)
            ideal_Y = make_ideal_Y(bin_length, net_mean, level)
            abf_make_a_graph(
                window_width, ideal_Y, abf, filtered_sweepY, duration, bins_list
            )
            continue
        elif u == "3":
            if x > 0:
                x -= 1
            else:
                print("Already at the first file. Can't rerun previous file.")
            continue
        elif u == "4":
            try:
                cutoff = float(input("Enter cutoff pA value: ").strip())
                continue
            except ValueError as ve:
                print(f"Invalid input for cutoff pA: {ve}")
                continue
        elif u == "5":
            try:
                input_cutoff_Freqs = input(
                    "Histogram cutoff pA by level ground(low high) level0(low high) level1(low high) level2(low high) level3(low high) level4(low high) level_r_2(low high) level_r_3(low high) level_r_4(low high) level_r_5(low high) level5(low high)"
                ).strip()

                if any(char.isalpha() for char in input_cutoff_Freqs):
                    raise ValueError("Cutoff frequencies must be numeric.")

                cutoff_Freqs = list(map(float, input_cutoff_Freqs.split()))

                for i in range(len(cutoff_Freqs)):
                    pA_levels[i] = cutoff_Freqs[i]

                # Calculate the total time excluding noise in seconds
                calc_total_time = 60 - sum(
                    stop - start for start, stop in zip(spike_start, spike_stop)
                )
                total_time.append(calc_total_time)

                # Store what times were removed
                calc_data_removed = ", ".join(
                    f"{start}-{stop}" for start, stop in zip(spike_start, spike_stop)
                )
                data_removed.append(calc_data_removed)

                # Add the values that were used in pA_levels
                calc_open_levels = "; ".join(
                    f"{pA_levels[i]}, {pA_levels[i+1]}"
                    for i in range(0, len(pA_levels), 2)
                )
                open_levels.append(calc_open_levels)
                # Summing up the number of times each value occurs in the file
                abf_sweepY = np.array(abf.sweepY)
                pA_levels_pairs = [
                    (pA_levels[i], pA_levels[i + 1])
                    for i in range(0, len(pA_levels), 2)
                ]
                time_levels = []

                for lower, upper in pA_levels_pairs:
                    time_levels.append(
                        np.sum((abf_sweepY >= lower) & (abf.sweepY <= upper)) / 20
                    )

                (
                    time_closed_val,
                    time_level0_val,
                    time_level1_val,
                    time_level_r_2_val,
                    time_level2_val,
                    time_level_r_3_val,
                    time_level3_val,
                    time_level_r_4_val,
                    time_level4_val,
                    time_level_r_5_val,
                    time_level5_val,
                ) = time_levels

                lipid_list.append(lipid)
                # placeholders
                tempature.append(0)
                voltage.append(0)
                abf_file.append(abf_file_number)
                time_closed.append(time_closed_val)
                time_level0.append(time_level0_val)
                time_level1.append(time_level1_val)
                time_level2.append(time_level2_val)
                time_level3.append(time_level3_val)
                time_level4.append(time_level4_val)
                time_level_r_2.append(time_level_r_2_val)
                time_level_r_3.append(time_level_r_3_val)
                time_level_r_4.append(time_level_r_4_val)
                time_level_r_5.append(time_level_r_5_val)
                time_level5.append(time_level5_val)

                spike_start.clear()
                spike_stop.clear()
                pA_levels.clear()
            except ValueError as ve:
                print(f"Invalid input: {ve}")
                continue
        elif u == "6":
            break
    x += 1

# all the variables that will be displayed in the excel files

abf_data = {
    "ABF file number": abf_file,
    "tempature(C)": tempature,
    "lipid": lipid,
    "Total Time(s)": total_time,
    "Voltage(mV)": voltage,
    "Time closed(ms)": time_closed,
    # even if not used need to be same length
    "Level 0 time(ms)": time_level0,
    "Level 1 time(ms)": time_level1,
    "Level 2 time(ms)": time_level2,
    "Level 3 time(ms)": time_level3,
    "Level 4 time(ms)": time_level4,
    "Level 5 time(ms)": time_level5,
    "Level 2 reduced time(ms)": time_level_r_2,
    "Level 3 reduced time(ms)": time_level_r_3,
    "Level 4 reduced time(ms)": time_level_r_4,
    "level 5 reduced timme (ms)": time_level_r_5,
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
        "Level 5 time(ms)",
        "Level 2 reduced time(ms)",
        "Level 3 reduced time(ms)",
        "Level 4 reduced time(ms)",
        "Level 5 reduced time(ms)",
        "Data Removed(s)",
        "Limits of open levels currents (pA)",
    ],
)

df1 = df1.groupby("ABF file number", as_index=False).last()

# changes excel file name and gives it a path then outputs
excel_loc = os.path.join(filesPath, "output.xlsx")
with pd.ExcelWriter(excel_loc, engine="xlsxwriter") as writer:
    df1.to_excel(writer, sheet_name="data", index=False)

print("done")
