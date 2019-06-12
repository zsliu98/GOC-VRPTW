# GOC-VRPTW
Implement Genetic Algorithm on Vehicle Routing Problem with Time Windows, Recharging Stations and other Constraints
## Code Structure
- main.py: run this will start the genetic algorithm directly, before this you may take a look at the parameter statement; also, if you want to restart the algorithm please all `controller.pkl` and `nature*.pkl` in `save_dir`
- data: store the data, include `input_distance-time.csv`, `input_node.xlsx` and `input_vehicle_type.xlsx`, the output will also be put here by default
- tools: include several tools used in this programme
    - data_taker.py: take data from data folder
    - global_map.py: contain all information in the map that can be obtained through several interface
    - macosFile: store big data by pickle
- PGA: include modules in genetic algorithm
    - controller.py: global controller
    - nature.py: nature, where chromosome in
    - chromo.py: chromosome, where route(gene) in
    - route.py: route(gene)
    - constant.py: all constant used in genetic algorithm
    - test.py: read the best route from `save_dir` and present it

## Parameter Statement
Here only introduce the parameters in main.py, not parameters in PGA/constant.py.
- `load`: whether load controller (and natures) from `save_dir`
- `save`: whether save controller (and natures) to `save_dir`
- `generation_num`: generation num, setting it large is ok, cause main.py will store the calculation process each 10 generation (in `save_dir` if `save == True`)
- `chromo_num`: chromo number in each nature, if too small may lead to early convergence, if too large may need more time to calculate
- `_punish`: punish parameter, if too big may weaken the influence of mutation, if too small may raise too much punishment
- `nature_num`: nature number, each nature will operate in one subprocess, don't set it larger than the number of CPU kernels (or it may become really slow)
- `punish_increase`: punish parameter times this number every 10 generation, if too big may weaken the influence of mutation
- `save_dir`: relative direction to save and load controller (and natures), default is `data/` (if you change this, please also change `save_dir` in test.py)
- `read_dir`: relative direction to read the input data, default is `data/`