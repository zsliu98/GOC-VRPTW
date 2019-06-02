from typing import List
import random
import math

from tools import GlobalMap
from PGA.route import Route

center_id = 0
custom_number = 1000
station_number = 100
random_add_station = 2

max_volume = 16
max_weight = 2.5
starve_para = 0.25
unload_time = 0.5
driving_range = 120000
charge_tm = 0.5
charge_cost = 50
wait_cost = 24
depot_wait = 1
depot_open_time = 16.
unit_trans_cost = 14. / 1000
vehicle_cost = 300


class Chromo:
    g_map: GlobalMap
    sequence: List[Route]

    def __init__(self, sequence=None, g_map=None, idx=0, punish=9999, reset_window=True):
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
            self.__random_init__()
        self.refresh_state()

    def refresh_state(self):
        """
        refresh state of this chromo
        :return: None
        """
        self.cost = 0
        self.vehicle_number = len(self.sequence)
        start_list = [depot_open_time]
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

    def __random_init__(self):
        """
        random init this chromo by some prior experience (when no data is given)
        :return: None
        """
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
                    temp_route.append(self.g_map.get_nearby_station(node))
                    temp_route.append(node)
                    capacity += self.g_map.get_distance(pre_node, node)
                    capacity -= self.g_map.get_distance(next_station, node)
                    pre_node = node
                else:
                    self.sequence.append(Route(sequence=temp_route, g_map=self.g_map, punish=self.punish))
                    capacity = driving_range
                    weight, volume = max_weight, max_volume
                    temp_route = []
                    pre_node = center_id
            else:
                temp_route.append(node)
                pre_node = node

    def set_punish_para(self, punish):
        self.punish = punish
        for route in self.sequence:
            route.set_punish_para(punish)

    def clear(self, route: Route):
        """
        clear all node in the given route to prepare for the route insert
        :param route: the route going to be inserted
        :return: None
        """
        clear_list = route.sequence
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
        max_s = max(self.sequence, lambda x: x.window_punish + x.weight_punish + x.volume_punish)
        max_s_punish = max_s.window_punish + max_s.weight_punish + max_s.volume_punish
        max_a_punish = max(self.sequence, lambda x: x.capacity_punish).capacity_punish
        max_d_remain = max(self.sequence, lambda x: x.capacity_remain).capacity_remain
        self.__split_mutate__(max_s_punish)
        self.__add_mutate__(max_a_punish)
        self.__delete_mutate__(max_d_remain)
        self.__combine_mutate__()
        self.__random_mutate__()

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
            split_p = (math.exp((route.window_punish + route.weight_punish + route.volume_punish) / max_punish) - 1) / (
                    math.e - 1)
            if random.random() < split_p:
                new_routes = route.split_mutate()
                self.sequence.remove(route)
                del route
                self.sequence.extend(new_routes)

    def __add_mutate__(self, max_punish):
        """
        if capacity punish exists, randomly add a charging station into the route
        if no capacity punish exists, nothing will be done
        :param max_punish: max capacity punish, use for normalization
        :return: None
        """
        if max_punish == 0:
            return
        for route in self.sequence:
            add_p = (math.exp(route.capacity_punish / max_punish) - 1) / (math.e - 1)
            if random.random() < add_p:
                route.add_mutate()

    def __delete_mutate__(self, max_remain):
        """
        if too much capacity remain, randomly delete a charging station (if exists)
        :param max_remain: max capacity remain, use for normalization
        :return: None
        """
        if max_remain < 0.1 * driving_range:
            return
        for route in self.sequence:
            add_p = (math.exp(route.capacity_remain / max_remain) - 1) / (math.e - 1)
            if random.random() < add_p:
                route.delete_mutate()

    def __combine_mutate__(self):
        """
        if too much cargo not be delivered in route (i.e. too few customers are served), combine two
        :return: None
        """
        route1 = min(self.sequence, key=lambda x: x.served_w)
        self.sequence.remove(route1)
        route2 = min(self.sequence, key=lambda x: x.served_v)
        self.sequence.remove(route2)
        if route1.served_v + route2.served_v < max_volume and route1.served_w + route2.served_w < max_weight:
            self.sequence.append(self.__combine__(route1, route2))
            self.sequence[-1].refresh_state()
        else:
            new_route = self.__combine__(route1, route2)
            self.sequence.extend(new_route.split_mutate())
            del new_route
        del route1
        del route2

    def __random_mutate__(self):
        """
        add little perturbation to route
        :return: None
        """
        mutate_pos = random.randint(0, len(self.sequence) - 1)
        self.sequence[mutate_pos].random_mutate()

    def __combine__(self, route1: Route, route2: Route):
        if sum(route1.get_mean_time_window()) > sum(route2.get_mean_time_window()):
            route1, route2 = route2, route1
        route_distance = self.g_map.get_distance(route1.sequence[-1], route2.sequence[0])
        if route1.capacity_remain + route2.capacity_remain - route_distance > driving_range:
            new_sequence = route1.sequence + route2.sequence
        else:
            new_station = self.g_map.get_nearby_station(route1.sequence[-1])
            new_sequence = route1.sequence + [new_station] + route2.sequence
        return Route(sequence=new_sequence, g_map=self.g_map, punish=self.punish, refresh_im=False)
