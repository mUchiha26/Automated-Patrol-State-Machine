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

| Feature | Description |
| --- | --- |
| 🔄 **Cyclic Patrol** | Navigate between 3-4+ waypoints in configurable loops |
| 🎯 **Waypoint Navigation** | Precise goal posing with orientation control (x, y, yaw) |
| ⚙️ **Nav2 Integration** | Built on official `NavigateToPose` action client |
| 🕐 **Simulation Ready** | Full support for Ignition Gazebo with `use_sim_time` |
| 🧩 **Extensible Design** | Modular node structure for adding custom behaviors |
| 📝 **Structured Logging** | Console feedback for mission progress and debugging |

---

## 📦 Repository Structure

```text
Automated-Patrol-State-Machine/
├── README.md                          ← You are here
├── LICENSE                            ← Apache 2.0
├── .gitignore                         ← ROS 2 workspace ignores
│
├── packages/
│   └── autonomous_patrol_system/      ← Your custom package
│       ├── autonomous_patrol_system/  ← Python module
│       │   ├── __init__.py
│       │   ├── cyclic_patrol_node.py     ← ✅ Current: Patrol logic
│       │   ├── anomaly_detector_node.py  ← 🔜 Future: Monitoring
│       │   ├── evidence_capture_node.py  ← 🔜 Future: Data logging
│       │   └── alert_dispatcher_node.py  ← 🔜 Future: Notifications
│       ├── launch/
│       │   └── patrol_demo.launch.py  ← Example launch file
│       ├── config/
│       │   └── waypoints.yaml         ← Example waypoint config
│       ├── resource/
│       │   └── autonomous_patrol_system
│       ├── test/                      ← Auto-generated tests
│       ├── setup.py                   ← Entry points registration
│       ├── setup.cfg
│       └── package.xml                ← ROS 2 package metadata
│
└── scripts/
    └── install_dependencies.sh        ← Helper: install official deps
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
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py

# Terminal 2: Navigation (with your map)
ros2 launch turtlebot4_navigation nav2.launch.py \
  map:=/opt/ros/humble/share/turtlebot4_navigation/maps/maze.yaml \
  use_sim_time:=true

# Terminal 3: Your patrol node
ros2 run autonomous_patrol_system cyclic_patrol \
  --ros-args -p use_sim_time:=true
```

---

## 🧭 `cyclic_patrol_node.py` – Current Implementation

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

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `use_sim_time` | `bool` | `true` | Use simulation clock (required for Gazebo) |
| `total_cycles` | `int` | `3` | Number of complete patrol loops to execute |
| `waypoints` | `list[list]` | See below | List of `[x, y, yaw_degrees]` coordinates |
| `waypoint_timeout` | `float` | `30.0` | Seconds to wait for navigation completion |

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

| Interface | Type | Direction | Purpose |
| --- | --- | --- | --- |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Client → Server | Send navigation goals |
| `/odom` | `nav_msgs/Odometry` | Subscribe | Monitor robot position (optional) |
| `/tf` | `tf2_msgs/TFMessage` | Subscribe | Transform handling (internal) |

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

## 🔮 Roadmap (Planned Extensions)

This package is designed as a **foundation** for advanced autonomous behaviors.

| Node | Status | Purpose |
| --- | --- | --- |
| `cyclic_patrol_node.py` | ✅ Implemented | Basic cyclic waypoint navigation |
| `anomaly_detector_node.py` | 🔜 Planned | Monitor LiDAR/camera for unexpected objects |
| `evidence_capture_node.py` | 🔜 Planned | Auto-record images/logs when anomaly detected |
| `alert_dispatcher_node.py` | 🔜 Planned | Publish alerts to ROS topics/services |
| `patrol_bt_loader.py` | 🔜 Planned | Load Behavior Tree XML for complex missions |

### Future architecture vision

```text
                    ┌─────────────────────┐
                    │  Behavior Tree Root │
                    └────────┬────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Patrol Loop  │ │  Monitoring   │ │  Recovery     │
│  (cyclic)     │ │  (parallel)   │ │  (on fail)    │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ NavigateToPose│ │ Anomaly Check │ │ Retry/Backup  │
│ (Nav2 action) │ │ (custom logic)│ │ (Nav2 recover)│
└───────────────┘ └───────┬───────┘ └───────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
    ┌─────────────────┐ ┌─────────────────┐
    │ Evidence Capture│ │ Alert Dispatch  │
    │ (parallel task) │ │ (parallel task) │
    └─────────────────┘ └─────────────────┘
```

---

## 🛠️ Development Guide

### Adding a new node

1. **Create the Python file** in `packages/autonomous_patrol_system/autonomous_patrol_system/`:

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

## 🧪 Testing

### Unit tests (skeleton)

The `test/` directory contains auto-generated test scaffolding. Extend with:

```python
# test/test_cyclic_patrol.py
import unittest
import rclpy
from autonomous_patrol_system.cyclic_patrol_node import CyclicPatrolNode

class TestCyclicPatrolNode(unittest.TestCase):
    def setUp(self):
        rclpy.init()
        self.node = CyclicPatrolNode()

    def tearDown(self):
        self.node.destroy_node()
        rclpy.shutdown()

    def test_waypoint_initialization(self):
        self.assertIsNotNone(self.node.waypoints)
```

Run tests with:

```bash
colcon test --packages-select autonomous_patrol_system
colcon test-result --verbose
```

### Integration testing

1. Launch simulation + Nav2
2. Run your node
3. Verify in RViz:
   - Robot follows planned path (green line)
   - Waypoints are reached in order
   - Cycles complete as configured

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