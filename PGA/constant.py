huge = 999999999  # nothing but the largest number during calculation, just for convenience

cross_p = 0.8  # chromo cross probability
random_mutate_p = 0.1  # chromo random mutate probability
inter_change_p = 0.5
combine_try_time = 10  # chromo try combination mutate times per step
insert_try_time = 5  # chromo try insert mutate times per step
remove_try_p = 0.7  # temporary not use
starve_para = 0.25
feasible_generate_p = 0.2
# when random init chromo, 'feasible_generate_p' of total generate number will generate by 'feasible generate' algorithm
# warning, feasible generate' algorithm is really time-consuming, don't set this probability too large

center_id = 0  # center depot idx, may not changeable (so don't change this one!)
custom_number = 1000  # custom number, may not changeable (so don't change this one!)
station_number = 100  # station number, may not changeable (so don't change this one!)

max_volume = 16  # max volume of cargo that vehicle can take
max_weight = 2.5  # max weight of cargo that vehicle can take
unload_time = 0.5  # cargo unload time
driving_range = 120000  # driving range of vehicle
charge_tm = 0.5  # charging time of vehicle
charge_cost = 50  # charge cost of vehicle
wait_cost = 24  # wait cost of vehicle
depot_wait = 1  # the time that vehicle need to spend when it is back to center depot
depot_open_time = 8.  # the open time of center depot
unit_trans_cost = 14. / 1000  # the unit transportation cost
vehicle_cost = 300  # the cost of using a vehicle in one day
