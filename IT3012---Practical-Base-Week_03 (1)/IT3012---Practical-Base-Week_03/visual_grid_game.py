from collections import deque
import heapq
import random
import tkinter as tk


# STEP 1.2 — SIMPLE REFLEX AGENT


class SimpleReflexAgent:
    """
    Uses only the current percept.
    It does not store percept history or previous actions.
    """

    def sense_and_act(self, percept):
        # Condition-action rule 1
        if percept["food_here"]:
            return "Suck"

        # Condition-action rule 2
        if percept["wall_ahead"]:
            return "TurnLeft"

        # Default condition-action rule
        return "Forward"


# STEP 1.3 — MODEL-BASED AGENT


class ModelBasedAgent:
    """
    Maintains an internal state containing:
    - Estimated relative position
    - Estimated facing direction
    - Visited cells
    - Previous percepts
    - Last action
    """

    def __init__(self):
        self.position = (0, 0)
        self.direction = 0

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
        """
        Transition model:
        Uses the last action to estimate how the internal state changed.

        Sensor model:
        Records the current local percept.
        """

        if self.last_action == "Forward":
            self.position = self.cell_in_direction(self.direction)
            self.visited_cells.add(self.position)

        elif self.last_action == "TurnLeft":
            self.direction = (self.direction - 1) % 4

        elif self.last_action == "TurnRight":
            self.direction = (self.direction + 1) % 4

        self.percept_history.append(dict(percept))
        self.visited_cells.add(self.position)

    def sense_and_act(self, percept):
        # First update the internal state
        self.update_state(percept)

        cell_ahead = self.cell_in_direction(self.direction)

        left_direction = (self.direction - 1) % 4
        left_cell = self.cell_in_direction(left_direction)

        # Memory-based condition-action rules
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


# STEP 1.4 — SEARCH AGENT (PROBLEM-SOLVING AGENT)


class SearchAgent:
    """
    Problem-Solving Agent that formulates a plan using search algorithms
    (BFS, DFS, or UCS) to find the shortest/optimal path to food pellets.
    """

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'

    def get_neighbors(self, pos, walls, grid_size):
        x, y = pos
        directions = [
            ('Up', (0, 1)),
            ('Right', (1, 0)),
            ('Down', (0, -1)),
            ('Left', (-1, 0))
        ]
        neighbors = []
        for action, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
                if (nx, ny) not in walls:
                    neighbors.append(((nx, ny), action))
        return neighbors

    def bfs_search(self, start, goal, walls, grid_size):
        start = tuple(start)
        goal = tuple(goal)
        walls = set(tuple(w) for w in walls)

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            curr, path = queue.popleft()
            if curr == goal:
                return path

            for next_node, action in self.get_neighbors(curr, walls, grid_size):
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [action]))

        return None

    def dfs_search(self, start, goal, walls, grid_size):
        start = tuple(start)
        goal = tuple(goal)
        walls = set(tuple(w) for w in walls)

        stack = [(start, [])]
        visited = set()

        while stack:
            curr, path = stack.pop()
            if curr == goal:
                return path

            if curr not in visited:
                visited.add(curr)
                for next_node, action in self.get_neighbors(curr, walls, grid_size):
                    if next_node not in visited:
                        stack.append((next_node, path + [action]))

        return None

    def ucs_search(self, start, goal, walls, grid_size):
        start = tuple(start)
        goal = tuple(goal)
        walls = set(tuple(w) for w in walls)

        counter = 0
        pq = [(0, counter, start, [])]
        visited = {}

        while pq:
            cost, _, curr, path = heapq.heappop(pq)
            if curr == goal:
                return path

            if curr in visited and visited[curr] <= cost:
                continue
            visited[curr] = cost

            for next_node, action in self.get_neighbors(curr, walls, grid_size):
                new_cost = cost + 1
                if next_node not in visited or new_cost < visited[next_node]:
                    counter += 1
                    heapq.heappush(pq, (new_cost, counter, next_node, path + [action]))

        return None

    def sense_and_act(self, percept):
        if not self.plan:
            all_food = percept.get('all_food', [])
            if not all_food:
                return "Forward"

            start = tuple(percept.get('agent_pos', (0, 0)))
            walls = set(percept.get('walls', []))
            grid_size = percept.get('grid_size', (10, 10))

            closest_food = min(
                all_food,
                key=lambda f: abs(f[0] - start[0]) + abs(f[1] - start[1])
            )
            goal = tuple(closest_food)

            if self.active_algo == 'BFS':
                actions = self.bfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'DFS':
                actions = self.dfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'UCS':
                actions = self.ucs_search(start, goal, walls, grid_size)
            else:
                actions = self.bfs_search(start, goal, walls, grid_size)

            if actions is not None:
                self.plan = list(actions) + ['Suck']
            else:
                self.plan = ['Forward']

        return self.plan.pop(0)


