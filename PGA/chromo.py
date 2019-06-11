from typing import List
import numpy as np
import random
import math

from tools import GlobalMap
from PGA.route import Route
import PGA.constant as const

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
random_mutate_p = const.random_mutate_p
inter_change_p = const.inter_change_p
remove_mutate_p = const.remove_mutate_p
perturb_generate_p = const.perturb_generate_p
restart_p = const.restart_p

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
        mutate the chromo, include: split, add, delete, remove, restart, random reverse, interchange
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
        if random.random() < remove_mutate_p:
            self.__remove_route_mutate__()
        else:
            self.__restart_mutate__()
        if random.random() < inter_change_p:
            self.__inter_change__()
        else:
            self.__random_reverse_mutate__()

    def has_punish_num(self):
        """
        calculate how many routes have punishment
        :return: number of routes have punishment, and all its punishment
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
        weight_punish /= self.punish
        volume_punish /= self.punish
        window_punish /= self.punish
        capacity_punish /= self.punish
        return num, weight_punish, volume_punish, window_punish, capacity_punish

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
            if not route.has_customer():
                self.sequence.remove(route)
            if route.capacity_waste > 0.05 * driving_range:
                route.delete_mutate()

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

    def __random_reverse_mutate__(self):
        """
        add little perturbation to a random route
        :return: None
        """
        mutate_pos = random.randint(0, len(self.sequence) - 1)
        self.sequence[mutate_pos].random_reverse_mutate()

    def __inter_change__(self):
        """
        inter change two near nodes in chromo
        :return: None
        """
        node1 = -1
        route1 = None
        random.shuffle(self.sequence)
        for route in self.sequence:
            temp_sequence = route.sequence.copy()
            random.shuffle(temp_sequence)
            for node in temp_sequence:
                if self.g_map.get_nearby_custom(node) != -1:
                    node1 = node
                    route1 = route
                    break
            if node1 != -1:
                break
        node2 = self.g_map.get_nearby_custom(node1)
        route2 = None
        for route in self.sequence:
            if node2 in route.sequence:
                route2 = route
                break
        route1.sequence[route1.sequence.index(node1)] = node2
        route2.sequence[route2.sequence.index(node2)] = node1

    def __restart_mutate__(self):
        """
        split a route into two routes by a station in this route if lower distance cost
        :return: None
        """
        random_flag = random.random() < 0.5
        for route in self.sequence:
            if random.random() < 0.5:
                continue
            for i in range(1, len(route.sequence) - 1):
                pre_node = route.sequence[i - 1]
                node = route.sequence[i]
                succ_node = route.sequence[i + 1]
                d1 = self.g_map.get_distance(pre_node, node) + self.g_map.get_distance(node, succ_node)
                d2 = self.g_map.get_distance(pre_node, center_id) + self.g_map.get_distance(center_id, node)
                if node > custom_number and (d1 > d2 or (random.random() < restart_p and random_flag)):
                    self.sequence.remove(route)
                    self.sequence.append(Route(g_map=self.g_map, punish=self.punish, sequence=route.sequence[:i]))
                    self.sequence.append(Route(g_map=self.g_map, punish=self.punish, sequence=route.sequence[i + 1:]))
                    break

    def deepcopy(self):
        """
        return a deep copy of itself, copy all except g_map
        :return: copy chromo
        """
        r_sequence = []
        for route in self.sequence:
            r_sequence.append(route.deepcopy())
        return Chromo(sequence=r_sequence, g_map=self.g_map, punish=self.punish)

    def remove_duplicate(self):
        """
        remove route which doesn't have customers, also remove duplicate stations
        :return: None
        """
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
        """
        examine whether this chromo is equal to another chromo
        :param chromo: another chromo
        :return: True if equal
        """
        if len(self.sequence) != len(chromo.sequence) or self.cost != chromo.cost:
            return False
        for route1, route2 in zip(self.sequence, chromo.sequence):
            if not route1.is_equal(route2):
                return False
        return True

    def get_custom_num(self):
        """
        get how the number of customers in this chromo, should be equal to 'custom_number'
        :return: custom_number in this chromo
        """
        _sum = 0
        for route in self.sequence:
            temp = np.array(route.sequence)
            temp = temp[temp <= 1000]
            _sum += len(temp)
        return _sum

    def feasible_generate(self, node_sequence: List[int]):
        """
        generate a feasible route list to serve all given nodes
        :param node_sequence: nodes need to be served
        :return: route list
        """
        r_sequence: List[Route] = []
        random.shuffle(node_sequence)
        node_sequence = node_sequence.copy()
        capacity = driving_range
        weight, volume = max_weight, max_volume
        pre_node = center_id
        time = depot_open_time
        node_sequence = np.array(node_sequence)
        para1, para2, para3 = random.random() * 4 + 2, random.random() * 1 + 0.25, random.random() * 3 + 0.75
        node_sequence = list(node_sequence[node_sequence <= custom_number])
        node_sequence.sort(reverse=True, key=lambda x: para1 * self.g_map.get_distance(center_id, x) / driving_range
                                                       + para2 * (self.g_map.get_window(x)[0] - time)
                                                       + para3 * (self.g_map.get_window(x)[1] - time))
        for i in range(1, len(node_sequence)):
            if random.random() < perturb_generate_p:
                node_sequence[i - 1], node_sequence[i] = node_sequence[i], node_sequence[i - 1]
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
                               + self.g_map.get_distance(new_node, self.g_map.get_nearby_station(new_node)) < capacity)\
                              or (self.g_map.get_distance(node, new_node)
                                  + self.g_map.get_distance(new_node, center_id) < capacity)
                new_demand = self.g_map.get_demand(new_node)
                d_condition = new_demand[0] < weight and new_demand[1] < volume
                t_condition = time + self.g_map.get_time(node, new_node) < self.g_map.get_window(new_node)[1]
                if c_condition and d_condition and t_condition:
                    temp_feasible_list.append(new_node)
                    para1, para2, para3 = random.random() * 2 + 1.5, random.random() * 0.5 + 0.25, random.random() * 1.5 + 0.75
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
