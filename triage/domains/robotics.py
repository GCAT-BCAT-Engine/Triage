"""Robotics domain configuration.

Prioritizes energy integrity and mechanical output.
"""

from triage.core.sufficiency import SufficiencyRegistry, SignalRequirement
from triage.core.admissibility import AdmissibilityGate
from triage.core.scalar import ScalarConfig
from triage.core.coherence import CoherenceMonitor, CoherenceRule
from triage.core.evaluator import DomainConfig

ROBOTICS_CONFIG = DomainConfig(
    domain="robotics",
    sufficiency=SufficiencyRegistry(
        domain="robotics",
        required_signals=[
            SignalRequirement("energy_integrity", min_quality=0.8, min_duration_sec=5),
            SignalRequirement("mechanical_output", min_quality=0.7, min_duration_sec=5),
            SignalRequirement("control", min_quality=0.9, min_duration_sec=2),
        ],
        optional_signals=[
            SignalRequirement("observability", min_quality=0.6),
            SignalRequirement("coherence"),
        ],
    ),
    admissibility=AdmissibilityGate(
        observability_threshold=0.2,
    ),
    scalar=ScalarConfig(
        domain="robotics",
        weights={
            "energy_integrity": 1.2,
            "mechanical_output": 1.2,
            "oxygen_delivery": 0.3,
            "respiration": 0.3,
            "coherence": 0.9,
            "trend": 1.0,
            "observability": 1.0,
        },
        floor=0.05,
        trend_window_sec=30.0,  # 30 seconds for robotics
    ),
    coherence=CoherenceMonitor(
        rules=[
            CoherenceRule("energy_integrity", "mechanical_output", "same_direction"),
            CoherenceRule("control", "authority", "proximity", tolerance=0.1),
        ],
    ),
)
