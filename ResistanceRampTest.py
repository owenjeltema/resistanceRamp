import pyabf
import math
import matplotlib.pyplot as plt
import pyabf.filter
import numpy as np
from statistics import mean 


#TO-Do 
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


#quadric
# TO-Do select only the resistnace part of the graph
# create somethig to analysis model 
def n_reg(voltage,current,n):
    #polynomial fit with degree = 2
    #x,y, n
    model = np.poly1d(np.polyfit(voltage, current, n))

    #add fitted polynomial line to orignal data 
    fig=plt.figure()
    ax=fig.add_subplot(111, label="1")
    ax2=fig.add_subplot(111,label="2", frame_on=False)
    
    #original data
    ax.plot(abf.sweepX, abf.sweepY, alpha=0.3,label='original')
    ax.axis([10, 160,abf.sweepY[0]-2,abf.sweepY[15990]+2])
    ax.set_xlabel("x label 1", color="C0")
    ax.set_ylabel("y label 1", color="C0")
    ax.tick_params(axis='x', colors="C0")
    ax.tick_params(axis='y', colors="C0")

    #step averages 
    ax2.scatter(voltage, current, color="C2")
    ax2.xaxis.tick_top()
    ax2.yaxis.tick_right()
    ax2.set_xlabel('x label 2', color="C2")     
    ax2.xaxis.set_label_position('top') 
    ax2.yaxis.set_label_position('right') 
    ax2.tick_params(axis='x', colors="C2")
    ax2.tick_params(axis='y', colors="C2")

    plt.show()
    print(model)

 #find the r-squared 
    results={}
    yhat = model(voltage)
    ybar = np.sum(current)/len(current)
    ssreg = np.sum((yhat-ybar)**2)
    sstot = np.sum((current - ybar)**2)
    results['r_squared'] = ssreg / sstot
    print(results)

    #find the slope at zero 
    print("condutance nS",model[1],"resistacne",pow(model[1],-1))




#takes the last n seconds of the graph and takes the average of the current 
#returns a list of the averages at each step
#to-dp
def averageI():
    a =[]
    indexList=[990,1990,2990,3990,4990,5990,6990,7990,8990,9990,10990,11990,12990,13990,14990,15990]
    for x in indexList:
        print(x)
        holdlist=abf.sweepY[x-200:x]
        print(mean(holdlist))
        a.append(mean(holdlist))
    return a 





# Brings in the file
abf = pyabf.ABF("23626039.abf")
plt.figure(figsize=(8, 5))    #this might not need to be here 

#testing average 

stepCurrent= averageI()
print(stepCurrent)
voltageList=[0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
n_reg(voltageList,stepCurrent,2)


# plot the original data


'''
#plot the filtered data 
abf.setSweep(0)  # reload sweep with new filter
label = "sigma: %.02f" % (10)
plt.plot(abf.sweepX, abf.sweepY, alpha=.8, label=label) 
'''



#Create a graph of the pre and post filter data 




