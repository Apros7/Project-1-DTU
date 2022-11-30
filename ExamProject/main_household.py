import numpy as np
import os
import matplotlib.pyplot as plt
import platform


# Loads measurements from csv files:
def load_measurements(filename: str, fmode: str):
    # Author:   Alexander Wittrup, s224196
    # Usage:    aggregate_measurements(), print_statistics()
    # Input:    filename and fmode (fill mode) strings.
    # Returns:  tvec, data, and error message if there is any (suffix).

    # Ensuring a correct path and converting the csv to a numpy array:
    abspath = os.path.dirname(os.path.abspath(__file__))
    path = abspath + "/" + filename
    data = [row.split(",") for row in open(path, "r")]
    data = np.array(data,dtype=float)

    # Mask that excludes all rows with corrupt measurements:
    mask_valid_rows = np.all(data != -1, axis=1)
    pct = np.count_nonzero(~mask_valid_rows) / len(mask_valid_rows)

    err_ffill = (
        "Error: Forward fill cannot be performed since the first row is corrupted,\n"
        f"{pct:.1%} of the data was corrupted and has been removed instead.")
    err_bfill = (
        "Error: Backward fill cannot be performed since the last row is corrupted,\n"
        f"{pct:.1%} of the data was corrupted and has been removed instead.")
    success = f"Data successfully loaded. {pct:.1%} of data was filled or excluded."
    prefix = ""
    suffix = ""

    if fmode == "drop":
        data = data[mask_valid_rows]
        if data.size <= 0 : data = np.zeros(10)[None, :]
        return data[:,:6], data[:,6:], prefix, suffix
    
    elif fmode == "forward fill":
        # Drops corrupt data if the first row is corrupt:
        if np.any(data[0] == -1):
            data = data[mask_valid_rows]
            suffix = err_ffill
        else:
            # Forward fills to previous valid measurement:
            for x, y in np.argwhere(data == -1):
                n=1
                while data[x-n, y] == -1: n+=1
                data[x, y] = data[x-n, y]
                prefix = success

    elif fmode == "backward fill":
        # Drops corrupt data if the last row is corrupt:
        if np.any(data[-1] == -1):
            data = data[mask_valid_rows]
            suffix = err_bfill
        else:
            # Backward fills to next valid measurement:
            for x, y in np.argwhere(data == -1):
                n=1
                while data[x+n, y] == -1: n+=1
                data[x, y] = data[x+n, y]
                prefix = success
    # If there is no data 
    if data.size <= 0 : data = np.zeros(10)[None, :]
    return data[:,:6], data[:,6:], prefix, suffix


# Aggregates measurements loaded via load_measurements():
def aggregate_measurements(tvec: np.ndarray, data: np.ndarray, period="minute"):
    # Author:   Alexander Wittrup, s224196
    # Usage:    visualize()
    # Input:    tvec and data (via. load_measurements()).
    # Returns:  tvec_a, data_a, and error message if there is any (suffix).

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


# Prints statistics from the loaded data
def print_statistics(_, data: np.ndarray):
    # Author: Lucas D. Vilsen, s224195
    # Usage:  main function
    # Input:  tvec and data, which is loaded from load_measurements
    # Return: None
    # Screen  output: Statistic table

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
    headers = ["Zone", "Minimum", "1. quart", "2. quart", "3. quart", "Maximum"]
    
    print(splitline)
    for header in headers:
        print(f"{header:<10}", end="")
    print("\n" + splitline)
    # We now print the statistic
    for x in range(5):
        for statistic in statistics[x]:
            print(f"{statistic:<10}", end="")
        print("\n", end="")
    print(splitline)


# Plots statistics from the loaded data
def plot_statistics(tvec: np.ndarray, data: np.ndarray, zone="All", time="minute"):
    # Author:        Lucas D. Vilsen, s224195
    # Usage:         main function
    # Input:         tvec and data (via. load_measurements()),
    #                desired zone (string or integer), and the time unit as a string
    # Return:        None
    # Screen output: Matplotlib plot

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


# String arrays for the set_display() function:
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

# Mini function to numerate and join a list of strings:
numerated_str = lambda list: "".join(f"{idx}. {item}\n" for idx, item in enumerate(list))
# Mini function to clear the terminal depending on the os:
def clear_terminal():
    if platform.system() == "Windows": os.system('cls')
    else: os.system("clear")

# Helper function responsible for the command-line interface:
def set_display(display_list, prefix, suffix, back=True):
    # Author: Alexander Wittrup, s224196
    # Usage:  main()
    # Screen output:
    #   top message        (prefix)  
    #   numerated options
    #   back option
    #   bottom message     (suffix, for errors)

    clear_terminal()
    print(prefix,"\n")
    print(numerated_str(display_list))
    print("9. Back\n") if back else None
    print(suffix)


