#Dylan & Sebastian
import pyabf
import math
import matplotlib.pyplot as plt
import pyabf.filter
import numpy as np
from statistics import mean
import os
import math
import copy

CSVdataList = [] #holds all data for use in excel -> [File number, Slope R Gohm, Conductance ns, conductance book, conductance error calc]
tempCSVdataList = [] #temporary version of CSVdataList

# include that other formula

# need to instal
# pip install xlrd
# also abf


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

#delta
def Eq8_12(x_array):
    length=len(x_array)
    x_array_np=np.array(x_array)
    return length* sum(np.square(x_array_np))-pow((sum(x_array)),2)

#this calcutates A(Y-intercept)
def Eq8_10(x_array, y_array):
    x_array_np=np.array(x_array)
    return (sum(np.square(x_array_np))*sum(y_array) - sum(x_array)*np.dot(x_array,y_array))/Eq8_12(x_array)

#this calculates B(slope)
def Eq8_11(x_array, y_array):
    length=len(x_array)
    return ((length*np.dot(x_array,y_array))-sum(x_array)*sum(y_array))/Eq8_12(x_array)

#this returns the uncertainity of Y
def Eq8_15(x_array, y_array):
    length=len(x_array)
    A = Eq8_10(x_array,y_array)
    B = Eq8_11(x_array,y_array)
    sum=0
    for i in range(length):
        sum+=pow(y_array[i]-A-B*x_array[i],2)


    return math.sqrt((1/(length-2))*sum)

#this returns the uncertainity of the slope
def Eq8_17(x_array,y_array):    
   return Eq8_15(x_array,y_array)*math.sqrt(len(x_array)/Eq8_12(x_array))



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
        # find the slope at zero and print wanted data
        temp = ['3 nums',pow(model[1], -1),model[1],Eq8_11(voltage,current),math.sqrt(cov[1][1])]
        tempCSVdataList.append(temp) #change first to file num
        print("condutance nS", temp[2], "\n", "resistance", temp[1])
        print("error in conductance: ", temp[4])

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
        # find the slope at zero and print wanted data
        temp = ['3 nums',pow(model[1], -1),model[1],Eq8_11(voltage,current),math.sqrt(cov[0][0])]
        tempCSVdataList.append(temp) #change first to file num
        print("condutance nS at ", temp[2], "\n", "resistance", temp[1])
        print("error in conductance: ", temp[4])  # is this correct?
        # need a linear regression
        print("From the book Condutance ns :", temp[3])
        print(
            "error in conductance: ", Eq8_17(voltage,current),
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
for file in fileDir:
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
        # call read abf file
        abf = pyabf.ABF(file)
        stepCurrent = averageI(abf.sweepY, 100)
        # larger scale (better for higher temps)
        fileNumber = file[:-4]
        fileNumber = fileNumber[::-1]
        temp = len(fileNumber) - 3
        fileNumber = fileNumber[:-temp]
        fileNumber = fileNumber[::-1]
        print(fileNumber)

        print("@@@@@@@@@@@@@@@@@@", file, "@@@@@@@@@@@@@@@@@@\n")
        userinput = input(
            'rerun a file: "rerun" \ncontinue to current file: "cont"  \npress enter to quickly move through files  \ngo to specific index: "number"  \n'
        )
        tempBool = False
        if userinput == "rerun":
            fileoperation(voltageList, stepCurrent, 1, fileDir[fileDir.index(file) - 1])
            fileoperation(voltageList, stepCurrent, 2, fileDir[fileDir.index(file) - 1])
            tempBool = True

        elif userinput == "cont":
            fileoperation(voltageList, stepCurrent, 1, file)
            fileoperation(voltageList, stepCurrent, 2, file)
            tempBool = True
        elif userinput.isnumeric() == True:
            tempBool = True
            fileoperation(
                voltageList,
                stepCurrent,
                1,
                fileDir[fileDir.index(file) + int(userinput)],
            )
            fileoperation(
                voltageList,
                stepCurrent,
                2,
                fileDir[fileDir.index(file) + int(userinput)],
            )
        if tempBool:
            userinput = input('Select data to use:\nUse first figure: "1"\nUse second figure: "2"\nUse neither figure: "pass"')
            if userinput == "1":
                CSVdataList.append(tempCSVdataList[1])
                CSVdataList[len(CSVdataList)-1][0] = fileNumber
            elif userinput == "2":
                CSVdataList.append(tempCSVdataList[3])
                CSVdataList[len(CSVdataList)-1][0] = fileNumber
            elif userinput == "pass":
                pass
            tempCSVdataList = []

dataAsCSV = ''
for i in CSVdataList: #gives all data selected in a CSV-style file which can be opened in excel
    dataAsCSV = dataAsCSV + i[0] + ', ' + '"' + str(i[1]) + '"' + ', ' + '"' + str(i[2]) + '"' + ', ' + '"' + str(i[3]) + '"' + ', ' + '"' + str(i[4]) + '"' + ';'
dataAsCSV = dataAsCSV[:-1]
print('')
print(dataAsCSV)
print('')
print('In excel use "=TEXTSPLIT(##$$,",",";")" to seperate data, with ##$$ being where data string is located (e.g. A1).')
print('')


# plot the original data


"""
#plot the filtered data 
abf.setSweep(0)  # reload sweep with new filter
label = "sigma: %.02f" % (10)
plt.plot(abf.sweepX, abf.sweepY, alpha=.8, label=label) 
"""


# Create a graph of the pre and post filter data