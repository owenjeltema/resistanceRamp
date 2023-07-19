# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 14:37:16 2021

@author: David Ruiter


HOW TO USE THIS PROGRAM:
    Name the directory variable with the complete file path of the directory you'll be analysing
    spreadsheets from. This directory should have analysis spreadsheets in it, in the format output
    by Create_ideal_trace_abf_false_positives_version2.py. The directory may have other files in
    it as well, but any spreadsheets should be in this format. Adjust your tolerance to the error 
    bar of gA opening magnitudes, and run. Set VERBOSE to True if you want output listing which 
    file each event came from.
"""

# -- Imports --     --      --      --      --      --      --      --      --

import pandas
import os
import matplotlib.pyplot as plt

# -- Constants --   --      --      --      --      --      --      --      --

directory = r"C:\Users\mrear\Documents\Summer 2021\Analysis Spreadsheets"       # Directory to find spreadsheets in
tolerance = 0.3         # We will collect openings of magnitude 2.6 pA +- this value
VERBOSE = False         # Print verbose output to the console?
show_plot = True

# -- Main code --   --      --      --      --      --      --      --      --

gA_openings = []        # List for identified gA openings to be placed into
openings_files = []     # The file names that the identified openings came from - only used for reference

for file in os.listdir(directory):      # Iterate over every file in the named directory
    # If the file is not an Excel sheet, skip it
    if file[-5:] != ".xlsx":
        continue
    
    # These two lines exist because Python is stupid and doesn't understand backslashes.
    filename = directory + r"\#" + file
    filename = filename.replace("#", "")

    # This block sets zero_point to the average current of the 0th bin in an ABF file, so
    # that we can then subtract off the zero point and get the actual magnitude of an opening
    # with respect to the closed state. 
    df_zero = pandas.read_excel(filename, sheet_name = 1, usecols = ["levels", "level means (pA)"])     # Read averages into a DataFrame
    df_zlist = df_zero.values.tolist()  # Convert the DataFrame to a list of lists in form [bin_number, mean_current]
    zero_point = 0
    for level in df_zlist:
        if level[0] == 0:
            zero_point = level[1] 
    
    df_main = pandas.read_excel(filename, sheet_name = 2, usecols = ["length (s)", "mean (pA)"])        # Read list of events into a DataFrame
    df_list = df_main.values.tolist()   # Convert the DataFrame to a list of lists in form [length, mean_current]
    # For each channel event, if its mean current minus the zero_point is within the given
    # tolerance of 2.6 pA, append it to the list of actual gA openings, and record which
    # file it came from in a separate list.
    for event in df_list:
        if (event[1] > (2.6 - tolerance + zero_point)) and (event[1] < (2.6 + tolerance + zero_point)):
            event[1] -= zero_point
            gA_openings.append(event)
            openings_files.append(filename)
    
    if VERBOSE: print(filename, "done")

# End output listing which file each identified event came from
if VERBOSE: 
    print()
    for i in range(len(gA_openings)):
        print(gA_openings[i], "from", openings_files[i])
        
print("Total number of openings found:", len(gA_openings))

if show_plot:
    plt.scatter(*zip(*gA_openings))
    plt.xlabel("Dwell time (s)")
    plt.ylabel("Opening magnitude (pA)")
    plt.title("Gramicidin-A Channel Dwell Time vs. Magnitude of Opening")