err_notint = "Error: Invalid input, try with an integer."
err_badrange = "Error: Number is not among the options, try another number"
err_badfile = "Error: Invalid file, try another file"
err_nodata = "Error: No data to perform action on"
back_val = 9

# Helper function, Check if input string is in range
# returns the number if it's valid and an error message otherwise:
def is_valid_num(num:str, num_range:list):
    # Author: Lucas D. Vilsen, s224195
    # Usage: main()

    # Check if the input number is an integer value.
    try: num = int(num)
    except:
        return None, err_notint
    # Check if the input number is in range
    if (num == back_val) or (num in num_range):
        return num, ""
    else:
        return None, err_badrange


def main():
    # Authors:  Alexander Wittrup, s224196
    #           Lucas D. Vilsen, s224195

    # Variable start values:
    tvec = None
    data = None
    intro_string = (
    "Hello world! This is our program for Analysis of Household Electricity Consumption.\n"
    "Press the number corresponding to the action you want to take:")
    prefix = ""
    suffix = ""
    period = "minute"
    display_intro = True

    while True:
        if display_intro:
            prefix = intro_string
            display_intro = False
        else: prefix = ""
        set_display(main_options, prefix, suffix, back=False)

        inp, suffix = is_valid_num(input(), range(len(main_options)))
        if inp == back_val:
            break
        elif inp is None:
            continue
        elif (inp in [1,2,3]) and tvec is None:
            suffix = err_nodata
            continue
        else:
            inp = main_options[inp]
        
        if inp == "Load Data":
            while True:
                prefix = "Choose your datafile (.csv or .txt):"
                set_display(dir_options, prefix, suffix)

                inp, suffix = is_valid_num(input(), range(len(dir_options)))
                if inp == back_val:
                    break
                elif inp is None:
                    continue
                else:
                    try: load_measurements(dir_options[inp], "")
                    except:
                        suffix = err_badfile
                        continue
                
                back = False
                while True:  # Get fmode
                    prefix = "Choose your desired fill mode:"
                    set_display(fmode_options, prefix, "")

                    fmode_inp, suffix = is_valid_num(input(), range(len(fmode_options)))
                    if fmode_inp == back_val:
                        back = True
                        break
                    elif fmode_inp is None:
                        continue
                    else:
                        tvec, data, prefix, suffix = load_measurements(dir_options[inp], fmode_dir[fmode_inp])
                        tvec_a, data_a = None, None
                        break
                if back:
                    continue
                break
        
        elif inp == "Aggregate Data":
            while True:
                set_display(aggregate_options, prefix, suffix)

                inp, suffix = is_valid_num(input(), range(len(aggregate_options)))
                if inp == back_val:
                    break
                elif inp is None:
                    continue
                else:
                    tvec_a, data_a = aggregate_measurements(tvec, data, aggregate_dir[inp])
                    break

        elif inp == "Display Statistics":
            while True:
                # We print the statistic
                clear_terminal()
                print("Here is your statistic displayed in a table")
                print_statistics(tvec, data)
                print("9. Back")
                print(suffix)

                inp, suffix = is_valid_num(input(), range(0))
                # and return to the main menu if 9 is pressed
                if inp == back_val:
                    break
                elif inp is None:
                    continue

        
        elif inp == "Visualize":
            prefix = (
                "You have chosen to visualize your electricity consumption.\n"
                "Please choose your next action:")

            # If data hasn't been aggregated, 
            if tvec_a is None:
                prefix = "The data will be sorted consumption per minute (no aggregation)\n" + prefix
                tvec_a, data_a = aggregate_measurements(tvec, data, "minute")
            
            # We get the zone the user wants to plot
            set_display(visualize_options, prefix, suffix)
            visualize_input, suffix = is_valid_num(input(), range(len(visualize_options)))
            print("To continue, please close the matplotlib window")
            if (visualize_input == back_val) or (visualize_input is None):
                continue
            elif visualize_input > 0:
                plot_statistics(tvec_a, data_a, zone=visualize_input, time=period)
            else:
                plot_statistics(tvec_a, data_a, zone="All", time=period)
        
        elif inp == "Quit":
            return


if __name__ == "__main__":
    clear_terminal()
    tvec, data, _, _ = load_measurements("testdata2.csv", "forward fill")
    print(tvec, data)
    tvec_a, data_a = aggregate_measurements(tvec, data, "minute")
    print(tvec_a, data_a)
    plot_statistics(tvec_a, data_a)

    # main()