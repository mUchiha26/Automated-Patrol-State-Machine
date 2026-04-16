## 🛠️ Development Guide

### Adding a new node

1. **Create the Python file** in `automated_patrol_state_machine/`:

   ```python
   # anomaly_detector_node.py
   import rclpy
   from rclpy.node import Node

   class AnomalyDetectorNode(Node):
       def __init__(self):
           super().__init__('anomaly_detector_node')
           # Your implementation here
   ```

2. **Register the entry point** in `setup.py`:

   ```python
   entry_points={
       'console_scripts': [
           'cyclic_patrol = automated_patrol_state_machine.patrol_executor_node:main',
           'anomaly_detector = automated_patrol_state_machine.anomaly_detector_node:main',
       ],
   },
   ```

3. **Rebuild and test**:

   ```bash
   cd ~/turtlebot4_ws
   colcon build --packages-select automated_patrol_state_machine
   source install/setup.bash
   ros2 run automated_patrol_state_machine anomaly_detector --help
   ```

### Creating a launch file

Example: `launch/patrol_demo.launch.py`

```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='automated_patrol_state_machine',
            executable='cyclic_patrol',
            name='patrol_executor_node',
            output='screen',
            parameters=[
                {'use_sim_time': True},
                {'total_cycles': 3},
                {'waypoints': [
                    [-0.5, -0.5, 0.0],
                    [1.0, -0.5, 90.0],
                    [1.0, 1.0, 180.0],
                    [-0.5, 1.0, 270.0],
                ]}
            ]
        )
    ])
```

### Console output example

```text
[INFO] [patrol_executor_node]: Waiting for Nav2 NavigateToPose action server...
[INFO] [patrol_executor_node]: Action server connected. Starting Patrol.
[INFO] [patrol_executor_node]: Sending Goal: Cycle 1/3, Waypoint 1
[INFO] [patrol_executor_node]: Goal accepted by Nav2, waiting for result...
[INFO] [patrol_executor_node]: Waypoint 1 Reached Successfully.
[INFO] [patrol_executor_node]: Sending Goal: Cycle 1/3, Waypoint 2
...
[INFO] [patrol_executor_node]: --- Cycle 1 Complete ---
...
[INFO] [patrol_executor_node]: *** PATROL MISSION COMPLETE ***
```

---
