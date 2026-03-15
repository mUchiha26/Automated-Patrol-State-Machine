# Autonomous Patrol System Testing Guide

This guide is for runtime testing in simulation, with special focus on Nav2 issues.

## 1. Test Goal

Validate the project in this order:

1. Bring up TurtleBot4 simulation and visualization.
2. Bring up Nav2 and verify it is healthy before project nodes start.
3. Test each project launch file.
4. Change config values and observe robot/system reaction.
5. Diagnose and isolate Nav2-related failures quickly.

## 2. Prerequisites

- ROS 2 Humble environment installed.
- TurtleBot4 simulation and Nav2 packages installed.
- Workspace builds successfully from `~/turtlebot4_ws`.

Recommended rebuild before test session:

```bash
cd ~/turtlebot4_ws
colcon build --packages-select autonomous_patrol_system
source /opt/ros/humble/setup.bash
source ~/turtlebot4_ws/install/setup.bash
```

## 3. Terminal Setup

Use 6 terminals for clean debugging.

- `T1`: simulation
- `T2`: Nav2 bringup
- `T3`: project launch under test
- `T4`: teleop (optional)
- `T5`: diagnostics (`ros2 node list`, `ros2 topic echo`, etc.)
- `T6`: RViz or extra debug commands

In every terminal:

```bash
source /opt/ros/humble/setup.bash
source ~/turtlebot4_ws/install/setup.bash
```

## 4. Bring Up Simulation + Visualization First

Start Ignition simulation:

```bash
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze
```

Then start Nav2 (RViz usually comes with this launch):

```bash
ros2 launch turtlebot4_navigation nav2.launch.py \
  map:=/opt/ros/humble/share/turtlebot4_navigation/maps/maze.yaml \
  use_sim_time:=true
```

Before launching patrol, set initial pose once in RViz (`2D Pose Estimate`) or publish it from CLI.
This is required for AMCL to provide `map -> odom`, otherwise Nav2 can fail with `frame does not exist`.

