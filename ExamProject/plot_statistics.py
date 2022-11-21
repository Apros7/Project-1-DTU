import matplotlib.pyplot as plt
import numpy as np

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
    plt.title(f"Consuption for {title} per {time}")
    plt.xlabel(f"Time in {time}")
    plt.ylabel("Energy used in Watt-hours")
    plt.show()