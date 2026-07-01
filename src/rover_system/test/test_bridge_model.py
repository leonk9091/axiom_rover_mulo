import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from rover_system.bridge_model import (
    HardwareBridgeModel,
    add_auxiliary_command_crc,
    auxiliary_command_crc_input,
    build_safety_command_frame,
    crc16_ccitt_false,
    mcu_status_crc_input,
    safety_command_crc_input,
    validate_mcu_status_payload,
)


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


def test_crc16_ccitt_false_known_vector():
    assert crc16_ccitt_false(b"123456789") == 0x29B1


def test_safety_command_frame_clamps_limits_and_adds_crc():
    frame = build_safety_command_frame(
        seq=7,
        stamp_ms=123,
        mode="trek_follow",
        desired_linear_velocity_ms=0.4,
        desired_angular_velocity_rads=-0.1,
        timeout_ms=900,
        estop_request=False,
        enable_motors_request=True,
        max_current_a=99.0,
    )

    assert frame["timeout_ms"] == 500
    assert frame["max_current_a"] == 30.0
    assert safety_command_crc_input(frame) == (
        b"seq=7;stamp_ms=123;mode=trek_follow;desired_linear_velocity_ms=0.400;"
        b"desired_angular_velocity_rads=-0.100;timeout_ms=500;estop_request=0;"
        b"enable_motors_request=1;max_current_a=30.000"
    )
    assert frame["crc16"] == crc16_ccitt_false(safety_command_crc_input(frame))


def test_auxiliary_command_crc_covers_rex_and_dump_load_fields():
    frame = {"seq": 8}
    frame.update(
        {
            "ice_on": True,
            "ice_kill": False,
            "dump_load": True,
            "rex_charge_current_a": 12.3456,
            "rex_throttle_request": 0.5,
        }
    )
    add_auxiliary_command_crc(frame)

    assert auxiliary_command_crc_input(frame) == (
        b"seq=8;ice_on=1;ice_kill=0;dump_load=1;"
        b"rex_charge_current_a=12.346;rex_throttle_request=0.500"
    )
    assert frame["aux_crc16"] == crc16_ccitt_false(auxiliary_command_crc_input(frame))


def test_mcu_status_payload_requires_valid_crc():
    payload = {
        "seq_ack": 7,
        "mcu_uptime_ms": 456,
        "safety_state": "armed",
        "estop_active": False,
        "motor_consent": True,
        "fault_code": "none",
        "fault_latched": False,
        "heartbeat_age_ms": 25,
        "sensor_validity": 31,
        "degraded_mode": "none",
        "roll_rad": 0.01,
        "pitch_rad": -0.02,
        "battery_voltage_v": 25.8,
        "motor_current_a": 4.2,
        "crc16": 0,
    }
    assert validate_mcu_status_payload(payload) == (False, "unsigned_status")

    payload["crc16"] = crc16_ccitt_false(mcu_status_crc_input(payload))
    assert validate_mcu_status_payload(payload) == (True, "ok")

    payload["crc16"] ^= 0x0001
    assert validate_mcu_status_payload(payload) == (False, "status_crc_error")
