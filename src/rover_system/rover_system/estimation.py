"""Pure rover state estimation logic."""

from __future__ import annotations

import math
from dataclasses import dataclass

from rover_control.kinematics import DifferentialKinematics4WD, rpm_to_ms

MOTOR_SIGN = {
    1: +1.0,
    2: +1.0,
    3: -1.0,
    4: -1.0,
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def quaternion_to_pitch_roll(x: float, y: float, z: float, w: float) -> tuple[float, float]:
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2.0, sinp)
    else:
        pitch = math.asin(sinp)
    return pitch, roll


@dataclass(frozen=True)
class EstimatedState:
    linear_velocity_ms: float
    angular_velocity_rads: float
    average_wheel_speed_ms: float
    slip_ratio: float
    pitch_rad: float
    roll_rad: float
    battery_soc: float
    stability_margin: float
    localization_ok: bool
    drive_ready: bool
    estop_active: bool
    mode: str


class RoverStateEstimator:
    """Fuses low-level signals into a single rover state snapshot."""

    def __init__(self, smoothing_alpha: float = 0.2):
        self.smoothing_alpha = clamp(smoothing_alpha, 0.01, 1.0)
        self.kinematics = DifferentialKinematics4WD()

        self.commanded_linear_ms = 0.0
        self.commanded_angular_rads = 0.0
        self.pitch_rad = 0.0
        self.roll_rad = 0.0
        self.linear_velocity_ms = 0.0
        self.angular_velocity_rads = 0.0
        self.average_wheel_speed_ms = 0.0
        self.battery_soc = 0.0
        self.stability_margin = 1.0
        self.localization_ok = False
        self.drive_ready = False
        self.estop_active = False
        self.mode = "manual"

    def update_command(self, linear_velocity_ms: float, angular_velocity_rads: float, mode: str) -> None:
        self.commanded_linear_ms = float(linear_velocity_ms)
        self.commanded_angular_rads = float(angular_velocity_rads)
        self.mode = mode

    def update_imu_orientation(self, x: float, y: float, z: float, w: float) -> None:
        pitch, roll = quaternion_to_pitch_roll(x, y, z, w)
        self.pitch_rad = self._smooth(self.pitch_rad, pitch)
        self.roll_rad = self._smooth(self.roll_rad, roll)

    def update_odometry(self, linear_velocity_ms: float, angular_velocity_rads: float) -> None:
        self.linear_velocity_ms = self._smooth(self.linear_velocity_ms, linear_velocity_ms)
        self.angular_velocity_rads = self._smooth(self.angular_velocity_rads, angular_velocity_rads)
        self.localization_ok = True

    def update_motor_telemetry(self, motor_ids: list[int], rpm_values: list[float]) -> None:
        if not motor_ids or not rpm_values:
            return
        wheel_speeds = []
        for index, motor_id in enumerate(motor_ids):
            if index >= len(rpm_values):
                break
            sign = MOTOR_SIGN.get(int(motor_id), 1.0)
            wheel_speeds.append(rpm_to_ms(float(rpm_values[index])) * sign)
        if not wheel_speeds:
            return
        average = sum(wheel_speeds) / len(wheel_speeds)
        self.average_wheel_speed_ms = self._smooth(self.average_wheel_speed_ms, average)
        if not self.localization_ok:
            self.linear_velocity_ms = self.average_wheel_speed_ms

    def update_energy(self, battery_soc: float) -> None:
        self.battery_soc = clamp(float(battery_soc), 0.0, 1.0)

    def update_stability(self, stability_margin: float) -> None:
        self.stability_margin = clamp(float(stability_margin), -1.0, 1.0)

    def update_safety(self, estop_active: bool, drive_ready: bool) -> None:
        self.estop_active = bool(estop_active)
        self.drive_ready = bool(drive_ready)

    def estimate(self) -> EstimatedState:
        slip_ratio = self.kinematics.estimate_slip_ratio(
            self.commanded_linear_ms,
            self.linear_velocity_ms if self.localization_ok else self.average_wheel_speed_ms,
        )
        drive_ready = self.drive_ready and self.stability_margin > 0.0 and not self.estop_active
        return EstimatedState(
            linear_velocity_ms=float(self.linear_velocity_ms if self.localization_ok else self.average_wheel_speed_ms),
            angular_velocity_rads=float(self.angular_velocity_rads),
            average_wheel_speed_ms=float(self.average_wheel_speed_ms),
            slip_ratio=float(slip_ratio),
            pitch_rad=float(self.pitch_rad),
            roll_rad=float(self.roll_rad),
            battery_soc=float(self.battery_soc),
            stability_margin=float(self.stability_margin),
            localization_ok=bool(self.localization_ok),
            drive_ready=bool(drive_ready),
            estop_active=bool(self.estop_active),
            mode=self.mode,
        )

    def _smooth(self, current: float, target: float) -> float:
        return current + self.smoothing_alpha * (target - current)
