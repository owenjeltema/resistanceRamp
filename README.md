# resistanceRamp

The function of this code is to analyze the CA1 step resistance measurements without using the PClamp software suite.

To use code: find file in directory with terminal command "ls", then select folder with "cd .\<folder_name>\". Running the file offers several prompts, which may be used to select data to analyze. Once commanded, the code will output a graph with datapoints on intervals of 10. Points that appear erroneous or inconsistent may then be removed by closing the window and typing the numbers to delete into the terminal in the form "10 30 50" (this example will delete datapoints at 10, 30, and 50 seconds). Data will then be adjusted to omit these datapoints, and conductance, resistance, and error values will be displayed as the result of the adjusted dataset.

There is some functionality that wasn't added but could become nessessary depending on use. The low_pass and filter methods support filtering out anomalous datapoints via guassian transformations. However, they currently delete voltages that the methods remove. The base functionality is nessessary, but means whatever list is given to the functions will not nessessarly have it's indices match the time list. This creates issues for the n_reg function, which performs much of the analysis on the abf.sweep(x,y) files. X corresponds to voltage, and Y current. 


Summary of functions:

Calculate_standard_error: The calculate_standard_error, calculates standard error for a given list.

low_pass: The low_pass function applies a gaussian filtering to a abf.sweep(x,y) which correspond to the datasets for voltage and current. This in tandem with the filter function can apply and fit a filter to a dataset to reduce noise corresponding to the sigma.

Filter: The filter function removes points dictated by the (Nan) from the low_pass function. This currently does not go back and edit other necessary dataset alongside the given resulting in graphing challenges for n_reg.

n_reg: The n_reg function graphs the given voltage and current, with an exponential regression. The function also takes the step averages at the end of each specified data section and allows users to remove wanted points. The function also has a r-squared calculation which provides an rough estimate for the data's fit.

AverageI: The averageI function segments the abf.sweep(x,y) into segments which are averaged by a timeshift, which is the amount of time at the step the user wants to sample. For 2023 purposes this was 2 seconds due to the higher accuracy, but lower can also be acceptable. The time array is in milliseconds and doesn't include the upward step, since it would introduce high outliers.

Note on use: the OS integration allows for ResistanceRampTest to work based on the directory that is calling it. This means it should be called from the directory that has the files that need to be analyzed. The function will then iterate through all files in that directory and the user can choose where to place the results as wanted.
