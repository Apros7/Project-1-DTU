# This function only runs in Python 3

# Loading the numpy to use for calculations of statistics
import numpy as np
# Loading matplotlib.pyplot to make plots
import matplotlib.pyplot as plt

# We make a simple bacteria look up dictionary to be able to
# find the correct name according to the number of the bacteria
bacteria_lookup = {1: "Salmonella enterica",
                    2: "Bacillus cereus",
                    3: "Listeria",
                    4: "Brochothrix thermosphacta"}

# This function loads the data.
# It takes a string as an input and returns an array.
def dataLoad(filename : str) -> np.ndarray:
    # An empty list is created to store the data as it is loaded in
    data = []
    # We open the file in read mode:
    with open(filename, "r") as file:
        # For every row in the file we split the row into its 3 respective categories
        for row in file:
            temperature, growth_rate, bacteria = row.split()
            # The values are tested on the conditions given
            # If an error is encountered we inform the user what the error is.
            # And we continue to the next iteration without appending the values.
            try: temperature = int(temperature)
            except:
                print(f"This temperature value: {temperature} in {filename} is not an integer value")
                print("This row wont included in the data")
                continue

            if temperature < 10 or temperature > 60 :
                print(f"This temperature value: {temperature} in {filename} is either below 10 or above 60.")
                print("This row wont included in the data")
                continue

            try: growth_rate = float(growth_rate)
            except:
                print(f"This growth rate value: {growth_rate} in {filename} is not a float value.")
                print("This row wont included in the data")
                continue

            if growth_rate < 0:
                print(f"This growth rate value: {growth_rate} in {filename} is not a positive value.")
                print("This row wont included in the data")
                continue

            try: bacteria = int(bacteria)
            except:
                print(f"This bacteria value: {bacteria} is not an integer value")
                print("This row wont included in the data")
                continue

            if not int(bacteria) in bacteria_lookup.keys():
                print(f"This bacteria value: {int(bacteria)} in {filename} is not between 1 and 4.")
                print("This row wont included in the data")
                continue
            # After testing we can append the data
            data.append([temperature, growth_rate, bacteria])
    # At the end we return the full list with all the data in an array
    return np.array(data)

# This function will show certain statistics about the data.
# It takes the data as an array as an input and only returns None in the case that
# the user wants to go back to the main menu. Else nothing is returned.
def dataStatistics(data : np.ndarray):
    # First the staticstic value, which is soon to be calculated, is initiated.
    statisticValue = 0
    # Here we create a statistic lookup to get the right statistic based on the user input.
    statisticLookup = {1: "Mean Temperature",
                       2: "Mean Growth rate",
                       3: "Std Temperature",
                       4: "Std Growth rate",
                       5: "Rows",
                       6: "Mean Cold Growth rate",
                       7: "Mean Hot Growth rate",
                       8: "Go back to the main menu"}
    # We then get the input from the user on which statistic the user would like:
    statisticInput = input("Type the number corresponding to the statistic you want to be shown:\n"
                      "1. Mean Temperature\n"
                      "2. Mean Growth rate\n"
                      "3. Std Temperature\n"
                      "4. Std Growth rate\n"
                      "5. Rows\n"
                      "6. Mean Cold Growth rate\n"
                      "7. Mean Hot Growth rate\n"
                      "8. Go back to the main menu\n")
    # We then check that this value is a number between 1 and 8.
    statistic = checkIfValidNumber(statisticInput, 1, 8)
    # We then, based on the input, compute the desired statistic
    # and assigns it to the statisticValue variable.
    if statistic == 1:
         statisticValue = np.mean(data[:,0])
    elif statistic == 2:
        statisticValue = np.mean(data[:,1])
    elif statistic == 3:
        statisticValue = np.std(data[:,0])
    elif statistic == 4:
        statisticValue = np.std(data[:,1])
    elif statistic == 5:
        statisticValue = len(data)
    elif statistic == 6:
        coldGrowthRate = [data[i,1] for i in range(len(data)) if data[i,0]<20]
        statisticValue = np.mean(coldGrowthRate)
    elif statistic == 7:
        coldGrowthRate = [data[i, 1] for i in range(len(data)) if data[i, 0] < 20]
        statisticValue = np.mean(coldGrowthRate)
    # If the user wishes to go back to the main menu
    # None is returned and therefore nothing is computed or displayed.
    elif statistic == 8:
        return None
    # We then print the statistic together with information on which statistic this is.
    print(f"The {statisticLookup[statistic]} of your current data is: {statisticValue}")


