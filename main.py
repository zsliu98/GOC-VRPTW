import pandas as pd
import numpy as np
import pickle

from tools import GlobalMap
from PGA import Nature
from PGA import Chromo

generation_num = 20
chromo_num = 100
save_dir = 'data/nature.pkl'


def main():
    g_map = GlobalMap()
    nature = Nature(chromo_list=[], chromo_num=chromo_num, g_map=g_map, new_chromo_num=5)
    for generation in range(0, generation_num):
        print('Generation {} start.'.format(generation))
        nature.operate()
        file = open(save_dir, 'wb')
        pickle.dump(nature, file)
        file.close()
        best_cost = nature.get_best().cost
        print('Best Cost: {}'.format(best_cost))
    best_chromo = nature.get_best()
    for route in best_chromo.sequence:
        print(route.sequence)


if __name__ == '__main__':
    main()
