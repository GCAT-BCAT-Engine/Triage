"""Tests for admissibility gate."""

import pytest

from triage.core.admissibility import AdmissibilityGate, HardTrigger


class TestAdmissibilityGate:
    def test_sufficiency_fail_triggers_inadmissible(self):
        gate = AdmissibilityGate()
        result = gate.check({}, sufficiency_ok=False, coherence_ok=True)
        assert result.admissible is False
        assert HardTrigger.SUFFICIENCY_FAIL in result.triggers

    def test_coherence_fail_triggers_inadmissible(self):
        gate = AdmissibilityGate()
        result = gate.check({}, sufficiency_ok=True, coherence_ok=False)
        assert result.admissible is False
        assert HardTrigger.INCOHERENT_SIGNALS in result.triggers

    def test_no_pulse(self):
        gate = AdmissibilityGate()
        result = gate.check(
            {"pulse": {"value": 0}},
            sufficiency_ok=True,
            coherence_ok=True,
        )
        assert result.admissible is False
        assert HardTrigger.NO_PULSE in result.triggers

    def test_low_observability(self):
        gate = AdmissibilityGate(observability_threshold=0.3)
        result = gate.check(
            {"observability": {"value": 0.1}},
            sufficiency_ok=True,
            coherence_ok=True,
        )
        assert result.admissible is False
        assert HardTrigger.LOW_OBSERVABILITY in result.triggers

    def test_all_clear(self):
        gate = AdmissibilityGate()
        result = gate.check(
            {"observability": {"value": 0.9}},
            sufficiency_ok=True,
            coherence_ok=True,
        )
        assert result.admissible is True
        assert result.triggers == []
