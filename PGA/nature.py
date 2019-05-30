from PGA.chromo import Chromo


class Nature:
    chromo_list: list

    def __init__(self, chromo_list):
        self.chromo_list = chromo_list

    def ranking(self):
        """
        give rank to each chromo in chromo list and sort by rank
        :return: None
        """
        # self.chromo_list.sort(key=lambda x: x.cost)
        for chromo in self.chromo_list:
            chromo.reset_rank()
        temp_list = self.chromo_list.copy()
        while temp_list:
            cost_min = 1e10
            cost_bound = 0
            vehicle_num_min = 1e5
            vehicle_num_bound = 0
            rank = 0
            for chromo in temp_list:
                cost, vehicle_num = chromo.get_score()
                if cost < cost_min:
                    cost_min = cost
                    vehicle_num_bound = vehicle_num
                if vehicle_num < vehicle_num_min:
                    vehicle_num_min = vehicle_num
                    cost_bound = cost
            for chromo in temp_list:
                cost, vehicle_num = chromo.get_score()
                if cost < cost_bound or vehicle_num < vehicle_num_bound:
                    chromo.rank = rank
                    temp_list.remove(chromo)
        self.chromo_list.sort(key=lambda x: x.rank)

