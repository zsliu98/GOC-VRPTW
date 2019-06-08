from typing import List
import numpy as np
import random
import math

from tools import GlobalMap
from PGA.route import Route
import PGA.constant as const

random_mutate_p = const.random_mutate_p

center_id = const.center_id
custom_number = const.custom_number
station_number = const.station_number

max_volume = const.max_volume
max_weight = const.max_weight
starve_para = const.starve_para
unload_time = const.unload_time
driving_range = const.driving_range
charge_tm = const.charge_tm
charge_cost = const.charge_cost
wait_cost = const.wait_cost
depot_wait = const.depot_wait
depot_open_time = const.depot_open_time
unit_trans_cost = const.unit_trans_cost
vehicle_cost = const.vehicle_cost

combine_try_time = const.combine_try_time
insert_try_time = const.insert_try_time
remove_try_p = const.remove_try_p

huge = const.huge


class Chromo:
    g_map: GlobalMap
    sequence: List[Route]

    def __init__(self, sequence=None, g_map=None, idx=0, punish=9999,
                 reset_window=True, refresh_im=True, feasible_flag=True):
        """
        :param sequence: routes in this chromo, order insensitive
        :param g_map: global map
        :param idx: chromo idx, not necessary
        :param punish: punish parameter
        :param reset_window: whether reset time window when time window punishment occurs
        :param refresh_im: whether refresh chromo state after init immediately
        :param feasible_flag: whether the chromo generate by feasible generator
        """
        self.idx = idx
        self.g_map = g_map
        self.sequence = sequence
        self.punish = punish
        self.reset_window = reset_window
        self.cost = 0
        self.vehicle_number = 0
        self.rank = 0
        if self.sequence is None:
            self.sequence = []
            self.__random_init__(feasible_flag=feasible_flag)
        if refresh_im:
            self.refresh_state()

    def refresh_state(self):
        """
        refresh state of this chromo
        :return: None
        """
        self.cost = 0
        self.vehicle_number = len(self.sequence)
        start_list = []
        for route in self.sequence:
            route.refresh_state()
            self.cost += route.cost  # pure route cost
            self.cost += vehicle_cost  # new vehicle cost
            start_list.append(route.start_time)  # record each route start time
        # reuse some vehicles
        start_list.sort()
        pos_1 = 0
        pos_2 = 0
        while pos_2 < len(start_list):
            if start_list[pos_2] - start_list[pos_1] >= depot_wait:  # an old vehicle is again usable
                self.cost += depot_wait * wait_cost - vehicle_cost  # replace new-vehicle cost as wait cost
                pos_1 += 1
                self.vehicle_number -= 1
            pos_2 += 1

    def get_fitness(self):
        return 1 / self.cost

    def get_score(self):
        return self.cost - self.vehicle_number * vehicle_cost, self.vehicle_number

    def reset_rank(self):
        self.rank = 0

    def __random_init__(self, feasible_flag=True):
        """
        random init this chromo by some prior experience (when no data is given)
        :return: None
        """
        if feasible_flag:
            self.sequence = self.feasible_generate(list(range(1, custom_number + 1)))
        else:
            # shuffle all customer randomly
            temp_node = list(range(1, custom_number + 1))
            random.shuffle(temp_node)
            # init all route, i.e. self.sequence
            capacity = driving_range
            weight, volume = max_weight, max_volume
            temp_route = []
            pre_node = center_id
            for idx, node in enumerate(temp_node):
                capacity -= self.g_map.get_distance(pre_node, node)
                demand = self.g_map.get_demand(node)
                weight -= demand[0]
                volume -= demand[1]
                if capacity < 0 or weight < 0 or volume < 0:
                    insert_station_p = (math.exp(min(weight / max_weight, volume / max_volume)) - 1) / (math.e - 1)
                    if weight < 0 or volume < 0:
                        insert_station_p = 0
                    next_station = self.g_map.get_nearby_station(pre_node)
                    if self.g_map.get_distance(pre_node, next_station) > capacity:
                        insert_station_p = 0
                    if random.random() < insert_station_p:
                        temp_route.append(next_station)
                        temp_route.append(node)
                        capacity = driving_range
                        capacity -= self.g_map.get_distance(next_station, node)
                        pre_node = node
                    else:
                        temp_route.append(node)
                        self.sequence.append(Route(sequence=temp_route.copy(), g_map=self.g_map, punish=self.punish))
                        capacity = driving_range
                        weight, volume = max_weight, max_volume
                        temp_route[:] = []
                        pre_node = center_id
                else:
                    temp_route.append(node)
                    pre_node = node
            self.sequence.append(Route(sequence=temp_route.copy(), g_map=self.g_map, punish=self.punish))

    def set_punish_para(self, punish):
        """
        set new punish parameter to current
        :param punish: new punish parameter
        :return: None
        """
        self.punish = punish
        for route in self.sequence:
            route.set_punish_para(punish)

    def clear(self, c_route: Route):
        """
        clear all node in the given route to prepare for the route insert
        :param c_route: the route going to be inserted
        :return: None
        """
        clear_list = c_route.sequence
        for node in clear_list:
            if node > custom_number:
                continue
            for route in self.sequence:
                try:
                    route.delete_node(node)
                    break
                except ValueError:
                    pass

    def mutate(self):
        """
        mutate the chromo, include: split, add, delete, combine, reschedule, random
        :return: None
        """
        max_d_waste = max(self.sequence, key=lambda x: x.capacity_waste).capacity_remain
        self.__delete_station_mutate__(max_d_waste)
        max_s = max(self.sequence, key=lambda x: x.window_punish + x.weight_punish + x.volume_punish)
        max_s_punish = max_s.window_punish + max_s.weight_punish + max_s.volume_punish
        self.__split_mutate__(max_s_punish)
        max_a_punish = max(self.sequence, key=lambda x: x.capacity_punish).capacity_punish
        self.__add_station_mutate__(max_a_punish)
        max_d_waste = max(self.sequence, key=lambda x: x.capacity_waste).capacity_remain
        self.__delete_station_mutate__(max_d_waste)
        self.__combine_mutate__()
        self.__remove_route_mutate__()
        # self.__reschedule_mutate__()
        if random.random() < random_mutate_p:
            self.__random_reverse_mutate__()

    def has_punish_num(self):
        """
        calculate how many routes have punishment
        :return: number of routes have punishment
        """
        num = 0
        window_punish = 0
        volume_punish = 0
        weight_punish = 0
        capacity_punish = 0
        for route in self.sequence:
            if route.get_if_punish():
                num += 1
                window_punish += route.window_punish
                volume_punish += route.volume_punish
                weight_punish += route.weight_punish
                capacity_punish += route.capacity_punish
        return num, weight_punish / self.punish, volume_punish / self.punish, window_punish / self.punish, capacity_punish / self.punish

    def __split_mutate__(self, max_punish):
        """
        if window, weight or volume punish exist, randomly split the route into two routes
        if no window, weight or volume punish exists, nothing will be done
        :param max_punish: max total window, weight and volume punish, use for normalization
        :return: None
        """
        if max_punish == 0:
            return
        origin_route = self.sequence.copy()
        for route in origin_route:
            if route.window_punish + route.weight_punish + route.volume_punish > 0:
                self.sequence.remove(route)
                self.sequence.extend(self.feasible_generate(route.sequence))

    def __add_station_mutate__(self, max_punish):
        """
        if capacity punish exists, randomly add a charging station into the route
        if no capacity punish exists, nothing will be done
        :param max_punish: max capacity punish, use for normalization
        :return: None
        """
        if max_punish == 0:
            return
        for route in self.sequence:
            # add_p = (math.exp((route.capacity_punish / max_punish)) - 1) / (math.e - 1)
            if route.capacity_punish > 0:
                route.add_mutate()

    def __delete_station_mutate__(self, max_waste):
        """
        if too much capacity remain, randomly delete a charging station (if exists)
        :param max_waste: max capacity waste, use for normalization
        :return: None
        """
        for route in self.sequence:
            if not route.has_customer():
                self.sequence.remove(route)
        if max_waste < 0.05 * driving_range:
            return
        for route in self.sequence:
            # delete_p = (math.exp(route.capacity_remain / max_waste) - 1) / (math.e - 1)
            if not route.has_customer():
                self.sequence.remove(route)
            if route.capacity_waste > 0.05 * driving_range:
                route.delete_mutate()

    def __combine_mutate__(self):
        """
        if too much cargo not be delivered in route (i.e. too few customers are served), combine two
        note that combination is applying 'combine_try_time' times on the 'worst' route
        :return: None
        """
        self.sequence.sort(key=lambda x: x.served_w)
        route_list1 = self.sequence[:combine_try_time]
        random.shuffle(route_list1)  # introduce randomness
        self.sequence.sort(key=lambda x: x.served_v)
        route_list2 = self.sequence[:combine_try_time]
        random.shuffle(route_list2)
        for route1, route2 in zip(route_list1, route_list2):
            if route1.is_equal(route2) or \
                    (route1.served_v + route2.served_v > max_volume or route1.served_w + route2.served_w > max_weight):
                continue
            if route1 in self.sequence and route2 in self.sequence:
                self.sequence.remove(route1)
                self.sequence.remove(route2)
                if route1.served_v + route2.served_v < max_volume and route1.served_w + route2.served_w < max_weight:
                    self.sequence.append(self.__combine__(route1, route2))
                else:
                    new_route = self.__combine__(route1, route2)
                    new_routes = new_route.split_mutate()
                    if (len(new_routes) == 1 and new_routes[0].cost + vehicle_cost < route1.cost + route2.cost) \
                            or (len(new_routes) == 2 and new_routes[0].cost + new_routes[
                        1].cost < route1.cost + route2.cost):
                        self.sequence.extend(new_route.split_mutate())
                        self.sequence[-1].refresh_state()
                        self.sequence[-2].refresh_state()
                    else:
                        self.sequence.append(route1)
                        self.sequence.append(route2)
                    del new_route

    def __remove_route_mutate__(self):
        """
        try to remove the worst route, i.e. served_w and served_v is too little
        note that remove is applying 'insert_try_time' times on the 'worst' route
        :return: None
        """
        random.shuffle(self.sequence)  # introduce randomness
        for i in range(0, insert_try_time):
            bad_weight = random.random()
            invalid_sequence = []
            bad_route = min(self.sequence, key=lambda x: bad_weight * x.served_w + (1 - bad_weight) * x.served_v)
            self.sequence.remove(bad_route)
            for node in bad_route.sequence:
                success = False
                if node > custom_number:
                    invalid_sequence.append(node)
                    continue
                demand = self.g_map.get_demand(node)
                for route in self.sequence:
                    if demand[0] + route.served_w > max_weight or demand[1] + route.served_v > max_volume:
                        continue
                    if route.try_insert(node) != huge:
                        success = True
                        break
                if not success:
                    invalid_sequence.append(node)
            uninsert_customer = np.array(invalid_sequence)
            uninsert_customer = uninsert_customer[uninsert_customer <= custom_number]
            if len(uninsert_customer) != 0:
                self.sequence.append(Route(g_map=self.g_map, sequence=invalid_sequence, punish=self.punish))

    def __reschedule_mutate__(self):
        """
        reschedule a random route
        :return: None
        """
        mutate_pos = random.randint(0, len(self.sequence) - 1)
        self.sequence[mutate_pos].reschedule_mutate()

    def __random_reverse_mutate__(self):
        """
        add little perturbation to a random route
        :return: None
        """
        mutate_pos = random.randint(0, len(self.sequence) - 1)
        self.sequence[mutate_pos].random_reverse_mutate()

    def __combine__(self, route1: Route, route2: Route):
        """
        combine two routes, insert station if needed
        :param route1: route 1
        :param route2: route 2
        :return: route combined from route 1 and route 2
        """
        if sum(route1.get_mean_time_window()) > sum(route2.get_mean_time_window()):
            route1, route2 = route2, route1
        route_distance = self.g_map.get_distance(route1.sequence[-1], route2.sequence[0])
        if route1.capacity_remain + route2.capacity_remain - route_distance > driving_range:
            new_sequence = route1.sequence + route2.sequence
        else:
            new_station = self.g_map.get_nearby_station(route1.sequence[-1])
            new_sequence = route1.sequence.copy() + [new_station] + route2.sequence.copy()
        return Route(sequence=new_sequence, g_map=self.g_map, punish=self.punish)

    def deepcopy(self):
        r_sequence = []
        for route in self.sequence:
            r_sequence.append(route.deepcopy())
        return Chromo(sequence=r_sequence, g_map=self.g_map, punish=self.punish)

    def remove_duplicate(self):
        for route in self.sequence:
            if not route.has_customer():
                self.sequence.remove(route)
                continue
            idx = 0
            while True:
                if idx >= len(route.sequence) - 1:
                    break
                if route.sequence[idx] == route.sequence[idx + 1]:
                    route.sequence.pop(idx)
                    idx -= 1
                idx += 1

    def is_equal(self, chromo):
        if len(self.sequence) != len(chromo.sequence) or self.cost != chromo.cost:
            return False
        for route1, route2 in zip(self.sequence, chromo.sequence):
            if not route1.is_equal(route2):
                return False
        return True

    def get_custom_num(self):
        _sum = 0
        for route in self.sequence:
            temp = np.array(route.sequence)
            temp = temp[temp <= 1000]
            _sum += len(temp)
        return _sum

    def feasible_generate(self, node_sequence: List[int]):
        r_sequence: List[Route] = []
        random.shuffle(node_sequence)
        node_sequence = node_sequence.copy()
        capacity = driving_range
        weight, volume = max_weight, max_volume
        pre_node = center_id
        time = depot_open_time
        node_sequence = np.array(node_sequence)
        node_sequence = list(node_sequence[node_sequence <= custom_number])
        node = node_sequence.pop()
        n_sequence = [node]
        while node_sequence:
            if node <= custom_number:
                demand = self.g_map.get_demand(node)
                weight -= demand[0]
                volume -= demand[1]
                time = max(time + self.g_map.get_time(pre_node, node), self.g_map.get_window(node)[0]) + unload_time
                capacity -= self.g_map.get_distance(pre_node, node)
            else:
                time += self.g_map.get_time(pre_node, node) + charge_tm
                capacity = driving_range
            temp_feasible_list = []
            temp_feasible_score_list = []
            for new_node in node_sequence:
                c_condition = (self.g_map.get_distance(node, new_node)
                               + self.g_map.get_distance(new_node, self.g_map.get_nearby_station(new_node)) < capacity) \
                              or (self.g_map.get_distance(node, new_node)
                                  + self.g_map.get_distance(new_node, center_id) < capacity)
                new_demand = self.g_map.get_demand(new_node)
                d_condition = new_demand[0] < weight and new_demand[1] < volume
                t_condition = time + self.g_map.get_time(node, new_node) < self.g_map.get_window(new_node)[1]
                if c_condition and d_condition and t_condition:
                    temp_feasible_list.append(new_node)
                    para1, para2, para3 = random.random() + 0.15, random.random() + 0.15, random.random() + 0.2
                    temp_feasible_score_list.append(para1 * self.g_map.get_distance(node, new_node) / driving_range
                                                    + para2 * self.g_map.get_time(node, new_node)
                                                    + para3 * max(0, self.g_map.get_window(new_node)[0]
                                                                  - time - self.g_map.get_time(node, new_node)))
            if temp_feasible_list:
                temp_feasible_score_list = np.array(temp_feasible_score_list)
                best_feasible = temp_feasible_list[int(np.argmin(temp_feasible_score_list))]
                pre_node = node
                node = best_feasible
                node_sequence.remove(node)
                n_sequence.append(node)
            else:
                station = self.g_map.get_nearby_station(node)
                if node <= custom_number and self.g_map.get_distance(node, station) < capacity:
                    pre_node = node
                    node = station
                    n_sequence.append(node)
                else:
                    r_sequence.append(Route(g_map=self.g_map, punish=self.punish, sequence=n_sequence))
                    capacity = driving_range
                    weight, volume = max_weight, max_volume
                    pre_node = center_id
                    time = depot_open_time
                    node = node_sequence.pop()
                    n_sequence = [node]
        if n_sequence:
            r_sequence.append(Route(g_map=self.g_map, punish=self.punish, sequence=n_sequence))
        return r_sequence