# This function will plot 2 plots based on the data.
# It takes the data as an array as an input and returns nothing.
# It opens a new window and displays 2 plots in it.
def dataPlot(data : np.ndarray) -> None:
    # Creating and selecting the right subplot:
    plt.subplot(2, 1, 1)
    
    # Creating lists with the x and y values
    x_values = list(bacteria_lookup.values())
    y_values = [np.count_nonzero(data[:,2] == i) for i in [1,2,3,4]]
    # plotting as a bar plot
    plt.bar(x_values, y_values)
    # Here we change the title, x label, size of x values, y label
    # and make the layout tight to make sure there are space for both plot
    plt.title("Number of bacteria")
    plt.xlabel("Bacteria")
    plt.xticks(size = 8)
    plt.ylabel("Number of instances")
    plt.tight_layout()

    # Plotting Growth rate by temperature
    plt.subplot(2, 1, 2)
    # A small dictionary is made to use to the correct color based on the bacteriatype
    colors = {1: "r", 2: "y", 3: "g", 4: "b"}
    # We then loop through every kind of bacteria and plot their data.
    data = data[data[:,0].argsort()]
    for Bacteria in range(1,5):
        xValuesBacteria = [data[i,0] for i in range(len(data)) if data[i,2] == Bacteria]
        yValuesBacteria = [data[i,1] for i in range(len(data)) if data[i,2] == Bacteria]
        plt.plot(xValuesBacteria, yValuesBacteria, colors[Bacteria], label=f"{bacteria_lookup[Bacteria]}")
    # We then change the title, x label, y label.
    plt.title("Growth Rate by Temperature for 4 bacteria")
    plt.xlabel("Temperature")
    plt.ylabel("Growth Rate")
    # We also make a legend to make sure the user easily can see
    # which line in the plot is corresponds to the different bacteria
    plt.legend(loc=1, fontsize=6)
    # And make the layout tight to make space for both.
    plt.tight_layout()
    # We then show the layout to the user
    plt.show()

# This function takes any numpy array as input and outputs one of three possibilities.
# 1: New filtered array, 2: the original data, or 3: return the input array.
def dataFilter(data : np.ndarray, filtered_data : np.ndarray) -> np.ndarray:
    # First the user is giving the different possibilities
    desiredFilter = input("Type the number corresponding with the way you want to filter your data: \n"
                          "1. By type of bacteria\n"
                          "2. By interval for growth rate\n"
                          "3. Reset filter\n"
                          "4. Go back to the main menu\n")
    # We then check that this number is a number between 1 and 4.
    filterNumber = checkIfValidNumber(desiredFilter, 1, 4)
    if filterNumber == 1:
        # If the user chooses to filter data based on type of bacteria
        # the user is prompted to choose which bacteria to filter on.
        print("You have chose to filter data based on the type of bacteria")
        bacteriaNumber = input("Please type number corresponding with the type of bacteria, you want to filter by:\n"
                             "1. Salmonella enterica\n"
                             "2. Bacillus cereus\n"
                             "3. Listeria\n"
                             "4. Brochothrix thermosphacta\n")
        # We check that this is a number between 1 and 4
        bacteriaNumber = checkIfValidNumber(bacteriaNumber, 1, 4)
        # Give the information that the data was filtered based on the bacteria
        # that the user chose
        print(f"Your data was successfully filtered based on the {bacteria_lookup[bacteriaNumber]} bacteria")
        # and then returns the data that only has the correct bacteria.
        return np.array([data[i,:] for i in range(len(data)) if data[i,2] == bacteriaNumber])

    if filterNumber == 2:
        # if the user wants to filter data based on an interval for the growth rate
        # the user is prompted to give a lower and upper bound
        print("You have chose to filter data based on an interval for growth rate\n."
              "The lower and upper bound will NOT be included in the data.")
        lowerBound = input("Please input the lower bound:\n")
        # We check that the lower and upper bound is a float value
        try: lowerBound = float(lowerBound)
        except: print("You need to type a number"); return "Error"
        upperBound = input("Please input the upper bound:\n")
        try: upperBound = float(upperBound)
        except: print("You need to type a number"); return "Error"
        if lowerBound >= upperBound:
            # Although the data would still work if the lower bound is higher or equal to the higher bound
            # this would make no sense as no data would be left
            # therefore we don't allow this and inform the user.
            print("The lower bound has to be lower than the upper bound"); return "Error"
        print("Your data was successfully filtered.")
        # The data with only the rows where the growth rate is between
        # the lower and upper bound is returned.
        return np.array([data[i, :] for i in range(len(data)) if data[i, 1] > lowerBound and data[i, 1] < upperBound])


    if filterNumber == 3:
        # if the user wants to reset the filter,
        # the full original data is returned without any filter.
        print("Your filter has been reset.")
        return data
    # if the user chooses to go back to the main menu,
    # the data will stay the same, whether or not there is a filter on it.
    return filtered_data

