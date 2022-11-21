import numpy as np
import os
import matplotlib.pyplot as plt


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
    return tvec_a, data_a, period


def print_statistics(_, data):
    statistics = []
    for i in range(4):
        current_row = data[:,i]
        zone = i+1
        statistics.append([
            zone,
            np.min(current_row),
            np.quantile(current_row, 0.25),
            np.quantile(current_row, 0.50),
            np.quantile(current_row, 0.75),
            np.max(current_row)
        ])
    statistics.append([
        "All",
        np.min(data),
        np.quantile(data, 0.25),
        np.quantile(data, 0.50),
        np.quantile(data, 0.75),
        np.max(data)
    ])
    # printing the statistics:
    splitline = "-"*60
    print(splitline)
    headers = ["Zone", "Minimum", "1. quart", "2. quart", "3. quart", "Maximum"]
    for header in headers:
        print(f"{header:<10}", end="")
    print("\n" + splitline)
    for x in range(5):
        for statistic in statistics[x]:
            print(f"{statistic:<10}", end="")
        print("\n", end="")
    print(splitline)


# Tvec skal kun indeholde relevante tidsdata
def plot_statistics(tvec, data, zone="All", time="minutes"):
    title = "all zones"
    if zone != "All":
        data = data[:, zone-1]
        title = f"zone {zone}"

    # Calculate size:
    size = 1
    for dim in np.shape(data): 
        size *= dim

    number_of_zones = 1
    if title == "all zones":
        number_of_zones = 4
    for i in range(number_of_zones):
        if size < 25:
            plt.bar(tvec, data)
        else:
            plt.plot(data)
    plt.title(f"Consumption for {title} per {time}")
    plt.xlabel(f"Time ({time})")
    plt.ylabel("Energy (kWh)")
    plt.show()


def main():
    tvec, data = load_measurements("2008.csv", "drop")
    tvec_a, data_a, period = aggregate_measurements(tvec, data, "day")
    print_statistics(tvec, data)
    plot_statistics(tvec_a, data_a, time=period)


if __name__ == "__main__":
    main()