# agent.py
class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SimpleReflexAgent:
    """A Simple Reflex Agent using only Condition-Action rules (no memory)."""
    def sense_and_act(self, percept: dict) -> str:
        if percept.get('food_here'):
            return 'suck'
        elif percept.get('wall_ahead'):
            return 'turn_left'
        else:
            return 'move_forward'


class ModelBasedAgent:
    """A Model-Based Agent that maintains an internal memory state to escape loops."""
    def __init__(self):
        self.visited_cells = set()
        self.pos = [0, 0]
        self.dir = 'Up'
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        # Update Transition Model based on last action
        if self.last_action == 'turn_left':
            dirs = ['Up', 'Left', 'Down', 'Right']
            self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        elif self.last_action == 'turn_right':
            dirs = ['Up', 'Right', 'Down', 'Left']
            self.dir = dirs[(dirs.index(self.dir) + 1) % 4]
        elif self.last_action == 'move_forward':
            if self.dir == 'Up': self.pos[1] += 1
            elif self.dir == 'Down': self.pos[1] -= 1
            elif self.dir == 'Left': self.pos[0] -= 1
            elif self.dir == 'Right': self.pos[0] += 1

        # Update Sensor Model / Memory
        current_pos_tuple = tuple(self.pos)
        self.visited_cells.add(current_pos_tuple)

        # Check if the cell to the left is visited
        left_dir = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}[self.dir]
        left_pos = list(self.pos)
        if left_dir == 'Up': left_pos[1] += 1
        elif left_dir == 'Down': left_pos[1] -= 1
        elif left_dir == 'Left': left_pos[0] -= 1
        elif left_dir == 'Right': left_pos[0] += 1
        
        left_is_visited = tuple(left_pos) in self.visited_cells

        # Condition-Action rules querying memory
        if percept.get('food_here'):
            action = 'suck'
        elif percept.get('wall_ahead'):
            # If we just turned left but there's still a wall (like in a corner),
            # keep turning left so we don't get stuck in a left-right toggle loop.
            if self.last_action == 'turn_left':
                action = 'turn_left'
            elif self.last_action == 'turn_right':
                action = 'turn_right'
            elif left_is_visited:
                action = 'turn_right'
            else:
                action = 'turn_left'
        else:
            action = 'move_forward'
            
        self.last_action = action
        return action