"""Integration tests for the full triage pipeline."""

from triage.core.admissibility import AdmissibilityGate
from triage.core.coherence import CoherenceMonitor
from triage.core.evaluator import DomainConfig, TriageEvaluator
from triage.core.scalar import ScalarConfig
from triage.core.sufficiency import SignalRequirement, SufficiencyRegistry


class TestTriageEvaluator:
    def _make_evaluator(self):
        config = DomainConfig(
            domain="test",
            sufficiency=SufficiencyRegistry(
                domain="test",
                required_signals=[
                    SignalRequirement("energy_integrity"),
                    SignalRequirement("control"),
                ],
            ),
            admissibility=AdmissibilityGate(),
            scalar=ScalarConfig(
                domain="test",
                weights={
                    "energy_integrity": 1.0,
                    "mechanical_output": 0.5,
                    "oxygen_delivery": 0.5,
                    "respiration": 0.5,
                    "coherence": 0.8,
                    "trend": 0.8,
                    "observability": 1.0,
                },
            ),
            coherence=CoherenceMonitor(),
        )
        return TriageEvaluator(config)

    def test_full_pipeline_green(self):
        ev = self._make_evaluator()
        result = ev.evaluate({
            "energy_integrity": 1.0,
            "control": 1.0,
            "mechanical_output": 1.0,
            "oxygen_delivery": 1.0,
            "respiration": 1.0,
            "observability": 1.0,
            "coherence": 1.0,
            "trend": 1.0,
        })
        assert result.admissible is True
        assert result.level == "GREEN"
        assert result.commit_hash is not None
        assert len(result.commit_hash) == 16

    def test_missing_required_inadmissible(self):
        ev = self._make_evaluator()
        result = ev.evaluate({
            "energy_integrity": 0.95,
            "mechanical_output": 0.90,
            "observability": 0.90,
        })
        assert result.admissible is False
        assert result.level in ("RED", "BLACK")
        assert any("control missing" in f for f in result.sufficiency_flags)
        assert "SUFFICIENCY_FAIL" in result.reason_codes

    def test_hard_trigger_inadmissible(self):
        ev = self._make_evaluator()
        result = ev.evaluate({
            "energy_integrity": 0.95,
            "control": {"value": 0},
            "mechanical_output": 0.90,
            "observability": 0.90,
        })
        assert result.admissible is False
        assert result.level in ("RED", "BLACK")
        assert "LOSS_OF_CONTROL" in result.reason_codes

    def test_commit_record_immutable(self):
        ev = self._make_evaluator()
        result = ev.evaluate({
            "energy_integrity": 0.95,
            "control": 0.95,
        })
        record = result.commit_record
        assert record.domain == "test"
        assert record.admissible is True
        assert record.commit_hash == result.commit_hash
