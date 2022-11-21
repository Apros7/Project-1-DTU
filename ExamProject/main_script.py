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
        tvec_a = np.append(tvec_a, n)

        mask = tvec[:,col] == n
        data_a = np.append(data_a, np.sum(data[mask], axis=0))
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
def plot_statistics(tvec, data, zone="All", time="minute"):
    title = "all zones"
    if zone != "All":
        data = data[:, zone-1]
        title = f"zone {zone}"

    # Calculate size:
    size = 1
    for dim in np.shape(data): 
        size *= dim

    labels = ["Zone 1", "Zone 2", "Zone 3", "Zone 4"]
    colors = ["r", "g", "b", "y"]
    width = 0.2
    if title == "all zones":
        for i in range(4):
            if size < 25:
                plt.bar(tvec+width*(i-1.5), data[:,i], width=0.2)
            else:
                plt.plot(tvec, data[:,i], label=labels[i], color=colors[i])
    if size < 25:
        plt.bar(tvec, data)
    else:
        plt.plot(tvec, data, label=f"Zone {zone}", color="r")

    plt.title(f"Consumption for {title} per {time}s")
    plt.xlabel(f"Time ({time}s)")
    plt.ylabel("Energy (Wh)")
    plt.tight_layout()
    plt.xticks(tvec)
    if size >= 25:
        plt.grid()
    plt.legend()
    plt.show()


def main():
    tvec, data = load_measurements("2008.csv", "drop")
    tvec_a, data_a, period = aggregate_measurements(tvec, data, "day")
    print_statistics(tvec, data)
    plot_statistics(tvec_a, data_a, zone=1, time=period)


def set_display(display_str, prefix=None, suffix=None, back=True):
    os.system('cls')
    print(prefix,"\n") if prefix is not None else print("\n")
    print(display_str)
    print("←  Back\n") if back else None
    print(suffix,"\n") if suffix is not None else print("\n")


err_nodata = "Error: This action can not be done before data is loaded."
err_notint = "Error: Invalid input, try with an integer."
err_badrange = "Error: Number not in range, try another number"
err_badstat = "Error: Invalid statistic, try another."
err_nofile = "Error: File not found, try another filename"
err_badfile = "Error: Invalid file, try another file" 


# def try_options(inp: str, inp_options: list):
#     try: out = inp_options[int(inp)]
#     except ValueError: return err_notint, None, inp
#     except IndexError: return err_badrange, None, inp
#     else:              return None, out, inp

options = ["load data", "aggregate data", "display statistics", "visualize", "quit"]

def main2():
    data = None



    while True:
        # correct input
        inp = options[0]

        if inp == "load data"
            while True:
                data = None
                new_data = None
                if new_data is None and data is not None:
                    break
                else:
                    data = new_data
                    break
        elif inp == "aggregate data":
        elif inp == "display statistics":
        elif inp == "visualize":
        elif inp == "quit":
            return


if __name__ == "__main__":
    main2()