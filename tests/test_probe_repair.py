"""Phase 2 red tests — L1 probe-in-loop repair directives (G2).

Contract: classification and directive content are deterministic and
total over the probe-failure taxonomy; diagnosis attaches ONLY to
probe-failed feedback; the audit-failed and clean paths are byte-for-
byte unchanged; the revision budget is untouched.

Attribution: Hermes Agent (Nous Research) under CTO direction.
"""

from __future__ import annotations

from leanecon.eval_formalizer import classify_probe_failure
from leanecon.probe_repair import (
    MAX_REVISION_ATTEMPTS_UNCHANGED,
    REVISION_FEEDBACK_HEADER,
    diagnose,
    revision_feedback_block,
)

# -- principle: directive table is total over classifier outputs --------


def test_directive_table_covers_every_classifier_output():
    from leanecon.probe_repair import DIRECTIVE_FOR_CLASS

    classes = {
        "clean_or_no_signal",
        "unknown_identifier",
        "binder_annotation",
        "ambiguity",
        "instance_synthesis",
        "type_mismatch",
        "unknown_universe",
        "recursion_depth",
        "sorry",
        "syntax",
        "unclassified",
    }
    assert set(DIRECTIVE_FOR_CLASS) == classes
    for klass, text in DIRECTIVE_FOR_CLASS.items():
        assert isinstance(text, str)
        if klass not in {"clean_or_no_signal", "sorry"}:
            # actionable directives mention Lean, never empty
            assert len(text) > 20


def test_budget_constant_untouched():
    """D2: probe repair lives inside the existing budget."""
    from leanecon.revise_loop import MAX_REVISION_ATTEMPTS

    assert MAX_REVISION_ATTEMPTS == 3
    assert MAX_REVISION_ATTEMPTS_UNCHANGED == MAX_REVISION_ATTEMPTS


# -- behavior: diagnosis attaches iff last feedback has failed probe ----


def _fb(**kw):
    base = {"draft": "theorem t : True", "static_problems": [], "probe_compiles": None, "probe_stderr": ""}
    base.update(kw)
    return base


def test_diagnose_none_for_audit_failed_feedback():
    fb = _fb(static_problems=["theorem-style proof body detected"])
    assert diagnose(fb) is None


def test_diagnose_none_for_clean_or_no_probe():
    assert diagnose(_fb()) is None
    assert diagnose(_fb(probe_compiles=True)) is None


def test_diagnose_binder_annotation():
    fb = _fb(probe_compiles=False, probe_stderr="error: invalid binder annotation, type is not a class instance")
    text = diagnose(fb)
    assert text is not None
    assert "binder" in text.lower()
    assert "typeclass" in text.lower()  # names the Lean fact
    assert classify_probe_failure(fb["probe_stderr"]) == "binder_annotation"


def test_diagnose_syntax_positions_kept_verbatim():
    stderr = "file.lean:3:345: error: unexpected token 'in'; expected ','"
    text = diagnose(_fb(probe_compiles=False, probe_stderr=stderr))
    assert text is not None
    assert "3:345" in text  # position surfaces verbatim


def test_diagnose_unclassified_is_honest():
    text = diagnose(_fb(probe_compiles=False, probe_stderr="something novel"))
    assert text is not None
    assert "outside the known classes" in text.lower()


# -- integration: feedback block gains a Diagnosis section only when ----


def test_block_unchanged_without_failed_probe():
    plain = revision_feedback_block([_fb(static_problems=["x"])])
    assert "Diagnosis" not in plain
    assert REVISION_FEEDBACK_HEADER in plain


def test_block_appends_diagnosis_after_failed_probe():
    hist = [
        _fb(static_problems=["d1 bare core"]),
        _fb(probe_compiles=False, probe_stderr="error: invalid binder annotation, type is not a class instance"),
    ]
    block = revision_feedback_block(hist)
    assert "Attempt 1:" in block and "Attempt 2:" in block
    assert "Diagnosis" in block
    assert "typeclass" in block


# -- runner delegation: a3_runner._revision_feedback_block is the live --


def test_runner_block_diagnoses_failed_probe():
    """The LIVE prompt builder gains the Diagnosis, not just the library copy."""
    from leanecon.a3_runner import _revision_feedback_block as runner_block
    from leanecon.revise_loop import Feedback

    hist = [
        Feedback(draft="theorem t : True", probe_compiles=False,
                 probe_stderr="error: invalid binder annotation, type is not a class instance"),
    ]
    block = runner_block(hist)
    assert "Diagnosis" in block
    assert "typeclass" in block


def test_runner_block_matches_library_when_no_diagnosis():
    """Byte-parity contract: without a failed probe both builders agree."""
    from leanecon.a3_runner import _revision_feedback_block as runner_block
    from leanecon.probe_repair import revision_feedback_block as lib_block
    from leanecon.revise_loop import Feedback

    hist = [Feedback(draft="theorem t : True", static_problems=["proof body detected"])]
    as_dicts = [{"draft": f.draft, "static_problems": list(f.static_problems),
                 "probe_compiles": f.probe_compiles, "probe_stderr": f.probe_stderr}
                for f in hist]
    assert runner_block(hist) == lib_block(as_dicts)

    clean = [Feedback(draft="theorem u : True", probe_compiles=True, probe_stderr="")]
    as_dicts = [{"draft": f.draft, "static_problems": list(f.static_problems),
                 "probe_compiles": f.probe_compiles, "probe_stderr": f.probe_stderr}
                for f in clean]
    assert runner_block(clean) == lib_block(as_dicts)
