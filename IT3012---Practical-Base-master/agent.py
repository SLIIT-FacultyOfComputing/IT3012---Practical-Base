import random

class SimpleReflexAgent:
    """Step 1.2: Simple Reflex Agent using strict Condition-Action rules (no memory)[cite: 3]."""
    def sense_and_act(self, percept: dict) -> str:
        wall = percept['wall_ahead']
        food = percept['food_nearby']

        # Condition-Action Rules mapped to available moves[cite: 3]
        if food['Up'] and not wall['Up']:
            return 'Up'
        elif food['Right'] and not wall['Right']:
            return 'Right'
        elif food['Down'] and not wall['Down']:
            return 'Down'
        elif food['Left'] and not wall['Left']:
            return 'Left'
        
        # Default reflex actions (will intentionally cause infinite loops in U-shapes)[cite: 3]
        if not wall['Up']:
            return 'Up'
        elif not wall['Right']:
            return 'Right'
        elif not wall['Down']:
            return 'Down'
        else:
            return 'Left'


class ModelBasedAgent:
    """Step 1.3: Model-Based Agent with internal memory tracking visited paths[cite: 3]."""
    def __init__(self):
        # Initialize internal state[cite: 3]
        self.visited_cells = set()
        self.current_pos = (0, 0)

    def sense_and_act(self, percept: dict) -> str:
        # Update transition state internal tracking[cite: 3]
        self.visited_cells.add(self.current_pos)
        wall = percept['wall_ahead']
        x, y = self.current_pos

        dirs = {
            'Up': (x, y + 1),
            'Right': (x + 1, y),
            'Down': (x, y - 1),
            'Left': (x - 1, y)
        }

        # Query memory: IF valid move AND NOT visited THEN choose[cite: 3]
        unvisited = [d for d in ['Up', 'Right', 'Down', 'Left'] if not wall[d] and dirs[d] not in self.visited_cells]

        if unvisited:
            chosen = unvisited[0]
        else:
            # Fallback if trapped
            valid_moves = [d for d in ['Up', 'Right', 'Down', 'Left'] if not wall[d]]
            chosen = valid_moves[0] if valid_moves else 'Up'

        self.current_pos = dirs[chosen]
        return chosen