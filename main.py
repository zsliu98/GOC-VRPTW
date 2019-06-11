from tools import GlobalMap
from tools import pickle_dump, pickle_load
from PGA import Controller, Nature, Chromo, Route

load = True
save = True  # warning: if save set to be true, it may save the 'controller' to save_dir, which is up to 100MB
generation_num = 500  # can set this number very large, cause it will store the calculation process each 10 generation
chromo_num = 100  # chromo number in each nature, if too small may lead to early convergence
_punish = 9999  # punish parameter, if too big may weaken the influence of mutation
nature_num = 5  # nature number, each nature will operate in one subprocess, don't set it larger than the number of CPU
punish_increase = 1.2  # punish parameter times this number every 10 generation
save_dir = 'data'
read_dir = 'data'


def main():
    g_map = GlobalMap(read_dir=read_dir)
    if not load:
        controller = Controller(nature_num=nature_num, chromo_num=chromo_num, g_map=g_map, punish=_punish,
                                read_dir=read_dir, save_dir=save_dir)
    else:
        try:
            controller: Controller = pickle_load(save_dir + '/controller.pkl')
            controller.set_punish(punish=_punish)
        except FileNotFoundError:
            print('No "controller" in given direction. New "controller" will be created.')
            controller = Controller(nature_num=nature_num, chromo_num=chromo_num, g_map=g_map, punish=_punish,
                                    read_dir=read_dir, save_dir=save_dir)

    for generation in range(0, generation_num):
        print('Generation {} start.'.format(generation))
        controller.operate()
        best: Chromo = controller.get_best()
        print('Best Cost: {}\tRoute Num: {}\tPunish Num: {}'.format(best.cost, len(best.sequence),
                                                                    best.has_punish_num()))
        if generation % 10 == 9:
            if save:
                pickle_dump(controller, file_path=save_dir + '/controller.pkl')
            controller.set_punish(punish=controller.punish * punish_increase)

    best_chromo: Chromo = controller.get_best()
    for route in best_chromo.sequence:
        print(route.sequence)


if __name__ == '__main__':
    main()
