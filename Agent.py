import random
from collections import deque
import heapq


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


class SearchAgent:
    """An agent that plans a full path to the nearest food using classical
    uninformed search (BFS, DFS, or UCS) over the exposed world model,
    then executes that plan one action at a time."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'  # one of 'BFS', 'DFS', 'UCS'

    # ------------------------------------------------------------------
    # Shared successor generator
    # ------------------------------------------------------------------
    def get_successors(self, pos, grid_size, walls):
        """Given a (x, y) position, return a list of (new_pos, action, step_cost)
        for every legal move. A move that would leave the grid boundary or
        land on a wall is not a valid successor (mirrors execute_action, where
        walking into a wall just wastes a turn rather than moving)."""
        x, y = pos
        width, height = grid_size
        candidate_moves = {
            'Up':    (x, min(height - 1, y + 1)),
            'Down':  (x, max(0, y - 1)),
            'Left':  (max(0, x - 1), y),
            'Right': (min(width - 1, x + 1), y),
        }

        successors = []
        for action, new_pos in candidate_moves.items():
            if new_pos == (x, y):
                continue          # blocked by grid boundary, no state change
            if new_pos in walls:
                continue          # blocked by wall
            successors.append((new_pos, action, 1))  # uniform step cost of 1
        return successors

    # ------------------------------------------------------------------
    # Step 1.2: BFS / DFS / UCS
    # ------------------------------------------------------------------
    def bfs_search(self, start, goal, grid_size, walls):
        start, goal = tuple(start), tuple(goal)
        frontier = deque([(start, [])])   # FIFO queue
        reached = {start}

        while frontier:
            pos, path = frontier.popleft()
            if pos == goal:
                return path
            for new_pos, action, _ in self.get_successors(pos, grid_size, walls):
                if new_pos not in reached:
                    reached.add(new_pos)
                    frontier.append((new_pos, path + [action]))
        return []  # no path found

    def dfs_search(self, start, goal, grid_size, walls):
        start, goal = tuple(start), tuple(goal)
        frontier = [(start, [])]          # LIFO stack
        reached = {start}

        while frontier:
            pos, path = frontier.pop()
            if pos == goal:
                return path
            for new_pos, action, _ in self.get_successors(pos, grid_size, walls):
                if new_pos not in reached:
                    reached.add(new_pos)
                    frontier.append((new_pos, path + [action]))
        return []  # no path found

    def ucs_search(self, start, goal, grid_size, walls):
        start, goal = tuple(start), tuple(goal)
        counter = 0  # tie-breaker so heapq never compares tuples of paths
        frontier = [(0, counter, start, [])]   # priority queue ordered by g(n)
        best_cost = {start: 0}

        while frontier:
            cost, _, pos, path = heapq.heappop(frontier)
            if pos == goal:
                return path
            if cost > best_cost.get(pos, float('inf')):
                continue  # a cheaper route to pos was already expanded
            for new_pos, action, step_cost in self.get_successors(pos, grid_size, walls):
                new_cost = cost + step_cost
                if new_cost < best_cost.get(new_pos, float('inf')):
                    best_cost[new_pos] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, new_pos, path + [action]))
        return []  # no path found

    # ------------------------------------------------------------------
    # Step 1.3: planning + execution
    # ------------------------------------------------------------------
    def find_closest_food(self, agent_pos, all_food):
        """Pick the nearest food pellet by Manhattan distance as the search goal."""
        ax, ay = agent_pos
        closest, best_dist = None, None
        for fx, fy in all_food:
            dist = abs(fx - ax) + abs(fy - ay)
            if best_dist is None or dist < best_dist:
                best_dist, closest = dist, (fx, fy)
        return closest

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            all_food = percept['all_food']
            if not all_food:
                return random.choice(['Up', 'Down', 'Left', 'Right'])

            agent_pos = percept['agent_pos']
            grid_size = percept['grid_size']
            walls = set(tuple(w) for w in percept['walls'])
            goal = self.find_closest_food(agent_pos, all_food)

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, goal, grid_size, walls)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, goal, grid_size, walls)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, goal, grid_size, walls)
            else:
                raise ValueError(f"Unknown algorithm: {self.active_algo}")

            if not self.plan:
                # goal unreachable (e.g. walled off) - fall back so the sim doesn't stall
                return random.choice(['Up', 'Down', 'Left', 'Right'])

        return self.plan.pop(0)