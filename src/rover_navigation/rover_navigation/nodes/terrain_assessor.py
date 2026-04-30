#!/usr/bin/env python3
"""Fuse terrain semantics and slope into a terrain-aware traversal cost."""

from __future__ import annotations

import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

from rover_interfaces.msg import TerrainCost


TERRAIN_BASE_TRAVERSABILITY = {
    "asphalt": 0.95,
    "gravel": 0.80,
    "grass": 0.70,
    "sand": 0.45,
    "mud": 0.35,
    "rock": 0.60,
}

TERRAIN_BASE_SPEED = {
    "asphalt": 1.20,
    "gravel": 0.95,
    "grass": 0.80,
    "sand": 0.45,
    "mud": 0.35,
    "rock": 0.55,
}


class TerrainAssessorNode(Node):
    def __init__(self):
        super().__init__("terrain_assessor")
        self.get_logger().info("Initializing Terrain Assessor Node...")
        self.terrain_class = "asphalt"
        self.traction_factor = 1.0
        self.pitch_rad = 0.0
        self.roll_rad = 0.0
        self.slip_ratio = 0.0

        self.create_subscription(String, "navigation/terrain_type", self._cb_terrain_type, 10)
        self.create_subscription(Float32, "navigation/traction_factor", self._cb_traction, 10)
        self.create_subscription(Float32, "sensors/pitch", self._cb_pitch, 10)
        self.create_subscription(Float32, "sensors/roll", self._cb_roll, 10)
        self.create_subscription(Float32, "control/slip_ratio", self._cb_slip, 10)

        self.publisher = self.create_publisher(TerrainCost, "terrain/cost", 10)
        self.create_timer(0.2, self._publish_cost)
        self.get_logger().info("Terrain Assessor ready.")

    def _cb_terrain_type(self, msg: String) -> None:
        self.terrain_class = msg.data.strip().lower() or "asphalt"

    def _cb_traction(self, msg: Float32) -> None:
        self.traction_factor = msg.data

    def _cb_pitch(self, msg: Float32) -> None:
        self.pitch_rad = msg.data

    def _cb_roll(self, msg: Float32) -> None:
        self.roll_rad = msg.data

    def _cb_slip(self, msg: Float32) -> None:
        self.slip_ratio = msg.data

    def _publish_cost(self) -> None:
        terrain = self.terrain_class if self.terrain_class in TERRAIN_BASE_TRAVERSABILITY else "grass"
        slope_rad = math.sqrt(self.pitch_rad**2 + self.roll_rad**2)
        roughness = min(1.0, abs(self.roll_rad) * 1.5 + abs(self.pitch_rad))
        slip_risk = min(1.0, max(abs(self.slip_ratio), 1.0 - max(self.traction_factor, 0.1)))
        vegetation_density = 0.6 if terrain in ("grass", "mud") else 0.2
        traversability = TERRAIN_BASE_TRAVERSABILITY[terrain]
        traversability *= max(0.2, 1.0 - 0.6 * roughness)
        traversability *= max(0.2, 1.0 - 0.5 * slip_risk)
        recommended_speed = TERRAIN_BASE_SPEED[terrain]
        recommended_speed *= max(0.2, 1.0 - 0.5 * roughness)
        recommended_speed *= max(0.2, 1.0 - 0.6 * slip_risk)
        confidence = max(0.3, min(1.0, 0.85 * self.traction_factor + 0.15 * traversability))

        msg = TerrainCost()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.terrain_class = terrain
        msg.slope_rad = float(slope_rad)
        msg.roughness = float(roughness)
        msg.slip_risk = float(slip_risk)
        msg.vegetation_density = float(vegetation_density)
        msg.traversability = float(traversability)
        msg.confidence = float(confidence)
        msg.recommended_speed_ms = float(recommended_speed)
        msg.traversable = traversability > 0.35
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TerrainAssessorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
