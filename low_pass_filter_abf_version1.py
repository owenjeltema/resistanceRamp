#low pass filture
def low_pass(sweepY, sweepX, cutoff, time_step):
    import numpy as np
    from scipy.signal import butter, lfilter
    from matplotlib import pyplot as plt
    def butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a
    def butter_lowpass_filter(data, cutoff, fs, order=5):
        b, a = butter_lowpass(cutoff, fs, order=order)
        filtered_sweepY = lfilter(b, a, data)
        return filtered_sweepY
    order = 1
    fs = (1/time_step)
    data = sweepY
    T = int(len(sweepX)*time_step)
    n = int(len(sweepX))
    b, a = butter_lowpass(cutoff, fs, order)
    filtered_sweepY = butter_lowpass_filter(data, cutoff, fs, order)
    return filtered_sweepY