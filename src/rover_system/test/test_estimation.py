import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from rover_system.estimation import RoverStateEstimator, quaternion_to_pitch_roll


def test_quaternion_to_pitch_roll_round_trip_for_small_roll():
    pitch, roll = quaternion_to_pitch_roll(0.049979, 0.0, 0.0, 0.99875)
    assert abs(pitch) < 1e-3
    assert roll > 0.09


def test_state_estimator_builds_drive_ready_snapshot():
    estimator = RoverStateEstimator(smoothing_alpha=1.0)
    estimator.update_command(1.0, 0.2, "mission")
    estimator.update_odometry(0.9, 0.2)
    estimator.update_motor_telemetry([1, 2, 3, 4], [500.0, 500.0, -500.0, -500.0])
    estimator.update_energy(0.72)
    estimator.update_stability(0.65)
    estimator.update_safety(False, True)

    estimate = estimator.estimate()
    assert estimate.mode == "mission"
    assert math.isclose(estimate.linear_velocity_ms, 0.9, rel_tol=1e-6)
    assert estimate.drive_ready is True
    assert -1.0 <= estimate.slip_ratio <= 1.0
