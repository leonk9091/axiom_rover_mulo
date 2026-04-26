#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
# Placeholder for YOLO and Depth processing
# import cv2
# from ultralytics import YOLO

class PersonFollowingNode(Node):
    def __init__(self):
        super().__init__('person_following')
        self.get_logger().info('Initializing YOLOv11 Person Following Node...')
        
        # Parameters
        self.target_distance = 1.5 # meters
        
        # Subscriptions (Depth Camera + RGB)
        self.image_sub = self.create_subscription(
            Image,
            'camera/rgb/image_raw',
            self.image_callback,
            10
        )
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        self.get_logger().info('Following logic ready. Target distance: 1.5m')

    def image_callback(self, msg):
        # 1. YOLOv11 Detection (Identify legs/person)
        # 2. Depth data extraction for the detected bounding box
        # 3. PID Control to maintain 1.5m distance
        
        twist = Twist()
        # twist.linear.x = calculated_speed
        # twist.angular.z = calculated_steering
        # self.cmd_vel_pub.publish(twist)
        pass

def main(args=None):
    rclpy.init(args=args)
    node = PersonFollowingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
