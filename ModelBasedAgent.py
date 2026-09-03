# ----------------------------------------------------------------------
# Step 1.3 – Model-Based Agent (WITH internal state / memory)
# ----------------------------------------------------------------------
class ModelBasedAgent:
    """
    Maintains an internal model of the world (visited cells + recent actions).
    Uses that model to break out of loops.
    """

    def __init__(self):
        # Internal state (Transition Model + Sensor Model)
        self.visited = set()                 # relative visited cells
        self.relative_pos = (0, 0)           # agent's own coordinate system
        self.facing = 0                      # 0=Right, 1=Up, 2=Left, 3=Down
        self.last_action = None
        self.recent_actions = deque(maxlen=8)  # short-term memory to detect cycles
        self.stuck_counter = 0

    def _update_state(self, percept: dict):
        """Transition Model + Sensor Model update"""
        # Record current relative cell as visited
        self.visited.add(self.relative_pos)

        # Update relative position based on last action
        if self.last_action == 'MoveForward':
            dx, dy = VisualGridHuntGame.DIRECTIONS[self.facing]
            self.relative_pos = (self.relative_pos[0] + dx,
                                 self.relative_pos[1] + dy)
        elif self.last_action == 'TurnLeft':
            self.facing = (self.facing + 1) % 4
        elif self.last_action == 'TurnRight':
            self.facing = (self.facing - 1) % 4

        # Keep recent action history (helps detect oscillation)
        if self.last_action:
            self.recent_actions.append(self.last_action)

    def sense_and_act(self, percept: dict) -> str:
        # 1. Update internal model first
        self._update_state(percept)

        # 2. Decision rules that now query memory
        if percept['food_here']:
            action = 'Stay'
        elif not percept['wall_ahead']:
            # Prefer unvisited cells ahead
            dx, dy = VisualGridHuntGame.DIRECTIONS[self.facing]
            next_cell = (self.relative_pos[0] + dx, self.relative_pos[1] + dy)
            if next_cell not in self.visited:
                action = 'MoveForward'
            else:
                # Prefer turning toward unvisited side
                left_f = (self.facing + 1) % 4
                ldx, ldy = VisualGridHuntGame.DIRECTIONS[left_f]
                left_cell = (self.relative_pos[0] + ldx, self.relative_pos[1] + ldy)

                right_f = (self.facing - 1) % 4
                rdx, rdy = VisualGridHuntGame.DIRECTIONS[right_f]
                right_cell = (self.relative_pos[0] + rdx, self.relative_pos[1] + rdy)

                if left_cell not in self.visited and not percept['wall_left']:
                    action = 'TurnLeft'
                elif right_cell not in self.visited and not percept['wall_right']:
                    action = 'TurnRight'
                else:
                    action = 'MoveForward'   # forced to re-visit
        else:
            # Wall ahead – use memory to choose better turn
            left_f = (self.facing + 1) % 4
            ldx, ldy = VisualGridHuntGame.DIRECTIONS[left_f]
            left_cell = (self.relative_pos[0] + ldx, self.relative_pos[1] + ldy)

            right_f = (self.facing - 1) % 4
            rdx, rdy = VisualGridHuntGame.DIRECTIONS[right_f]
            right_cell = (self.relative_pos[0] + rdx, self.relative_pos[1] + rdy)

            if left_cell not in self.visited and not percept['wall_left']:
                action = 'TurnLeft'
            elif right_cell not in self.visited and not percept['wall_right']:
                action = 'TurnRight'
            elif not percept['wall_left']:
                action = 'TurnLeft'
            elif not percept['wall_right']:
                action = 'TurnRight'
            else:
                action = 'TurnLeft'          # turn around

        # Simple cycle breaker
        if len(self.recent_actions) >= 6:
            last_six = list(self.recent_actions)[-6:]
            if last_six.count('TurnLeft') >= 4 or last_six.count('TurnRight') >= 4:
                action = 'MoveForward' if not percept['wall_ahead'] else 'TurnRight'

        self.last_action = action
        return action