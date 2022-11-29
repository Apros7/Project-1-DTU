import numpy as np
import os
import matplotlib.pyplot as plt
import platform


def load_measurements(filename: str, fmode=None):
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

    # Assuming the data is already sorted:
    tvec = data[:,:6]
    data = data[:,6:]
    return tvec, data


def aggregate_measurements(tvec: np.ndarray, data: np.ndarray, period="minute"):
    if period == "minute":
        init_val = tvec[0,:]
        relative_tvec = tvec - init_val
        # Converts the columns of relative_tvec to minutes and adds them:
        time_to_min_const = np.array([525948.766, 43829.0639, 1440, 60, 1, 1])
        min_tvec = np.sum(relative_tvec * time_to_min_const, axis=1, dtype=int)
        return min_tvec, data

    elif period == "hour of the day":  #AKA: hotd
        tvec_a = np.arange(24)
        hotd_data = []
        for hour in tvec_a:
            # Mask that only accepts elements that correspond to the currently iterated hour.
            mask = tvec[:,3] == hour
            is_not_empty = data[mask].size > 0
            # Takes mean of data only if list isn't empty to avoid RuntimeWarning.
            if is_not_empty: hotd_data.append(np.mean(data[mask], axis=0))
            else: hotd_data.append(np.zeros(4))
        return tvec_a, np.asarray(hotd_data)

    elif period == "hour": col = 3
    elif period == "day": col = 2
    elif period == "month": col = 1

    # Collects all the unique elements from the relevant time column.
    tvec_a = np.unique(tvec[:,col])
    # Does basically the same as hotd but takes sum instead of average.
    data_a = np.array([np.sum(data[tvec[:,col] == n], axis=0) for n in tvec_a])
    return tvec_a, data_a


def print_statistics(_, data):
    statistics = []
    # We append the statistics for every zone
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
    # And then for all data
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
    # We now print the statistic
    for x in range(5):
        for statistic in statistics[x]:
            print(f"{statistic:<10}", end="")
        print("\n", end="")
    print(splitline)


def plot_statistics(tvec, data, zone="All", time="minute"):
    title = "all zones"
    # We choose the appropriate data
    if zone != "All":
        data = data[:, zone-1]
        title = f"zone {zone}"

    # Calculate size:
    size = 1
    for dim in np.shape(data): 
        size *= dim

    # We make the plot a bit transparent if we plot by minutes
    if time == "minute":
        alpha = 0.4
    else: 
        alpha = 1

    labels = ["Zone 1", "Zone 2", "Zone 3", "Zone 4"]
    colors = ["tab:red", "tab:green", "tab:blue", "tab:orange"]
    width = 0.2
    if title == "all zones":
        # We loop over each zone
        for i in range(4):
            if size < 25:
                plt.bar(tvec+width*(i-1.5), data[:,i], width=0.2)
            else:
                plt.plot(tvec, data[:,i], label=labels[i], color=colors[i], alpha=alpha)
    # or just plot the zone we want to look at
    else: 
        if size < 25:
            plt.bar(tvec, data)
        else:
            plt.plot(tvec, data, label=f"Zone {zone}", color="r",alpha=alpha)

    # we make the layout
    plt.title(f"Consumption for {title} per {time}s")
    plt.xlabel(f"Time ({time}s)")
    plt.ylabel("Energy (Wh)")
    plt.tight_layout()
    if time != "minute":
        # we do not include xticks if we look at minutes
        # as there would be way to many x labels on the plot
        plt.xticks(tvec)
    if size >= 25:
        plt.grid()
    plt.legend()
    plt.show()


def clear():  # Clears all text from the console:
    if platform.system() == "Windows": os.system('cls')
    else: os.system("clear")


numerated_str = lambda list: "".join(f"{idx}. {item}\n" for idx, item in enumerate(list))
def set_display(display_list, prefix, suffix, back=True):
    clear()
    print(prefix,"\n")
    print(numerated_str(display_list))
    print("9. Back\n") if back else None
    print(suffix)


