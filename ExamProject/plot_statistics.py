import matplotlib.pyplot as plt
import numpy as np

from load_measurements import load_measurements
tvec, data = load_measurements("testdata3.csv")


# Tvec skal kun indeholde relevante tidsdata
tvec = tvec[:, 4]

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
    plt.title(f"Consuption for {title} per {time}")
    plt.xlabel(f"Time in {time}")
    plt.ylabel("Energy used in Watt-hours")
    plt.show()


    
plot_statistics(tvec, data, zone=1)