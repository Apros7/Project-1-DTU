import numpy as np

def aggregate_measurements(tvec, data, period):
    if period == "hour":
        col = 3
    if period == "day":
        col = 2
    if period == "month":
        col = 1
    if period == "hour of the day":
        col = 3
    
    nums = np.unique(tvec[:,col])
    data_a = np.array([])
    tvec_a = np.array([])
    for n in nums:
        list1 = [0]*6
        list1[col] = n
        tvec_a = np.append(tvec_a, list1)

        mask = tvec[:,col] == n
        data_a = np.append(data_a, np.sum(data[mask], axis=0))
    tvec_a = np.reshape(tvec_a, (-1,6))
    data_a = np.reshape(data_a, (-1,4))
    return tvec_a, data_a