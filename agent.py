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


class SimpleReflexAgent:
    """A Simple Reflex Agent using only Condition-Action rules (no memory)."""
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'suck'
        elif percept.get('wall_ahead'):
            return 'turn_left'
        else:
            return 'move_forward'


class ModelBasedAgent:
    """A Model-Based Agent that maintains an internal memory state to escape loops."""
    def __init__(self):
        self.visited_cells = set()
        self.pos = [0, 0]
        self.dir = 'Up'
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        # Update Transition Model based on last action
        if self.last_action == 'turn_left':
            dirs = ['Up', 'Left', 'Down', 'Right']
            self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        elif self.last_action == 'turn_right':
            dirs = ['Up', 'Right', 'Down', 'Left']
            self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        elif self.last_action == 'move_forward':
            if self.dir == 'Up': self.pos[1] += 1
            elif self.dir == 'Down': self.pos[1] -= 1
            elif self.dir == 'Left': self.pos[0] -= 1
            elif self.dir == 'Right': self.pos[0] += 1

        # Update Sensor Model / Memory
        current_pos_tuple = tuple(self.pos)
        self.visited_cells.add(current_pos_tuple)

        # Check if the cell to the left is visited
        left_dir = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}[self.dir]
        left_pos = list(self.pos)
        if left_dir == 'Up': left_pos[1] += 1
        elif left_dir == 'Down': left_pos[1] -= 1
        elif left_dir == 'Left': left_pos[0] -= 1
        elif left_dir == 'Right': left_pos[0] += 1
        
        left_is_visited = tuple(left_pos) in self.visited_cells

        # Condition-Action rules querying memory
        if percept.get('food_here'):
            action = 'suck'
        elif percept.get('wall_ahead'):
            # If we just turned left but there's still a wall (like in a corner),
            # keep turning left so we don't get stuck in a left-right toggle loop.
            if self.last_action == 'turn_left':
                action = 'turn_left'
            elif self.last_action == 'turn_right':
                action = 'turn_right'
            elif left_is_visited:
                action = 'turn_right'
            else:
                action = 'turn_left'
        else:
            action = 'move_forward'
            
        self.last_action = action
        return action


class SearchAgent:
    """
    agent that try to use bfs and dfs to find the shortest path to food.
    """
    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            food_targets = percept['all_food']
            if not food_targets:
                return 'Stay'

            start_pos = percept['agent_pos']
            # Find closest food using Manhattan distance
            closest_food = min(food_targets, key=lambda f: abs(f[0]-start_pos[0]) + abs(f[1]-start_pos[1]))
            
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start_pos, closest_food, percept['walls'], percept['grid_size'])
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start_pos, closest_food, percept['walls'], percept['grid_size'])
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start_pos, closest_food, percept['walls'], percept['grid_size'])
                
        if self.plan:
            return self.plan.pop(0)
        return 'Stay'

    def get_successors(self, pos, walls, grid_size):
        x, y = pos
        w, h = grid_size
        successors = []
        moves = {'Up': (x, y+1), 'Down': (x, y-1), 'Left': (x-1, y), 'Right': (x+1, y)}
        for action, (nx, ny) in moves.items():
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in walls:
                successors.append((action, (nx, ny)))
        return successors

    def bfs_search(self, start, goal, walls, grid_size):
        walls = set(walls)
        queue = deque([(start, [])])
        reached = {start}
        while queue:
            curr, path = queue.popleft()
            if curr == goal:
                return path + ['suck']
            for action, nxt in self.get_successors(curr, walls, grid_size):
                if nxt not in reached:
                    reached.add(nxt)
                    queue.append((nxt, path + [action]))
        return []

    def dfs_search(self, start, goal, walls, grid_size):
        walls = set(walls)
        stack = [(start, [])]
        reached = {start}
        while stack:
            curr, path = stack.pop()
            if curr == goal:
                return path + ['suck']
            for action, nxt in self.get_successors(curr, walls, grid_size):
                if nxt not in reached:
                    reached.add(nxt)
                    stack.append((nxt, path + [action]))
        return []

    def ucs_search(self, start, goal, walls, grid_size):
        walls = set(walls)
        pq = [(0, start, [])]
        reached = {start: 0}
        
        while pq:
            cost, curr, path = heapq.heappop(pq)
            
            # Skip if we already found a shorter path to this node
            if cost > reached.get(curr, float('inf')):
                continue
                
            if curr == goal:
                return path + ['suck']
                
            for action, nxt in self.get_successors(curr, walls, grid_size):
                new_cost = cost + 1
                if nxt not in reached or new_cost < reached[nxt]:
                    reached[nxt] = new_cost
                    heapq.heappush(pq, (new_cost, nxt, path + [action]))
        return []

