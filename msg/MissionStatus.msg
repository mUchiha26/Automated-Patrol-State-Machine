std_msgs/Header header

# State: IDLE, PATROLLING, ANOMALY_HANDLING, RECOVERING, COMPLETE
string state

# Current subtask being executed
string current_task

# Retry counter for failed tasks
uint32 retry_count

# Node uptime in seconds
int64 uptime_sec

# Optional: last error message
string last_error