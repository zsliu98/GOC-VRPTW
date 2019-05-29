from tools import GlobalMap

center_id = 0
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
        self.served_w = 0
        self.served_v = 0
        self.extra_t = 0
        self.refresh_cost()

    def refresh_cost(self, reset_window=True):
        self.start_time = depot_open_time
        self.cost = 0
        self.served_w = 0
        self.served_v = 0
        self.extra_t = 0
        time = depot_open_time
        distance = 0
        capacity = driving_range
        volume = max_volume
        weight = max_weight
        pre_node = 0
        extra_time = []
        for node in self.sequence:
            d = self.g_map.get_distance(pre_node, node)
            t = self.g_map.get_time(pre_node, node)
            capacity -= d
            if node > 1000:
                time += t + charge_tm
                distance += d
                self.cost += charge_cost + unit_trans_cost * d  # regular cost
                self.cost += self.punish * capacity if capacity < 0 else 0  # battery capacity punish
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
                    self.cost += self.punish * (time - window[1])  # time window punish
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
                self.cost += self.punish * abs(weight) if weight < 0 else 0  # weight negative punish
                self.cost += self.punish * abs(volume) if volume < 0 else 0  # volume negative punish
                self.cost += self.punish * abs(capacity) if capacity < 0 else 0  # battery capacity punish
        d = self.g_map.get_distance(pre_node, center_id)
        t = self.g_map.get_time(pre_node, center_id)
        capacity -= d
        time += t
        self.cost += unit_trans_cost * d  # regular cost
        self.cost += self.punish * capacity if capacity < 0 else 0  # battery capacity punish
        if time > 24.:  # time window self.punish
            self.cost += self.punish * abs(time - 24.)
            extra_time.append(1)
        else:
            extra_time.append(24. - time)
        self.extra_t = max(0, min(extra_time))
        self.cost -= len(extra_time) * self.extra_t * wait_cost  # reduce wait cost
        self.start_time += self.extra_t
