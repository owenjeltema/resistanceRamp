# Dylan & Sebastian
import pyabf
import math
import matplotlib.pyplot as plt
import pyabf.filter
import numpy as np
from statistics import mean
import os
import math
import copy
import pandas as pd

# need to install
# pip install xlrd
# pip install pyabf
# pip install pandas
# pip install glob

# defines lists for excel exporting
abf_file_list = []
g_lin = []
bg_lin = []
r_lin = []
eg_lin = []
g_quad = []
bg_quad = []
r_quad = []
eg_quad = []
egb_lin = []


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


# delta
def Eq8_12(x_array):
    length = len(x_array)
    x_array_np = np.array(x_array)
    return length * sum(np.square(x_array_np)) - pow((sum(x_array)), 2)


# this calcutates A(Y-intercept)
def Eq8_10(x_array, y_array):
    x_array_np = np.array(x_array)
    return (
        sum(np.square(x_array_np)) * sum(y_array)
        - sum(x_array) * np.dot(x_array, y_array)
    ) / Eq8_12(x_array)


# this calculates B(slope)
def Eq8_11(x_array, y_array):
    length = len(x_array)
    return ((length * np.dot(x_array, y_array)) - sum(x_array) * sum(y_array)) / Eq8_12(
        x_array
    )


# this returns the uncertainity of Y
def Eq8_15(x_array, y_array):
    length = len(x_array)
    A = Eq8_10(x_array, y_array)
    B = Eq8_11(x_array, y_array)
    sum = 0
    for i in range(length):
        sum += pow(y_array[i] - A - B * x_array[i], 2)

    return math.sqrt((1 / (length - 2)) * sum)


# this returns the uncertainity of the slope
def Eq8_17(x_array, y_array):
    return Eq8_15(x_array, y_array) * math.sqrt(len(x_array) / Eq8_12(x_array))


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
def n_reg(volt, cur, n, range, abf_num):
    voltage = copy.deepcopy(volt)
    current = copy.deepcopy(cur)

    # polynomial fit with degree = 2
    # x,y, n

    if n == 2:
        p, cov = np.polyfit(voltage, current, n, cov=True)
        model = np.poly1d(p)
        # adds post processed data to dataframe
        g_quad.append(model[1]), r_quad.append(pow(model[1], -1)), bg_quad.append(
            Eq8_11(voltage, current)
        ), eg_quad.append(math.sqrt(cov[1][1]))
        # find the slope at zero and print wanted data
        print("condutance nS", model[1], "\n", "resistance", pow(model[1], -1))
        print("error in conductance: ", math.sqrt(cov[1][1]))

    if n == 1:
        linearRange = [90, 100, 110, 120, 130, 140, 150]
        if len(voltage) > 9:
            for x in linearRange:
                a = int(x)
                index = voltage.index(a)
                voltage.pop(index)
                current.pop(index)
        p, cov = np.polyfit(voltage, current, n, cov=True)
        model = np.poly1d(p)
        # adds post processed data to dataframe
        g_lin.append(model[1]), r_lin.append(pow(model[1], -1)), bg_lin.append(
            Eq8_11(voltage, current)
        ), eg_lin.append(math.sqrt(cov[0][0])), egb_lin.append(Eq8_17(voltage, current))
        # find the slope at zero and print wanted data
        print("condutance nS at ", model[1], "\n", "resistance", pow(model[1], -1))
        print("error in conductance: ", math.sqrt(cov[0][0]))  # is this correct?
        # need a linear regression
        print("From the book Condutance ns :", Eq8_11(voltage, current))
        print(
            "error in book conductance: ",
            Eq8_17(voltage, current),
        )

    model = np.poly1d(p)
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
    plt.title("resistance Data File: " + abf_num)

    # find the slope at zero and print wanted data

    plt.show()


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


def fileoperation(voltList, stepList, n, file):
    voltageList = copy.deepcopy(voltList)
    stepCurrent = copy.deepcopy(stepList)
    print("\n", "Data regression n = ", n, file)
    print(file, "n = ", n), n_reg(voltageList, stepCurrent, n, 2, file)

    remove = input("Enter values:  ")
    if remove != "no":
        delete = remove.split()
        for x in delete:
            a = int(x)
            index = voltageList.index(a)
            voltageList.pop(index)
            stepCurrent.pop(index)
    print("\n", "Post data regression n = ", n, file)
    n_reg(voltageList, stepCurrent, n, 2, file), print(
        file, "\n", "######################################", "\n"
    )


# iterate through all files within directory that IDE is currently within. Set path to be wherever dataset is for easy itteration and saving.
fileDir = os.listdir()
i = 0
while i < len(fileDir):
    file = fileDir[i]
    tempBool = False
    # Check whether file is in abf format or not
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
    if file.endswith(".abf"):
        abf_file_number = file.split(".")[0][-3:]
        # abf_file_list.append(abf_file_number)
        abf = pyabf.ABF(file)
        stepCurrent = averageI(abf.sweepY, 100)
        # larger scale (better for higher temps)

        print("@@@@@@@@@@@@@@@@@@", file, "@@@@@@@@@@@@@@@@@@\n")
        userinput = input(
            'rerun a file: "rerun" \ncontinue to current file: "cont"  \npress enter to quickly move through files  \ngo to specific index: "number"  \n'
        )
        if userinput == "rerun":
            if i > 0:
                i -= 1
            else:
                print("Already at the first file. Can't rerun previous file.")
            continue  # Skip the increment to rerun the previous file

        elif userinput == "cont":
            # makes the abf file numbers work for dataframe
            abf_file_list.append(abf_file_number)
            abf_file_list.append(abf_file_number)
            fileoperation(voltageList, stepCurrent, 1, file)
            fileoperation(voltageList, stepCurrent, 2, file)
        elif userinput.isnumeric():
            new_index = i + int(userinput)
            if 0 <= new_index < len(fileDir):
                i = new_index
            else:
                print("Index out of range. Continuing with the current file.")
            continue  # Skip the increment to jump to the specified index
    i += 1  # Move to the next file


# data frame which holds relevant information, then exports using glob to an excel file.
abf_data = {
    "ABF file number": abf_file_list,
    "Condutance Linear": g_lin,
    "Book Conductance Linear": bg_lin,
    "Resistance Linear": r_lin,
    "Error in Conductance Linear": eg_lin,
    "Condutance Quadratic": g_quad,
    "Book Conductance Quadratic": bg_quad,
    "Book Conductance Error Linear": egb_lin,
    "Resistance Quadratic": r_quad,
    "Error in Conductance Quadratic": eg_quad,
}

df1 = pd.DataFrame(
    abf_data,
    columns=[
        "ABF file number",
        "Condutance Linear",
        "Book Conductance Linear",
        "Resistance Linear",
        "Error in Conductance Linear",
        "Condutance Quadratic",
        "Book Conductance Quadratic",
        "Resistance Quadratic",
        "Error in Conductance Quadratic",
    ],
)

# uses current working directory
filesPath = os.getcwd()
with pd.ExcelWriter(rf"{filesPath}.xlsx", engine="xlsxwriter") as writer:
    df1.to_excel(writer, sheet_name="data", index=False)

print("done")


# plot the original data


"""
#plot the filtered data 
abf.setSweep(0)  # reload sweep with new filter
label = "sigma: %.02f" % (10)
plt.plot(abf.sweepX, abf.sweepY, alpha=.8, label=label) 
"""

# Create a graph of the pre and post filter data
