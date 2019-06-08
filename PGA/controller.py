from typing import List
from multiprocessing import Process

from tools import pickle_dump, pickle_load, GlobalMap
from PGA.nature import Nature


class Controller:
    nature_list: List[Nature]

    def __init__(self, nature_num, chromo_num, g_map, new_chromo_num=5, punish=9999, save_dir='data', read_dir='data'):
        self.nature_list = []
        self.punish = punish
        self.nature_num = nature_num
        self.chromo_sum = chromo_num
        self.g_map = g_map
        self.new_chromo_num = new_chromo_num
        self.punish = punish
        self.save_dir = save_dir
        self.read_dir = read_dir
        print('Controller OK.')

    def operate(self):
        self.nature_list[:] = []
        process_list = []
        for i in range(0, self.nature_num):
            process_list.append(NatureProcess(idx=i, save_dir=self.save_dir, read_dir=self.read_dir,
                                              chromo_num=self.chromo_sum, new_chromo_num=self.new_chromo_num,
                                              punish=self.punish))
        for nature_process in process_list:
            nature_process.start()
        for nature_process in process_list:
            nature_process.join()
        for i in range(0, self.nature_num):
            nature = pickle_load(self.save_dir + '/nature' + str(i) + '.pkl')
            self.nature_list.append(nature)
        for nature in self.nature_list:
            nature.g_map = self.g_map
            for chromo in nature.chromo_list:
                chromo.g_map = self.g_map
                for route in chromo.sequence:
                    route.g_map = self.g_map
        self.__migrate__()
        for i, nature in enumerate(self.nature_list):
            pickle_dump(nature, self.save_dir + '/nature' + str(i) + '.pkl')

    def set_punish(self, punish):
        self.punish = punish
        for nature in self.nature_list:
            nature.set_punish_para(punish=punish)
        for i, nature in enumerate(self.nature_list):
            pickle_dump(nature, self.save_dir + '/nature' + str(i) + '.pkl')

    def __migrate__(self):
        for idx in range(1, len(self.nature_list)):
            self.nature_list[idx - 1].chromo_list.append(self.nature_list[idx].chromo_list[0].deepcopy())
        self.nature_list[-1].chromo_list.append(self.nature_list[0].chromo_list[0].deepcopy())

    def get_best(self):
        best_list = [nature.get_best() for nature in self.nature_list]
        return min(best_list, key=lambda chromo: chromo.cost)


class NatureProcess(Process):

    def __init__(self, idx, save_dir, read_dir, chromo_num, new_chromo_num, punish=9999):
        super(NatureProcess, self).__init__()
        self.idx = idx
        self.save_dir = save_dir + '/nature' + str(idx) + '.pkl'
        self.read_dir = read_dir
        self.chromo_num = chromo_num
        self.new_chromo_num = new_chromo_num
        self.punish = punish

    def run(self) -> None:
        try:
            nature: Nature = pickle_load(self.save_dir)
            nature.set_punish_para(punish=self.punish)
        except FileNotFoundError:
            print('No "nature{}" in given direction. New "nature" will be created.'.format(self.idx))
            nature: Nature = Nature(chromo_list=[], chromo_num=self.chromo_num, g_map=GlobalMap(self.read_dir),
                                    new_chromo_num=self.new_chromo_num, punish=self.punish)
        nature.operate()
        pickle_dump(nature, self.save_dir)
