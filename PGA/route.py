from typing import List
import random
import numpy as np

from tools import GlobalMap
import PGA.constant as const

center_id = const.center_id
custom_number = const.custom_number
station_number = const.station_number

max_volume = const.max_volume
max_weight = const.max_weight
unload_time = const.unload_time
driving_range = const.driving_range
charge_tm = const.charge_tm
charge_cost = const.wait_cost
wait_cost = const.wait_cost
depot_open_time = const.depot_open_time
unit_trans_cost = const.unit_trans_cost
huge = const.huge


class Route:
    g_map: GlobalMap
    sequence: List[int]

    def __init__(self, sequence, g_map, punish=9999, refresh_im=True):
        """
        :param sequence: node in this route, order sensitive
        :param g_map: global map
        :param punish: punish parameter
        :param refresh_im: whether refresh route state after init immediately
        """
        self.sequence = sequence
        self.g_map = g_map
        self.punish = punish
        self.start_time = depot_open_time
        self.cost = 0
        self.window_punish, self.capacity_punish, self.weight_punish, self.volume_punish = 0, 0, 0, 0
        self.capacity_remain = driving_range
        self.capacity_waste = 0
        self.served_w, self.served_v = 0, 0
        self.extra_t = 0
        if refresh_im:
            self.refresh_state()

    def refresh_state(self, reset_window=True):
        """
        refresh state of this route, i.e. recalculate all punish, cost and other parameters
        if the sequence and punish parameter of this route hasn't been changed, this method shouldn't be called
        :param reset_window: if time window is reset to the last serve time after time window punish
        :return: None
        """
        self.start_time = depot_open_time
        self.cost = 0
        self.window_punish, self.capacity_punish, self.weight_punish, self.volume_punish = 0, 0, 0, 0
        self.capacity_remain = driving_range
        self.capacity_waste = 0
        self.served_w, self.served_v = 0, 0
        self.extra_t = 0
        time = depot_open_time
        distance = 0
        capacity = driving_range
        weight, volume = max_weight, max_volume
        pre_node = center_id
        extra_time = []
        for node in self.sequence:
            d = self.g_map.get_distance(pre_node, node)
            t = self.g_map.get_time(pre_node, node)
            capacity -= d
            if node > custom_number:
                time += t + charge_tm
                distance += d
                self.cost += charge_cost + unit_trans_cost * d
                self.capacity_punish += self.punish * abs(capacity) / driving_range if capacity < 0 else 0
                self.capacity_waste = max(self.capacity_waste, capacity)
                capacity = driving_range  # recharge battery
            else:
                self.cost += unit_trans_cost * d  # regular cost
                time += t
                window = self.g_map.get_window(node)
                if time < window[0]:
                    self.cost += wait_cost * abs(window[0] - time)  # waiting cost
                    extra_time.append(window[1] - time)
                    time = window[0]
                elif time > window[1]:
                    self.window_punish += self.punish * abs(time - window[1])
                    time = window[1] if reset_window else time
                    extra_time.append(-1)
                else:
                    extra_time.append(window[1] - time)
                time += unload_time
                demand = self.g_map.get_demand(node)
                weight -= demand[0]
                volume -= demand[1]
                self.served_w += demand[0]
                self.served_v += demand[1]
                self.weight_punish += self.punish * abs(weight) if weight < 0 else 0
                self.volume_punish += self.punish * abs(volume) if volume < 0 else 0
                self.capacity_punish += self.punish * abs(capacity) / driving_range if capacity < 0 else 0
            pre_node = node
        d = self.g_map.get_distance(pre_node, center_id)
        t = self.g_map.get_time(pre_node, center_id)
        capacity -= d
        self.capacity_remain = capacity
        time += t
        self.cost += unit_trans_cost * d  # regular cost
        self.capacity_punish += self.punish * abs(capacity) / driving_range if capacity < 0 else 0
        if time > 24.:
            self.window_punish += self.punish * abs(time - 24.)
            extra_time.append(-1)
        else:
            extra_time.append(24. - time)
        self.extra_t = max(0, min(extra_time))
        self.cost -= len(extra_time) * self.extra_t * wait_cost  # reduce wait cost
        self.cost += self.window_punish + self.capacity_punish + self.weight_punish + self.volume_punish  # add punish
        self.start_time += self.extra_t

    def set_punish_para(self, punish):
        self.punish = punish

    def delete_node(self, node: int):
        self.sequence.remove(node)

    def get_volume_remain(self):
        return (max_volume - self.served_v) / max_volume

    def get_weight_remain(self):
        return (max_weight - self.served_w) / max_weight

    def get_mean_time_window(self):
        """
        get mean time window, i.e. mean value of first time and last time
        may be used to compare this route with the other
        :return: mean value of first time, mean value of last time
        """
        first_tm = []
        last_tm = []
        for node in self.sequence:
            if node <= custom_number:
                window = self.g_map.get_window(node)
                first_tm.append(window[0])
                last_tm.append(window[1])
        return sum(first_tm) / (len(first_tm) + 1), sum(last_tm) / (len(last_tm) + 1)

    def get_if_punish(self):
        return self.volume_punish > 0 or self.weight_punish > 0 or self.window_punish > 0 or self.capacity_punish > 0

    def has_customer(self):
        """
        get if this route has any customer (if none, this route absolutely needs to be removed)
        :return: whether this route has any customer
        """
        for node in self.sequence:
            if node <= custom_number:
                return True
        return False

    def split_mutate(self, p=0.618):
        """
        split this route into two routes
        :param p: the probability of put node into first route
        :return: route 1 and route 2 from this route
        """
        sequence1 = []
        sequence2 = []
        for node in self.sequence:
            if random.random() < p:
                sequence1.append(node)
            else:
                sequence2.append(node)
        route1 = Route(sequence=sequence1, g_map=self.g_map, punish=self.punish)
        route2 = Route(sequence=sequence2, g_map=self.g_map, punish=self.punish)
        if len(route2.sequence) == 0:
            return [route1]
        elif len(route1.sequence) == 0:
            return [route2]
        else:
            return route1, route2

    def add_mutate(self):
        """
        add a station to this route, between [0, len], i.e. everywhere is possible
        :return: None
        """
        for i in range(0, 5):
            add_pos = random.randint(0, len(self.sequence))
            if random.random() < 0.5:
                if add_pos != len(self.sequence):
                    station = self.g_map.get_nearby_station(self.sequence[add_pos])
                else:
                    station = self.g_map.get_nearby_station(self.sequence[center_id])
            else:
                if add_pos != 0:
                    station = self.g_map.get_nearby_station(self.sequence[add_pos - 1])
                else:
                    station = self.g_map.get_nearby_station(self.sequence[center_id])
            old_sequence = self.sequence.copy()
            old_capacity_punish = self.capacity_punish
            self.sequence.insert(add_pos, station)
            self.refresh_state()
            if self.capacity_punish < old_capacity_punish:
                break
            else:
                self.sequence = old_sequence.copy()
                del old_sequence
        self.refresh_state()

    def delete_mutate(self):
        """
        delete a station in this route if not increase punish
        :return: None
        """
        idx = 0
        while idx < len(self.sequence):
            node = self.sequence[idx]
            if node > custom_number:
                new_sequence = self.sequence.copy()
                new_sequence.pop(idx)
                new_route = Route(g_map=self.g_map, punish=self.punish, sequence=new_sequence)
                if new_route.capacity_punish <= self.capacity_punish:
                    self.sequence.pop(idx)
                    idx -= 1
                    self.refresh_state()
                    del new_route
            idx += 1

    def reschedule_mutate(self):
        """
        reschedule the route, i.e. each time add the nearest node from pre node
        :return: None
        """
        temp_sequence = self.sequence.copy()
        copy_sequence = self.sequence.copy()
        copy_cost = self.cost
        self.sequence[:] = []
        pre_node = center_id
        while temp_sequence:
            node = min(temp_sequence, key=lambda x: self.g_map.get_distance(pre_node, x))
            self.sequence.append(node)
            temp_sequence.remove(node)
        self.refresh_state()
        if self.cost > copy_cost:
            del self.sequence
            self.sequence = copy_sequence
            self.refresh_state()

    def random_mutate(self):
        """
        randomly swap two node in thie route
        :return: None
        """
        pos1 = random.randint(0, len(self.sequence) - 1)
        pos2 = random.randint(0, len(self.sequence) - 1)
        self.sequence[pos1], self.sequence[pos2] = self.sequence[pos2], self.sequence[pos1]

    def deepcopy(self):
        new_route = Route(sequence=self.sequence.copy(), g_map=self.g_map, punish=self.punish, refresh_im=False)
        new_route.start_time = self.start_time
        new_route.cost = self.cost
        new_route.window_punish, new_route.capacity_punish, new_route.weight_punish, new_route.volume_punish = \
            self.window_punish, self.capacity_punish, self.weight_punish, self.volume_punish
        new_route.capacity_remain = self.capacity_remain
        new_route.served_w, new_route.served_v = self.served_w, self.served_v
        new_route.extra_t = self.extra_t
        return new_route

    def is_equal(self, route):
        if len(self.sequence) != len(route.sequence) or self.cost != route.cost:
            return False
        for node1, node2 in zip(self.sequence, route.sequence):
            if node1 != node2:
                return False
        return True

    def get_total_punish(self):
        return self.capacity_punish + self.window_punish + self.volume_punish + self.weight_punish

    def try_insert(self, node: int):
        old_cost = self.cost
        old_punish = self.get_total_punish()
        try_route_list = []
        nearby_station = self.g_map.get_nearby_station(node)
        for insert_pos in range(0, len(self.sequence) + 1):
            try_sequence = self.sequence.copy()
            try_sequence.insert(insert_pos, node)
            try_route_list.append(Route(g_map=self.g_map, sequence=try_sequence, punish=self.punish))
            try_sequence = self.sequence.copy()
            try_sequence.insert(insert_pos, node)
            try_sequence.insert(insert_pos, nearby_station)
            try_route_list.append(Route(g_map=self.g_map, sequence=try_sequence, punish=self.punish))
            try_sequence = self.sequence.copy()
            try_sequence.insert(insert_pos, node)
            try_sequence.insert(insert_pos + 1, node)
            try_route_list.append(Route(g_map=self.g_map, sequence=try_sequence, punish=self.punish))
        best_insert = min(try_route_list, key=lambda x: x.cost)
        del try_route_list
        if best_insert.get_total_punish() <= old_punish:
            self.sequence = best_insert.sequence.copy()
            self.refresh_state()
            return self.cost - old_cost
        else:
            return huge
