
def plot_statistics(tvec, data, zone="All"):
    if zone != "All":
        data = data[:, zone-1]
    print(data)
    print(len(data))
