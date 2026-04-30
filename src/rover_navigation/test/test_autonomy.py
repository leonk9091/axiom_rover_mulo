import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from rover_navigation.autonomy import (
    LeaderObservation,
    LinkDecision,
    SharedAutonomyCore,
    StabilityDecision,
    TerrainDecision,
)


def test_shared_autonomy_stops_when_leader_missing():
    core = SharedAutonomyCore()
    command = core.compute_command(
        observation=LeaderObservation(False, 0.0, 0.0, 0.0),
        terrain=TerrainDecision(True, 0.7, 0.9, 0.1),
        stability=StabilityDecision(0.8, 0.7, False),
        link=LinkDecision(True, True, False, "nominal"),
        target_distance_m=1.5,
        max_linear_velocity_ms=1.0,
        max_angular_velocity_rads=0.8,
        allow_reverse=False,
    )
    assert command.linear_velocity_ms == 0.0
    assert command.angular_velocity_rads == 0.0


def test_shared_autonomy_respects_stability_limit():
    core = SharedAutonomyCore()
    command = core.compute_command(
        observation=LeaderObservation(True, 4.0, 0.2, 0.9),
        terrain=TerrainDecision(True, 1.0, 0.9, 0.0),
        stability=StabilityDecision(0.2, 0.25, True),
        link=LinkDecision(True, True, False, "nominal"),
        target_distance_m=1.5,
        max_linear_velocity_ms=1.0,
        max_angular_velocity_rads=0.8,
        allow_reverse=False,
    )
    assert 0.0 <= command.linear_velocity_ms <= 0.25