# GRID ENVIRONMENT


class VisualGridHuntGame:

    DIRECTIONS = [
        (0, 1),    # Up
        (1, 0),    # Right
        (0, -1),   # Down
        (-1, 0)    # Left
    ]

    DIRECTION_NAMES = ["Up", "Right", "Down", "Left"]

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=0,
        num_traps=5,
        custom_walls=None
    ):
        self.width = width
        self.height = height

        # Actual position belongs to the environment.
        # It is not returned by get_percept().
        self.agent_pos = [0, 0]

        # Agent initially faces right
        self.agent_direction = 1

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (2, 4),
                (3, 4),
                (4, 4),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        self.score = 0
        self.steps = 0
        self.collision = False

        # Generate random food positions
        self.food_positions = set()

        available_cells = (
            width * height
            - len(self.walls)
            - 1
        )

        num_food = min(num_food, available_cells)

        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            food_position = (fx, fy)

            if (
                food_position != (0, 0)
                and food_position not in self.walls
            ):
                self.food_positions.add(food_position)

        # Generate opponents
        self.opponents = []

        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            opponent_position = (ox, oy)

            if (
                opponent_position != (0, 0)
                and opponent_position not in self.walls
                and opponent_position not in self.food_positions
                and list(opponent_position) not in self.opponents
            ):
                self.opponents.append(list(opponent_position))

        # Generate toxic traps
        self.toxic_traps = set()

        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap_position = (tx, ty)

            if (
                trap_position != (0, 0)
                and trap_position not in self.walls
                and trap_position not in self.food_positions
                and list(trap_position) not in self.opponents
            ):
                self.toxic_traps.add(trap_position)

    def get_cell_ahead(self):
        dx, dy = self.DIRECTIONS[self.agent_direction]

        next_x = self.agent_pos[0] + dx
        next_y = self.agent_pos[1] + dy

        return next_x, next_y

    # STEP 1.1 — PARTIALLY OBSERVABLE PERCEPT


    def get_percept(self):
        """
        Returns only local Boolean information.

        It does not return:
        - agent_pos
        - opponent_positions
        - complete wall positions
        - complete food positions
        """

        next_position = self.get_cell_ahead()
        next_x, next_y = next_position

        outside_grid = (
            next_x < 0
            or next_x >= self.width
            or next_y < 0
            or next_y >= self.height
        )

        wall_ahead = (
            outside_grid
            or next_position in self.walls
        )

        food_here = (
            tuple(self.agent_pos) in self.food_positions
        )

        return {
            "wall_ahead": wall_ahead,
            "food_here": food_here,
            "agent_pos": tuple(self.agent_pos),
            "agent_direction": self.agent_direction,
            "all_food": list(self.food_positions),
            "walls": set(self.walls),
            "grid_size": (self.width, self.height)
        }

    def execute_action(self, action):
        self.steps += 1

        if action in ["Up", "Right", "Down", "Left"]:
            dir_map = {
                "Up": (0, 1, 0),
                "Right": (1, 0, 1),
                "Down": (0, -1, 2),
                "Left": (-1, 0, 3)
            }
            dx, dy, new_dir = dir_map[action]
            self.agent_direction = new_dir
            next_x = self.agent_pos[0] + dx
            next_y = self.agent_pos[1] + dy

            inside_grid = (
                0 <= next_x < self.width
                and 0 <= next_y < self.height
            )

            if (
                inside_grid
                and (next_x, next_y) not in self.walls
            ):
                self.agent_pos = [next_x, next_y]
            else:
                self.score -= 5

        elif action == "TurnLeft":
            self.agent_direction = (
                self.agent_direction - 1
            ) % 4

        elif action == "TurnRight":
            self.agent_direction = (
                self.agent_direction + 1
            ) % 4

        elif action == "Forward":
            next_position = self.get_cell_ahead()
            next_x, next_y = next_position

            inside_grid = (
                0 <= next_x < self.width
                and 0 <= next_y < self.height
            )

            if (
                inside_grid
                and next_position not in self.walls
            ):
                self.agent_pos = [next_x, next_y]
            else:
                self.score -= 5

        elif action == "Suck":
            current_position = tuple(self.agent_pos)

            if current_position in self.food_positions:
                self.food_positions.remove(current_position)
                self.score += 20

        current_position = tuple(self.agent_pos)

        # Apply trap penalty once
        if current_position in self.toxic_traps:
            self.score -= 15

        self.move_opponents()

    def move_opponents(self):
        for opponent in self.opponents:
            action = random.choice(
                ["Up", "Down", "Left", "Right", "Stay"]
            )

            new_position = list(opponent)

            if action == "Up":
                new_position[1] += 1
            elif action == "Down":
                new_position[1] -= 1
            elif action == "Left":
                new_position[0] -= 1
            elif action == "Right":
                new_position[0] += 1

            inside_grid = (
                0 <= new_position[0] < self.width
                and 0 <= new_position[1] < self.height
            )

            if (
                inside_grid
                and tuple(new_position) not in self.walls
            ):
                opponent[0] = new_position[0]
                opponent[1] = new_position[1]

            if opponent == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self):
        return (
            len(self.food_positions) == 0
            or self.steps >= 100
            or self.collision
        )


