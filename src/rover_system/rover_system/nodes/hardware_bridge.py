#!/usr/bin/env python3
"""Unified hardware bridge for STM32 safety MCU and auxiliary raw signals."""

from __future__ import annotations

import json
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Bool, Float32

from rover_interfaces.msg import FaultReport, HardwareState, McuStatus, SafetyCommand
from rover_system.bridge_model import (
    HardwareBridgeModel,
    add_auxiliary_command_crc,
    build_safety_command_frame,
    validate_mcu_status_payload,
)

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
        self.declare_parameter("allow_unsigned_mcu_status", False)
        self.declare_parameter("command_timeout_ms", 250)
        self.declare_parameter("max_current_a", 18.0)

        self.serial_port = self.get_parameter("serial_port").value
        self.serial_baud = int(self.get_parameter("serial_baud").value)
        self.heartbeat_period_s = float(self.get_parameter("heartbeat_period_s").value)
        self.publish_period_s = float(self.get_parameter("publish_period_s").value)
        self.simulate_without_serial = bool(self.get_parameter("simulate_without_serial").value)
        self.allow_unsigned_mcu_status = bool(self.get_parameter("allow_unsigned_mcu_status").value)
        self.command_timeout_ms = int(self.get_parameter("command_timeout_ms").value)
        self.max_current_a = float(self.get_parameter("max_current_a").value)

        self.model = HardwareBridgeModel(
            serial_stale_s=float(self.get_parameter("serial_stale_s").value),
            battery_stale_s=float(self.get_parameter("battery_stale_s").value),
            link_stale_s=float(self.get_parameter("link_stale_s").value),
            thermal_headroom_default=float(self.get_parameter("thermal_headroom_default").value),
        )
        self.estop_request = False
        self.ice_on = False
        self.ice_kill = False
        self.dump_load_on = False
        self.rex_charge_current_a = 0.0
        self.rex_throttle_request = 0.0
        self.desired_linear_velocity_ms = 0.0
        self.desired_angular_velocity_rads = 0.0
        self.command_mode = "manual"
        self.enable_motors_request = False
        self._last_motion_cmd_s = -1e9
        self._fault_states: set[str] = set()
        self._seq = 0
        self._last_command_frame: dict | None = None
        self._last_mcu_payload: dict = {}
        self._serial = None
        self._last_connect_attempt_s = -1e9
        self._start_time_s = time.monotonic()

        self.create_subscription(Bool, "safety/estop", self._cb_estop, 10)
        self.create_subscription(Bool, "hardware/ice_generator_start", self._cb_ice, 10)
        self.create_subscription(Bool, "hardware/ice_generator_kill", self._cb_ice_kill, 10)
        self.create_subscription(Bool, "hardware/dump_load_enable", self._cb_dump_load, 10)
        self.create_subscription(
            Float32, "hardware/range_extender_charge_current_a", self._cb_rex_charge_current, 10
        )
        self.create_subscription(
            Float32, "hardware/range_extender_throttle_request", self._cb_rex_throttle, 10
        )
        self.create_subscription(Twist, "mission/cmd_vel", self._cb_mission_cmd_vel, 10)
        self.create_subscription(Twist, "cmd_vel", self._cb_manual_cmd_vel, 10)
        self.create_subscription(Float32, "hardware/battery_voltage_raw", self._cb_battery_voltage, 10)
        self.create_subscription(Float32, "hardware/battery_current_raw", self._cb_battery_current, 10)
        self.create_subscription(Float32, "hardware/thermal_headroom_raw", self._cb_thermal, 10)
        self.create_subscription(Bool, "hardware/primary_link_raw", self._cb_primary_link, 10)
        self.create_subscription(Bool, "hardware/fallback_link_raw", self._cb_fallback_link, 10)

        self.hardware_pub = self.create_publisher(HardwareState, "hardware/state", 10)
        self.safety_command_pub = self.create_publisher(SafetyCommand, "safety/mcu_command", 10)
        self.mcu_status_pub = self.create_publisher(McuStatus, "hardware/mcu_status", 10)
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
            self.get_logger().info(f"Safety MCU connessa su {self.serial_port} @ {self.serial_baud} bps")
        except serial.SerialException as exc:
            self._serial = None
            if not self.simulate_without_serial:
                self.get_logger().error(f"Impossibile connettere seriale safety MCU: {exc}")
            else:
                self.get_logger().warn(f"Safety MCU non disponibile ({exc}). Modalità simulata.")

    def _cb_estop(self, msg: Bool) -> None:
        self.estop_request = bool(msg.data)

    def _cb_ice(self, msg: Bool) -> None:
        self.ice_on = bool(msg.data)

    def _cb_ice_kill(self, msg: Bool) -> None:
        self.ice_kill = bool(msg.data)

    def _cb_dump_load(self, msg: Bool) -> None:
        self.dump_load_on = bool(msg.data)

    def _cb_rex_charge_current(self, msg: Float32) -> None:
        self.rex_charge_current_a = max(0.0, float(msg.data))

    def _cb_rex_throttle(self, msg: Float32) -> None:
        self.rex_throttle_request = max(0.0, min(1.0, float(msg.data)))

    def _cb_mission_cmd_vel(self, msg: Twist) -> None:
        self._set_motion_command(msg, "mission")

    def _cb_manual_cmd_vel(self, msg: Twist) -> None:
        self._set_motion_command(msg, "manual")

    def _set_motion_command(self, msg: Twist, mode: str) -> None:
        self.desired_linear_velocity_ms = float(msg.linear.x)
        self.desired_angular_velocity_rads = float(msg.angular.z)
        self.command_mode = mode
        self.enable_motors_request = not self.estop_request
        self._last_motion_cmd_s = time.monotonic()

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

    def _build_current_command_frame(self) -> dict:
        self._seq += 1
        command_stale = (time.monotonic() - self._last_motion_cmd_s) > (self.command_timeout_ms / 1000.0)
        desired_linear_velocity_ms = 0.0 if command_stale else self.desired_linear_velocity_ms
        desired_angular_velocity_rads = 0.0 if command_stale else self.desired_angular_velocity_rads
        enable_motors_request = self.enable_motors_request and not command_stale and not self.estop_request
        command = build_safety_command_frame(
            seq=self._seq,
            stamp_ms=int(time.monotonic() * 1000.0),
            mode=self.command_mode,
            desired_linear_velocity_ms=desired_linear_velocity_ms,
            desired_angular_velocity_rads=desired_angular_velocity_rads,
            timeout_ms=self.command_timeout_ms,
            estop_request=self.estop_request,
            enable_motors_request=enable_motors_request,
            max_current_a=self.max_current_a,
        )
        command.update(
            {
                "cmd": "heartbeat",
                "estop": self.estop_request,
                "ice_on": self.ice_on,
                "ice_kill": self.ice_kill,
                "dump_load": self.dump_load_on,
                "rex_charge_current_a": self.rex_charge_current_a,
                "rex_throttle_request": self.rex_throttle_request,
            }
        )
        add_auxiliary_command_crc(command)
        self._last_command_frame = command
        return command

    def _io_loop(self) -> None:
        command = self._build_current_command_frame()
        self._publish_safety_command(command)

        if self._serial is None:
            self.model.note_serial_disconnected()
            if self.simulate_without_serial:
                payload = {
                    "ack": command["seq"],
                    "mcu_uptime_ms": int((time.monotonic() - self._start_time_s) * 1000.0),
                    "safety_state": "estop" if self.estop_request else "safe_disabled",
                    "estop_hw": self.estop_request,
                    "motor_consent": False,
                    "fault_code": "none",
                    "fault_latched": False,
                    "heartbeat_age_ms": 0,
                    "sensor_validity": 0,
                    "degraded_mode": "simulated",
                    "encoder": self.model.cable_length_m,
                    "tension": self.model.winch_tension_n,
                    "battery_voltage_v": self.model.battery_voltage_v,
                    "motor_current_a": self.model.battery_current_a,
                    "crc16": 0,
                }
                self._last_mcu_payload = payload
                self.model.update_serial_payload(payload, time.monotonic())
            elif (time.monotonic() - self._last_connect_attempt_s) > 1.0:
                self._connect_serial()
            return

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
                valid, reason = validate_mcu_status_payload(
                    payload,
                    allow_unsigned=self.allow_unsigned_mcu_status,
                )
                if not valid:
                    self.model.note_serial_disconnected()
                    self._publish_fault(
                        "hardware_bridge",
                        "CRITICAL",
                        reason,
                        "MCU status rejected by bridge validation",
                        latched=True,
                    )
                    continue
                self._last_mcu_payload = payload
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
        self._publish_mcu_status(snapshot)

        self.winch_tension_pub.publish(Float32(data=float(snapshot.winch_tension_n)))
        self.cable_length_pub.publish(Float32(data=float(snapshot.cable_length_m)))
        self.battery_voltage_pub.publish(Float32(data=float(snapshot.battery_voltage_v)))
        self.battery_current_pub.publish(Float32(data=float(snapshot.battery_current_a)))
        self.power_demand_pub.publish(Float32(data=float(snapshot.battery_power_w)))
        self.thermal_headroom_pub.publish(Float32(data=float(snapshot.thermal_headroom)))

        self._sync_faults(snapshot.active_faults)

    def _publish_safety_command(self, command: dict) -> None:
        msg = SafetyCommand()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.seq = int(command.get("seq", 0))
        msg.stamp_ms = int(command.get("stamp_ms", 0))
        msg.mode = str(command.get("mode", "manual"))
        msg.desired_linear_velocity_ms = float(command.get("desired_linear_velocity_ms", 0.0))
        msg.desired_angular_velocity_rads = float(command.get("desired_angular_velocity_rads", 0.0))
        msg.timeout_ms = int(max(0, min(65535, command.get("timeout_ms", self.command_timeout_ms))))
        msg.estop_request = bool(command.get("estop_request", self.estop_request))
        msg.enable_motors_request = bool(command.get("enable_motors_request", False))
        msg.max_current_a = float(command.get("max_current_a", self.max_current_a))
        msg.crc16 = int(max(0, min(65535, command.get("crc16", 0))))
        self.safety_command_pub.publish(msg)

    def _publish_mcu_status(self, snapshot) -> None:
        payload = self._last_mcu_payload
        msg = McuStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.seq_ack = int(payload.get("seq_ack", payload.get("ack", 0)))
        msg.mcu_uptime_ms = int(max(0, min(0xFFFFFFFF, payload.get("mcu_uptime_ms", 0))))
        if snapshot.estop_hw:
            default_state = "estop"
        elif snapshot.bridge_connected:
            default_state = "armed" if payload.get("motor_consent", False) else "safe_disabled"
        else:
            default_state = "fault"
        msg.safety_state = str(payload.get("safety_state", default_state))
        msg.estop_active = bool(payload.get("estop_active", snapshot.estop_hw))
        msg.motor_consent = bool(payload.get("motor_consent", False))
        msg.fault_code = str(payload.get("fault_code", "none" if not snapshot.active_faults else snapshot.active_faults[0]))
        msg.fault_latched = bool(payload.get("fault_latched", snapshot.estop_hw))
        msg.heartbeat_age_ms = int(
            max(0, min(65535, payload.get("heartbeat_age_ms", 0 if snapshot.bridge_connected else self.command_timeout_ms)))
        )
        msg.sensor_validity = int(max(0, min(0xFFFFFFFF, payload.get("sensor_validity", 0))))
        msg.degraded_mode = str(payload.get("degraded_mode", snapshot.degraded_mode))
        msg.roll_rad = float(payload.get("roll_rad", 0.0))
        msg.pitch_rad = float(payload.get("pitch_rad", 0.0))
        msg.battery_voltage_v = float(payload.get("battery_voltage_v", snapshot.battery_voltage_v))
        msg.motor_current_a = float(payload.get("motor_current_a", snapshot.battery_current_a))
        msg.crc16 = int(max(0, min(65535, payload.get("crc16", 0))))
        self.mcu_status_pub.publish(msg)

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
