import rclpy
from autonomous_patrol_system.msg import AnomalyEvent
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class EnvironmentMonitorNode(Node):
    def __init__(self):
        super().__init__('environment_monitor_node')

        # --- Parameters ---
        self.declare_parameter('min_distance_threshold', 0.3)  # meters
        self.declare_parameter('anomaly_duration_threshold', 1.0)  # seconds
        self.declare_parameter('scan_topic', '/scan')

        self.min_dist = self.get_parameter('min_distance_threshold').value
        self.duration_thresh = self.get_parameter('anomaly_duration_threshold').value
        scan_topic = self.get_parameter('scan_topic').value

        # --- State ---
        self.anomaly_start_time = None
        self.anomaly_active = False

        # --- Publishers/Subscribers ---
        self.anomaly_pub = self.create_publisher(AnomalyEvent, '/anomaly/detected', 10)
        self.scan_sub = self.create_subscription(LaserScan, scan_topic, self.scan_callback, 10)

        self.get_logger().info('Environment Monitor initialized')

    def scan_callback(self, msg: LaserScan):
        """Check LiDAR ranges for obstacles within threshold."""
        # Filter valid ranges (ignore inf/nan)
        valid_ranges = [r for r in msg.ranges if msg.range_min <= r <= msg.range_max]
        if not valid_ranges:
            return

        min_range = min(valid_ranges)

        if min_range < self.min_dist:
            now = self.get_clock().now()
            if not self.anomaly_active:
                self.anomaly_start_time = now
                self.anomaly_active = True
            elif (now - self.anomaly_start_time).nanoseconds / 1e9 >= self.duration_thresh:
                # Publish anomaly event
                event = AnomalyEvent()
                event.header.stamp = now.to_msg()
                event.header.frame_id = msg.header.frame_id
                event.detected_distance = min_range
                event.anomaly_type = 'obstacle_proximity'
                event.severity = 1 if min_range < 0.15 else 2  # 1=critical, 2=warning
                self.anomaly_pub.publish(event)
                self.get_logger().warn(f'Anomaly detected: {min_range:.2f}m')
                # Reset to avoid spam
                self.anomaly_active = False
        else:
            self.anomaly_active = False
            self.anomaly_start_time = None


def main(args=None):
    rclpy.init(args=args)
    node = EnvironmentMonitorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