# TKINTER USER INTERFACE

class GridGameGUI:

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=0,
        num_traps=5,
        walls=None
    ):
        self.root = root
        self.root.title(
            "IT3012 - Simple Reflex and Model-Based Agents"
        )

        self.width = width
        self.height = height
        self.num_food = num_food
        self.num_opponents = num_opponents
        self.num_traps = num_traps
        self.walls = walls

        self.env = None
        self.agent = None
        self.agent_name = None

        maximum_canvas_size = 600

        self.cell_size = max(
            20,
            min(
                maximum_canvas_size // width,
                maximum_canvas_size // height
            )
        )

        canvas_width = width * self.cell_size
        canvas_height = height * self.cell_size

        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg="white"
        )
        self.canvas.pack()

        self.label = tk.Label(
            root,
            text="Select an agent to begin",
            font=("Arial", 14)
        )
        self.label.pack(pady=8)

        self.simple_button = tk.Button(
            root,
            text="Run Simple Reflex Agent",
            command=self.start_simple_agent,
            font=("Arial", 12),
            bg="#9a3412",
            fg="white"
        )
        self.simple_button.pack(pady=3)

        self.model_button = tk.Button(
            root,
            text="Run Model-Based Agent",
            command=self.start_model_agent,
            font=("Arial", 12),
            bg="#166534",
            fg="white"
        )
        self.model_button.pack(pady=3)

        self.bfs_button = tk.Button(
            root,
            text="Run Search Agent (BFS)",
            command=self.start_bfs_agent,
            font=("Arial", 12),
            bg="#1d4ed8",
            fg="white"
        )
        self.bfs_button.pack(pady=3)

        self.dfs_button = tk.Button(
            root,
            text="Run Search Agent (DFS)",
            command=self.start_dfs_agent,
            font=("Arial", 12),
            bg="#b91c1c",
            fg="white"
        )
        self.dfs_button.pack(pady=3)

        self.ucs_button = tk.Button(
            root,
            text="Run Search Agent (UCS)",
            command=self.start_ucs_agent,
            font=("Arial", 12),
            bg="#6d28d9",
            fg="white"
        )
        self.ucs_button.pack(pady=3)

        self.reset_environment()
        self.draw_grid()

    def set_buttons_state(self, state):
        self.simple_button.config(state=state)
        self.model_button.config(state=state)
        self.bfs_button.config(state=state)
        self.dfs_button.config(state=state)
        self.ucs_button.config(state=state)

    def reset_environment(self):
        self.env = VisualGridHuntGame(
            width=self.width,
            height=self.height,
            num_food=self.num_food,
            num_opponents=self.num_opponents,
            num_traps=self.num_traps,
            custom_walls=self.walls
        )

    def start_simple_agent(self):
        self.reset_environment()
        self.agent = SimpleReflexAgent()
        self.agent_name = "Simple Reflex Agent"
        self.start_simulation()

    def start_model_agent(self):
        self.reset_environment()
        self.agent = ModelBasedAgent()
        self.agent_name = "Model-Based Agent"
        self.start_simulation()

    def start_bfs_agent(self):
        self.reset_environment()
        self.agent = SearchAgent()
        self.agent.active_algo = "BFS"
        self.agent_name = "Search Agent (BFS)"
        self.start_simulation()

    def start_dfs_agent(self):
        self.reset_environment()
        self.agent = SearchAgent()
        self.agent.active_algo = "DFS"
        self.agent_name = "Search Agent (DFS)"
        self.start_simulation()

    def start_ucs_agent(self):
        self.reset_environment()
        self.agent = SearchAgent()
        self.agent.active_algo = "UCS"
        self.agent_name = "Search Agent (UCS)"
        self.start_simulation()

    def start_simulation(self):
        self.set_buttons_state("disabled")

        self.draw_grid()
        self.run_loop()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (
                    self.env.height - 1 - y
                ) * self.cell_size

                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if (x, y) in self.env.walls:
                    color = "#64748b"
                else:
                    color = "#f1f5f9"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1"
                )

                if (
                    self.cell_size >= 40
                    and (x, y) in self.env.walls
                ):
                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold")
                    )

        # Draw food
        for food_x, food_y in self.env.food_positions:
            offset = self.cell_size * 0.25

            x1 = food_x * self.cell_size + offset
            y1 = (
                self.env.height - 1 - food_y
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )

        # Draw toxic traps
        for trap_x, trap_y in self.env.toxic_traps:
            offset = self.cell_size * 0.20

            x1 = trap_x * self.cell_size + offset
            y1 = (
                self.env.height - 1 - trap_y
            ) * self.cell_size + offset

            x2 = x1 + self.cell_size * 0.60
            y2 = y1 + self.cell_size * 0.60

            self.canvas.create_polygon(
                x1 + self.cell_size * 0.30,
                y1,
                x2,
                y1 + self.cell_size * 0.30,
                x1 + self.cell_size * 0.30,
                y2,
                x1,
                y1 + self.cell_size * 0.30,
                fill="purple",
                outline="#581c87"
            )

        # Draw opponents
        for opponent_x, opponent_y in self.env.opponents:
            offset = self.cell_size * 0.2

            x1 = opponent_x * self.cell_size + offset
            y1 = (
                self.env.height - 1 - opponent_y
            ) * self.cell_size + offset

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )

        # Draw agent
        agent_x, agent_y = self.env.agent_pos
        offset = self.cell_size * 0.15

        x1 = agent_x * self.cell_size + offset
        y1 = (
            self.env.height - 1 - agent_y
        ) * self.cell_size + offset

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )

        direction_symbol = ["↑", "→", "↓", "←"][
            self.env.agent_direction
        ]

        self.canvas.create_text(
            x1 + self.cell_size * 0.35,
            y1 + self.cell_size * 0.35,
            text=direction_symbol,
            fill="white",
            font=("Arial", 16, "bold")
        )

    def run_loop(self):
        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()

                action = self.agent.sense_and_act(
                    percept
                )

                self.env.execute_action(action)
                self.draw_grid()

                self.label.config(
                    text=(
                        f"{self.agent_name} | "
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action} | "
                        f"Pos: {percept['agent_pos']} | "
                        f"Food left: {len(percept['all_food'])}"
                    )
                )

                self.root.after(300, step)

            else:
                if self.env.collision:
                    result = "Collision — Game Over"
                elif not self.env.food_positions:
                    result = "All food collected"
                else:
                    result = "Maximum steps reached"

                self.label.config(
                    text=(
                        f"{self.agent_name} finished | "
                        f"{result} | "
                        f"Final score: {self.env.score}"
                    )
                )

                self.set_buttons_state("normal")

        step()



# START PROGRAM


if __name__ == "__main__":
    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=10,
        height=10,
        num_food=10,
        num_opponents=0,
        num_traps=5
    )

    root.mainloop()