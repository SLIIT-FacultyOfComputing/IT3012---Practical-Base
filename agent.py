import random
from collections import deque
import heapq
import math

from logic_engine import KnowledgeBase


# ==================================================
# RANDOM AGENT
# ==================================================

class GreedyGridAgent:

    def __init__(self):
        self.actions_pool = [
            'Up',
            'Down',
            'Left',
            'Right'
        ]

    def sense_and_act(self, percept: dict) -> str:
        return random.choice(self.actions_pool)


# ==================================================
# SEARCH AGENT
# ==================================================

class SearchAgent:

    def __init__(self, algorithm='BFS'):

        self.plan = []
        self.active_algorithm = algorithm

        # ==================================================
        # KNOWLEDGE BASE
        # ==================================================

        self.kb = KnowledgeBase()

        # Rule 1:
        # TargetVisible AND HasDust -> SafeToEngage

        self.kb.tell_rule(
            ['TargetVisible', 'HasDust'],
            'SafeToEngage'
        )

        # Rule 2:
        # SafeToEngage AND BloodseekerMissing -> Retreat

        self.kb.tell_rule(
            ['SafeToEngage', 'BloodseekerMissing'],
            'Retreat'
        )

    # ==================================================
    # BFS SEARCH
    # ==================================================

    def bfs_search(self, start, goal, grid_size, walls):

        w, h = grid_size

        if start in walls or goal in walls:
            return None

        queue = deque([(start, [])])
        visited = {start}

        while queue:

            pos, path = queue.popleft()

            if pos == goal:
                return path

            x, y = pos

            neighbors = [
                (x, y + 1, 'Up'),
                (x, y - 1, 'Down'),
                (x - 1, y, 'Left'),
                (x + 1, y, 'Right')
            ]

            for nx, ny, action in neighbors:

                if 0 <= nx < w and 0 <= ny < h:

                    new_pos = (nx, ny)

                    if (
                        new_pos not in walls
                        and new_pos not in visited
                    ):

                        visited.add(new_pos)

                        queue.append(
                            (
                                new_pos,
                                path + [action]
                            )
                        )

        return None

    # ==================================================
    # DFS SEARCH
    # ==================================================

    def dfs_search(self, start, goal, grid_size, walls):

        w, h = grid_size

        if start in walls or goal in walls:
            return None

        stack = [(start, [])]
        visited = {start}

        while stack:

            pos, path = stack.pop()

            if pos == goal:
                return path

            x, y = pos

            neighbors = [
                (x, y + 1, 'Up'),
                (x, y - 1, 'Down'),
                (x - 1, y, 'Left'),
                (x + 1, y, 'Right')
            ]

            for nx, ny, action in neighbors:

                if 0 <= nx < w and 0 <= ny < h:

                    new_pos = (nx, ny)

                    if (
                        new_pos not in walls
                        and new_pos not in visited
                    ):

                        visited.add(new_pos)

                        stack.append(
                            (
                                new_pos,
                                path + [action]
                            )
                        )

        return None

    # ==================================================
    # UCS SEARCH
    # ==================================================

    def ucs_search(self, start, goal, grid_size, walls):

        w, h = grid_size

        if start in walls or goal in walls:
            return None

        heap = []

        heapq.heappush(
            heap,
            (0, 0, start, [])
        )

        best_cost = {
            start: 0
        }

        while heap:

            cost, _, pos, path = heapq.heappop(heap)

            if pos == goal:
                return path

            x, y = pos

            neighbors = [
                (x, y + 1, 'Up'),
                (x, y - 1, 'Down'),
                (x - 1, y, 'Left'),
                (x + 1, y, 'Right')
            ]

            for nx, ny, action in neighbors:

                if 0 <= nx < w and 0 <= ny < h:

                    new_pos = (nx, ny)

                    if new_pos not in walls:

                        new_cost = cost + 1

                        if (
                            new_pos not in best_cost
                            or new_cost < best_cost[new_pos]
                        ):

                            best_cost[new_pos] = new_cost

                            heapq.heappush(
                                heap,
                                (
                                    new_cost,
                                    new_cost,
                                    new_pos,
                                    path + [action]
                                )
                            )

        return None

    # ==================================================
    # MANHATTAN DISTANCE
    # ==================================================

    def manhattan_distance(self, pos, goal):

        return (
            abs(pos[0] - goal[0])
            + abs(pos[1] - goal[1])
        )

    # ==================================================
    # EUCLIDEAN DISTANCE
    # ==================================================

    def euclidean_distance(self, pos, goal):

        return math.sqrt(
            (pos[0] - goal[0]) ** 2
            + (pos[1] - goal[1]) ** 2
        )

    # ==================================================
    # KNOWLEDGE BASE FEASIBILITY CHECK
    # ==================================================

    def is_tile_feasible(
        self,
        neighbor,
        percept
    ):

        # Clear previous facts
        self.kb.clear_facts()

        # --------------------------------------------------
        # Read percept information
        # --------------------------------------------------

        # TargetVisible
        if percept.get('target_visible', False):

            self.kb.tell_fact(
                'TargetVisible'
            )

        # HasDust
        if percept.get('has_dust', False):

            self.kb.tell_fact(
                'HasDust'
            )

        # BloodseekerMissing
        if percept.get('bloodseeker_missing', False):

            self.kb.tell_fact(
                'BloodseekerMissing'
            )

        # --------------------------------------------------
        # Optional tile-specific percepts
        # --------------------------------------------------

        target_visible_cells = {
            tuple(cell)
            for cell in percept.get(
                'target_visible_cells',
                []
            )
        }

        dust_cells = {
            tuple(cell)
            for cell in percept.get(
                'dust_cells',
                []
            )
        }

        bloodseeker_missing_cells = {
            tuple(cell)
            for cell in percept.get(
                'bloodseeker_missing_cells',
                []
            )
        }

        # If the specific neighbor has the percept,
        # add the corresponding fact.

        if neighbor in target_visible_cells:

            self.kb.tell_fact(
                'TargetVisible'
            )

        if neighbor in dust_cells:

            self.kb.tell_fact(
                'HasDust'
            )

        if neighbor in bloodseeker_missing_cells:

            self.kb.tell_fact(
                'BloodseekerMissing'
            )

        # --------------------------------------------------
        # Forward Chaining
        # --------------------------------------------------

        self.kb.forward_chain()

        # --------------------------------------------------
        # Check whether Retreat was deduced
        # --------------------------------------------------

        if 'Retreat' in self.kb.facts:

            return False

        return True

    # ==================================================
    # A* SEARCH
    # ==================================================

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan',
        percept=None
    ):

        w, h = grid_size

        # Default percept
        if percept is None:
            percept = {}

        # Check invalid start or goal
        if (
            start_pos in walls
            or goal_pos in walls
        ):
            return None

        # --------------------------------------------------
        # Select heuristic
        # --------------------------------------------------

        if heuristic_type == 'euclidean':

            heuristic = self.euclidean_distance

        else:

            heuristic = self.manhattan_distance

        # --------------------------------------------------
        # Priority queue
        # --------------------------------------------------

        heap = []

        # --------------------------------------------------
        # Reached states
        # --------------------------------------------------

        reached_states = set()

        # --------------------------------------------------
        # Start node
        # --------------------------------------------------

        g_cost = 0

        h_cost = heuristic(
            start_pos,
            goal_pos
        )

        f_cost = g_cost + h_cost

        heapq.heappush(
            heap,
            (
                f_cost,
                g_cost,
                start_pos,
                []
            )
        )

        # ==================================================
        # A* LOOP
        # ==================================================

        while heap:

            (
                f_cost,
                g_cost,
                current_pos,
                path_taken
            ) = heapq.heappop(heap)

            # Goal test
            if current_pos == goal_pos:

                return path_taken

            # Skip already reached states
            if current_pos in reached_states:

                continue

            # Mark current state as reached
            reached_states.add(
                current_pos
            )

            x, y = current_pos

            # --------------------------------------------------
            # Generate neighbors
            # --------------------------------------------------

            neighbors = [
                (x, y + 1, 'Up'),
                (x, y - 1, 'Down'),
                (x - 1, y, 'Left'),
                (x + 1, y, 'Right')
            ]

            for nx, ny, action in neighbors:

                # --------------------------------------------------
                # Check grid boundaries
                # --------------------------------------------------

                if (
                    0 <= nx < w
                    and 0 <= ny < h
                ):

                    neighbor = (nx, ny)

                    # --------------------------------------------------
                    # Check wall and reached state
                    # --------------------------------------------------

                    if (
                        neighbor not in walls
                        and neighbor not in reached_states
                    ):

                        # ==============================================
                        # KNOWLEDGE BASE FEASIBILITY CHECK
                        # ==============================================

                        is_feasible = self.is_tile_feasible(
                            neighbor,
                            percept
                        )

                        # If Retreat is deduced,
                        # skip this neighbor.

                        if not is_feasible:

                            continue

                        # ==============================================
                        # CALCULATE A* COSTS
                        # ==============================================

                        # g(n)
                        new_g = g_cost + 1

                        # h(n)
                        new_h = heuristic(
                            neighbor,
                            goal_pos
                        )

                        # f(n)
                        new_f = new_g + new_h

                        # Add neighbor to open list
                        heapq.heappush(
                            heap,
                            (
                                new_f,
                                new_g,
                                neighbor,
                                path_taken + [action]
                            )
                        )

        # No path found
        return None

    # ==================================================
    # FIND CLOSEST FOOD
    # ==================================================

    def find_closest_food(
        self,
        pos,
        foods
    ):

        if not foods:
            return None

        closest_food = None

        minimum_distance = float(
            'inf'
        )

        for food in foods:

            distance = self.manhattan_distance(
                pos,
                food
            )

            if distance < minimum_distance:

                minimum_distance = distance

                closest_food = food

        return closest_food

    # ==================================================
    # INTEGRATE SEARCH INTO AGENT
    # ==================================================

    def sense_and_act(self, percept):

        # --------------------------------------------------
        # Use existing plan
        # --------------------------------------------------

        if self.plan:

            return self.plan.pop(0)

        # --------------------------------------------------
        # Agent position
        # --------------------------------------------------

        pos = tuple(
            percept['agent_pos']
        )

        # --------------------------------------------------
        # Food positions
        # --------------------------------------------------

        foods = [
            tuple(food)
            for food in percept.get(
                'all_food',
                []
            )
        ]

        # --------------------------------------------------
        # Grid size
        # --------------------------------------------------

        grid_size = percept.get(
            'grid_size',
            (10, 10)
        )

        # --------------------------------------------------
        # Walls
        # --------------------------------------------------

        walls = {
            tuple(wall)
            for wall in percept.get(
                'walls',
                []
            )
        }

        # --------------------------------------------------
        # Toxic traps
        # --------------------------------------------------

        toxic_traps = {
            tuple(trap)
            for trap in percept.get(
                'toxic_traps',
                []
            )
        }

        # Treat walls and toxic traps as blocked
        blocked_cells = (
            walls | toxic_traps
        )

        # --------------------------------------------------
        # No food
        # --------------------------------------------------

        if not foods:

            return 'Stay'

        # --------------------------------------------------
        # Find closest food
        # --------------------------------------------------

        goal = self.find_closest_food(
            pos,
            foods
        )

        if goal is None:

            return 'Stay'

        # ==================================================
        # SELECT SEARCH ALGORITHM
        # ==================================================

        if self.active_algorithm == 'BFS':

            path = self.bfs_search(
                pos,
                goal,
                grid_size,
                blocked_cells
            )

        elif self.active_algorithm == 'DFS':

            path = self.dfs_search(
                pos,
                goal,
                grid_size,
                blocked_cells
            )

        elif self.active_algorithm == 'UCS':

            path = self.ucs_search(
                pos,
                goal,
                grid_size,
                blocked_cells
            )

        elif self.active_algorithm == 'AStar':

            path = self.astar_search(
                start_pos=pos,
                goal_pos=goal,
                walls=blocked_cells,
                grid_size=grid_size,
                heuristic_type='manhattan',
                percept=percept
            )

        else:

            return 'Stay'

        # --------------------------------------------------
        # No path available
        # --------------------------------------------------

        if not path:

            return 'Stay'

        # --------------------------------------------------
        # Save generated plan
        # --------------------------------------------------

        self.plan = path

        # --------------------------------------------------
        # Return first action
        # --------------------------------------------------

        return self.plan.pop(0)


# ==================================================
# HEURISTIC TESTING
# ==================================================

if __name__ == "__main__":

    agent = SearchAgent()

    print(
        "Manhattan:",
        agent.manhattan_distance(
            (0, 0),
            (3, 4)
        )
    )

    print(
        "Euclidean:",
        agent.euclidean_distance(
            (0, 0),
            (3, 4)
        )
    )

    # ==================================================
    # KNOWLEDGE BASE TEST
    # ==================================================

    agent.kb.clear_facts()

    agent.kb.tell_fact(
        'TargetVisible'
    )

    agent.kb.tell_fact(
        'HasDust'
    )

    agent.kb.forward_chain()

    
    print("KB Facts:", agent.kb.facts)
    # Expected:
    # TargetVisible
    # HasDust
    # SafeToEngage

    # Test Rule 2
agent.kb.clear_facts()

agent.kb.tell_fact("TargetVisible")
agent.kb.tell_fact("HasDust")
agent.kb.tell_fact("BloodseekerMissing")

agent.kb.forward_chain()

print("KB Facts:", agent.kb.facts)