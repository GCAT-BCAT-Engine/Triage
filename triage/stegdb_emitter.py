"""Triage-specific StegDB event emitter.

Emits triage.evaluation events and receives canonical updates.
Platform agnostic — works on any Git host.
"""

from __future__ import annotations

from typing import Any

from triage.core.evaluator import TriageResult
from triage.stegdb_adapter import StegDBAdapter


class TriageStegDBEmitter:
    """Emit triage events to StegDB and receive canonical updates."""

    def __init__(
        self,
        source_repo: str,
        platform: str = "github",
        backend: str = "git_commit",
    ) -> None:
        self.adapter = StegDBAdapter(
            source_repo=source_repo,
            platform=platform,
            backend=backend,
        )

    def emit_evaluation(self, result: TriageResult, inputs: dict[str, Any]) -> None:
        """Emit a triage.evaluation event after every evaluation."""
        payload = {
            "domain": result.commit_record.domain,
            "admissible": result.admissible,
            "scalar": result.scalar,
            "level": result.level,
            "sufficiency_flags": result.sufficiency_flags,
            "reason_codes": result.reason_codes,
            "commit_hash": result.commit_hash,
            "inputs_summary": {k: ("present" if v is not None else "missing") for k, v in inputs.items()},
        }
        self.adapter.emit(
            event_type="triage.evaluation",
            payload=payload,
            source_commit=result.commit_hash,
        )

    def emit_canonical_update_request(
        self,
        domain: str,
        requested_changes: list[dict[str, Any]],
    ) -> None:
        """Request a canonical update from StegDB.

        Used when Triage detects that its local config has drifted
        from the canonical version stored in StegDB.
        """
        payload = {
            "domain": domain,
            "requested_changes": requested_changes,
            "reason": "config_drift_detected",
        }
        self.adapter.emit(
            event_type="triage.canonical_update_request",
            payload=payload,
        )

    def receive_canonical_update(self, update_path: str) -> dict[str, Any]:
        """Receive and apply a canonical update from StegDB.

        Returns the update payload. The caller (typically CI or a
        maintenance script) is responsible for applying the changes.
        """
        return self.adapter.receive_canonical_update(update_path)
