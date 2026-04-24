"""Commit-time binding.

Every triage evaluation is hashed and logged for audit.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CommitRecord:
    """Immutable record of a triage evaluation."""

    timestamp: float
    domain: str
    admissible: bool
    scalar: float
    level: str
    sufficiency_flags: list[str]
    reason_codes: list[str]
    commit_hash: str


def bind_commit(
    domain: str,
    admissible: bool,
    scalar: float,
    level: str,
    sufficiency_flags: list[str],
    reason_codes: list[str],
    inputs: dict[str, Any],
) -> CommitRecord:
    """Create an immutable commit record with a content hash."""
    timestamp = time.time()

    payload = {
        "timestamp": timestamp,
        "domain": domain,
        "admissible": admissible,
        "scalar": scalar,
        "level": level,
        "sufficiency_flags": sufficiency_flags,
        "reason_codes": reason_codes,
        "inputs": inputs,
    }

    canonical = json.dumps(payload, sort_keys=True, default=str)
    commit_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    return CommitRecord(
        timestamp=timestamp,
        domain=domain,
        admissible=admissible,
        scalar=scalar,
        level=level,
        sufficiency_flags=sufficiency_flags,
        reason_codes=reason_codes,
        commit_hash=commit_hash,
    )
