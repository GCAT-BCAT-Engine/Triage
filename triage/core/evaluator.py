"""Triage evaluator — orchestrates the full pipeline.

sensor input -> sufficiency registry -> sufficiency check ->
admissibility gate -> scalar computation -> triage output
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from triage.core.admissibility import AdmissibilityGate, AdmissibilityResult
from triage.core.coherence import CoherenceMonitor, CoherenceResult
from triage.core.commit_binding import CommitRecord, bind_commit
from triage.core.scalar import ScalarConfig, ScalarResult, compute_scalar, scalar_to_level
from triage.core.sufficiency import SufficiencyRegistry, SufficiencyResult


@dataclass
class DomainConfig:
    """Complete configuration for a triage domain."""

    domain: str
    sufficiency: SufficiencyRegistry
    admissibility: AdmissibilityGate
    scalar: ScalarConfig
    coherence: CoherenceMonitor


@dataclass(frozen=True)
class TriageResult:
    """Final output of the triage pipeline."""

    admissible: bool
    scalar: float
    level: str
    sufficiency_flags: list[str]
    reason_codes: list[str]
    commit_hash: str
    commit_record: CommitRecord


class TriageEvaluator:
    """Orchestrates the full triage pipeline for a given domain."""

    def __init__(self, config: DomainConfig) -> None:
        self.config = config

    def evaluate(self, inputs: dict[str, Any]) -> TriageResult:
        """Run the full triage pipeline."""
        sufficiency: SufficiencyResult = self.config.sufficiency.check(inputs)
        coherence: CoherenceResult = self.config.coherence.check(inputs)
        admissibility: AdmissibilityResult = self.config.admissibility.check(
            inputs,
            sufficiency_ok=sufficiency.sufficient,
            coherence_ok=coherence.coherent,
        )
        scalar_result: ScalarResult = compute_scalar(inputs, self.config.scalar)
        level = scalar_to_level(scalar_result.scalar, admissibility.admissible)

        record = bind_commit(
            domain=self.config.domain,
            admissible=admissibility.admissible,
            scalar=scalar_result.scalar,
            level=level,
            sufficiency_flags=sufficiency.flags,
            reason_codes=admissibility.reason_codes + coherence.violations,
            inputs=inputs,
        )

        return TriageResult(
            admissible=admissibility.admissible,
            scalar=scalar_result.scalar,
            level=level,
            sufficiency_flags=sufficiency.flags,
            reason_codes=admissibility.reason_codes + coherence.violations,
            commit_hash=record.commit_hash,
            commit_record=record,
        )
