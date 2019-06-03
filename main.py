import pandas as pd
import numpy as np
import pickle
from pympler import tracker, muppy, summary

from tools import GlobalMap, pickle_dump, pickle_load
from PGA import Nature
from PGA import Chromo
from PGA import Route

load = True
save = True  # warning: if save set to be true, it may save the 'nature' to save_dir, which is up to 100MB
generation_num = 100
chromo_num = 120
_punish = 9999
save_dir = 'data/nature.pkl'


def main():
    g_map = GlobalMap()
    '''
    route = Route(sequence=[371], g_map=g_map)
    print(g_map.get_distance(1,2))
    for node in range(0, 1101):
        print(g_map.get_nearby_station(node))
    '''
    if not load:
        nature = Nature(chromo_list=[], chromo_num=chromo_num, g_map=g_map, new_chromo_num=5)
    else:
        try:
            nature = pickle_load(save_dir)
        except FileNotFoundError or EOFError:
            print('No "nature" in given direction. New "nature" will be created.')
            nature = Nature(chromo_list=[], chromo_num=chromo_num, g_map=g_map, new_chromo_num=5)

    punish = _punish

    for generation in range(0, generation_num):
        print('Generation {} start.'.format(generation))
        nature.operate()
        best: Chromo = nature.get_best()
        print('Total {} Chromo.'.format(len(nature.chromo_list)))
        print('Best Cost: {}\tRoute Num: {}\tPunish Num: {}'.format(best.cost, len(best.sequence),
                                                                    best.has_punish_num()))
        #  this is memory watcher
        #  all_objects = muppy.get_objects()
        #  sum1 = summary.summarize(all_objects)
        #  summary.print_(sum1)
        if generation % 10 == 9:
            if save:
                pickle_dump(nature, file_path=save_dir)
            punish *= 1.1
            nature.set_new_punish(new_punish=punish)

    best_chromo: Chromo = nature.get_best()
    for route in best_chromo.sequence:
        print(route.sequence)


if __name__ == '__main__':
    main()
