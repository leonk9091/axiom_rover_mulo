"""Pure rover-drive kinematics utilities."""

from __future__ import annotations

import math
from dataclasses import dataclass

WHEEL_RADIUS_M = 0.254
TRACK_WIDTH_M = 0.6
GEAR_RATIO = 71.5
MOTOR_POLE_PAIRS = 7


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def rpm_to_ms(rpm_electrical: float) -> float:
    """Convert electrical RPM to wheel linear speed in m/s."""
    rpm_mech = rpm_electrical / (MOTOR_POLE_PAIRS * GEAR_RATIO)
    return rpm_mech * 2.0 * math.pi * WHEEL_RADIUS_M / 60.0


def ms_to_rpm(v_ms: float) -> float:
    """Convert wheel linear speed in m/s to electrical RPM."""
    rpm_mech = v_ms * 60.0 / (2.0 * math.pi * WHEEL_RADIUS_M)
    return rpm_mech * MOTOR_POLE_PAIRS * GEAR_RATIO


@dataclass(frozen=True)
class WheelSpeeds:
    front_left: float
    rear_left: float
    front_right: float
    rear_right: float

    @property
    def average(self) -> float:
        return (
            self.front_left
            + self.rear_left
            + self.front_right
            + self.rear_right
        ) / 4.0


class DifferentialKinematics4WD:
    """4WD skid-steer differential kinematics."""

    def __init__(self, track_width_m: float = TRACK_WIDTH_M):
        self.half_track = track_width_m / 2.0

    def twist_to_wheel_speeds(
        self,
        linear_velocity_ms: float,
        angular_velocity_rads: float,
        max_wheel_speed_ms: float,
    ) -> WheelSpeeds:
        left = linear_velocity_ms - angular_velocity_rads * self.half_track
        right = linear_velocity_ms + angular_velocity_rads * self.half_track
        scale = max(abs(left), abs(right)) / max(max_wheel_speed_ms, 1e-6)
        if scale > 1.0:
            left /= scale
            right /= scale
        return WheelSpeeds(
            front_left=left,
            rear_left=left,
            front_right=right,
            rear_right=right,
        )

    def estimate_slip_ratio(
        self,
        commanded_linear_ms: float,
        measured_linear_ms: float,
    ) -> float:
        denominator = max(abs(commanded_linear_ms), 0.1)
        return clamp(
            (commanded_linear_ms - measured_linear_ms) / denominator,
            -1.0,
            1.0,
        )
