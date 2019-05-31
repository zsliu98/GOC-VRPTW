import pandas as pd
import numpy as np

from tools import DataTaker


def main():
    dt = DataTaker()
    table = dt.read_node()
    print(list(table['first_receive_tm'][2:4]))
    print(table['first_receive_tm'][2].hour + table['first_receive_tm'][2].minute / 60)


if __name__ == '__main__':
    main()
