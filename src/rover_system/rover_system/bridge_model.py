"""Pure hardware bridge aggregation logic."""

from __future__ import annotations

from dataclasses import dataclass


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def crc16_ccitt_false(data: bytes) -> int:
    """Compute CRC-16/CCITT-FALSE for MCU command/status frames."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def safety_command_crc_input(payload: dict) -> bytes:
    """Return the canonical byte string used for SafetyCommand CRC."""
    fields = [
        ("seq", str(int(payload["seq"]))),
        ("stamp_ms", str(int(payload["stamp_ms"]))),
        ("mode", str(payload["mode"])),
        ("desired_linear_velocity_ms", f"{float(payload['desired_linear_velocity_ms']):.3f}"),
        ("desired_angular_velocity_rads", f"{float(payload['desired_angular_velocity_rads']):.3f}"),
        ("timeout_ms", str(int(payload["timeout_ms"]))),
        ("estop_request", "1" if payload["estop_request"] else "0"),
        ("enable_motors_request", "1" if payload["enable_motors_request"] else "0"),
        ("max_current_a", f"{float(payload['max_current_a']):.3f}"),
    ]
    return ";".join(f"{key}={value}" for key, value in fields).encode("ascii")


def auxiliary_command_crc_input(payload: dict) -> bytes:
    """Return the canonical byte string for auxiliary REX/dump-load commands."""
    fields = [
        ("seq", str(int(payload["seq"]))),
        ("ice_on", "1" if payload.get("ice_on", False) else "0"),
        ("ice_kill", "1" if payload.get("ice_kill", False) else "0"),
        ("dump_load", "1" if payload.get("dump_load", False) else "0"),
        ("rex_charge_current_a", f"{float(payload.get('rex_charge_current_a', 0.0)):.3f}"),
        ("rex_throttle_request", f"{float(payload.get('rex_throttle_request', 0.0)):.3f}"),
    ]
    return ";".join(f"{key}={value}" for key, value in fields).encode("ascii")


def build_safety_command_frame(
    *,
    seq: int,
    stamp_ms: int,
    mode: str,
    desired_linear_velocity_ms: float,
    desired_angular_velocity_rads: float,
    timeout_ms: int,
    estop_request: bool,
    enable_motors_request: bool,
    max_current_a: float,
) -> dict:
    """Build a deterministic Jetson/ROS -> safety MCU command frame."""
    payload = {
        "seq": int(seq) & 0xFFFFFFFF,
        "stamp_ms": int(stamp_ms) & 0xFFFFFFFF,
        "mode": str(mode),
        "desired_linear_velocity_ms": float(desired_linear_velocity_ms),
        "desired_angular_velocity_rads": float(desired_angular_velocity_rads),
        "timeout_ms": int(clamp(timeout_ms, 50, 500)),
        "estop_request": bool(estop_request),
        "enable_motors_request": bool(enable_motors_request),
        "max_current_a": float(clamp(max_current_a, 0.0, 30.0)),
    }
    payload["crc16"] = crc16_ccitt_false(safety_command_crc_input(payload))
    return payload


def add_auxiliary_command_crc(payload: dict) -> dict:
    """Attach CRC for non-traction hardware commands in the heartbeat frame."""
    payload["aux_crc16"] = crc16_ccitt_false(auxiliary_command_crc_input(payload))
    return payload


def mcu_status_crc_input(payload: dict) -> bytes:
    """Return the canonical byte string used for MCU status CRC."""
    seq_ack = payload.get("seq_ack", payload.get("ack", 0))
    fields = [
        ("seq_ack", str(int(seq_ack))),
        ("mcu_uptime_ms", str(int(payload["mcu_uptime_ms"]))),
        ("safety_state", str(payload["safety_state"])),
        ("estop_active", "1" if payload["estop_active"] else "0"),
        ("motor_consent", "1" if payload["motor_consent"] else "0"),
        ("fault_code", str(payload["fault_code"])),
        ("fault_latched", "1" if payload["fault_latched"] else "0"),
        ("heartbeat_age_ms", str(int(payload["heartbeat_age_ms"]))),
        ("sensor_validity", str(int(payload["sensor_validity"]))),
        ("degraded_mode", str(payload["degraded_mode"])),
        ("roll_rad", f"{float(payload['roll_rad']):.3f}"),
        ("pitch_rad", f"{float(payload['pitch_rad']):.3f}"),
        ("battery_voltage_v", f"{float(payload['battery_voltage_v']):.3f}"),
        ("motor_current_a", f"{float(payload['motor_current_a']):.3f}"),
    ]
    return ";".join(f"{key}={value}" for key, value in fields).encode("ascii")


def validate_mcu_status_payload(payload: dict, *, allow_unsigned: bool = False) -> tuple[bool, str]:
    """Validate required fields and CRC for an MCU status payload."""
    required_fields = (
        "mcu_uptime_ms",
        "safety_state",
        "estop_active",
        "motor_consent",
        "fault_code",
        "fault_latched",
        "heartbeat_age_ms",
        "sensor_validity",
        "degraded_mode",
        "roll_rad",
        "pitch_rad",
        "battery_voltage_v",
        "motor_current_a",
        "crc16",
    )
    if "seq_ack" not in payload and "ack" not in payload:
        return False, "missing_seq_ack"
    missing = [field for field in required_fields if field not in payload]
    if missing:
        return False, f"missing_{missing[0]}"

    observed_crc = int(payload.get("crc16", 0))
    if observed_crc == 0:
        return (True, "unsigned_status_allowed") if allow_unsigned else (False, "unsigned_status")

    expected_crc = crc16_ccitt_false(mcu_status_crc_input(payload))
    if observed_crc != expected_crc:
        return False, "status_crc_error"
    return True, "ok"


@dataclass(frozen=True)
class HardwareSnapshot:
    bridge_connected: bool
    serial_connected: bool
    estop_hw: bool
    primary_link_up: bool
    fallback_link_up: bool
    load_cell_valid: bool
    cable_encoder_valid: bool
    battery_valid: bool
    cable_length_m: float
    cable_velocity_ms: float
    winch_tension_n: float
    battery_voltage_v: float
    battery_current_a: float
    battery_power_w: float
    thermal_headroom: float
    degraded_mode: str
    active_faults: list[str]


class HardwareBridgeModel:
    """Tracks freshness and derived values for hardware-facing topics."""

    def __init__(
        self,
        serial_stale_s: float = 0.5,
        battery_stale_s: float = 1.5,
        link_stale_s: float = 1.5,
        thermal_headroom_default: float = 1.0,
    ):
        self.serial_stale_s = serial_stale_s
        self.battery_stale_s = battery_stale_s
        self.link_stale_s = link_stale_s
        self.thermal_headroom_default = thermal_headroom_default

        self.serial_connected = False
        self.estop_hw = False
        self.last_serial_rx_s = -1e9

        self.cable_length_m = 0.0
        self.cable_velocity_ms = 0.0
        self.winch_tension_n = 0.0
        self._prev_cable_length_m = 0.0
        self._prev_cable_stamp_s = None

        self.battery_voltage_v = 24.0
        self.battery_current_a = 0.0
        self.thermal_headroom = thermal_headroom_default
        self._battery_voltage_seen_s = -1e9
        self._battery_current_seen_s = -1e9
        self._thermal_seen_s = -1e9

        self.primary_link_seen_s = -1e9
        self.fallback_link_seen_s = -1e9
        self.primary_link_up = False
        self.fallback_link_up = False

    def update_serial_payload(self, payload: dict, now_s: float) -> None:
        self.last_serial_rx_s = now_s
        self.serial_connected = True
        self.estop_hw = bool(payload.get("estop_hw", self.estop_hw))

        cable_length = float(payload.get("encoder", self.cable_length_m))
        if self._prev_cable_stamp_s is not None:
            dt = max(now_s - self._prev_cable_stamp_s, 1e-6)
            self.cable_velocity_ms = (cable_length - self._prev_cable_length_m) / dt
        self._prev_cable_stamp_s = now_s
        self._prev_cable_length_m = cable_length
        self.cable_length_m = cable_length
        self.winch_tension_n = max(0.0, float(payload.get("tension", self.winch_tension_n)))

    def note_serial_disconnected(self) -> None:
        self.serial_connected = False

    def update_battery_voltage(self, voltage_v: float, now_s: float) -> None:
        self.battery_voltage_v = float(voltage_v)
        self._battery_voltage_seen_s = now_s

    def update_battery_current(self, current_a: float, now_s: float) -> None:
        self.battery_current_a = float(current_a)
        self._battery_current_seen_s = now_s

    def update_thermal_headroom(self, headroom: float, now_s: float) -> None:
        self.thermal_headroom = clamp(float(headroom), 0.0, 1.0)
        self._thermal_seen_s = now_s

    def update_primary_link(self, up: bool, now_s: float) -> None:
        self.primary_link_up = bool(up)
        self.primary_link_seen_s = now_s

    def update_fallback_link(self, up: bool, now_s: float) -> None:
        self.fallback_link_up = bool(up)
        self.fallback_link_seen_s = now_s

    def snapshot(self, now_s: float) -> HardwareSnapshot:
        serial_fresh = (now_s - self.last_serial_rx_s) <= self.serial_stale_s
        load_cell_valid = serial_fresh
        cable_encoder_valid = serial_fresh
        battery_valid = (
            (now_s - self._battery_voltage_seen_s) <= self.battery_stale_s
            and (now_s - self._battery_current_seen_s) <= self.battery_stale_s
        )
        thermal_fresh = (now_s - self._thermal_seen_s) <= self.battery_stale_s
        primary_up = self.primary_link_up and (now_s - self.primary_link_seen_s) <= self.link_stale_s
        fallback_up = self.fallback_link_up and (now_s - self.fallback_link_seen_s) <= self.link_stale_s

        active_faults: list[str] = []
        if not serial_fresh:
            active_faults.append("serial_stale")
        if not battery_valid:
            active_faults.append("battery_stale")
        if not primary_up:
            active_faults.append("primary_link_down")
        if not fallback_up:
            active_faults.append("fallback_link_down")
        if self.estop_hw:
            active_faults.append("hardware_estop_active")

        if primary_up:
            degraded_mode = "nominal"
        elif fallback_up:
            degraded_mode = "command_only"
        else:
            degraded_mode = "link_loss_hold"

        power_w = max(self.battery_voltage_v * self.battery_current_a, 0.0)
        bridge_connected = self.serial_connected and serial_fresh
        thermal_headroom = self.thermal_headroom if thermal_fresh else self.thermal_headroom_default
        return HardwareSnapshot(
            bridge_connected=bridge_connected,
            serial_connected=self.serial_connected,
            estop_hw=self.estop_hw,
            primary_link_up=primary_up,
            fallback_link_up=fallback_up,
            load_cell_valid=load_cell_valid,
            cable_encoder_valid=cable_encoder_valid,
            battery_valid=battery_valid,
            cable_length_m=self.cable_length_m,
            cable_velocity_ms=self.cable_velocity_ms,
            winch_tension_n=self.winch_tension_n,
            battery_voltage_v=self.battery_voltage_v,
            battery_current_a=self.battery_current_a,
            battery_power_w=power_w,
            thermal_headroom=thermal_headroom,
            degraded_mode=degraded_mode,
            active_faults=active_faults,
        )
