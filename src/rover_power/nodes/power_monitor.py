#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool

class PowerMonitorNode(Node):
    def __init__(self):
        super().__init__('power_monitor')
        self.get_logger().info('Initializing Hybrid Power Management Node...')
        
        # Subscriptions
        self.soc_sub = self.create_subscription(
            Float32,
            'battery/soc',
            self.soc_callback,
            10
        )
        
        # Publishers to ESP32 (via bridge or direct)
        self.ice_starter_pub = self.create_publisher(
            Bool,
            'hardware/ice_generator_start',
            10
        )
        
        self.ice_active = False

    def soc_callback(self, msg):
        soc = msg.data
        
        # Logica Gestione Ibrida
        if soc < 20.0 and not self.ice_active:
            self.start_generator()
        elif soc > 80.0 and self.ice_active:
            self.stop_generator()

    def start_generator(self):
        self.get_logger().warn("Battery Low (<20%). Starting ICE Generator...")
        self.ice_starter_pub.publish(Bool(data=True))
        self.ice_active = True

    def stop_generator(self):
        self.get_logger().info("Battery Charged (>80%). Stopping ICE Generator.")
        self.ice_starter_pub.publish(Bool(data=False))
        self.ice_active = False

def main(args=None):
    rclpy.init(args=args)
    node = PowerMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
