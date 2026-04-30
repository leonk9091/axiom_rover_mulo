#!/usr/bin/env python3
"""Safety watchdog with degraded link supervision and hardware heartbeat."""

from __future__ import annotations

import json
import threading
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool, Float32, String

from rover_interfaces.msg import LinkState, MotorTelemetry, SafetyState

try:
    import serial
except ImportError:  # pragma: no cover - runtime dependency on target only
    serial = None

HEARTBEAT_PERIOD_S = 0.1
WATCHDOG_CHECK_PERIOD_S = 0.2
NODE_TIMEOUT_S = 1.0
ESP32_TIMEOUT_S = 0.5
LINK_TIMEOUT_S = 1.5
ESP32_BAUD = 115200
ESP32_PORT = "/dev/ttyUSB0"

FAULT_WARNING = "WARNING"
FAULT_FAULT = "FAULT"
FAULT_CRITICAL = "CRITICAL"

CRITICAL_NODES = {
    "winch_manager": "winch/status",
    "power_monitor": "battery/soc_estimated",
    "shared_autonomy": "mission/cmd_vel",
    "vesc_driver": "motor_telemetry",
}


class FaultRecord:
    def __init__(self, node_name: str, level: str, description: str):
        self.node_name = node_name
        self.level = level
        self.description = description
        self.timestamp = time.monotonic()
        self.active = True

    def to_dict(self) -> dict:
        return {
            "node": self.node_name,
            "level": self.level,
            "desc": self.description,
            "age_s": round(time.monotonic() - self.timestamp, 2),
        }


