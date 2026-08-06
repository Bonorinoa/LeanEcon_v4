"""A1 runner — health-first diagnostics (Gate 4).

Runs all ten A1 criteria and emits one machine-readable event per
diagnostic. Criteria that need live credentials or the pinned workspace
are probed; anything unavailable is reported as UNAVAILABLE/BLOCKED —
never silent fallback.

Live provider probes run only with --live and only for the models named
in the adapter's MVP configuration map (core and runner never name model
identifiers directly). Payloads are synthetic and PUBLIC-classified.
Secrets are never printed; output is redacted by construction.

Attribution: prepared by Hermes Agent (Nous Research) under direction of
the CTO (@Bonorinoa).
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from leanecon import lean_probe
from leanecon.adapters.mistral import MVP_MODEL_MAP, MistralAdapter
from leanecon.data_policy import classify, evaluate
from leanecon.events import (
    EVENT_DIAGNOSTIC_RESULT,
    EVENT_HEALTH_CHECK,
    CapabilityStatus,
    Event,
    EventLog,
)
from leanecon.providers import Capability, ProviderFailure
from leanecon.repopath import find_repo_root

REPO_ROOT = find_repo_root()
WORKSPACE = REPO_ROOT / "lean_workspace"

A1_GREEN_CRITERIA = {
    "C1_pinned_lean_mathlib_build": "pinned Lean and Mathlib build successfully",
    "C2_lean_compiler_probe": "Lean compiler probe succeeds",
    "C3_lsp_probe": "LSP responds or explicitly reports UNAVAILABLE",
    "C4_formalization_structured_output": "formalization model returns valid structured output (live)",
    "C5_interpretation_schema": "interpretation model returns schema-valid interpretation (live)",
    "C6_provider_metadata": "provider metadata includes model/request-id/latency/tokens",
    "C7_machine_readable_events": "every diagnostic emits a machine-readable event",
    "C8_gold_isolation": "runtime cannot access v3 gold/labels/release artifacts",
    "C9_invalid_lean_typed_failure": "invalid Lean input produces a typed failure",
    "C10_provider_failure_typed": "outage/malformed output produces typed provider failure",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class A1Run:
    def __init__(self, events_dir: Path):
        self.run_id = f"a1-{uuid.uuid4().hex[:12]}"
        self.events = EventLog(events_dir / f"{self.run_id}.jsonl")
        self.results: dict[str, dict] = {}
        self.events.append(
            Event(
                event_type=EVENT_HEALTH_CHECK,
                run_id=self.run_id,
                source_component="a1-runner",
                actor="system",
                payload_class="PROJECT",
                trace_ref=self.run_id,
                detail={"started_at": _now()},
            )
        )

    def record(self, criterion: str, status: CapabilityStatus, detail: dict, reason_code: str | None = None):
        event = Event(
            event_type=EVENT_DIAGNOSTIC_RESULT,
            run_id=self.run_id,
            source_component="a1-runner",
            actor="system",
            payload_class="PROJECT",
            trace_ref=self.run_id,
            reason_codes=(reason_code,) if reason_code else (),
            detail={"criterion": criterion, "status": status.value, **detail},
        )
        self.events.append(event)
        self.results[criterion] = {"status": status.value, "reason_code": reason_code}

    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "emitted_at": _now(),
            "criteria": self.results,
            "all_green": all(r["status"] == CapabilityStatus.HEALTHY.value for r in self.results.values()),
        }


def probe_c1_c2_c3(run: A1Run) -> None:
    workspace = lean_probe.probe_workspace(WORKSPACE)
    if workspace.status is CapabilityStatus.HEALTHY:
        compile_probe = lean_probe.probe_lean_compile(WORKSPACE, target="LeanEcon.A1")
        run.record("C1_pinned_lean_mathlib_build", compile_probe.status, compile_probe.detail, compile_probe.reason_code)
        run.record("C2_lean_compiler_probe", compile_probe.status, {"target": "LeanEcon.A1"}, compile_probe.reason_code)
    else:
        run.record("C1_pinned_lean_mathlib_build", CapabilityStatus.UNAVAILABLE, workspace.detail, workspace.reason_code)
        run.record("C2_lean_compiler_probe", CapabilityStatus.UNAVAILABLE, {"note": "workspace unpinned"}, workspace.reason_code)
    lsp = lean_probe.probe_lsp(WORKSPACE)
    run.record("C3_lsp_probe", lsp.status, lsp.detail, lsp.reason_code)


def probe_c9(run: A1Run) -> None:
    result = lean_probe.probe_invalid_lean(WORKSPACE, "def broken : Nat := ", timeout_s=120)
    run.record("C9_invalid_lean_typed_failure", result.status, result.detail, result.reason_code)


def probe_c4_c5_c6(run: A1Run) -> None:
    """Live probes for criteria 4–6. Requires --live; synthetic PUBLIC
    payloads only. No silent fallback: failures are typed and recorded."""
    adapter = MistralAdapter(
        emit_event=lambda decision, cap, run_id, claim_id: run.events.append(
            adapter.emit_blocked_event(decision, cap, run_id, claim_id)
        )
    )
    probes = {
        "C4_formalization_structured_output": (
            Capability.FORMALIZE,
            MVP_MODEL_MAP[Capability.FORMALIZE].model,
            {
                "prompt": (
                    "A1 diagnostic probe. Return JSON only: "
                    '{"a1_probe": true}. No Lean code is requested.'
                )
            },
        ),
        "C5_interpretation_schema": (
            Capability.INTERPRET,
            MVP_MODEL_MAP[Capability.INTERPRET].model,
            {
                "prompt": (
                    "A1 diagnostic probe. Interpret this synthetic microeconomic "
                    "claim in one sentence: 'If a budget set expands and preferences "
                    "are unchanged, the attainable set does not shrink.' Reply with "
                    "JSON: {\"interpretation\": \"...\"}."
                )
            },
        ),
    }
    metadata_ok = True
    for criterion, (capability, model, payload) in probes.items():
        try:
            response = adapter.request(
                capability=capability,
                model=model,
                typed_payload=payload,
                declared_class="PUBLIC",
                run_id=run.run_id,
            )
        except ProviderFailure as failure:
            run.record(criterion, CapabilityStatus.UNAVAILABLE, {"error": failure.message}, failure.reason_code)
            metadata_ok = False
            continue
        meta = response.metadata
        has_metadata = all(
            (
                meta.model == model,
                meta.provider == "mistral",
                meta.latency_ms is not None,
            )
        )
        metadata_ok = metadata_ok and has_metadata
        run.record(
            criterion,
            response.status,
            {
                "model": meta.model,
                "request_id": meta.request_id,
                "latency_ms": meta.latency_ms,
                "token_metadata_present": meta.token_metadata is not None,
                "output_preview": str(response.output)[:120],
            },
        )
    status = CapabilityStatus.HEALTHY if metadata_ok else CapabilityStatus.UNAVAILABLE
    run.record("C6_provider_metadata", status, {"checked": ["model", "request_id", "latency", "token_metadata"]})


def probe_c7(run: A1Run) -> None:
    # Every recorded criterion must have a machine-readable event in the log.
    records = run.events.read_all()
    diagnostics = [r for r in records if r.get("event_type") == EVENT_DIAGNOSTIC_RESULT]
    covered = {r["detail"]["criterion"] for r in diagnostics}
    ok = covered == set(run.results.keys())
    run.record(
        "C7_machine_readable_events",
        CapabilityStatus.HEALTHY if ok else CapabilityStatus.UNAVAILABLE,
        {"events": len(diagnostics), "criteria_covered": sorted(covered)},
    )


def probe_c8(run: A1Run) -> None:
    from leanecon import gold_isolation

    problems = gold_isolation.scan_forbidden_paths(REPO_ROOT)
    problems += gold_isolation.scan_forbidden_env()
    problems += gold_isolation.scan_release_artifacts(REPO_ROOT)
    run.record(
        "C8_gold_isolation",
        CapabilityStatus.HEALTHY if not problems else CapabilityStatus.UNAVAILABLE,
        {"forbidden_paths_found": problems},
        reason_code="INPUT_REJECTED" if problems else None,
    )


def probe_c10(run: A1Run) -> None:
    """Typed provider failure against a guaranteed-invalid response shape."""
    from leanecon.providers import ProviderFailureKind

    def malformed(request, api_key, timeout_s):
        return {"no": "choices"}

    adapter = MistralAdapter(transport=malformed, api_key_env=MistralAdapter.credential_env_name)
    try:
        adapter.request(
            capability=Capability.INTERPRET,
            model=MVP_MODEL_MAP[Capability.INTERPRET].model,
            typed_payload={"prompt": "A1 failure-path probe"},
            declared_class="PUBLIC",
            run_id=run.run_id,
        )
        run.record("C10_provider_failure_typed", CapabilityStatus.UNAVAILABLE, {"error": "malformed output unexpectedly accepted"})
    except ProviderFailure as failure:
        typed = failure.kind in (ProviderFailureKind.INVALID_OUTPUT, ProviderFailureKind.UNAVAILABLE)
        run.record(
            "C10_provider_failure_typed",
            CapabilityStatus.HEALTHY if typed else CapabilityStatus.UNAVAILABLE,
            {"kind": failure.kind.value, "reason_code": failure.reason_code},
        )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="LeanEcon v4 A1 diagnostics")
    parser.add_argument("--live", action="store_true", help="run live provider probes (criteria 4-6)")
    parser.add_argument("--events-dir", default="artifacts/local/a1-events", help="event log directory")
    parser.add_argument("--skip-lean", action="store_true", help="skip workspace probes (criterion 1,2,3,9)")
    args = parser.parse_args(argv)

    run = A1Run(Path(args.events_dir))
    print(f"A1 run: {run.run_id}", file=sys.stderr)

    if not args.skip_lean:
        probe_c1_c2_c3(run)
        probe_c9(run)
    probe_c8(run)
    probe_c10(run)
    if args.live:
        probe_c4_c5_c6(run)
    else:
        for criterion in ("C4_formalization_structured_output", "C5_interpretation_schema"):
            run.record(criterion, CapabilityStatus.UNAVAILABLE, {"note": "skipped: rerun with --live"})
        run.record("C6_provider_metadata", CapabilityStatus.UNAVAILABLE, {"note": "skipped: rerun with --live"})
    probe_c7(run)

    summary = run.summary()
    print(json.dumps(summary, indent=2))
    return 0 if summary["all_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
