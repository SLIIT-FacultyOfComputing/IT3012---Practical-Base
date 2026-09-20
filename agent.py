import random
from collections import deque
import heapq
import math
from logic_engine import KnowledgeBase



class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = "AStar"

        self.kb = KnowledgeBase()

        self.kb.tell_rule(
            ["TargetVisible", "HasDust"],
            "SafeToEngage"
        )

        self.kb.tell_rule(
            ["SafeToEngage", "BloodseekerMissing"],
            "Retreat"
        )





    def manhattan_distance(self, pos, goal):

        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):

        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )


    def bfs_search(self, start, goal, walls, grid_size):

        queue = deque([(start, [])])
        visited = set()

        while queue:

            state, path = queue.popleft()

            if state == goal:
                return path

            if state in visited:
                continue

            visited.add(state)

            x, y = state

            moves = [
                ((x, y + 1), "Up"),
                ((x, y - 1), "Down"),
                ((x - 1, y), "Left"),
                ((x + 1, y), "Right")
            ]

            for next_state, action in moves:

                nx, ny = next_state

                if (
                    0 <= nx < grid_size[0]
                    and 0 <= ny < grid_size[1]
                    and next_state not in walls
                ):
                    queue.append((next_state, path + [action]))

        return []

    def dfs_search(self, start, goal, walls, grid_size):

        stack = [(start, [])]
        visited = set()

        while stack:

            state, path = stack.pop()

            if state == goal:
                return path

            if state in visited:
                continue

            visited.add(state)

            x, y = state

            moves = [
                ((x, y + 1), "Up"),
                ((x, y - 1), "Down"),
                ((x - 1, y), "Left"),
                ((x + 1, y), "Right")
            ]

            for next_state, action in moves:

                nx, ny = next_state

                if (
                    0 <= nx < grid_size[0]
                    and 0 <= ny < grid_size[1]
                    and next_state not in walls
                ):
                    stack.append((next_state, path + [action]))

        return []

    def ucs_search(self, start, goal, walls, grid_size):

        pq = [(0, start, [])]
        visited = set()

        while pq:

            cost, state, path = heapq.heappop(pq)

            if state == goal:
                return path

            if state in visited:
                continue

            visited.add(state)

            x, y = state

            moves = [
                ((x, y + 1), "Up"),
                ((x, y - 1), "Down"),
                ((x - 1, y), "Left"),
                ((x + 1, y), "Right")
            ]

            for next_state, action in moves:

                nx, ny = next_state

                if (
                    0 <= nx < grid_size[0]
                    and 0 <= ny < grid_size[1]
                    and next_state not in walls
                ):
                    heapq.heappush(
                        pq,
                        (cost + 1, next_state, path + [action])
                    )

        return []

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type="manhattan",
        danger_tiles=None
    ):

        # Tiles where the Bloodseeker escort is missing (real-time
        # per-tile percept fed into the Knowledge Base below).
        danger_tiles = set(danger_tiles) if danger_tiles else set()

        frontier = []
        reached_states = set()

        if heuristic_type == "manhattan":
            h = self.manhattan_distance(start_pos, goal_pos)
        else:
            h = self.euclidean_distance(start_pos, goal_pos)

        heapq.heappush(
            frontier,
            (h, 0, start_pos, [])
        )

        while frontier:

            f_cost, g_cost, current_pos, path = heapq.heappop(frontier)

            if current_pos == goal_pos:
                return path

            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            x, y = current_pos

            moves = [
                ((x, y + 1), "Up"),
                ((x, y - 1), "Down"),
                ((x - 1, y), "Left"),
                ((x + 1, y), "Right")
            ]

            for next_pos, action in moves:

                nx, ny = next_pos

                if (
                    0 <= nx < grid_size[0]
                    and 0 <= ny < grid_size[1]
                    and next_pos not in walls
                    and next_pos not in reached_states
                ):

                    # Step 2: clear facts before evaluating this neighbor
                    self.kb.clear_facts()

                    # Step 3: feed the CURRENT PERCEPTS for THIS SPECIFIC
                    # tile. TargetVisible/HasDust hold for every tile on
                    # this map, but BloodseekerMissing is tile-specific —
                    # it is only true on tiles the environment reports as
                    # danger tiles (toxic traps == no Bloodseeker escort).
                    self.kb.tell_fact("TargetVisible")
                    self.kb.tell_fact("HasDust")

                    if next_pos in danger_tiles:
                        self.kb.tell_fact("BloodseekerMissing")

                    # Step 4: run forward chaining
                    self.kb.forward_chain()

                    # Step 5: skip tile if logically Infeasible, even
                    # though it is physically reachable
                    if "Retreat" in self.kb.facts:
                        continue


                    g_new = g_cost + 1

                    if heuristic_type == "manhattan":
                        h_new = self.manhattan_distance(
                            next_pos,
                            goal_pos
                        )
                    else:
                        h_new = self.euclidean_distance(
                            next_pos,
                            goal_pos
                        )

                    f_new = g_new + h_new

                    heapq.heappush(
                        frontier,
                        (
                            f_new,
                            g_new,
                            next_pos,
                            path + [action]
                        )
                    )

        return []


    def sense_and_act(self, percept):

        if not self.plan:

            start = percept["agent_pos"]

            if percept["all_food"]:

                goal = percept["all_food"][0]

                if self.active_algo == "BFS":
                    self.plan = self.bfs_search(
                        start,
                        goal,
                        percept["walls"],
                        percept["grid_size"]
                    )

                elif self.active_algo == "DFS":
                    self.plan = self.dfs_search(
                        start,
                        goal,
                        percept["walls"],
                        percept["grid_size"]
                    )

                elif self.active_algo == "UCS":
                    self.plan = self.ucs_search(
                        start,
                        goal,
                        percept["walls"],
                        percept["grid_size"]
                    )

                elif self.active_algo == "AStar":

                    self.plan = self.astar_search(
                        start,
                        goal,
                        percept["walls"],
                        percept["grid_size"],
                        danger_tiles=percept.get("danger_tiles", [])
                    )

 
        if self.plan:
            return self.plan.pop(0)

        return random.choice(["Up", "Down", "Left", "Right"])