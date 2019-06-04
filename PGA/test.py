from tools import GlobalMap, pickle_dump, pickle_load
from PGA import Nature
from PGA import Chromo
from PGA import Route

load = True
save = True  # warning: if save set to be true, it may save the 'nature' to save_dir, which is up to 100MB
generation_num = 500
chromo_num = 50
_punish = 99999
save_dir = 'data/nature.pkl'

nature: Nature = pickle_load(save_dir)

best: Chromo = nature.get_best()

print(best.cost)

print(best.has_punish_num())
print(best.vehicle_number)
print(best.cost - best.punish * (best.has_punish_num()[3] + best.has_punish_num()[4]))

for route in best.sequence:
    idx = 0
    while True:
        if idx >= len(route.sequence) - 1:
            break
        if route.sequence[idx] == route.sequence[idx + 1] \
                or (route.sequence[idx] >= 1000 and route.sequence[idx + 1] >= 1000):
            route.sequence.pop(idx)
            idx -= 1
        idx += 1

best.refresh_state()

print(best.cost)

print(best.has_punish_num())

print(best.vehicle_number)
print(best.cost - best.punish * (best.has_punish_num()[3] + best.has_punish_num()[4]))

for route in best.sequence:
    if route.window_punish != 0:
        print(route.start_time, route.sequence, route.capacity_punish, route.window_punish)