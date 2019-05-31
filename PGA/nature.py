from typing import List
import random

from PGA.chromo import Chromo


class Nature:
    chromo_list: List[Chromo]

    def __init__(self, chromo_list, chromo_num, g_map=None, new_chromo_num=1, punish_increase=1.1):
        self.chromo_list = chromo_list
        self.chromo_num = chromo_num
        self.max_idx = 0
        self.g_map = g_map
        self.new_chromo_num = new_chromo_num
        self.punish_increase = punish_increase
        for i in range(0, len(self.chromo_list)):
            self.max_idx += 1
            self.chromo_list[i].idx = i
        self.__random_add__(num=chromo_num - len(self.chromo_list))

    def operate(self):
        self.__random_add__(self.new_chromo_num)
        new_punish = self.chromo_list[0].punish * self.punish_increase
        for chromo in self.chromo_list:
            chromo.set_punish(punish=new_punish)
            chromo.refresh_state()

    def __ranking__(self):
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

    @staticmethod
    def crossover(chromo1: Chromo, chromo2: Chromo):
        """
        operate cross over operation
        :param chromo1: the chromo to be crossed
        :param chromo2: the chromo to be crossed
        :return: None
        """
        route1 = chromo1.sequence[random.randint(0, len(chromo1.sequence) - 1)]
        route2 = chromo2.sequence[random.randint(0, len(chromo2.sequence) - 1)]
        chromo1.clear(route1)
        chromo2.clear(route2)
        chromo1.sequence.append(route2)
        chromo2.sequence.append(route1)
        chromo1.refresh_state()
        chromo2.refresh_state()

    def hill_climbing(self):
        pass

    def get_best(self):
        return min(self.chromo_list, key=lambda x: x.cost)

    def __random_add__(self, num: int):
        for i in range(0, num):
            self.chromo_list.append(Chromo(sequence=None, g_map=self.g_map, idx=self.max_idx))
            self.max_idx += 1
