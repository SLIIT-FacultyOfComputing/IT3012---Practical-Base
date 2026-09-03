# agent.py
import math
import random
import heapq
from collections import deque


class SimpleReflexAgent:
    """Step 1.2: Simple Reflex Agent using direct directional movements."""
    def __init__(self):
        pass

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'Suck'
        elif percept.get('wall_ahead'):
            return 'Left'
        else:
            return 'Up'


class ModelBasedAgent:
    """Step 1.3: Model-Based Agent tracking past actions to prevent looping."""
    def __init__(self):
        self.history = []
        self.moves = ['Up', 'Right', 'Down', 'Left']

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'Suck'

        if percept.get('wall_ahead'):
            # Cycle through alternative moves to break identical loops
            last_action = self.history[-1] if self.history else None
            options = [m for m in self.moves if m != last_action and m != 'Up']
            action = options[len(self.history) % len(options)]
        else:
            action = 'Up'

        self.history.append(action)
        return action


class SearchAgent:
    """
    SearchAgent supporting BFS, DFS, UCS, and A* Search.
    Compatible with autograder parameter ordering and grid formats.
    """

    def __init__(self, algo: str = 'AStar', heuristic_type: str = 'manhattan'):
        self.plan = []
        self.active_algo = algo
        self.heuristic_type = heuristic_type

    # --- Heuristic Functions ---
    def manhattan_distance(self, pos: tuple, goal: tuple) -> int:
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos: tuple, goal: tuple) -> float:
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    def _get_h(self, pos: tuple, goal: tuple, heuristic_type: str) -> float:
        if heuristic_type == 'euclidean':
            return self.euclidean_distance(pos, goal)
        return self.manhattan_distance(pos, goal)

    def _parse_grid(self, grid_arg, walls_arg):
        """Standardizes grid_size and walls regardless of parameter swapping or format."""
        if isinstance(grid_arg, (set, list)) and isinstance(walls_arg, (tuple, int)):
            walls, grid_size = set(map(tuple, grid_arg)), walls_arg
        else:
            walls = set(map(tuple, walls_arg))
            grid_size = grid_arg

        if isinstance(grid_size, int):
            width, height = grid_size, grid_size
        else:
            width, height = grid_size[0], grid_size[1]

        return width, height, walls

    def get_neighbors(self, state: tuple, grid_size, walls):
        """Generates valid 4-way adjacent moves."""
        width, height, wall_set = self._parse_grid(grid_size, walls)
        x, y = state
        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]
        
        valid_neighbors = []
        for action, (nx, ny) in moves:
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in wall_set:
                valid_neighbors.append((action, (nx, ny)))
        return valid_neighbors

    # --- Search Algorithms (Handles both parameter orders) ---
    def bfs_search(self, start: tuple, goal: tuple, arg3=None, arg4=None):
        width, height, walls = self._parse_grid(arg3, arg4)
        start, goal = tuple(start), tuple(goal)

        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            current_state, path = frontier.popleft()
            if current_state == goal:
                return path

            for action, next_state in self.get_neighbors(current_state, (width, height), walls):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    def dfs_search(self, start: tuple, goal: tuple, arg3=None, arg4=None):
        width, height, walls = self._parse_grid(arg3, arg4)
        start, goal = tuple(start), tuple(goal)

        frontier = [(start, [])]
        reached = {start}

        while frontier:
            current_state, path = frontier.pop()
            if current_state == goal:
                return path

            for action, next_state in self.get_neighbors(current_state, (width, height), walls):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    def ucs_search(self, start: tuple, goal: tuple, arg3=None, arg4=None):
        width, height, walls = self._parse_grid(arg3, arg4)
        start, goal = tuple(start), tuple(goal)

        frontier = []
        counter = 0
        heapq.heappush(frontier, (0, counter, start, []))
        reached = {start: 0}

        while frontier:
            cost, _, current_state, path = heapq.heappop(frontier)
            if current_state == goal:
                return path

            for action, next_state in self.get_neighbors(current_state, (width, height), walls):
                new_cost = cost + 1
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, next_state, path + [action]))
        return []

    def astar_search(self, start_pos: tuple, goal_pos: tuple, arg3=None, arg4=None, heuristic_type: str = 'manhattan'):
        width, height, walls = self._parse_grid(arg3, arg4)
        start_pos, goal_pos = tuple(start_pos), tuple(goal_pos)

        frontier = []
        counter = 0
        h_start = self._get_h(start_pos, goal_pos, heuristic_type)
        g_start = 0
        f_start = g_start + h_start

        heapq.heappush(frontier, (f_start, counter, g_start, start_pos, []))
        reached_states = {}

        while frontier:
            f_cost, _, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states and reached_states[current_pos] <= g_cost:
                continue
            reached_states[current_pos] = g_cost

            for action, next_pos in self.get_neighbors(current_pos, (width, height), walls):
                g_new = g_cost + 1
                if next_pos in reached_states and reached_states[next_pos] <= g_new:
                    continue

                h_new = self._get_h(next_pos, goal_pos, heuristic_type)
                f_new = g_new + h_new
                counter += 1
                heapq.heappush(frontier, (f_new, counter, g_new, next_pos, path_taken + [action]))

        return []

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            all_food = percept.get('all_food', [])
            if not all_food:
                return 'Stay'

            agent_pos = tuple(percept['agent_pos'])
            grid_size = percept['grid_size']
            walls = set(map(tuple, percept['walls']))

            closest_food = min(
                all_food,
                key=lambda f: self.manhattan_distance(agent_pos, tuple(f))
            )
            goal = tuple(closest_food)

            if self.active_algo == 'AStar':
                self.plan = self.astar_search(agent_pos, goal, walls, grid_size, self.heuristic_type)
            elif self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, goal, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, goal, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, goal, walls, grid_size)

        if self.plan:
            return self.plan.pop(0)
        return 'Stay'


if __name__ == "__main__":
    tester = SearchAgent()
    p1 = (0, 0)
    p2 = (3, 4)
    print(f"Testing Checkpoint:")
    print(f"Manhattan Distance between {p1} and {p2}: {tester.manhattan_distance(p1, p2)}")
    print(f"Euclidean Distance between {p1} and {p2}: {tester.euclidean_distance(p1, p2)}")