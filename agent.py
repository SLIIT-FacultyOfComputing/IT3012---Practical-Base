from collections import deque
import heapq
import math

from logic_engine import KnowledgeBase


class GreedyGridAgent:
    """Original Lab 01-style agent kept for compatibility."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        return self.actions_pool[0]


class SimpleReflexAgent:
    """
    Simple Reflex Agent 
    The agent has no __init__ method and therefore does not
    maintain any history or memory.

    It uses only the current percept and condition-action rules.
    """

    def sense_and_act(self, percept: dict) -> str:

        # IF food is ahead THEN move toward it.
        if percept.get('food_here', False):
            return 'Right'

        # IF there is a wall ahead THEN change direction.
        if percept.get('wall_ahead', False):
            return 'Up'

        # ELSE continue with the default action.
        return 'Right'


class ModelBasedAgent:
    """
    Model-Based Agent
    The agent maintains internal memory of previous percepts,
    actions, and visited cells. When the same percept is received
    repeatedly, the agent changes its action to avoid repeating
    the same behaviour.
    """

    def __init__(self):

        # Internal memory
        self.visited_cells = {(0, 0)}
        self.percept_history = []
        self.action_history = []

        self.last_percept = None
        self.last_action = None

        # Estimated internal position
        self.estimated_position = [0, 0]

        # Estimated facing direction
        self.directions = ['Up', 'Right', 'Down', 'Left']
        self.direction_index = 1  # Start facing Right

        # Used to detect repeated situations
        self.repeated_percept_count = 0

    def _normalise_percept(self, percept):

        return (
            bool(percept.get('wall_ahead', False)),
            bool(percept.get('food_here', False))
        )

    def _turn_left(self):

        self.direction_index = (
            self.direction_index - 1
        ) % 4

    def _turn_right(self):

        self.direction_index = (
            self.direction_index + 1
        ) % 4

    def _update_internal_state(self, action):

        """
        Update the internal model using the previous action.
        """

        if action == 'Left':

            self._turn_left()

        elif action == 'Right':

            self._turn_right()

        elif action == 'Forward':

            direction = self.directions[
                self.direction_index
            ]

            if direction == 'Up':
                self.estimated_position[1] += 1

            elif direction == 'Down':
                self.estimated_position[1] -= 1

            elif direction == 'Left':
                self.estimated_position[0] -= 1

            elif direction == 'Right':
                self.estimated_position[0] += 1

    def sense_and_act(self, percept):

        current_percept = self._normalise_percept(
            percept
        )

        
        # 1. Update internal state using previous action
        if self.last_action is not None:

            self._update_internal_state(
                self.last_action
            )

        
        # 2. Record current state
        current_cell = tuple(
            self.estimated_position
        )

        self.visited_cells.add(
            current_cell
        )

        self.percept_history.append(
            current_percept
        )

        
        # 3. Detect repeated percept
        if self.last_percept == current_percept:

            self.repeated_percept_count += 1

        else:

            self.repeated_percept_count = 0

        
        # 4. Condition-Action Rules
        wall_ahead = current_percept[0]
        food_here = current_percept[1]

        
        # IF food is ahead THEN move forward.
        if food_here:

            action = 'Forward'

        elif self.repeated_percept_count >= 1:

            if self.last_action == 'Left':

                action = 'Right'

            elif self.last_action == 'Right':

                action = 'Left'

            elif self.last_action == 'Forward':

                action = 'Right'

            else:

                action = 'Left'

        
        # IF wall ahead THEN turn left.
        elif wall_ahead:

            action = 'Left'

        
        # ELSE move forward.
        else:

            action = 'Forward'

        
        # 5. Store the current decision in memory
        self.last_percept = current_percept
        self.last_action = action

        self.action_history.append(
            action
        )

        return action
    
class SearchAgent:
    """Goal-based planning agent.
    The agent plans a complete path to one food pellet using the
    selected search strategy, then executes the stored plan one
    action at a time.
    """

    ACTIONS = [
        ('Up', (0, 1)),
        ('Down', (0, -1)),
        ('Left', (-1, 0)),
        ('Right', (1, 0))
    ]

    def __init__(self):
        # Step 1.3: offline plan and active search algorithm.
        self.plan = []
        self.active_algo = 'BFS'

        self.estimated_position = [0, 0]
        self.last_action = None

        self.kb = KnowledgeBase()
        self.kb.tell_rule(
            ['TargetVisible', 'HasDust'],
            'SafeToEngage'
        )
        self.kb.tell_rule(
            ['SafeToEngage', 'BloodseekerMissing'],
            'Retreat'
        )

    @staticmethod
    def _normalise_walls(walls):
        return {tuple(wall) for wall in walls}

    @staticmethod
    def _in_bounds(position, grid_size):
        width, height = grid_size
        return (
            0 <= position[0] < width
            and 0 <= position[1] < height
        )

    def _successor(self, position, delta, walls, grid_size):
        next_position = (
            position[0] + delta[0],
            position[1] + delta[1]
        )

        if not self._in_bounds(next_position, grid_size):
            return None

        if next_position in walls:
            return None

        return next_position

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        """Breadth-First Search using a FIFO queue.
        """
        walls = self._normalise_walls(walls)
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if not self._in_bounds(start, grid_size) or not self._in_bounds(goal, grid_size):
            return None

        if start in walls or goal in walls:
            return None

        if start == goal:
            return []

        queue = deque([(start, [])])
        reached = {start}

        while queue:
            current, path = queue.popleft()

            for action, delta in self.ACTIONS:
                next_position = self._successor(
                    current, delta, walls, grid_size
                )

                if next_position is None or next_position in reached:
                    continue

                new_path = path + [action]

                if next_position == goal:
                    return new_path

                reached.add(next_position)
                queue.append((next_position, new_path))

        return None

    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        """Depth-First Search using a LIFO stack."""
        walls = self._normalise_walls(walls)
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if not self._in_bounds(start, grid_size) or not self._in_bounds(goal, grid_size):
            return None

        if start in walls or goal in walls:
            return None

        if start == goal:
            return []

        stack = [(start, [])]
        reached = {start}

        while stack:
            current, path = stack.pop()

            if current == goal:
                return path

            for action, delta in reversed(self.ACTIONS):
                next_position = self._successor(
                    current, delta, walls, grid_size
                )

                if next_position is None or next_position in reached:
                    continue

                reached.add(next_position)
                stack.append(
                    (next_position, path + [action])
                )

        return None

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        """Uniform-Cost Search using a priority queue
        """
        walls = self._normalise_walls(walls)
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if not self._in_bounds(start, grid_size) or not self._in_bounds(goal, grid_size):
            return None

        if start in walls or goal in walls:
            return None

        if start == goal:
            return []

        counter = 0
        frontier = [(0, counter, start, [])]
        reached = {start}
        best_cost = {start: 0}

        while frontier:
            cost, _, current, path = heapq.heappop(frontier)

            # Ignore stale priority-queue entries.
            if cost != best_cost.get(current):
                continue

            if current == goal:
                return path

            for action, delta in self.ACTIONS:
                next_position = self._successor(
                    current, delta, walls, grid_size
                )

                if next_position is None:
                    continue

                new_cost = cost + 1

                if new_cost < best_cost.get(next_position, float('inf')):
                    best_cost[next_position] = new_cost
                    reached.add(next_position)
                    counter += 1
                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            counter,
                            next_position,
                            path + [action]
                        )
                    )

        return None

    def manhattan_distance(self, pos, goal):
        """Return Manhattan distance for four-way grid movement."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Return straight-line (Euclidean) distance between two positions."""
        return math.sqrt(
            (pos[0] - goal[0]) ** 2
            + (pos[1] - goal[1]) ** 2
        )

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan',
        tile_facts=None
    ):
        """A* Search using f(n) = g(n) + h(n)."""

        walls = self._normalise_walls(walls)
        tile_facts = tile_facts or {}
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if not self._in_bounds(start, grid_size) or not self._in_bounds(goal, grid_size):
            return None

        if start in walls or goal in walls:
            return None

        if start == goal:
            return []

        if heuristic_type.lower() == 'euclidean':
            heuristic = self.euclidean_distance
        else:
            heuristic = self.manhattan_distance

        frontier = []
        reached_states = set()

        h_start = heuristic(start, goal)
        heapq.heappush(frontier, (h_start, 0, start, []))

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos in reached_states:
                continue

            if current_pos == goal:
                return path_taken

            reached_states.add(current_pos)

            for action, delta in self.ACTIONS:
                next_position = self._successor(
                    current_pos, delta, walls, grid_size
                )

                if next_position is None or next_position in reached_states:
                    continue

                self.kb.clear_facts()
                for fact in tile_facts.get(next_position, []):
                    self.kb.tell_fact(fact)
                self.kb.forward_chain()

                if 'Retreat' in self.kb.facts:
                    continue

                new_g = g_cost + 1
                new_h = heuristic(next_position, goal)
                new_f = new_g + new_h

                heapq.heappush(
                    frontier,
                    (new_f, new_g, next_position, path_taken + [action])
                )

        return None

    def _search(self, start_pos, goal_pos, walls, grid_size, tile_facts=None):
        """Run the search algorithm selected by active_algo."""
        if self.active_algo == 'DFS':
            return self.dfs_search(
                start_pos, goal_pos, walls, grid_size
            )

        if self.active_algo == 'UCS':
            return self.ucs_search(
                start_pos, goal_pos, walls, grid_size
            )

        if self.active_algo == 'AStar':
            return self.astar_search(
                start_pos,
                goal_pos,
                walls,
                grid_size,
                heuristic_type='manhattan',
                tile_facts=tile_facts
            )

        # Default required by the practical.
        return self.bfs_search(
            start_pos, goal_pos, walls, grid_size
        )

    def _update_estimated_position(self, percept):
        """Update the internal position after the previous action.
        """
        if self.last_action is None:
            return

        grid_size = percept.get('grid_size')
        walls = self._normalise_walls(percept.get('walls', []))

        action_delta = dict(self.ACTIONS).get(self.last_action)
        if action_delta is None or grid_size is None:
            return

        candidate = (
            self.estimated_position[0] + action_delta[0],
            self.estimated_position[1] + action_delta[1]
        )

        if (
            self._in_bounds(candidate, grid_size)
            and candidate not in walls
        ):
            self.estimated_position = list(candidate)

    def sense_and_act(self, percept: dict) -> str:
        """Plan to the closest food, then execute the plan step-by-step."""
        self._update_estimated_position(percept)

        if not self.plan:
            tile_facts = {
                (1, 0): ['TargetVisible', 'HasDust', 'BloodseekerMissing'],
                (0, 1): ['TargetVisible', 'HasDust'],
            }
            all_food = [
                tuple(food)
                for food in percept.get('all_food', [])
            ]

            if not all_food:
                # The environment should normally terminate before this.
                self.last_action = 'Up'
                return 'Up'

            start = tuple(self.estimated_position)

            goal = min(
                all_food,
                key=lambda food: (
                    abs(food[0] - start[0])
                    + abs(food[1] - start[1])
                )
            )

            self.plan = self._search(
                start,
                goal,
                percept.get('walls', []),
                percept.get('grid_size', (0, 0)),
                tile_facts=tile_facts
            ) or []

        if self.plan:
            action = self.plan.pop(0)
        else:
            action = 'Up'

        self.last_action = action
        return action



if __name__ == '__main__':
    demo_agent = SearchAgent()
    print("Manhattan (0,0) -> (3,4):", demo_agent.manhattan_distance((0, 0), (3, 4)))
    print("Euclidean (0,0) -> (3,4):", demo_agent.euclidean_distance((0, 0), (3, 4)))
