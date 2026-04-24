"""Coherence detection.

Detects mismatches between signals that should agree.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CoherenceRule:
    """A rule defining expected coherence between two signals."""

    signal_a: str
    signal_b: str
    relation: str  # 'same_direction', 'proximity', 'mutex'
    tolerance: float = 0.2


@dataclass
class CoherenceMonitor:
    """Evaluates signal coherence."""

    rules: list[CoherenceRule] = field(default_factory=list)

    def check(self, inputs: dict[str, Any]) -> CoherenceResult:
        """Check all coherence rules."""
        violations = []

        for rule in self.rules:
            a_raw = inputs.get(rule.signal_a)
            b_raw = inputs.get(rule.signal_b)

            if a_raw is None or b_raw is None:
                continue  # Cannot check coherence if signals missing

            a_val = a_raw["value"] if isinstance(a_raw, dict) else a_raw
            b_val = b_raw["value"] if isinstance(b_raw, dict) else b_raw

            if rule.relation == "same_direction":
                if (a_val > 0.5 and b_val < 0.5) or (a_val < 0.5 and b_val > 0.5):
                    violations.append(
                        f"{rule.signal_a} ({a_val}) and {rule.signal_b} ({b_val}) diverge"
                    )
            elif rule.relation == "proximity":
                if abs(a_val - b_val) > rule.tolerance:
                    violations.append(
                        f"{rule.signal_a} ({a_val}) and {rule.signal_b} ({b_val}) "
                        f"differ by {abs(a_val - b_val)} > {rule.tolerance}"
                    )
            elif rule.relation == "mutex":
                if a_val > 0.5 and b_val > 0.5:
                    violations.append(
                        f"{rule.signal_a} and {rule.signal_b} both active (mutex violated)"
                    )

        return CoherenceResult(
            coherent=len(violations) == 0,
            violations=violations,
        )


@dataclass(frozen=True)
class CoherenceResult:
    """Outcome of coherence check."""

    coherent: bool
    violations: list[str]
