from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg = FindPackageShare('autonomous_patrol_system')
    waypoints_config = PathJoinSubstitution([pkg, 'config', 'waypoints.yaml'])
    monitor_config = PathJoinSubstitution([pkg, 'config', 'monitor_thresholds.yaml'])
    evidence_config = PathJoinSubstitution([pkg, 'config', 'evidence_storage.yaml'])
    alert_config = PathJoinSubstitution([pkg, 'config', 'alert_channels.yaml'])
    cli_config = PathJoinSubstitution([pkg, 'config', 'log_formats.yaml'])
    mission_config = PathJoinSubstitution([pkg, 'config', 'mission_params.yaml'])
    
    return LaunchDescription([
        # 1. Patrol
        Node(
            package='autonomous_patrol_system',
            executable='cyclic_patrol',
            name='cyclic_patrol_node',
            parameters=[waypoints_config],
        ),
        # 2. Monitor
        Node(package='autonomous_patrol_system', executable='environment_monitor', parameters=[monitor_config]),
        # 3. Evidence
        Node(package='autonomous_patrol_system', executable='evidence_capture', parameters=[evidence_config]),
        # 4. Alert
        Node(package='autonomous_patrol_system', executable='alert_dispatcher', parameters=[alert_config]),
        # 5. CLI
        Node(package='autonomous_patrol_system', executable='cli_feedback', parameters=[cli_config]),
        # 6. Mission Controller (State Machine)
        Node(package='autonomous_patrol_system', executable='mission_controller', parameters=[mission_config]),
    ])