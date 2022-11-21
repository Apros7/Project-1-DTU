import numpy as np

def print_statistics(tvec, data):
    statistics = []
    for i in range(4):
        current_row = list(data[i])
        zone = i+1
        statistics.append(
            [zone,
            np.min(current_row),
            np.quantile(current_row, 0.25),
            np.quantile(current_row, 0.50),
            np.quantile(current_row, 0.75),
            np.max(current_row)
        ])
    statistics.append(
            ["All",
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
    