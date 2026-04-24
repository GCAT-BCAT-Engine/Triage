"""Triage evaluator — orchestrates the full pipeline.

sensor input → sufficiency registry → sufficiency check → admissibility gate → scalar computation → triage output
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from triage.core.sufficiency import SufficiencyRegistry, SufficiencyResult
from triage.core.admissibility import AdmissibilityGate, AdmissibilityResult
from triage.core.scalar import ScalarConfig, ScalarResult, compute_scalar, scalar_to_level
from triage.core.coherence import CoherenceMonitor, CoherenceResult
from triage.core.commit_binding import CommitRecord, bind_commit


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
        # 1. Sufficiency check
        sufficiency: SufficiencyResult = self.config.sufficiency.check(inputs)

        # 2. Coherence check
        coherence: CoherenceResult = self.config.coherence.check(inputs)

        # 3. Admissibility gate (fail-closed)
        admissibility: AdmissibilityResult = self.config.admissibility.check(
            inputs,
            sufficiency_ok=sufficiency.sufficient,
            coherence_ok=coherence.coherent,
        )

        # 4. Scalar computation (always run for telemetry, even if inadmissible)
        scalar_result: ScalarResult = compute_scalar(inputs, self.config.scalar)

        # 5. Level assignment
        level = scalar_to_level(scalar_result.scalar, admissibility.admissible)

        # 6. Commit binding
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
