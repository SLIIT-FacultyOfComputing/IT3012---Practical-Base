import heapq
import math
import random
from collections import deque

from logic_engine import KnowledgeBase


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
    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'suck'
        if percept['wall_ahead']:
            return 'Left'
        return 'Right'


class ModelBasedAgent:
    def __init__(self):
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            action = 'suck'
        elif percept['wall_ahead']:
            action = 'turn_right' if self.last_action == 'turn_left' else 'turn_left'
        else:
            action = 'move_forward'

        self.last_action = action
        return action


class SearchAgent:
    def __init__(self):
        self.plan = []
        self.active_algo = 'UCS'
        self.position = (0, 0)
        self.dir_idx = 0
        self.kb = KnowledgeBase()
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    def _neighbors(self, state, walls, grid_size):
        x, y = state
        width, height = grid_size
        moves = [
            ('Up', (x, y + 1)),
            ('Right', (x + 1, y)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
        ]
        for action, next_state in moves:
            nx, ny = next_state
            if 0 <= nx < width and 0 <= ny < height and next_state not in walls:
                yield action, next_state

    def _reconstruct_path(self, parents, goal):
        path = []
        current = goal
        while parents[current][0] is not None:
            current, action = parents[current]
            path.append(action)
        path.reverse()
        return path

    def _tile_facts(self, tile_percepts, position):
        """Return facts for a tile from a mapping or percept callback."""
        if tile_percepts is None:
            return []
        if callable(tile_percepts):
            percepts = tile_percepts(position)
        else:
            percepts = tile_percepts.get(position, [])
        if isinstance(percepts, dict):
            return [fact for fact, present in percepts.items() if present]
        return percepts

    def _is_feasible(self, position, tile_percepts):
        self.kb.clear_facts()
        for fact in self._tile_facts(tile_percepts, position):
            self.kb.tell_fact(fact)
        self.kb.forward_chain()
        return 'Retreat' not in self.kb.facts

    def bfs_search(self, start, goal, walls, grid_size):
        frontier = deque([start])
        reached = {start}
        parents = {start: (None, None)}
        while frontier:
            current = frontier.popleft()
            if current == goal:
                return self._reconstruct_path(parents, goal)
            for action, next_state in self._neighbors(current, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    parents[next_state] = (current, action)
                    frontier.append(next_state)
        return []

    def dfs_search(self, start, goal, walls, grid_size):
        frontier = [start]
        reached = {start}
        parents = {start: (None, None)}
        while frontier:
            current = frontier.pop()
            if current == goal:
                return self._reconstruct_path(parents, goal)
            for action, next_state in self._neighbors(current, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    parents[next_state] = (current, action)
                    frontier.append(next_state)
        return []

    def ucs_search(self, start, goal, walls, grid_size):
        frontier = [(0, 0, start)]
        reached = {start: 0}
        parents = {start: (None, None)}
        counter = 0
        while frontier:
            cost, _, current = heapq.heappop(frontier)
            if cost != reached[current]:
                continue
            if current == goal:
                return self._reconstruct_path(parents, goal)
            for action, next_state in self._neighbors(current, walls, grid_size):
                new_cost = cost + 1
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    parents[next_state] = (current, action)
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, next_state))
        return []

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan',
        tile_percepts=None,
    ):
        heuristic = {
            'manhattan': self.manhattan_distance,
            'euclidean': self.euclidean_distance,
        }.get(heuristic_type.lower())
        if heuristic is None:
            raise ValueError("heuristic_type must be 'manhattan' or 'euclidean'")

        frontier = []
        start_h = heuristic(start_pos, goal_pos)
        heapq.heappush(frontier, (start_h, 0, start_pos, []))
        reached_states = set()

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)
            if current_pos == goal_pos:
                return path_taken
            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)

            for action, next_pos in self._neighbors(current_pos, walls, grid_size):
                if next_pos not in reached_states and self._is_feasible(
                    next_pos, tile_percepts
                ):
                    new_g = g_cost + 1
                    new_f = new_g + heuristic(next_pos, goal_pos)
                    heapq.heappush(frontier, (new_f, new_g, next_pos, path_taken + [action]))
        return []

    def _closest_food(self, start, food_positions):
        return min(food_positions, key=lambda food: self.manhattan_distance(start, food), default=None)

    def _movement_to_actions(self, movement_path):
        actions = []
        direction_map = {'Up': 0, 'Right': 1, 'Down': 2, 'Left': 3}
        current_dir = self.dir_idx
        for movement in movement_path:
            target_dir = direction_map[movement]
            right_turns = (target_dir - current_dir) % 4
            left_turns = (current_dir - target_dir) % 4
            if left_turns <= right_turns:
                actions.extend(['turn_left'] * left_turns)
            else:
                actions.extend(['turn_right'] * right_turns)
            current_dir = target_dir
            actions.append('move_forward')
        return actions

    def sense_and_act(self, percept):
        self.position = tuple(percept['agent_pos'])
        self.dir_idx = percept['agent_dir_idx']
        if not self.plan:
            food_positions = [tuple(food) for food in percept.get('all_food', [])]
            if not food_positions:
                return 'suck'
            goal = self._closest_food(self.position, food_positions)
            walls = {tuple(wall) for wall in percept['walls']}
            if self.active_algo == 'BFS':
                movement_path = self.bfs_search(self.position, goal, walls, percept['grid_size'])
            elif self.active_algo == 'DFS':
                movement_path = self.dfs_search(self.position, goal, walls, percept['grid_size'])
            elif self.active_algo == 'UCS':
                movement_path = self.ucs_search(self.position, goal, walls, percept['grid_size'])
            elif self.active_algo == 'AStar':
                movement_path = self.astar_search(
                    self.position,
                    goal,
                    walls,
                    percept['grid_size'],
                    tile_percepts=percept.get('tile_percepts'),
                )
            else:
                raise ValueError(f'Unknown algorithm: {self.active_algo}')
            self.plan = self._movement_to_actions(movement_path)
        return self.plan.pop(0) if self.plan else 'suck'