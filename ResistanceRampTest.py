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
   #removes the values that are associted with NaN
   low = np.where(abf.sweepX == lower)[0][0]
   up = np.where(abf.sweepX == upper)[0][0]
   print("low",low,"high",up)
   list=list[low:up]
   return list

# zoom in on an interesting region and decorate the plot
def graph():
    plt.title("Gaussian Filtering of ABF Data")
    plt.ylabel(abf.sweepLabelY)
    plt.xlabel(abf.sweepLabelX)
    plt.axis([0, 150, -5, 10])
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
    polyline = np.linspace(1, 15000, 50)
    plt.scatter(time, current)
    plt.plot(polyline, model(polyline))
    plt.show()
    print(model)


#takes the last n seconds of the graph and takes the average of the current 
#returns a list of the averages at each step
#to-dp
def averageI(n):
    a =[]
    indexList=[990,1990,2990,3990,4990,5990,6990,7990,8990,9990,10990,11990,12990,13990,14990]
    '''
    timeList= [7.5,9.5] #all 15 steps
    #holdList = filter(8,9,abf.sweepY)
    for x in timeList:
        print(x)
        holdList = filter(x-n,x,abf.sweepY)
        print(mean(holdList))
        #a.append(mean(holdList))
    return a
'''
    for x in indexList:
        print(x)
        holdlist=abf.sweepY[x-200:x]
        print(mean(holdlist))
        a.append(mean(holdlist))
    return a 


#returns the index of a specific time


# Brings in the file
abf = pyabf.ABF("23626001.abf")
plt.figure(figsize=(8, 5))    #this might not need to be here 

#testing average 
test =[]
test= averageI(1.6)
print(test)
indexList=[990,1990,2990,3990,4990,5990,6990,7990,8990,9990,10990,11990,12990,13990,14990]
n_reg(indexList,test,2)

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



