from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='autonomous_patrol_system',
            executable='cyclic_patrol',
            name='cyclic_patrol_node',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                {'total_cycles': 3},
            ],
        )
    ])
