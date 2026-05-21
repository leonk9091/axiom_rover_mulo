#!/usr/bin/env python3
"""Unified rover state estimation node."""

from __future__ import annotations

import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32

from rover_interfaces.msg import EnergyBudget, LinkState, MotorTelemetry, RoverState, SafetyState, StabilityMargin
from rover_system.estimation import RoverStateEstimator


class StateEstimationNode(Node):
    def __init__(self):
        super().__init__("state_estimation")
        self.get_logger().info("Initializing State Estimation Node...")

        self.declare_parameter("publish_period_s", 0.05)
        self.declare_parameter("stale_timeout_s", 1.0)
        self.declare_parameter("smoothing_alpha", 0.2)

        self.estimator = RoverStateEstimator(
            smoothing_alpha=float(self.get_parameter("smoothing_alpha").value)
        )
        self.stale_timeout_s = float(self.get_parameter("stale_timeout_s").value)
        self._last_imu_s = -1e9
        self._last_odom_s = -1e9
        self._last_energy_s = -1e9
        self._last_mode = "manual"

        self.create_subscription(Imu, "imu/data", self._cb_imu, 10)
        self.create_subscription(Odometry, "odom", self._cb_odom, 10)
        self.create_subscription(MotorTelemetry, "motor_telemetry", self._cb_motor_telemetry, 10)
        self.create_subscription(EnergyBudget, "power/energy_budget", self._cb_energy_budget, 10)
        self.create_subscription(StabilityMargin, "safety/stability_margin", self._cb_stability_margin, 10)
        self.create_subscription(SafetyState, "safety/state", self._cb_safety_state, 10)
        self.create_subscription(LinkState, "safety/link_state", self._cb_link_state, 10)
        self.create_subscription(Twist, "cmd_vel", self._cb_manual_cmd, 10)
        self.create_subscription(Twist, "mission/cmd_vel", self._cb_mission_cmd, 10)

        self.state_pub = self.create_publisher(RoverState, "system/rover_state", 10)
        self.pitch_pub = self.create_publisher(Float32, "sensors/pitch", 10)
        self.roll_pub = self.create_publisher(Float32, "sensors/roll", 10)

        self.create_timer(float(self.get_parameter("publish_period_s").value), self._publish_state)
        self.get_logger().info("State Estimation ready.")

    def _cb_imu(self, msg: Imu) -> None:
        q = msg.orientation
        self.estimator.update_imu_orientation(q.x, q.y, q.z, q.w)
        self._last_imu_s = time.monotonic()

    def _cb_odom(self, msg: Odometry) -> None:
        self.estimator.update_odometry(
            msg.twist.twist.linear.x,
            msg.twist.twist.angular.z,
        )
        self._last_odom_s = time.monotonic()

    def _cb_motor_telemetry(self, msg: MotorTelemetry) -> None:
        self.estimator.update_motor_telemetry(list(msg.motor_ids), list(msg.rpm))

    def _cb_energy_budget(self, msg: EnergyBudget) -> None:
        self.estimator.update_energy(msg.soc)
        self._last_energy_s = time.monotonic()

    def _cb_stability_margin(self, msg: StabilityMargin) -> None:
        self.estimator.update_stability(msg.margin)

    def _cb_safety_state(self, msg: SafetyState) -> None:
        self.estimator.update_safety(msg.estop_active, msg.system_ok)

    def _cb_link_state(self, msg: LinkState) -> None:
        if msg.command_only_mode:
            self._last_mode = "command_only"

    def _cb_manual_cmd(self, msg: Twist) -> None:
        self._last_mode = "manual"
        self.estimator.update_command(msg.linear.x, msg.angular.z, self._last_mode)

    def _cb_mission_cmd(self, msg: Twist) -> None:
        self._last_mode = "mission"
        self.estimator.update_command(msg.linear.x, msg.angular.z, self._last_mode)

    def _publish_state(self) -> None:
        estimate = self.estimator.estimate()
        now_s = time.monotonic()
        localization_ok = estimate.localization_ok and (
            (now_s - self._last_imu_s) <= self.stale_timeout_s
            or (now_s - self._last_odom_s) <= self.stale_timeout_s
        )
        if (now_s - self._last_energy_s) > 5.0:
            battery_soc = 0.0
        else:
            battery_soc = estimate.battery_soc

        msg = RoverState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.mode = estimate.mode
        msg.linear_velocity_ms = float(estimate.linear_velocity_ms)
        msg.angular_velocity_rads = float(estimate.angular_velocity_rads)
        msg.average_wheel_speed_ms = float(estimate.average_wheel_speed_ms)
        msg.slip_ratio = float(estimate.slip_ratio)
        msg.pitch_rad = float(estimate.pitch_rad)
        msg.roll_rad = float(estimate.roll_rad)
        msg.battery_soc = float(battery_soc)
        msg.stability_margin = float(estimate.stability_margin)
        msg.localization_ok = bool(localization_ok)
        msg.drive_ready = bool(estimate.drive_ready and localization_ok)
        msg.estop_active = bool(estimate.estop_active)
        self.state_pub.publish(msg)

        self.pitch_pub.publish(Float32(data=float(estimate.pitch_rad)))
        self.roll_pub.publish(Float32(data=float(estimate.roll_rad)))


def main(args=None):
    rclpy.init(args=args)
    node = StateEstimationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
