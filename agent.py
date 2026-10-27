# agent.py
import random


class GreedyGridAgent:
    """A simple baseline agent that moves around the grid using available percepts."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, prioritize eating
        if percept.get('food_here') or percept.get('smells_food'):
            return 'Suck' if 'food_here' in percept else random.choice(self.actions_pool)

        # Fallback movement logic handling both global and local percept schemas
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """
    Step 1.2: Simple Reflex Agent
    Uses strictly IF-THEN logic (Condition-Action rules) based exclusively 
    on immediate percepts without storing any history or internal state.
    """

    def __init__(self):
        pass  # Memoryless: Intentionally no state attributes

    def sense_and_act(self, percept: dict) -> str:
        # Condition-Action Rules (IF-THEN)
        if percept.get('food_here'):
            return 'Suck'
        elif percept.get('wall_ahead'):
            return 'TurnLeft'
        else:
            return 'MoveForward'


class ModelBasedAgent:
    """
    Step 1.3: Model-Based Agent
    Maintains an internal state (memory of visited relative positions)
    and updates a transition/sensor model to break out of infinite loops.
    """

    def __init__(self):
        self.visited_cells = set()
        self.current_pos = [0, 0]
        self.orientations = ['North', 'East', 'South', 'West']
        self.dir_idx = 0  # Starts facing North (index 0)
        self.visited_cells.add(tuple(self.current_pos))
        self.last_action = None

    def update_state(self, percept: dict):
        """Updates internal transition and sensor model based on the previous action taken."""
        if self.last_action == 'TurnLeft':
            self.dir_idx = (self.dir_idx - 1) % 4
        elif self.last_action == 'TurnRight':
            self.dir_idx = (self.dir_idx + 1) % 4
        elif self.last_action == 'MoveForward' and not percept.get('hit_wall'):
            dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][self.dir_idx]
            self.current_pos[0] += dx
            self.current_pos[1] += dy
            self.visited_cells.add(tuple(self.current_pos))

    def sense_and_act(self, percept: dict) -> str:
        # 1. Update world model using last action and current percept
        if self.last_action:
            self.update_state(percept)

        # 2. Condition-Action rules querying internal memory
        if percept.get('food_here'):
            action = 'Suck'
        elif percept.get('wall_ahead'):
            action = 'TurnRight'
        else:
            # Predict ahead position to check if already visited
            dx, dy = [(0, 1), (1, 0), (0, -1), (-1, 0)][self.dir_idx]
            next_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)
            
            # Query memory state: if visited, turn right to explore alternate paths
            if next_pos in self.visited_cells:
                action = 'TurnRight'
            else:
                action = 'MoveForward'

        self.last_action = action
        return action