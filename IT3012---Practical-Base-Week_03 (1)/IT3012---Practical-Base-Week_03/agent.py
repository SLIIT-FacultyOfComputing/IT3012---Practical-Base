# agent.py
# IT3012 – Intelligent Agents  |  Week 03: Problem-Solving Agents

from collections import deque
import heapq
import random


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1.2 — SIMPLE REFLEX AGENT  (kept here for test_suite.py imports)
# ──────────────────────────────────────────────────────────────────────────────

class SimpleReflexAgent:
    """
    Uses only the current percept (condition-action rules).
    Does not store history or previous actions.
    """

    def sense_and_act(self, percept: dict) -> str:
        # Condition-action rule 1: eat food if present
        if percept["food_here"]:
            return "Suck"

        # Condition-action rule 2: turn if wall ahead
        if percept["wall_ahead"]:
            return "TurnLeft"

        # Default rule: keep moving forward
        return "Forward"


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1.3 — MODEL-BASED AGENT  (kept here for test_suite.py imports)
# ──────────────────────────────────────────────────────────────────────────────

class ModelBasedAgent:
    """
    Maintains an internal state:
    - Estimated relative position & facing direction
    - Set of visited cells
    - Percept history and last action
    """

    def __init__(self):
        self.position = (0, 0)
        self.direction = 0          # 0=Up, 1=Right, 2=Down, 3=Left

        self.visited_cells = {(0, 0)}
        self.percept_history = []
        self.last_action = None

    def cell_in_direction(self, direction):
        movements = [
            (0, 1),    # 0 = Up
            (1, 0),    # 1 = Right
            (0, -1),   # 2 = Down
            (-1, 0)    # 3 = Left
        ]
        dx, dy = movements[direction]
        x, y = self.position
        return x + dx, y + dy

    def update_state(self, percept):
        """Transition model + sensor model update."""
        if self.last_action == "Forward":
            self.position = self.cell_in_direction(self.direction)
            self.visited_cells.add(self.position)
        elif self.last_action == "TurnLeft":
            self.direction = (self.direction - 1) % 4
        elif self.last_action == "TurnRight":
            self.direction = (self.direction + 1) % 4

        self.percept_history.append(dict(percept))
        self.visited_cells.add(self.position)

    def sense_and_act(self, percept: dict) -> str:
        self.update_state(percept)

        cell_ahead = self.cell_in_direction(self.direction)
        left_direction = (self.direction - 1) % 4
        left_cell = self.cell_in_direction(left_direction)

        if percept["food_here"]:
            action = "Suck"
        elif percept["wall_ahead"] and left_cell in self.visited_cells:
            action = "TurnRight"
        elif percept["wall_ahead"]:
            action = "TurnLeft"
        elif cell_ahead in self.visited_cells:
            action = "TurnRight"
        else:
            action = "Forward"

        self.last_action = action
        return action


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1.4 — SEARCH AGENT (PROBLEM-SOLVING AGENT)
# Implements BFS, DFS, and UCS offline planning.
# ──────────────────────────────────────────────────────────────────────────────

