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

g_map = GlobalMap()
nature: Nature = pickle_load(save_dir)

best = nature.get_best()
_cost = best.cost
print(_cost)

r_sequence = []

for route in best.sequence:
    r_sequence.append(Route(g_map=g_map, sequence=route.sequence.copy()))

best = Chromo(g_map=g_map, sequence=r_sequence)
_cost = best.cost
print(_cost)
best.sequence.sort(key=lambda x: x.sequence[0])
for route in best.sequence[:10]:
    print(route.sequence)
print('__________')
sbest = nature.chromo_list[1]
sbest.sequence.sort(key=lambda x: x.sequence[0])
print(sbest.cost)
for route in sbest.sequence[:10]:
    print(route.sequence)
