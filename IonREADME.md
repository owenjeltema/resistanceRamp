# *Create_ideal_trace_abf_false_positives_version3.py*
**The function of this code is to analyize the opening lengths and ratios of measured ion channels.**

**For MacOS/Linux:** change any rf"{something}(backslash){something}" to f"{something}/{something}". Note that backslash changes to forward slash.

In summer 2024, **Create_ideal_trace_abf_levels_version2** was overhauled to fix bugs, reduce crashes, optimize performance, and add functionality, culminating in **Create_ideal_trace_abf_levels_version3**. Added functionality includes a peak-finding algorithm, dwell time analysis with filtering, and a more complete excel file export including error bar calculations and other dwell time and general calculations based on filter time.

**Last year's README Intro**: Much of the difference between this year's code is in optimizations. Many of the misc functions, were placed in defonitions for easy access and error prevention, the bin system which is defined more fully in last year's README was scaled back as was possible, and finally the old histogram function was removed. In addition to these, the **Create_ideal_trace_abf_set_levels**, was combined into the **Create_ideal_trace_abf_levels_version2**.
**The new additions** are: a new histogram function, os integration and ui, along with functionallity for excel merging.

# **User Directions**:
The directory the code runs from must be the folder where the files to be analyzed are stored. Use files from a single data run in each folder. Follow user interface to run code.

**Recommended procedure**:
Before running program set path to file directory. Setup code by changing variables noted in findLevels() method. Notes for setting variables are stated next to variables.
1. Choose lipid.
2. Check histogram and setup code as stated before.
3. Create new excel file/sheet for data run analysis notes. I recommend columns for file number, temperature, voltage, noise removed, levels manually altered, and notes (Example in "Summer2024 Data and Analysis" folder - "ION Channel Analysis File Notes" excel sheet). Add any other columns you find useful.
4. Run files as listed in file procedure.

**File procedure**:
1. Graph data and check second figure (capacitance/time figure). List any noisy sections in applicable excel column. If file is too noisy remove entire time range. I recommend removing any good time range with less than 2 seconds between noisy parts to avoid p-hacking.
2. Remove noise in program from listed excel file ranges.
3. Check histogram level ranges against program's identified level ranges. Program will print level and reduced level ranges to terminal. Check each level and reduced level against histogram figure and alter if program misses maximum. Program misses are fairly frequent, so make sure to check diligently. Recommendations for setting levels are listed below.
   - If bounds are not visibly incorrect: leave as is for consistency reasons. 
   - If only one bound is visibly incorrect: leave other bound as found by program. This is to remain consistent.
   - If bounds of seperate levels are overlapping, choose most obvious minimum as bound for both levels.
   - If levels -- especially level 0 -- are unclear, check excitations in second figure for clarity.
4. List any level range changes to be made in corresponding excel column.
5. Manually set pA level in program to match excel sheet.
6. Continue to next file.
7. When finishing analysis (either reaching end of file or exporting data) save "output.xlsx" as another name so file is not overwritten in the future. I recommend {date}+{lipid}

**User interface:**
1. Next file and record data. Records data to export later and moves on to next file.
2. Remove noise. Removes capacitance data in time range. This removes capacitance data everywhere in that time range and any analysis will skip over these time intervals.
3. Graph. Opens histogram figure of capacitance vs frequency. Then opens second figure of capacitance over time. Both must be closed before continuing.
4. Manually set pA level. Set all or individual capacitance level ranges (in pA/pF) based on histogram appearance. Individual changes are recommended in almost any case.
5. Change file. Rerun previous file or search for file based on 3-number code.
6. Change settings. Change cutoff frequency or histogram x-axis range.
7. Export raw data in time range. Export dwell times per level or capacitance data in time range in excel sheet.
8. End analysis and export excel. Stop program early and export excel sheet.

# **Definition of terms:**
- Cutoff-- lowpass filter cutoff frequency [Hz].
- voltage-- the voltage at which data was taken.
- pA levels-- top- and bottom- limits for activation levels for analysis.
- lowVal-- minimum value that data analysis features consider for activation.
- highVal-- maximum value that data analysis features consider for activation.
- pA_min-- minimum value that binning algorithm considers for activation.
- pA_max-- maximum value that binning algorithm considers for activation.
- histogram_min-- minimum value that histogram considers for activation.
- histogram_max-- maximum value that histogram considers for activation.
- files-- list of all files in repository sorted by number.

## Functions:
**set_level**: initializes variables program uses, formats abf file reader.

**histogram**: takes the file your in, the cutoff (low pass), and two arrays. Graphs filtered sweep with abf file depending on cutoff.

**large_spike**: Noise removal. Removes data from code and deletes spike ranges set by user from the arrays so they are not sampled for the histogram.

**calculate_histogram_times**: 

**The main UI**: 
- The file navigation system is used when finishing analysis on a file or when the user prompts the program to go to a specific file. Navigation is done with the run number, or the last three numbers of the abf file name.
- The user input functionality is done using input strings of numbers 1-8 depending on the user's intentions. All user inputs are done in while loops that break upon a valid input to avoid crashes.

**Create_ideal_trace_abf_false_positives_version2**: Allows a person to look at the idealized trace and identify false positives, then redraws the trace with the false positives accounted for. It also recalculates the average length and means. It finally formats and produces the excel file. 

**low_pass_filter_abf_version1**: A low pass filter 

**ideal_trace_same_bin_version2**: a subroutine to determine if two values are in the same bin as each other.  

**ideal_trace_combine_repeates_version2**: After false positives are removed, the chronological list of levels and their means and lengths often have several events at the same level in a row. This combines those events. 

**ideal_trace_calculate_mean_version2**: Finds the mean current and average length for each level. 

**ideal_trace_make_ideal_Y_list_version2**: Takes the mean of each level, the list of levels, and the length of each event to create a list of Y values that form the idealized trace.  

**Ideal_trace_graph_formatting_version2**: Has the formatting to graph the filtered data, idealized trace and dotted lines at the bin junctions with a scrollbar. It also has an input to adjust the height of the graph. 




# **Inputs**
**Create_ideal_trace_abf_false_positives_version2**:

**spike_start**: a list with the approximate start locations for large noise spikes, can have multiple starts for different spikes, but there is usually only one 

**spike_stop**: a list with the corresponding approximate stop location for a large noise spike. Every level change between these values is categorized as noise and assigned to the noise level and does not affect any mean values. Must be the same length as spike_start. 

# **Errors**
