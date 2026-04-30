#!/usr/bin/env python3
"""Mission-aware hybrid power supervisor for Mulo X-1."""

from __future__ import annotations

import rclpy
from geometry_msgs.msg import Vector3
from rclpy.node import Node
from std_msgs.msg import Bool, Float32, String

from rover_interfaces.msg import EnergyBudget
from rover_power.energy import BatteryEKF, ECMSController, MissionEnergySupervisor

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

        self.ekf = BatteryEKF(dt_s=EKF_DT)
        self.ecms = ECMSController()
        self.supervisor = MissionEnergySupervisor()
        self.last_split = {"p_batt": 0.0, "p_ice": 0.0, "ice_on": False, "s": 0.0, "h_eq": 0.0}

        self.create_subscription(Float32, "battery/voltage", self._cb_voltage, 10)
        self.create_subscription(Float32, "battery/current", self._cb_current, 10)
        self.create_subscription(Float32, "system/power_demand_w", self._cb_power_demand, 10)
        self.create_subscription(Float32, "power/thermal_headroom", self._cb_thermal_headroom, 10)
        self.create_subscription(String, "mission/power_mode", self._cb_mission_mode, 10)

        self.ice_pub = self.create_publisher(Bool, "hardware/ice_generator_start", 10)
        self.dump_pub = self.create_publisher(Bool, "hardware/dump_load_enable", 10)
        self.soc_pub = self.create_publisher(Float32, "battery/soc_estimated", 10)
        self.soh_pub = self.create_publisher(Float32, "battery/soh_estimated", 10)
        self.split_pub = self.create_publisher(Vector3, "power/split_debug", 10)
        self.energy_budget_pub = self.create_publisher(EnergyBudget, "power/energy_budget", 10)

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

        self.ice_pub.publish(Bool(data=bool(self.last_split["ice_on"])))
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
        msg.generator_active = bool(self.last_split["ice_on"])
        msg.dump_load_active = bool(self.dump_load_on)
        self.energy_budget_pub.publish(msg)

        self.get_logger().info(
            f"POWER mode={self.mission_mode} demand={self.power_demand_w:.0f}W "
            f"batt={self.last_split['p_batt']:.0f}W ice={self.last_split['p_ice']:.0f}W "
            f"soc={self.ekf.soc*100:.1f}% reserve={budget.power_reserve_w:.0f}W "
            f"runtime={budget.estimated_runtime_s/60.0:.1f}min"
        )


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
