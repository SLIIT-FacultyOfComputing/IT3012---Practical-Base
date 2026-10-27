# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents, hazards, and local directional sensing."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, num_traps=4, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.agent_dir = 'North'  # Agent orientation: 'North', 'East', 'South', 'West'

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Step 2.1: Declare & populate toxic_traps
        self.toxic_traps = set()
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap_pos = (tx, ty)
            if (trap_pos != (0, 0) and 
                trap_pos not in self.walls and 
                trap_pos not in self.food_positions):
                self.toxic_traps.add(trap_pos)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if (tuple(op_pos) != (0, 0) and 
                tuple(op_pos) not in self.walls and 
                tuple(op_pos) not in self.food_positions and 
                tuple(op_pos) not in self.toxic_traps):
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        """
        Step 1.1: Modified perception subsystem for Partial Observability.
        Returns relative boolean sensors instead of exact global agent coordinates.
        """
        x, y = self.agent_pos
        
        # Mapping orientation to relative coordinate deltas
        dir_offsets = {
            'North': (0, 1),
            'East': (1, 0),
            'South': (0, -1),
            'West': (-1, 0)
        }
        
        dx, dy = dir_offsets[self.agent_dir]
        next_x, next_y = x + dx, y + dy
        
        # Check if advancing in the current facing direction hits grid bounds or walls
        out_of_bounds = not (0 <= next_x < self.width and 0 <= next_y < self.height)
        wall_ahead = out_of_bounds or ((next_x, next_y) in self.walls)

        return {
            'wall_ahead': wall_ahead,
            'food_here': tuple(self.agent_pos) in self.food_positions,
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,
            'hit_wall': tuple(self.agent_pos) in self.walls,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }

    def execute_action(self, action: str):
        self.steps += 1
        
        # Directional navigation handling
        directions = ['North', 'East', 'South', 'West']
        curr_idx = directions.index(self.agent_dir)

        if action == 'TurnLeft':
            self.agent_dir = directions[(curr_idx - 1) % 4]
            return
        elif action == 'TurnRight':
            self.agent_dir = directions[(curr_idx + 1) % 4]
            return
        elif action == 'Suck':
            tuple_pos = tuple(self.agent_pos)
            if tuple_pos in self.food_positions:
                self.food_positions.remove(tuple_pos)
                self.score += 20
            return

        # Legacy absolute translation actions & MoveForward support
        new_pos = list(self.agent_pos)
        if action == 'MoveForward':
            if self.agent_dir == 'North': new_pos[1] = min(self.height - 1, new_pos[1] + 1)
            elif self.agent_dir == 'South': new_pos[1] = max(0, new_pos[1] - 1)
            elif self.agent_dir == 'West': new_pos[0] = max(0, new_pos[0] - 1)
            elif self.agent_dir == 'East': new_pos[0] = min(self.width - 1, new_pos[0] + 1)
        elif action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        # Collision & Trap logic
        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)

        if tuple_pos in self.toxic_traps:
            self.score -= 15

        if tuple_pos in self.food_positions and action != 'Suck':
            self.food_positions.remove(tuple_pos)
            self.score += 20

        # Opponent simulation
        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, num_traps=4, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, 
                                     num_opponents=num_opponents, num_traps=num_traps, custom_walls=walls)

        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        # Draw structural grid and walls
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        # Render toxic traps (purple diamonds)
        for tx, ty in self.env.toxic_traps:
            offset = self.cell_size * 0.2
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset
            x2 = x1 + self.cell_size * 0.6
            y2 = y1 + self.cell_size * 0.6
            self.canvas.create_polygon(
                (x1 + x2) / 2, y1,
                x2, (y1 + y2) / 2,
                (x1 + x2) / 2, y2,
                x1, (y1 + y2) / 2,
                fill="#8b5cf6", outline="#6d28d9"
            )

        # Render food items
        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        # Render opponents
        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        # Render Agent with Direction indicator
        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                action = random.choice(['MoveForward', 'TurnLeft', 'TurnRight', 'Suck'])
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Dir: {self.env.agent_dir} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=2, num_traps=4)
    root.mainloop()