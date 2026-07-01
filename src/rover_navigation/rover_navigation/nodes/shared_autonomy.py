#!/usr/bin/env python3
"""Shared-autonomy mission node for trail-following and assisted trekking."""

from __future__ import annotations

import asyncio
import math
import time
from typing import Optional

import rclpy
from geometry_msgs.msg import PoseStamped, Twist, Vector3Stamped
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from std_msgs.msg import Bool, String

from rover_interfaces.action import FollowLeader
from rover_interfaces.msg import LinkState, StabilityMargin, TerrainCost, WinchState
from rover_navigation.autonomy import (
    LeaderObservation,
    LinkDecision,
    SharedAutonomyCore,
    StabilityDecision,
    TerrainDecision,
    WinchObservation,
)


class SharedAutonomyNode(Node):
    def __init__(self):
        super().__init__("shared_autonomy")
        self.get_logger().info("Initializing Shared Autonomy Node...")

        self.core = SharedAutonomyCore()
        self.target_distance_m = 1.5
        self.max_linear_velocity_ms = 1.0
        self.max_angular_velocity_rads = 0.8
        self.allow_reverse = False
        self.estop_active = False

        # Stati stradali e Guinzaglio
        self.road_state = "nominal"
        self.leash_enabled = False
        self._last_pull_time = 0.0
        self._pull_active = False

        self.leader_observation = LeaderObservation(False, 0.0, 0.0, 0.0)
        self.terrain_decision = TerrainDecision(True, 0.6, 0.5, 0.0)
        self.stability_decision = StabilityDecision(1.0, 1.0, False)
        self.link_decision = LinkDecision(True, True, False, "nominal")
        self.winch_observation = WinchObservation("passive", 0.0, 0.0, 0.0)
        self._active_goal_handle: Optional[object] = None
        self._last_control_mode = "idle"

        self.create_subscription(Vector3Stamped, "mission/leader_vector", self._cb_leader_vector, 10)
        self.create_subscription(TerrainCost, "terrain/cost", self._cb_terrain_cost, 10)
        self.create_subscription(StabilityMargin, "safety/stability_margin", self._cb_stability_margin, 10)
        self.create_subscription(LinkState, "safety/link_state", self._cb_link_state, 10)
        self.create_subscription(Bool, "safety/estop", self._cb_estop, 10)
        self.create_subscription(WinchState, "winch/state", self._cb_winch_state, 10)
        self.create_subscription(String, "navigation/road_state", self._cb_road_state, 10)
        self.create_subscription(Bool, "navigation/leash_enabled", self._cb_leash_enabled, 10)

        self.cmd_pub = self.create_publisher(Twist, "mission/cmd_vel", 10)
        self.target_pub = self.create_publisher(PoseStamped, "mission/target_pose", 10)
        self.heartbeat_pub = self.create_publisher(String, "mission/autonomy_heartbeat", 10)
        self.road_state_pub = self.create_publisher(String, "navigation/current_road_state", 10)

        self.action_server = ActionServer(
            self,
            FollowLeader,
            "mission/follow_leader",
            execute_callback=self._execute_follow_leader,
            goal_callback=self._goal_callback,
            cancel_callback=self._cancel_callback,
        )
        self.create_timer(0.05, self._control_loop)
        self.get_logger().info("Shared Autonomy ready.")

    def _goal_callback(self, goal_request: FollowLeader.Goal):
        self.target_distance_m = goal_request.target_distance_m or self.target_distance_m
        self.max_linear_velocity_ms = (
            goal_request.max_linear_velocity_ms or self.max_linear_velocity_ms
        )
        self.max_angular_velocity_rads = (
            goal_request.max_angular_velocity_rads or self.max_angular_velocity_rads
        )
        self.allow_reverse = goal_request.allow_reverse
        return GoalResponse.ACCEPT

    def _cancel_callback(self, _goal_handle):
        self._stop_motion()
        return CancelResponse.ACCEPT

    async def _execute_follow_leader(self, goal_handle):
        self._active_goal_handle = goal_handle
        while rclpy.ok() and goal_handle.is_active:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self._stop_motion()
                result = FollowLeader.Result()
                result.success = False
                result.result_message = "Goal cancelled"
                result.final_distance_error_m = 0.0
                self._active_goal_handle = None
                return result

            feedback = FollowLeader.Feedback()
            feedback.target_visible = self.leader_observation.visible
            feedback.target_range_m = float(self.leader_observation.range_m)
            feedback.target_bearing_rad = float(self.leader_observation.bearing_rad)
            feedback.stability_margin = float(self.stability_decision.margin)
            feedback.control_mode = self._last_control_mode
            goal_handle.publish_feedback(feedback)
            await asyncio.sleep(0.2)

        result = FollowLeader.Result()
        result.success = True
        result.result_message = "Follow leader server stopped"
        result.final_distance_error_m = float(
            self.leader_observation.range_m - self.target_distance_m
        )
        self._active_goal_handle = None
        return result

    def _cb_leader_vector(self, msg: Vector3Stamped) -> None:
        self.leader_observation = LeaderObservation(
            visible=msg.vector.z > 0.1,
            range_m=max(0.0, msg.vector.x),
            bearing_rad=msg.vector.y,
            confidence=max(0.0, min(1.0, msg.vector.z)),
        )

    def _cb_terrain_cost(self, msg: TerrainCost) -> None:
        self.terrain_decision = TerrainDecision(
            traversable=msg.traversable,
            recommended_speed_ms=msg.recommended_speed_ms,
            confidence=msg.confidence,
            slip_risk=msg.slip_risk,
        )

    def _cb_stability_margin(self, msg: StabilityMargin) -> None:
        self.stability_decision = StabilityDecision(
            margin=msg.margin,
            safe_linear_velocity_ms=msg.safe_linear_velocity_ms,
            degraded=msg.degraded,
        )

    def _cb_link_state(self, msg: LinkState) -> None:
        self.link_decision = LinkDecision(
            primary_link_up=msg.primary_link_up,
            fallback_link_up=msg.fallback_link_up,
            command_only_mode=msg.command_only_mode,
            degraded_mode=msg.degraded_mode,
        )

    def _cb_estop(self, msg: Bool) -> None:
        self.estop_active = msg.data

    def _cb_road_state(self, msg: String) -> None:
        self.road_state = msg.data.strip().lower()

    def _cb_leash_enabled(self, msg: Bool) -> None:
        self.leash_enabled = msg.data

    def _cb_winch_state(self, msg: WinchState) -> None:
        self.winch_observation = WinchObservation(
            mode=msg.mode,
            tension_measured_n=msg.tension_measured_n,
            cable_length_m=msg.cable_length_m,
            cable_velocity_ms=msg.cable_velocity_ms,
        )

        # Riconoscimento del Doppio Strattone (Handshake Attraversamento)
        now = time.monotonic()
        tension = msg.tension_measured_n
        if tension > 100.0:
            if not self._pull_active:
                self._pull_active = True
                # Intervallo corretto tra i due strattoni (tra 0.2s e 1.5s)
                if 0.2 < (now - self._last_pull_time) < 1.5:
                    self.get_logger().info("DOPPIO STRATTONE RILEVATO: Handshake per Attraversamento Strada!")
                    if self.road_state == "waiting_for_crossing":
                        self.road_state = "crossing"
                self._last_pull_time = now
        else:
            self._pull_active = False

    def _control_loop(self) -> None:
        if self.estop_active:
            self._stop_motion()
            return

        command = self.core.compute_command(
            observation=self.leader_observation,
            terrain=self.terrain_decision,
            stability=self.stability_decision,
            link=self.link_decision,
            winch=self.winch_observation,
            target_distance_m=self.target_distance_m,
            max_linear_velocity_ms=self.max_linear_velocity_ms,
            max_angular_velocity_rads=self.max_angular_velocity_rads,
            allow_reverse=self.allow_reverse,
            leash_enabled=self.leash_enabled,
            road_state=self.road_state,
        )

        twist = Twist()
        twist.linear.x = float(command.linear_velocity_ms)
        twist.angular.z = float(command.angular_velocity_rads)
        self.cmd_pub.publish(twist)
        self._last_control_mode = command.control_mode
        self.heartbeat_pub.publish(String(data=command.control_mode))
        self.road_state_pub.publish(String(data=self.road_state))

        if self.leader_observation.visible:
            target = PoseStamped()
            target.header.stamp = self.get_clock().now().to_msg()
            target.header.frame_id = "base_link"
            target.pose.position.x = float(self.leader_observation.range_m)
            target.pose.position.y = float(
                math.tan(self.leader_observation.bearing_rad) * max(self.leader_observation.range_m, 0.1)
            )
            self.target_pub.publish(target)

    def _stop_motion(self) -> None:
        self.cmd_pub.publish(Twist())

    def destroy_node(self):
        self.action_server.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SharedAutonomyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
