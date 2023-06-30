import pyabf
import math
import matplotlib.pyplot as plt
import pyabf.filter
import numpy as np
from statistics import mean 
import pandas as pd 
#need to instal
#pip install xlrd
#also abf 


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




#quadric
#takes the average data of the voltage steps, plots it against the original and returns the conductance and resistanace 
#voltage is a the voltage step list
#current is the list of current values
#n is the degree of polynomial and range is the scale of the y axis 
def n_reg(voltage,current,n,range):
    #polynomial fit with degree = 2
    #x,y, n
    model = np.poly1d(np.polyfit(voltage, current, n))

    #add fitted polynomial line to orignal data 
    fig=plt.figure()
    ax=fig.add_subplot(111, label="1")
    #ax2=fig.add_subplot(111,label="2", frame_on=False)
    
    #fig, (ax, ax2) = plt.subplots(2, sharey=True)

    #original data
    ax.plot(abf.sweepX, abf.sweepY, alpha=0.3,label='original')
    ax.axis([0, 165,abf.sweepY[0]-range,abf.sweepY[15990]+range])
    ax.set_xlabel("time seconds", color="C0")
    ax.set_ylabel("current pA", color="C0")
    ax.tick_params(axis='x', colors="C0")
    ax.tick_params(axis='y', colors="C0")

    #step averages 
    ax2 =ax.twiny()
    ax2.scatter(voltage, current, color="C2")
    ax2.axis([-10,155,abf.sweepY[0]-range,abf.sweepY[15990]+range])
    ax2.xaxis.tick_top()
    ax2.set_xlabel('voltage mV', color="C2")     
    ax2.xaxis.set_label_position('top') 
    ax2.tick_params(axis='x', colors="C2")
    polyline = np.linspace(1, 150, 50)
    plt.plot(polyline, model(polyline))

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
    print("condutance nS",model[1],"resistance",pow(model[1],-1))




#takes the last n seconds of the graph and takes the average of the current 
#returns a list of the averages at each step
#amount is the amount of time that is used to get data from
#to-dp
def averageI(list,amount):
    a =[]
    indexList=[990,1990,2990,3990,4990,5990,6990,7990,8990,9990,10990,11990,12990,13990,14990,15990]
    for x in indexList:
        print(x)
        holdlist=list[x-amount:x]
        print(mean(holdlist))
        a.append(mean(holdlist))
    return a 

def filtered_average(list,range):
    time=[9.9,19.9]
          #,29.9,39.9,49.9,59.9,69.9,79.9,89.9,99.9,109.9,119.9,129.9,139.9,149.9]
    stepCurrent=[]
    for x in time:
        hold=filter(x-range,x,list)
        stepCurrent.append(mean(hold))
        print(mean(hold))
    return stepCurrent

#fuction to read in the resitsance files into an array
#for loop to flip through the differnt files and analysis the data
# maybe instert temp into an array too 
#read in excel
def excel(book):
    files=pd.read_excel(book, usecols='M')
    #filter out the unessary stuff 



# Brings in the file
abf = pyabf.ABF("23626039.abf")
plt.figure(figsize=(8, 5))    #this might not need to be here 

#testing average 

stepCurrent= averageI(abf.sweepY,100)
print(stepCurrent)
voltageList=[0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
#bigger scale (better for higher temps)
n_reg(voltageList,stepCurrent,1,2)

#code to fix scale                                                              to-do

print('enter voltages that should be removed, n = no data')
remove = input("Enter values:")
if(remove!='n'):
    delete=remove.split()
    for x in delete:
        a=int(x)
        index=voltageList.index(a)
        voltageList.pop(index)
        stepCurrent.pop(index)
#print(stepCurrent)
n_reg(voltageList,stepCurrent,1,1)

#plot filtered data
#filteredCurrent=low_pass(abf.sweepY)
#filteredTime=low_pass(abf.sweepX)
#filteredStepCurrent=filtered_average(filteredCurrent,2)
#n_reg(voltageList,filteredStepCurrent,2,2)


# plot the original data


'''
#plot the filtered data 
abf.setSweep(0)  # reload sweep with new filter
label = "sigma: %.02f" % (10)
plt.plot(abf.sweepX, abf.sweepY, alpha=.8, label=label) 
'''



#Create a graph of the pre and post filter data 




