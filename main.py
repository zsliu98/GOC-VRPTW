from tools import GlobalMap, pickle_dump, pickle_load
from PGA import Controller, Nature, Chromo, Route

load = True
save = True  # warning: if save set to be true, it may save the 'nature' to save_dir, which is up to 100MB
generation_num = 500
chromo_num = 4
_punish = 99999
nature_num = 3
punish_increase = 1.5  # punish parameter times this number every 10 generation
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
