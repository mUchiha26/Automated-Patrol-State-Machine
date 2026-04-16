# Automated Patrol State Machine - Engineering Concepts Log

## 1. ROS 2 Architecture Principle

The system is built on a modular ROS 2 architecture using:

- Nodes (runtime execution units)
- Topics (communication streams)
- Services (request/response actions)
- Parameters (configuration layer)

Each node follows the Single Responsibility Principle (SRP) to ensure scalability and maintainability.

## 2. Node Design Philosophy

Nodes are designed as thin execution layers, meaning:

- They do not contain business logic.
- They only:
  - Publish data
  - Subscribe to data
  - Call the FSM layer
  - Execute outputs (for example, robot commands)

This prevents "God Node" architecture.

## 3. Finite State Machine (FSM) Concept

The FSM is the decision-making engine of the robot.

It is composed of:

### 3.1 State

A state represents a robot behavior:

- `PATROL`
- `RECOVERY`
- `IDLE`
- `ALERT`

Each state has:

- `enter()` -> initialization logic
- `execute()` -> ongoing behavior logic
- `exit()` -> cleanup logic

### 3.2 State Machine Controller

The state machine:

- Stores the current state
- Executes state logic cyclically
- Handles transitions between states

Transition logic is triggered by:

- Sensor input
- Internal conditions
- System events

## 4. Separation of Concerns (Key Design Rule)

The system is divided into three layers:

### Layer 1 - ROS Interface (Nodes)

- Communication layer
- Receives sensor data
- Sends robot commands

### Layer 2 - FSM Core

- Decision-making logic
- State transitions
- Behavior orchestration

### Layer 3 - Configuration Layer

- YAML-based tuning
- No hardcoded parameters

## 5. Event-Driven vs Polling Logic

Current implementation uses a polling FSM:

- `execute()` runs periodically
- Conditions are checked every cycle

Future improvement:

- Event-driven FSM using ROS topics
- Reduces unnecessary computation
- Improves responsiveness

## 6. ROS 2 Python Packaging System

The system uses:

- `ament_python` build system
- `setuptools` for module discovery
- `entry_points` for CLI node execution

Key concept:

Python modules must be explicitly discoverable using `find_packages()` and `__init__.py` files.

## 7. Package Structure Philosophy

The project structure is designed for scalability:

- `nodes/` -> ROS runtime layer
- `fsm/` -> decision logic layer
- `config/` -> runtime parameters
- `test/` -> validation layer

This ensures:

- Modular expansion
- Independent testing
- Clean separation of logic

## 8. Testing Strategy

Testing is designed in two levels:

### 8.1 Unit Testing

- FSM logic validation
- State transitions
- No ROS dependency

### 8.2 Integration Testing

- ROS node execution
- Communication between nodes
- Real simulation behavior

## 9. System Execution Flow

`Sensors -> ROS Node -> FSM -> Decision -> Action Node -> Robot`

Flow:

- Environment data is collected
- FSM evaluates state
- Transition occurs if needed
- Robot action is executed
- Loop repeats

## 10. Key Engineering Insight

The most important design principle:

> "Nodes should not think - they should only execute. The FSM is the only thinking component."
