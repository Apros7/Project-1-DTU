import numpy as np
import os
import matplotlib.pyplot as plt

# import platform
# platform.system

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
    if period == "minute":
        return tvec, data, period
    
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


def fix_tvec(tvec):
    start_tvec = tvec[0,:]
    new_tvec = []
    for row in tvec:
        year, month, day, hour, minute, _= row-start_tvec
        month = 12*year + month
        day = 31*month + day
        hour = 24*day + hour
        minute = 60*hour + minute
        new_tvec.append(minute)


def set_display(display_str, prefix, suffix, windows, back=True):
    if windows:
        os.system('cls')
    else: 
        os.system("clear")
    print(prefix,"\n")
    print(display_str)
    print("9. Back\n") if back else None
    print(suffix)


err_nodata = "Error: This action can not be done before data is loaded."
err_notint = "Error: Invalid input, try with an integer."
err_badrange = "Error: Number not in range, try another number"
err_badstat = "Error: Invalid statistic, try another."
err_nofile = "Error: File not found, try another filename"
err_badfile = "Error: Invalid file, try another file" 

back_val = 9

# This function is introduced to simplify the code related to our command-line interface.
def checkIfValidNumber(value, lowerBound, upperBound):
    # If the input can't be converted to an int, print error and return none.
    try: intValue = int(value)
    except: return None, err_notint

    if intValue == back_val:
        return back_val, ""

    # If the input isn't between lower and upper bound, print error and return none.
    if not (lowerBound <= intValue and intValue <= upperBound and intValue != 9):
        return None, err_badrange
    return intValue, ""


numerated_str = lambda list: "".join(f"{idx}. {item}\n" for idx, item in enumerate(list))

main_options = ["Load Data", "Aggregate Data", "Display Statistics", "Visualize", "Quit"]
main_string = numerated_str(main_options)

aggregate_options = [
    "Consumption per minute (no aggregation)",
    "Consumption per hour",
    "Consumption per day",
    "Consumption per month",
    "Hour-of-day consumption (hourly average)"
]
aggregate_dir = ["minute", "hour", "day", "month", "hour of the day"]
aggregate_string = numerated_str(aggregate_options)

visualize_options = ["All zones", "Zone 1", "Zone 2", "Zone 3", "Zone 4"]
visualize_string = numerated_str(visualize_options)

dir_options = os.listdir(os.path.dirname(__file__))
dir_string = numerated_str(dir_options)

fmode_options = [
    "Fill forward (replace corrupt measurement with latest valid measurement)",
    "Fill backward (replace corrupt measurement with next valid measurement)",
    "Delete corrupt measurements"]
fmode_dir = ["forward fill", "backward fill", "drop"]
fmode_string = numerated_str(fmode_options)

def main():
    tvec = None
    data = None
    prefix = ""
    suffix = ""
    period = "minute"

    print("Type anything and press enter if you are on a mac, else just press enter please :-)")
    windows_string = input()
    if windows_string == "": windows = True
    else: windows = False

    while True:

        # correct input
        intro_message = "hej"
        aggregated = False
        set_display(main_string, intro_message, suffix, windows)
        inp, suffix = checkIfValidNumber(input(),0,len(main_options))

        if inp == back_val:
            break
        if inp is None:
            continue

        inp = main_options[inp]
        
        if inp == "Load Data":
            while True:
                set_display(dir_string, prefix, suffix, windows)

                inp, suffix = checkIfValidNumber(input(), 0, len(dir_options))
                if inp == back_val:
                    break
                if inp is None:
                    continue
                out = dir_options[inp]

                try: load_measurements(out)
                except:
                    suffix = err_badfile
                    continue

                while True: #fmode loop
                    suffix = ""
                    set_display(fmode_string, prefix, suffix, windows)
                    fmode_inp, suffix = checkIfValidNumber(input(), 0, len(fmode_options))
                    if fmode_inp == back_val:
                        break
                    if fmode_inp is None:
                        continue
                    fmode = fmode_dir[fmode_inp]
                    break

                new_tvec, new_data = load_measurements(out, fmode)
                if new_data is None:
                    set_display(aggregate_string, prefix, suffix, windows)
                    continue
                else:
                    tvec, data = new_tvec, new_data
                    break
        
        elif inp == "Aggregate Data":
            while True:
                set_display(aggregate_string, prefix, suffix, windows)

                inp, suffix = checkIfValidNumber(input(), 0, len(aggregate_options))
                if inp == back_val:
                    break
                elif inp is None:
                    continue
                out = aggregate_dir[inp]

                tvec_a, data_a, period = aggregate_measurements(tvec, data, out)
                aggregated = True
                break

        elif inp == "Display Statistics":
            while True:
                if windows:
                    os.system("cls")
                else:
                    os.system("clear")
                print("Here is your statistic displayed in a table")
                print_statistics(tvec, data)

                print("9. Back\n", suffix)
                val, suffix = checkIfValidNumber(input(), 1, 0)
                if val == back_val:
                    break

        
        elif inp == "Visualize":
            if aggregated:
                temp_tvec = tvec_a
                print("You have not aggregated your data. Your data will be sorted by minute (no aggregation)")
            else: 
                temp_tvec = fix_tvec(tvec)
            prefix = "You have chosen to visualize your electricity consumption.\nPlease choose your next action:"
            set_display(visualize_string, prefix, suffix, windows)
            visualize_input = checkIfValidNumber(input(), 0, len(visualize_options))
            if visualize_input == back_val: break
            if visualize_input != 0: plot_statistics(temp_tvec, data_a, zone=visualize_input, time=period)
            else: plot_statistics(temp_tvec, data_a, time=period)
        
        elif inp == "Quit":
            return


if __name__ == "__main__":
    main()