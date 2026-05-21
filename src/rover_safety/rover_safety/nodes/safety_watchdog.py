#!/usr/bin/env python3
"""Safety watchdog supervising critical ROS nodes and the unified hardware bridge."""

from __future__ import annotations

import json
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool, String

from rover_interfaces.msg import (
    EnergyBudget,
    FaultReport,
    HardwareState,
    LinkState,
    MotorTelemetry,
    RoverState,
    SafetyState,
)

HEARTBEAT_PERIOD_S = 0.1
WATCHDOG_CHECK_PERIOD_S = 0.2
NODE_TIMEOUT_S = 1.0
STARTUP_GRACE_S = 5.0

FAULT_WARNING = "WARNING"
FAULT_FAULT = "FAULT"
FAULT_CRITICAL = "CRITICAL"

CRITICAL_NODES = {
    "hardware_bridge": "hardware/state",
    "vesc_driver": "motor_telemetry",
    "winch_manager": "winch/status",
    "power_monitor": "power/energy_budget",
    "state_estimation": "system/rover_state",
}


class FaultRecord:
    def __init__(self, node_name: str, level: str, description: str, fault_code: str):
        self.node_name = node_name
        self.level = level
        self.description = description
        self.fault_code = fault_code
        self.timestamp = time.monotonic()
        self.active = True

    def to_dict(self) -> dict:
        return {
            "node": self.node_name,
            "level": self.level,
            "code": self.fault_code,
            "desc": self.description,
            "age_s": round(time.monotonic() - self.timestamp, 2),
        }


