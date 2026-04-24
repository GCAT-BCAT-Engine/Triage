# Commit-Time Triage Engine — Architecture

## Design Principles

1. **Fail-closed by default**: Any uncertainty, missing data, or hard trigger forces inadmissibility.
2. **Separation of concerns**: Sufficiency, admissibility, and scalar are distinct, independently testable layers.
3. **Commit-time binding**: Every evaluation is hashed and logged, creating an immutable audit trail.
4. **Domain-agnostic core, domain-specific config**: The same pipeline runs for human, robot, and AI; only the parameters change.

## Pipeline Flow

```
┌─────────────┐
│ Sensor Input│
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Sufficiency Registry│  ← required signals, min quality, min duration
│      .check()       │
└──────┬──────────────┘
       │ sufficient?
       ▼
┌─────────────────────┐
│  Coherence Monitor  │  ← signal agreement rules
│      .check()       │
└──────┬──────────────┘
       │ coherent?
       ▼
┌─────────────────────┐
│ Admissibility Gate  │  ← hard triggers (fail-closed)
│      .check()       │
└──────┬──────────────┘
       │ admissible?
       ▼
┌─────────────────────┐
│  Scalar Computation │  ← U = ∏(factor^weight), floor-protected
│   compute_scalar()  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Level Assignment  │  ← GREEN/YELLOW/ORANGE/RED/BLACK
│  scalar_to_level()  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Commit Binding    │  ← SHA-256 hash, immutable record
│    bind_commit()    │
└─────────────────────┘
```

## Scalar Formula

```
U = ∏(factor_i ^ weight_i) × Q

where:
  factor_i = clamp(input_i, floor, 1.0)
  Q = observability factor (double-weighted)
  floor = domain-configurable minimum (default 0.05)
```

The floor prevents total scalar collapse when a single sensor fails. This is intentional: degradation should be visible, not binary.

## Triage Levels

| Level | Condition | Action |
|-------|-----------|--------|
| GREEN | admissible=True, scalar ≥ 0.8 | Normal operation |
| YELLOW | admissible=True, scalar ≥ 0.5 | Degraded — monitor closely |
| ORANGE | admissible=True, scalar < 0.5 | Restricted — reduced authority |
| RED | admissible=False, scalar > 0.05 | Hard stop — requires reset |
| BLACK | admissible=False, scalar ≤ 0.05 | Nonrecoverable — halt, notify oversight |

## Commit Binding

Every `TriageResult` includes a `CommitRecord` with:
- `timestamp`: Unix epoch seconds
- `domain`: Which domain config was used
- `admissible`, `scalar`, `level`: The decision
- `sufficiency_flags`, `reason_codes`: Why
- `commit_hash`: SHA-256 of canonical JSON payload (first 16 chars)

This creates an immutable, auditable log entry suitable for:
- StegDB governance event ingestion
- Forensic replay
- Regulatory compliance

## Extending to New Domains

1. Create a new file in `triage/domains/`
2. Define a `DomainConfig` with:
   - `SufficiencyRegistry` (required/optional signals)
   - `AdmissibilityGate` (thresholds)
   - `ScalarConfig` (weights, floor, trend window)
   - `CoherenceMonitor` (agreement rules)
3. Instantiate `TriageEvaluator(config)` and use

## Safety Invariants (enforced by tests)

- [x] Missing required data blocks diagnosis
- [x] Critical states fail closed
- [x] Scalar drops under degradation
- [x] Reason codes explain every decision
- [x] Human, robot, and AI share the same architecture
