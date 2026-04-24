# Commit-Time Triage Engine — Architecture

## Design Principles

1. **Fail-closed by default**: Any uncertainty, missing data, or hard trigger
   forces inadmissibility.
2. **Separation of concerns**: Sufficiency, admissibility, and scalar are
   distinct, independently testable layers.
3. **Commit-time binding**: Every evaluation is hashed and logged, creating an
   immutable audit trail.
4. **Domain-agnostic core, domain-specific config**: The same pipeline runs for
   human, robot, and AI; only the parameters change.

## Pipeline Flow

```
sensor input -> sufficiency registry -> sufficiency check ->
coherence monitor -> admissibility gate -> scalar computation ->
level assignment -> commit binding
```

## Scalar Formula

```
U = prod(factor_i ^ weight_i) x Q

where:
  factor_i = clamp(input_i, floor, 1.0)
  Q = observability factor (double-weighted)
  floor = domain-configurable minimum (default 0.05)
```

## Triage Levels

| Level | Condition | Action |
|-------|-----------|--------|
| GREEN | admissible=True, scalar >= 0.8 | Normal operation |
| YELLOW | admissible=True, scalar >= 0.5 | Degraded — monitor closely |
| ORANGE | admissible=True, scalar < 0.5 | Restricted — reduced authority |
| RED | admissible=False, scalar > 0.05 | Hard stop — requires reset |
| BLACK | admissible=False, scalar <= 0.05 | Nonrecoverable — halt, notify |

## Safety Invariants

- [x] Missing required data blocks diagnosis
- [x] Critical states fail closed
- [x] Scalar drops under degradation
- [x] Reason codes explain every decision
- [x] Human, robot, and AI share the same architecture
