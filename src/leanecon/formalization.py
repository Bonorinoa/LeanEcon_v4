"""Formalization service (docs/gate5/a3-design.md §4).

Turns the ACCEPTED interpretation into a candidate Lean statement plus a
mapping report (EI element -> Mathlib identifier, Core identifier, glossary
term, or A3-local scaffolding definition). The mapping report is required
before PROVING (locked EI decision 3): material elements must be mapped or
explicitly flagged as unmapped gaps; unacknowledged gaps block PROVING
entry.

Core exists since the P2 batch (2026-08-06): economics vocabulary may map
to promoted LeanEcon.Core declarations via `core` rows (fully-qualified
identifiers only, D1) or to clearly-labeled, namespace-scoped A3-local
scaffolding (D4). Nothing here invents definitions silently.
"""

from __future__ import annotations

import json
import re

#: Element kinds that must be mapped (or flagged unmapped) before PROVING.
MATERIAL_KINDS = {"object", "assumption", "quantifier", "conclusion", "solution", "definition"}
#: Expository kinds may be deferred with a note.
DEFERRABLE_KINDS = {"context", "note"}

MAPPING_STATUSES = ("mapped", "unmapped", "deferred")
MAPPING_KINDS = ("mathlib", "core", "local_definition", "glossary_term", "none")

#: D1 (a3-core-design.md §4): a ``core`` row must carry the FULLY-QUALIFIED
#: Lean identifier — ``LeanEcon.Core.<Area>.<name>`` (e.g.
#: ``LeanEcon.Core.Choice.attainableSet``), never a bare name. The namespace
#: skeleton requires an Area component (Core declarations live under
#: ``LeanEcon.Core.<Area>``), so at least TWO dotted components after the
#: ``LeanEcon.Core.`` prefix are required.
CORE_IDENTIFIER_RE = re.compile(
    r"^LeanEcon\.Core\.[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$"
)

#: Bare-name → fully-qualified Core id, derived from the pinned workspace
#: (lean_workspace/LeanEcon/Core/*.lean). Used by
#: ``sanitize_core_mapping_rows`` to promote a bare Core name in a ``core``
#: mapping row to its FQ form instead of rejecting the whole draft (D1).
KNOWN_CORE_NAMES: dict[str, str] = {
    "attainableSet": "LeanEcon.Core.Choice.attainableSet",
    "budgetSet": "LeanEcon.Core.Constraints.budgetSet",
    "budgetSetEndowment": "LeanEcon.Core.Constraints.budgetSetEndowment",
    "marketClearing": "LeanEcon.Core.Equilibrium.marketClearing",
    "competitiveEquilibrium": "LeanEcon.Core.Equilibrium.competitiveEquilibrium",
    "paretoEfficiency": "LeanEcon.Core.Equilibrium.paretoEfficiency",
    "weakPreference": "LeanEcon.Core.Preferences.weakPreference",
    "bundle": "LeanEcon.Core.Primitives.bundle",
    "utility": "LeanEcon.Core.Utility.utility",
    "strictlyIncreasing": "LeanEcon.Core.Utility.strictlyIncreasing",
}


def material_element_ids(ei: dict) -> list[tuple[str, str]]:
    """Return [(element_id, kind)] for every material element of the EI.

    Element ids are stable: objects use their ``id``; other elements use
    ``kind:index`` references. The formalizer is instructed to use these.
    """
    elements: list[tuple[str, str]] = []
    for obj in ei.get("objects", []) or []:
        elements.append((obj.get("id", "?"), "object"))
    for i, _ in enumerate(ei.get("assumptions", {}).get("proposed", []) or []):
        elements.append((f"assumption:{i}", "assumption"))
    for i, _ in enumerate(ei.get("quantifiers", []) or []):
        elements.append((f"quantifier:{i}", "quantifier"))
    elements.append(("conclusion", "conclusion"))
    if (ei.get("conclusion") or {}).get("solution_or_equilibrium_concept"):
        elements.append(("solution_concept", "solution"))
    for i, _ in enumerate(ei.get("context", {}).get("definitions", []) or []):
        elements.append((f"definition:{i}", "definition"))
    return elements


