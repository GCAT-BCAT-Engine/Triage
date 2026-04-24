"""Scalar reserve computation.

U = E × M × O × R × C × T × Q

with per-factor floors and domain-specific weighting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Per-factor floor to prevent total collapse from one bad sensor
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
    """Compute the scalar reserve metric.

    Args:
        inputs: Signal values. Each may be a bare float or a dict with 'value'.
        config: Domain-specific weights and floor.

    Returns:
        ScalarResult with scalar, raw scalar, per-factor breakdown, and
        observability-adjusted value.
    """
    factor_names = ["energy_integrity", "mechanical_output", "oxygen_delivery",
                    "respiration", "coherence", "trend", "observability"]

    factors: dict[str, float] = {}
    for name in factor_names:
        raw = inputs.get(name)
        if raw is None:
            # Missing optional factor — treat as floor, not zero
            factors[name] = config.floor
            continue

        if isinstance(raw, dict):
            val = raw.get("value", config.floor)
        elif isinstance(raw, (int, float)):
            val = float(raw)
        else:
            val = config.floor

        # Clamp to [floor, 1.0]
        factors[name] = max(config.floor, min(1.0, val))

    # Weighted product
    raw_scalar = 1.0
    for name in factor_names:
        weight = config.weights.get(name, 1.0)
        raw_scalar *= factors[name] ** weight

    # Observability adjustment: U* = U × Q (Q already in factors, but double-apply
    # if you want observability to have outsized influence)
    obs = factors.get("observability", 1.0)
    adjusted = raw_scalar * obs

    # Final clamp
    scalar = max(0.0, min(1.0, adjusted))

    return ScalarResult(
        scalar=scalar,
        raw_scalar=raw_scalar,
        factors=factors,
        observability_adjusted=adjusted,
    )


def scalar_to_level(scalar: float, admissible: bool) -> str:
    """Map scalar to triage level.

    GREEN  → strong reserve
    YELLOW → degraded
    ORANGE → restricted
    RED    → inadmissible
    BLACK  → nonrecoverable
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