class SafetyWatchdogNode(Node):
    def __init__(self):
        super().__init__("safety_watchdog")
        self.get_logger().info("Initializing Safety Watchdog Node...")

        qos_reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            depth=10,
        )

        self.estop_active = False
        self.estop_reason = ""
        self.degraded_mode = "nominal"
        self.fault_log: list[FaultRecord] = []
        self.hardware_state: HardwareState | None = None
        self._startup_time = time.monotonic()
        self._node_last_seen: dict[str, float] = {name: time.monotonic() for name in CRITICAL_NODES}

        self.create_subscription(String, "winch/status", lambda _: self._node_heartbeat("winch_manager"), 10)
        self.create_subscription(EnergyBudget, "power/energy_budget", lambda _: self._node_heartbeat("power_monitor"), 10)
        self.create_subscription(MotorTelemetry, "motor_telemetry", lambda _: self._node_heartbeat("vesc_driver"), 10)
        self.create_subscription(String, "mission/autonomy_heartbeat", lambda _: self._node_heartbeat("shared_autonomy"), 10)
        self.create_subscription(RoverState, "system/rover_state", lambda _: self._node_heartbeat("state_estimation"), 10)
        self.create_subscription(HardwareState, "hardware/state", self._cb_hardware_state, 10)
        self.create_subscription(Bool, "safety/estop", self._cb_estop_request, qos_reliable)

        self.estop_pub = self.create_publisher(Bool, "safety/estop", qos_reliable)
        self.fault_pub = self.create_publisher(String, "safety/fault_log", 10)
        self.fault_report_pub = self.create_publisher(FaultReport, "safety/fault_report", 10)
        self.system_ok_pub = self.create_publisher(Bool, "safety/system_ok", 10)
        self.link_state_pub = self.create_publisher(LinkState, "safety/link_state", 10)
        self.safety_state_pub = self.create_publisher(SafetyState, "safety/state", 10)

        self.create_timer(HEARTBEAT_PERIOD_S, self._heartbeat_loop)
        self.create_timer(WATCHDOG_CHECK_PERIOD_S, self._watchdog_check)
        self.get_logger().info("Safety Watchdog ready.")

    def _cb_estop_request(self, msg: Bool) -> None:
        if msg.data and not self.estop_active:
            self._trigger_estop("E-Stop richiesto da topic ROS", "ros_estop_request", FAULT_CRITICAL)

    def _cb_hardware_state(self, msg: HardwareState) -> None:
        self.hardware_state = msg
        self._node_heartbeat("hardware_bridge")
        if msg.estop_hw and not self.estop_active:
            self._trigger_estop("E-Stop hardware ESP32", "hardware_estop", FAULT_CRITICAL)

    def _node_heartbeat(self, node_name: str) -> None:
        if node_name not in self._node_last_seen:
            return
        self._node_last_seen[node_name] = time.monotonic()
        for fault in self.fault_log:
            if fault.node_name == node_name and fault.fault_code.endswith("_timeout"):
                fault.active = False
                self._publish_fault_report(fault, recovered=True)

    def _heartbeat_loop(self) -> None:
        self._publish_link_state()

    def _watchdog_check(self) -> None:
        now = time.monotonic()
        all_ok = True
        startup_complete = (now - self._startup_time) >= STARTUP_GRACE_S

        for node_name in CRITICAL_NODES:
            age = now - self._node_last_seen[node_name]
            if startup_complete and age > NODE_TIMEOUT_S:
                all_ok = False
                code = f"{node_name}_timeout"
                if not any(f.fault_code == code and f.active for f in self.fault_log):
                    level = FAULT_CRITICAL if node_name in ("hardware_bridge", "vesc_driver", "winch_manager", "state_estimation") else FAULT_FAULT
                    self._register_fault(node_name, level, f"Nodo {node_name} non risponde da {age:.1f}s", code)
                    if level == FAULT_CRITICAL:
                        self._trigger_estop(f"Nodo critico {node_name} perso", code, level)

        primary_up = False
        fallback_up = False
        if self.hardware_state is not None:
            primary_up = bool(self.hardware_state.primary_link_up)
            fallback_up = bool(self.hardware_state.fallback_link_up)
            self.degraded_mode = self.hardware_state.degraded_mode or "nominal"
            if startup_complete and not self.hardware_state.bridge_connected:
                all_ok = False
                if not self.estop_active:
                    self._trigger_estop("Bridge hardware non connesso o dati stale", "hardware_bridge_stale", FAULT_CRITICAL)
        else:
            all_ok = not startup_complete
            self.degraded_mode = "bridge_missing"

        if primary_up:
            self.degraded_mode = "nominal"
        elif fallback_up:
            self.degraded_mode = "command_only"
        else:
            self.degraded_mode = "link_loss_hold"
            all_ok = not startup_complete
            if startup_complete and not self.estop_active:
                self._trigger_estop("Perdita completa dei link di supervisione", "link_loss_hold", FAULT_CRITICAL)

        self.system_ok_pub.publish(Bool(data=all_ok and not self.estop_active))
        self._publish_safety_state(all_ok)

        active_faults = [f.to_dict() for f in self.fault_log if f.active]
        if active_faults:
            self.fault_pub.publish(String(data=json.dumps(active_faults)))

    def _publish_link_state(self) -> None:
        msg = LinkState()
        msg.header.stamp = self.get_clock().now().to_msg()
        if self.hardware_state is not None:
            msg.primary_link_up = bool(self.hardware_state.primary_link_up)
            msg.fallback_link_up = bool(self.hardware_state.fallback_link_up)
            msg.packet_loss_ratio = 0.0 if msg.primary_link_up else 0.5 if msg.fallback_link_up else 1.0
        else:
            msg.primary_link_up = False
            msg.fallback_link_up = False
            msg.packet_loss_ratio = 1.0
        msg.heartbeat_age_s = 0.0 if self.hardware_state is not None else float(NODE_TIMEOUT_S)
        msg.rssi_dbm = -55.0 if msg.primary_link_up else -87.0 if msg.fallback_link_up else -120.0
        msg.degraded_mode = self.degraded_mode
        msg.command_only_mode = self.degraded_mode == "command_only"
        self.link_state_pub.publish(msg)

    def _publish_safety_state(self, all_ok: bool) -> None:
        msg = SafetyState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.system_ok = bool(all_ok and not self.estop_active)
        msg.estop_active = bool(self.estop_active)
        msg.watchdog_ok = bool(all_ok)
        msg.sto_available = bool(self.hardware_state.serial_connected) if self.hardware_state is not None else False
        msg.link_healthy = self.degraded_mode in ("nominal", "command_only")
        msg.degraded_mode = self.degraded_mode
        msg.estop_reason = self.estop_reason
        msg.active_faults = [json.dumps(f.to_dict()) for f in self.fault_log if f.active]
        self.safety_state_pub.publish(msg)

    def _trigger_estop(self, reason: str, fault_code: str, level: str = FAULT_CRITICAL) -> None:
        if self.estop_active:
            return
        self.estop_active = True
        self.estop_reason = reason
        self._register_fault("safety_watchdog", level, reason, fault_code)
        self.estop_pub.publish(Bool(data=True))
        self.get_logger().error(f"[{level}] E-STOP ATTIVATO: {reason}")

    def _register_fault(self, node_name: str, level: str, description: str, fault_code: str) -> None:
        record = FaultRecord(node_name, level, description, fault_code)
        self.fault_log.append(record)
        log_fn = {
            FAULT_WARNING: self.get_logger().warn,
            FAULT_FAULT: self.get_logger().error,
            FAULT_CRITICAL: self.get_logger().fatal,
        }.get(level, self.get_logger().error)
        log_fn(f"[{level}] {node_name}: {description}")
        self._publish_fault_report(record)

    def _publish_fault_report(self, record: FaultRecord, recovered: bool = False) -> None:
        report = FaultReport()
        report.header.stamp = self.get_clock().now().to_msg()
        report.source_node = record.node_name
        report.level = record.level if not recovered else "INFO"
        report.fault_code = record.fault_code
        report.message = record.description
        report.latched = record.level == FAULT_CRITICAL
        report.recovered = recovered
        self.fault_report_pub.publish(report)


def main(args=None):
    rclpy.init(args=args)
    node = SafetyWatchdogNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
