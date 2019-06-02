from typing import List
import random
import copy

from PGA.chromo import Chromo

cross_p = 0.2


class Nature:
    chromo_list: List[Chromo]

    def __init__(self, chromo_list, chromo_num, g_map, new_chromo_num=1,
                 reserve=0.4, bad_reserve_p=0.1):
        self.chromo_list = chromo_list
        self.chromo_num = chromo_num
        self.max_idx = 0
        self.g_map = g_map
        self.new_chromo_num = new_chromo_num
        for i in range(0, len(self.chromo_list)):
            self.max_idx += 1
            self.chromo_list[i].idx = i
        self.__random_add__(num=chromo_num - len(self.chromo_list))
        if reserve + bad_reserve_p * (1 - reserve) >= 0.5:
            print('Chromo Num explode may occur. Chromo Reverse and Bad Chromo Reverse Probability reset to 0.3; 0.1.')
            reserve = 0.3
            bad_reserve_p = 0.1
        self.reserve = reserve
        self.bad_reserve_p = bad_reserve_p

    def operate(self):
        self.__random_add__(self.new_chromo_num)
        self.__ranking__()
        print('Ranking OK.', end='\t')
        bad_chromo_list = []
        for chromo in self.chromo_list[int(self.reserve * len(self.chromo_list)):]:
            if random.random() < self.bad_reserve_p:
                bad_chromo_list.append(chromo)
        self.chromo_list = self.chromo_list[:int(self.reserve * len(self.chromo_list))]
        self.chromo_list.extend(bad_chromo_list)
        old_chromo_list = copy.deepcopy(self.chromo_list)
        print('Select OK.', end='\t')
        chromo_copy1 = copy.deepcopy(self.chromo_list)
        chromo_copy2 = self.chromo_list[1:]
        chromo_copy2.append(self.chromo_list[0])
        self.chromo_list[:] = []
        for chromo1, chromo2 in zip(chromo_copy1, chromo_copy2):
            if random.random() < cross_p:
                chromo1_cross, chromo2_cross, r = self.__crossover__(chromo1, chromo2)
                if r == 1:
                    self.chromo_list.append(chromo1)
                    self.chromo_list.append(chromo2)
        print('Cross OK.', end='\t')
        self.__ranking__()
        for idx, chromo in enumerate(self.chromo_list):
            chromo.mutate()
        self.chromo_list.extend(old_chromo_list)
        print('Mutate OK.', end='\t')
        self.__random_add__(num=self.chromo_num - len(self.chromo_list))
        print('New Chromo Add OK.')

    def get_best(self):
        """
        return current best chromo/solution
        :return: best chromo
        """
        return min(self.chromo_list, key=lambda x: x.cost)

    def set_new_punish(self, new_punish):
        for chromo in self.chromo_list:
            chromo.set_punish_para(punish=new_punish)
            chromo.refresh_state()

    def __ranking__(self):
        """
        give rank to each chromo in chromo list and sort by rank
        :return: None
        """
        self.chromo_list.sort(key=lambda x: x.cost)
        '''for chromo in self.chromo_list:
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
                if cost <= cost_bound or vehicle_num <= vehicle_num_bound:
                    chromo.rank = rank
                    temp_list.remove(chromo)
        self.chromo_list.sort(key=lambda x: x.rank)'''

    @staticmethod
    def __crossover__(chromo1: Chromo, chromo2: Chromo):
        """
        operate cross over operation
        :param chromo1: the chromo to be crossed
        :param chromo2: the chromo to be crossed
        :return: None
        """
        sequence1 = []
        for route in chromo1.sequence:
            if not route.get_if_punish():
                sequence1.append(route)
        sequence2 = []
        for route in chromo2.sequence:
            if not route.get_if_punish():
                sequence2.append(route)
        if len(sequence1) == 0 or len(sequence2) == 0:
            return chromo1, chromo2, -1
        route1 = sequence1[random.randint(0, len(sequence1) - 1)]
        route2 = sequence2[random.randint(0, len(sequence2) - 1)]
        chromo1.clear(route2)
        chromo2.clear(route1)
        chromo1.sequence.append(route2)
        chromo2.sequence.append(route1)
        chromo1.refresh_state()
        chromo2.refresh_state()
        return chromo1, chromo2, 1

    def __hill_climbing__(self):
        pass

    def __random_add__(self, num: int):
        for i in range(0, num):
            self.chromo_list.append(Chromo(sequence=None, g_map=self.g_map, idx=self.max_idx))
            self.max_idx += 1
