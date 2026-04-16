from ..state import State

class PatrolState(State):
    def __init__(self):
        super().__init__("PATROL")

    def enter(self, context):
        context.get_logger().info("Entering PATROL state")

    def execute(self, context):
        """
        Here we simulate patrol behavior.
        Later: send velocity commands to robot.
        """
        context.get_logger().info("Patrolling...")

        # Example simple transition condition
        if context.obstacle_detected:
            return "RECOVERY"

        return "PATROL"

    def exit(self, context):
        context.get_logger().info("Exiting PATROL state")
