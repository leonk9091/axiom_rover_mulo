"""Pure shared-autonomy logic for Mulo X-1."""

from __future__ import annotations

from dataclasses import dataclass


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class LeaderObservation:
    visible: bool
    range_m: float
    bearing_rad: float
    confidence: float


@dataclass(frozen=True)
class TerrainDecision:
    traversable: bool
    recommended_speed_ms: float
    confidence: float
    slip_risk: float


@dataclass(frozen=True)
class StabilityDecision:
    margin: float
    safe_linear_velocity_ms: float
    degraded: bool


@dataclass(frozen=True)
class LinkDecision:
    primary_link_up: bool
    fallback_link_up: bool
    command_only_mode: bool
    degraded_mode: str


@dataclass(frozen=True)
class SharedAutonomyCommand:
    linear_velocity_ms: float
    angular_velocity_rads: float
    control_mode: str


class SharedAutonomyCore:
    """Policy layer that blends leader tracking with terrain and safety constraints."""

    def __init__(self, kp_distance: float = 0.8, kp_bearing: float = 1.5):
        self.kp_distance = kp_distance
        self.kp_bearing = kp_bearing

    def compute_command(
        self,
        observation: LeaderObservation,
        terrain: TerrainDecision,
        stability: StabilityDecision,
        link: LinkDecision,
        target_distance_m: float,
        max_linear_velocity_ms: float,
        max_angular_velocity_rads: float,
        allow_reverse: bool,
    ) -> SharedAutonomyCommand:
        if not observation.visible or observation.confidence < 0.2:
            return SharedAutonomyCommand(0.0, 0.0, "search_hold")

        if not link.primary_link_up and not link.fallback_link_up:
            return SharedAutonomyCommand(0.0, 0.0, "link_loss_hold")

        distance_error = observation.range_m - target_distance_m
        if not allow_reverse and distance_error < 0.0:
            distance_error = 0.0

        linear_velocity_ms = self.kp_distance * distance_error
        angular_velocity_rads = self.kp_bearing * observation.bearing_rad

        terrain_limit = terrain.recommended_speed_ms if terrain.traversable else 0.15
        linear_limit = min(max_linear_velocity_ms, terrain_limit, stability.safe_linear_velocity_ms)

        if link.command_only_mode:
            linear_limit = min(linear_limit, 0.25)
            angular_velocity_rads *= 0.5

        if stability.degraded:
            angular_velocity_rads *= 0.75

        linear_velocity_ms = clamp(linear_velocity_ms, -linear_limit if allow_reverse else 0.0, linear_limit)
        angular_velocity_rads = clamp(
            angular_velocity_rads,
            -max_angular_velocity_rads,
            max_angular_velocity_rads,
        )

        mode = "shared_autonomy"
        if stability.degraded:
            mode = "stability_limited"
        elif not terrain.traversable:
            mode = "terrain_caution"
        elif link.command_only_mode:
            mode = "command_only"

        return SharedAutonomyCommand(
            linear_velocity_ms=linear_velocity_ms,
            angular_velocity_rads=angular_velocity_rads,
            control_mode=mode,
        )
