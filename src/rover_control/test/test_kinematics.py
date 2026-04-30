import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from rover_control.kinematics import DifferentialKinematics4WD, ms_to_rpm, rpm_to_ms


def test_rpm_round_trip_is_close():
    speed = 0.72
    rpm = ms_to_rpm(speed)
    rebuilt = rpm_to_ms(rpm)
    assert abs(rebuilt - speed) < 1e-6


def test_skid_steer_turns_left_and_right_differently():
    model = DifferentialKinematics4WD()
    wheels = model.twist_to_wheel_speeds(0.8, 0.5, max_wheel_speed_ms=1.5)
    assert wheels.front_left < wheels.front_right
    assert wheels.rear_left < wheels.rear_right
