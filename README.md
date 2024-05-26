# resistanceRamp
@author: grabills

# Guide to Analyzing CA1 Step Resistance Measurements

This guide will help you understand how to analyze CA1 step resistance measurements without using the PClamp software suite. This process involves simulating the behavior of an LCR circuit, which PClamp cannot measure directly through the voltage step procedure. The analysis uses a program called `ResistanceRamp.py`.

## Overview

Our experimental setup involves applying a voltage through an electrode in a salty water solution, which is similar to current flowing through a wire. A capacitor, representing a bilayer, is placed between the positive and negative terminals. As we shift the voltage across it, the capacitor causes an exponential decay since the voltage across a capacitor cannot change instantly. This is why we use the Resistance Ramp procedure.

## Setup Instructions

1. **Organize Data**: Place all the data you want to analyze in a directory that you can access from your terminal.
2. **Compile the Program**: Navigate to that directory in your terminal and compile the `ResistanceRamp.py` script. This tells the program to analyze the data within the specified path.

## Key Functions and Their Roles

- **`calculate_standard_error`**: This function calculates the standard error for a given list of data points.

- **`low_pass`**: This function applies a Gaussian filter to the dataset (`abf.sweep(x,y)`) to reduce noise. Here, `x` corresponds to voltage and `y` to current. The Gaussian filter smooths the data based on a parameter called sigma.

- **`filter`**: This function removes data points marked as (NaN) by the `low_pass` function. Note that this currently does not adjust other datasets accordingly, which can cause issues for the `n_reg` function.

- **`n_reg`**: This function graphs the voltage and current data and performs exponential regression. It calculates the average values at the end of each data section and allows users to remove unwanted points. It also provides an R-squared value to estimate the data fit.

- **`averageI`**: This function segments the `abf.sweep(x,y)` data into sections, averaging the values over a specified time interval (2 seconds for 2023 purposes, but this can be adjusted). The time array is in milliseconds and does not include the initial upward step to avoid introducing high outliers.

## Additional Notes

- **OS Integration**: The program is designed to work based on the directory from which it is called. It iterates through all files in the specified directory, and you can choose where to save the results.
- **Limitations**: Some functionality, such as adjusting datasets alongside filtering, is not fully implemented. This can create challenges, particularly for graphing with the `n_reg` function.