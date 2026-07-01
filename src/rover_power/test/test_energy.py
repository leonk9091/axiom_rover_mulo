import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from rover_power.energy import (
    BatteryEKF,
    ECMSController,
    MissionEnergySupervisor,
    REX_FAULT_BUS_OVERVOLTAGE,
    REX_FAULT_NO_CHARGE_CURRENT,
    REX_STATE_DISABLED,
    REX_STATE_FAULT,
    REX_STATE_SPOOL_UP,
    RangeExtenderSupervisor,
)


def test_ekf_soc_decreases_under_discharge():
    ekf = BatteryEKF(dt_s=1.0)
    start_soc = ekf.soc
    ekf.predict(10.0)
    ekf.update(24.0, 10.0)
    assert ekf.soc < start_soc


def test_ecms_returns_feasible_split():
    ecms = ECMSController()
    split = ecms.optimize(400.0, soc=0.7, soh=0.95)
    assert split["p_ice"] >= 0.0
    assert split["p_batt"] <= 400.0


def test_mission_budget_derates_runtime():
    supervisor = MissionEnergySupervisor()
    budget = supervisor.build_budget(
        mission_mode="winch_assist",
        split={"p_batt": 250.0, "p_ice": 150.0, "ice_on": True, "s": 2.0, "h_eq": 0.0},
        soc=0.8,
        soh=0.95,
        voltage_v=24.0,
        thermal_headroom=0.7,
    )
    assert budget.thermal_derate == 0.7
    assert budget.estimated_runtime_s > 0.0


def test_range_extender_is_fail_closed_when_disabled():
    rex = RangeExtenderSupervisor(enabled=False)
    status = rex.evaluate(
        requested_power_w=500.0,
        soc=0.5,
        bus_voltage_v=24.0,
        thermal_headroom=1.0,
    )
    assert status.state == REX_STATE_DISABLED
    assert status.engine_start_request is False
    assert status.generation_enable is False


def test_range_extender_requests_current_when_enabled():
    rex = RangeExtenderSupervisor(enabled=True, max_power_w=700.0, max_charge_current_a=24.0)
    status = rex.evaluate(
        requested_power_w=600.0,
        soc=0.5,
        bus_voltage_v=25.0,
        thermal_headroom=1.0,
    )
    assert status.state == REX_STATE_SPOOL_UP
    assert status.engine_start_request is True
    assert status.generation_enable is True
    assert 23.0 <= status.charge_current_target_a <= 24.0


def test_range_extender_faults_on_bus_overvoltage():
    rex = RangeExtenderSupervisor(enabled=True, bus_voltage_max_v=29.2)
    status = rex.evaluate(
        requested_power_w=500.0,
        soc=0.5,
        bus_voltage_v=30.0,
        thermal_headroom=1.0,
    )
    assert status.state == REX_STATE_FAULT
    assert status.fault_code == REX_FAULT_BUS_OVERVOLTAGE
    assert status.engine_kill_request is True


def test_range_extender_faults_on_no_charge_current():
    rex = RangeExtenderSupervisor(enabled=True)
    status = rex.evaluate(
        requested_power_w=500.0,
        soc=0.5,
        bus_voltage_v=25.0,
        thermal_headroom=1.0,
        rpm=5200.0,
        measured_charge_current_a=0.0,
        no_charge_current_fault=True,
    )
    assert status.state == REX_STATE_FAULT
    assert status.fault_code == REX_FAULT_NO_CHARGE_CURRENT
    assert status.engine_kill_request is True
