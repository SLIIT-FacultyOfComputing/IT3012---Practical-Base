# ----------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------
class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=0,
                 walls=None, agent_type="model"):
        self.root = root
        self.root.title("IT3012 – Lab 02: Simple Reflex vs Model-Based Agent")

        self.env = VisualGridHuntGame(width=width, height=height,
                                      num_food=num_food,
                                      num_opponents=num_opponents,
                                      custom_walls=walls)

        # Choose agent
        if agent_type == "simple":
            self.agent = SimpleReflexAgent()
            print(">>> Running Simple Reflex Agent (expect loops)")
        else:
            self.agent = ModelBasedAgent()
            print(">>> Running Model-Based Agent (has memory)")

        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width,
                                     max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 13))
        self.label.pack(pady=8)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.btn_simple = tk.Button(btn_frame, text="Run Simple Reflex",
                                    command=lambda: self.start("simple"),
                                    font=("Arial", 11), bg="#b91c1c", fg="white")
        self.btn_simple.pack(side=tk.LEFT, padx=6)

        self.btn_model = tk.Button(btn_frame, text="Run Model-Based",
                                   command=lambda: self.start("model"),
                                   font=("Arial", 11), bg="#000066", fg="white")
        self.btn_model.pack(side=tk.LEFT, padx=6)

        self.draw_grid()

    def start(self, agent_type):
        # Reset environment
        self.env = VisualGridHuntGame(width=self.env.width, height=self.env.height,
                                      num_food=12, num_opponents=0)
        if agent_type == "simple":
            self.agent = SimpleReflexAgent()
            print("\n>>> Simple Reflex Agent started")
        else:
            self.agent = ModelBasedAgent()
            print("\n>>> Model-Based Agent started")

        self.btn_simple.config(state="disabled")
        self.btn_model.config(state="disabled")
        self.run_loop()

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

                if self.cell_size >= 30 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2,
                                            y1 + self.cell_size / 2,
                                            text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        # Food
        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1,
                                    x1 + self.cell_size * 0.5,
                                    y1 + self.cell_size * 0.5,
                                    fill="#f59e0b", outline="#d97706")

        # Opponents
        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1,
                                         x1 + self.cell_size * 0.6,
                                         y1 + self.cell_size * 0.6,
                                         fill="#990000", outline="#7a0000")

        # Agent (with facing indicator)
        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1,
                                x1 + self.cell_size * 0.7,
                                y1 + self.cell_size * 0.7,
                                fill="#000066", outline="#1e3a8a")

        # Small triangle showing facing direction
        cx = x1 + self.cell_size * 0.35
        cy = y1 + self.cell_size * 0.35
        size = self.cell_size * 0.18
        dx, dy = VisualGridHuntGame.DIRECTIONS[self.env.facing]
        # Note: canvas y is inverted
        self.canvas.create_line(cx, cy,
                                cx + dx * size * 2,
                                cy - dy * size * 2,
                                fill="white", width=2, arrow=tk.LAST)

    def run_loop(self):
        def step():
            if not self.env.is_done():
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(
                    text=f"Score: {self.env.score} | Steps: {self.env.steps} | "
                         f"Action: {action} | Food left: {len(self.env.food_positions)}"
                )
                self.root.after(180, step)
            else:
                end_text = (f"Collision! Final Score: {self.env.score}"
                            if self.env.collision
                            else f"Finished! Final Score: {self.env.score}  "
                                 f"(Food left: {len(self.env.food_positions)})")
                self.label.config(text=end_text)
                self.btn_simple.config(state="normal")
                self.btn_model.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # 10×10 grid with a deliberate U-shaped trap is perfect for demonstrating failure
    app = GridGameGUI(root, width=10, height=10, num_food=12, num_opponents=0,
                      agent_type="model")
    root.mainloop()