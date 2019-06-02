import pandas as pd
import numpy as np
import datetime
from tools.data_taker import DataTaker


class GlobalMap:

    def __init__(self, read_dir='data'):
        dt = DataTaker(read_dir=read_dir)
        self.distance_table = dt.read_distance()
        self.node_table = dt.read_node()
        self.nearby_station_list = []
        self.initialize()

    def get_distance(self, idx, idy):
        """
        get travel distance between two position
        :param idx: position id
        :param idy: position id
        :return: travel distance between two position
        """
        if idx == idy:
            print('Error may occur. Distance has been asked between two identical position.')
            return 0
        else:
            return self.distance_table['distance'][self.__get_index__(idx, idy)]

    def get_time(self, idx, idy):
        """
        get travel time between two position
        :param idx: position id
        :param idy: position id
        :return: travel time between two position
        """
        if idx == idy:
            print('Error may occur. Travel time has been asked between two identical position.')
            return 0
        else:
            return self.distance_table['spend_tm'][self.__get_index__(idx, idy)]

    def __get_index__(self, idx, idy):
        if idx >= idy:
            idx, idy = idy, idx
        if idx == 0:
            return idy - 1
        else:
            return idx * 1099 + idy

    def get_window(self, idx):
        first_tm: datetime.time
        last_tm: datetime.time
        """
        return time window of the customer
        :param idx: customer id
        :return: time window
        """
        first_tm = self.node_table['first_receive_tm'][idx]
        last_tm = self.node_table['last_receive_tm'][idx]
        first = first_tm.hour + first_tm.minute / 60
        last = last_tm.hour + last_tm.minute / 60
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
        if idx > 1000:
            print('Error occurs. Nearby station has been asked of a station.')
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
            del temp_station_d
