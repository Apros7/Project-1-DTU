import numpy as np
import os


def load_measurements(filename, fmode=None):
    abspath = os.path.dirname(os.path.abspath(__file__))
    path = abspath + "/" + filename

    data = [row.split(",") for row in open(path, "r")]
    data = np.array(data,dtype=float)

    if fmode == "drop":
        # remove all rows that contain a corrupted measurement:
        data = data[np.all(data != -1, axis=1)]

    if fmode == "forward fill" and np.all(data[0] != -1): num = -1
    elif fmode == "backward fill" and np.all(data[-1] != -1): num = 1
    elif fmode != "drop":
        data = data[np.all(data != -1, axis=1)]
        print("errmsg")

    for x, y in np.argwhere(data == -1):
        data[x][y] = data[x + num][y]

    tvec = data[:,:6]
    data = data[:,6:]
    return tvec, data