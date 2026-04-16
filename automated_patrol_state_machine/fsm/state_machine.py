from .states.patrol_state import PatrolState

class StateMachine:
    def __init__(self, context):
        self.context = context

        # Register states
        self.states = {
            "PATROL": PatrolState(),
        }

        self.current_state = self.states["PATROL"]
        self.current_state.enter(context)

    def update(self):
        """
        Called repeatedly by ROS node
        """

        next_state_name = self.current_state.execute(self.context)

        if next_state_name != self.current_state.name:
            self.transition(next_state_name)

    def transition(self, next_state_name):
        self.current_state.exit(self.context)

        self.current_state = self.states[next_state_name]
        self.current_state.enter(self.context)
