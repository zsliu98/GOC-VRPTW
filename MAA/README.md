# GOC-VRPTW-MAA
Implement Multi-Agent Algorithm
## Introduction
Core idea is treating objects in this problem as agents, such as route/vehicle agent and customer agent. Each step a global optimizer examine all moves proposed by agents and choose the best one.
## Agent Operations
### Customer Agent
- Best Insert (Active)
- Best Exchange (Active)
- Propose Route (Passive)
- Propose Customer Replacement (Passive)

### Route Agent
- Best Insert (Active)
- Best Exchange (Active)
- Insert Customer (Passive)
- Replace Customer (Passive)

### Planner Agent
- Best Move Selection
    - periodically, move pools is re-initialized by emptying itself and asking all agents to re-proposed moves
- Route Optimization
    - traditional TSP, use the 2-opt exchange heuristics to reorder the customers in the route
- Bad Route Removal
    - transferring the customers in the bad route to other routes, wherever possible, by making use of the passive operations of the customer and route agents



## Reference
[1] Leong, Hon Wai , and M. Liu . "A multi-agent algorithm for vehicle routing problem with time window." Acm Symposium on Applied Computing DBLP, 2006.</br>
[2] Dan, Zhenggang , L. Cai , and L. Zheng . "Improved multi-agent system for the vehicle routing problem with time windows." Tsinghua Science and Technology 14.3(2009):407-412.