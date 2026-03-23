# Autonomous Patrol System Project Completion Test Plan

## 1. Objective

Prove that the package is production-ready for TurtleBot4 by validating:

1. Build and static quality gates.
2. Runtime contract and launch integrity.
3. End-to-end behavior in TurtleBot4 simulation.
4. Nav2 stability and prior failure regression.
5. Full-system data flow (monitor -> alert -> mission -> evidence -> CLI).

## 2. Scope

In-scope components:

1. Nodes in `autonomous_patrol_system/`.
2. Launch files in `launch/`.
3. Runtime configs in `config/`.
4. Core quality checks under `test/`.

Out-of-scope for this plan:

1. Cloud or external alert integrations beyond topic-level verification.
2. Long-duration battery endurance and hardware wear testing.

## 3. Test Environments

Required environments:

1. Dev machine with ROS 2 Humble + TurtleBot4 simulation stack.
2. TurtleBot4 simulation in Ignition Gazebo (`world:=maze` baseline).

Optional extension:

1. Real TurtleBot4 hardware in safe test area for final acceptance.

## 4. Pre-Test Setup

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

## 5. Quality Gates (Stage A)

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

## 6. Simulation Bringup Baseline (Stage B)

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

## 7. Node and Launch Validation (Stage C)

### 7.1 Patrol only

```bash
ros2 launch autonomous_patrol_system cyclic_patrol.launch.py
```

Verify:

1. Node starts as `/cyclic_patrol_node`.
2. Logs show readiness wait then goal dispatch.
3. Robot reaches all waypoints and cycles complete.

### 7.2 Monitor only

```bash
ros2 launch autonomous_patrol_system environment_monitor.launch.py
```

Verify:

1. Subscribes to `/scan`.
2. Publishes `/anomaly/detected` when threshold + duration conditions are met.

### 7.3 Evidence only

```bash
ros2 launch autonomous_patrol_system evidence_capture.launch.py
```

Verify:

1. Logs are written in configured `storage_path`.
2. Service `save_evidence` responds successfully.

### 7.4 Full system

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

## 8. Config Sensitivity Tests (Stage D)

Run one change at a time, relaunch full system, observe expected behavior.

Files and expected outcomes:

1. `config/waypoints.yaml`: Path and cycle behavior should change directly.
2. `config/monitor_thresholds.yaml`: Alert frequency should vary with threshold/duration.
3. `config/mission_params.yaml`: State transition timing/retry behavior should change.
4. `config/alert_channels.yaml`: External forwarding enable/disable should reflect on topic output.
5. `config/log_formats.yaml`: CLI verbosity/color behavior should change.

## 9. Nav2 Regression and Recovery (Stage E)

This stage explicitly closes the prior Nav2 issue.

Key regression points to validate:

1. `cyclic_patrol_node` waits for Nav2 action server and TF before sending goals.
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

## 10. Final Acceptance Checklist

Project is considered complete when all are true:

1. Build and runtime contract tests pass.
2. Patrol launch completes configured cycles in simulation.
3. Full-system launch starts all six core nodes without crashing.
4. At least one anomaly-to-evidence pipeline run is validated end-to-end.
5. Nav2 regression stage passes with no false navigation-failure logs.
6. Config changes produce predictable behavior changes.

## 11. Recommended Execution Order (One Session)

1. Stage A quality gates.
2. Stage B sim + Nav2 baseline.
3. Stage C launch tests.
4. Stage D config sensitivity.
5. Stage E Nav2 regression + recovery drill.
6. Final acceptance sign-off using Section 10.
