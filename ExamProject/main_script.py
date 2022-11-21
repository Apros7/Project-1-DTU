from load_measurements import load_measurements
from print_statistics import print_statistics
from plot_statistics import plot_statistics

def main():
    pass

tvec, data = load_measurements("testdata1.csv")
plot_statistics(tvec, data)
