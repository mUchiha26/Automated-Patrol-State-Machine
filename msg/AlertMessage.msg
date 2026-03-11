std_msgs/Header header

# Severity: 1=critical, 2=warning, 3=info
uint8 severity

# Source node that triggered alert
string source_node

# Human-readable alert message
string message

# Optional structured payload (key:value pairs)
string payload

# Optional: JSON-formatted metadata for external systems
string metadata_json