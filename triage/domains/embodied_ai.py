"""Embodied AI domain configuration.

Prioritizes coherence, observability, and authority.
"""

from triage.core.admissibility import AdmissibilityGate
from triage.core.coherence import CoherenceMonitor, CoherenceRule
from triage.core.evaluator import DomainConfig
from triage.core.scalar import ScalarConfig
from triage.core.sufficiency import SignalRequirement, SufficiencyRegistry

EMBODIED_AI_CONFIG = DomainConfig(
    domain="embodied_ai",
    sufficiency=SufficiencyRegistry(
        domain="embodied_ai",
        required_signals=[
            SignalRequirement("coherence", min_quality=0.8, min_duration_sec=10),
            SignalRequirement("observability", min_quality=0.7, min_duration_sec=10),
            SignalRequirement("authority", min_quality=0.9, min_duration_sec=5),
        ],
        optional_signals=[
            SignalRequirement("energy_integrity"),
            SignalRequirement("trend"),
        ],
    ),
    admissibility=AdmissibilityGate(
        observability_threshold=0.3,
    ),
    scalar=ScalarConfig(
        domain="embodied_ai",
        weights={
            "energy_integrity": 0.6,
            "mechanical_output": 0.4,
            "oxygen_delivery": 0.3,
            "respiration": 0.3,
            "coherence": 1.3,
            "trend": 1.0,
            "observability": 1.2,
        },
        floor=0.05,
        trend_window_sec=60.0,
    ),
    coherence=CoherenceMonitor(
        rules=[
            CoherenceRule("coherence", "observability", "same_direction"),
            CoherenceRule("authority", "control", "proximity", tolerance=0.15),
        ],
    ),
)
