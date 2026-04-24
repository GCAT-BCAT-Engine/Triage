"""Canonical Update Receiver for Triage.

Applies validated canonical updates from StegDB to the local repo.
Designed to run in CI or as a scheduled maintenance job.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from triage.stegdb_adapter import StegDBAdapter


def apply_canonical_update(update_path: str, repo_root: str = ".") -> None:
    """Apply a canonical update to the Triage repo.

    Args:
        update_path: Path to the canonical_update.json from StegDB.
        repo_root: Root of the Triage repo.
    """
    adapter = StegDBAdapter(
        source_repo="github.com/GCAT-BCAT-Engine/Triage",
        backend="git_commit",
    )

    try:
        payload = adapter.receive_canonical_update(update_path)
    except ValueError as e:
        print(f"Update rejected: {e}", file=sys.stderr)
        sys.exit(1)

    changes = payload.get("changes", [])
    for change in changes:
        _apply_change(change, repo_root)

    print(f"Applied {len(changes)} canonical changes.")


def _apply_change(change: dict, repo_root: str) -> None:
    """Apply a single canonical change."""
    action = change.get("action")
    target = change.get("target")
    content = change.get("content")

    target_path = Path(repo_root) / target

    if action == "update_file":
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {target}")
    elif action == "delete_file":
        if target_path.exists():
            target_path.unlink()
            print(f"Deleted: {target}")
    elif action == "rename_file":
        new_name = change.get("new_name")
        if new_name:
            target_path.rename(Path(repo_root) / new_name)
            print(f"Renamed: {target} -> {new_name}")
    elif action == "update_config":
        # Merge config into domain config file
        domain = change.get("domain", "robotics")
        config_path = Path(repo_root) / "triage" / "domains" / f"{domain}.py"
        if config_path.exists():
            print(f"Config update for {domain}: manual review required")
            print(f"  Changes: {json.dumps(content, indent=2)}")
        else:
            print(f"Config target not found: {config_path}", file=sys.stderr)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m triage.canonical_updater <update.json>", file=sys.stderr)
        sys.exit(1)
    apply_canonical_update(sys.argv[1])
