import numpy as np

def print_statistics(tvec, data):
    statistics = []
    for i in range(4):
        current_row = list(tvec[i])
        zone = i+1
        statistics.append(
            [zone,
            min(current_row),
            np.quartile(current_row, 0.25),
            np.quartile(current_row, 0.50),
            np.quartile(current_row, 0.75),
            max(current_row)
        ])

    # printing the statistics:
    headers = ["Zone", "Minimum", "1. kvartil", "2. kvartil", "3. kvartil", "Maximum"]
    for header in headers:
        print(f"{header:>10}", end="")
    
from load_measurements import load_measurements
tvec, data = load_measurements("testdata1.csv", fmode=None)
print_statistics(tvec, data)
    