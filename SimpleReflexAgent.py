
# ----------------------------------------------------------------------
# Step 1.2 – Simple Reflex Agent (NO memory)
# ----------------------------------------------------------------------
class SimpleReflexAgent:
    """
    Pure condition-action rules. No internal state / history.
    This agent will get stuck in loops under partial observability.
    """

    def sense_and_act(self, percept: dict) -> str:
        # Condition-Action Rules (exactly as discussed in Lecture 02)
        if percept['food_here']:
            return 'Stay'                 # "suck" equivalent – just stand on the food

        if not percept['wall_ahead']:
            return 'MoveForward'

        # Wall ahead → try to turn
        if not percept['wall_left']:
            return 'TurnLeft'
        if not percept['wall_right']:
            return 'TurnRight'

        # Completely blocked → turn around
        return 'TurnLeft'
