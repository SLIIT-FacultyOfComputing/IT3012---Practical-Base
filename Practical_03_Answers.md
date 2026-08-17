# Practical 03: Uninformed Search - Theoretical Evaluation

## 1. Fundamental difference between "State Space" and "Search Tree"
The **State Space** is the abstract mathematical or physical representation of all possible valid configurations (states) the agent can be in (e.g., all valid (x, y) coordinates on the grid). It is a graph where nodes are physical states and edges are valid actions transitioning between those states.
A **Search Tree**, on the other hand, is a data structure dynamically generated *in memory* during the execution of a search algorithm. It represents the paths explored by the agent. Multiple nodes in the Search Tree can correspond to the exact same physical state in the State Space if that state was reached via different paths.

## 2. The role of the `reached` set and impact on DFS
The `reached` set solves the problem of **redundant paths and cycles (infinite loops)** by keeping track of states that have already been visited. Adding this converts the algorithm from a Tree Search to a Graph Search. 
Without the `reached` set, a DFS agent operates in Tree Search mode. In a grid environment with reversible actions, it would almost certainly get stuck in an infinite loop toggling between two adjacent empty cells (e.g., moving Left, then Right, then Left...) until it crashes due to an out-of-memory error or recursion/stack overflow limit, never finding the food.

## 3. Optimality of BFS vs. DFS
**BFS** explores the state space level-by-level (all nodes at depth $d$ before depth $d+1$), ensuring that it finds the shallowest goal node first. Because every move in this grid has a uniform, identical step cost of 1, the path with the fewest steps is identically the path with the lowest cost. Hence, BFS is guaranteed to be optimal here.
**DFS**, however, dives as deep as possible along a single branch before it backtracks. It terminates as soon as it stumbles upon *any* path to the goal, regardless of how many steps it took. In an open grid, this often results in highly erratic, winding, and suboptimal routes.

## 4. Memory bottlenecks of BFS vs. DFS on a massive 1000x1000 grid
According to complexity formulas, **BFS** has a space complexity of $O(b^d)$, meaning the memory required grows exponentially with the depth of the solution $d$ (where $b$ is the branching factor, up to 4). On a massive grid, the Frontier (queue) grows extremely wide (proportional to the perimeter of the search boundary), consuming huge amounts of memory and potentially crashing.
In contrast, standard **DFS** only needs to store the current path and unexpanded siblings, yielding a linear space complexity of $O(bm)$ for the Frontier, where $m$ is the maximum depth. DFS is significantly more memory-efficient than BFS, though Graph Search DFS also maintains the `reached` set in memory which bounds its space to $O(|V|)$ (the total number of states). Still, BFS's Frontier memory requirements are generally much more punishing than DFS's on large grids before a solution is found.
