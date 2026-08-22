"""Proof-skeleton drafting assist (v2 Phase 3).

Per INIT_V2.md Phase 3: the model drafts an explicit have-chain proof
skeleton with clearly marked gaps; the reviewer refines it into the
kernel-passing proof. This module is the CONTRACT + MEASUREMENT layer:

- ``validate_skeleton`` parses a candidate skeleton and enforces the
  skeleton contract (structure, explicit annotated gaps, no smuggled
  tactic bodies);
- ``refined_proof_ok`` mirrors the verifier's contamination scan (a
  refined proof must be free of sorry/admit);
- ``skeleton_edit_distance`` measures reviewer delta (lines changed from
  model skeleton to the reviewer's refined proof) for the
  edit-distance / time-to-VERIFIED gate.

A skeleton with unresolved gaps MUST NOT proceed to verify — it would
fail the kernel sorryAx audit, by design. This module adds no bypass:
the verifier's kernel axiom audit remains the only pass gate.

Smuggling risk (B2 spike, 2026-08-08): auto-tactic bodies (aesop, simp,
trivial, exact?, apply?, omega, ...) can fabricate sorry bodies with exit
0. A have-step whose body is auto-tactic soup with NO gap annotation is
flagged as a contract violation — the reviewer must either fill it with a
real proof or mark it as a gap.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

#: Tactic soup that can fabricate sorry bodies with exit 0 (B2 spike,
#: 2026-08-08). A have-step body made of these with no gap annotation is
#: a smuggling risk and must be flagged.
_AUTO_TACTICS = (
    "aesop",
    "simp",
    "trivial",
    "exact?",
    "apply?",
    "omega",
    "linarith",
    "nlinarith",
    "ring_nf",
    "norm_num",
    "first",
    "solve_by_elim",
    "tauto",
    "tauto2",
    "decide",
    "native_decide",
)

_GAP_NOTE_RE = re.compile(r"--\s*GAP\s*:[^\S\n]*(.*)$", re.MULTILINE)
_SORRY_TOKENS = ("sorry", "admit")

#: have-step header: ``have <name> : <statement> := by``
_STEP_RE = re.compile(r"^(?P<indent>\s*)have\s+(?P<name>\w+)\s*:\s*(?P<stmt>.*?)\s*:=\s*by\s*$")


@dataclass
class HaveStep:
    """One have-step of a skeleton."""

    name: str
    statement: str
    body: str
    gap_note: str | None = None
    unresolved: bool = False


@dataclass
class Skeleton:
    """Parsed skeleton: have-steps plus any contract violations."""

    have_steps: list[HaveStep] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)

    @property
    def gaps(self) -> list[HaveStep]:
        return [s for s in self.have_steps if s.unresolved]

    @property
    def has_unresolved_gaps(self) -> bool:
        return any(s.unresolved for s in self.have_steps)


def _strip_comments(text: str) -> str:
    """Strip Lean line (``--``) and block (``/- ... -/``) comments."""
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        if text.startswith("/-", i):
            end = text.find("-/", i + 2)
            if end == -1:
                break
            i = end + 2
        elif text.startswith("--", i):
            nl = text.find("\n", i)
            i = n if nl == -1 else nl + 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def _analyze_step(name: str, stmt: str, body: str, problems: list[str]) -> HaveStep:
    """Classify one have-step: gap annotation, contamination, smuggling."""
    lowered = body.lower()
    gap_note: str | None = None
    m = _GAP_NOTE_RE.search(body)
    has_gap_comment = "-- GAP" in body
    if m:
        gap_note = m.group(1).strip()
        if not gap_note:
            problems.append(f"empty gap note in have step '{name}'")

    has_sorry = any(tok in lowered for tok in _SORRY_TOKENS)
    has_metavar = "?_" in body

    if (has_sorry or has_metavar) and not has_gap_comment and gap_note is None:
        problems.append(f"unannotated placeholder/sorry in have step '{name}'")

    if not has_sorry and not has_metavar and not has_gap_comment and gap_note is None:
        body_tactics = re.findall(r"\b[\w?]+\b", body)
        if any(t in body_tactics for t in _AUTO_TACTICS):
            problems.append(f"unmarked tactic body in have step '{name}' (B2 smuggling risk)")

    unresolved = has_sorry or has_metavar or has_gap_comment or gap_note is not None
    return HaveStep(name=name, statement=stmt, body=body, gap_note=gap_note, unresolved=unresolved)


def parse_skeleton(text: str) -> Skeleton:
    """Parse a candidate proof into its have-chain skeleton."""
    steps: list[HaveStep] = []
    problems: list[str] = []
    lines = text.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        m = _STEP_RE.match(lines[i])
        if m:
            name = m.group("name")
            stmt = m.group("stmt").strip()
            indent = len(m.group("indent"))
            body_lines: list[str] = []
            i += 1
            while i < n:
                nxt = lines[i]
                stripped = nxt.strip()
                if (
                    stripped
                    and len(nxt) - len(nxt.lstrip()) <= indent
                    and not stripped.startswith("--")
                ):
                    break
                body_lines.append(nxt)
                i += 1
            steps.append(_analyze_step(name, stmt, "\n".join(body_lines), problems))
            continue
        i += 1
    return Skeleton(have_steps=steps, problems=problems)


def validate_skeleton(text: str) -> Skeleton:
    """Validate a candidate skeleton against the skeleton contract."""
    return parse_skeleton(text)


def refined_proof_ok(text: str) -> bool:
    """True iff the refined proof is contamination-free (no sorry/admit).

    Mirrors the verifier's static scan: comments are stripped first, then
    sorry/admit tokens are looked for. The kernel sorryAx audit remains
    the authoritative layer at verify time.
    """
    lowered = _strip_comments(text).lower()
    return not any(tok in lowered for tok in _SORRY_TOKENS)


def skeleton_edit_distance(a: str, b: str) -> int:
    """Line-based edit distance between two proofs (reviewer delta).

    0 for identical texts; monotonically larger for more rework.
    """
    matcher = difflib.SequenceMatcher(None, a.splitlines(), b.splitlines(), autojunk=False)
    return sum(
        len(a[i1:i2]) + len(b[j1:j2])
        for tag, i1, i2, j1, j2 in matcher.get_opcodes()
        if tag != "equal"
    )
