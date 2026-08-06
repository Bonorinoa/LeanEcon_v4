"""A3 runner — minimal verified workflow orchestrator (Gate 5).

CLI entry point: ``python -m leanecon.a3_runner <subcommand>``.

Subcommands (the CTO-facing surface):
  ingest        create a claim revision (DRAFT)
  interpret     run interpretation (live) -> INTERPRETED -> REVIEW_REQUIRED
  review        reviewer decision: approve | reject  (ACCEPTED | REJECTED)
  formalize     run formalization (live) -> FORMALIZED (or stays with gaps)
  gap-ack       reviewer acknowledges mapping gaps (enables PROVING)
  axiom-approve reviewer approves the axiom list (per-run reviewer record)
  verify        proof input -> PROVING -> VERIFIED | FAILED | BLOCKED + bundle
  bundle        re-validate the current bundle and print the 11-item checklist
  replay        trace replay by run id or claim id
  status        claim state and artifact references

Actor rules (locked at Gate 3): only a human reviewer may emit ACCEPTED or
REJECTED; the system emits processing states and FAILED/BLOCKED; VERIFIED
comes only from the bundle validator path. ``--reviewer`` (or the
LEANECON_REVIEWER_ID environment variable) is required for review commands.

Attribution: prepared by Hermes Agent (Nous Research) under direction of
the CTO (@Bonorinoa).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

from leanecon import lean_probe
from leanecon.adapters.mistral import MVP_MODEL_MAP, MistralAdapter
from leanecon.bundle import build_bundle, validate_bundle
from leanecon.claim_store import (
    DEFAULT_ROOT,
    ArtifactStore,
    ClaimRecord,
    new_run_id,
)
from leanecon.data_policy import contains_gold
from leanecon.events import (
    EVENT_CLAIM_STATE_CHANGED,
    EVENT_DIAGNOSTIC_RESULT,
    EVENT_PROVIDER_REQUEST_BLOCKED,
    EVENT_VERIFICATION_COMPLETED,
    Event,
    EventLog,
)
from leanecon.formalization import (
    formalize_prompt,
    parse_formalize_response,
    validate_mapping_report,
)
from leanecon.interpretation import (
    finalize_ei,
    interpret_prompt,
    parse_interpret_response,
    validate_ei_candidate,
)
from leanecon.lean_probe import probe_workspace
from leanecon.lifecycle import TERMINAL_STATES
from leanecon.providers import Capability, ProviderAdapter, ProviderFailure
from leanecon.repopath import find_repo_root
from leanecon.trace_replay import replay_claim, replay_run
from leanecon.verifier import REASON_SORRY_FOUND, verify_candidate

REPO_ROOT = find_repo_root()
WORKSPACE = REPO_ROOT / "lean_workspace"
EVENTS_DIR = REPO_ROOT / "artifacts/local/a3-events"

#: canonical claim texts (Appendix A of docs/gate5/a3-design.md, approved as proposed)
CANONICAL_CLAIMS: dict[str, str] = {
    "c1": "If a consumer's feasible budget set expands while preferences remain unchanged, the consumer's attainable set does not shrink.",
    "c2": "Weak preference is transitive: if A is weakly preferred to B and B is weakly preferred to C, then A is weakly preferred to C.",
    "c3": "If a utility function is strictly increasing, then x >= y componentwise and x != y implies u(x) > u(y).",
    "c4": "A monotone nondecreasing function f : R -> R preserves order: a <= b implies f a <= f b.",
}


def _new_run(events_dir: Path | str) -> tuple[str, EventLog]:
    run_id = new_run_id()
    log = EventLog(Path(events_dir) / f"{run_id}.jsonl")
    return run_id, log


def _emit(log: EventLog, event: Event) -> Event:
    return log.append(event)


def _state_event(
    log: EventLog,
    run_id: str,
    claim_id: str,
    before: Optional[str],
    after: str,
    actor: str,
    source_component: str,
    reason_codes: tuple = (),
    detail: Optional[dict] = None,
) -> Event:
    return _emit(
        log,
        Event(
            event_type=EVENT_CLAIM_STATE_CHANGED,
            run_id=run_id,
            claim_id=claim_id,
            state_before=before,
            state_after=after,
            source_component=source_component,
            actor=actor,
            reason_codes=reason_codes,
            payload_class="PROJECT",
            trace_ref=f"claim:{claim_id}",
            detail=detail or {},
        ),
    )


def _reviewer_identity(args) -> str:
    reviewer = getattr(args, "reviewer", None) or os.environ.get("LEANECON_REVIEWER_ID")
    if not reviewer:
        raise SystemExit("reviewer identity required: pass --reviewer or set LEANECON_REVIEWER_ID")
    return reviewer


def _claim_state_guard(claim: ClaimRecord, allowed: set[str], action: str) -> None:
    if claim.state not in allowed:
        raise SystemExit(
            f"cannot {action}: claim {claim.claim_id} is in state {claim.state}, expected one of {sorted(allowed)}"
        )


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------


def cmd_ingest(args, store: ArtifactStore) -> int:
    claim_id = args.claim_id
    existing = None
    try:
        existing = store.load_claim(claim_id)
    except FileNotFoundError:
        pass

    data_class = (args.claim_class or "PROJECT").upper()
    if data_class not in ("PUBLIC", "PROJECT"):
        run_id, log = _new_run(args.events_dir)
        _emit(
            log,
            Event(
                event_type="PROVIDER_REQUEST_BLOCKED",
                run_id=run_id,
                claim_id=claim_id,
                source_component="a3-ingest",
                actor="policy-boundary",
                reason_codes=("RESTRICTED_BLOCKED",),
                payload_class="RESTRICTED",
                trace_ref=f"deny-{run_id}",
                detail={"reason": "RESTRICTED claims are hard-denied in MVP; no opt-in mechanism"},
            ),
        )
        print(f"refused: RESTRICTED class hard-denied (event in {log.path})")
        return 1

    # Fail fast at ingest: sealed gold / hidden evaluation material must
    # never enter the pipeline (evaluation integrity). The provider boundary
    # would also deny it later, but the state event would then carry
    # PROVIDER_UNAVAILABLE — the ingest-time check gives the correct reason.
    if args.claim_text and contains_gold({"claim_text": args.claim_text}):
        run_id, log = _new_run(args.events_dir)
        _emit(
            log,
            Event(
                event_type="PROVIDER_REQUEST_BLOCKED",
                run_id=run_id,
                claim_id=claim_id,
                source_component="a3-ingest",
                actor="policy-boundary",
                reason_codes=("INPUT_REJECTED",),
                payload_class=data_class,
                trace_ref=f"deny-{run_id}",
                detail={"reason": "claim text contains sealed-gold/hidden-evaluation markers"},
            ),
        )
        print(f"refused: claim text contains sealed-gold/hidden-evaluation markers (event in {log.path})")
        return 1

    if existing is not None:
        if existing.state not in TERMINAL_STATES:
            raise SystemExit(f"claim {claim_id} is already active in state {existing.state}")
        revision = existing.revision + 1
        source_text = args.claim_text or existing.source_text
        print(f"new revision {revision} for claim {claim_id} (previous state {existing.state})")
    else:
        revision = 1
        source_text = args.claim_text
        if not source_text:
            raise SystemExit("--claim-text required for a new claim")

    claim = ClaimRecord(claim_id=claim_id, revision=revision, source_text=source_text, data_class=data_class)
    store.save_claim(claim)
    run_id, log = _new_run(args.events_dir)
    _state_event(log, run_id, claim_id, None, "DRAFT", "system", "a3-ingest", detail={"revision": revision})
    print(f"claim {claim_id} r{revision} created: DRAFT")
    print(f"  digest={store.read_json(store.claim_path(claim_id))['digest'][:16]}… class={data_class}")
    print(f"  events={log.path}")
    return 0


# ---------------------------------------------------------------------------
# interpret
# ---------------------------------------------------------------------------


def _make_adapter(run_id: str, log: EventLog) -> MistralAdapter:
    def emit_blocked(decision, capability, run_id, claim_id):
        _emit(
            log,
            Event(
                event_type=EVENT_PROVIDER_REQUEST_BLOCKED,
                run_id=run_id,
                claim_id=claim_id,
                source_component="provider-boundary",
                actor="policy-boundary",
                reason_codes=(decision.reason_code,) if decision.reason_code else (),
                payload_class=decision.payload_class.value,
                trace_ref=f"deny-{run_id}",
                detail={"capability": capability.value},
            ),
        )

    return MistralAdapter(emit_event=emit_blocked)


def interpret_claim(claim: ClaimRecord, store: ArtifactStore, log: EventLog, run_id: str, adapter: ProviderAdapter) -> tuple[str, Optional[dict]]:
    """Run interpretation; returns (state_after, ei_candidate_or_None)."""
    claim_id = claim.claim_id
    try:
        response = adapter.request(
            capability=Capability.INTERPRET,
            model=MVP_MODEL_MAP[Capability.INTERPRET].model,
            typed_payload={"prompt": interpret_prompt(claim.source_text)},
            declared_class=claim.data_class,
            run_id=run_id,
            claim_id=claim_id,
        )
    except ProviderFailure as failure:
        if failure.kind.value == "PROVIDER_UNAVAILABLE":
            _state_event(log, run_id, claim_id, claim.state, "BLOCKED", "system", "a3-interpret",
                         reason_codes=(failure.reason_code,), detail={"error": failure.message})
            return "BLOCKED", None
        _state_event(log, run_id, claim_id, claim.state, "FAILED", "system", "a3-interpret",
                     reason_codes=(failure.reason_code,), detail={"error": failure.message})
        return "FAILED", None

    content = (response.output or {}).get("content", "")
    try:
        candidate = parse_interpret_response(content)
    except ValueError as exc:
        _state_event(log, run_id, claim_id, claim.state, "FAILED", "system", "a3-interpret",
                     reason_codes=("PROVIDER_INVALID_OUTPUT",), detail={"error": str(exc)})
        return "FAILED", None

    problems = validate_ei_candidate(candidate)
    if problems:
        _state_event(log, run_id, claim_id, claim.state, "FAILED", "system", "a3-interpret",
                     reason_codes=("PROVIDER_INVALID_OUTPUT",), detail={"validation_problems": problems[:5]})
        return "FAILED", None

    ei_artifact = store.write_ei(claim_id, candidate, status="draft")
    _state_event(log, run_id, claim_id, claim.state, "INTERPRETED", "system", "a3-interpret",
                 detail={"ei_rev": ei_artifact["revision"], "ei_digest": ei_artifact["digest"][:16]})
    _state_event(log, run_id, claim_id, "INTERPRETED", "REVIEW_REQUIRED", "system", "a3-validate",
                 detail={"ei_rev": ei_artifact["revision"]})
    return "REVIEW_REQUIRED", candidate


def cmd_interpret(args, store: ArtifactStore) -> int:
    claim = store.load_claim(args.claim_id)
    _claim_state_guard(claim, {"DRAFT", "BLOCKED", "FAILED"}, "interpret")
    run_id, log = _new_run(args.events_dir)
    adapter = _make_adapter(run_id, log)
    state_after, candidate = interpret_claim(claim, store, log, run_id, adapter)
    claim.state = state_after
    store.save_claim(claim)
    if candidate is not None:
        print(f"claim {claim.claim_id}: INTERPRETED -> REVIEW_REQUIRED (ei digest {candidate.get('digest', 'n/a')[:16]})")
        print("  canonical:", (candidate.get("claim") or {}).get("canonical_text", "")[:120])
        print("  objects:", ", ".join(o.get("id", "?") for o in candidate.get("objects", [])[:8]))
        amb = candidate.get("ambiguities") or []
        print(f"  ambiguities: {len(amb)}" if amb else "  ambiguities: none_noted (reviewer acknowledgement required)")
        print("  conclusion:", (candidate.get("conclusion") or {}).get("text", "")[:120])
    else:
        print(f"claim {claim.claim_id}: {state_after} (see event log)")
    return 0


# ---------------------------------------------------------------------------
# review
# ---------------------------------------------------------------------------


def cmd_review(args, store: ArtifactStore) -> int:
    claim = store.load_claim(args.claim_id)
    _claim_state_guard(claim, {"REVIEW_REQUIRED"}, "review")
    reviewer = _reviewer_identity(args)
    run_id, log = _new_run(args.events_dir)

    ei = store.read_ei(claim.claim_id)
    none_noted = bool(ei.get("none_noted", False))
    acknowledges = getattr(args, "acknowledge_none_noted", False)

    if args.decision == "approve":
        if none_noted and not acknowledges:
            print("refused: interpretation found no ambiguity (none_noted) and the approval does not acknowledge it")
            print("rerun with --acknowledge-none-noted to confirm the reviewer accepts 'no ambiguity noted'")
            return 1
        try:
            finalized = finalize_ei(ei, reviewer, event_ref=f"evt-{run_id}", acknowledges_none_noted=acknowledges, notes=args.notes or "")
        except ValueError as exc:
            print(f"refused: {exc}")
            return 1
        event = _state_event(log, run_id, claim.claim_id, claim.state, "ACCEPTED", reviewer, "a3-review",
                             detail={"ei_rev": ei.get("revision"), "acknowledges_none_noted": acknowledges})
        accepted = store.write_ei(claim.claim_id, finalized, status="accepted")
        store.write_review_record(claim.claim_id, "approval", {
            "decision": "APPROVED", "reviewer": reviewer, "notes": args.notes or "",
            "event_ref": event.event_id, "acknowledges_none_noted": acknowledges,
            "ei_rev": accepted["revision"], "ei_digest": accepted["digest"],
        })
        store.supersede_formals_for(claim.claim_id, accepted["digest"])
        claim.state = "ACCEPTED"
        claim.accepted_ei_rev = accepted["revision"]
        store.save_claim(claim)
        print(f"claim {claim.claim_id}: REVIEW_REQUIRED -> ACCEPTED (reviewer={reviewer})")
        print(f"  accepted EI rev {accepted['revision']} digest {accepted['digest'][:16]}…")
        print(f"  superseded downstream artifacts: any formalization not built on this EI digest")
        return 0

    if args.decision == "reject":
        reason = getattr(args, "reason", None) or "USER_REJECTED"
        event = _state_event(log, run_id, claim.claim_id, claim.state, "REJECTED", reviewer, "a3-review",
                             reason_codes=(reason,), detail={"notes": args.notes or ""})
        store.write_review_record(claim.claim_id, "approval", {
            "decision": "REJECTED", "reviewer": reviewer, "notes": args.notes or "",
            "event_ref": event.event_id, "reason_codes": [reason],
        })
        claim.state = "REJECTED"
        store.save_claim(claim)
        print(f"claim {claim.claim_id}: REVIEW_REQUIRED -> REJECTED ({reason})")
        print("  revision is terminal; open a new revision with `ingest` to retry")
        return 0

    raise SystemExit(f"unknown decision: {args.decision}")


# ---------------------------------------------------------------------------
# formalize
# ---------------------------------------------------------------------------


def formalize_claim(claim: ClaimRecord, store: ArtifactStore, log: EventLog, run_id: str, adapter: ProviderAdapter) -> tuple[str, Optional[dict]]:
    ei = store.read_ei(claim.claim_id, claim.accepted_ei_rev)
    try:
        response = adapter.request(
            capability=Capability.FORMALIZE,
            model=MVP_MODEL_MAP[Capability.FORMALIZE].model,
            typed_payload={"prompt": formalize_prompt(ei)},
            declared_class=claim.data_class,
            run_id=run_id,
            claim_id=claim.claim_id,
        )
    except ProviderFailure as failure:
        if failure.kind.value == "PROVIDER_UNAVAILABLE":
            _state_event(log, run_id, claim.claim_id, claim.state, "BLOCKED", "system", "a3-formalize",
                         reason_codes=(failure.reason_code,), detail={"error": failure.message})
            return "BLOCKED", None
        _state_event(log, run_id, claim.claim_id, claim.state, "FAILED", "system", "a3-formalize",
                     reason_codes=(failure.reason_code,), detail={"error": failure.message})
        return "FAILED", None

    try:
        parsed = parse_formalize_response((response.output or {}).get("content", ""))
    except ValueError as exc:
        _state_event(log, run_id, claim.claim_id, claim.state, "FAILED", "system", "a3-formalize",
                     reason_codes=("PROVIDER_INVALID_OUTPUT",), detail={"error": str(exc)})
        return "FAILED", None

    problems, gaps = validate_mapping_report(parsed["mapping_report"], ei)
    if problems:
        _state_event(log, run_id, claim.claim_id, claim.state, "FAILED", "system", "a3-formalize",
                     reason_codes=("PROVIDER_INVALID_OUTPUT",), detail={"mapping_problems": problems[:5]})
        return "FAILED", None

    imports = [line.split("import", 1)[1].strip() for line in parsed["statement"].splitlines()
               if line.strip().startswith("import")]
    candidate = {
        "statement_text": parsed["statement"],
        "target_theorem": parsed["target_theorem"],
        "mapping_report": parsed["mapping_report"],
        "imports": imports,
        "interpretation_digest": ei.get("digest"),
        "gaps": gaps,
        "provenance": {"capability": "formalize", "model": response.metadata.model, "request_id": response.metadata.request_id},
    }
    artifact = store.write_formal(claim.claim_id, candidate, status="current")
    # The claim DID transition to FORMALIZED (candidate + mapping report exist)
    # even when gaps are present — the state event must be emitted either way
    # or the trace chain becomes inconsistent with the persisted state.
    _state_event(log, run_id, claim.claim_id, claim.state, "FORMALIZED", "system", "a3-formalize",
                 detail={"formal_rev": artifact["revision"], "target_theorem": parsed["target_theorem"],
                         "gap_count": len(gaps)})
    if gaps:
        _emit(log, Event(
            event_type=EVENT_DIAGNOSTIC_RESULT,
            run_id=run_id,
            claim_id=claim.claim_id,
            source_component="a3-formalize",
            actor="system",
            payload_class="PROJECT",
            trace_ref=f"claim:{claim.claim_id}",
            detail={"event": "mapping_gaps", "gap_count": len(gaps),
                    "gaps": [g["ei_element_id"] for g in gaps]},
        ))
        return "FORMALIZED", candidate  # stays FORMALIZED; PROVING blocked until gap-ack

    return "FORMALIZED", candidate


def cmd_formalize(args, store: ArtifactStore) -> int:
    claim = store.load_claim(args.claim_id)
    _claim_state_guard(claim, {"ACCEPTED", "BLOCKED"}, "formalize")
    run_id, log = _new_run(args.events_dir)
    adapter = _make_adapter(run_id, log)
    state_after, candidate = formalize_claim(claim, store, log, run_id, adapter)
    claim.state = state_after
    claim.formal_rev = store.formal_revs(claim.claim_id)[-1]
    store.save_claim(claim)
    if candidate is not None:
        gaps = candidate.get("gaps") or []
        print(f"claim {claim.claim_id}: FORMALIZED (target theorem {candidate['target_theorem']})")
        if gaps:
            print(f"  MAPPING GAPS ({len(gaps)}): PROVING blocked until reviewed")
            for gap in gaps:
                print(f"    - {gap['ei_element_id']} ({gap['ei_element_kind']}): {gap.get('reason')}")
            print("  resolve with: `a3 gap-ack --claim-id ... --reviewer <id>` or revise the claim")
        else:
            print("  mapping report complete: no gaps")
    else:
        print(f"claim {claim.claim_id}: {state_after}")
    return 0


# ---------------------------------------------------------------------------
# gap-ack / axiom-approve (per-run reviewer records)
# ---------------------------------------------------------------------------


def cmd_gap_ack(args, store: ArtifactStore) -> int:
    claim = store.load_claim(args.claim_id)
    _claim_state_guard(claim, {"FORMALIZED"}, "gap-ack")
    reviewer = _reviewer_identity(args)
    run_id, log = _new_run(args.events_dir)
    formal = store.read_formal(claim.claim_id, claim.formal_rev)
    gaps = formal.get("gaps") or []
    if not gaps:
        print(f"claim {claim.claim_id}: no mapping gaps to acknowledge")
        return 0
    store.write_review_record(claim.claim_id, "gap", {
        "reviewer": reviewer, "notes": args.notes or "",
        "acknowledged_gap_ids": [g["ei_element_id"] for g in gaps],
        "event_ref": f"evt-{run_id}", "formal_rev": formal.get("revision"),
    })
    _emit(log, Event(
        event_type=EVENT_DIAGNOSTIC_RESULT,
        run_id=run_id, claim_id=claim.claim_id, source_component="a3-review",
        actor=reviewer, payload_class="PROJECT", trace_ref=f"claim:{claim.claim_id}",
        detail={"event": "gaps_acknowledged", "gap_count": len(gaps)},
    ))
    print(f"claim {claim.claim_id}: {len(gaps)} gaps acknowledged by {reviewer}; PROVING now allowed")
    return 0


def cmd_axiom_approve(args, store: ArtifactStore) -> int:
    claim = store.load_claim(args.claim_id)
    reviewer = _reviewer_identity(args)
    run_id, log = _new_run(args.events_dir)
    axioms = [a.strip() for a in args.axioms.split(",") if a.strip()]
    if not axioms:
        raise SystemExit("--axioms required (comma-separated list)")
    record = store.write_review_record(claim.claim_id, "axiom", {
        "reviewer": reviewer, "notes": args.notes or "",
        "approved_axioms": axioms, "event_ref": f"evt-{run_id}",
        "claim_revision": claim.revision,
    })
    _emit(log, Event(
        event_type=EVENT_DIAGNOSTIC_RESULT,
        run_id=run_id, claim_id=claim.claim_id, source_component="a3-review",
        actor=reviewer, payload_class="PROJECT", trace_ref=f"claim:{claim.claim_id}",
        detail={"event": "axiom_approval", "approved_axioms": axioms},
    ))
    print(f"claim {claim.claim_id}: axiom review record written ({record['digest'][:16]}…)")
    print(f"  approved: {', '.join(axioms)}")
    return 0


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------


def cmd_verify(args, store: ArtifactStore) -> int:
    claim = store.load_claim(args.claim_id)
    _claim_state_guard(claim, {"FORMALIZED", "FAILED", "BLOCKED"}, "verify")
    if claim.formal_rev is None:
        raise SystemExit(f"claim {claim.claim_id}: no formalization exists; run formalize first")
    run_id, log = _new_run(args.events_dir)

    formal = store.read_formal(claim.claim_id, claim.formal_rev)
    if formal.get("gaps") and not store.list_review_records(claim.claim_id, "gap"):
        raise SystemExit(f"claim {claim.claim_id}: mapping gaps unacknowledged — PROVING refused (run gap-ack first)")

    proof_path = Path(args.proof)
    if not proof_path.exists():
        raise SystemExit(f"proof file not found: {proof_path}")
    proof_source = proof_path.read_text(encoding="utf-8")

    target = formal.get("target_theorem", "")
    if not target:
        raise SystemExit(f"claim {claim.claim_id}: formalization has no target theorem; run formalize first")

    _state_event(log, run_id, claim.claim_id, claim.state, "PROVING", "system", "a3-verify",
                 detail={"target_theorem": target, "proof": str(proof_path)})

    axiom_records = store.list_review_records(claim.claim_id, "axiom")
    approved = frozenset(axiom_records[-1].get("approved_axioms", [])) if axiom_records else None

    record = verify_candidate(
        workspace_root=WORKSPACE,
        candidate_source=proof_source,
        theorem_name=target,
        run_id=run_id,
        claim_id=claim.claim_id,
        approved_axioms=approved,
        timeout_s=args.timeout,
    )

    # bundle inputs
    approval = store.list_review_records(claim.claim_id, "approval")[-1] if store.list_review_records(claim.claim_id, "approval") else {}
    axiom_rec = axiom_records[-1] if axiom_records else None
    ws_probe = probe_workspace(WORKSPACE)
    snapshots = {"lean_workspace": ws_probe.status.value}
    trace_refs = [f"claim:{claim.claim_id}", f"formal:{claim.claim_id}:r{formal.get('revision')}", f"run:{run_id}"]

    state_after = record.outcome  # VERIFIED | FAILED | BLOCKED
    reason_codes = (record.reason_code,) if record.reason_code else ()

    ei_artifact = store.read_ei(claim.claim_id, claim.accepted_ei_rev)
    bundle_id, bundle_path = build_bundle(
        store=store, claim=claim, ei_artifact=ei_artifact, formal_artifact=formal,
        proof_source=proof_source, verification=record.to_dict(),
        approval_record=approval, axiom_record=axiom_rec, trace_refs=trace_refs,
        capability_snapshots=snapshots, workspace_root=WORKSPACE,
        commands=[f"a3 verify --claim-id {claim.claim_id} --proof {args.proof}"],
    )

    # The bundle validator gates VERIFIED (gate3/05): a kernel-verified record
    # with an invalid bundle must NOT produce a VERIFIED claim state. Rebuild
    # the manifest so the failure is self-consistent.
    checks = validate_bundle(store, bundle_id, claim)
    if state_after == "VERIFIED" and not all(ok for _, ok, _ in checks):
        state_after = "FAILED"
        failing = [c[0] for c in checks if not c[1]]
        manifest = store.read_bundle_manifest(bundle_id)
        manifest["result"] = "FAILED"
        manifest["failure_reasons"] = ["bundle_validation_failed"]
        manifest["sanity_checks"]["bundle_failing_checks"] = failing
        (store.bundle_path(bundle_id) / "manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        reason_codes = ()
        print(f"  WARNING: kernel verified but bundle invalid: {failing} — state set to FAILED")

    _emit(log, Event(
        event_type=EVENT_VERIFICATION_COMPLETED,
        run_id=run_id, claim_id=claim.claim_id, state_before="PROVING", state_after=state_after,
        source_component="a3-verify", actor="verifier", reason_codes=reason_codes,
        payload_class="PROJECT", trace_ref=bundle_id, detail={"theorem": target},
    ))

    claim.state = state_after
    claim.current_bundle = bundle_id
    store.save_claim(claim)

    print(f"claim {claim.claim_id}: PROVING -> {state_after}" + (f" ({record.reason_code})" if record.reason_code else ""))
    print(f"  axioms used: {', '.join(record.axiom_list) or '(none)'}")
    if record.reason_code == REASON_SORRY_FOUND:
        print("  SORRY_FOUND: incomplete proof placeholder detected — never acceptable for VERIFIED")
    if record.reason_code == "AXIOM_VIOLATION":
        print(f"  unapproved axioms: {', '.join(record.detail.get('unapproved_axioms', []))}")
        print("  reviewer action: `a3 axiom-approve --claim-id ... --reviewer <id> --axioms <list>`, then verify again")
    if record.compile_ok and not record.reason_code:
        checks = validate_bundle(store, bundle_id, claim)
        print(f"  bundle: {bundle_path}")
        for item, ok, detail in checks:
            print(f"    [{('x' if ok else ' ')}] {item}: {detail}")
    return 0


# ---------------------------------------------------------------------------
# bundle / replay / status
# ---------------------------------------------------------------------------


def cmd_bundle(args, store: ArtifactStore) -> int:
    claim = store.load_claim(args.claim_id)
    if not claim.current_bundle:
        raise SystemExit(f"claim {claim.claim_id} has no bundle yet")
    checks = validate_bundle(store, claim.current_bundle, claim)
    ok = all(c[1] for c in checks)
    print(f"bundle {claim.current_bundle}: {'VALID' if ok else 'INVALID'} (11-item checklist)")
    for item, passed, detail in checks:
        print(f"  [{('x' if passed else ' ')}] {item}: {detail}")
    return 0 if ok else 1


def cmd_replay(args, store: ArtifactStore) -> int:
    if args.run_id:
        report = replay_run(Path(args.events_dir) / f"{args.run_id}.jsonl", store=store)
    elif args.claim_id:
        report = replay_claim(Path(args.events_dir), args.claim_id, store=store)
    else:
        raise SystemExit("--run-id or --claim-id required")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["replay_ok"] else 1


def cmd_status(args, store: ArtifactStore) -> int:
    claim = store.load_claim(args.claim_id)
    print(f"claim {claim.claim_id} r{claim.revision}: state={claim.state} class={claim.data_class}")
    print(f"  accepted_ei_rev={claim.accepted_ei_rev} formal_rev={claim.formal_rev} bundle={claim.current_bundle}")
    for kind in ("approval", "axiom", "gap"):
        records = store.list_review_records(claim.claim_id, kind)
        if records:
            print(f"  {kind} records: {len(records)} (latest {records[-1].get('digest', '')[:16]}…)")
    print(f"  claim digest: {store.read_json(store.claim_path(claim.claim_id))['digest'][:16]}…")
    return 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="leanecon-a3", description="LeanEcon v4 A3 minimal verified workflow")
    parser.add_argument("--store", default=str(DEFAULT_ROOT), help="artifact store root (default artifacts/local/a3)")
    parser.add_argument("--events-dir", default=str(EVENTS_DIR), help="event log directory")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("ingest", help="create a claim revision (DRAFT)")
    p.add_argument("--claim-id", required=True)
    p.add_argument("--claim-text", default="")
    p.add_argument("--class", dest="claim_class", default="PROJECT", help="PUBLIC or PROJECT (RESTRICTED hard-denied)")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("interpret", help="run interpretation (live provider call)")
    p.add_argument("--claim-id", required=True)
    p.set_defaults(func=cmd_interpret)

    p = sub.add_parser("review", help="reviewer decision: approve | reject")
    p.add_argument("--claim-id", required=True)
    p.add_argument("--decision", required=True, choices=["approve", "reject"])
    p.add_argument("--reviewer", default="")
    p.add_argument("--acknowledge-none-noted", action="store_true", help="required when EI found no ambiguity")
    p.add_argument("--reason", default="", help="reject reason code (default USER_REJECTED)")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("formalize", help="run formalization (live provider call)")
    p.add_argument("--claim-id", required=True)
    p.set_defaults(func=cmd_formalize)

    p = sub.add_parser("gap-ack", help="reviewer acknowledges mapping gaps (per-run reviewer record)")
    p.add_argument("--claim-id", required=True)
    p.add_argument("--reviewer", default="")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_gap_ack)

    p = sub.add_parser("axiom-approve", help="reviewer approves the axiom list (per-run reviewer record)")
    p.add_argument("--claim-id", required=True)
    p.add_argument("--reviewer", default="")
    p.add_argument("--axioms", required=True, help="comma-separated axiom names")
    p.add_argument("--notes", default="")
    p.set_defaults(func=cmd_axiom_approve)

    p = sub.add_parser("verify", help="proof input -> PROVING -> VERIFIED|FAILED|BLOCKED + bundle")
    p.add_argument("--claim-id", required=True)
    p.add_argument("--proof", required=True, help="path to the Lean proof fixture")
    p.add_argument("--timeout", type=int, default=600)
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("bundle", help="re-validate the current bundle (11-item checklist)")
    p.add_argument("--claim-id", required=True)
    p.set_defaults(func=cmd_bundle)

    p = sub.add_parser("replay", help="trace replay (deterministic validation)")
    p.add_argument("--run-id", default="")
    p.add_argument("--claim-id", default="")
    p.set_defaults(func=cmd_replay)

    p = sub.add_parser("status", help="claim state and artifact references")
    p.add_argument("--claim-id", required=True)
    p.set_defaults(func=cmd_status)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    store = ArtifactStore(args.store)
    return args.func(args, store)


if __name__ == "__main__":
    raise SystemExit(main())
