from collections import deque
import random
import heapq

# agent.py
class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

class SearchAgent:

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']
        self.plan = []
        self.active_algo = 'BFS'
        
    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            # We assume agent_pos is in percept (you may need to add it to get_percept if missing)
            agent_pos = tuple(percept.get('agent_pos', (0,0)))
            all_food = percept.get('all_food', [])
            
            if not all_food:
                return random.choice(self.actions_pool)
                
            # Find the closest food pellet using Manhattan distance
            closest_food = min(all_food, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))
            
            def get_successors(state):
                successors = []
                x, y = state
                moves = {'Up': (x, y + 1), 'Down': (x, y - 1), 'Left': (x - 1, y), 'Right': (x + 1, y)}
                
                grid_w, grid_h = percept.get('grid_size', (10, 10))
                walls = set(percept.get('walls', []))
                
                for action, (nx, ny) in moves.items():
                    if 0 <= nx < grid_w and 0 <= ny < grid_h:
                        if (nx, ny) not in walls:
                            if self.active_algo == 'UCS':
                                successors.append((action, (nx, ny), 1)) # include step cost for UCS
                            else:
                                successors.append((action, (nx, ny)))
                return successors

            # Execute the search method matching self.active_algo
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, closest_food, get_successors)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, closest_food, get_successors)
            elif self.active_algo == 'UCS':
                def cost_function(s, a, s_next): return 1
                self.plan = self.ucs_search(agent_pos, closest_food, get_successors, cost_function)
                
        # Return the first action from the plan
        if self.plan:
            return self.plan.pop(0)
            
        return random.choice(self.actions_pool)
    
    def bfs_search(self, start_state, goal_state, get_successors):
        frontier = deque([(start_state, [])]) # here queue store state and path
        reached = set([start_state]) # this will track explored states

        while frontier: # while queue is not empty
            current_state, current_path = frontier.popleft() # get the first element

            if current_state == goal_state:
                return current_path # if goal is reached, return the path

            for action, successor in get_successors(current_state):
                if successor not in reached:
                    reached.add(successor)
                    frontier.append((successor, current_path + [action]))
        
        return []

    
    def dfs_search(self, start_state, goal_state, get_successors):
        frontier = [(start_state, [])] # Stack stores (state, path)
        reached = set()                # Track explored states (added when popped)
        while frontier:
            current_state, path = frontier.pop() # LIFO Stack
            if current_state == goal_state:
                return path
            
            if current_state not in reached:
                reached.add(current_state)
                for action, successor in get_successors(current_state):
                    if successor not in reached:
                        frontier.append((successor, path + [action]))
        return []
        
    def ucs_search(self, start_state, goal_state, get_successors, cost_function):
        frontier = []
        heapq.heappush(frontier, (0, id(start_state), start_state, [])) 
        
        reached = {start_state: 0} 
        while frontier:
            current_cost, _, current_state, path = heapq.heappop(frontier)
            if current_state == goal_state:
                return path
            for action, successor, step_cost in get_successors(current_state):
                new_cost = current_cost + step_cost
                
                if successor not in reached or new_cost < reached[successor]:
                    reached[successor] = new_cost
                    heapq.heappush(frontier, (new_cost, id(successor), successor, path + [action]))
                    
        return []
            


