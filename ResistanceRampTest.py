import pyabf
import math
import matplotlib.pyplot as plt
import pyabf.filter
import numpy as np
from statistics import mean
import os
import math

# include that other formula

# need to instal
# pip install xlrd
# also abf


def calculate_standard_error(data):
    n = len(data)
    mean = sum(data) / n
    squared_diff = [(x - mean) ** 2 for x in data]
    variance = sum(squared_diff) / (n - 1)
    standard_error = math.sqrt(variance / n)
    return standard_error


# Filters the data and returns and list with the nan removed
# a is the array that will be filtered
def low_pass(listToFilter):
    # aplies the low pass
    sigma = 10  # change this value to increase or decrease the level of filtering
    pyabf.filter.gaussian(abf, 0)  # remove old filter
    pyabf.filter.gaussian(abf, sigma)  # apply custom sigma
    abf.setSweep(0)  # reload sweep with new filter

    # removes the values that are associted with NaN
    listWithoutNan = np.logical_not(np.isnan(abf.sweepY))
    listToFilter = listToFilter[listWithoutNan]
    return listToFilter


# Removes the data that is outside the lower and upper bound
# list is the list that needs to be filtered
def filter(lower, upper, list):
    # removes the values that are associted with NaN
    low = np.where(abf.sweepX == lower)[0][0]
    up = np.where(abf.sweepX == upper)[0][0]
    list = list[low:up]
    return list


# quadric
# takes the average data of the voltage steps, plots it against the original and returns the conductance and resistanace
# voltage is a the voltage step list
# current is the list of current values
# n is the degree of polynomial and range is the scale of the y axis
def n_reg(voltage, current, n, range,abf_num):
    # polynomial fit with degree = 2
    # x,y, n
    p, cov = np.polyfit(voltage, current, n, cov=True)
    #
    model=np.poly1d(p)
    #error of G = sqrt(cov[1][1])
    # add fitted polynomial line to orignal data
    fig = plt.figure()
    ax = fig.add_subplot(111, label="1")

    # original data
    ax.plot(abf.sweepX, abf.sweepY, alpha=0.3, label="original")
    ax.axis([0, 165, abf.sweepY[0] - range, abf.sweepY[15990] + range])
    ax.set_xlabel("time seconds", color="C0")
    ax.set_ylabel("current pA", color="C0")
    ax.tick_params(axis="x", colors="C0")
    ax.tick_params(axis="y", colors="C0")

    # step averages
    ax2 = ax.twiny()
    ax2.scatter(voltage, current, color="C2")
    ax2.axis([-10, 155, abf.sweepY[0] - range, abf.sweepY[15990] + range])
    ax2.xaxis.tick_top()
    ax2.set_xlabel("voltage mV", color="C2")
    ax2.xaxis.set_label_position("top")
    ax2.tick_params(axis="x", colors="C2")
    polyline = np.linspace(1, 150, 50)
    plt.plot(polyline, model(polyline))
    plt.title("resistance Data File: "+ abf_num)


    # find the slope at zero
    print("condutance nS", model[1], "resistance", pow(model[1], -1))
    print("Error in conductance",math.sqrt(cov[1][1]))

    #displays the graph
    plt.show()

    # find the r-squared
    results = {}
    yhat = model(voltage)
    ybar = np.sum(current) / len(current)
    ssreg = np.sum((yhat - ybar) ** 2)
    sstot = np.sum((current - ybar) ** 2)
    results["r_squared"] = ssreg / sstot
    print(results)

    


# takes the last n seconds of the graph and takes the average of the current
# returns a list of the averages at each step
# amount is the amount of time that is used to get data from
# to-dp
def averageI(list, timeshift):
    AverageTimeShiftDataAllSteps = []
    timeArray = [
        990,
        1990,
        2990,
        3990,
        4990,
        5990,
        6990,
        7990,
        8990,
        9990,
        10990,
        11990,
        12990,
        13990,
        14990,
        15990,
    ]
    for x in timeArray:
        TimeShiftData = list[x - timeshift : x]
        AverageTimeShiftDataAllSteps.append(mean(TimeShiftData))
    return AverageTimeShiftDataAllSteps


# iterate through all files within directory that IDE is currently within. Set path to be wherever dataset is for easy itteration and saving.
for file in os.listdir():
    # Check whether file is in abf format or not
    if file.endswith(".abf"):
        # call read abf file
        abf = pyabf.ABF(file)
        stepCurrent = averageI(abf.sweepY, 100)
        voltageList = [
            0,
            10,
            20,
            30,
            40,
            50,
            60,
            70,
            80,
            90,
            100,
            110,
            120,
            130,
            140,
            150,
        ]
        # larger scale (better for higher temps)
        print("**Exit file to move into data removal or file progression**")
        print("Standard Error: ", calculate_standard_error(stepCurrent), file)
        print(file, "  "), n_reg(voltageList, stepCurrent, 2, 2,file)
        print("enter voltages that should be removed, n = no data")
        remove = input("Enter values:")
        if remove != "n":
            delete = remove.split()
            for x in delete:
                a = int(x)
                index = voltageList.index(a)
                voltageList.pop(index)
                stepCurrent.pop(index)
        print("\n", "**information after removal**")
        print("Standard Error: ", calculate_standard_error(stepCurrent), file)
        n_reg(voltageList, stepCurrent,2 , 2, file), 
        print("linear fit")
        
        
        
        
        print(
            file, "\n", "######################################", "\n"
        )


# plot the original data


"""
#plot the filtered data 
abf.setSweep(0)  # reload sweep with new filter
label = "sigma: %.02f" % (10)
plt.plot(abf.sweepX, abf.sweepY, alpha=.8, label=label) 
"""


# Create a graph of the pre and post filter data
