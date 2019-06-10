from tools import GlobalMap, pickle_dump, pickle_load
from PGA import Controller
from PGA import Nature
from PGA import Chromo
from PGA import Route

import numpy as np

generation_num = 500
chromo_num = 50
_punish = 99999
save_dir = 'data/controller.pkl'

controller: Controller = pickle_load(save_dir)

best = controller.get_best()
_cost = best.cost
print(_cost)

for route in best.sequence:
    print("served_w:{0:.5f}, served_v:{1:.5f}, start_tm:{2:.5f}, capacity_waste:{3:.5f}".format(route.served_w, route.served_v, route.start_time, max(route.capacity_waste, route.capacity_remain)), route.sequence)
print(best.get_custom_num())
'''
g_map = GlobalMap()
for i in range(1, 1001):
    print(i, g_map.get_nearby_custom(i))'''
