import random


class GridHuntGame:
    """
    The environment keeps the true state internally, but get_percept()
    exposes only the local information required for the partially
    observable tasks.
    """

    DIRECTIONS = {
        'Up': (0, 1),
        'Down': (0, -1),
        'Left': (-1, 0),
        'Right': (1, 0),
    }

    def __init__(self, width=8, height=8, seed=7, custom_walls=None, num_food=8):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]
        self.facing = 'Right'

        if seed is not None:
            random.seed(seed)

        self.walls = set(custom_walls) if custom_walls is not None else {
            (2, 2), (2, 3), (5, 5), (6, 5), (3, 7)
        }

        self.food_positions = set()
        while len(self.food_positions) < num_food:
            pos = (random.randint(0, width - 1), random.randint(0, height - 1))
            if pos != (0, 0) and pos not in self.walls:
                self.food_positions.add(pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    def _ahead_position(self):
        dx, dy = self.DIRECTIONS[self.facing]
        return (
            self.agent_pos[0] + dx,
            self.agent_pos[1] + dy
        )

    def get_percept(self) -> dict:
        """
        Return only the local percept.
        The agent does NOT receive agent_pos, score, remaining food,
        or any other global state.
        """
        ahead = self._ahead_position()

        wall_ahead = (
            ahead[0] < 0 or ahead[0] >= self.width
            or ahead[1] < 0 or ahead[1] >= self.height
            or ahead in self.walls
        )

        return {
            'wall_ahead': wall_ahead,
            'food_here': ahead in self.food_positions,
        }

    def execute_action(self, action: str):
        """
        Convert the agent's relative action into an environment action.
        """
        self.steps += 1

        if action == 'FORWARD':
            direction = self.facing

        elif action == 'LEFT':
            order = ['Up', 'Right', 'Down', 'Left']
            direction = order[(order.index(self.facing) - 1) % 4]
            self.facing = direction

        elif action == 'RIGHT':
            order = ['Up', 'Right', 'Down', 'Left']
            direction = order[(order.index(self.facing) + 1) % 4]
            self.facing = direction

        elif action in self.DIRECTIONS:
            direction = action
            self.facing = action

        else:
            direction = self.facing

        dx, dy = self.DIRECTIONS[direction]

        new_pos = [
            max(0, min(self.width - 1, self.agent_pos[0] + dx)),
            max(0, min(self.height - 1, self.agent_pos[1] + dy)),
        ]

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        current = tuple(self.agent_pos)

        if current in self.food_positions:
            self.food_positions.remove(current)
            self.score += 20

    def is_done(self):
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision
