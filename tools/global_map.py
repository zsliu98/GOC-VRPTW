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
        self.nearby_custom_list = []
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

    def get_nearby_custom(self, idx):
        """
        return the most 'nearest' customer of the customer
        :param idx: customer id
        :return: 'nearest' customer id
        """
        if idx > 1000:
            if self.warning:
                print('Error may occur. Nearby custom has been asked of a custom.')
            return -1
        else:
            return self.nearby_custom_list[idx]

    def initialize(self):
        """
        set nearby station of every customer
        set 'nearby' customer of every customer
        :return: None
        """
        # set nearby station of every customer, evaluated by distance
        for i in range(0, 1001):
            temp_station_d = self.distance_table['distance'][self.__get_index__(i, 1001):self.__get_index__(i, 1100)]
            self.nearby_station_list.append(np.argmin(np.array(temp_station_d)) + 1001)
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

        # set 'nearby' customer of every customer, evaluated by distance, demand and time window
        self.nearby_custom_list.append(-1)
        for i in range(1, 1001):
            min_d = 99999999
            min_pos = -1
            demand = self.get_demand(i)
            time = self.get_window(i)
            for j in range(1, 1001):
                if i == j:
                    continue
                else:
                    n_dist = self.distance_table['distance'][self.__get_index__(i, j)]
                    n_demand = self.get_demand(j)
                    n_time = self.get_window(j)
                    if abs(demand[0] - n_demand[0]) >= 0.35 or abs(demand[1] - n_demand[1]) >= 7 or n_dist >= 10000:
                        continue
                    if abs(time[0] - n_time[0]) >= 0.5 or abs(time[1] - n_time[1]) >= 1:
                        continue
                    n_d = abs(demand[0] - n_demand[0]) / 2.5 + 0.1 * abs(demand[1] - n_demand[1]) / 16 + n_dist / 120000
                    n_d += abs(time[0] - n_time[0]) + abs(time[1] - n_time[1])
                    if n_d < min_d:
                        min_d = n_d
                        min_pos = j
            self.nearby_custom_list.append(min_pos)

    @staticmethod
    def __get_index__(idx, idy):
        if idx >= idy:
            idx, idy = idy, idx
        index = idx * 1100 + idy - 1
        return index
