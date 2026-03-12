import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from autonomous_patrol_system.msg import AnomalyEvent, AlertMessage


class AlertDispatcherNode(Node):
    def __init__(self):
        super().__init__('alert_dispatcher_node')

        # --- Parameters ---
        self.declare_parameter('alert_topic', '/patrol/alerts')
        self.declare_parameter('enable_external_forwarding', False)

        alert_topic = self.get_parameter('alert_topic').value
        self.forward_external = self.get_parameter('enable_external_forwarding').value

        # --- Publishers ---
        self.alert_pub = self.create_publisher(AlertMessage, alert_topic, 10)
        if self.forward_external:
            self.external_pub = self.create_publisher(String, '/external/alert_bridge', 10)

        # --- Subscriber ---
        self.anomaly_sub = self.create_subscription(
            AnomalyEvent, '/anomaly/detected', self.anomaly_callback, 10
        )

        self.get_logger().info('Alert Dispatcher listening on /anomaly/detected')

    def anomaly_callback(self, msg: AnomalyEvent):
        """Convert AnomalyEvent to AlertMessage and publish."""
        alert = AlertMessage()
        alert.header = msg.header
        alert.severity = msg.severity
        alert.source_node = 'environment_monitor_node'
        alert.message = f"{msg.anomaly_type}: {msg.description or 'Proximity alert'}"
        alert.payload = f"distance:{msg.detected_distance:.2f}"

        self.alert_pub.publish(alert)
        self.get_logger().info(f'Alert published: {alert.message}')

        if self.forward_external:
            ext_msg = String(data=f"[ALERT] {alert.message}")
            self.external_pub.publish(ext_msg)


def main(args=None):
    rclpy.init(args=args)
    node = AlertDispatcherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
