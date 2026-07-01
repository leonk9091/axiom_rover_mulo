"""Pure energy-management models for rover_power."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

BATT_CAPACITY_AH = 30.0
BATT_NOMINAL_V = 24.0
BATT_R0_OHM = 0.05
BATT_R1_OHM = 0.02
BATT_C1_F = 1500.0
BATT_TEMP_NOM_K = 298.15
BATT_EA_OVER_R = 3000.0
OCV_POLY = np.array([1.2, -2.8, 4.1, 22.5])
ICE_FUEL_RATE_IDLE_GS = 0.8
ICE_POWER_MAX_W = 800.0
ICE_ETA_OPTIMAL = 0.28
ICE_POWER_OPTIMAL_W = 500.0
FUEL_LHV_J_G = 43000.0
ECMS_S0 = 2.5
ECMS_SOC_REF = 0.60
ECMS_SOC_BAND = 0.15
ECMS_LAMBDA_ADAPT = 0.05


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def ocv_from_soc(soc: float) -> float:
    return float(np.polyval(OCV_POLY, clamp(soc, 0.0, 1.0)))


class BatteryEKF:
    """Joint SoC/SoH estimator for a first-order battery model."""

    def __init__(self, dt_s: float = 1.0):
        self.x = np.array([0.80, 1.00, 0.0])
        self.P = np.diag([0.01, 0.001, 0.1])
        self.Q = np.diag([1e-5, 1e-7, 1e-4])
        self.R = np.array([[0.04]])
        self.dt = dt_s

    def _f(self, x: np.ndarray, u: float) -> np.ndarray:
        soc, soh, v_rc = x
        capacity_ah = BATT_CAPACITY_AH * soh
        capacity_as = max(capacity_ah * 3600.0, 1.0)
        soc_new = soc - (u * self.dt) / capacity_as
        aging_rate = 1e-9 * math.exp(-BATT_EA_OVER_R / BATT_TEMP_NOM_K)
        soh_new = soh - aging_rate * abs(u) * self.dt
        tau = BATT_R1_OHM * BATT_C1_F
        alpha = math.exp(-self.dt / tau)
        v_rc_new = v_rc * alpha + BATT_R1_OHM * u * (1.0 - alpha)
        return np.array([
            clamp(soc_new, 0.0, 1.0),
            clamp(soh_new, 0.5, 1.0),
            v_rc_new,
        ])

    def _h(self, x: np.ndarray, u: float) -> np.ndarray:
        soc, _, v_rc = x
        return np.array([ocv_from_soc(soc) - u * BATT_R0_OHM - v_rc])

    def _jacobian_f(self, x: np.ndarray, u: float) -> np.ndarray:
        _, soh, _ = x
        capacity_as = max(BATT_CAPACITY_AH * soh * 3600.0, 1.0)
        tau = BATT_R1_OHM * BATT_C1_F
        f = np.eye(3)
        f[0, 1] = (u * self.dt * BATT_CAPACITY_AH * 3600.0) / (capacity_as**2)
        f[2, 2] = math.exp(-self.dt / tau)
        return f

    def _jacobian_h(self, x: np.ndarray) -> np.ndarray:
        soc = x[0]
        d_ocv_d_soc = float(np.polyval(np.polyder(OCV_POLY), soc))
        return np.array([[d_ocv_d_soc, 0.0, -1.0]])

    def predict(self, current_a: float) -> None:
        f = self._jacobian_f(self.x, current_a)
        self.x = self._f(self.x, current_a)
        self.P = f @ self.P @ f.T + self.Q

    def update(self, terminal_voltage_v: float, current_a: float) -> None:
        h = self._jacobian_h(self.x)
        innovation = np.array([terminal_voltage_v]) - self._h(self.x, current_a)
        s = h @ self.P @ h.T + self.R
        k = self.P @ h.T @ np.linalg.inv(s)
        self.x = self.x + k @ innovation
        self.x[0] = clamp(float(self.x[0]), 0.0, 1.0)
        self.x[1] = clamp(float(self.x[1]), 0.5, 1.0)
        self.P = (np.eye(3) - k @ h) @ self.P

    @property
    def soc(self) -> float:
        return float(self.x[0])

    @property
    def soh(self) -> float:
        return float(self.x[1])


class ECMSController:
    """Equivalent Consumption Minimization Strategy."""

    def __init__(self):
        self.s = ECMS_S0

    def _adapt_s(self, soc: float) -> None:
        soc_error = ECMS_SOC_REF - soc
        self.s = clamp(
            ECMS_S0 * (1.0 + ECMS_LAMBDA_ADAPT * soc_error / ECMS_SOC_BAND),
            1.0,
            5.0,
        )

    def _ice_fuel_power(self, p_ice_w: float) -> float:
        p_ice_w = clamp(p_ice_w, 0.0, ICE_POWER_MAX_W)
        if p_ice_w < 10.0:
            return ICE_FUEL_RATE_IDLE_GS * FUEL_LHV_J_G
        eta = ICE_ETA_OPTIMAL * (
            1.0 - ((p_ice_w - ICE_POWER_OPTIMAL_W) / ICE_POWER_MAX_W) ** 2
        )
        eta = max(0.10, eta)
        return p_ice_w / eta

    def optimize(self, p_demand_w: float, soc: float, soh: float) -> dict[str, float | bool]:
        self._adapt_s(soc)
        best_h = math.inf
        best_split = {"p_batt": p_demand_w, "p_ice": 0.0, "ice_on": False}
        battery_power_limit = BATT_NOMINAL_V * BATT_CAPACITY_AH * max(soh, 0.5)

        for i in range(21):
            alpha = i / 20.0
            p_ice = alpha * p_demand_w
            p_batt = p_demand_w - p_ice
            if p_ice > ICE_POWER_MAX_W:
                continue
            if p_batt > battery_power_limit or p_batt < -ICE_POWER_MAX_W:
                continue

            soc_penalty = 0.0
            if soc < 0.20 and p_batt > 0.0:
                soc_penalty = 1e6
            if soc > 0.90 and p_batt < 0.0:
                soc_penalty = 1e6

            fuel_cost_ice = self._ice_fuel_power(p_ice)
            fuel_cost_batt = self.s * abs(p_batt) / (0.95 * FUEL_LHV_J_G)
            h_eq = fuel_cost_ice + fuel_cost_batt + soc_penalty
            if h_eq < best_h:
                best_h = h_eq
                best_split = {
                    "p_batt": p_batt,
                    "p_ice": p_ice,
                    "ice_on": p_ice > 20.0,
                    "s": self.s,
                    "h_eq": h_eq,
                }
        return best_split


@dataclass(frozen=True)
class EnergyBudgetSnapshot:
    mission_mode: str
    power_reserve_w: float
    mission_reserve_j: float
    estimated_runtime_s: float
    thermal_derate: float


class MissionEnergySupervisor:
    """Mission-aware energy policy on top of the ECMS split."""

    MODE_MULTIPLIERS = {
        "idle": 0.6,
        "trek_follow": 1.0,
        "climb_assist": 1.3,
        "descent_control": 0.8,
        "winch_assist": 1.4,
    }

    def build_budget(
        self,
        mission_mode: str,
        split: dict[str, float | bool],
        soc: float,
        soh: float,
        voltage_v: float,
        thermal_headroom: float,
    ) -> EnergyBudgetSnapshot:
        multiplier = self.MODE_MULTIPLIERS.get(mission_mode, 1.0)
        usable_energy_j = BATT_CAPACITY_AH * BATT_NOMINAL_V * 3600.0 * soc * soh
        thermal_derate = clamp(thermal_headroom, 0.1, 1.0)
        p_batt = float(split["p_batt"])
        p_ice = float(split["p_ice"])
        power_reserve_w = max(0.0, ICE_POWER_MAX_W * thermal_derate - max(p_batt + p_ice, 0.0))
        mission_reserve_j = usable_energy_j * thermal_derate / multiplier
        estimated_runtime_s = mission_reserve_j / max(abs(p_batt) + 10.0, 10.0)
        return EnergyBudgetSnapshot(
            mission_mode=mission_mode,
            power_reserve_w=power_reserve_w,
            mission_reserve_j=mission_reserve_j,
            estimated_runtime_s=estimated_runtime_s,
            thermal_derate=thermal_derate,
        )


REX_STATE_DISABLED = 0
REX_STATE_IDLE = 1
REX_STATE_SPOOL_UP = 2
REX_STATE_GENERATING = 3
REX_STATE_COOLDOWN = 4
REX_STATE_FAULT = 5

REX_FAULT_NONE = 0
REX_FAULT_DISABLED = 1
REX_FAULT_SOC_HIGH = 2
REX_FAULT_BUS_OVERVOLTAGE = 3
REX_FAULT_RPM_OVERSPEED = 4
REX_FAULT_DC_LINK_OVERVOLTAGE = 5
REX_FAULT_NO_CHARGE_CURRENT = 6
REX_FAULT_THERMAL_DERATE = 7

REX_STATE_LABELS = {
    REX_STATE_DISABLED: "DISABLED",
    REX_STATE_IDLE: "IDLE",
    REX_STATE_SPOOL_UP: "SPOOL_UP",
    REX_STATE_GENERATING: "GENERATING",
    REX_STATE_COOLDOWN: "COOLDOWN",
    REX_STATE_FAULT: "FAULT",
}

REX_FAULT_LABELS = {
    REX_FAULT_NONE: "NONE",
    REX_FAULT_DISABLED: "DISABLED",
    REX_FAULT_SOC_HIGH: "SOC_HIGH",
    REX_FAULT_BUS_OVERVOLTAGE: "BUS_OVERVOLTAGE",
    REX_FAULT_RPM_OVERSPEED: "RPM_OVERSPEED",
    REX_FAULT_DC_LINK_OVERVOLTAGE: "DC_LINK_OVERVOLTAGE",
    REX_FAULT_NO_CHARGE_CURRENT: "NO_CHARGE_CURRENT",
    REX_FAULT_THERMAL_DERATE: "THERMAL_DERATE",
}


@dataclass(frozen=True)
class RangeExtenderSnapshot:
    state: int
    fault_code: int
    state_label: str
    fault_label: str
    reason: str
    engine_start_request: bool
    engine_kill_request: bool
    generation_enable: bool
    dump_load_request: bool
    generator_power_target_w: float
    charge_current_target_a: float
    throttle_request: float


class RangeExtenderSupervisor:
    """Fail-closed supervisor for the Honda GX50 range extender."""

    def __init__(
        self,
        enabled: bool = False,
        max_power_w: float = 700.0,
        max_charge_current_a: float = 24.0,
        min_soc_start: float = 0.25,
        stop_soc: float = 0.90,
        bus_voltage_max_v: float = 29.2,
        dc_link_max_v: float = 70.0,
        rpm_max: float = 7500.0,
        thermal_min_headroom: float = 0.35,
        clutch_engage_rpm: float = 4400.0,
    ):
        self.enabled = enabled
        self.max_power_w = max_power_w
        self.max_charge_current_a = max_charge_current_a
        self.min_soc_start = min_soc_start
        self.stop_soc = stop_soc
        self.bus_voltage_max_v = bus_voltage_max_v
        self.dc_link_max_v = dc_link_max_v
        self.rpm_max = rpm_max
        self.thermal_min_headroom = thermal_min_headroom
        self.clutch_engage_rpm = clutch_engage_rpm

    def evaluate(
        self,
        requested_power_w: float,
        soc: float,
        bus_voltage_v: float,
        thermal_headroom: float,
        measured_charge_current_a: float = 0.0,
        rpm: float = 0.0,
        dc_link_voltage_v: float = 0.0,
        dump_load_request: bool = False,
        no_charge_current_fault: bool = False,
    ) -> RangeExtenderSnapshot:
        fault_code = REX_FAULT_NONE
        reason = "ready"
        state = REX_STATE_IDLE

        if not self.enabled:
            fault_code = REX_FAULT_DISABLED
            reason = "range extender disabled by profile"
        elif soc >= self.stop_soc:
            fault_code = REX_FAULT_SOC_HIGH
            reason = "battery soc above generator stop threshold"
        elif bus_voltage_v >= self.bus_voltage_max_v:
            fault_code = REX_FAULT_BUS_OVERVOLTAGE
            reason = "24v bus above generator limit"
        elif rpm > self.rpm_max:
            fault_code = REX_FAULT_RPM_OVERSPEED
            reason = "gx50/alternator rpm overspeed"
        elif dc_link_voltage_v > self.dc_link_max_v:
            fault_code = REX_FAULT_DC_LINK_OVERVOLTAGE
            reason = "rectified dc link above limit"
        elif no_charge_current_fault:
            fault_code = REX_FAULT_NO_CHARGE_CURRENT
            reason = "no charge current while gx50 clutch should be engaged"
        elif thermal_headroom < self.thermal_min_headroom:
            fault_code = REX_FAULT_THERMAL_DERATE
            reason = "thermal headroom below generator threshold"

        if fault_code != REX_FAULT_NONE:
            state = REX_STATE_DISABLED if fault_code == REX_FAULT_DISABLED else REX_STATE_FAULT
            return self._snapshot(
                state=state,
                fault_code=fault_code,
                reason=reason,
                engine_start_request=False,
                engine_kill_request=fault_code != REX_FAULT_DISABLED,
                generation_enable=False,
                dump_load_request=dump_load_request,
                generator_power_target_w=0.0,
                charge_current_target_a=0.0,
                throttle_request=0.0,
            )

        target_power = clamp(requested_power_w, 0.0, self.max_power_w)
        if target_power <= 20.0 and soc > self.min_soc_start:
            return self._snapshot(
                state=REX_STATE_IDLE,
                fault_code=REX_FAULT_NONE,
                reason="generator demand below start threshold",
                engine_start_request=False,
                engine_kill_request=False,
                generation_enable=False,
                dump_load_request=dump_load_request,
                generator_power_target_w=0.0,
                charge_current_target_a=0.0,
                throttle_request=0.0,
            )

        charge_current = clamp(
            target_power / max(bus_voltage_v, 1.0),
            0.0,
            self.max_charge_current_a,
        )
        state = REX_STATE_GENERATING if measured_charge_current_a > 0.5 else REX_STATE_SPOOL_UP
        throttle = clamp(target_power / max(self.max_power_w, 1.0), 0.15, 1.0)
        return self._snapshot(
            state=state,
            fault_code=REX_FAULT_NONE,
            reason="closed-loop current generation requested",
            engine_start_request=True,
            engine_kill_request=False,
            generation_enable=True,
            dump_load_request=dump_load_request,
            generator_power_target_w=target_power,
            charge_current_target_a=charge_current,
            throttle_request=throttle,
        )

    def _snapshot(
        self,
        state: int,
        fault_code: int,
        reason: str,
        engine_start_request: bool,
        engine_kill_request: bool,
        generation_enable: bool,
        dump_load_request: bool,
        generator_power_target_w: float,
        charge_current_target_a: float,
        throttle_request: float,
    ) -> RangeExtenderSnapshot:
        return RangeExtenderSnapshot(
            state=state,
            fault_code=fault_code,
            state_label=REX_STATE_LABELS[state],
            fault_label=REX_FAULT_LABELS[fault_code],
            reason=reason,
            engine_start_request=engine_start_request,
            engine_kill_request=engine_kill_request,
            generation_enable=generation_enable,
            dump_load_request=dump_load_request,
            generator_power_target_w=generator_power_target_w,
            charge_current_target_a=charge_current_target_a,
            throttle_request=throttle_request,
        )
