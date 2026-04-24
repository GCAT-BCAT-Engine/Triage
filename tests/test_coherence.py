"""Tests for coherence monitor."""

from triage.core.coherence import CoherenceMonitor, CoherenceRule


class TestCoherenceMonitor:
    def test_proximity_pass(self):
        mon = CoherenceMonitor(rules=[CoherenceRule("a", "b", "proximity", tolerance=0.2)])
        result = mon.check({"a": 0.5, "b": 0.6})
        assert result.coherent is True
        assert result.violations == []

    def test_proximity_fail(self):
        mon = CoherenceMonitor(rules=[CoherenceRule("a", "b", "proximity", tolerance=0.2)])
        result = mon.check({"a": 0.5, "b": 0.9})
        assert result.coherent is False
        assert any("differ" in v for v in result.violations)

    def test_same_direction_pass(self):
        mon = CoherenceMonitor(rules=[CoherenceRule("a", "b", "same_direction")])
        result = mon.check({"a": 0.8, "b": 0.7})
        assert result.coherent is True

    def test_same_direction_fail(self):
        mon = CoherenceMonitor(rules=[CoherenceRule("a", "b", "same_direction")])
        result = mon.check({"a": 0.8, "b": 0.2})
        assert result.coherent is False

    def test_mutex_pass(self):
        mon = CoherenceMonitor(rules=[CoherenceRule("a", "b", "mutex")])
        result = mon.check({"a": 0.8, "b": 0.2})
        assert result.coherent is True

    def test_mutex_fail(self):
        mon = CoherenceMonitor(rules=[CoherenceRule("a", "b", "mutex")])
        result = mon.check({"a": 0.8, "b": 0.9})
        assert result.coherent is False

    def test_missing_signal_skipped(self):
        mon = CoherenceMonitor(rules=[CoherenceRule("a", "b", "proximity")])
        result = mon.check({"a": 0.5})
        assert result.coherent is True