# This function is introduced to simplify the code related to our command-line interface.
def checkIfValidNumber(value, lowerBound, upperBound):
    # If the input can't be converted to an int, print error and return none.
    try: intValue = int(value)
    except: print("You need to type a number"); return None

    # If the input isn't between lower and upper bound, print error and return none.
    if not (lowerBound < intValue and intValue < upperBound):
        print("You need to type a valid number"); return None
    return intValue

def main():
    ## Main program:
    # This is the time of which the main program will begin.
    # First we create a variable to keep track whether the data has been loaded or not.
    # We set it to False as the data has not yet been loaded
    isDataLoaded = False

    # Introduction to the program
    print("Welcome to our program :-).\n"
          "This program is used to analyze bacteria-data.\n"
            "You need to load in data before any other action is possible")

    # This loop will until the user wants to quit
    while True:
        # The user is prompted which action should be taken
        action = input("Please choose what you want to do by typing the number "
                       "corresponding to the action you would like to take:\n"
                    "1. Load data\n"
                    "2. Filter data\n"
                    "3. Show statistics\n"
                    "4. Create plots\n"
                    "5. Exit program\n")
        # We then check that this input is a number between 1 and 5.
        action = checkIfValidNumber(action, 1, 5)
        # If the user want to quit, the program loop will stop and therefore also the program.
        if action == 5:
            break

        if action == 1:
            # If the users wants to load in data
            # the user is prompted to write the filename of the file which should be loaded
            filename = input("You have chosen to load data.\n"
                             "Please write the filename of the file that should be loaded in:\n")
            # We then try to load the file
            # If the filename does not exist or is not a string, no data will be loaded and the user til be informed
            # If the filename is correct, the original data is assigned to data
            # As this is the variable for the unfiltered data.
            # We now also know that the data has been loaded and user is informed.
            try:
                data = dataLoad(filename)
                originalData = data
                isDataLoaded = True
                print("Your data was successfully loaded")

            except: print("You need to type in a valid filename")

        # The rest of the actions are only allowed if the data has been loaded
        if isDataLoaded:
            if action == 2:
                # if the user wants to filter the data, then we try to perform the function
                # if we get an error, which will happen if the user does not input a number between 1 and 4
                # the user will already be informed and nothing should happen
                try: data = dataFilter(originalData, data)
                except: None

            if action == 3:
                # if the user wants to get statistic, then we try to perform the function
                # if we get an error, which will happen if the user does not input a number between 1 and 8
                # the user will already be informed and nothing should happen
                try: dataStatistics(data)
                except: None

            if action == 4:
                # if the user wants to have their data plotted
                # then another window will open and the user will be informed
                dataPlot(data)
                print("Your data has been plotted and will open in a new window.")
        # if the data has not been loaded the user will get a reminder before the loop resets.
        else:
            print("You need to load in your data before you can take any other action.")

# main()

