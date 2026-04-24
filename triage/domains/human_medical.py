"""Human medical domain configuration.

Prioritizes oxygen delivery, respiration, and perfusion.
"""

from triage.core.sufficiency import SufficiencyRegistry, SignalRequirement
from triage.core.admissibility import AdmissibilityGate
from triage.core.scalar import ScalarConfig
from triage.core.coherence import CoherenceMonitor, CoherenceRule
from triage.core.evaluator import DomainConfig

HUMAN_MEDICAL_CONFIG = DomainConfig(
    domain="human_medical",
    sufficiency=SufficiencyRegistry(
        domain="human_medical",
        required_signals=[
            SignalRequirement("heart_rate", min_quality=0.7, min_duration_sec=10),
            SignalRequirement("blood_pressure", min_quality=0.7, min_duration_sec=10),
            SignalRequirement("oxygen_saturation", min_quality=0.8, min_duration_sec=15),
        ],
        optional_signals=[
            SignalRequirement("respiration_rate", min_quality=0.6),
            SignalRequirement("temperature"),
        ],
    ),
    admissibility=AdmissibilityGate(
        observability_threshold=0.25,
    ),
    scalar=ScalarConfig(
        domain="human_medical",
        weights={
            "energy_integrity": 0.8,
            "mechanical_output": 0.5,
            "oxygen_delivery": 1.2,
            "respiration": 1.2,
            "coherence": 1.0,
            "trend": 0.9,
            "observability": 1.1,
        },
        floor=0.05,
        trend_window_sec=300.0,  # 5 minutes for medical trend
    ),
    coherence=CoherenceMonitor(
        rules=[
            CoherenceRule("heart_rate", "pulse", "proximity", tolerance=5.0),
            CoherenceRule("oxygen_saturation", "respiration_rate", "same_direction"),
        ],
    ),
)
