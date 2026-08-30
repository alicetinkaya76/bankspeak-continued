"""Pin the PLOS ONE submission limits that the manuscript has to satisfy.

The abstract limit is the one that matters. It was 374 words against a stated
300 and nothing in the repository would have noticed, because until now nothing
measured it. Two tests, therefore: the manuscript passes, and the checker can
still fail. A compliance tool that cannot fail is a compliance tool that is not
being run.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "plos_compliance.py"
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"


def mutate_abstract(text: str, addition: str) -> str:
    """Append to the ABSTRACT, not to the first thing that looks like one.

    The manuscript opens with a preregistration note closed by its own `---`
    rule, so splitting on the first rule lands in the header and the padding
    never reaches the abstract at all. The first version of these two tests did
    that and then read the tool's clean verdict as the tool failing to notice —
    a broken negative control, which is worse than no negative control, because
    it makes an unexercised checker look exercised.
    """
    m = re.search(r"(^## Abstract\n.*?)(\n---\n)", text, re.S | re.M)
    assert m, "no abstract block"
    return text[:m.end(1)] + addition + text[m.end(1):]


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *args],
                          capture_output=True, text=True, timeout=120)


def test_manuscript_has_no_blockers_at_initial_submission():
    r = run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 blocker(s)" in r.stdout


def test_abstract_is_within_the_three_hundred_word_limit():
    r = run()
    line = next(l for l in r.stdout.splitlines() if "abstract" in l and "words" in l)
    n = int(line.split("abstract")[1].split("words")[0].strip())
    assert n <= 300, line


def test_checker_fails_on_an_over_length_abstract(tmp_path):
    """The guard on the guard. Pad the abstract past the limit and the tool must
    report a blocker; if it still passes, the passing result above means nothing.
    """
    fake = tmp_path / "over.md"
    fake.write_text(mutate_abstract(PAPER.read_text(encoding="utf-8"),
                                    " padding" * 120), encoding="utf-8")
    r = run(str(fake))
    assert r.returncode == 1, r.stdout
    assert "BLOCKER" in r.stdout


def test_checker_fails_on_a_citation_in_the_abstract(tmp_path):
    fake = tmp_path / "cited.md"
    fake.write_text(mutate_abstract(PAPER.read_text(encoding="utf-8"), " (2015)"),
                    encoding="utf-8")
    r = run(str(fake))
    assert r.returncode == 1, r.stdout
    assert "abstract citations: ['(2015)']" in r.stdout


# --- the single submission PDF -------------------------------------------------

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "build_submission_pdf", ROOT / "tools" / "build_submission_pdf.py")
_pdf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pdf)


def test_unicode_scripts_become_latex_math():
    """Times New Roman has no glyph for U+2079, so "2**9 = 512" set in it becomes
    "2 = 512" with no error anywhere. The claim about the bootstrap's support
    turns into an arithmetic falsehood in the submitted PDF."""
    assert _pdf.scripts_to_math("support is 2⁹ = 512") == "support is 2$^{9}$ = 512"
    assert _pdf.scripts_to_math("MDE₈₀ is") == "MDE$_{80}$ is"
    assert _pdf.scripts_to_math("|b₂|") == "|b$_{2}$|"


def test_figure_embedding_refuses_a_missing_image(monkeypatch, tmp_path):
    """A submission PDF with a figure silently dropped is worse than a failed
    build, because nothing in the output says a figure is missing."""
    monkeypatch.setattr(_pdf, "FIGDIR", tmp_path)          # empty
    md = ("# T\n\n## Figures\n\n- **Figure 1** — `fig1_composition`. A caption.\n\n---\n")
    with pytest.raises(SystemExit) as e:
        _pdf.embed_figures(md)
    assert "no image for fig1_composition" in str(e.value)


def test_figure_embedding_refuses_a_section_it_cannot_parse():
    with pytest.raises(SystemExit) as e:
        _pdf.embed_figures("# T\n\n## Figures\n\n- Figure 1: no backticks here.\n\n---\n")
    assert "matched no caption entries" in str(e.value)


def test_every_manuscript_figure_has_an_image_on_disk():
    stems = re.findall(r"- \*\*Figure \d+\*\* — `([a-z0-9_]+)`",
                       PAPER.read_text(encoding="utf-8"))
    assert stems, "no figure entries found in the manuscript"
    for stem in stems:
        assert (_pdf.FIGDIR / f"{stem}.pdf").exists() or \
               (_pdf.FIGDIR / f"{stem}.png").exists(), stem


# --- unfilled fields ----------------------------------------------------------

_ph_spec = importlib.util.spec_from_file_location(
    "placeholder_report", ROOT / "tools" / "placeholder_report.py")
_ph = importlib.util.module_from_spec(_ph_spec)
_ph_spec.loader.exec_module(_ph)


def test_the_manuscript_carries_no_unfilled_placeholder():
    assert _ph.scan(_ph.MANUSCRIPT) == []


def test_the_scanner_sees_a_placeholder_wrapped_across_a_line_break(tmp_path):
    """The two that mattered were both wrapped, and a line-scoped pattern found
    neither. Without this control the tool's clean verdict is unearned."""
    f = tmp_path / "wrapped.md"
    f.write_text("the deposit is **[deposited at DOI … / to be deposited\n"
                 "before publication]** and nothing else.\n", encoding="utf-8")
    hits = _ph.scan([f])
    assert len(hits) == 1, hits
    assert "to be deposited before publication" in hits[0][2]


