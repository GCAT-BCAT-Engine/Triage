"""Tests for sufficiency registry."""

import pytest

from triage.core.sufficiency import SufficiencyRegistry, SignalRequirement


class TestSufficiencyRegistry:
    def test_all_required_present(self):
        reg = SufficiencyRegistry(
            domain="test",
            required_signals=[
                SignalRequirement("a", min_quality=0.5),
                SignalRequirement("b", min_duration_sec=5),
            ],
        )
        result = reg.check({
            "a": {"value": 1.0, "quality": 0.8, "duration_sec": 10},
            "b": {"value": 1.0, "quality": 0.8, "duration_sec": 10},
        })
        assert result.sufficient is True
        assert result.flags == []

    def test_missing_required(self):
        reg = SufficiencyRegistry(
            domain="test",
            required_signals=[SignalRequirement("a")],
        )
        result = reg.check({"b": 1.0})
        assert result.sufficient is False
        assert "a missing" in result.flags

    def test_quality_failure(self):
        reg = SufficiencyRegistry(
            domain="test",
            required_signals=[SignalRequirement("a", min_quality=0.8)],
        )
        result = reg.check({"a": {"value": 1.0, "quality": 0.5, "duration_sec": 10}})
        assert result.sufficient is False
        assert any("quality" in f for f in result.flags)

    def test_duration_failure(self):
        reg = SufficiencyRegistry(
            domain="test",
            required_signals=[SignalRequirement("a", min_duration_sec=10)],
        )
        result = reg.check({"a": {"value": 1.0, "quality": 1.0, "duration_sec": 2}})
        assert result.sufficient is False
        assert any("duration" in f for f in result.flags)

    def test_bare_values_assumed_perfect(self):
        reg = SufficiencyRegistry(
            domain="test",
            required_signals=[SignalRequirement("a", min_quality=0.9)],
        )
        result = reg.check({"a": 0.5})  # bare value
        assert result.sufficient is True  # assumed perfect quality
