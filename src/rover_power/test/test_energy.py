import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from rover_power.energy import BatteryEKF, ECMSController, MissionEnergySupervisor


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
