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
        _ = percept.get('agent_pos')
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """React to immediate percepts without memory."""

    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here', False):
            return 'Up'
        if percept.get('wall_ahead', False):
            return 'Left'
        return 'Right'


class ModelBasedAgent:
    """Maintain simple memory so it can avoid repeating the same failed action."""

    def __init__(self):
        self.last_percept = None
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        if self.last_percept == percept and self.last_action is not None:
            alternatives = [action for action in ['Up', 'Down', 'Left', 'Right'] if action != self.last_action]
            action = alternatives[0] if alternatives else 'Up'
        elif percept.get('wall_ahead', False):
            action = 'Left'
        elif percept.get('food_here', False):
            action = 'Up'
        else:
            action = 'Right'

        self.last_percept = percept
        self.last_action = action
        return action


class SearchAgent:
    """Use breadth-first search to find the shortest path through a static grid."""

    def __init__(self, active_algo: str = 'BFS'):
        self.plan = []
        self.active_algo = active_algo
        # mapping for convenience
        self.search_methods = {
            'BFS': self.bfs_search,
            'DFS': self.dfs_search,
            'UCS': self.ucs_search,
        }

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        start = (start_pos[0], start_pos[1])
        goal = (goal_pos[0], goal_pos[1])
        width, height = grid_size
        walls = set(walls)

        if start == goal:
            return []
        if goal in walls:
            return None

        queue = deque([start])
        parents = {start: None}
        actions = {}
        moves = [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]

        while queue:
            current = queue.popleft()
            if current == goal:
                break

            x, y = current
            for action, (dx, dy) in moves:
                nxt = (x + dx, y + dy)
                if (
                    0 <= nxt[0] < width
                    and 0 <= nxt[1] < height
                    and nxt not in walls
                    and nxt not in parents
                ):
                    parents[nxt] = current
                    actions[nxt] = action
                    queue.append(nxt)

        if goal not in parents:
            return None

        path = []
        node = goal
        while True:
            parent = parents[node]
            if parent is None:
                break
            path.append(actions[node])
            node = parent
        path.reverse()
        return path
    
    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        start = (start_pos[0], start_pos[1])
        goal = (goal_pos[0], goal_pos[1])
        width, height = grid_size
        walls = set(walls)

        if start == goal:
            return []
        if goal in walls:
            return None

        stack = [start]
        parents = {start: None}
        actions = {}
        reached = {start}
        moves = [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]

        while stack:
            current = stack.pop()
            if current == goal:
                break

            x, y = current
            for action, (dx, dy) in moves:
                nxt = (x + dx, y + dy)
                if (
                    0 <= nxt[0] < width
                    and 0 <= nxt[1] < height
                    and nxt not in walls
                    and nxt not in reached
                ):
                    reached.add(nxt)
                    parents[nxt] = current
                    actions[nxt] = action
                    stack.append(nxt)

        if goal not in parents:
            return None

        path = []
        node = goal
        while True:
            parent = parents[node]
            if parent is None:
                break
            path.append(actions[node])
            node = parent
        path.reverse()
        return path

    def sense_and_act(self, percept: dict) -> str:
        # If we already have a plan, execute next action
        if self.plan:
            return self.plan.pop(0)

        # If standing on food, attempt a simple move to trigger collection
        if percept.get('food_here', False):
            return 'Up'

        foods = percept.get('all_food', [])
        if not foods:
            return 'Up'

        # choose closest food by Manhattan distance
        x, y = percept.get('position', (0, 0))
        def manh(p):
            return abs(p[0] - x) + abs(p[1] - y)

        target = tuple(sorted(foods, key=manh)[0])
        walls = percept.get('walls', [])
        grid_size = percept.get('grid_size', (10, 10))

        search_method = self.search_methods.get(self.active_algo, self.bfs_search)
        path = search_method((x, y), target, walls, grid_size)

        if not path:
            # fallback: pick any safe neighboring move
            for move in ['Up', 'Right', 'Down', 'Left']:
                nx, ny = x, y
                if move == 'Up':
                    ny += 1
                elif move == 'Down':
                    ny -= 1
                elif move == 'Left':
                    nx -= 1
                elif move == 'Right':
                    nx += 1
                if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1] and (nx, ny) not in set(walls):
                    return move
            return 'Up'

        self.plan = path
        return self.plan.pop(0)

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        start = (start_pos[0], start_pos[1])
        goal = (goal_pos[0], goal_pos[1])
        width, height = grid_size
        walls = set(walls)

        if start == goal:
            return []
        if goal in walls:
            return None

        # Priority queue entries: (cost, node)
        pq = []
        heapq.heappush(pq, (0, start))
        parents = {start: None}
        actions = {}
        gscore = {start: 0}
        moves = [('Up', (0, 1)), ('Down', (0, -1)), ('Left', (-1, 0)), ('Right', (1, 0))]

        while pq:
            cost, current = heapq.heappop(pq)
            if current == goal:
                break

            # If we popped a stale entry, skip it
            if cost != gscore.get(current, float('inf')):
                continue

            x, y = current
            for action, (dx, dy) in moves:
                nxt = (x + dx, y + dy)
                if not (0 <= nxt[0] < width and 0 <= nxt[1] < height):
                    continue
                if nxt in walls:
                    continue

                new_cost = cost + 1  # uniform step cost
                if new_cost < gscore.get(nxt, float('inf')):
                    gscore[nxt] = new_cost
                    parents[nxt] = current
                    actions[nxt] = action
                    heapq.heappush(pq, (new_cost, nxt))

        if goal not in parents:
            return None

        path = []
        node = goal
        while True:
            parent = parents[node]
            if parent is None:
                break
            path.append(actions[node])
            node = parent
        path.reverse()
        return path