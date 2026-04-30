import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from rover_safety.stability import StabilityEnvelopeModel


def test_stability_margin_drops_with_roll_and_tension():
    model = StabilityEnvelopeModel()
    nominal = model.evaluate(0.0, 0.0, 0.1, 0.0, 1.0)
    stressed = model.evaluate(0.25, 0.22, 0.9, 350.0, 0.6)
    assert stressed.margin < nominal.margin
    assert stressed.rollover_risk > nominal.rollover_risk


def test_safe_winch_tension_is_positive():
    model = StabilityEnvelopeModel()
    estimate = model.evaluate(0.1, 0.05, 0.4, 100.0, 0.9)
    assert estimate.safe_winch_tension_n > 0.0
