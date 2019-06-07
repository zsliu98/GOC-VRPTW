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
chromo = Chromo(sequence=None, g_map=g_map)
f_chromo = Chromo(sequence=chromo.feasible_generate(node_sequence=list(range(1, 1001))), g_map=g_map)
print(f_chromo.cost)
print(f_chromo.has_punish_num())

'''
nature: Nature = pickle_load(save_dir)

best: Chromo = nature.get_best()

print(best.get_custom_num())

for idx, route in enumerate(best.sequence):
    if route.window_punish != 0 or route.capacity_punish != 0:
        print(route.window_punish, route.capacity_punish, idx, route.sequence)

print(best.cost - best.punish * sum(best.has_punish_num()[1:]))
print(best.sequence[110].capacity_remain)
best.sequence[110].delete_mutate()
print("____________")

print(best.vehicle_number)
print(len(best.sequence))
'''
'''for idx, route in enumerate(best.sequence):
    print(idx, route.sequence)

# _map = GlobalMap()'''