def test_the_scanner_does_not_flag_a_confidence_interval():
    """The manuscript is full of '[-0.732, 0.239]'. A scanner that calls those
    placeholders gets switched off within a day."""
    f = ROOT / "docs" / "PAPER_DRAFT_v2.md"
    text = f.read_text(encoding="utf-8")
    assert "[−0.732, 0.239]" in text or "[" in text
    assert not [h for h in _ph.scan([f])]


# --- the uncited-entry check must not pass on a substring -----------------------

_audit_spec = importlib.util.spec_from_file_location(
    "audit_citations", ROOT / "tools" / "audit_citations.py")
_audit = importlib.util.module_from_spec(_audit_spec)
_audit_spec.loader.exec_module(_audit)


def test_a_surname_inside_a_longer_word_does_not_count_as_a_citation():
    """"Ban" is inside "Bank", which this paper contains hundreds of times. Under
    substring matching an uncited Ban entry was reported as cited, and the check
    returned "none uncited" while checking nothing for that entry."""
    body = "the World Bank and the Bank of England published banking data"
    hit = re.search(r"(?<![A-Za-zÀ-ÿ])Ban(?![A-Za-zÀ-ÿ])", body)
    assert hit is None, "word-boundary matching must not find Ban inside Bank"
    assert "Ban" in body, "but a substring test would have found it — the bug"


def test_the_audit_source_no_longer_uses_a_bare_substring_test():
    src = (ROOT / "tools" / "audit_citations.py").read_text(encoding="utf-8")
    assert "n not in body" not in src, "the substring uncited-check is back"
    assert "(?<![A-Za-zÀ-ÿ])" in src


# --- internal cross-references -------------------------------------------------

def test_every_internal_cross_reference_resolves():
    r = subprocess.run([sys.executable,
                        str(ROOT / "tools" / "check_cross_references.py")],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_cross_reference_check_can_fail(tmp_path, monkeypatch):
    """A reference to a section that does not exist must be caught. Without this
    the clean verdict above could mean the pattern matches nothing at all."""
    spec = importlib.util.spec_from_file_location(
        "check_cross_references", ROOT / "tools" / "check_cross_references.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    fake = tmp_path / "p.md"
    fake.write_text("## 1. Intro\n\nAs shown in §9.9 and Table 42.\n", encoding="utf-8")
    monkeypatch.setattr(m, "PAPER", fake)
    monkeypatch.setattr(m, "SUPP", tmp_path / "absent.md")
    assert m.main() == 1


def test_a_preregistration_reference_is_not_read_as_an_internal_one():
    """§11.5 in this manuscript is the PREREGISTRATION's §11.5. A naive pattern
    reports three false dangling references on that alone."""
    paper = (ROOT / "docs" / "PAPER_DRAFT_v2.md").read_text(encoding="utf-8")
    assert "PREREG §11.5" in paper, "the qualified form this guards is gone"
    r = subprocess.run([sys.executable,
                        str(ROOT / "tools" / "check_cross_references.py")],
                       capture_output=True, text=True, timeout=120)
    assert "section 11.5" not in r.stdout
