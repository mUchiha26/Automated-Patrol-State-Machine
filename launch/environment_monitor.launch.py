from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    config = PathJoinSubstitution([FindPackageShare('autonomous_patrol_system'), 'config', 'monitor_thresholds.yaml'])
    
    return LaunchDescription([
        Node(
            package='autonomous_patrol_system',
            executable='environment_monitor',
            name='environment_monitor_node',
            output='screen',
            parameters=[config, {'use_sim_time': True}]
        )
    ])