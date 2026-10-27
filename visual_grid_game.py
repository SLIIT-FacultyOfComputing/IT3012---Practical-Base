import random
import tkinter as tk


class VisualGridHuntGame:
    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, num_traps=3, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]
        self.agent_dir_idx = 0  # 0: Up (+Y), 1: Right (+X), 2: Down (-Y), 3: Left (-X)
        self.dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        self.toxic_traps = set()
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            pos_tuple = (tx, ty)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls and pos_tuple not in self.food_positions:
                self.toxic_traps.add(pos_tuple)

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
        dx, dy = self.dirs[self.agent_dir_idx]
        ahead_x, ahead_y = self.agent_pos[0] + dx, self.agent_pos[1] + dy
        wall_ahead = (ahead_x < 0 or ahead_x >= self.width or 
                      ahead_y < 0 or ahead_y >= self.height or 
                      (ahead_x, ahead_y) in self.walls)

        left_dir = (self.agent_dir_idx - 1) % 4
        lx, ly = self.dirs[left_dir]
        left_x, left_y = self.agent_pos[0] + lx, self.agent_pos[1] + ly
        wall_left = (left_x < 0 or left_x >= self.width or 
                     left_y < 0 or left_y >= self.height or 
                     (left_x, left_y) in self.walls)

        right_dir = (self.agent_dir_idx + 1) % 4
        rx, ry = self.dirs[right_dir]
        right_x, right_y = self.agent_pos[0] + rx, self.agent_pos[1] + ry
        wall_right = (right_x < 0 or right_x >= self.width or 
                      right_y < 0 or right_y >= self.height or 
                      (right_x, right_y) in self.walls)

        return {
            'wall_ahead': wall_ahead,
            'wall_left': wall_left,
            'wall_right': wall_right,
            'food_here': tuple(self.agent_pos) in self.food_positions
        }

    def execute_action(self, action: str):
        self.steps += 1

        if action == 'suck':
            tuple_pos = tuple(self.agent_pos)
            if tuple_pos in self.food_positions:
                self.food_positions.remove(tuple_pos)
                self.score += 20
        elif action == 'turn_left':
            self.agent_dir_idx = (self.agent_dir_idx - 1) % 4
        elif action == 'turn_right':
            self.agent_dir_idx = (self.agent_dir_idx + 1) % 4
        elif action == 'move_forward':
            dx, dy = self.dirs[self.agent_dir_idx]
            new_x = self.agent_pos[0] + dx
            new_y = self.agent_pos[1] + dy

            if (new_x < 0 or new_x >= self.width or 
                new_y < 0 or new_y >= self.height or 
                (new_x, new_y) in self.walls):
                self.score -= 5
            else:
                self.agent_pos = [new_x, new_y]

        tuple_pos = tuple(self.agent_pos)

        if tuple_pos in self.toxic_traps:
            self.score -= 15

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


class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        if percept['food_here']:
            return 'suck'
        elif percept['wall_ahead']:
            return 'turn_left'
        else:
            return 'move_forward'


class ModelBasedAgent:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.dir_idx = 0  # Relative orientation tracking
        self.dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self.visited_cells = {(0, 0)}
        self.last_action = None
        self.was_wall_ahead = False

    def sense_and_act(self, percept: dict) -> str:
        if self.last_action == 'turn_left':
            self.dir_idx = (self.dir_idx - 1) % 4
        elif self.last_action == 'turn_right':
            self.dir_idx = (self.dir_idx + 1) % 4
        elif self.last_action == 'move_forward':
            if not self.was_wall_ahead:
                dx, dy = self.dirs[self.dir_idx]
                self.x += dx
                self.y += dy
                self.visited_cells.add((self.x, self.y))

        self.was_wall_ahead = percept['wall_ahead']

        if percept['food_here']:
            action = 'suck'
        else:
            ahead_dir = self.dir_idx
            left_dir = (self.dir_idx - 1) % 4
            right_dir = (self.dir_idx + 1) % 4

            ahead_pos = (self.x + self.dirs[ahead_dir][0], self.y + self.dirs[ahead_dir][1])
            left_pos = (self.x + self.dirs[left_dir][0], self.y + self.dirs[left_dir][1])
            right_pos = (self.x + self.dirs[right_dir][0], self.y + self.dirs[right_dir][1])

            left_valid = not percept['wall_left']
            right_valid = not percept['wall_right']
            ahead_valid = not percept['wall_ahead']

            left_unvisited = left_valid and (left_pos not in self.visited_cells)
            right_unvisited = right_valid and (right_pos not in self.visited_cells)
            ahead_unvisited = ahead_valid and (ahead_pos not in self.visited_cells)

            if ahead_unvisited:
                action = 'move_forward'
            elif left_unvisited:
                action = 'turn_left'
            elif right_unvisited:
                action = 'turn_right'
            elif ahead_valid:
                action = 'move_forward'
            elif left_valid:
                action = 'turn_left'
            elif right_valid:
                action = 'turn_right'
            else:
                action = 'turn_left'

        self.last_action = action
        return action


class GridGameGUI:
    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, num_traps=3, walls=None, agent_type="model"):
        self.root = root
        self.root.title("IT3012 - Partially Observable Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents, num_traps=num_traps, custom_walls=walls)

        if agent_type == "reflex":
            self.agent = SimpleReflexAgent()
        else:
            self.agent = ModelBasedAgent()

        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066", fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white", font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b", outline="#d97706")

        for tx, ty in self.env.toxic_traps:
            x1 = tx * self.cell_size
            y1 = (self.env.height - 1 - ty) * self.cell_size
            points = [
                x1 + self.cell_size / 2, y1 + self.cell_size * 0.2,
                x1 + self.cell_size * 0.2, y1 + self.cell_size * 0.8,
                x1 + self.cell_size * 0.8, y1 + self.cell_size * 0.8
            ]
            self.canvas.create_polygon(points, fill="#7e22ce", outline="#581c87")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000", outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066", outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Change agent_type to "reflex" to demonstrate failure/trap loop, or "model" to run ModelBasedAgent
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0, num_traps=4, agent_type="model")
    root.mainloop()