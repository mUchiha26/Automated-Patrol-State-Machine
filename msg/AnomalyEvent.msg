# Standard ROS header
std_msgs/Header header

# Detected distance to obstacle (meters)
geometry_msgs/Point32 detected_position

# Distance value (redundant but convenient)
float32 detected_distance

# Type identifier: 'obstacle_proximity', 'motion_anomaly', etc.
string anomaly_type

# Severity: 1=critical, 2=warning, 3=info
uint8 severity

# Optional metadata
string description