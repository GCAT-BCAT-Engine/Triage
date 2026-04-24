"""Admissibility gate — fail-closed.

Hard safety triggers that override the scalar and force
admissibility = False regardless of other factors.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class HardTrigger(str, Enum):
    """Named hard safety triggers."""

    NO_PULSE = "NO_PULSE"
    NO_BREATHING = "NO_BREATHING"
    CRITICAL_PERFUSION_FAILURE = "CRITICAL_PERFUSION_FAILURE"
    LOSS_OF_CONTROL = "LOSS_OF_CONTROL"
    LOSS_OF_AUTHORITY = "LOSS_OF_AUTHORITY"
    LOW_OBSERVABILITY = "LOW_OBSERVABILITY"
    INCOHERENT_SIGNALS = "INCOHERENT_SIGNALS"
    SUFFICIENCY_FAIL = "SUFFICIENCY_FAIL"


@dataclass
class AdmissibilityGate:
    """Evaluates hard safety triggers."""

    observability_threshold: float = 0.2

    def check(
        self,
        inputs: dict[str, Any],
        sufficiency_ok: bool,
        coherence_ok: bool,
    ) -> AdmissibilityResult:
        """Return fail-closed admissibility decision."""
        triggers: list[HardTrigger] = []

        if not sufficiency_ok:
            triggers.append(HardTrigger.SUFFICIENCY_FAIL)

        if not coherence_ok:
            triggers.append(HardTrigger.INCOHERENT_SIGNALS)

        pulse = inputs.get("pulse")
        if pulse is not None and isinstance(pulse, dict):
            if pulse.get("value") in (0, None, False):
                triggers.append(HardTrigger.NO_PULSE)
        elif pulse == 0:
            triggers.append(HardTrigger.NO_PULSE)

        breathing = inputs.get("breathing")
        if breathing is not None and isinstance(breathing, dict):
            if breathing.get("value") in (0, None, False):
                triggers.append(HardTrigger.NO_BREATHING)
        elif breathing == 0:
            triggers.append(HardTrigger.NO_BREATHING)

        perfusion = inputs.get("perfusion")
        if perfusion is not None and isinstance(perfusion, dict):
            if perfusion.get("value", 1.0) < 0.1:
                triggers.append(HardTrigger.CRITICAL_PERFUSION_FAILURE)
        elif isinstance(perfusion, (int, float)) and perfusion < 0.1:
            triggers.append(HardTrigger.CRITICAL_PERFUSION_FAILURE)

        control = inputs.get("control")
        if control is not None and isinstance(control, dict):
            if control.get("value") in (0, None, False):
                triggers.append(HardTrigger.LOSS_OF_CONTROL)
        elif control == 0:
            triggers.append(HardTrigger.LOSS_OF_CONTROL)

        authority = inputs.get("authority")
        if authority is not None and isinstance(authority, dict):
            if authority.get("value") in (0, None, False):
                triggers.append(HardTrigger.LOSS_OF_AUTHORITY)
        elif authority == 0:
            triggers.append(HardTrigger.LOSS_OF_AUTHORITY)

        observability = inputs.get("observability")
        if observability is not None and isinstance(observability, dict):
            obs_val = observability.get("value", 1.0)
        elif isinstance(observability, (int, float)):
            obs_val = observability
        else:
            obs_val = 1.0

        if obs_val < self.observability_threshold:
            triggers.append(HardTrigger.LOW_OBSERVABILITY)

        admissible = len(triggers) == 0
        return AdmissibilityResult(
            admissible=admissible,
            triggers=triggers,
        )


@dataclass(frozen=True)
class AdmissibilityResult:
    """Outcome of the admissibility gate."""

    admissible: bool
    triggers: list[HardTrigger]

    @property
    def reason_codes(self) -> list[str]:
        return [t.value for t in self.triggers]
