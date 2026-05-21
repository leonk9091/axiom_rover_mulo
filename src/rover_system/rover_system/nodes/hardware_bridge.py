#!/usr/bin/env python3
"""Unified hardware bridge for ESP32 safety MCU and auxiliary raw signals."""

from __future__ import annotations

import json
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32

from rover_interfaces.msg import FaultReport, HardwareState
from rover_system.bridge_model import HardwareBridgeModel

try:
    import serial
except ImportError:  # pragma: no cover - runtime dependency on target only
    serial = None


class HardwareBridgeNode(Node):
    def __init__(self):
        super().__init__("hardware_bridge")
        self.get_logger().info("Initializing Hardware Bridge Node...")

        self.declare_parameter("serial_port", "/dev/ttyUSB0")
        self.declare_parameter("serial_baud", 115200)
        self.declare_parameter("heartbeat_period_s", 0.1)
        self.declare_parameter("publish_period_s", 0.1)
        self.declare_parameter("serial_stale_s", 0.5)
        self.declare_parameter("battery_stale_s", 1.5)
        self.declare_parameter("link_stale_s", 1.5)
        self.declare_parameter("thermal_headroom_default", 1.0)
        self.declare_parameter("simulate_without_serial", True)

        self.serial_port = self.get_parameter("serial_port").value
        self.serial_baud = int(self.get_parameter("serial_baud").value)
        self.heartbeat_period_s = float(self.get_parameter("heartbeat_period_s").value)
        self.publish_period_s = float(self.get_parameter("publish_period_s").value)
        self.simulate_without_serial = bool(self.get_parameter("simulate_without_serial").value)

        self.model = HardwareBridgeModel(
            serial_stale_s=float(self.get_parameter("serial_stale_s").value),
            battery_stale_s=float(self.get_parameter("battery_stale_s").value),
            link_stale_s=float(self.get_parameter("link_stale_s").value),
            thermal_headroom_default=float(self.get_parameter("thermal_headroom_default").value),
        )
        self.estop_request = False
        self.ice_on = False
        self.dump_load_on = False
        self._fault_states: set[str] = set()
        self._seq = 0
        self._serial = None
        self._last_connect_attempt_s = -1e9

        self.create_subscription(Bool, "safety/estop", self._cb_estop, 10)
        self.create_subscription(Bool, "hardware/ice_generator_start", self._cb_ice, 10)
        self.create_subscription(Bool, "hardware/dump_load_enable", self._cb_dump_load, 10)
        self.create_subscription(Float32, "hardware/battery_voltage_raw", self._cb_battery_voltage, 10)
        self.create_subscription(Float32, "hardware/battery_current_raw", self._cb_battery_current, 10)
        self.create_subscription(Float32, "hardware/thermal_headroom_raw", self._cb_thermal, 10)
        self.create_subscription(Bool, "hardware/primary_link_raw", self._cb_primary_link, 10)
        self.create_subscription(Bool, "hardware/fallback_link_raw", self._cb_fallback_link, 10)

        self.hardware_pub = self.create_publisher(HardwareState, "hardware/state", 10)
        self.fault_pub = self.create_publisher(FaultReport, "safety/fault_report", 10)
        self.winch_tension_pub = self.create_publisher(Float32, "winch/load_cell_tension", 10)
        self.cable_length_pub = self.create_publisher(Float32, "winch/cable_length_m", 10)
        self.battery_voltage_pub = self.create_publisher(Float32, "battery/voltage", 10)
        self.battery_current_pub = self.create_publisher(Float32, "battery/current", 10)
        self.power_demand_pub = self.create_publisher(Float32, "system/power_demand_w", 10)
        self.thermal_headroom_pub = self.create_publisher(Float32, "power/thermal_headroom", 10)

        self._connect_serial()
        self.create_timer(self.heartbeat_period_s, self._io_loop)
        self.create_timer(self.publish_period_s, self._publish_loop)
        self.get_logger().info("Hardware Bridge ready.")

    def _connect_serial(self) -> None:
        self._last_connect_attempt_s = time.monotonic()
        if serial is None:
            self.get_logger().warn("pyserial non disponibile. Bridge in modalità degradata.")
            return
        try:
            self._serial = serial.Serial(self.serial_port, self.serial_baud, timeout=0.01)
            self.get_logger().info(f"ESP32 bridge connesso su {self.serial_port} @ {self.serial_baud} bps")
        except serial.SerialException as exc:
            self._serial = None
            if not self.simulate_without_serial:
                self.get_logger().error(f"Impossibile connettere seriale ESP32: {exc}")
            else:
                self.get_logger().warn(f"ESP32 non disponibile ({exc}). Modalità simulata.")

    def _cb_estop(self, msg: Bool) -> None:
        self.estop_request = bool(msg.data)

    def _cb_ice(self, msg: Bool) -> None:
        self.ice_on = bool(msg.data)

    def _cb_dump_load(self, msg: Bool) -> None:
        self.dump_load_on = bool(msg.data)

    def _cb_battery_voltage(self, msg: Float32) -> None:
        self.model.update_battery_voltage(msg.data, time.monotonic())

    def _cb_battery_current(self, msg: Float32) -> None:
        self.model.update_battery_current(msg.data, time.monotonic())

    def _cb_thermal(self, msg: Float32) -> None:
        self.model.update_thermal_headroom(msg.data, time.monotonic())

    def _cb_primary_link(self, msg: Bool) -> None:
        self.model.update_primary_link(msg.data, time.monotonic())

    def _cb_fallback_link(self, msg: Bool) -> None:
        self.model.update_fallback_link(msg.data, time.monotonic())

    def _io_loop(self) -> None:
        if self._serial is None:
            self.model.note_serial_disconnected()
            if self.simulate_without_serial:
                self.model.update_serial_payload(
                    {
                        "encoder": self.model.cable_length_m,
                        "tension": self.model.winch_tension_n,
                        "estop_hw": self.estop_request,
                    },
                    time.monotonic(),
                )
            elif (time.monotonic() - self._last_connect_attempt_s) > 1.0:
                self._connect_serial()
            return

        self._seq += 1
        command = {
            "cmd": "heartbeat",
            "seq": self._seq,
            "estop": self.estop_request,
            "ice_on": self.ice_on,
            "dump_load": self.dump_load_on,
        }
        try:
            self._serial.write((json.dumps(command) + "\n").encode())
            while self._serial.in_waiting:
                line = self._serial.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                payload = json.loads(line)
                now_s = time.monotonic()
                if payload.get("boot"):
                    continue
                self.model.update_serial_payload(payload, now_s)
        except (serial.SerialException, OSError, json.JSONDecodeError) as exc:
            self.model.note_serial_disconnected()
            self._serial = None
            self._publish_fault("hardware_bridge", "CRITICAL", "serial_io_error", str(exc), latched=True)

    def _publish_loop(self) -> None:
        snapshot = self.model.snapshot(time.monotonic())

        msg = HardwareState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.bridge_connected = snapshot.bridge_connected
        msg.serial_connected = snapshot.serial_connected
        msg.estop_hw = snapshot.estop_hw
        msg.primary_link_up = snapshot.primary_link_up
        msg.fallback_link_up = snapshot.fallback_link_up
        msg.load_cell_valid = snapshot.load_cell_valid
        msg.cable_encoder_valid = snapshot.cable_encoder_valid
        msg.battery_valid = snapshot.battery_valid
        msg.cable_length_m = float(snapshot.cable_length_m)
        msg.cable_velocity_ms = float(snapshot.cable_velocity_ms)
        msg.winch_tension_n = float(snapshot.winch_tension_n)
        msg.battery_voltage_v = float(snapshot.battery_voltage_v)
        msg.battery_current_a = float(snapshot.battery_current_a)
        msg.battery_power_w = float(snapshot.battery_power_w)
        msg.thermal_headroom = float(snapshot.thermal_headroom)
        msg.degraded_mode = snapshot.degraded_mode
        msg.active_faults = list(snapshot.active_faults)
        self.hardware_pub.publish(msg)

        self.winch_tension_pub.publish(Float32(data=float(snapshot.winch_tension_n)))
        self.cable_length_pub.publish(Float32(data=float(snapshot.cable_length_m)))
        self.battery_voltage_pub.publish(Float32(data=float(snapshot.battery_voltage_v)))
        self.battery_current_pub.publish(Float32(data=float(snapshot.battery_current_a)))
        self.power_demand_pub.publish(Float32(data=float(snapshot.battery_power_w)))
        self.thermal_headroom_pub.publish(Float32(data=float(snapshot.thermal_headroom)))

        self._sync_faults(snapshot.active_faults)

    def _sync_faults(self, active_faults: list[str]) -> None:
        current = set(active_faults)
        for fault_code in sorted(current - self._fault_states):
            self._publish_fault("hardware_bridge", "FAULT", fault_code, fault_code.replace("_", " "), latched=True)
        for fault_code in sorted(self._fault_states - current):
            self._publish_fault("hardware_bridge", "INFO", fault_code, fault_code.replace("_", " "), recovered=True)
        self._fault_states = current

    def _publish_fault(
        self,
        source_node: str,
        level: str,
        fault_code: str,
        message: str,
        *,
        latched: bool = False,
        recovered: bool = False,
    ) -> None:
        report = FaultReport()
        report.header.stamp = self.get_clock().now().to_msg()
        report.source_node = source_node
        report.level = level
        report.fault_code = fault_code
        report.message = message
        report.latched = latched
        report.recovered = recovered
        self.fault_pub.publish(report)

    def destroy_node(self):
        if self._serial and self._serial.is_open:
            self._serial.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = HardwareBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