def validate_mapping_report(report: list[dict], ei: dict) -> tuple[list[str], list[dict]]:
    """Validate report shape; return (problems, gaps).

    A gap is a material element with status ``unmapped`` (or a missing row).
    Deferred rows are allowed only for non-material kinds.
    """
    problems: list[str] = []
    if not isinstance(report, list):
        return ["mapping_report must be a list"], []

    by_id = {row.get("ei_element_id"): row for row in report if isinstance(row, dict)}
    for row in report:
        if not isinstance(row, dict):
            problems.append("mapping report rows must be objects")
            continue
        if row.get("status") not in MAPPING_STATUSES:
            problems.append(f"row {row.get('ei_element_id')}: invalid status {row.get('status')!r}")
        if row.get("status") == "mapped" and row.get("mapping_kind") not in MAPPING_KINDS:
            problems.append(
                f"row {row.get('ei_element_id')}: invalid mapping_kind {row.get('mapping_kind')!r}"
            )
        if row.get("status") == "mapped" and row.get("mapping_kind") == "core":
            # D1: core rows must resolve as written — fully-qualified
            # LeanEcon.Core identifier, no bare names (eliminates open-based
            # shadowing ambiguity; a3-core-design.md §4).
            ident = row.get("lean_identifier") or ""
            if not CORE_IDENTIFIER_RE.match(ident):
                problems.append(
                    f"row {row.get('ei_element_id')}: core mapping requires a fully-qualified "
                    f"LeanEcon.Core identifier (e.g. 'LeanEcon.Core.Choice.attainableSet'), got {ident!r}"
                )
        if row.get("status") == "deferred" and row.get("ei_element_kind") not in DEFERRABLE_KINDS:
            problems.append(f"row {row.get('ei_element_id')}: material element may not be deferred")

    gaps: list[dict] = []
    for element_id, kind in material_element_ids(ei):
        row = by_id.get(element_id)
        if row is None:
            gaps.append(
                {
                    "ei_element_id": element_id,
                    "ei_element_kind": kind,
                    "reason": "missing mapping row",
                }
            )
        elif row.get("status") == "unmapped":
            gaps.append(
                {
                    "ei_element_id": element_id,
                    "ei_element_kind": kind,
                    "reason": row.get("note") or "unmapped",
                }
            )
        elif row.get("status") not in ("mapped",):
            problems.append(
                f"row {element_id}: material {kind} must be mapped or unmapped, got {row.get('status')!r}"
            )
    return problems, gaps


def _sanitize_namespace(claim_id: str) -> str:
    """Lean namespace segment: only letters, digits, _ and '.'. Claim ids like
    'v3h2-A' or 'v3p1-A' contain '-' which is not a valid Lean identifier
    character — the scaffold namespace must use a sanitized form."""
    cleaned = "".join(ch if ch.isalnum() or ch in "._" else "_" for ch in claim_id)
    cleaned = cleaned.strip(".")
    return cleaned or "claim"