class ESP32SafetyBridge:
    def __init__(self, port: str, baud: int, logger):
        self.logger = logger
        self._seq = 0
        self._last_rx_time = time.monotonic()
        self._lock = threading.Lock()
        self._hw_estop = False
        self.connected = False
        self._serial = None

        if serial is None:
            logger.warn("pyserial non disponibile. Safety MCU in modalità simulata.")
            return

        try:
            self._serial = serial.Serial(port, baud, timeout=0.1)
            self.connected = True
            logger.info(f"ESP32 connesso su {port} @ {baud} bps")
        except serial.SerialException as exc:
            logger.warn(f"ESP32 non disponibile ({exc}). Modalità simulata.")

    def send_heartbeat(self, estop: bool) -> None:
        if not self.connected or self._serial is None:
            return
        self._seq += 1
        msg = json.dumps({"cmd": "heartbeat", "seq": self._seq, "estop": estop}) + "\n"
        with self._lock:
            try:
                self._serial.write(msg.encode())
            except serial.SerialException as exc:
                self.logger.error(f"Errore TX ESP32: {exc}")
                self.connected = False

    def read_response(self) -> None:
        if not self.connected or self._serial is None:
            return
        with self._lock:
            try:
                line = self._serial.readline().decode().strip()
                if not line:
                    return
                data = json.loads(line)
                self._hw_estop = bool(data.get("estop_hw", False))
                self._last_rx_time = time.monotonic()
            except (json.JSONDecodeError, UnicodeDecodeError, serial.SerialException):
                return

    def is_alive(self) -> bool:
        return (time.monotonic() - self._last_rx_time) < ESP32_TIMEOUT_S

    def hw_estop_triggered(self) -> bool:
        return self._hw_estop

    def close(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()


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
        self._node_last_seen: dict[str, float] = {name: time.monotonic() for name in CRITICAL_NODES}
        self._primary_link_seen = time.monotonic()
        self._fallback_link_seen = time.monotonic()

        self.esp32 = ESP32SafetyBridge(ESP32_PORT, ESP32_BAUD, self.get_logger())

        self.create_subscription(String, "winch/status", lambda _: self._node_heartbeat("winch_manager"), 10)
        self.create_subscription(Float32, "battery/soc_estimated", lambda _: self._node_heartbeat("power_monitor"), 10)
        self.create_subscription(MotorTelemetry, "motor_telemetry", lambda _: self._node_heartbeat("vesc_driver"), 10)
        self.create_subscription(Bool, "safety/estop", self._cb_estop_request, qos_reliable)
        self.create_subscription(Bool, "ops/primary_link_heartbeat", self._cb_primary_link, 10)
        self.create_subscription(Bool, "ops/fallback_link_heartbeat", self._cb_fallback_link, 10)
        self.create_subscription(String, "mission/autonomy_heartbeat", lambda _: self._node_heartbeat("shared_autonomy"), 10)

        self.estop_pub = self.create_publisher(Bool, "safety/estop", qos_reliable)
        self.fault_pub = self.create_publisher(String, "safety/fault_log", 10)
        self.system_ok_pub = self.create_publisher(Bool, "safety/system_ok", 10)
        self.link_state_pub = self.create_publisher(LinkState, "safety/link_state", 10)
        self.safety_state_pub = self.create_publisher(SafetyState, "safety/state", 10)

        self.create_timer(HEARTBEAT_PERIOD_S, self._heartbeat_loop)
        self.create_timer(WATCHDOG_CHECK_PERIOD_S, self._watchdog_check)
        self.get_logger().info("Safety Watchdog ready.")

    def _cb_estop_request(self, msg: Bool) -> None:
        if msg.data and not self.estop_active:
            self._trigger_estop("E-Stop richiesto da topic ROS", FAULT_CRITICAL)

    def _cb_primary_link(self, _msg: Bool) -> None:
        self._primary_link_seen = time.monotonic()

    def _cb_fallback_link(self, _msg: Bool) -> None:
        self._fallback_link_seen = time.monotonic()

    def _node_heartbeat(self, node_name: str) -> None:
        self._node_last_seen[node_name] = time.monotonic()
        for fault in self.fault_log:
            if fault.node_name == node_name and "non risponde" in fault.description:
                fault.active = False

    def _heartbeat_loop(self) -> None:
        self.esp32.send_heartbeat(self.estop_active)
        self.esp32.read_response()

        if self.esp32.hw_estop_triggered() and not self.estop_active:
            self._trigger_estop("E-Stop hardware ESP32", FAULT_CRITICAL)

        if self.esp32.connected and not self.esp32.is_alive():
            self._trigger_estop("ESP32 safety MCU non risponde", FAULT_CRITICAL)

        self._publish_link_state()

    def _watchdog_check(self) -> None:
        now = time.monotonic()
        all_ok = True

        for node_name in CRITICAL_NODES:
            age = now - self._node_last_seen[node_name]
            if age > NODE_TIMEOUT_S:
                all_ok = False
                if not any(f.node_name == node_name and f.active for f in self.fault_log):
                    level = FAULT_CRITICAL if node_name in ("winch_manager", "vesc_driver") else FAULT_FAULT
                    self._register_fault(node_name, level, f"Nodo {node_name} non risponde da {age:.1f}s")
                    if level == FAULT_CRITICAL:
                        self._trigger_estop(f"Nodo critico {node_name} perso", level)

        primary_up = (now - self._primary_link_seen) < LINK_TIMEOUT_S
        fallback_up = (now - self._fallback_link_seen) < LINK_TIMEOUT_S
        if primary_up:
            self.degraded_mode = "nominal"
        elif fallback_up:
            self.degraded_mode = "command_only"
        else:
            self.degraded_mode = "link_loss_hold"
            all_ok = False
            if not self.estop_active:
                self._trigger_estop("Perdita completa dei link di supervisione", FAULT_CRITICAL)

        self.system_ok_pub.publish(Bool(data=all_ok and not self.estop_active))
        self._publish_safety_state(all_ok)

        active_faults = [f.to_dict() for f in self.fault_log if f.active]
        if active_faults:
            self.fault_pub.publish(String(data=json.dumps(active_faults)))

    def _publish_link_state(self) -> None:
        now = time.monotonic()
        primary_age = now - self._primary_link_seen
        fallback_age = now - self._fallback_link_seen
        primary_up = primary_age < LINK_TIMEOUT_S
        fallback_up = fallback_age < LINK_TIMEOUT_S

        msg = LinkState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.primary_link_up = primary_up
        msg.fallback_link_up = fallback_up
        msg.heartbeat_age_s = float(min(primary_age, fallback_age))
        msg.packet_loss_ratio = 0.0 if primary_up else 0.5 if fallback_up else 1.0
        msg.rssi_dbm = -55.0 if primary_up else -87.0 if fallback_up else -120.0
        msg.degraded_mode = self.degraded_mode
        msg.command_only_mode = self.degraded_mode == "command_only"
        self.link_state_pub.publish(msg)

    def _publish_safety_state(self, all_ok: bool) -> None:
        msg = SafetyState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.system_ok = bool(all_ok and not self.estop_active)
        msg.estop_active = bool(self.estop_active)
        msg.watchdog_ok = bool(all_ok)
        msg.sto_available = bool(self.esp32.connected)
        msg.link_healthy = self.degraded_mode in ("nominal", "command_only")
        msg.degraded_mode = self.degraded_mode
        msg.estop_reason = self.estop_reason
        msg.active_faults = [json.dumps(f.to_dict()) for f in self.fault_log if f.active]
        self.safety_state_pub.publish(msg)

    def _trigger_estop(self, reason: str, level: str = FAULT_CRITICAL) -> None:
        if self.estop_active:
            return
        self.estop_active = True
        self.estop_reason = reason
        self._register_fault("safety_watchdog", level, reason)
        self.estop_pub.publish(Bool(data=True))
        self.esp32.send_heartbeat(estop=True)
        self.get_logger().error(f"[{level}] E-STOP ATTIVATO: {reason}")

    def _register_fault(self, node_name: str, level: str, description: str) -> None:
        self.fault_log.append(FaultRecord(node_name, level, description))
        log_fn = {
            FAULT_WARNING: self.get_logger().warn,
            FAULT_FAULT: self.get_logger().error,
            FAULT_CRITICAL: self.get_logger().fatal,
        }.get(level, self.get_logger().error)
        log_fn(f"[{level}] {node_name}: {description}")

    def destroy_node(self):
        self.esp32.close()
        super().destroy_node()


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
