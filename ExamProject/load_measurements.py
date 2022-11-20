import numpy as np
import pandas as pd
import os


def load_measurements(filename, fmode=None):
    abspath = os.path.dirname(os.path.abspath(__file__))
    path = abspath + "\\" + filename

    data = [row.split(",") for row in open(path, "r")]
    data = np.array(data,dtype=float)

    tvec = data[:,:6]
    data = data[:,6:]

    return tvec, data