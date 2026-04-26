#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
# from rover_interfaces.msg import WinchStatus

class WinchManagerNode(Node):
    def __init__(self):
        super().__init__('winch_manager')
        self.get_logger().info('Initializing Winch Manager Node...')
        
        # State: passive, assisted, anchor
        self.current_mode = "passive"
        self.tension_threshold = 500.0 # Newtons - breaking load limit
        
        # Subscriptions
        self.load_cell_sub = self.create_subscription(
            Float32,
            'winch/load_cell_tension',
            self.tension_callback,
            10
        )
        
        self.imu_sub = self.create_subscription(
            Float32, # Simplificato: pitch angle
            'sensors/pitch',
            self.pitch_callback,
            10
        )
        
        self.mode_sub = self.create_subscription(
            String,
            'winch/set_mode',
            self.set_mode_callback,
            10
        )
        
        # Publishers
        self.status_pub = self.create_publisher(String, 'winch/status', 10)
        
        # Timer for control loop
        self.create_timer(0.1, self.control_loop)

    def tension_callback(self, msg):
        self.current_tension = msg.data
        if self.current_tension > self.tension_threshold:
            self.emergency_stop("Critical Tension Exceeded!")

    def pitch_callback(self, msg):
        self.current_pitch = msg.data # Radianti o Gradi
        if self.current_pitch > 0.5: # Esempio ~30 gradi
            self.emergency_stop("Anti-Rollover Triggered!")

    def set_mode_callback(self, msg):
        new_mode = msg.data.lower()
        if new_mode in ["passive", "assisted", "anchor"]:
            self.current_mode = new_mode
            self.get_logger().info(f"Winch mode set to: {new_mode}")

    def control_loop(self):
        if self.current_mode == "passive":
            # Mantiene tensione minima per non impigliarsi
            pass
        elif self.current_mode == "assisted":
            # Tira con forza costante (N)
            pass
        elif self.current_mode == "anchor":
            # Blocca ruote e tira carico
            pass
            
    def emergency_stop(self, reason):
        self.get_logger().error(f"EMERGENCY STOP: {reason}")
        # Comando di arresto immediato al verricello e rover
        self.current_mode = "passive"

def main(args=None):
    rclpy.init(args=args)
    node = WinchManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
