# 🤖 Autonomous Patrol System for TurtleBot4

[![ROS 2 Humble](https://img.shields.io/badge/ROS_2-Humble-blue)](https://docs.ros.org/en/humble/)
[![TurtleBot4](https://img.shields.io/badge/Platform-TurtleBot4-orange)](https://turtlebot.org/turtlebot4/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10-green)](https://www.python.org/)

> **Autonomous cyclic patrol navigation with extensible behavior tree architecture for TurtleBot4**

---

## 🎯 Overview

This repository contains **custom ROS 2 nodes** that extend the official TurtleBot4 navigation stack with intelligent patrol capabilities. The system enables a TurtleBot4 robot to autonomously navigate between predefined waypoints in repeated cycles, forming the foundation for advanced behaviors like anomaly detection and automated response.

---

## ✨ Key Features

| Feature                    | Description                                              |
| -------------------------- | -------------------------------------------------------- |
| 🔄 **Cyclic Patrol**       | Navigate between 3-4+ waypoints in configurable loops    |
| 🎯 **Waypoint Navigation** | Precise goal posing with orientation control (x, y, yaw) |
| ⚙️ **Nav2 Integration**    | Built on official `NavigateToPose` action client         |
| 🕐 **Simulation Ready**    | Full support for Ignition Gazebo with `use_sim_time`     |
| 🧩 **Extensible Design**   | Modular node structure for adding custom behaviors       |
| 📝 **Structured Logging**  | Console feedback for mission progress and debugging      |

---

## 📦 Repository Structure

```text
Automated-Patrol-State-Machine/
├── README.md
├── LICENSE
├── CMakeLists.txt
├── package.xml
├── setup.py
├── setup.cfg
├── .gitignore
├── autonomous_patrol_system/
│   ├── __init__.py
│   ├── cyclic_patrol_node.py
│   ├── environment_monitor_node.py
│   ├── evidence_capture_node.py
│   ├── alert_dispatcher_node.py
│   ├── cli_feedback_node.py
│   └── mission_controller_node.py
├── launch/
│   ├── cyclic_patrol.launch.py
│   ├── environment_monitor.launch.py
│   ├── evidence_capture.launch.py
│   └── full_system.launch.py
├── config/
│   ├── waypoints.yaml
│   ├── monitor_thresholds.yaml
│   ├── mission_params.yaml
│   ├── evidence_storage.yaml
│   ├── alert_channels.yaml
│   └── log_formats.yaml
├── msg/
├── srv/
├── resource/
├── test/
├── docs/
│   ├── PROJECT_COMPLETION_TEST_PLAN.md
│   └── TESTING_GUIDE.md
└── scripts/
```

---

## 🚀 Quick Start

### Prerequisites

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- TurtleBot4 packages installed
- Ignition Gazebo (for simulation)

### 1) Install Official Dependencies

```bash
# Update package list
sudo apt update

# Install TurtleBot4 and Nav2 packages
sudo apt install ros-humble-turtlebot4 \
                 ros-humble-turtlebot4-ignition-bringup \
                 ros-humble-turtlebot4-navigation \
                 ros-humble-nav2-bringup \
                 ros-humble-slam-toolbox \
                 ros-humble-tf-transformations \
                 python3-colcon-common-extensions
```

### 2) Clone This Repository

```bash
# Create workspace if needed
mkdir -p ~/turtlebot4_ws/src
cd ~/turtlebot4_ws/src

# Clone this repo
git clone https://github.com/mUchiha26/Automated-Patrol-State-Machine.git
```

### 3) Build the Package

```bash
cd ~/turtlebot4_ws
colcon build --packages-select autonomous_patrol_system
source install/setup.bash
```

### 4) Run the Patrol Node

```bash
# Terminal 1: Ignition Simulation
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze

# Terminal 2: Navigation (with your map)
ros2 launch turtlebot4_navigation nav2.launch.py \
  map:=/opt/ros/humble/share/turtlebot4_navigation/maps/maze.yaml \
  use_sim_time:=true

# Terminal 3: Your patrol node
ros2 run autonomous_patrol_system cyclic_patrol \
  --ros-args -p use_sim_time:=true
```

---

## 🧭 `cyclic_patrol_node.py`

### What it does

The `cyclic_patrol_node` implements autonomous cyclic waypoint navigation using the Nav2 `NavigateToPose` action client.

### High-level architecture

```text
┌─────────────────────────────────┐
│   cyclic_patrol_node            │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Waypoint Manager        │   │
│  │ - Load coordinates      │   │
│  │ - Track cycle progress  │   │
│  └────────┬────────────────┘   │
│           │                     │
│  ┌────────▼────────────────┐   │
│  │ Nav2 Action Client      │   │
│  │ - Send NavigateToPose   │   │
│  │ - Handle async results  │   │
│  └────────┬────────────────┘   │
│           │                     │
│  ┌────────▼────────────────┐   │
│  │ Mission Controller      │   │
│  │ - Cycle counter         │   │
│  │ - Success/failure logic │   │
│  └─────────────────────────┘   │
└─────────────────────────────────┘
```

### Parameters

| Parameter          | Type         | Default   | Description                                |
| ------------------ | ------------ | --------- | ------------------------------------------ |
| `use_sim_time`     | `bool`       | `true`    | Use simulation clock (required for Gazebo) |
| `total_cycles`     | `int`        | `3`       | Number of complete patrol loops to execute |
| `waypoints`        | `list[list]` | See below | List of `[x, y, yaw_degrees]` coordinates  |
| `waypoint_timeout` | `float`      | `30.0`    | Seconds to wait for navigation completion  |

### Example waypoint configuration (Python)

```python
self.waypoints = [
    # [x (m), y (m), yaw (degrees)]
    [-0.5, -0.5, 0.0],    # Start position
    [1.0, -0.5, 90.0],    # Turn right corridor
    [1.0, 1.0, 180.0],    # Top-right corner
    [-0.5, 1.0, 270.0],   # Top-left corner (return path)
]
```

### Topics & actions

| Interface           | Type                              | Direction       | Purpose                           |
| ------------------- | --------------------------------- | --------------- | --------------------------------- |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Client → Server | Send navigation goals             |
| `/odom`             | `nav_msgs/Odometry`               | Subscribe       | Monitor robot position (optional) |
| `/tf`               | `tf2_msgs/TFMessage`              | Subscribe       | Transform handling (internal)     |

### Console output example

```text
[INFO] [cyclic_patrol_node]: Waiting for Nav2 NavigateToPose action server...
[INFO] [cyclic_patrol_node]: Action server connected. Starting Patrol.
[INFO] [cyclic_patrol_node]: Sending Goal: Cycle 1/3, Waypoint 1
[INFO] [cyclic_patrol_node]: Goal accepted by Nav2, waiting for result...
[INFO] [cyclic_patrol_node]: Waypoint 1 Reached Successfully.
[INFO] [cyclic_patrol_node]: Sending Goal: Cycle 1/3, Waypoint 2
...
[INFO] [cyclic_patrol_node]: --- Cycle 1 Complete ---
...
[INFO] [cyclic_patrol_node]: *** PATROL MISSION COMPLETE ***
```

---

## 🛠️ Development Guide

### Adding a new node

1. **Create the Python file** in `autonomous_patrol_system/`:

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
           'cyclic_patrol = autonomous_patrol_system.cyclic_patrol_node:main',
           'anomaly_detector = autonomous_patrol_system.anomaly_detector_node:main',
       ],
   },
   ```

3. **Rebuild and test**:

   ```bash
   cd ~/turtlebot4_ws
   colcon build --packages-select autonomous_patrol_system
   source install/setup.bash
   ros2 run autonomous_patrol_system anomaly_detector --help
   ```

### Creating a launch file

Example: `launch/patrol_demo.launch.py`

```python
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

---

## 🧪 Testing And Project Completion Plan

This section merges the project completion test plan into the README so you can execute final validation from one place.

### 1. Objective

Prove that the package is production-ready for TurtleBot4 by validating:

1. Build and static quality gates.
2. Runtime contract and launch integrity.
3. End-to-end behavior in TurtleBot4 simulation.
4. Nav2 stability and prior failure regression.
5. Full-system data flow (monitor -> alert -> mission -> evidence -> CLI).

### 2. Scope

In-scope components:

1. Nodes in `autonomous_patrol_system/`.
2. Launch files in `launch/`.
3. Runtime configs in `config/`.
4. Core quality checks under `test/`.

Out-of-scope for this plan:

1. Cloud or external alert integrations beyond topic-level verification.
2. Long-duration battery endurance and hardware wear testing.

### 3. Test Environments

Required environments:

1. Dev machine with ROS 2 Humble + TurtleBot4 simulation stack.
2. TurtleBot4 simulation in Ignition Gazebo (`world:=maze` baseline).

Optional extension:

1. Real TurtleBot4 hardware in safe test area for final acceptance.

### 4. Pre-Test Setup

Run once per session:

```bash
cd ~/turtlebot4_ws
colcon build --packages-select autonomous_patrol_system
source /opt/ros/humble/setup.bash
source ~/turtlebot4_ws/install/setup.bash
```

If using venv for local pytest helper checks:

```bash
source /home/yass/turtlebot4_ws/src/autonomous_patrol_system/.venv/bin/activate
```

### 5. Quality Gates (Stage A)

Execute in package root (`~/turtlebot4_ws/src/autonomous_patrol_system`):

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q test/test_runtime_contracts.py
```

Optional style checks:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q test/test_flake8.py test/test_pep257.py test/test_copyright.py
```

Pass criteria:

1. Runtime contract tests pass.
2. No new style or packaging regressions.

### 6. Simulation Bringup Baseline (Stage B)

Terminal `T1`:

```bash
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze
```

Terminal `T2`:

```bash
ros2 launch turtlebot4_navigation localization.launch.py \
    map:=/opt/ros/humble/share/turtlebot4_navigation/maps/maze.yaml \
    use_sim_time:=true
```

Terminal `T3`:

```bash
ros2 launch turtlebot4_navigation nav2.launch.py use_sim_time:=true
```

Set initial pose once in RViz (`2D Pose Estimate`) or via CLI:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {z: 0.0, w: 1.0}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0685]}}"
```

Baseline checks:

```bash
ros2 action info /navigate_to_pose
ros2 run tf2_ros tf2_echo map base_link
ros2 topic echo /clock --once
```

Pass criteria:

1. `/navigate_to_pose` action exists.
2. `map -> base_link` is resolvable.
3. Sim clock is active.

### 7. Node And Launch Validation (Stage C)

#### 7.1 Patrol only

```bash
ros2 launch autonomous_patrol_system cyclic_patrol.launch.py
```

Verify:

1. Node starts as `/cyclic_patrol_node`.
2. Logs show readiness wait then goal dispatch.
3. Robot reaches all waypoints and cycles complete.

#### 7.2 Monitor only

```bash
ros2 launch autonomous_patrol_system environment_monitor.launch.py
```

Verify:

1. Subscribes to `/scan`.
2. Publishes `/anomaly/detected` when threshold + duration conditions are met.

#### 7.3 Evidence only

```bash
ros2 launch autonomous_patrol_system evidence_capture.launch.py
```

Verify:

1. Logs are written in configured `storage_path`.
2. Service `save_evidence` responds successfully.

#### 7.4 Full system

```bash
ros2 launch autonomous_patrol_system full_system.launch.py
```

Verify nodes:

```bash
ros2 node list | grep -E "cyclic_patrol_node|environment_monitor_node|evidence_capture_node|alert_dispatcher_node|cli_feedback_node|mission_controller_node"
```

Functional flow checks:

1. Patrol movement occurs.
2. Anomaly event generates alert.
3. Mission state transitions from `PATROLLING` to anomaly-handling path.
4. Evidence is persisted to disk.

### 8. Config Sensitivity Tests (Stage D)

Run one change at a time, relaunch full system, and observe expected behavior.

Files and expected outcomes:

1. `config/waypoints.yaml`: Path and cycle behavior should change directly.
2. `config/monitor_thresholds.yaml`: Alert frequency should vary with threshold/duration.
3. `config/mission_params.yaml`: State transition timing/retry behavior should change.
4. `config/alert_channels.yaml`: External forwarding enable/disable should reflect on topic output.
5. `config/log_formats.yaml`: CLI verbosity/color behavior should change.

### 9. Nav2 Regression And Recovery (Stage E)

This stage explicitly closes the prior Nav2 issue.

Key regression points to validate:

1. `cyclic_patrol_node` waits for Nav2 action server before sending goals and reports TF readiness issues as warnings.
2. Success condition checks canonical action status (`STATUS_SUCCEEDED`), not raw `0`.
3. Patrol no longer reports false failure when waypoints are reached.

Run this sequence:

1. Bring up sim + Nav2, set initial pose.
2. Launch patrol only.
3. Send one direct manual goal:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

4. Compare Nav2 action status with patrol logs.

Pass criteria:

1. Manual goal succeeds.
2. Patrol logs successful waypoint completion.
3. No recurring `frame does not exist` or immediate goal rejection after initial pose is set.

Fast recovery playbook if Nav2 stalls:

1. Stop patrol/full-system launch.
2. Keep simulation running.
3. Restart Nav2 only.
4. Recheck `/navigate_to_pose` and `map -> base_link`.
5. Relaunch patrol.

### 10. Final Acceptance Checklist

Project is considered complete when all are true:

1. Build and runtime contract tests pass.
2. Patrol launch completes configured cycles in simulation.
3. Full-system launch starts all six core nodes without crashing.
4. At least one anomaly-to-evidence pipeline run is validated end-to-end.
5. Nav2 regression stage passes with no false navigation-failure logs.
6. Config changes produce predictable behavior changes.

### 11. Recommended Execution Order (One Session)

1. Stage A quality gates.
2. Stage B sim + Nav2 baseline.
3. Stage C launch tests.
4. Stage D config sensitivity.
5. Stage E Nav2 regression + recovery drill.
6. Final acceptance sign-off using Section 10.

Additional troubleshooting and scenario examples are still available in `docs/TESTING_GUIDE.md`.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/anomaly-detector`
3. Commit your changes: `git commit -m 'Add anomaly detection logic'`
4. Push to the branch: `git push origin feature/anomaly-detector`
5. Open a Pull Request

### Coding standards

- Follow [PEP 8](https://pep8.org/) for Python code
- Use [ROS 2 logging](https://docs.ros.org/en/humble/Tutorials/Intermediate/Logging.html) instead of `print()`
- Document public functions with docstrings
- Add tests for new functionality

---

## 📄 License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.

```text
Copyright 2024 Yasseene

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 🙏 Acknowledgments

- [TurtleBot4 Official Documentation](https://docs.turtlebot.org/turtlebot4/)
- [Nav2 Documentation](https://navigation.ros.org/)
- [ROS 2 Humble Documentation](https://docs.ros.org/en/humble/)
- Open Robotics community for amazing tools

---

## 📬 Contact

**Maintainer**: Yasseene  
**GitHub**: [@mUchiha26](https://github.com/mUchiha26)  
**Issues**: Report a bug or request a feature via the repository Issues page.

---