Example CLI initial pose:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: map}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {z: 0.0, w: 1.0}}, covariance: [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0685]}}"
```

Optional manual control while testing:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Optional checks before launching project nodes:

```bash
ros2 action list | grep navigate_to_pose
ros2 action info /navigate_to_pose
ros2 node list | sort
```

Expected baseline:

- `/navigate_to_pose` action exists.
- Nav2 lifecycle nodes are active.
- `/tf`, `/tf_static`, `/odom`, `/scan`, `/clock` are published.

## 5. Launch File Tests

## 5.1 `launch/cyclic_patrol.launch.py`

```bash
ros2 launch autonomous_patrol_system cyclic_patrol.launch.py
```

Verify:

- Node starts as `/cyclic_patrol_node`.
- Log shows: waiting for Nav2 action server, then goal dispatch.
- Robot moves through waypoints and cycles.

Quick probes:

```bash
ros2 node info /cyclic_patrol_node
ros2 param get /cyclic_patrol_node total_cycles
ros2 param get /cyclic_patrol_node waypoints
```

## 5.2 `launch/environment_monitor.launch.py`

```bash
ros2 launch autonomous_patrol_system environment_monitor.launch.py
```

Verify:

- Node starts as `/environment_monitor_node`.
- Subscribes to `/scan`.
- Publishes anomaly events only when threshold condition is met.

Quick probes:

```bash
ros2 node info /environment_monitor_node
ros2 param get /environment_monitor_node min_distance_threshold
```

## 5.3 `launch/evidence_capture.launch.py`

```bash
ros2 launch autonomous_patrol_system evidence_capture.launch.py
```

Verify:

- Node starts as `/evidence_capture_node`.
- Uses configured storage path.
- Captures evidence on anomaly trigger path.

Quick probes:

```bash
ros2 node info /evidence_capture_node
ros2 param get /evidence_capture_node storage_path
```

## 5.4 `launch/full_system.launch.py`

```bash
ros2 launch autonomous_patrol_system full_system.launch.py
```

Verify all nodes exist:

```bash
ros2 node list | grep -E "cyclic_patrol_node|environment_monitor_node|evidence_capture_node|alert_dispatcher_node|cli_feedback_node|mission_controller_node"
```

Functional checks:

- Patrol goals are sent and robot moves.
- Monitor can detect anomaly.
- Mission controller state changes when alerts arrive.
- Evidence and alert paths respond.

## 6. Config Tuning Experiments

Edit YAML files under `config/`, relaunch, and observe behavior.

## 6.1 Patrol behavior: `config/waypoints.yaml`

Try:

- Set `total_cycles` to `1` for quick iteration.
- Set `waypoint_timeout` to `5.0` to stress timeout behavior.
- Replace waypoints with easy map coordinates first.

Expected reaction:

- Robot path shape changes immediately after relaunch.
- Too aggressive timeout can cause more mission failures.

## 6.2 Monitoring sensitivity: `config/monitor_thresholds.yaml`

Try:

- Raise `min_distance_threshold` (example `0.8`) to detect farther obstacles.
- Lower `anomaly_duration_threshold` (example `0.2`) for faster triggering.

Expected reaction:

- Higher sensitivity increases alert frequency.
- Very low duration can produce noisy anomaly events.

## 6.3 Mission state behavior: `config/mission_params.yaml`

Try:

- `initial_state: "PATROLLING"` (normal baseline).
- Reduce `task_timeout` to check timeout transitions.
- Reduce `max_retries` to force earlier recovery behavior.

Expected reaction:

- Mission state transition cadence changes.
- Recovery/timeout behavior appears sooner with lower limits.

## 6.4 Alert and CLI behavior

Files:

- `config/alert_channels.yaml`
- `config/log_formats.yaml`

Try:

- Toggle `enable_external_forwarding` true/false.
- Change CLI verbosity to reduce or increase log noise.

Expected reaction:

- Alert forwarding path toggles.
- Console output detail changes.

## 7. Nav2 Problem Focus (Primary Debug Path)

Use this section whenever patrol appears stuck, goals are rejected, or logs show navigation failures.

## 7.1 Health checks in order

1. Confirm simulation clock is available:

```bash
ros2 topic echo /clock --once
```

2. Confirm action server exists:

```bash
ros2 action info /navigate_to_pose
```

3. Confirm transform chain is valid:

```bash
ros2 run tf2_ros tf2_echo map base_link
```

If this command says `frame does not exist`, do this immediately:

1. Ensure Nav2 launch is still running.
2. Publish initial pose (`/initialpose`) or set `2D Pose Estimate` in RViz.
3. Re-run `tf2_echo map base_link` until it resolves.
4. Only then launch patrol/full system.

5. Confirm Nav2 lifecycle nodes are active:

```bash
for n in /controller_server /planner_server /behavior_server /bt_navigator /amcl; do
  ros2 lifecycle get $n
done
```

5. Confirm your patrol node uses simulation time:

```bash
ros2 param get /cyclic_patrol_node use_sim_time
```

## 7.2 Manual action sanity test

Send a direct Nav2 goal to isolate whether problem is in Nav2 or in project logic:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: map}, pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

Interpretation:

- If this fails: Nav2/sim/map/localization issue.
- If this succeeds but patrol node still reports failure: likely project-side result handling issue.

## 7.3 Known repository pitfall (important)

In `autonomous_patrol_system/cyclic_patrol_node.py`, goal result handling currently treats status `0` as success.
For ROS 2 actions, successful completion is typically `STATUS_SUCCEEDED = 4`.

Impact:

- Robot may actually reach waypoint, but node logs `Navigation failed!`.
- Patrol flow may stop or behave incorrectly.

What to verify while testing:

- Compare Nav2 action result status with patrol logs.
- If mismatch appears, fix status check in the node before further tuning.

## 7.4 Fast recovery sequence for Nav2 issues

1. Stop patrol/full-system launch.
2. Keep simulation running.
3. Restart Nav2 launch only.
4. Recheck `/navigate_to_pose` availability.
5. Relaunch patrol.

This sequence avoids full reset and is faster for iterative debugging.

## 8. Suggested Test Session Script

Run this exact order for repeatable sessions:

1. Rebuild package.
2. Start simulation.
3. Start Nav2 and wait until stable.
4. Run `cyclic_patrol.launch.py` and confirm baseline motion.
5. Run `full_system.launch.py` and validate node interactions.
6. Change one config value at a time and rerun.
7. If movement fails, go directly to Section 7.

## 9. Pass Criteria

A test cycle is considered successful when:

- Robot receives and executes Nav2 goals from patrol node.
- Patrol completes configured cycles.
- Full-system launch starts all six project nodes.
- Config changes produce expected behavioral changes.
- Nav2 failures can be diagnosed and isolated using Section 7.
