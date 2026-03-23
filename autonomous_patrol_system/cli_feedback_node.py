import sys

import rclpy
from autonomous_patrol_system.msg import AlertMessage, AnomalyEvent
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from std_msgs.msg import String


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class CLIFeedbackNode(Node):
    def __init__(self):
        super().__init__('cli_feedback_node')

        # --- Parameters ---
        self.declare_parameter('verbosity', 'info')  # debug, info, warn, error
        self.declare_parameter('use_colors', sys.stdout.isatty())

        self.verbosity = self.get_parameter('verbosity').value
        self.use_colors = self.get_parameter('use_colors').value

        # --- Subscribers (best-effort for live feedback) ---
        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, depth=10)

        self.create_subscription(AlertMessage, '/patrol/alerts', self.alert_callback, qos)
        self.create_subscription(AnomalyEvent, '/anomaly/detected', self.anomaly_callback, qos)
        self.create_subscription(String, '/patrol/status', self.status_callback, qos)

        self.get_logger().info('CLI Feedback node active')

    def _print(self, level: str, message: str, color: str = None):
        """Print formatted message respecting verbosity and color settings."""
        levels = {'debug': 0, 'info': 1, 'warn': 2, 'error': 3}
        if levels.get(self.verbosity, 1) > levels.get(level, 1):
            return

        prefix = f"[{level.upper()}]"
        if self.use_colors and color:
            print(f"{color}{prefix} {message}{Colors.ENDC}", flush=True)
        else:
            print(f"{prefix} {message}", flush=True)

    def alert_callback(self, msg: AlertMessage):
        color = (
            Colors.FAIL
            if msg.severity == 1
            else Colors.WARNING if msg.severity == 2 else Colors.OKCYAN
        )
        self._print('warn', f"ALERT {msg.message} (src:{msg.source_node})", color)

    def anomaly_callback(self, msg: AnomalyEvent):
        self._print(
            'info',
            f"ANOMALY {msg.anomaly_type} @ {msg.detected_distance:.2f}m",
            Colors.OKBLUE,
        )

    def status_callback(self, msg: String):
        self._print('info', f"STATUS {msg.data}", Colors.OKGREEN)


def main(args=None):
    rclpy.init(args=args)
    node = CLIFeedbackNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
