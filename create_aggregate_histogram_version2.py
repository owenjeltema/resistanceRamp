# -*- coding: utf-8 -*-
"""
Created on Mon Jul 26 10:19:53 2021

@author: mrear
"""

# -- Imports --     --      --      --      --      --      --      --      --

import pandas
import pyabf
import matplotlib.pyplot as plt
from low_pass_filter_abf_version1 import low_pass               #changed to 1 in 2023
import os

# -- Constants --   --      --      --      --      --      --      --      --

VERBOSE = True          # Recommended to stay True
cutoff = 1000             # Used for low-pass filter
xmin, xmax = -1, 600
ymin, ymax = 0, 12000   # Visual limits of the plot
bin_size = 0.01         # Width of each bin on the histogram - must mulitply into 1 evenly, rounding is fine
directory = r"C:\Users\dcmou\Downloads\work\resistanceRamp\ion_data" 
# ^ This directory should contain all the ABF files to be aggregated. 
subdir = r"\Analysis Spreadsheets"
# ^ This should be a subdirectory of the first directory, containing
# spreadsheets of each ABF file in the first. They should be named 
# identically to their paired ABF files, but with the .xlsx suffix.

# -- Function definitions --        --      --      --      --      --      --

# Truncate f to n decimal places, with NO rounding errors left behind
def truncate(f, n):
    s = '{}'.format(f)                             # Turns f into a string
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)            # Handles scientific notation
    i, p, d = s.partition('.')                     # Separates around the decimal point
    return float('.'.join([i, (d+'0'*n)[:n]]))     # Rejoins around the decimal point with truncate

# -- Main code --   --      --      --      --      --      --      --      --

aggregate = []                          # The list all data will be appended to
for file in os.listdir(directory):      # Iterate over every file in the named directory

    # If the file is not an ABF file, skip it
    if file[-4:] != ".abf":
        continue
    
    # These lines exist because Python is stupid and doesn't understand backslashes
    abf_filename = directory + r"\#" + file
    abf_filename = abf_filename.replace("#", "")
    xlsx_filename = directory + subdir + r"\#" + file
    xlsx_filename = xlsx_filename.replace("#", "")
    xlsx_filename = xlsx_filename.replace(".abf", ".xlsx")
    
    # Import ABF file, define some variables, and run it through a low-pass filter
    abf = pyabf.ABF(abf_filename)
    duration = abf.sweepLengthSec
    time_step= duration / len(abf.sweepY)
    cutoff = 1000
    filtered_sweepY= low_pass(abf.sweepY, abf.sweepX, cutoff, time_step)
    
    # This block sets zero_point to the average current of the 0th bin in an ABF file, so
    # that we can then subtract off the zero point and get the actual magnitude of each 
    # sample in the file.
    df_zero = pandas.read_excel(xlsx_filename, sheet_name = 1, usecols = ["levels", "level means (pA)"]) # Read averages into a DataFrame
    for level in df_zero.values:
        if level[0] == 0:                     # if the trace code identified the level as closed:
            zero_point = level[1]             # then record the mean current of all closed samples as zero_point
    for i in range(len(filtered_sweepY)):
        filtered_sweepY[i] -= zero_point      # now subtract off zero_point from every value
    
    # Append to the aggregate list
    aggregate.extend(filtered_sweepY)
    
    if VERBOSE: print(abf_filename, "done")

if VERBOSE: print("\n" + str(len(aggregate)), "samples aggregated", "\n")

# Set histogram bins based on given plot range and bin sizes
bin_vals =[]        # The magnitudes of the bins
bins = {}           # The indices of the bins, paired with the number of samples in them
for i in range(int((xmax - xmin) / bin_size)):
    bin_vals.append(round(xmin + bin_size * i, 2))
    bins[i] = 0
    # bins[round(xmin + bin_size * i, 2)] = 0

# bin n = xmin + bin_size * n
# n = (bin n - xmin) / bin_size
# 0th bin is at xmin
# final bin is at xmax - bin_size

if VERBOSE: counter = 0
for sample in aggregate:
    
    # Skip samples outside the plotted area
    if (sample < xmin) or (sample > xmax):
        continue
    
    # Compute the bin index to put the sample into
    index = int((sample - xmin) / bin_size)
    bins[index] += 1
    
    # Print out progress in this loop
    if VERBOSE:
        counter += 1
        if counter % 1000000 == 0:
            print(counter, "samples put into bins")

# Finally, plot the bins on a bar graph (the output plot is a histogram)
plt.bar(bin_vals, bins.values(), width=0.01)
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)
plt.xlabel("Magnitude of sample (pA)")
plt.ylabel("Number of occurrences")
plt.show()