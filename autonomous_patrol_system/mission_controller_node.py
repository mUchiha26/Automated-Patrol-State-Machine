import rclpy
from autonomous_patrol_system.msg import AlertMessage, MissionStatus
from autonomous_patrol_system.srv import ResumePatrol
from rclpy.node import Node
from std_msgs.msg import Bool


class MissionControllerNode(Node):
    def __init__(self):
        super().__init__('mission_controller_node')

        # --- Parameters ---
        self.declare_parameter('task_timeout', 30.0)
        self.declare_parameter('max_retries', 3)
        self.declare_parameter('initial_state', 'PATROLLING')

        # --- State Machine ---
        self.mission_state = self.get_parameter('initial_state').value
        self.current_task = None
        self.retry_count = 0
        self.task_start_time = None

        # --- Publishers/Subscribers ---
        self.status_pub = self.create_publisher(MissionStatus, '/mission/status', 10)
        self.alert_sub = self.create_subscription(
            AlertMessage, '/patrol/alerts', self.alert_callback, 10
        )
        self.resume_sub = self.create_subscription(
            Bool, '/mission/resume_trigger', self.resume_callback, 10
        )

        # --- Service ---
        self.resume_srv = self.create_service(
            ResumePatrol, 'resume_patrol', self.resume_service_callback
        )

        # Publish initial status
        self._publish_status()
        self.get_logger().info(f'Mission Controller initialized in state: {self.mission_state}')

    def alert_callback(self, msg: AlertMessage):
        """Handle incoming alerts: pause patrol, trigger evidence capture."""
        if self.mission_state == 'PATROLLING':
            self.get_logger().warn(f'Alert received: {msg.message}. Pausing patrol.')
            self.mission_state = 'ANOMALY_HANDLING'
            self.current_task = 'handle_anomaly'
            self.task_start_time = self.get_clock().now()
            self._publish_status()
            # In full system: trigger evidence_capture_node via service call here

    def resume_callback(self, msg: Bool):
        """External trigger to resume patrol."""
        if msg.data and self.mission_state in ['ANOMALY_HANDLING', 'RECOVERING']:
            self.get_logger().info('Resume signal received. Resuming patrol.')
            self.mission_state = 'PATROLLING'
            self.current_task = None
            self.retry_count = 0
            self._publish_status()

    def resume_service_callback(self, request, response):
        """Service interface for resume."""
        if self.mission_state in ['ANOMALY_HANDLING', 'RECOVERING']:
            self.mission_state = 'PATROLLING'
            response.success = True
            response.message = 'Patrol resumed'
        else:
            response.success = False
            response.message = f'Cannot resume from state: {self.mission_state}'
        return response

    def _publish_status(self):
        """Publish current mission state."""
        status = MissionStatus()
        status.header.stamp = self.get_clock().now().to_msg()
        status.state = self.mission_state
        status.current_task = self.current_task or ''
        status.retry_count = self.retry_count
        status.uptime_sec = int(self.get_clock().now().nanoseconds / 1e9)
        self.status_pub.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = MissionControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
