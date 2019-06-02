from typing import List
import random
import numpy as np

from tools import GlobalMap

center_id = 0
custom_number = 1000
station_number = 100

max_volume = 16
max_weight = 2.5
unload_time = 0.5
driving_range = 120000
charge_tm = 0.5
charge_cost = 50
wait_cost = 24
depot_open_time = 16.
unit_trans_cost = 14. / 1000


class Route:
    g_map: GlobalMap
    sequence: List[int]

    def __init__(self, sequence, g_map, punish=9999, refresh_im=True):
        self.sequence = sequence
        self.g_map = g_map
        self.punish = punish
        self.start_time = depot_open_time
        self.cost = 0
        self.window_punish, self.capacity_punish, self.weight_punish, self.volume_punish = 0, 0, 0, 0
        self.capacity_remain = 0
        self.served_w, self.served_v = 0, 0
        self.extra_t = 0
        if refresh_im:
            self.refresh_state()

    def refresh_state(self, reset_window=True):
        """
        refresh state of this route
        :param reset_window: if time window is reset to the last serve time after time window punish
        :return: None
        """
        self.start_time = depot_open_time
        self.cost = 0
        self.window_punish, self.capacity_punish, self.weight_punish, self.volume_punish = 0, 0, 0, 0
        self.capacity_remain = 0
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
                self.capacity_punish += self.punish * capacity / driving_range if capacity < 0 else 0
                capacity = driving_range  # recharge battery
            else:
                self.cost += unit_trans_cost * d  # regular cost
                time += t
                window = self.g_map.get_window(node)
                if time < window[0]:
                    self.cost += wait_cost * (window[0] - time)  # waiting cost
                    extra_time.append(window[1] - time)
                    time = window[0]
                elif time > window[1]:
                    self.window_punish += self.punish * (time - window[1])
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
        self.capacity_punish += self.punish * capacity if capacity < 0 else 0
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
        first_tm = [self.g_map.get_window(x)[0] for x in self.sequence]
        last_tm = [self.g_map.get_window(x)[1] for x in self.sequence]
        return sum(first_tm) / len(first_tm), sum(last_tm) / len(last_tm)

    def split_mutate(self, p=0.618):
        sequence1 = []
        sequence2 = []
        for node in self.sequence:
            if random.random() < p:
                sequence1.append(node)
            else:
                sequence2.append(node)
        route1 = Route(sequence=sequence1, g_map=self.g_map, punish=self.punish)
        route2 = Route(sequence=sequence2, g_map=self.g_map, punish=self.punish)
        return route1, route2

    def add_mutate(self):
        add_pos = random.randint(int(len(self.sequence) / 4), int(len(self.sequence) * 3 / 4))
        station = self.g_map.get_nearby_station(self.sequence[add_pos - 1])
        self.sequence.insert(add_pos, station)

    def delete_mutate(self):
        temp_sequence = np.array(self.sequence)
        temp_sequence = temp_sequence[temp_sequence > custom_number]
        delete_pos = random.randint(0, len(temp_sequence) - 1)
        self.sequence.remove(int(temp_sequence[delete_pos]))

    def random_mutate(self):
        pos1 = random.randint(0, len(self.sequence) - 1)
        pos2 = random.randint(0, len(self.sequence) - 1)
        if pos1 == pos2:
            return
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1
        self.sequence = self.sequence[:pos1] + [self.sequence[pos2]] + self.sequence[pos1 + 1:pos2] \
            + [self.sequence[pos1]] + self.sequence[pos2 + 1:]

