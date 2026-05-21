import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from rover_system.bridge_model import HardwareBridgeModel


def test_bridge_snapshot_tracks_serial_and_battery_freshness():
    model = HardwareBridgeModel(serial_stale_s=0.5, battery_stale_s=1.0, link_stale_s=1.0)
    model.update_serial_payload({"encoder": 1.0, "tension": 120.0, "estop_hw": False}, now_s=1.0)
    model.update_serial_payload({"encoder": 1.2, "tension": 130.0, "estop_hw": False}, now_s=1.2)
    model.update_battery_voltage(25.2, now_s=1.2)
    model.update_battery_current(8.0, now_s=1.2)
    model.update_primary_link(True, now_s=1.2)
    model.update_fallback_link(True, now_s=1.2)

    snapshot = model.snapshot(now_s=1.3)
    assert snapshot.bridge_connected is True
    assert snapshot.battery_valid is True
    assert snapshot.cable_velocity_ms > 0.0
    assert snapshot.battery_power_w == 25.2 * 8.0


def test_bridge_snapshot_reports_link_loss_and_stale_serial():
    model = HardwareBridgeModel(serial_stale_s=0.1, battery_stale_s=0.2, link_stale_s=0.2)
    model.update_primary_link(True, now_s=0.0)
    snapshot = model.snapshot(now_s=1.0)
    assert snapshot.bridge_connected is False
    assert "serial_stale" in snapshot.active_faults
    assert snapshot.degraded_mode == "link_loss_hold"
