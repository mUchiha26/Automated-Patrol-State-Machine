import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import os
import time
from datetime import datetime
from autonomous_patrol_system.msg import AnomalyEvent
from autonomous_patrol_system.srv import SaveEvidence

class EvidenceCaptureNode(Node):
    def __init__(self):
        super().__init__('evidence_capture_node')
        
        # --- Parameters ---
        self.declare_parameter('storage_path', '/tmp/patrol_evidence')
        self.declare_parameter('image_topic', '/camera/image_raw')  # Future: camera integration
        self.declare_parameter('retain_days', 7)
        
        self.storage_path = self.get_parameter('storage_path').value
        os.makedirs(self.storage_path, exist_ok=True)
        
        # --- Service ---
        self.srv = self.create_service(SaveEvidence, 'save_evidence', self.save_callback)
        
        # --- Subscriber ---
        # Use best-effort QoS for anomaly events (don't block patrol)
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.anomaly_sub = self.create_subscription(
            AnomalyEvent, '/anomaly/detected', self.anomaly_callback, qos
        )
        
        self.get_logger().info(f'Evidence capture ready. Saving to: {self.storage_path}')

    def anomaly_callback(self, msg: AnomalyEvent):
        """Log anomaly metadata when detected."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        filename = f"anomaly_{timestamp}.log"
        filepath = os.path.join(self.storage_path, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"Timestamp: {msg.header.stamp.sec}.{msg.header.stamp.nanosec}\n")
            f.write(f"Frame: {msg.header.frame_id}\n")
            f.write(f"Type: {msg.anomaly_type}\n")
            f.write(f"Severity: {msg.severity}\n")
            f.write(f"Distance: {msg.detected_distance.data:.3f}m\n")
            f.write(f"Description: {msg.description}\n")
        
        self.get_logger().info(f'Evidence logged: {filename}')

    def save_callback(self, request, response):
        """Service handler to confirm evidence save (for external triggers)."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(self.storage_path, f"manual_{timestamp}.log")
        
        with open(filepath, 'w') as f:
            f.write(f"Manual save request at {timestamp}\n")
            f.write(f"Meta {request.metadata}\n")
        
        response.success = True
        response.file_path = filepath
        return response

def main(args=None):
    rclpy.init(args=args)
    node = EvidenceCaptureNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()