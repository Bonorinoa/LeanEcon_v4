"""L1 probe-in-loop repair directives (Phase 2, DECISION_LOG 51/D2).

When a formalize attempt is audit-clean but the compile probe fails,
the next attempt's feedback block gains one deterministic Diagnosis
line: the classified failure (``eval_formalizer.classify_probe_failure``)
plus a static directive naming the relevant Lean fact. The directive
table below is PRINCIPLED and total over the classifier's outputs; the
wording of the surrounding block is the HEURISTIC part. Nothing here
rewrites statements mechanically — binder semantics are not safe to
transform blindly, so binders are *explained*, never edited.

The revision budget is untouched (D2): diagnosis rides the existing
MAX_REVISION_ATTEMPTS loop.

Attribution: Hermes Agent (Nous Research) under CTO direction.
CTO remains the sole semantic approver.
"""

from __future__ import annotations

from typing import Any

from leanecon.eval_formalizer import classify_probe_failure

#: Frozen by tests: probe repair consumes the normal revision budget.
MAX_REVISION_ATTEMPTS_UNCHANGED = 3

#: Header used by a3_runner._revision_feedback_block — re-exported here
#: so tests can pin the shared string in one place.
REVISION_FEEDBACK_HEADER = (
    "Prior kernel/static feedback from earlier attempts in this formalize call."
)

#: Static class → Lean-fact directives. Total over classify_probe_failure
#: outputs. `clean_or_no_signal` and `sorry` carry no directive: there is
#: nothing actionable (no signal) or nothing to want (sorry never passes).
DIRECTIVE_FOR_CLASS: dict[str, str] = {
    "clean_or_no_signal": "",
    "unknown_identifier": (
        "Diagnosis (elaboration): unknown identifier. Every LeanEcon.Core "
        "name must appear fully qualified as written (e.g. "
        "`LeanEcon.Core.Choice.attainableSet`) or be imported; bare names "
        "do not resolve. Check spelling against the mapping_report ids."
    ),
    "binder_annotation": (
        "Diagnosis (elaboration): invalid binder annotation — the named type "
        "is not a typeclass. `[Set α]`, `[Type]` etc. are INVALID instance "
        "binders; use genuine typeclasses (`[Fintype α]`, `[LinearOrder α]`, "
        "`[Inhabited α]`) only where an instance exists, and pass sets as "
        "plain parameters `(s : Set α)` instead."
    ),
    "ambiguity": (
        "Diagnosis (elaboration): ambiguous notation / metavariable type. "
        "Annotate the ambiguous term with its intended type explicitly "
        "(e.g. `(p : ι → ℝ)` rather than leaving `p`'s type to inference), "
        "and avoid subset/notation sugar on unresolved types."
    ),
    "instance_synthesis": (
        "Diagnosis (elaboration): instance synthesis failed. Provide the "
        "missing instance as an explicit binder argument (`[inst : Fintype ι]`) "
        "or restrict the claim's objects so a Mathlib instance applies."
    ),
    "type_mismatch": (
        "Diagnosis (elaboration): type mismatch. Re-check each hypothesis's "
        "stated type against how it is used in the conclusion; align bundle/"
        "goods index types (`ι → ℝ` vs `Fin ι → ℝ`) before adjusting the "
        "proposition itself."
    ),
    "unknown_universe": (
        "Diagnosis (elaboration): unknown universe level. Declare universe "
        "variables explicitly (`universe u`) or use concrete universes."
    ),
    "recursion_depth": (
        "Diagnosis (elaboration): maximum recursion depth exceeded during "
        "elaboration. Simplify the statement — reduce nested notation, split "
        "auxiliary definitions into A3-local scaffolding under the required "
        "namespace."
    ),
    "syntax": (
        "Diagnosis (elaboration): Lean syntax error. Fix at the exact reported "
        "position first; common causes for this pipeline are `:=` proof bodies "
        "(forbidden — signature only), non-ASCII lookalikes, and misplaced "
        "quantifier parentheses."
    ),
    "sorry": "",
    "unclassified": (
        "Diagnosis (elaboration): kernel rejected the statement with an error "
        "outside the known classes. Quote the full stderr verbatim in your "
        "revision reasoning; do not guess a fix class."
    ),
}


def diagnose(feedback: dict[str, Any]) -> str | None:
    """One directive line for probe-FAILED feedback; None otherwise.

    Contract (tests/test_probe_repair.py):
    - static_problems present → None (audit path unchanged);
    - no probe signal or probe compiled → None;
    - probe failed → DIRECTIVE_FOR_CLASS[classify(stderr)], which for
      `sorry` yields the table's empty string surfaced as a short
      refusal line.
    """
    if list(feedback.get("static_problems") or []):
        return None
    if not feedback.get("probe_compiles") is False:
        return None
    klass = classify_probe_failure(feedback.get("probe_stderr"))
    directive = DIRECTIVE_FOR_CLASS[klass]
    if not directive:
        if klass == "clean_or_no_signal":
            return (
                "Diagnosis (elaboration): the kernel rejected the draft but "
                "captured no error text. Treat the statement as unverified "
                "structure: re-check declaration headers and syntax before "
                "resubmitting."
            )
        # sorry-carrying compiles: compile ≠ pass, nothing to direct.
        return (
            "Diagnosis (elaboration): the draft compiled but uses `sorry`. "
            "Compile is not a pass; produce a sorry-free signature-only draft."
        )
    stderr = (feedback.get("probe_stderr") or "").strip()
    position = ""
    for token in stderr.split():
        if ".lean:" in token:
            position = f" Reported at {token.rstrip(':')}."
            break
    return f"{directive}{position}"


def revision_feedback_block(history: list[dict[str, Any]]) -> str:
    """Runner-shaped feedback block: verbatim attempts + optional Diagnosis.

    Mirrors ``a3_runner._revision_feedback_block`` byte-for-byte when no
    failed probe exists in the history (same header lines, blank line
    after every attempt), and appends a final ``Diagnosis`` section
    derived from the LAST feedback item when it carries a failed probe.
    """
    lines = [
        REVISION_FEEDBACK_HEADER,
        "Revise the statement. Do not repeat the same contract violations.",
        "",
    ]
    for index, item in enumerate(history, start=1):
        lines.append(f"Attempt {index}:")
        lines.append(f"  draft: {item.get('draft', '')}")
        problems = list(item.get("static_problems") or [])
        if problems:
            lines.append("  static_problems:")
            for problem in problems:
                lines.append(f"    - {problem}")
        stderr = item.get("probe_stderr") or ""
        if stderr:
            lines.append(f"  probe_stderr: {stderr}")
        lines.append("")
    last = history[-1] if history else None
    diagnosis = diagnose(last) if last is not None else None
    if diagnosis:
        lines.append(diagnosis)
    return "\n".join(lines)