class SearchAgent:
    """
    Problem-Solving Agent that formulates a complete plan using an uninformed
    search algorithm (BFS, DFS, or UCS) before acting.

    Configuration
    -------------
    self.plan        : list[str]  – action buffer (pop from front to execute)
    self.active_algo : str        – one of 'BFS', 'DFS', 'UCS'
    """

    def __init__(self):
        self.plan: list = []
        self.active_algo: str = 'BFS'   # ← change to 'DFS' or 'UCS' to observe

    # ── Internal helper ────────────────────────────────────────────────────────

    def _get_neighbors(self, pos, walls, grid_size):
        """Return valid (neighbor_pos, action) pairs from *pos*."""
        x, y = pos
        moves = [
            ('Up',    (0,  1)),
            ('Right', (1,  0)),
            ('Down',  (0, -1)),
            ('Left',  (-1, 0)),
        ]
        neighbors = []
        for action, (dx, dy) in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
                if (nx, ny) not in walls:
                    neighbors.append(((nx, ny), action))
        return neighbors

    # ── BFS ────────────────────────────────────────────────────────────────────

    def bfs_search(self, start, goal, walls, grid_size):
        """
        Breadth-First Search – FIFO frontier (deque.popleft()).
        Guarantees the shortest path (fewest steps) in an unweighted grid.
        """
        start = tuple(start)
        goal  = tuple(goal)
        walls = set(tuple(w) for w in walls)

        frontier = deque([(start, [])])   # (position, path_so_far)
        reached  = {start}                # graph-search reached set

        while frontier:
            curr, path = frontier.popleft()
            if curr == goal:
                return path

            for next_pos, action in self._get_neighbors(curr, walls, grid_size):
                if next_pos not in reached:
                    reached.add(next_pos)
                    frontier.append((next_pos, path + [action]))

        return None   # goal unreachable

    # ── DFS ────────────────────────────────────────────────────────────────────

    def dfs_search(self, start, goal, walls, grid_size):
        """
        Depth-First Search – LIFO frontier (list.pop()).
        Not optimal; may take erratic, winding paths.
        """
        start = tuple(start)
        goal  = tuple(goal)
        walls = set(tuple(w) for w in walls)

        frontier = [(start, [])]    # stack: (position, path_so_far)
        reached  = set()            # graph-search reached set

        while frontier:
            curr, path = frontier.pop()
            if curr == goal:
                return path

            if curr not in reached:
                reached.add(curr)
                for next_pos, action in self._get_neighbors(curr, walls, grid_size):
                    if next_pos not in reached:
                        frontier.append((next_pos, path + [action]))

        return None   # goal unreachable

    # ── UCS ────────────────────────────────────────────────────────────────────

    def ucs_search(self, start, goal, walls, grid_size):
        """
        Uniform-Cost Search – priority queue ordered by cumulative cost g(n).
        Optimal for non-negative, possibly variable step costs.
        (On a uniform-cost grid it produces the same result as BFS.)
        """
        start = tuple(start)
        goal  = tuple(goal)
        walls = set(tuple(w) for w in walls)

        counter  = 0
        frontier = [(0, counter, start, [])]   # (cost, tie_breaker, pos, path)
        reached  = {}                           # pos → best cost seen

        while frontier:
            cost, _, curr, path = heapq.heappop(frontier)
            if curr == goal:
                return path

            if curr in reached and reached[curr] <= cost:
                continue
            reached[curr] = cost

            for next_pos, action in self._get_neighbors(curr, walls, grid_size):
                new_cost = cost + 1
                if next_pos not in reached or new_cost < reached[next_pos]:
                    counter += 1
                    heapq.heappush(
                        frontier,
                        (new_cost, counter, next_pos, path + [action])
                    )

        return None   # goal unreachable

    # ── sense_and_act ──────────────────────────────────────────────────────────

    def sense_and_act(self, percept: dict) -> str:
        """
        If the plan buffer is empty, run the selected search algorithm to find
        the closest food pellet and store the resulting action sequence.
        Return and remove the next action from the front of the plan.
        """
        if not self.plan:
            all_food  = percept.get('all_food', [])

            # Nothing left to collect – wander forward
            if not all_food:
                return "Forward"

            start     = tuple(percept.get('agent_pos', (0, 0)))
            walls     = set(tuple(w) for w in percept.get('walls', []))
            grid_size = percept.get('grid_size', (10, 10))

            # Pick the Manhattan-closest food pellet as the immediate goal
            closest_food = min(
                all_food,
                key=lambda f: abs(f[0] - start[0]) + abs(f[1] - start[1])
            )
            goal = tuple(closest_food)

            # Run the chosen algorithm
            if self.active_algo == 'BFS':
                actions = self.bfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'DFS':
                actions = self.dfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'UCS':
                actions = self.ucs_search(start, goal, walls, grid_size)
            else:
                actions = self.bfs_search(start, goal, walls, grid_size)

            if actions is not None:
                # Navigate to food, then collect it
                self.plan = list(actions) + ['Suck']
            else:
                # Goal unreachable – take a single step and try again next turn
                self.plan = ['Forward']

        return self.plan.pop(0)


# ──────────────────────────────────────────────────────────────────────────────
# ORIGINAL GREEDY AGENT (kept for backward compatibility with simulator.py)
# ──────────────────────────────────────────────────────────────────────────────

class GreedyGridAgent:
    """A simple agent that moves randomly to collect food (original skeleton)."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)