import pandas as pd
import numpy as np
import datetime
from tools.data_taker import DataTaker


class GlobalMap:

    def __init__(self, read_dir='data', warning=False):
        dt = DataTaker(read_dir=read_dir)
        self.distance_table = dt.read_distance()
        self.node_table = dt.read_node()
        self.nearby_station_list = []
        self.warning = warning
        self.initialize()

    def get_distance(self, idx, idy):
        """
        get travel distance between two position
        :param idx: position id
        :param idy: position id
        :return: travel distance between two position
        """
        if idx == idy:
            if idx != 0 and self.warning:
                print('Error may occur. Distance has been asked between two identical position.')
            return 0
        else:
            return float(self.distance_table['distance'][self.__get_index__(idx, idy)])

    def get_time(self, idx, idy):
        """
        get travel time between two position
        :param idx: position id
        :param idy: position id
        :return: travel time between two position
        """
        if idx == idy:
            if idx != 0 and self.warning:
                print('Error may occur. Travel time has been asked between two identical position.')
            return 0
        else:
            return float(self.distance_table['spend_tm'][self.__get_index__(idx, idy)]) / 60

    def get_window(self, idx):
        """
        return time window of the customer
        :param idx: customer id
        :return: time window
        """
        first_tm: datetime.time = self.node_table['first_receive_tm'][idx]
        last_tm: datetime.time = self.node_table['last_receive_tm'][idx]
        first = float(first_tm.hour + first_tm.minute / 60)
        last = float(last_tm.hour + last_tm.minute / 60)
        del first_tm
        del last_tm
        return first, last

    def get_demand(self, idx):
        """
        return demand of the customer
        :param idx: customer id
        :return: weight, volume
        """
        weight = self.node_table['pack_total_weight'][idx]
        volume = self.node_table['pack_total_volume'][idx]
        return weight, volume

    def get_nearby_station(self, idx):
        """
        return the most nearest station of the customer
        :param idx: customer id
        :return: station id
        """
        if idx > 1000 and self.warning:
            print('Error may occur. Nearby station has been asked of a station.')
        return self.nearby_station_list[idx]

    def initialize(self):
        """
        remove un-useful edges in the map
        set nearby station of every customer
        :return: None
        """
        for i in range(0, 1001):
            temp_station_d = self.distance_table['distance'][self.__get_index__(i, 1001):self.__get_index__(i, 1100)]
            self.nearby_station_list.append(np.argmax(np.array(temp_station_d)) + 1001)
        for i in range(1001, 1101):
            min_d = 99999999
            min_pos = 0
            for j in range(1001, 1101):
                if i == j:
                    continue
                elif self.distance_table['distance'][self.__get_index__(i, j)] < min_d:
                    min_d = self.distance_table['distance'][self.__get_index__(i, j)]
                    min_pos = j
            self.nearby_station_list.append(min_pos)

    @staticmethod
    def __get_index__(idx, idy):
        if idx >= idy:
            idx, idy = idy, idx
        index = idx * 1100 + idy - 1
        return index
