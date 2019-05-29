import pandas as pd
import numpy as np

from tools import DataTaker



def main():
    dt = DataTaker()
    table = dt.read_distance()
    print(table)


if __name__ == '__main__':
    main()
