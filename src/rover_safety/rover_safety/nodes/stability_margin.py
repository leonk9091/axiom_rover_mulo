#!/usr/bin/env python3
"""Publish a fused stability margin for planning, winch control, and safety."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float32

from rover_interfaces.msg import StabilityMargin
from rover_safety.stability import StabilityEnvelopeModel


class StabilityMarginNode(Node):
    def __init__(self):
        super().__init__("stability_margin")
        self.get_logger().info("Initializing Stability Margin Node...")

        self.model = StabilityEnvelopeModel()
        self.pitch_rad = 0.0
        self.roll_rad = 0.0
        self.linear_velocity_ms = 0.0
        self.winch_tension_n = 0.0
        self.traction_factor = 1.0

        self.create_subscription(Float32, "sensors/pitch", self._cb_pitch, 10)
        self.create_subscription(Float32, "sensors/roll", self._cb_roll, 10)
        self.create_subscription(Float32, "winch/load_cell_tension", self._cb_tension, 10)
        self.create_subscription(Float32, "navigation/traction_factor", self._cb_traction, 10)
        self.create_subscription(Twist, "mission/cmd_vel", self._cb_cmd_vel, 10)
        self.create_subscription(Twist, "cmd_vel", self._cb_cmd_vel, 10)

        self.publisher = self.create_publisher(StabilityMargin, "safety/stability_margin", 10)
        self.create_timer(0.1, self._publish_margin)
        self.get_logger().info("Stability Margin ready.")

    def _cb_pitch(self, msg: Float32) -> None:
        self.pitch_rad = msg.data

    def _cb_roll(self, msg: Float32) -> None:
        self.roll_rad = msg.data

    def _cb_tension(self, msg: Float32) -> None:
        self.winch_tension_n = msg.data

    def _cb_traction(self, msg: Float32) -> None:
        self.traction_factor = msg.data

    def _cb_cmd_vel(self, msg: Twist) -> None:
        self.linear_velocity_ms = msg.linear.x

    def _publish_margin(self) -> None:
        estimate = self.model.evaluate(
            pitch_rad=self.pitch_rad,
            roll_rad=self.roll_rad,
            linear_velocity_ms=self.linear_velocity_ms,
            winch_tension_n=self.winch_tension_n,
            traction_factor=self.traction_factor,
        )

        msg = StabilityMargin()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.longitudinal_margin = float(estimate.longitudinal_margin)
        msg.lateral_margin = float(estimate.lateral_margin)
        msg.rollover_risk = float(estimate.rollover_risk)
        msg.traction_margin = float(estimate.traction_margin)
        msg.margin = float(estimate.margin)
        msg.pitch_rad = float(self.pitch_rad)
        msg.roll_rad = float(self.roll_rad)
        msg.safe_linear_velocity_ms = float(estimate.safe_linear_velocity_ms)
        msg.safe_winch_tension_n = float(estimate.safe_winch_tension_n)
        msg.degraded = bool(estimate.degraded)
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = StabilityMarginNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
