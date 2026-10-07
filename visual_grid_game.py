import random
import tkinter as tk

from agent import SearchAgent


class VisualGridHuntGame:
    """Practical 04 visual environment with BFS, DFS, UCS and A* search."""

    DIRECTIONS = {
        'Up': (0, 1),
        'Down': (0, -1),
        'Left': (-1, 0),
        'Right': (1, 0),
    }

    def __init__(self, width=8, height=8, num_food=8, custom_walls=None, seed=7):
        if seed is not None:
            random.seed(seed)

        self.width = width
        self.height = height
        self.agent_pos = [0, 0]

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7),
            }

        self.food_positions = set()

        while len(self.food_positions) < num_food:
            pos = (
                random.randint(0, width - 1),
                random.randint(0, height - 1),
            )

            if pos != (0, 0) and pos not in self.walls:
                self.food_positions.add(pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self):
        """
        Practical 03 gives the SearchAgent the world model needed
        for offline planning.
        """
        return {
            'grid_size': (self.width, self.height),
            'walls': list(self.walls),
            'all_food': list(self.food_positions),
        }

    def execute_action(self, action):
        self.steps += 1

        if action not in self.DIRECTIONS:
            return

        dx, dy = self.DIRECTIONS[action]

        new_pos = [
            max(0, min(self.width - 1, self.agent_pos[0] + dx)),
            max(0, min(self.height - 1, self.agent_pos[1] + dy)),
        ]

        if tuple(new_pos) in self.walls:
            self.score -= 5
            self.collision = True
            return

        self.agent_pos = new_pos

        current_position = tuple(self.agent_pos)

        if current_position in self.food_positions:
            self.food_positions.remove(current_position)
            self.score += 20

    def is_done(self):
        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


class GridGameGUI:
    """Practical 03 GUI"""

    def __init__(self, root, width=8, height=8, num_food=8, seed=7):
        self.root = root
        self.width = width
        self.height = height
        self.num_food = num_food
        self.seed = seed

        self.agent = None
        self.running = False

        self.root.title('IT3012 Practical 04 - Informed Search')
        self.root.geometry('650x760')
        self.root.resizable(False, False)

        self.title_label = tk.Label(
            root,
            text='Practical 04: Informed Search',
            font=('Arial', 16, 'bold'),
            width=60,
            height=2,
        )
        self.title_label.pack()

        self.canvas = tk.Canvas(
            root,
            width=520,
            height=520,
            bg='white',
            highlightthickness=1,
        )
        self.canvas.pack(pady=5)

        self.info_label = tk.Label(
            root,
            text=' ',
            font=('Arial', 10),
            width=85,
            height=4,
            anchor='center',
            justify='center',
            wraplength=620,
        )
        self.info_label.pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        self.bfs_button = tk.Button(
            button_frame,
            text='Run BFS',
            command=lambda: self.start_agent('BFS'),
            font=('Arial', 10),
            width=12,
        )
        self.bfs_button.pack(side=tk.LEFT, padx=4)

        self.dfs_button = tk.Button(
            button_frame,
            text='Run DFS',
            command=lambda: self.start_agent('DFS'),
            font=('Arial', 10),
            width=12,
        )
        self.dfs_button.pack(side=tk.LEFT, padx=4)

        self.ucs_button = tk.Button(
            button_frame,
            text='Run UCS',
            command=lambda: self.start_agent('UCS'),
            font=('Arial', 10),
            width=12,
        )
        self.ucs_button.pack(side=tk.LEFT, padx=4)

        self.astar_button = tk.Button(
            button_frame,
            text='Run A*',
            command=lambda: self.start_agent('AStar'),
            font=('Arial', 10),
            width=12,
        )
        self.astar_button.pack(side=tk.LEFT, padx=4)

        self.reset_button = tk.Button(
            button_frame,
            text='Reset',
            command=self.reset,
            font=('Arial', 10),
            width=10,
        )
        self.reset_button.pack(side=tk.LEFT, padx=4)

        self.reset()

    def reset(self):
        self.running = False
        self.agent = None

        self.env = VisualGridHuntGame(
            width=self.width,
            height=self.height,
            num_food=self.num_food,
            seed=self.seed,
        )

        self.bfs_button.config(state='normal')
        self.dfs_button.config(state='normal')
        self.ucs_button.config(state='normal')
        self.astar_button.config(state='normal')

        self.title_label.config(
            text='Practical 04 - Informed Search'
        )

        self.info_label.config(
            text=' '
        )

        self.draw_grid()

    def start_agent(self, algorithm):
        if self.running:
            return

        self.reset()

        self.agent = SearchAgent()
        self.agent.active_algo = algorithm

        self.running = True

        self.bfs_button.config(state='disabled')
        self.dfs_button.config(state='disabled')
        self.ucs_button.config(state='disabled')
        self.astar_button.config(state='disabled')

        self.title_label.config(
            text=f'Practical 04 - {algorithm}'
        )

        self.info_label.config(
            text=f'{algorithm} selected. Planning and executing...'
        )

        self.step()

    def step(self):
        if not self.running:
            return

        if not self.env.is_done():
            percept = self.env.get_percept()

            action = self.agent.sense_and_act(percept)

            self.env.execute_action(action)

            self.draw_grid()

            plan_length = len(self.agent.plan)

            self.info_label.config(
                text=(
                    f'Algorithm: {self.agent.active_algo}\n'
                    f'Action: {action} | '
                    f'Steps: {self.env.steps} | '
                    f'Score: {self.env.score}\n'
                    f'Food left: {len(self.env.food_positions)} | '
                    f'Plan remaining: {plan_length}'
                )
            )

            self.root.after(250, self.step)

        else:
            self.running = False

            if len(self.env.food_positions) == 0:
                result = 'All food collected!'
            elif self.env.collision:
                result = 'Collision occurred.'
            else:
                result = '60-step limit reached.'

            self.info_label.config(
                text=(
                    f'Finished: {result}\n'
                    f'Algorithm: {self.agent.active_algo} | '
                    f'Final Score: {self.env.score}\n'
                    f'Steps: {self.env.steps} | '
                    f'Food left: {len(self.env.food_positions)}'
                )
            )

            self.bfs_button.config(state='normal')
            self.dfs_button.config(state='normal')
            self.ucs_button.config(state='normal')
            self.astar_button.config(state='normal')

    def draw_grid(self):
        self.canvas.delete('all')

        cell = 520 // max(self.env.width, self.env.height)

        # Draw grid and walls
        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * cell
                y1 = (self.env.height - 1 - y) * cell
                x2 = x1 + cell
                y2 = y1 + cell

                if (x, y) in self.env.walls:
                    fill = '#64748b'
                else:
                    fill = '#f1f5f9'

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill,
                    outline='#cbd5e1',
                )

        # Draw food
        for fx, fy in self.env.food_positions:
            offset = cell * 0.25

            x1 = fx * cell + offset
            y1 = (self.env.height - 1 - fy) * cell + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + cell * 0.5,
                y1 + cell * 0.5,
                fill='#f59e0b',
                outline='#d97706',
            )

        # Draw agent
        ax, ay = self.env.agent_pos

        offset = cell * 0.15

        x1 = ax * cell + offset
        y1 = (self.env.height - 1 - ay) * cell + offset

        self.canvas.create_oval(
            x1,
            y1,
            x1 + cell * 0.7,
            y1 + cell * 0.7,
            fill='#000066',
            outline='#1e3a8a',
        )


if __name__ == '__main__':
    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=8,
        height=8,
        num_food=8,
        seed=7,
    )

    root.mainloop()