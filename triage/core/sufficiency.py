"""Sufficiency registry and validation.

A diagnosis is only permitted when all required signals are present,
meet minimum quality thresholds, and have been observed for the
minimum required duration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SignalRequirement:
    """Specification for a single required signal."""

    signal_id: str
    min_quality: float = 0.0
    min_duration_sec: float = 0.0


@dataclass
class SufficiencyRegistry:
    """Holds the sufficiency rules for a given domain."""

    domain: str
    required_signals: list[SignalRequirement] = field(default_factory=list)
    optional_signals: list[SignalRequirement] = field(default_factory=list)

    def check(self, inputs: dict[str, Any]) -> SufficiencyResult:
        """Evaluate whether the provided inputs satisfy sufficiency."""
        missing = []
        quality_failures = []
        duration_failures = []

        for req in self.required_signals:
            raw = inputs.get(req.signal_id)
            if raw is None:
                missing.append(req.signal_id)
                continue

            if isinstance(raw, dict):
                quality = raw.get("quality", 1.0)
                duration = raw.get("duration_sec", float("inf"))
            else:
                quality = 1.0
                duration = float("inf")

            if quality < req.min_quality:
                quality_failures.append(f"{req.signal_id} quality {quality} < {req.min_quality}")
            if duration < req.min_duration_sec:
                duration_failures.append(
                    f"{req.signal_id} duration {duration}s < {req.min_duration_sec}s"
                )

        sufficient = not (missing or quality_failures or duration_failures)

        return SufficiencyResult(
            sufficient=sufficient,
            missing=missing,
            quality_failures=quality_failures,
            duration_failures=duration_failures,
        )


@dataclass(frozen=True)
class SufficiencyResult:
    """Outcome of a sufficiency check."""

    sufficient: bool
    missing: list[str]
    quality_failures: list[str]
    duration_failures: list[str]

    @property
    def flags(self) -> list[str]:
        """Human-readable flags for reporting."""
        out = [f"{m} missing" for m in self.missing]
        out.extend(self.quality_failures)
        out.extend(self.duration_failures)
        return out
