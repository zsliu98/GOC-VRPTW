from tools import GlobalMap
from PGA.route import Route

center_id = 0
max_volume = 16
max_weight = 2.5
unload_time = 0.5
driving_range = 120000
charge_tm = 0.5
charge_cost = 50
wait_cost = 24
depot_wait = 1
depot_open_time = 16.  # suppose first vehicle start at 8:00
unit_trans_cost = 14. / 1000
vehicle_cost = 300


class Chromo:
    g_map: GlobalMap

    def __init__(self, sequence, g_map, idx=0, punish=9999, reset_window=True):
        self.idx = idx
        self.g_map = g_map
        self.sequence = sequence
        self.punish = punish
        self.reset_window = reset_window
        self.cost = 0
        self.vehicle_number = 0
        self.refresh_cost()

    def refresh_cost(self):
        self.cost = 0
        self.vehicle_number = len(self.sequence)
        start_list = [depot_open_time]
        for route in self.sequence:
            assert isinstance(route, Route)
            self.cost += route.cost  # pure route cost
            self.cost += vehicle_cost  # new vehicle cost
            start_list.append(route.start_time)  # record each route start time
        # reuse some vehicles
        start_list.sort()
        pos_1 = 0
        pos_2 = 0
        while pos_2 < len(start_list):
            if start_list[pos_2] - start_list[pos_1] >= depot_wait:
                self.cost += depot_wait * wait_cost - vehicle_cost  # replace new-vehicle cost as wait cost
                pos_1 += 1
                self.vehicle_number -= 1
            pos_2 += 1

    def get_fitness(self):
        return 1 / self.cost

    def get_ranking(self):
        return self.cost - self.vehicle_number * vehicle_cost, self.vehicle_number
