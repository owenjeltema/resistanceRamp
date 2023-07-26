# *Create_ideal_trace_abf_false_positives_version2.py*


# **The function of this code is to analyize the opening lengths and ratios of measured ion channels.**

Much of the difference between this year's code is in optimizations. Many of the misc functions, were placed in defonitions for easy access and error prevention, the bin system which is defined more fully in last year's README was scaled back as was possible, and finally the old histogram function was removed. In addition to these, the **Create_ideal_trace_abf_set_levels**, was combined into the **Create_ideal_trace_abf_levels_version2**.
**The new additions** are: a new histogram function, os integration and ui, along with functionallity for excel merging.

**How to use**: the directory you are running the code from should be set to where your data is. This means that if you have a folder for data you should be compiling from within that folder, so your current directory is where your data is. This ensures files can be accessed without changing them out individually. resultant excel files will be placed into the same folder and under the same name with a .xlsx. The bottom few lines have a very important script for combining the individual excel files into a singular excel file. Only have that line uncommented when you want to compile a full data sheet.


# **Definition of terms:**
Cutoff--the amount of lowpass filtering being put onto the data.
voltage-- the voltage at which data was taken
pA levels-- these are the variables user will input to determine the activation levels, for example: when the ion chanell is closed. This separates data into helpful bins so that it can be analized in excel.

**Set level function**: makes the varibles the rest of program uses along with helping with formating abf file reader.

**Histogram**: takes the file your in, the cutoff (low pass), and two arrays. It then graphs the filtered sweep. When graphing it does not like removing zero or 60. Instead use 59.99, and 0.01 when using histogram.

**large spike**: This is the method by which data is removed from the code, deletes the values from the arrays, so they won't be sampled for the histogram.

**The main UI**: has features for moving to different files, if you type file, then however you want to search. The skip simply proceeds to the next index in the for loop. Noise removal happens with the cmd dr then you can give the start and ending which all data between those will be removed. To move between files the user can input *file*, then decide if they want to search by file name ( year, month, day, run), which is abreviated as *fn*, or if they want to search as index. The index search uses the abf files in the directory of the user, and uses standard coding rules: file 1 is index 0, file 2 is index 1, etc. Beyond the file system to access noise removal, the user should type *dr* (data removal), and can then give a start and stop time. To exit data removal, the user can input *done*, which will exit back to main section. To graph data the user can input *graph*, which will display a histogram that can be zoomed by mouse then will display the ion channel graph, which can moved via the slider or zoomed by the mouse. If the user wants to select bins to segement activity, eg: closed, lv 0, lv 1, lv 2, ect. they can do so by typing *data* and following prompts. This is the only aspect of the program that should save between files in your chosen directory so it doesn't need to be changed unless you want it to. When finished analyzing a file the user on the main UI can type *done* and the file will be finished and an excel file will be created of the same in the users directory.


In the section after this is where data is made ready for an excel file, and is compiled and time spent in each level is calculated and along with file number and other misc information.

Imediately after is the overal excel doc creator, which synthesizes all created excel files into one large file with all the data. Ideally this won't be used untill you are finished creating the individual files.


# **The code itself is run from Create_ideal_trace_abf_false_positives_version2.py.**



**Create_ideal_trace_abf_false_positives_version2**: Allows a person to look at the idealized trace and identify false positives, then redraws the trace with the false positives accounted for. It also recalculates the average length and means. It finally formats and produces the excel file. 

**low_pass_filter_abf_version1**: A low pass filter 

**ideal_trace_same_bin_version2**: a subroutine to determine if two values are in the same bin as each other.  

**ideal_trace_combine_repeates_version2**: After false positives are removed, the chronological list of levels and their means and lengths often have several events at the same level in a row. This combines those events. 

**ideal_trace_calculate_mean_version2**: Finds the mean current and average length for each level. 

**ideal_trace_make_ideal_Y_list_version2**: Takes the mean of each level, the list of levels, and the length of each event to create a list of Y values that form the idealized trace.  

**Ideal_trace_graph_formatting_version2**: Has the formatting to graph the filtered data, idealized trace and dotted lines at the bin junctions with a scrollbar. It also has an input to adjust the height of the graph. 

**set_level**: The set level function is all that was needed from the **Create_ideal_trace_abf_set_levels_version2**.

**histogram**: This creates the histogram, given the file location for the title, the start and stop times, and the low pass wanted.

**large_spike**: this performs the noise removal for our purposes, the code last year has a couple of other options if this becomes insuffient. Making the code into a function is quite simple and the **Large_spike** can serve as nearly identical example.


**misc code**: this block of code should be commented out less the user wants all .xlsm (excel) files compiled into one massive file. This is helpful for getting data consolidated into one place, however this works off current directory so make sure that the VS Code directory that is compiling the program is in the same directory as the excel files so they can be compiled.
<!-- path = rf"{os.getcwd()}\\"
filenames = [file for file in os.listdir(path) if file.endswith('.xlsx')]

df = pd.concat([pd.read_excel(path + file) for file in filenames], ignore_index=True,)
df.to_excel("output.xlsx") -->


 

# **Inputs**


**Cutoff**: cutoff value for low pass filter (in Hz) 

**Window_width**: for the scrollbar on the graph, how many seconds of data are displayed at once 

**Abf**: the abf file  

**bins_list**: list of values that define the junctions between different levels of events 


**Create_ideal_trace_abf_false_positives_version2**: 

**Location**: the location you want the excel file and your computer and the file name 

**spike_start**: a list with the approximate start locations for large noise spikes, can have multiple starts for different spikes, but there is usually only one 

**spike_stop**: a list with the corresponding approximate stop location for a large noise spike. Every level change between these values is categorized as noise and assigned to the noise level and does not affect any mean values. Must be the same length as spike_start. 

**Ideal_trace_graph_formatting_version2**: 

**top_Yvalue**: The upper value shown on the y axis of the graph  

# **Errors**

**Can't remove 0 or 60**: instead remove 0.01 and 59.99, the reason this is isn't fully understood but it likely has to do with the indexing for the abf.sweep(x,y) arrays. The assumption is that data can be removed from the middle due to the specifics on how time is calculated with the points, ie each point is 1/10 millisecond which total out to be a minute and by removing from the end the scale changes which causes the histogram function to crash when called.

