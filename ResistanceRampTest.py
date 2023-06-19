import pyabf
import math
import matplotlib.pyplot as plt
import pyabf.filter
import numpy as np 

# TO_DO
## even files are for resistance right now or everyother to a certain point 
## y shows slop n change graph or more issues 
# after slope y to move on n to change things 
# find slope 
# what type of regression do we want 


#this creates a graph of the file 

import pyabf

import matplotlib.pyplot as plt

#Brings in the file 
abf = pyabf.ABF("23616002.abf")
plt.figure(figsize=(8, 5))

# plot the original data
abf.setSweep(0)
plt.plot(abf.sweepX, abf.sweepY, alpha=.3, label="original")


#Filters the data and returns and list with the nan removed 
def filter(a):

    sigma=10 # change this value to increase or decrease the level of filtering 
    pyabf.filter.gaussian(abf, 0)  # remove old filter
    pyabf.filter.gaussian(abf, sigma)  # apply custom sigma
    abf.setSweep(0)  # reload sweep with new filter
    label = "sigma: %.02f" % (sigma)
    plt.plot(abf.sweepX, abf.sweepY, alpha=.8, label=label) #this will need to change later 
    newList=list()
    newList= [x for x in abf.sweepY if not math.isnan(x)]
    return newList



print(abf.sweepY)
print("len Y:", len(abf.sweepY)) # prints all of the current data 
print("len X ", len(abf.sweepX)) #prints all of the time


    





# zoom in on an interesting region and decorate the plot
plt.title("Gaussian Filtering of ABF Data")
plt.ylabel(abf.sweepLabelY)
plt.xlabel(abf.sweepLabelX)
plt.axis([20.05, 50.05, -5, 10])
plt.legend()
plt.show()





