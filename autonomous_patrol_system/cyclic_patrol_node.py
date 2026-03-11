import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from tf_transformations import quaternion_from_euler
import math

class CyclicPatrolNode(Node):
    def __init__(self):
        super().__init__('cyclic_patrol_node')
        
        self.get_logger().info('Patrol node started with simulation time')
        
        # --- Configuration ---
        self.total_cycles = 3  # Number of full patrol loops
        self.current_cycle = 0
        
        # Define Waypoints [x, y, yaw_degrees]
        # Adjust these coordinates to match your Gazebo map!
        self.waypoints = [
            [0.0, 0.0, 0.0],    # Start/Home
            [2.0, 0.0, 90.0],   # Point A
            [2.0, 2.0, 180.0],  # Point B
            [0.0, 2.0, 270.0],  # Point C
        ]
        
        self.current_waypoint_index = 0
        self.mission_active = False

        # --- Action Client Setup ---
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Wait for Nav2 server to be available
        self.get_logger().info('Waiting for Nav2 NavigateToPose action server...')
        self._action_client.wait_for_server()
        self.get_logger().info('Action server connected. Starting Patrol.')

        # Start the mission
        self.send_next_goal()

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
        result = future.result().result
        
        # Check navigation status (0 = SUCCEEDED)
        if result.status == 0: 
            self.get_logger().info(f'Waypoint {self.current_waypoint_index + 1} Reached Successfully.')
            
            # Move to next waypoint
            self.current_waypoint_index += 1
            
            # Check if cycle is complete
            if self.current_waypoint_index >= len(self.waypoints):
                self.current_waypoint_index = 0 # Reset to first waypoint
                self.current_cycle += 1
                self.get_logger().info(f'--- Cycle {self.current_cycle} Complete ---')
            
            # Send next goal immediately
            self.send_next_goal()
        else:
            self.get_logger().error('Navigation failed!')
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