def formalize_prompt(ei: dict) -> str:
    """Prompt for the formalize capability (MVP model per adapter config).

    Hardened after the 2026-08-06 walkthrough: the live formalizer produced
    vacuous tautologies (c1), an invalid `[Set α]` binder (c2), a `sorry`
    proof body (c3), and non-canonical mapping ids. The rules below make each
    failure mode an explicit instruction; the static validator
    (validate_statement_text) and the compile probe back it up.
    """
    return (
        "You are the formalization service of a kernel-checked economics system. "
        "Given the ACCEPTED interpretation below (JSON), write a Lean 4 formal "
        "statement in the pinned Mathlib workspace.\n\n"
        "Rules:\n"
        '- Output ONLY a JSON object: {"statement": <theorem signature as Lean text, '
        "e.g. 'theorem name (args) : proposition' — signature ONLY, no proof body>, "
        '"target_theorem": <theorem name>, "mapping_report": [...]}.\\n'
        "- FORMAT EXEMPLAR (follow this shape exactly):\\n"
        "  GOOD: `theorem budget_binds {ι : Type*} [Fintype ι] (p : ι → ℝ) "
        "(x : ι → ℝ) (hp : ∀ i, p i > 0) (hx : ∀ g, x g ∈ budgetSet p e) : "
        "∑ g, p g * x g = ∑ g, p g * e g` — ends at the conclusion, no `:=`.\\n"
        "  BAD:  `theorem t ... : P := by exact ...` or `... := sorry` — proof "
        "bodies are REJECTED before review.\\n"
        "- HARD: the statement must be a SIGNATURE ONLY. It must end at the "
        "conclusion: `... : <conclusion>` with NO `:=` and NO `by ...` — do not "
        "attach a proof body. Do not use sorry/admit anywhere.\n"
        "- HARD: the statement must be well-formed Lean that compiles under "
        "`import Mathlib`. Typeclass binders like `[Set α]` are INVALID — use "
        "`[Fintype α]`, `[LinearOrder α]` etc. only for genuine typeclasses.\n"
        "- HARD: finite goods/agents must be `Finset` (or `[Fintype]` on a Type) "
        "so `∑` has a summation instance. Do not write `∑ g,` over a bare Type. "
        "Do not apply `StrictMono` to a utility on bundles — state monotonicity "
        "as an explicit hypothesis `∀ x y, …`. Prefer `Finset.sum` over set "
        "comprehensions that Lean cannot elaborate.\n"
        "- HARD: no tautologies and no vacuous theorems. The conclusion must be "
        "a substantive proposition about the claim, NOT identical to any "
        "hypothesis, and not derivable from a hypothesis alone. If the claim "
        "is a property claim (e.g. 'weak preference is transitive'), state the "
        "property as the conclusion with the objects as parameters.\n"
        "- Every hypothesis you list in the signature must actually appear in "
        "the signature, and every parameter must be USED in the statement. Do "
        "not reference hypotheses that are absent.\n"
        "- The statement may define small A3-local scaffolding definitions first "
        "(clearly commented 'A3-local scaffolding, not LeanEcon Core'). "
        "Scaffolding MUST be namespace-scoped: put it inside "
        f"'namespace A3Scaffolding.{_sanitize_namespace(str(ei.get('claim_id') or 'claim'))} ... end' "
        "— never at the root "
        "namespace (root declarations can shadow Mathlib identifiers within the file). "
        "Use only letters, digits, dots and underscores in the namespace — never '-' "
        "or other punctuation (claim ids like 'v3p1-A' must become e.g. 'v3p1_A').\n"
        "- The mapping_report must contain one row per material EI element with "
        "fields: ei_element_id, ei_element_kind, lean_identifier, mapping_kind "
        "(mathlib|core|glossary_term|local_definition), status (mapped|unmapped|deferred), "
        "provenance, note. A 'core' row REQUIRES the fully-qualified Lean identifier "
        "(e.g. 'LeanEcon.Core.Choice.attainableSet') — never a bare name; the row "
        "must resolve as written. Element ids MUST be used EXACTLY as given: object ids "
        "from the interpretation (e.g. 'u', 'x', 'preferences' — never 'object:u'), "
        "'assumption:<i>', 'quantifier:<i>', 'conclusion', 'solution_concept', "
        "'definition:<i>'. Do not rename or prefix them.\n"
        "- HARD (D1 discipline): 'core' is ONLY for genuine LeanEcon.Core vocabulary "
        "(e.g. LeanEcon.Core.Constraints.budgetSet, LeanEcon.Core.Constraints.budgetSetEndowment, "
        "LeanEcon.Core.Choice.attainableSet, LeanEcon.Core.Equilibrium.marketClearing, "
        "LeanEcon.Core.Equilibrium.competitiveEquilibrium, LeanEcon.Core.Equilibrium.paretoEfficiency, "
        "LeanEcon.Core.Utility.strictlyIncreasing, LeanEcon.Core.Primitives.bundle, "
        "LeanEcon.Core.Preferences.weakPreference). THEOREM BINDERS, HYPOTHESIS NAMES "
        "(p, x, e, u, h, hx, hp, goods, prices...) and ordinary Mathlib types (ℝ, Finset, ∀) "
        "are NEVER core rows — use mapping_kind 'local_definition' (binder/lemma) or "
        "'mathlib' (Mathlib identifier) for them. When the statement references Core, "
        "add the matching 'import LeanEcon.Core.<Area>' line at the top of the statement.\n"
        "- If an element cannot be mapped, mark it unmapped with a note — never "
        "invent a definition to hide the gap.\n\n"
        "Accepted interpretation (JSON):\n"
        f"{json.dumps(ei, indent=1, sort_keys=True)}"
    )


_SORRY_TOKENS = ("sorry", "admit")

#: Declaration keywords that introduce A3-local scaffolding names at the
#: current namespace. `theorem` is deliberately absent — the candidate's
#: target theorem is not scaffolding (D4).
_SCAFFOLDING_KEYWORDS = ("abbrev", "def", "structure", "class", "inductive", "instance")

