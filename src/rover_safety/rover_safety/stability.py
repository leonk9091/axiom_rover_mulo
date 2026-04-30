"""Pure stability and rollover-risk models."""

from __future__ import annotations

import math
from dataclasses import dataclass


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class StabilityEstimate:
    longitudinal_margin: float
    lateral_margin: float
    rollover_risk: float
    traction_margin: float
    margin: float
    safe_linear_velocity_ms: float
    safe_winch_tension_n: float
    degraded: bool


class StabilityEnvelopeModel:
    """Lightweight fused stability heuristic for trekking/off-road operation."""

    def __init__(
        self,
        wheelbase_m: float = 0.8,
        track_width_m: float = 0.6,
        cog_height_m: float = 0.2,
        max_linear_velocity_ms: float = 1.2,
        max_winch_tension_n: float = 500.0,
    ):
        self.wheelbase_m = wheelbase_m
        self.track_width_m = track_width_m
        self.cog_height_m = max(cog_height_m, 0.05)
        self.max_linear_velocity_ms = max_linear_velocity_ms
        self.max_winch_tension_n = max_winch_tension_n

    @property
    def pitch_limit_rad(self) -> float:
        return math.atan(self.wheelbase_m / (2.0 * self.cog_height_m))

    @property
    def roll_limit_rad(self) -> float:
        return math.atan(self.track_width_m / (2.0 * self.cog_height_m))

    def evaluate(
        self,
        pitch_rad: float,
        roll_rad: float,
        linear_velocity_ms: float,
        winch_tension_n: float,
        traction_factor: float,
    ) -> StabilityEstimate:
        speed_ratio = clamp(abs(linear_velocity_ms) / self.max_linear_velocity_ms, 0.0, 1.0)
        tension_ratio = clamp(winch_tension_n / self.max_winch_tension_n, 0.0, 1.2)
        traction_factor = clamp(traction_factor, 0.1, 1.0)

        pitch_ratio = abs(pitch_rad) / max(self.pitch_limit_rad, 1e-3)
        roll_ratio = abs(roll_rad) / max(self.roll_limit_rad, 1e-3)

        longitudinal_margin = 1.0 - pitch_ratio - 0.25 * speed_ratio - 0.35 * tension_ratio
        lateral_margin = 1.0 - roll_ratio - 0.35 * speed_ratio - 0.20 * (1.0 - traction_factor)
        traction_margin = traction_factor - 0.20 * speed_ratio - 0.10 * tension_ratio
        longitudinal_margin = clamp(longitudinal_margin, -1.0, 1.0)
        lateral_margin = clamp(lateral_margin, -1.0, 1.0)
        traction_margin = clamp(traction_margin, -1.0, 1.0)
        margin = min(longitudinal_margin, lateral_margin, traction_margin)
        margin = clamp(margin, -1.0, 1.0)

        rollover_risk = clamp(1.0 - max(margin, 0.0), 0.0, 1.0)
        safe_linear_velocity_ms = self.max_linear_velocity_ms * clamp(max(margin, 0.05), 0.05, 1.0)
        safe_linear_velocity_ms *= clamp(0.5 + 0.5 * traction_factor, 0.3, 1.0)
        safe_winch_tension_n = self.max_winch_tension_n * clamp(max(margin, 0.2), 0.2, 1.0)
        degraded = margin < 0.35

        return StabilityEstimate(
            longitudinal_margin=longitudinal_margin,
            lateral_margin=lateral_margin,
            rollover_risk=rollover_risk,
            traction_margin=traction_margin,
            margin=margin,
            safe_linear_velocity_ms=safe_linear_velocity_ms,
            safe_winch_tension_n=safe_winch_tension_n,
            degraded=degraded,
        )