err_notint = "Error: Invalid input, try with an integer."
err_badrange = "Error: Number is not among the options, try another number"
err_badfile = "Error: Invalid file, try another file" 
back_val = 9

# Helper function, Check if input string is in range
# returns the number if valid and an error message otherwise:
def is_valid_num(num:str, num_range:list):
    # Check if the input number is an integer value.
    try: num = int(num)
    except:
        return None, err_notint
    # Check if the input number is in range
    if (num == back_val) or (num in num_range):
        return num, ""
    else:
        return None, err_badrange


main_options = ["Load Data", "Aggregate Data", "Display Statistics", "Visualize", "Quit"]

aggregate_options = [
    "Consumption per minute (no aggregation)",
    "Consumption per hour",
    "Consumption per day",
    "Consumption per month",
    "Hour-of-day consumption (hourly average)"
]
aggregate_dir = ["minute", "hour", "day", "month", "hour of the day"]

visualize_options = ["All zones", "Zone 1", "Zone 2", "Zone 3", "Zone 4"]

dir_options = os.listdir(os.path.dirname(__file__))

fmode_options = [
    "Fill forward (replace corrupt measurement with latest valid measurement)",
    "Fill backward (replace corrupt measurement with next valid measurement)",
    "Delete corrupt measurements"]
fmode_dir = ["forward fill", "backward fill", "drop"]


def main():
    tvec = None
    data = None
    prefix = (
        "Hello world! This is our program for Analysis of Household Electricity Consumption.\n"
        "Press the number corresponding to the action you want to take:")
    suffix = ""
    period = "minute"
    aggregated = False

    while True:
        set_display(main_options, prefix, suffix, back=False)
        inp, suffix = is_valid_num(input(), range(len(main_options)))
        if inp == back_val:
            break
        if inp is None:
            continue

        inp = main_options[inp]
        
        if inp == "Load Data":
            while True:
                set_display(dir_options, prefix, suffix)

                inp, suffix = is_valid_num(input(), range(len(dir_options)))
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
                    set_display(fmode_options, prefix, suffix)
                    fmode_inp, suffix = is_valid_num(input(), range(len(fmode_options)))
                    if fmode_inp == back_val:
                        break
                    if fmode_inp is None:
                        continue
                    fmode = fmode_dir[fmode_inp]
                    break

                new_tvec, new_data = load_measurements(out, fmode)
                if new_data is None:
                    set_display(aggregate_options, prefix, suffix)
                    continue
                else:
                    tvec, data = new_tvec, new_data
                    break
        
        elif inp == "Aggregate Data":
            while True:
                set_display(aggregate_options, prefix, suffix)

                inp, suffix = is_valid_num(input(), range(len(aggregate_options)))
                if inp == back_val:
                    break
                elif inp is None:
                    continue
                out = aggregate_dir[inp]

                tvec_a, data_a = aggregate_measurements(tvec, data, out)
                aggregated = True
                break

        elif inp == "Display Statistics":
            while True:
                clear()
                print("Here is your statistic displayed in a table")
                print_statistics(tvec, data)
                print("9. Back")
                print(suffix)

                inp, suffix = is_valid_num(input(), range(0))

                if inp == back_val:
                    break
                elif inp is None:
                    continue

        
        elif inp == "Visualize":
            if aggregated:
                temp_tvec = tvec_a
            else: 
                temp_tvec, data_a = aggregate_measurements(tvec, data, period)
            prefix = "You have not aggregated your data. Your data will be sorted by minute (no aggregation)\nYou have chosen to visualize your electricity consumption.\nPlease choose your next action:"
            set_display(visualize_options, prefix, suffix)
            visualize_input, suffix = is_valid_num(input(), range(len(visualize_options)))

            if (visualize_input == back_val) or (visualize_input is None):
                continue
            elif visualize_input > 0:
                plot_statistics(temp_tvec, data_a, zone=visualize_input, time=period)
            else:
                plot_statistics(temp_tvec, data_a, zone="All", time=period)
        
        elif inp == "Quit":
            return


if __name__ == "__main__":
    main()