#: Declaration keywords tracked for the proof-body check (P4 finding: the
#: old `\s:=` regex false-positived on scaffolding definitions like
#: `abbrev Bundle := ℝ`; only THEOREM-STYLE declarations are signature-only).
_DECL_KEYWORDS = (
    "theorem",
    "lemma",
    "example",
    "axiom",
    "def",
    "abbrev",
    "structure",
    "class",
    "inductive",
    "instance",
)
_SIGNATURE_ONLY = ("theorem", "lemma", "example", "axiom")


def _decl_head(line: str) -> str | None:
    """Declaration keyword at the start of a stripped line, or None.

    Tolerates ``noncomputable``/``private``/``protected`` prefixes and
    ``@[attr]`` groups so a ``theorem``/``def`` line is still recognized.
    """
    while True:
        if line.startswith(("noncomputable ", "private ", "protected ")):
            line = line.split(" ", 1)[1].lstrip()
        elif line.startswith("@["):
            close = line.find("]")
            if close == -1:
                return None
            line = line[close + 1 :].lstrip()
        else:
            break
    for kw in _DECL_KEYWORDS:
        if line.startswith(kw) and (len(line) == len(kw) or line[len(kw)] in " \t"):
            return kw
    return None


def validate_statement_text(statement: str) -> list[str]:
    """Static contract checks on the candidate statement. Returns problems.

    Hard failures (the run is rejected with PROVIDER_INVALID_OUTPUT):
    - sorry/admit anywhere in the statement;
    - a proof body attached to a THEOREM-STYLE declaration (``theorem`` /
      ``lemma`` / ``example`` / ``axiom`` ... : P := ...) — the prompt
      requires a bare signature. Definitional ``:=`` on scaffolding
      declarations (``abbrev Bundle := ℝ``, ``def f ... := ...``) is
      legitimate syntax and NOT a proof body (P4 finding; D4 namespaced
      scaffolding relies on this distinction).

    These mirror the walkthrough's c2/c3 failure modes. The kernel compile
    probe (verifier.probe_statement_compiles) additionally records whether the
    statement compiles — an evaluation signal, not a blocker.
    """
    problems: list[str] = []
    lowered = statement.lower()
    for token in _SORRY_TOKENS:
        if token in lowered:
            problems.append(f"statement contains '{token}' (contract violation)")
    current_decl: str | None = None
    for lineno, raw in enumerate(statement.splitlines(), start=1):
        if not raw.strip():
            continue
        head = _decl_head(raw.strip())
        if head is not None:
            current_decl = head
            if head in _SIGNATURE_ONLY and ":=" in raw:
                problems.append(
                    f"line {lineno}: {head} '{raw.strip()[:70]}' carries a proof body "
                    "('... :='); output the signature only"
                )
        elif current_decl in _SIGNATURE_ONLY and ":=" in raw:
            # continuation of a wrapped theorem-style declaration
            problems.append(
                f"line {lineno}: continuation of a theorem-style declaration carries a proof body ('... :=')"
            )
    return problems


