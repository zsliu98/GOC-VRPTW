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

nature: Nature = pickle_load(save_dir)

best: Chromo = nature.get_best()

print(best.get_custom_num())

for route in best.sequence:
    print(route.window_punish, route.sequence)

# _map = GlobalMap()
