import pyabf
import math
import matplotlib.pyplot as plt
import pyabf.filter
import numpy as np
from statistics import mean 


#TO-Do 
#split lowapss into 2 functions??
#fix n_reg
#fix y axis to fit the graph 
#figure out time better

#Filters the data and returns and list with the nan removed 
# a is the array that will be filtered 
def low_pass(a):
    #aplies the low pass
    sigma=10 # change this value to increase or decrease the level of filtering 
    pyabf.filter.gaussian(abf, 0)  # remove old filter
    pyabf.filter.gaussian(abf, sigma)  # apply custom sigma
    abf.setSweep(0)  # reload sweep with new filter
   
   #removes the values that are associted with NaN
    indices = np.logical_not(np.isnan(abf.sweepY))
    a = a[indices]
    return a

#Removes the data that is outside the lower and upper bound
# list is the list that needs to be filtered
def filter(lower, upper,list):
   #removesthe values that are associted with NaN
   low = np.where(abf.sweepX == lower)[0][0]
   up = np.where(abf.sweepX == upper)[0][0]
   list=list[low:up]
   return list

# zoom in on an interesting region and decorate the plot
def graph():
    plt.title("Gaussian Filtering of ABF Data")
    plt.ylabel(abf.sweepLabelY)
    plt.xlabel(abf.sweepLabelX)
    plt.axis([9.99, 20, -5, 10])
    plt.legend()
    plt.show()

#quadric
# TO-Do select only the resistnace part of the graph
# create somethig to analysis model 
def n_reg(time,current,n):
    #polynomial fit with degree = 2
    #x,y, n
    model = np.poly1d(np.polyfit(time, current, n))

    #add fitted polynomial line to scatterplot
    polyline = np.linspace(1, 60, 50)
    plt.scatter(time, current)
    plt.plot(polyline, model(polyline))
    plt.show()
    print(model)


#takes the last n seconds of the graph and takes the average of the current 
#returns a list of the averages at each step
#to-dp
def averageI(n):
    timeList= [9.5, 19.5] #all 15 steps
    a = []
    for x in timeList:
        holdList = filter(x-n,x,abf.sweepY)
        a.append(mean(holdList))
    return a


#returns the index of a specific time


# Brings in the file
abf = pyabf.ABF("23626001.abf")
plt.figure(figsize=(8, 5))    #this might not need to be here 

#testing average 
test=averageI(1.6)
print(test)

#quad_reg
#n_reg(abf.sweepX,abf.sweepY,2)

# plot the original data
abf.setSweep(0)
plt.plot(abf.sweepX, abf.sweepY, alpha=0.3, label="original")


#Filter the data 
current_lowpass = low_pass(abf.sweepY)
time_lowpass =low_pass(abf.sweepX)

#plot the filtered data 
abf.setSweep(0)  # reload sweep with new filter
label = "sigma: %.02f" % (10)
plt.plot(abf.sweepX, abf.sweepY, alpha=.8, label=label) 

#Create a graph of the pre and post filter data 
graph()



