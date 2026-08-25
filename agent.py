# agent.py
import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


#lab02
class SimpleReflexAgent:
    """A Simple Reflex Agent that acts purely on immediate percepts using Condition-Action rules."""

    def sense_and_act(self, percept: dict) -> str:
        # Condition-Action Rules (IF-THEN logic)
        if percept.get('food_here'):
            return 'Up'  # Collect / move forward
        elif percept.get('wall_ahead'):
            return 'Left'  # Turn left when facing a wall
        else:
            return 'Up'  # Default movement action

#lab02
class ModelBasedAgent:
    """A Model-Based Agent that uses internal memory to track past movements."""

    def __init__(self):
        self.actions_pool = ['Up', 'Right', 'Down', 'Left']
        self.current_action_idx = 0
        self.last_action = None
        self.loop_counter = 0  # Internal state memory

    def sense_and_act(self, percept: dict) -> str:
        # 1. Update Internal State (Sensor & Transition Model)
        if percept.get('wall_ahead'):
            self.loop_counter += 1
            # Memory check: If stuck repeatedly at a wall, change direction sequence
            self.current_action_idx = (self.current_action_idx + 1) % len(self.actions_pool)
        else:
            self.loop_counter = 0

        chosen_action = self.actions_pool[self.current_action_idx]
        self.last_action = chosen_action
        return chosen_action


#lab03
class SearchAgent:
    """A Goal-Based Agent that plans step-by-step routes using graph search algorithms."""

    def __init__(self, algo='BFS'):
        self.plan = []  # Holds the calculated sequence of actions
        self.active_algo = algo  # Active algorithm ('BFS', 'DFS', or 'UCS')

    def _get_neighbors(self, current_pos, walls, grid_size):
        """Helper method to return valid adjacent tiles and movement actions."""
        x, y = current_pos
        w, h = grid_size
        moves = [('Up', (x, y + 1)), ('Down', (x, y - 1)), ('Left', (x - 1, y)), ('Right', (x + 1, y))]
        
        valid = []
        for action, (nx, ny) in moves:
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in walls:
                valid.append((action, (nx, ny)))
        return valid

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        """Breadth-First Search: Explores shallowest nodes using a FIFO queue."""
        frontier = deque([(start_pos, [])])
        reached = {start_pos}  # Graph search visited set

        while frontier:
            curr_pos, path = frontier.popleft()  # FIFO extraction
            if curr_pos == goal_pos:
                return path

            for action, next_pos in self._get_neighbors(curr_pos, walls, grid_size):
                if next_pos not in reached:
                    reached.add(next_pos)
                    frontier.append((next_pos, path + [action]))
        return None

    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        """Depth-First Search: Explores deepest nodes using a LIFO stack."""
        frontier = [(start_pos, [])]
        reached = set()  # Graph search visited set

        while frontier:
            curr_pos, path = frontier.pop()  # LIFO extraction
            if curr_pos == goal_pos:
                return path

            if curr_pos not in reached:
                reached.add(curr_pos)
                for action, next_pos in self._get_neighbors(curr_pos, walls, grid_size):
                    if next_pos not in reached:
                        frontier.append((next_pos, path + [action]))
        return None

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        """Uniform-Cost Search: Explores lowest total path cost g(n) using a Priority Queue."""
        # Element format: (cost g(n), counter_id, current_position, path_taken)
        counter = 0
        frontier = [(0, counter, start_pos, [])]
        reached = {start_pos: 0}

        while frontier:
            cost, _, curr_pos, path = heapq.heappop(frontier)  # Priority Queue extraction
            if curr_pos == goal_pos:
                return path

            for action, next_pos in self._get_neighbors(curr_pos, walls, grid_size):
                new_cost = cost + 1  # Standard step cost = 1
                if next_pos not in reached or new_cost < reached[next_pos]:
                    reached[next_pos] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, next_pos, path + [action]))
        return None

    def sense_and_act(self, percept: dict) -> str:
        """Executes one action per tick from the generated plan."""
        # Step 1: Generate plan if empty
        if not self.plan:
            start_pos = percept['agent_pos']
            all_food = percept['all_food']
            walls = set(percept['walls'])
            grid_size = percept['grid_size']

            if not all_food:
                return 'Up'

            # Find closest food pellet using Manhattan Distance
            closest_food = min(all_food, key=lambda f: abs(f[0] - start_pos[0]) + abs(f[1] - start_pos[1]))

            # Execute active algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start_pos, closest_food, walls, grid_size) or []
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start_pos, closest_food, walls, grid_size) or []
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start_pos, closest_food, walls, grid_size) or []

        # Step 2: Pop and execute first action from the plan[cite: 8]
        if self.plan:
            return self.plan.pop(0)
        return 'Up'