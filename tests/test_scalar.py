"""Tests for scalar computation."""

from triage.core.scalar import ScalarConfig, compute_scalar, scalar_to_level


class TestScalarComputation:
    def test_perfect_inputs(self):
        config = ScalarConfig(
            domain="test",
            weights={k: 1.0 for k in [
                "energy_integrity", "mechanical_output", "oxygen_delivery",
                "respiration", "coherence", "trend", "observability"
            ]},
        )
        inputs = {k: 1.0 for k in config.weights}
        result = compute_scalar(inputs, config)
        assert result.scalar == 1.0

    def test_floor_prevents_zero_collapse(self):
        config = ScalarConfig(
            domain="test",
            weights={k: 1.0 for k in [
                "energy_integrity", "mechanical_output", "oxygen_delivery",
                "respiration", "coherence", "trend", "observability"
            ]},
            floor=0.1,
        )
        inputs = {k: 0.0 for k in config.weights}
        result = compute_scalar(inputs, config)
        assert result.scalar > 0.0

    def test_missing_optional_uses_floor(self):
        config = ScalarConfig(
            domain="test",
            weights={"energy_integrity": 1.0, "observability": 1.0},
            floor=0.2,
        )
        inputs = {"energy_integrity": 0.8}
        result = compute_scalar(inputs, config)
        assert result.factors["observability"] == 0.2

    def test_scalar_to_level_green(self):
        assert scalar_to_level(0.85, True) == "GREEN"

    def test_scalar_to_level_yellow(self):
        assert scalar_to_level(0.65, True) == "YELLOW"

    def test_scalar_to_level_orange(self):
        assert scalar_to_level(0.3, True) == "ORANGE"

    def test_scalar_to_level_red(self):
        assert scalar_to_level(0.3, False) == "RED"

    def test_scalar_to_level_black(self):
        assert scalar_to_level(0.02, False) == "BLACK"
