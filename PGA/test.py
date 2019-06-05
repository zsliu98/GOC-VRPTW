from tools import GlobalMap, pickle_dump, pickle_load
from PGA import Nature
from PGA import Chromo
from PGA import Route

import numpy as np

load = True
save = True  # warning: if save set to be true, it may save the 'nature' to save_dir, which is up to 100MB
generation_num = 500
chromo_num = 50
_punish = 99999
save_dir = 'data/nature.pkl'

# nature: Nature = pickle_load(save_dir)

g_map = GlobalMap()

chromo1 = Chromo(sequence=None, g_map=g_map)
chromo2 = chromo1.deepcopy()

print(chromo1.get_custom_num())
print(chromo2.get_custom_num())

print(chromo1.get_custom_num())
print(chromo2.get_custom_num())

nature = Nature(g_map=g_map, chromo_list=[chromo1, chromo2], chromo_num=2)

chromo3, chromo4, r = nature.__crossover__(chromo1, chromo2)
chromo1.sequence.pop()
print(chromo1.get_custom_num())
print(chromo2.get_custom_num())
print(chromo3.get_custom_num())
print(chromo4.get_custom_num())
