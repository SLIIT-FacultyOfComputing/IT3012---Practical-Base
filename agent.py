# agent.py
import random
import heapq
from collections import deque


class SimpleReflexAgent:
    """Step 1.2 from Lab 02: Condition-Action memoryless reflex agent."""
    def __init__(self):
        pass

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'Suck'
        elif percept.get('wall_ahead'):
            return 'TurnLeft'
        else:
            return 'MoveForward'


class ModelBasedAgent:
    """Step 1.3 from Lab 02: Model-based agent tracking internal state/history."""
    def __init__(self):
        self.visited_cells = set()
        self.current_pos = [0, 0]
        self.orientations = ['North', 'East', 'South', 'West']
        self.dir_idx = 0
        self.visited_cells.add(tuple(self.current_pos))
        self.last_action = None

    def update_state(self, percept: dict):
        if self.last_action == 'TurnLeft':
            self.dir_idx = (self.dir_idx - 1) % 4
        elif self.last_action == 'TurnRight':
            self.dir_idx = (self.dir_idx + 1) % 4
        elif self.last_action == 'MoveForward' and not percept.get('hit_wall'):
            dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][self.dir_idx]
            self.current_pos[0] += dx
            self.current_pos[1] += dy
            self.visited_cells.add(tuple(self.current_pos))

    def sense_and_act(self, percept: dict) -> str:
        if self.last_action:
            self.update_state(percept)

        if percept.get('food_here'):
            action = 'Suck'
        elif percept.get('wall_ahead'):
            action = 'TurnRight'
        else:
            dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][self.dir_idx]
            next_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)
            if next_pos in self.visited_cells:
                action = 'TurnRight'
            else:
                action = 'MoveForward'

        self.last_action = action
        return action


class SearchAgent:
    """
    Lab 03: SearchAgent implementing BFS, DFS, and UCS
    Generates offline plans to systematically collect food.
    """

    def __init__(self, algo: str = 'BFS'):
        self.plan = []
        self.active_algo = algo  # Options: 'BFS', 'DFS', 'UCS'

    def get_neighbors(self, state: tuple, grid_size: tuple, walls: set):
        """Generates valid adjacent successor moves (Up, Down, Left, Right)."""
        width, height = grid_size
        x, y = state
        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]
        
        valid_neighbors = []
        for action, (nx, ny) in moves:
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                valid_neighbors.append((action, (nx, ny)))
        return valid_neighbors

    def bfs_search(self, start: tuple, goal: tuple, grid_size: tuple, walls: set):
        """Step 1.2: Breadth-First Search using a FIFO Queue (deque)."""
        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            current_state, path = frontier.popleft()
            if current_state == goal:
                return path

            for action, next_state in self.get_neighbors(current_state, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    def dfs_search(self, start: tuple, goal: tuple, grid_size: tuple, walls: set):
        """Step 1.2: Depth-First Search using a LIFO Stack (list)."""
        frontier = [(start, [])]
        reached = {start}

        while frontier:
            current_state, path = frontier.pop()
            if current_state == goal:
                return path

            for action, next_state in self.get_neighbors(current_state, grid_size, walls):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    def ucs_search(self, start: tuple, goal: tuple, grid_size: tuple, walls: set):
        """Step 1.2: Uniform Cost Search using a Priority Queue (heapq) ordered by g(n)."""
        frontier = []
        counter = 0  # Tie-breaker for heapq
        heapq.heappush(frontier, (0, counter, start, []))
        reached = {start: 0}

        while frontier:
            cost, _, current_state, path = heapq.heappop(frontier)

            if current_state == goal:
                return path

            for action, next_state in self.get_neighbors(current_state, grid_size, walls):
                new_cost = cost + 1  # Uniform step cost of 1
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, next_state, path + [action]))
        return []

    def sense_and_act(self, percept: dict) -> str:
        """Step 1.3: Formulates a complete offline plan and executes it sequentially."""
        if not self.plan:
            all_food = percept.get('all_food', [])
            if not all_food:
                return 'Stay'

            agent_pos = tuple(percept['agent_pos'])
            grid_size = percept['grid_size']
            walls = set(map(tuple, percept['walls']))

            # Find closest food using Manhattan distance
            closest_food = min(
                all_food,
                key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1])
            )
            goal = tuple(closest_food)

            # Plan using the configured search algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, goal, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, goal, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, goal, grid_size, walls)

        if self.plan:
            return self.plan.pop(0)
        return 'Stay'