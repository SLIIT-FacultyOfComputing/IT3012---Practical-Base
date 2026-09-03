import random
import tkinter as tk
from collections import deque


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    # Direction vectors: 0=Right, 1=Up, 2=Left, 3=Down
    DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    DIR_NAMES = ['Right', 'Up', 'Left', 'Down']

    def __init__(self, width=10, height=10, num_food=10, num_opponents=0, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]          # Starting position (x, y)
        self.facing = 0                  # 0=Right, 1=Up, 2=Left, 3=Down

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Create a U-shaped trap and some scattered walls so Simple Reflex fails
            self.walls = {
                (2, 1), (2, 2), (2, 3),
                (3, 1),
                (4, 1), (4, 2), (4, 3),
                (6, 5), (7, 5), (8, 5),
                (1, 7), (2, 7), (3, 7)
            }

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents (set to 0 for clearer observation of agent behaviour)
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if (tuple(op_pos) != (0, 0)
                    and tuple(op_pos) not in self.walls
                    and tuple(op_pos) not in self.food_positions):
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False
        self.last_action = None

    def get_percept(self) -> dict:
        """
        PARTIAL OBSERVABILITY (Step 1.1)
        Returns only local sensor information – no global coordinates.
        """
        dx, dy = self.DIRECTIONS[self.facing]
        ahead_x = self.agent_pos[0] + dx
        ahead_y = self.agent_pos[1] + dy

        # Check wall ahead (also treat out-of-bounds as wall)
        wall_ahead = (
            ahead_x < 0 or ahead_x >= self.width or
            ahead_y < 0 or ahead_y >= self.height or
            (ahead_x, ahead_y) in self.walls
        )

        food_here = tuple(self.agent_pos) in self.food_positions

        # Optional: also sense left and right (helps Model-Based Agent)
        left_facing = (self.facing + 1) % 4
        ldx, ldy = self.DIRECTIONS[left_facing]
        left_x, left_y = self.agent_pos[0] + ldx, self.agent_pos[1] + ldy
        wall_left = (
            left_x < 0 or left_x >= self.width or
            left_y < 0 or left_y >= self.height or
            (left_x, left_y) in self.walls
        )

        right_facing = (self.facing - 1) % 4
        rdx, rdy = self.DIRECTIONS[right_facing]
        right_x, right_y = self.agent_pos[0] + rdx, self.agent_pos[1] + rdy
        wall_right = (
            right_x < 0 or right_x >= self.width or
            right_y < 0 or right_y >= self.height or
            (right_x, right_y) in self.walls
        )

        return {
            'wall_ahead': wall_ahead,
            'wall_left': wall_left,
            'wall_right': wall_right,
            'food_here': food_here,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions),
            'steps': self.steps
        }

    def execute_action(self, action: str):
        """
        Actions the agent can take:
          - 'MoveForward'
          - 'TurnLeft'
          - 'TurnRight'
          - 'Stay' (optional)
        """
        self.steps += 1
        self.last_action = action

        if action == 'TurnLeft':
            self.facing = (self.facing + 1) % 4
        elif action == 'TurnRight':
            self.facing = (self.facing - 1) % 4
        elif action == 'MoveForward':
            dx, dy = self.DIRECTIONS[self.facing]
            new_pos = [self.agent_pos[0] + dx, self.agent_pos[1] + dy]

            # Stay in bounds and avoid walls
            if (0 <= new_pos[0] < self.width and
                    0 <= new_pos[1] < self.height and
                    tuple(new_pos) not in self.walls):
                self.agent_pos = new_pos
            else:
                self.score -= 5          # bump into wall penalty
        # 'Stay' does nothing

        # Collect food
        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        # Move opponents (if any)
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
        return len(self.food_positions) == 0 or self.steps >= 80 or self.collision






