"""Scalar reserve computation.

U = E x M x O x R x C x T x Q

with per-factor floors and domain-specific weighting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_FLOOR = 0.05


@dataclass
class ScalarConfig:
    """Domain-specific scalar configuration."""

    domain: str
    weights: dict[str, float]
    floor: float = DEFAULT_FLOOR
    trend_window_sec: float = 30.0


@dataclass(frozen=True)
class ScalarResult:
    """Outcome of scalar computation."""

    scalar: float
    raw_scalar: float
    factors: dict[str, float]
    observability_adjusted: float


def compute_scalar(
    inputs: dict[str, Any],
    config: ScalarConfig,
) -> ScalarResult:
    """Compute the scalar reserve metric."""
    factor_names = [
        "energy_integrity",
        "mechanical_output",
        "oxygen_delivery",
        "respiration",
        "coherence",
        "trend",
        "observability",
    ]

    factors: dict[str, float] = {}
    for name in factor_names:
        raw = inputs.get(name)
        if raw is None:
            factors[name] = config.floor
            continue

        if isinstance(raw, dict):
            val = raw.get("value", config.floor)
        elif isinstance(raw, (int, float)):
            val = float(raw)
        else:
            val = config.floor

        factors[name] = max(config.floor, min(1.0, val))

    raw_scalar = 1.0
    for name in factor_names:
        weight = config.weights.get(name, 1.0)
        raw_scalar *= factors[name] ** weight

    obs = factors.get("observability", 1.0)
    adjusted = raw_scalar * obs
    scalar = max(0.0, min(1.0, adjusted))

    return ScalarResult(
        scalar=scalar,
        raw_scalar=raw_scalar,
        factors=factors,
        observability_adjusted=adjusted,
    )


def scalar_to_level(scalar: float, admissible: bool) -> str:
    """Map scalar to triage level.

    GREEN  -> strong reserve
    YELLOW -> degraded
    ORANGE -> restricted
    RED    -> inadmissible
    BLACK  -> nonrecoverable
    """
    if not admissible:
        if scalar <= 0.05:
            return "BLACK"
        return "RED"

    if scalar >= 0.8:
        return "GREEN"
    if scalar >= 0.5:
        return "YELLOW"
    return "ORANGE"
