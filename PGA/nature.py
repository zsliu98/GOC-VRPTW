from typing import List
import random
import numpy as np

from PGA.chromo import Chromo
import PGA.constant as const

cross_p = const.cross_p
feasible_generate_p = const.feasible_generate_p


class Nature:
    chromo_list: List[Chromo]

    def __init__(self, chromo_list, chromo_num, g_map, new_chromo_num=10,
                 reserve=0.4, bad_reserve_p=0.1, punish=9999):
        """
        :param chromo_list: chromo in this nature
        :param chromo_num: the number of chromo in this nature
        :param g_map: global map
        :param new_chromo_num: the number of chromo add to this route each operation
        :param reserve:
        :param bad_reserve_p: the probability of reserve bad chromo
        """
        self.chromo_list = chromo_list
        self.chromo_num = chromo_num
        self.max_idx = 0
        self.g_map = g_map
        self.new_chromo_num = new_chromo_num
        self.punish = punish
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
        """
        operate the nature, include rank, select, cross, mutate, new add, experience apply
        :return: None
        """
        self.__ranking__()
        print('Ranking OK.', end='\t')
        bad_chromo_list = []
        for chromo in self.chromo_list[int(self.reserve * len(self.chromo_list)):]:
            if random.random() < self.bad_reserve_p:
                bad_chromo_list.append(chromo)
        self.chromo_list = self.chromo_list[:int(self.reserve * len(self.chromo_list))]
        self.chromo_list.extend(bad_chromo_list)
        print('Select OK {}.'.format(len(self.chromo_list)), end='\t')
        self.__random_add__(self.new_chromo_num)
        print('New Chromo Add OK {}.'.format(self.new_chromo_num), end='\t')
        old_chromo_list = []
        for chromo in self.chromo_list:
            old_chromo_list.append(chromo.deepcopy())
        chromo_copy1 = self.chromo_list[::2]
        chromo_copy2 = self.chromo_list[1::2]
        random.shuffle(chromo_copy2)
        if len(chromo_copy2) < len(chromo_copy1):
            chromo_copy1.pop()
        for chromo1, chromo2 in zip(chromo_copy1, chromo_copy2):
            if random.random() < cross_p:
                chromo1_cross, chromo2_cross, r = self.__crossover__(chromo1, chromo2)
                if r == 1:
                    self.chromo_list.append(chromo1)
                    self.chromo_list.append(chromo2)
        print('Cross OK {}.'.format(len(self.chromo_list)), end='\t')
        del chromo_copy1
        del chromo_copy2
        for chromo in old_chromo_list:
            self.chromo_list.append(chromo.deepcopy())
        for idx, chromo in enumerate(self.chromo_list):
            chromo.mutate()
        self.chromo_list.extend(old_chromo_list)
        del old_chromo_list
        print('Mutate OK.', end='\t')
        add_num = self.chromo_num - len(self.chromo_list)
        self.__random_add__(num=add_num)

        self.__experience_apply__()
        print('Experience Apply OK.', end='\t')
        print('Total {} Chromo.'.format(len(self.chromo_list)))
        self.__ranking__()
        self.chromo_list = self.chromo_list[:self.chromo_num]

    def get_best(self):
        """
        return current best chromo/solution
        :return: best chromo
        """
        return min(self.chromo_list, key=lambda x: x.cost)

    def set_punish_para(self, punish):
        self.punish = punish
        for chromo in self.chromo_list:
            chromo.set_punish_para(punish=punish)

    def __ranking__(self):
        """
        give rank to each chromo in chromo list and sort by rank
        :return: None
        """
        for chromo in self.chromo_list:
            chromo.refresh_state()
        self.chromo_list.sort(key=lambda x: x.cost)

    @staticmethod
    def __crossover__(chromo1: Chromo, chromo2: Chromo):
        """
        operate cross over operation
        :param chromo1: the chromo to be crossed
        :param chromo2: the chromo to be crossed
        :return: None
        """
        chromo1 = chromo1.deepcopy()
        chromo2 = chromo2.deepcopy()
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
        random_weight = random.random()
        route1 = max(sequence1, key=lambda x: random_weight * x.served_w + (1 - random_weight) * x.served_v).deepcopy()
        route2 = max(sequence2, key=lambda x: random_weight * x.served_w + (1 - random_weight) * x.served_v).deepcopy()
        # route1 = sequence1[random.randint(0, len(sequence1) - 1)].deepcopy()
        # route2 = sequence2[random.randint(0, len(sequence2) - 1)].deepcopy()
        chromo1.clear(route2)
        chromo2.clear(route1)
        chromo1.sequence.append(route2)
        chromo2.sequence.append(route1)
        chromo1.refresh_state()
        chromo2.refresh_state()
        return chromo1, chromo2, 1

    def __hill_climbing__(self):
        pass

    def __experience_apply__(self):
        """
        apply experience on all chromo, include remove duplicate in single chromo and among chromo
        :return:
        """
        for chromo in self.chromo_list:
            chromo.remove_duplicate()
            chromo.sequence.sort(key=lambda route: route.sequence[0])
        self.__ranking__()
        idx = 0
        while idx < len(self.chromo_list) - 1:
            if self.chromo_list[idx].is_equal(self.chromo_list[idx + 1]):
                self.chromo_list.pop(idx)
                idx -= 1
            idx += 1

    def __random_add__(self, num: int):
        """
        random add num of chromo in this nature
        :param num: the number of new chromo
        :return: None
        """
        for i in range(0, int(num * feasible_generate_p)):
            self.chromo_list.append(Chromo(sequence=None, g_map=self.g_map, idx=self.max_idx,
                                           punish=self.punish, feasible_flag=True))
            self.max_idx += 1
        for i in range(int(num * feasible_generate_p), num):
            self.chromo_list.append(Chromo(sequence=None, g_map=self.g_map, idx=self.max_idx,
                                           punish=self.punish, feasible_flag=False))
            self.max_idx += 1
