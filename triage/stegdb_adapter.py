"""StegDB Governance Adapter — platform agnostic.

Embedded in Triage repo for self-containment. No external deps.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any


@dataclass
class GovernanceEvent:
    """A canonical governance event."""

    event_type: str
    source_repo: str
    source_commit: str
    payload: dict[str, Any]
    platform: str = "github"
    event_id: str = ""
    timestamp: str = ""
    canonical_signature: str = ""
    routing_key: str = "default"

    def __post_init__(self):
        if not self.event_id:
            self.event_id = hashlib.sha256(
                f"{self.source_repo}:{time.time()}:{uuid.uuid4()}".encode()
            ).hexdigest()[:32]
        if not self.timestamp:
            self.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source_repo": self.source_repo,
            "source_commit": self.source_commit,
            "timestamp": self.timestamp,
            "platform": self.platform,
            "payload": self.payload,
            "canonical_signature": self.canonical_signature,
            "routing_key": self.routing_key,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, default=str, separators=(",", ":"))


class StegDBAdapter:
    """Platform-agnostic StegDB adapter."""

    def __init__(
        self,
        source_repo: str,
        platform: str = "github",
        backend: str = "git_commit",
        endpoint: str | None = None,
        secret: str | None = None,
    ) -> None:
        self.source_repo = source_repo
        self.platform = platform
        self.backend = backend
        self.endpoint = endpoint or os.environ.get("STEGDB_ENDPOINT", "")
        self.secret = secret or os.environ.get("STEGDB_SECRET", "")

    def emit(
        self,
        event_type: str,
        payload: dict[str, Any],
        source_commit: str = "",
    ) -> GovernanceEvent:
        event = GovernanceEvent(
            event_type=event_type,
            source_repo=self.source_repo,
            source_commit=source_commit or self._get_current_commit(),
            payload=payload,
            platform=self.platform,
        )

        if self.backend == "git_commit":
            self._emit_via_git(event)
        elif self.backend == "webhook":
            self._emit_via_webhook(event)
        elif self.backend == "file_drop":
            self._emit_via_file_drop(event)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")

        return event

    def receive_canonical_update(self, update_path: str) -> dict[str, Any]:
        with open(update_path, "r", encoding="utf-8") as f:
            update = json.load(f)

        expected = self._compute_hmac(update["canonical_json"])
        if update.get("canonical_signature") != expected:
            raise ValueError("Canonical signature mismatch")

        update_time = time.mktime(time.strptime(update["timestamp"], "%Y-%m-%dT%H:%M:%SZ"))
        if abs(time.time() - update_time) > 300:
            raise ValueError("Canonical update expired")

        return update["payload"]

    def _get_current_commit(self) -> str:
        import subprocess

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()[:16]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"

    def _emit_via_git(self, event: GovernanceEvent) -> None:
        events_file = "stegdb_events.jsonl"
        with open(events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), default=str) + "\n")

    def _emit_via_webhook(self, event: GovernanceEvent) -> None:
        import urllib.request

        headers = {
            "Content-Type": "application/json",
            "X-StegDB-Signature": self._compute_hmac(event.canonical_json()),
        }
        data = event.canonical_json().encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers=headers,
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)

    def _emit_via_file_drop(self, event: GovernanceEvent) -> None:
        drop_dir = os.environ.get("STEGDB_DROP_DIR", "/var/stegdb/incoming")
        os.makedirs(drop_dir, exist_ok=True)
        filepath = os.path.join(drop_dir, f"{event.event_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(event.to_dict(), f, default=str)

    def _compute_hmac(self, message: str) -> str:
        import hmac

        if not self.secret:
            return ""
        return hmac.new(
            self.secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