def validate_scaffolding_namespace(statement: str) -> list[str]:
    """D4 (a3-core-design.md §4): A3-local scaffolding must be namespace-scoped.

    Flags root-namespace declarations ('abbrev Bundle := ...' outside any
    'namespace ...'), which can shadow Mathlib identifiers within the
    candidate file. The target theorem itself ('theorem ...') is never
    scaffolding and is not flagged. Namespace depth is tracked lexically:
    'namespace X' increments, 'end'/'end X' decrements; a declaration at
    depth 0 is a root-namespace declaration.

    Hard failures (the run is rejected with PROVIDER_INVALID_OUTPUT): the
    prompt requires scaffolding inside 'namespace A3Scaffolding.<claim_id>'.
    The kernel check at verify time remains the authoritative layer; this
    static check removes the confound EARLIER (fwt1 lesson: reviewer proofs
    and candidates used root 'abbrev Bundle').
    """
    problems: list[str] = []
    depth = 0
    for lineno, raw in enumerate(statement.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(("--", "/-")) or line.startswith("import"):
            continue
        if line.startswith(("namespace ", "namespace\t")):
            depth += 1
            continue
        if line.startswith("end"):
            depth = max(0, depth - 1)
            continue
        if depth == 0:
            for kw in _SCAFFOLDING_KEYWORDS:
                if line.startswith(kw) and (len(line) == len(kw) or line[len(kw)] in " \t"):
                    problems.append(
                        f"line {lineno}: root-namespace declaration '{line[:70]}' — "
                        "A3-local scaffolding must live in 'namespace A3Scaffolding.<claim>' (D4)"
                    )
                    break
    return problems


def sanitize_signature_draft(statement: str) -> tuple[str, list[str]]:
    """Mechanically repair the known signature-only violations in a draft.

    v4 intelligence sprint (Day 2 lever): the spent-set inventory showed
    the loop burning its whole budget repeating IDENTICAL rejects
    (v3h2-A: the same ``:=`` continuation problem on attempts 1-3).
    The feedback text alone did not change behavior, so the repair is
    now mechanical and happens BEFORE the audit:

    1. Cut a theorem-style proof body: everything from the first
       declaration-aware `` :=`` on a signature-only declaration
       (theorem/lemma/example/axiom) onward.
    2. Remove any remaining ``sorry``/``admit`` tokens (bodies only;
       belt-and-braces for inline cases).
    3. Re-home root-namespace ``def``/``abbrev`` scaffolding under
       ``namespace A3Scaffolding.<claim_id> ... end`` (D4).

    Returns ``(repaired_statement, notes)``. The audit gate is NOT
    bypassed: whatever survives still goes through
    ``validate_statement_text`` + ``validate_scaffolding_namespace``,
    then the kernel probe and the reviewer. Notes are appended to the
    revision feedback so the model sees what was fixed mechanically.
    """
    lines = statement.splitlines()
    out: list[str] = []
    notes: list[str] = []
    current_decl: str | None = None
    cut_done = False
    in_body = False

    # Pass 1: strip proof bodies on signature-only declarations.
    for raw in lines:
        stripped = raw.strip()
        head = _decl_head(stripped)
        structural = stripped.startswith(("import ", "import\t", "namespace ", "end", "--", "/-"))
        if in_body:
            if head is not None or structural:
                in_body = False
            else:
                continue  # still inside the discarded proof body
        if head is not None:
            current_decl = head
        triggered = (
            not cut_done
            and not stripped.startswith("import")
            and current_decl in _SIGNATURE_ONLY
            and (" := " in raw.rstrip() or raw.rstrip().endswith(":="))
        )
        if triggered:
            idx = raw.find(" :=")
            out.append(raw[:idx].rstrip())
            notes.append(
                "stripped a theorem-style proof body ('... := ...'); "
                "the statement must be a bare signature"
            )
            cut_done = True
            current_decl = None
            in_body = True
            continue
        out.append(raw)
    repaired = "\n".join(out)
    if statement.endswith("\n") and repaired and not repaired.endswith("\n"):
        repaired += "\n"

    # Pass 2: remove residual sorry/admit tokens.
    lowered = repaired.lower()
    for token in _SORRY_TOKENS:
        if token in lowered:
            repaired = re.sub(rf"\b{token}\b", "", repaired)
            lowered = repaired.lower()
            notes.append(f"removed '{token}' token; sorry/admit are contract violations")

    # Pass 3: re-home root-namespace scaffolding under A3Scaffolding.
    ns_problems = validate_scaffolding_namespace(repaired)
    if ns_problems:
        claim_ns = "A3Scaffolding.repaired"
        scaffold_lines: list[str] = []
        body_lines: list[str] = []
        depth = 0
        for raw in repaired.splitlines():
            line = raw.strip()
            is_scaffold_head = any(
                line.startswith(kw) and (len(line) == len(kw) or line[len(kw)] in " \t")
                for kw in _SCAFFOLDING_KEYWORDS
            )
            if depth == 0 and is_scaffold_head:
                scaffold_lines.append(raw)
                continue
            if line.startswith(("namespace ", "end")):
                if depth > 0 or not line.startswith("end"):
                    body_lines.append(raw)
                depth += 1 if not line.startswith("end") else -1
                continue
            body_lines.append(raw)
        if scaffold_lines:
            block = [f"namespace {claim_ns}", *scaffold_lines, f"end {claim_ns}"]
            rebuilt: list[str] = []
            inserted = False
            for raw in body_lines:
                if not inserted and _decl_head(raw.strip()) in _SIGNATURE_ONLY:
                    rebuilt.extend(block)
                    inserted = True
                rebuilt.append(raw)
            if not inserted:
                rebuilt.extend(block)
            repaired = "\n".join(rebuilt)
            notes.append(f"moved root-namespace scaffolding under 'namespace {claim_ns}' (D4)")

    return repaired, notes


def sanitize_core_mapping_rows(
    mapping_report: list[dict],
) -> tuple[list[dict], list[str]]:
    """Mechanically repair D1 violations in ``core`` mapping rows.

    v4 lever extension (Day 3): the smoke run showed the surviving killer
    class is core rows whose ``lean_identifier`` is not a bare
    fully-qualified Core id — the model writes applications
    (``attainableSet p e``) or bare names (``StrictMono u``). Repair:

    1. Strip an application suffix: ``Name args...`` → first token.
    2. If the remaining token is a known Core declaration, promote it to
       its FQ ``LeanEcon.Core.<Area>.<name>`` form.
    3. If it is NOT known Core vocabulary, downgrade the row to
       ``local_definition`` — honest: that identifier is not Core.

    Returns ``(repaired_report, notes)``. The audit still runs after this;
    anything unfixable is rejected exactly as before.
    """
    repaired: list[dict] = []
    notes: list[str] = []
    for row in mapping_report:
        if row.get("mapping_kind") != "core":
            repaired.append(row)
            continue
        ident = str(row.get("lean_identifier") or "").strip()
        if CORE_IDENTIFIER_RE.match(ident):
            repaired.append(row)
            continue
        new_row = dict(row)
        # 1. application suffix: keep the head term only
        head = ident.split(" ", 1)[0].strip()
        # strip leading universal/existential binder noise if any
        head = head.lstrip("∀∃").strip()
        if head in KNOWN_CORE_NAMES:
            fq = KNOWN_CORE_NAMES[head]
            new_row["lean_identifier"] = fq
            note = (
                f"core row '{row.get('ei_element_id')}': trimmed "
                f"'{ident}' and promoted bare name to '{fq}' (D1)"
            )
            notes.append(note)
            new_row["note"] = ((new_row.get("note") or "") + f" [repaired: {note}]").strip()
            repaired.append(new_row)
            continue
        # 2. not known Core vocabulary → honest downgrade
        new_row["mapping_kind"] = "local_definition"
        new_row["lean_identifier"] = head or ident
        note = (
            f"core row '{row.get('ei_element_id')}': '{ident}' is not known "
            "Core vocabulary; downgraded to local_definition (D1)"
        )
        notes.append(note)
        new_row["note"] = ((new_row.get("note") or "") + f" [repaired: {note}]").strip()
        repaired.append(new_row)
    return repaired, notes


def vacuity_warning(statement: str) -> str | None:
    """Heuristic: does the conclusion restate a hypothesis (vacuous/tautological)?

    Extracts the text after the LAST ``:`` (the conclusion) and checks whether
    a normalized form of it also appears in the hypothesis region. A warning
    only — the reviewer decides; the kernel arbitrates.
    """
    colon = statement.rfind(":")
    if colon == -1:
        return None
    conclusion = statement[colon + 1 :].strip().rstrip(".")
    if not conclusion:
        return None
    hypothesis_region = statement[:colon]

    def norm(value: str) -> str:
        return re.sub(r"\s+", "", value)

    if norm(conclusion) in norm(hypothesis_region):
        return f"conclusion restates a hypothesis (potential vacuity): '{conclusion[:80]}'"
    return None


def classify_gaps(gaps: list[dict], report: list[dict]) -> list[dict]:
    """Annotate missing-row gaps: id-scheme deviation vs genuinely missing.

    The live formalizer sometimes prefixed canonical ids ('object:u' instead
    of 'u'). A row whose id is '<anything>:<canonical>' (or '<kind>:<canonical>')
    demonstrably covers the element under a non-compliant id — an evaluation
    signal about id discipline, not a coverage gap. Anything else is
    genuinely missing. Unmapped-status gaps keep their reason unchanged.
    """
    row_ids = {str(row.get("ei_element_id", "")) for row in report if isinstance(row, dict)}
    classified: list[dict] = []
    for gap in gaps:
        gap = dict(gap)
        cid = str(gap["ei_element_id"])
        if gap.get("reason") == "missing mapping row":
            deviation = any(
                rid != cid and (rid.endswith(":" + cid) or rid == f"{gap['ei_element_kind']}:{cid}")
                for rid in row_ids
            )
            gap["classification"] = "id_scheme_deviation" if deviation else "genuinely_missing"
        else:
            gap["classification"] = "unmapped_with_note"
        classified.append(gap)
    return classified


def parse_formalize_response(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"formalize response is not valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("formalize response must be a JSON object")
    for key in ("statement", "target_theorem", "mapping_report"):
        if key not in parsed:
            raise ValueError(f"formalize response missing key: {key}")
    if not isinstance(parsed["mapping_report"], list):
        raise ValueError("formalize mapping_report must be a list")
    return parsed
