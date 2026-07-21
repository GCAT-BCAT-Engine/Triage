#!/usr/bin/env python3
"""Project Triage implementation evidence without overstating operational completion."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJECTIVE = ROOT / "autonomy" / "objective-contract.json"
OUT = ROOT / "data" / "autonomy" / "completion-evidence.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    objective = json.loads(OBJECTIVE.read_text(encoding="utf-8"))
    if objective.get("repository") != "GCAT-BCAT-Engine/Triage":
        raise SystemExit("TRIAGE AUTONOMY PROJECTION: DENY repository binding mismatch")
    if objective.get("completion_policy", {}).get("unit_tests_prove_implementation_only") is not True:
        raise SystemExit("TRIAGE AUTONOMY PROJECTION: DENY unit-test authority boundary missing")

    tests_passed = os.environ.get("TRIAGE_TESTS_PASSED") == "true"
    implementation_checks = {
        "all_domain_unit_tests_pass": tests_passed,
        "objective_contract_bound": True,
        "fail_closed_completion_policy": objective.get("completion_policy", {}).get("unknown_is_complete") is False,
        "medical_authority_not_claimed": objective.get("safety_boundary", {}).get("medical_device_claimed") is False,
    }
    implementation_installed = all(implementation_checks.values())

    missing_gates = []
    if not implementation_installed:
        missing_gates.append("implementation_validation")
    missing_gates.extend([
        "observed_user_facing_execution",
        "runtime_observed",
        "user_visible_outcome_verified",
    ])

    payload = {
        "schema_version": "1.0",
        "repository": "GCAT-BCAT-Engine/Triage",
        "objective_id": objective["objective_id"],
        "runtime_observed": False,
        "user_visible_outcome_verified": False,
        "verifier_source": "github-actions",
        "critical_blockers": len(missing_gates),
        "manual_completion_dependency": False,
        "verified_at": now(),
        "evidence_urls": [
            "https://github.com/GCAT-BCAT-Engine/Triage/actions/workflows/autonomy-objective-validation.yml",
            "https://github.com/GCAT-BCAT-Engine/Triage/blob/main/autonomy/objective-contract.json",
        ],
        "projection_state": "IMPLEMENTATION_INSTALLED_ACTIVATION_UNVERIFIED" if implementation_installed else "PARTIAL",
        "implementation_checks": implementation_checks,
        "missing_gates": missing_gates,
        "authority": {
            "unit_tests_are_operational_completion": False,
            "workflow_success_is_user_visible_runtime": False,
            "projection_is_release_authority": False,
            "projection_is_medical_authority": False,
            "manual_user_action_required": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"projection_state": payload["projection_state"], "missing_gates": missing_gates}))


if __name__ == "__main__":
    main()
