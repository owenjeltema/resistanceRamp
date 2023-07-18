from statistics import mean, stdev
#determinds if two values are in the same bin as each other
#if they are, it returns true
def same_bin(first_value, second_value, bins_list):
    w=1
    while w <= len(bins_list):
        if (first_value < bins_list[0]) and (second_value < bins_list[0]):
            return True
        if w < len(bins_list) and ((first_value > bins_list[w-1]) and (first_value <= bins_list[w])) and ((second_value > bins_list[w-1]) and (second_value <= bins_list[w])):
            return True
        if ((first_value >= bins_list[w-1]) and (second_value >= bins_list[w-1])) and (w == len(bins_list)):
            return True
        w=w+1

    