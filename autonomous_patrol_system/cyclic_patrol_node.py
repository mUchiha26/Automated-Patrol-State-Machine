import math

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener
from tf_transformations import quaternion_from_euler


class CyclicPatrolNode(Node):
    def __init__(self):
        super().__init__('cyclic_patrol_node')

        # --- Parameters ---
        self.declare_parameter('use_sim_time', True)
        self.declare_parameter('total_cycles', 3)
        self.declare_parameter(
            'waypoints',
            [
                [0.0, 0.0, 0.0],
                [2.0, 0.0, 90.0],
                [2.0, 2.0, 180.0],
                [0.0, 2.0, 270.0],
            ],
        )
        self.declare_parameter('waypoint_timeout', 30.0)
        self.declare_parameter('startup_timeout_sec', 60.0)

        self.total_cycles = int(self.get_parameter('total_cycles').value)
        self.waypoint_timeout = float(self.get_parameter('waypoint_timeout').value)
        self.startup_timeout_sec = float(self.get_parameter('startup_timeout_sec').value)
        raw_waypoints = self.get_parameter('waypoints').value
        self.waypoints = self._validate_waypoints(raw_waypoints)

        self.get_logger().info(
            (
                f'Patrol node started. cycles={self.total_cycles}, '
                f'waypoints={len(self.waypoints)}, timeout={self.waypoint_timeout:.1f}s'
            )
        )

        # --- Runtime state ---
        self.current_cycle = 0
        self.current_waypoint_index = 0
        self.mission_active = False

        # TF readiness is required before sending map-framed goals to Nav2.
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)

        # --- Action Client Setup ---
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # Wait for Nav2 action and map->base_link TF to avoid "frame does not exist" failures.
        self._wait_for_nav2_readiness(self.startup_timeout_sec)
        self.get_logger().info('Nav2 and TF are ready. Starting Patrol.')

        # Start the mission
        self.send_next_goal()

    def _validate_waypoints(self, raw_waypoints):
        """Normalize waypoints into [[x, y, yaw_deg], ...] and fail fast on bad input."""
        if not isinstance(raw_waypoints, list) or not raw_waypoints:
            raise ValueError('Parameter "waypoints" must be a non-empty list')

        validated = []
        for idx, wp in enumerate(raw_waypoints, start=1):
            if not isinstance(wp, list) or len(wp) != 3:
                raise ValueError(f'Waypoint {idx} must be [x, y, yaw_deg]')
            x, y, yaw = wp
            validated.append([float(x), float(y), float(yaw)])
        return validated

    def _wait_for_nav2_readiness(self, timeout_sec):
        """Wait until Nav2 action server and map->base_link TF are available."""
        self.get_logger().info('Waiting for Nav2 action server and map->base_link transform...')
        deadline = self.get_clock().now() + Duration(seconds=timeout_sec)

        while rclpy.ok() and self.get_clock().now() < deadline:
            action_ready = self._action_client.wait_for_server(timeout_sec=0.5)
            tf_ready = self._tf_buffer.can_transform(
                'map',
                'base_link',
                Time(),
                timeout=Duration(seconds=0.1),
            )

            if action_ready and tf_ready:
                return

            # Keep processing subscriptions while waiting.
            rclpy.spin_once(self, timeout_sec=0.1)

        raise RuntimeError(
            (
                'Timed out waiting for Nav2 readiness. Missing action server or map->base_link TF. '
                'Set initial pose in RViz or publish /initialpose, then relaunch.'
            )
        )

    def get_pose_stamped(self, x, y, yaw_deg):
        """Helper to create a PoseStamped message with correct orientation."""
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0

        # Convert Yaw (degrees) to Quaternion
        yaw_rad = math.radians(yaw_deg)
        q = quaternion_from_euler(0.0, 0.0, yaw_rad)
        pose.pose.orientation.x = q[0]
        pose.pose.orientation.y = q[1]
        pose.pose.orientation.z = q[2]
        pose.pose.orientation.w = q[3]

        return pose

    def send_next_goal(self):
        """Sends the next waypoint goal to Nav2."""

        # Check if mission is complete
        if self.current_cycle >= self.total_cycles:
            self.get_logger().info('*** PATROL MISSION COMPLETE ***')
            self.mission_active = False
            return

        # Get current waypoint coordinates
        wp = self.waypoints[self.current_waypoint_index]
        goal_pose = self.get_pose_stamped(wp[0], wp[1], wp[2])

        # Create the goal object
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = goal_pose

        self.get_logger().info(f'Sending Goal: Cycle {self.current_cycle + 1}/{self.total_cycles}, Waypoint {self.current_waypoint_index + 1}')

        # Send goal asynchronously
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """Handles the response when a goal is accepted/rejected."""
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by Nav2')
            return

        self.get_logger().info('Goal accepted by Nav2, waiting for result...')

        # Wait for the result
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """Handles the result when the robot arrives at the waypoint."""
        nav_result = future.result()
        status = nav_result.status

        # GoalStatus.STATUS_SUCCEEDED is the canonical successful action status.
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'Waypoint {self.current_waypoint_index + 1} Reached Successfully.')

            # Move to next waypoint
            self.current_waypoint_index += 1

            # Check if cycle is complete
            if self.current_waypoint_index >= len(self.waypoints):
                self.current_waypoint_index = 0  # Reset to first waypoint
                self.current_cycle += 1
                self.get_logger().info(f'--- Cycle {self.current_cycle} Complete ---')

            # Send next goal immediately
            self.send_next_goal()
        else:
            self.get_logger().error(f'Navigation failed with status={status}')
            # Optional: Add retry logic here


def main(args=None):
    rclpy.init(args=args)
    node = CyclicPatrolNode()

    # Keep the node alive while the async callbacks handle the logic
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
