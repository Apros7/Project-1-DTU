from load_measurements import load_measurements
from print_statistics import print_statistics
from plot_statistics import plot_statistics
from aggregate_measurements import aggregate_measurements

def main():
    tvec, data = load_measurements("testdata1.csv", "drop")
    tvec_a, data_a = aggregate_measurements(tvec, data, "month")

    # print_statistics(tvec, data)
    plot_statistics(tvec, data)


if __name__ == "__main__":
    main()

