from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    config = PathJoinSubstitution([FindPackageShare('autonomous_patrol_system'), 'config', 'evidence_storage.yaml'])
    
    return LaunchDescription([
        Node(
            package='autonomous_patrol_system',
            executable='evidence_capture',
            name='evidence_capture_node',
            output='screen',
            parameters=[config]
        )
    ])