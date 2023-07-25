#Create_ideal_trace_abf_false_positives_version2.py


The function of this code is to analyize the opening lengths and ratios of measured ion channels.

Much of the difference between this year's code is in optimizations. Many of the misc functions, were placed in defonitions for easy access and error prevention, the bin system which is defined more fully in last year's README was scaled back as was possible, and finally the old histogram function was removed.

The new additions are: a new histogram function, os integration and ui, along with functionallity for excel merging.

How to use: the directory you are running the code from should be set to where your data is. This means that if you have a folder for data you should be compiling from within that folder, so your current directory is where your data is. This ensures files can be accessed without changing them out individually. resultant excel files will be placed into the same folder and under the same name with a .xlsx. The bottom few lines have a very important script for combining the individual excel files into a singular excel file. Only have that line uncommented when you want to compile a full data sheet.


Definition of terms:
Cutoff--the amount of lowpass filtering being put onto the data.
voltage-- the voltage at which data was taken
pA levels-- these are the variables user will input to determine the activation levels, for example: when the ion chanell is closed. This separates data into helpful bins so that it can be analized in excel.

Set level function: makes the varibles the rest of program uses along with helping with formating abf file reader.

Histogram: takes the file your in, the cutoff (low pass), and two arrays. It then graphs the filtered sweep. When graphing it does not like removing zero or 60. Instead use 59.99, and 0.01 when using histogram.

large spike: This is the method by which data is removed from the code, deletes the values from the arrays, so they won't be sampled for the histogram.

The main UI, has features for moving to different files, if you type file, then however you want to search. The skip simply proceeds to the next index in the for loop. Noise removal happens with the cmd dr then you can give the start and ending which all data between those will be removed.


In the section after this is where data is made ready for an excel file, and is compiled and time spent in each level is calculated and along with file number and other misc information.

Imediately after is the overal excel doc creator, which synthesizes all created excel files into one large file with all the data. Ideally this won't be used untill you are finished creating the individual files.


The code itself is run from Create_ideal_trace_abf_false_positives_version2.py.