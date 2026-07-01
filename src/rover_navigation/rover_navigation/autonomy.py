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
class WinchObservation:
    mode: str
    tension_measured_n: float
    cable_length_m: float
    cable_velocity_ms: float


@dataclass(frozen=True)
class SharedAutonomyCommand:
    linear_velocity_ms: float
    angular_velocity_rads: float
    control_mode: str


class SharedAutonomyCore:
    """Policy layer that blends leader tracking with terrain, safety, winch, and road constraints."""

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
        winch: WinchObservation | None = None,
        leash_enabled: bool = False,
        road_state: str = "nominal",
    ) -> SharedAutonomyCommand:
        if winch is None:
            winch = WinchObservation("passive", 0.0, 0.0, 0.0)

        # Controllo E-Stop o perdita link
        if not link.primary_link_up and not link.fallback_link_up:
            return SharedAutonomyCommand(0.0, 0.0, "link_loss_hold")

        # Gestione stato Attraversamento Strada (attesa conferma)
        if road_state == "waiting_for_crossing":
            return SharedAutonomyCommand(0.0, 0.0, "waiting_for_crossing")

        # Per la marcia normale (non attraversamento autonomo), è necessaria la visibilità del leader
        if road_state != "crossing" and (not observation.visible or observation.confidence < 0.2):
            return SharedAutonomyCommand(0.0, 0.0, "search_hold")

        # Calcolo velocità lineare di base
        if leash_enabled or winch.mode == "leash":
            # MODALITÀ GUINZAGLIO: velocità basata sulla tensione del cavo (Ammettenza)
            # F_start = 50 N, F_slack = 30 N. Guadagno K_a = 0.008 m/(s*N)
            if winch.tension_measured_n >= 50.0:
                linear_velocity_ms = 0.008 * (winch.tension_measured_n - 50.0)
            else:
                linear_velocity_ms = 0.0
            mode = "leash"
        else:
            # INSEGUIMENTO STANDARD
            distance_error = observation.range_m - target_distance_m
            if not allow_reverse and distance_error < 0.0:
                distance_error = 0.0
            linear_velocity_ms = self.kp_distance * distance_error
            mode = "shared_autonomy"

        # Calcolo velocità angolare (sterzo)
        if road_state == "crossing":
            # Attraversamento rapido: punta dritto all'operatore o avanti velocemente
            angular_velocity_rads = self.kp_bearing * observation.bearing_rad if observation.visible else 0.0
            linear_velocity_ms = max_linear_velocity_ms  # Forza velocità massima per attraversamento
            mode = "crossing"
        elif road_state == "pull_over":
            # Accostamento stradale: sterzo orientato a seguire la banchina (gestito allineamento)
            angular_velocity_rads = self.kp_bearing * observation.bearing_rad if observation.visible else 0.0
            linear_velocity_ms = min(linear_velocity_ms, 0.2)  # Velocità molto bassa e cauta
            mode = "pull_over"
        else:
            # Sterzo normale verso l'operatore
            angular_velocity_rads = self.kp_bearing * observation.bearing_rad

        # Limitazioni ambientali e di sicurezza
        terrain_limit = terrain.recommended_speed_ms if terrain.traversable else 0.15
        linear_limit = min(max_linear_velocity_ms, terrain_limit, stability.safe_linear_velocity_ms)

        if road_state == "pull_over":
            linear_limit = min(linear_limit, 0.2)

        if link.command_only_mode:
            linear_limit = min(linear_limit, 0.25)
            angular_velocity_rads *= 0.5

        if stability.degraded:
            angular_velocity_rads *= 0.75

        # Clamp finale delle velocità
        linear_velocity_ms = clamp(linear_velocity_ms, -linear_limit if allow_reverse else 0.0, linear_limit)
        angular_velocity_rads = clamp(
            angular_velocity_rads,
            -max_angular_velocity_rads,
            max_angular_velocity_rads,
        )

        # Selezione etichetta modalità se non ci sono stati stradali attivi
        if mode not in ("leash", "pull_over", "crossing"):
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
