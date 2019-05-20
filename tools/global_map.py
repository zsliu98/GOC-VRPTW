import pandas as pd
from tools.data_taker import DataTaker


class GlobalMap:

    def __init__(self,read_dir):
        dt = DataTaker(read_dir=read_dir)
        self.distance_table = dt.read_distance()
        self.initialize()

    def get_distance(self, id_x, id_y):
        """
        return travel distance between two customer
        :param id_x: customer id
        :param id_y: customer id
        :return:
        """
        pass

    def get_time(self, id_x, id_y):
        """
        return travel time between two customer
        :param id_x: customer id
        :param id_y: customer id
        :return:
        """
        pass

    def initialize(self):
        """
        remove un-useful edges in the map
        :return:
        """
        pass
