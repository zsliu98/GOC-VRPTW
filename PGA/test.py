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
save_dir = 'data/nature9.pkl'

g_map = GlobalMap()
nature: Nature = pickle_load(save_dir)

best = nature.get_best()
_cost = best.cost
print(_cost)

print(best.get_custom_num())
best.__remove_route_mutate__()
print(best.get_custom_num())
