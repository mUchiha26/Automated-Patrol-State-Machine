import rclpy
from rclpy.node import Node

from automated_patrol_state_machine.fsm.state_machine import StateMachine


class PatrolExecutorNode(Node):
    def __init__(self):
        super().__init__('patrol_executor_node')

        # Fake robot state (for learning)
        self.obstacle_detected = False

        # FSM
        self.fsm = StateMachine(self)

        # Timer = main loop (10 Hz)
        self.timer = self.create_timer(0.1, self.loop)

        self.get_logger().info("Patrol Executor Node started")

    def loop(self):
        """
        Main control loop
        """
        self.fsm.update()

        # Simulated sensor toggle (for testing)
        self.obstacle_detected = not self.obstacle_detected


def main(args=None):
    rclpy.init(args=args)
    node = PatrolExecutorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
