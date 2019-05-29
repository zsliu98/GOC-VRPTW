import pandas as pd
from tools.data_taker import DataTaker


class GlobalMap:

    def __init__(self, read_dir):
        dt = DataTaker(read_dir=read_dir)
        self.distance_table = dt.read_distance()
        self.initialize()

    def get_distance(self, idx, idy):
        """
        return travel distance between two customer
        :param idx: customer id
        :param idy: customer id
        :return:
        """
        return 0

    def get_time(self, idx, idy):
        """
        return travel time between two customer
        :param idx: customer id
        :param idy: customer id
        :return:
        """
        return 0

    def get_window(self, idx):
        return 0, 0

    def get_demand(self, idx):
        return 0, 0

    def initialize(self):
        """
        remove un-useful edges in the map
        :return:
        """
        pass
