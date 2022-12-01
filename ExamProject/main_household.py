import matplotlib.pyplot as plt
import numpy as np
import platform
import os


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


# Loads measurements from csv files:
def load_measurements(filename: str, fmode="drop"):
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
    success = f"Data successfully loaded.\n{pct:.1%} of data was corrupted and has been filled or excluded."
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

    if (period == "minute") or (period not in aggregate_dir):
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
def print_statistics(_, data: np.ndarray) -> None:
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
            stat = statistic
            # crude method of rounding:
            if statistic not in [1,2,3,4,"All"]:
                stat = f"{statistic:.1f}"
            print(f"{stat:<10}", end="")
        print("\n", end="")
    print(splitline)


# Plots statistics from the loaded data
def plot_statistics(tvec: np.ndarray, data: np.ndarray, zone=0, time_unit="minute"):
    # Author:         Lucas D. Vilsen, s224195
    # Usage:          main function
    # Input:          tvec and data (via. load_measurements()),
    #                 desired zone (string or integer), and the time unit as a string
    # Return:         None
    # Screen output:  Matplotlib plot

    # We choose the zone appropriate data
    if zone == 0:
        title = "all zones"
    else:
        title = f"zone {zone}"
        data = data[:, zone-1]

    # Condtition for bar plot:
    cond_bar_plot = np.size(data) < 25

    # We make the plot a bit transparent if we plot by minutes etc.
    if time_unit == "minute":
        alpha = 0.4
    else:
        alpha = 1

    labels = ["Zone 1", "Zone 2", "Zone 3", "Zone 4"]
    colors = ["tab:red", "tab:green", "tab:blue", "tab:orange"]
    width = 0.15

    # If the values get too high, change unit:
    if np.max(data) > 50000:
        data /= 1000
        unit = "k"
    else:
        unit = ""

    if zone == 0:
        # We loop over each zone
        for i in range(4):
            if cond_bar_plot:
                new_tvec = np.arange(len(tvec))
                plt.bar(new_tvec + width*(i-1.5), data[:,i], width=width)
            else:
                plt.plot(tvec, data[:,i], label=labels[i], color=colors[i], alpha=alpha)
    # or just plot the zone we want to look at
    else: 
        if cond_bar_plot:
            new_tvec = np.arange(len(tvec))
            plt.bar(new_tvec, data)
        else:
            plt.plot(tvec, data, label=f"Zone {zone}", color="r",alpha=alpha)

    # we make the layout
    plt.title(f"Consumption for {title} per {time_unit}")
    plt.xlabel(f"Time ({time_unit}s)")
    plt.ylabel(f"Energy ({unit}Wh)")
    plt.tight_layout()

    if time_unit == "hour of the day": # Unique case:
        plt.title(f"Average consumption for {title} per hour")
        plt.xlabel(f"Time (hours)")
        plt.ylabel(f"Energy (Wh)")
    
    # Makes x-axis more readable:
    if (time_unit in ["hour", "day", "hour of the day"]) and (not cond_bar_plot):
        plt.xticks(rotation = 45)
    
    if cond_bar_plot:
        plt.xticks(range(len(tvec)), [str(int(n)) for n in tvec])
    elif period != "minute":
        plt.xticks(tvec)

    if not cond_bar_plot:
        plt.grid()
        plt.legend(labels)
    plt.show()


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
    print("99. Back\n") if back else None
    print(suffix)


err_notint = "Error: Invalid input, try with an integer."
err_badrange = "Error: Number is not among the options, try another number"
err_badfile = "Error: Invalid file, try another file"
err_nodata = "Error: No data to perform action on"
back_val = 99

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


