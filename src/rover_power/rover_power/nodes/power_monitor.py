#!/usr/bin/env python3
"""Mission-aware hybrid power supervisor for Mulo X-1."""

from __future__ import annotations

import time

import rclpy
from geometry_msgs.msg import Vector3
from rclpy.node import Node
from std_msgs.msg import Bool, Float32, String

from rover_interfaces.msg import EnergyBudget, RangeExtenderStatus
from rover_power.energy import (
    BatteryEKF,
    ECMSController,
    MissionEnergySupervisor,
    RangeExtenderSnapshot,
    RangeExtenderSupervisor,
)

DUMP_LOAD_SOC_THRESH = 0.95
DUMP_LOAD_V_THRESH = 28.5
EKF_DT = 1.0
POWER_DT = 0.5


class PowerMonitorNode(Node):
    def __init__(self):
        super().__init__("power_monitor")
        self.get_logger().info("Initializing Mission-Aware Power Supervisor...")

        self.batt_voltage = 24.0
        self.batt_current = 0.0
        self.power_demand_w = 0.0
        self.thermal_headroom = 1.0
        self.mission_mode = "trek_follow"
        self.dump_load_on = False
        self.rex_rpm = 0.0
        self.rex_dc_link_voltage_v = 0.0
        self.rex_charge_current_a = 0.0
        self._rex_no_charge_since_s: float | None = None

        self.declare_parameter("range_extender_enabled", False)
        self.declare_parameter("range_extender_max_power_w", 700.0)
        self.declare_parameter("range_extender_max_charge_current_a", 24.0)
        self.declare_parameter("range_extender_min_soc_start", 0.25)
        self.declare_parameter("range_extender_stop_soc", 0.90)
        self.declare_parameter("range_extender_bus_voltage_max_v", 29.2)
        self.declare_parameter("range_extender_dc_link_max_v", 70.0)
        self.declare_parameter("range_extender_rpm_max", 7500.0)
        self.declare_parameter("range_extender_clutch_engage_rpm", 4400.0)
        self.declare_parameter("range_extender_no_charge_timeout_s", 2.0)
        self.declare_parameter("range_extender_thermal_min_headroom", 0.35)
        self.rex_no_charge_timeout_s = float(
            self.get_parameter("range_extender_no_charge_timeout_s").value
        )
        self.rex_clutch_engage_rpm = float(
            self.get_parameter("range_extender_clutch_engage_rpm").value
        )

        self.ekf = BatteryEKF(dt_s=EKF_DT)
        self.ecms = ECMSController()
        self.supervisor = MissionEnergySupervisor()
        self.rex = RangeExtenderSupervisor(
            enabled=bool(self.get_parameter("range_extender_enabled").value),
            max_power_w=float(self.get_parameter("range_extender_max_power_w").value),
            max_charge_current_a=float(
                self.get_parameter("range_extender_max_charge_current_a").value
            ),
            min_soc_start=float(self.get_parameter("range_extender_min_soc_start").value),
            stop_soc=float(self.get_parameter("range_extender_stop_soc").value),
            bus_voltage_max_v=float(
                self.get_parameter("range_extender_bus_voltage_max_v").value
            ),
            dc_link_max_v=float(self.get_parameter("range_extender_dc_link_max_v").value),
            rpm_max=float(self.get_parameter("range_extender_rpm_max").value),
            clutch_engage_rpm=self.rex_clutch_engage_rpm,
            thermal_min_headroom=float(
                self.get_parameter("range_extender_thermal_min_headroom").value
            ),
        )
        self.last_split = {"p_batt": 0.0, "p_ice": 0.0, "ice_on": False, "s": 0.0, "h_eq": 0.0}

        self.create_subscription(Float32, "battery/voltage", self._cb_voltage, 10)
        self.create_subscription(Float32, "battery/current", self._cb_current, 10)
        self.create_subscription(Float32, "system/power_demand_w", self._cb_power_demand, 10)
        self.create_subscription(Float32, "power/thermal_headroom", self._cb_thermal_headroom, 10)
        self.create_subscription(String, "mission/power_mode", self._cb_mission_mode, 10)
        self.create_subscription(Float32, "range_extender/rpm", self._cb_rex_rpm, 10)
        self.create_subscription(
            Float32, "range_extender/dc_link_voltage", self._cb_rex_dc_link_voltage, 10
        )
        self.create_subscription(
            Float32, "range_extender/charge_current", self._cb_rex_charge_current, 10
        )

        self.ice_pub = self.create_publisher(Bool, "hardware/ice_generator_start", 10)
        self.ice_kill_pub = self.create_publisher(Bool, "hardware/ice_generator_kill", 10)
        self.rex_current_pub = self.create_publisher(
            Float32, "hardware/range_extender_charge_current_a", 10
        )
        self.rex_throttle_pub = self.create_publisher(
            Float32, "hardware/range_extender_throttle_request", 10
        )
        self.dump_pub = self.create_publisher(Bool, "hardware/dump_load_enable", 10)
        self.soc_pub = self.create_publisher(Float32, "battery/soc_estimated", 10)
        self.soh_pub = self.create_publisher(Float32, "battery/soh_estimated", 10)
        self.split_pub = self.create_publisher(Vector3, "power/split_debug", 10)
        self.energy_budget_pub = self.create_publisher(EnergyBudget, "power/energy_budget", 10)
        self.rex_status_pub = self.create_publisher(
            RangeExtenderStatus, "range_extender/status", 10
        )

        self.create_timer(EKF_DT, self._ekf_loop)
        self.create_timer(POWER_DT, self._power_loop)
        self.get_logger().info("Power Supervisor ready.")

    def _cb_voltage(self, msg: Float32) -> None:
        self.batt_voltage = msg.data

    def _cb_current(self, msg: Float32) -> None:
        self.batt_current = msg.data

    def _cb_power_demand(self, msg: Float32) -> None:
        self.power_demand_w = msg.data

    def _cb_thermal_headroom(self, msg: Float32) -> None:
        self.thermal_headroom = msg.data

    def _cb_mission_mode(self, msg: String) -> None:
        self.mission_mode = msg.data.strip() or "trek_follow"

    def _cb_rex_rpm(self, msg: Float32) -> None:
        self.rex_rpm = msg.data

    def _cb_rex_dc_link_voltage(self, msg: Float32) -> None:
        self.rex_dc_link_voltage_v = msg.data

    def _cb_rex_charge_current(self, msg: Float32) -> None:
        self.rex_charge_current_a = msg.data

    def _ekf_loop(self) -> None:
        self.ekf.predict(self.batt_current)
        self.ekf.update(self.batt_voltage, self.batt_current)
        self.soc_pub.publish(Float32(data=self.ekf.soc))
        self.soh_pub.publish(Float32(data=self.ekf.soh))

        should_dump = self.ekf.soc > DUMP_LOAD_SOC_THRESH or self.batt_voltage > DUMP_LOAD_V_THRESH
        if should_dump != self.dump_load_on:
            self.dump_load_on = should_dump
            self.dump_pub.publish(Bool(data=self.dump_load_on))
            level = self.get_logger().warn if should_dump else self.get_logger().info
            level(
                f"Dump load {'ATTIVATO' if should_dump else 'disattivato'} "
                f"(SoC={self.ekf.soc*100:.1f}%, V={self.batt_voltage:.2f}V)"
            )

    def _power_loop(self) -> None:
        self.last_split = self.ecms.optimize(self.power_demand_w, self.ekf.soc, self.ekf.soh)
        budget = self.supervisor.build_budget(
            mission_mode=self.mission_mode,
            split=self.last_split,
            soc=self.ekf.soc,
            soh=self.ekf.soh,
            voltage_v=self.batt_voltage,
            thermal_headroom=self.thermal_headroom,
        )

        no_charge_fault = self._detect_rex_no_charge_fault(float(self.last_split["p_ice"]))
        rex_status = self.rex.evaluate(
            requested_power_w=float(self.last_split["p_ice"]),
            soc=self.ekf.soc,
            bus_voltage_v=self.batt_voltage,
            thermal_headroom=self.thermal_headroom,
            measured_charge_current_a=self.rex_charge_current_a,
            rpm=self.rex_rpm,
            dc_link_voltage_v=self.rex_dc_link_voltage_v,
            dump_load_request=self.dump_load_on,
            no_charge_current_fault=no_charge_fault,
        )

        self.ice_pub.publish(Bool(data=rex_status.engine_start_request))
        self.ice_kill_pub.publish(Bool(data=rex_status.engine_kill_request))
        self.rex_current_pub.publish(Float32(data=float(rex_status.charge_current_target_a)))
        self.rex_throttle_pub.publish(Float32(data=float(rex_status.throttle_request)))
        self._publish_rex_status(rex_status)
        self.split_pub.publish(
            Vector3(
                x=float(self.last_split["p_batt"]),
                y=float(self.last_split["p_ice"]),
                z=float(self.last_split["s"]),
            )
        )

        msg = EnergyBudget()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.mission_mode = self.mission_mode
        msg.soc = float(self.ekf.soc)
        msg.soh = float(self.ekf.soh)
        msg.bus_voltage_v = float(self.batt_voltage)
        msg.battery_power_w = float(self.last_split["p_batt"])
        msg.generator_power_w = float(self.last_split["p_ice"])
        msg.power_reserve_w = float(budget.power_reserve_w)
        msg.mission_reserve_j = float(budget.mission_reserve_j)
        msg.estimated_runtime_s = float(budget.estimated_runtime_s)
        msg.thermal_derate = float(budget.thermal_derate)
        msg.generator_active = bool(rex_status.generation_enable)
        msg.dump_load_active = bool(self.dump_load_on)
        self.energy_budget_pub.publish(msg)

        self.get_logger().info(
            f"POWER mode={self.mission_mode} demand={self.power_demand_w:.0f}W "
            f"batt={self.last_split['p_batt']:.0f}W rex={rex_status.state_label} "
            f"ice={rex_status.generator_power_target_w:.0f}W "
            f"soc={self.ekf.soc*100:.1f}% reserve={budget.power_reserve_w:.0f}W "
            f"runtime={budget.estimated_runtime_s/60.0:.1f}min"
        )

    def _detect_rex_no_charge_fault(self, requested_power_w: float) -> bool:
        generating_requested = requested_power_w > 20.0
        clutch_should_be_engaged = self.rex_rpm >= self.rex_clutch_engage_rpm
        no_current = self.rex_charge_current_a <= 0.5
        fault_condition = generating_requested and clutch_should_be_engaged and no_current

        now_s = time.monotonic()
        if not fault_condition:
            self._rex_no_charge_since_s = None
            return False
        if self._rex_no_charge_since_s is None:
            self._rex_no_charge_since_s = now_s
            return False
        return (now_s - self._rex_no_charge_since_s) >= self.rex_no_charge_timeout_s

    def _publish_rex_status(self, status: RangeExtenderSnapshot) -> None:
        msg = RangeExtenderStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.state = int(status.state)
        msg.fault_code = int(status.fault_code)
        msg.state_label = status.state_label
        msg.fault_label = status.fault_label
        msg.reason = status.reason
        msg.engine_start_request = bool(status.engine_start_request)
        msg.engine_kill_request = bool(status.engine_kill_request)
        msg.generation_enable = bool(status.generation_enable)
        msg.dump_load_request = bool(status.dump_load_request)
        msg.generator_power_target_w = float(status.generator_power_target_w)
        msg.charge_current_target_a = float(status.charge_current_target_a)
        msg.throttle_request = float(status.throttle_request)
        msg.measured_generator_power_w = float(self.batt_voltage * self.rex_charge_current_a)
        msg.measured_charge_current_a = float(self.rex_charge_current_a)
        msg.rpm = float(self.rex_rpm)
        msg.dc_link_voltage_v = float(self.rex_dc_link_voltage_v)
        msg.thermal_headroom = float(self.thermal_headroom)
        self.rex_status_pub.publish(msg)


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


if __name__ == "__main__":
    main()
