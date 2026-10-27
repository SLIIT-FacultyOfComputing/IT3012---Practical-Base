import random
import math
import heapq


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept['agent_pos']
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'Up'
        elif percept['wall_ahead']:
            return 'Left'
        else:
            return 'Up'


class ModelBasedAgent:

    def __init__(self):
        self.visited_cells = set()
        self.last_action = None
        self.current_position = (0, 0)

    def sense_and_act(self, percept: dict) -> str:
        self.visited_cells.add(self.current_position)

        if percept['food_here']:
            action = 'Up'
        elif percept['wall_ahead']:
            if self.last_action == 'Left':
                action = 'Right'
            else:
                action = 'Left'
        else:
            action = 'Up'

        self.last_action = action
        return action


class SearchAgent:

    def __init__(self):
        self.active_algo = 'AStar'
        self.plan = []

    def manhattan_distance(self, pos, goal):
        distance = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
        return int(distance)

    def euclidean_distance(self, pos, goal):
        distance = math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )
        return distance

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):

        frontier = []
        reached_states = set()

        if heuristic_type == 'euclidean':
            heuristic = self.euclidean_distance
        else:
            heuristic = self.manhattan_distance

        # Starting node
        g_cost = 0
        h_cost = heuristic(start_pos, goal_pos)
        f_cost = g_cost + h_cost

        heapq.heappush(
            frontier,
            (f_cost, g_cost, start_pos, [])
        )

        while frontier:

            f_cost, g_cost, current_pos, path_taken = heapq.heappop(
                frontier
            )

            # Goal reached
            if current_pos == goal_pos:
                return path_taken

            # Already visited
            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            # Up, Down, Left, Right
            neighbors = [
                ('Up', (0, 1)),
                ('Down', (0, -1)),
                ('Left', (-1, 0)),
                ('Right', (1, 0))
            ]

            for action, (dx, dy) in neighbors:

                new_pos = (
                    current_pos[0] + dx,
                    current_pos[1] + dy
                )

                # Check grid boundaries
                if not (
                    0 <= new_pos[0] < grid_size[0]
                    and
                    0 <= new_pos[1] < grid_size[1]
                ):
                    continue

                # Check wall
                if new_pos in walls:
                    continue

                # Check already reached
                if new_pos in reached_states:
                    continue

                # Calculate costs
                new_g_cost = g_cost + 1
                new_h_cost = heuristic(new_pos, goal_pos)
                new_f_cost = new_g_cost + new_h_cost

                new_path = path_taken + [action]

                heapq.heappush(
                    frontier,
                    (
                        new_f_cost,
                        new_g_cost,
                        new_pos,
                        new_path
                    )
                )

        return None

    def sense_and_act(self, percept):

        if self.active_algo == 'AStar':

            current_pos = tuple(percept['agent_pos'])

            food_positions = percept['food_positions']

            # No food remaining
            if not food_positions:
                return None

            # Find closest food
            goal_pos = min(
                food_positions,
                key=lambda food: self.manhattan_distance(
                    current_pos,
                    food
                )
            )

            # Run A*
            self.plan = self.astar_search(
                current_pos,
                goal_pos,
                percept['walls'],
                percept['grid_size']
            )

            # Return next action
            if self.plan:
                return self.plan.pop(0)

            return None

        return None