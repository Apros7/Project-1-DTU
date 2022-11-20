from load_measurements import load_measurements
from print_statistics import print_statistics

def main():
    tvec, data = load_measurements("testdata2.csv", "forward fill")
    print(data)
    print_statistics(tvec, data)


main()