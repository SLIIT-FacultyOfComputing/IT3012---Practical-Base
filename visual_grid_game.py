import random
import tkinter as tk
from typing import List, Set, Tuple, Dict, Any


class EnvironmentState:
    """Encapsulates physical boundaries, entities, and hazard states of the grid."""

    def __init__(self, width: int = 10, height: int = 10, num_food: int = 10, 
                 num_opponents: int = 2, num_traps: int = 5, custom_walls: Set[Tuple[int, int]] = None):
        self.width = width
        self.height = height
        self.agent_pos: List[int] = [0, 0]

        # Initialize static obstacles
        self.walls: Set[Tuple[int, int]] = set(custom_walls) if custom_walls is not None else {
            (2, 2), (2, 3), (5, 5), (6, 5), (3, 7)
        }

        # Dynamically generate non-overlapping food positions
        self.food_positions: Set[Tuple[int, int]] = self._generate_unique_positions(
            count=num_food, 
            excluded=self.walls | {(0, 0)}
        )

        # Generate adversarial opponents
        self.opponents: List[List[int]] = [
            list(pos) for pos in self._generate_unique_positions(
                count=num_opponents, 
                excluded=self.walls | self.food_positions | {(0, 0)}
            )
        ]

        # Step 2.1: Add toxic traps avoiding starting position, walls, and food
        self.toxic_traps: Set[Tuple[int, int]] = self._generate_unique_positions(
            count=num_traps,
            excluded=self.walls | self.food_positions | {tuple(op) for op in self.opponents} | {(0, 0)}
        )

    def _generate_unique_positions(self, count: int, excluded: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        positions = set()
        while len(positions) < count:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos = (fx, fy)
            if pos not in excluded:
                positions.add(pos)
        return positions


class VisualGridHuntGame:
    """Main game engine managing physics rules, step evaluation, and performance score."""

    def __init__(self, width: int = 10, height: int = 10, num_food: int = 10, 
                 num_opponents: int = 2, num_traps: int = 5, custom_walls: Set[Tuple[int, int]] = None):
        self.state = EnvironmentState(width, height, num_food, num_opponents, num_traps, custom_walls)
        self.score: int = 0
        self.steps: int = 0
        self.collision: bool = False

    @property
    def width(self) -> int:
        return self.state.width

    @property
    def height(self) -> int:
        return self.state.height

    def get_percept(self) -> Dict[str, Any]:
        """Perception Subsystem - Step 2.2: Returns sensor data including 'smells_toxin'."""
        current_pos_tuple = tuple(self.state.agent_pos)
        return {
            'agent_pos': list(self.state.agent_pos),
            'opponent_positions': [list(op) for op in self.state.opponents],
            'smells_food': current_pos_tuple in self.state.food_positions,
            'hit_wall': current_pos_tuple in self.state.walls,
            'smells_toxin': current_pos_tuple in self.state.toxic_traps,  # Step 2.2 Percept key
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.state.food_positions)
        }

    def execute_action(self, action: str) -> None:
        """Executes agent movement, opponent movement, collision detection, and score updates."""
        self.steps += 1
        new_pos = list(self.state.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.state.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.state.width - 1, new_pos[0] + 1)

        # Wall collision check
        if tuple(new_pos) in self.state.walls:
            self.score -= 5
        else:
            self.state.agent_pos = new_pos

        tuple_pos = tuple(self.state.agent_pos)

        # Food pickup
        if tuple_pos in self.state.food_positions:
            self.state.food_positions.remove(tuple_pos)
            self.score += 20

        # Step 2.3: Toxic trap interaction penalty (-15 points)
        if tuple_pos in self.state.toxic_traps:
            self.score -= 15

        # Opponents random movement & collision check
        for op in self.state.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.state.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.state.width - 1:
                op[0] += 1

            if op == self.state.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.state.food_positions) == 0 or self.steps >= 60 or self.collision


class GridGameGUI:
    """Tkinter graphical UI interface responsible purely for visual rendering."""

    def __init__(self, root: tk.Tk, width: int = 10, height: int = 10, 
                 num_food: int = 12, num_opponents: int = 2, num_traps: int = 5, walls: Set[Tuple[int, int]] = None):
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

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066", fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self) -> None:
        """Step 2.3: Renders grid entities including purple toxic trap shapes on the canvas."""
        self.canvas.delete("all")

        # Draw grid cells and walls
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.state.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                if self.cell_size >= 40 and (x, y) in self.env.state.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white", font=("Arial", 8, "bold"))

        # Step 2.3: Render Toxic Traps (Custom Purple Shapes)
        for tx, ty in self.env.state.toxic_traps:
            offset = self.cell_size * 0.2
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset
            x2 = x1 + self.cell_size * 0.6
            y2 = y1 + self.cell_size * 0.6
            self.canvas.create_oval(x1, y1, x2, y2, fill="#7e22ce", outline="#581c87")

        # Render Food
        for fx, fy in self.env.state.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b", outline="#d97706")

        # Render Opponents
        for ox, oy in self.env.state.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000", outline="#7a0000")

        # Render Agent
        ax, ay = self.env.state.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066", outline="#1e3a8a")

    def run_loop(self) -> None:
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                action = random.choice(['Up', 'Down', 'Left', 'Right'])
                self.env.execute_action(action)
                self.draw_grid()

                percept = self.env.get_percept()
                status_text = f"Score: {percept['score']} | Steps: {self.env.steps} | Action: {action}"
                if percept['smells_toxin']:
                    status_text += " | TRAP HIT! (-15)"

                self.label.config(text=status_text)
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=2, num_traps=6)
    root.mainloop()
