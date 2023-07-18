#in the list of levels and means, something at the same level can be recorded as multiple events from before and after a no longer existant noise spike
#this combines the lengths and weighted means and removes the extra index and level values
def combine_repeates(bin_mean, bin_length, bin_index, level):
    new_mean=[]
    new_length=[]
    v=1
    while v < len(level):
        if level[v] == level[v-1]:
            new_mean= (bin_mean[v-1]*bin_length[v-1] + bin_mean[v]*bin_length[v])/ (bin_length[v-1] + bin_length[v])
            bin_mean.pop(v)
            bin_mean.pop(v-1)
            bin_mean.insert(v-1,new_mean)
            new_length= bin_length[v-1]+ bin_length[v]
            bin_length.pop(v)
            bin_length.pop(v-1)
            bin_length.insert(v-1, new_length)
            bin_index.pop(v)
            level.pop(v)
        if v == len(level) or level[v] != level[v-1]:
            v=v+1
    return [bin_mean, bin_length, bin_index, level]