# ResistanceRamp
@author: grabills

# Guide to Analyzing CA1 Step Resistance Measurements

This guide will help you understand how to analyze CA1 step resistance measurements without using the PClamp software suite. This process involves simulating the behavior of an LCR circuit, which PClamp cannot measure directly through the voltage step procedure. The analysis uses a program called `ResistanceRamp.py`.

## Overview

Our experimental setup involves applying a voltage through an electrode in a salty water solution, which is similar to current flowing through a wire. A capacitor, representing a bilayer, is placed between the positive and negative terminals. As we shift the voltage across it, the capacitor causes an exponential decay since the voltage across a capacitor cannot change instantly. This is why we use the Resistance Ramp procedure.

## Setup Instructions

1. **Organize Data**: Place all the data you want to analyze in a directory that you can access from your terminal.
2. **Compile the Program**: Navigate to that directory in your terminal and compile the `ResistanceRamp.py` script. This tells the program to analyze the data within the specified path.

## How to Use
The basic user interface is a prompt with 3 options:
```python
rerun a file: "rerun"
continue to current file: "cont"
press enter to quickly move through files
go to specific index: "number"
```
- `rerun`: shifts index back so previous file can be analyzed again.
- `cont`: will begin analysis on file.
- `number`: will go to a specific file number and give index base 0.
- `enter`: pressing enter will quickly iterate through files and resume `cont` from a new starting position.

## Key Functions and Their Roles

- **`calculate_standard_error`**: This function calculates the standard error for a given list of data points.

- **`low_pass`**: This function applies a Gaussian filter to the dataset (`abf.sweep(x,y)`) to reduce noise. Here, `x` corresponds to voltage and `y` to current. The Gaussian filter smooths the data based on a parameter called sigma.

- **`filter`**: This function removes data points marked as (NaN) by the `low_pass` function. Note that this currently does not adjust other datasets accordingly, which can cause issues for the `n_reg` function.

- **`n_reg`**: This function graphs the voltage and current data and performs exponential regression. It calculates the average values at the end of each data section and allows users to remove unwanted points. It also provides an R-squared value to estimate the data fit.

- **`averageI`**: This function segments the `abf.sweep(x,y)` data into sections, averaging the values over a specified time interval (2 seconds for 2023 purposes, but this can be adjusted). The time array is in milliseconds and does not include the initial upward step to avoid introducing high outliers.

## Additional Notes

- **OS Integration**: The program is designed to work based on the directory from which it is called. It iterates through all files in the specified directory, and you can choose where to save the results.
- **Limitations**: Some functionality, such as adjusting datasets alongside filtering, is not fully implemented. This can create challenges, particularly for graphing with the `n_reg` function.



# *Create_ideal_trace_abf_false_positives_version2.py*

## The function of this code is to analyze the opening lengths and ratios of measured ion channels.

Much of the difference between this year's code is in optimizations. Many of the miscellaneous functions were placed in definitions for easy access and error prevention. The bin system, which is defined more fully in last year's README, was scaled back as much as possible, and the old histogram function was removed. In addition to these changes, the **Create_ideal_trace_abf_set_levels** was combined into **Create_ideal_trace_abf_levels_version2**.

### New Additions
- A new histogram function
- OS integration and UI
- Functionality for Excel merging

### How to Use
The directory you are running the code from should be set to where your data is. This means that if you have a folder for data, you should be compiling from within that folder, so your current directory is where your data is. This ensures files can be accessed without changing them out individually. Resultant Excel files will be placed into the same folder and under the same name with a `.xlsx` extension. The bottom few lines have a very important script for combining the individual Excel files into a single Excel file. Only have that line uncommented when you want to compile a full data sheet.

## Definition of Terms
- **Cutoff**: The amount of low pass filtering being applied to the data.
- **Voltage**: The voltage at which data was taken.
- **pA levels**: These are the variables users will input to determine the activation levels, such as when the ion channel is closed. This separates data into helpful bins for analysis in Excel.

## Key Functions
- **Set Level Function**: Makes the variables the rest of the program uses, along with helping with formatting the ABF file reader.
- **Histogram**: Takes the file you're in, the cutoff (low pass), and two arrays. It then graphs the filtered sweep. When graphing, avoid removing 0 or 60; instead, use 59.99 and 0.01.
- **Large Spike**: This method removes noise data from the arrays, so they won't be sampled for the histogram.
- **The Main UI**: Has features for moving to different files, noise removal, and graphing data. It allows users to segment activity into bins (e.g., closed, lv 0, lv 1, lv 2, etc.) and saves these settings between files.

### Additional Features
In the section after this, data is prepared for an Excel file. Time spent in each level is calculated, along with file number and other miscellaneous information. Immediately after, the overall Excel document creator synthesizes all created Excel files into one large file with all the data. Ideally, this won't be used until you are finished creating the individual files.

## Code Details

### Create_ideal_trace_abf_false_positives_version2.py
Allows a person to look at the idealized trace and identify false positives, then redraws the trace with the false positives accounted for. It also recalculates the average length and means, and finally formats and produces the Excel file.

### Functions
- **low_pass_filter_abf_version1**: A low pass filter.
- **ideal_trace_same_bin_version2**: A subroutine to determine if two values are in the same bin.
- **ideal_trace_combine_repeats_version2**: Combines consecutive events at the same level after removing false positives.
- **ideal_trace_calculate_mean_version2**: Finds the mean current and average length for each level.
- **ideal_trace_make_ideal_Y_list_version2**: Creates a list of Y values that form the idealized trace.
- **Ideal_trace_graph_formatting_version2**: Formats the graph of filtered data, idealized trace, and dotted lines at bin junctions with a scrollbar. Includes an input to adjust graph height.
- **set_level**: The set level function from **Create_ideal_trace_abf_set_levels_version2**.
- **histogram**: Creates the histogram, given the file location, start and stop times, and the low pass filter.
- **large_spike**: Performs noise removal. If insufficient, additional options from last year's code can be used.
- **misc code**: Commented out unless the user wants to compile all `.xlsm` (Excel) files into one massive file. Ensure that the VS Code directory compiling the program is in the same directory as the Excel files for compilation.

```python
# Example code block for compiling Excel files
path = rf"{os.getcwd()}\\"
filenames = [file for file in os.listdir(path) if file.endswith('.xlsx')]

df = pd.concat([pd.read_excel(path + file) for file in filenames], ignore_index=True)
df.to_excel("output.xlsx")
```
### Inputs
- **Location**: The location on your computer where the Excel file will be saved, along with the file name.
- **spike_start**: A list of approximate start locations for large noise spikes.
- **spike_stop**: A list of corresponding stop locations for large noise spikes. Must be the same length as spike_start.

### Ideal_trace_graph_formatting_version2
- **top_Yvalue**: The upper value shown on the y-axis of the graph.

### Errors
- **Can't remove 0 or 60**: Instead, remove 0.01 and 59.99. This issue likely relates to how time is calculated with the `abf.sweep(x,y)` arrays. Removing data from the end changes the scale, causing the histogram function to crash.


