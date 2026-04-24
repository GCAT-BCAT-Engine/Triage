# Commit-Time Triage Engine

A minimal admissibility-based triage framework for evaluating whether a human, robotic, or AI-enabled embodied system remains in a recoverable state at the moment an action, escalation, or continued operation decision is made.

> **No diagnosis without sufficient data. No action without admissibility.**

---

## Purpose

This repository provides a governed triage layer across:
- Human medical monitoring (hospital and field)
- Mobile robotics
- Embodied AI systems

It separates:
- **Sufficiency** — can we claim anything?
- **Admissibility** — can we safely continue?
- **Scalar reserve** — how close to failure?

---

## Core Architecture

```
sensor input → sufficiency registry → sufficiency check → admissibility gate → scalar computation → triage output
```

## Key Outputs

| Field | Type | Description |
|-------|------|-------------|
| `admissible` | bool | Whether operation may continue |
| `scalar` | float | Reserve metric (0.0–1.0) |
| `level` | enum | GREEN / YELLOW / ORANGE / RED / BLACK |
| `sufficiency_flags` | list | Which required signals were missing |
| `reason_codes` | list | Why a level was assigned |
| `commit_hash` | str | Immutable audit binding |

---

## Quick Start

```python
from triage.core.evaluator import TriageEvaluator
from triage.domains.robotics import ROBOTICS_CONFIG

evaluator = TriageEvaluator(ROBOTICS_CONFIG)
result = evaluator.evaluate({
    "energy_integrity": 0.85,
    "mechanical_output": 0.90,
    "oxygen_delivery": None,      # missing — sufficiency check catches this
    "respiration": 0.80,
    "coherence": 0.95,
    "trend": -0.02,
    "observability": 0.70
})

print(result)
# {
#   "admissible": False,
#   "scalar": 0.0,
#   "level": "RED",
#   "sufficiency_flags": ["oxygen_delivery missing"],
#   "reason_codes": ["SUFFICIENCY_FAIL"],
#   "commit_hash": "a3f7..."
# }
```

---

## Safety Rules

1. Do not diagnose without sufficient required data.
2. Do not treat missing data as normal.
3. Do not average hard safety failures into the scalar.
4. Do not allow optional signals to replace required signals.
5. Do not continue operation when denial or stop is not reachable.
6. Always emit reason codes.
7. Always separate sufficiency from admissibility.

---

## What This Is Not

- Not a medical diagnostic device.
- Not a replacement for emergency responders.
- Not a replacement for formal verification.
- Not a complete autonomous medical system.

## What This Is

- A sufficiency gate.
- An admissibility gate.
- A scalar reserve estimator.
- A coherence monitor.
- An uncertainty-aware triage layer.
- A commit-time governance primitive.

---

## Development Goal

The first working version proves:
- Missing data blocks diagnosis.
- Critical states fail closed.
- Scalar drops under degradation.
- Reason codes explain degradation.
- Human, robot, and AI use the same architecture.

---

## License

Apache 2.0 — see [LICENSE](LICENSE). This software is provided with an explicit safety notice: it is not a medical device and must not be used as a substitute for professional medical judgment or emergency response.

---

## Status

Prototype specification → initial implementation.