# The command-line UI
def main():
    # Authors:  Alexander Wittrup, s224196
    #           Lucas D. Vilsen, s224195

    # Variable initial values:
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
        # Display intro message at first:
        if display_intro or tvec is None:
            prefix = intro_string
            display_intro = False

        # Display all actions and ask for input:
        set_display(main_options, prefix, suffix, back=False)

        inp, suffix = is_valid_num(input(), range(len(main_options)))
        if (inp is None) or (inp == back_val):
            if suffix == "": suffix = err_badrange
            continue
        # Check if data has been loaded before taking other actions:
        elif (inp in [1,2,3]) and tvec is None:
            suffix = err_nodata
            continue
        else:
            inp = main_options[inp]
        
        if inp == "Load Data":
            while True:
                # Display the file options and ask for input:
                prefix = "Choose your datafile (.csv or .txt):"
                set_display(dir_options, prefix, suffix)
                prefix = ""

                inp, suffix = is_valid_num(input(), range(len(dir_options)))
                if inp == back_val:
                    break
                elif inp is None:
                    continue
                else:
                    # Test if file can be loaded, return error if not:
                    clear_terminal()
                    print("Loading ...")
                    try: load_measurements(dir_options[inp], "")
                    except:
                        suffix = err_badfile
                        continue
                
                back = False
                suffix = ""
                while True: # fmode loop
                    # Display fmodes and ask for input:
                    prefix = "Choose your desired fill mode:"
                    set_display(fmode_options, prefix, suffix)
                    prefix = ""

                    fmode_inp, suffix = is_valid_num(input(), range(len(fmode_options)))
                    if fmode_inp == back_val:
                        back = True
                        break
                    elif fmode_inp is None:
                        continue
                    else:
                        clear_terminal()
                        print("Loading ...")
                        tvec, data, prefix, suffix = load_measurements(dir_options[inp], fmode_dir[fmode_inp])
                        # If new data is loaded, reset aggregated data:
                        tvec_a, data_a = None, None
                        break
                if back:  # to differentiate "back" being pressed and the loop finishing
                    continue
                break
        
        elif inp == "Aggregate Data":
            while True:
                # Display the options and ask for input:
                prefix = "Choose the method of aggregation:"
                set_display(aggregate_options, prefix, suffix)
                prefix = ""

                inp, suffix = is_valid_num(input(), range(len(aggregate_options)))
                if inp == back_val:
                    break
                elif inp is None:
                    continue
                else:
                    # Return aggregated data:
                    period = aggregate_dir[inp]
                    tvec_a, data_a = aggregate_measurements(tvec, data, period)
                    # Don't give any message when not aggregating:
                    if period != "minute": prefix = f"Data successfully aggregated by {period}."
                    break

        elif inp == "Display Statistics":
            while True:
                # We print the statistic
                clear_terminal()

                # Print appropriate title:
                if period == "hour of the day":
                    print(f"Average electricity consumption per hour:")
                else:
                    print(f"Electricity consumption per {period}:")
                # Print aggregated data if any:
                print_statistics(None, data) if tvec_a is None else print_statistics(None, data_a)

                print("99. Back")
                print(suffix)

                inp, suffix = is_valid_num(input(), range(0))
                # and return to the main menu if 9 is pressed
                if inp == back_val:
                    break
                elif inp is None:
                    continue

        elif inp == "Visualize":
            prefix = "To visualize the eletricity consumption, choose the zones you want displayed:"
            set_display(visualize_options, prefix, suffix)
            prefix = ""

            # If data hasn't been aggregated, fix it per default
            if tvec_a is None:
                tvec_a, data_a = aggregate_measurements(tvec, data, "minute")
                # prefix = "The data will be sorted consumption per minute (no aggregation)\n" + prefix
            
            # We get the zone the user wants to plot
            visualize_input, suffix = is_valid_num(input(), range(len(visualize_options)))
            
            clear_terminal()
            print("To continue, please close the Matplotlib window")
            if (visualize_input == back_val) or (visualize_input is None):
                continue
            plot_statistics(tvec_a, data_a, zone=visualize_input, time_unit=period)
        
        elif inp == "Quit":
            return


if __name__ == "__main__":
    # fmode = "forward fill"
    # zone = 0
    # period = "hour of the day"

    # clear_terminal()
    # tvec, data, _, _ = load_measurements("testdata1.csv", fmode)
    # tvec_a, data_a = aggregate_measurements(tvec, data, period)

    # plot_statistics(tvec_a, data_a, zone=zone, time_unit=period)
    main()