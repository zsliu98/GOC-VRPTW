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

    def __init__(self, sequence, g_map, punish=9999):
        self.sequence = sequence
        self.g_map = g_map
        self.punish = punish
        self.start_time = depot_open_time
        self.cost = 0
        self.window_punish, self.capacity_punish, self.weight_punish,  self.volume_punish = 0, 0, 0, 0
        self.capacity_remain = 0
        self.served_w, self.served_v = 0, 0
        self.extra_t = 0
        self.refresh_state()

    def refresh_state(self, reset_window=True):
        """
        refresh state of this route
        :param reset_window: if time window is reset to the last serve time after time window punish
        :return:
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

    def set_punish(self, punish):
        self.punish = punish

    def delete_node(self, node: int):
        self.sequence.remove(node)
