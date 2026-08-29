"""The spacing-loss remedy (2026-08-20).

Old-commit classification matrix (round-13 honesty rule): ALL tests FAIL at every
commit up to and including 8b82787 — `tools/refetch_server_txt_defects.py` does
not exist there. Every arm is new-behaviour.

Fixture-only; no network, no PDFs opened.

The defect: 70 documents carry words glued together, all of them from `txturl`
(server_txt 70/2,688 = 2.6%; pymupdf 0/437 = 0.0%), concentrated in 2003-2009
and 65 of them in `pad`, the P2 panel. The remedy is D9's own `pdfurl` fallback.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


rf = _load("refetch_server_txt_defects")

GOOD = ("the project appraisal document of the world bank for official use only "
        "on a proposed credit to the republic in support of the reform program ")
GLUED = ("PROJECTAPPRAISALDOCUMENT FOROFFICIALUSEONLY INTERNATIONALDEVELOPMENT"
         "ASSOCIATION PROPOSEDCREDITTOTHEREPUBLIC REFORMPROGRAMSUPPORT ")


def test_spacing_stats_separates_glued_text_from_prose():
    _, ml_good, ls_good = rf.spacing_stats(GOOD * 30)
    _, ml_bad, ls_bad = rf.spacing_stats(GLUED * 30)
    assert ml_bad > ml_good * 1.5
    assert ls_bad > rf.LONG_SHARE >= ls_good


def test_find_defective_flags_the_glued_document_only(tmp_path):
    for i in range(6):                      # a normal corpus to set the median
        p = tmp_path / "pad" / "2015" / f"ok{i}.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(GOOD * 40, encoding="utf-8")
    bad = tmp_path / "pad" / "2004" / "glued.txt"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text(GLUED * 40, encoding="utf-8")
    found = rf.find_defective(tmp_path)
    assert [r["id"] for r in found] == ["glued"]


def test_short_documents_are_not_judged(tmp_path):
    p = tmp_path / "pad" / "2004" / "tiny.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(GLUED, encoding="utf-8")          # < 200 tokens
    assert rf.find_defective(tmp_path) == []


def test_the_sap_gate_refuses_a_refetch(tmp_path, monkeypatch):
    for i in range(6):
        p = tmp_path / "pad" / "2015" / f"ok{i}.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(GOOD * 40, encoding="utf-8")
    bad = tmp_path / "pad" / "2004" / "glued.txt"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text(GLUED * 40, encoding="utf-8")
    idx = tmp_path / "index.csv"                 # the defective doc IS sampled
    idx.write_text("id,pdfurl\nglued,http://example.org/x.pdf\n", encoding="utf-8")
    monkeypatch.setattr(rf, "FROZEN", idx)
    with pytest.raises(SystemExit) as e:
        rf.main(["--text-root", str(tmp_path)])
    assert "SAP freeze" in str(e.value)


def test_nothing_to_remedy_exits_cleanly_without_invoking_the_gate(tmp_path, monkeypatch):
    """A defective file that the analysis never reads is not work, so there is
    nothing for the gate to guard."""
    for i in range(6):
        p = tmp_path / "pad" / "2015" / f"ok{i}.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(GOOD * 40, encoding="utf-8")
    stray = tmp_path / "pad" / "2004" / "stray.txt"
    stray.parent.mkdir(parents=True, exist_ok=True)
    stray.write_text(GLUED * 40, encoding="utf-8")
    idx = tmp_path / "index.csv"
    idx.write_text("id,pdfurl\nsomeone_else,http://example.org/y.pdf\n", encoding="utf-8")
    monkeypatch.setattr(rf, "FROZEN", idx)
    assert rf.main(["--text-root", str(tmp_path)]) == 0


def test_list_mode_needs_no_gate_and_writes_nothing(tmp_path, capsys):
    p = tmp_path / "pad" / "2004" / "a.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(GOOD * 40, encoding="utf-8")
    before = {q: q.read_bytes() for q in tmp_path.rglob("*.txt")}
    assert rf.main(["--list", "--text-root", str(tmp_path)]) == 0
    assert {q: q.read_bytes() for q in tmp_path.rglob("*.txt")} == before


def test_replacement_is_conditional_on_measured_improvement():
    """The tool replaces text only when the re-extraction reads BETTER on the
    same statistic that condemned it. A remedy assumed rather than verified is
    how a corpus quietly gets worse."""
    src = (ROOT / "tools" / "refetch_server_txt_defects.py").read_text()
    assert 'mean_len < r["mean_token_len"] and long_share < r["long_share"]' in src
    assert "kept_original_no_improvement" in src


def test_a_partial_pass_is_refused_rather_than_silently_skipped():
    src = (ROOT / "tools" / "refetch_server_txt_defects.py").read_text()
    assert "refusing a partial pass rather than silently skipping" in src


def test_only_documents_in_the_analysis_index_are_owed_a_remedy(tmp_path):
    """The Stage-B redraw swapped 72.6% of the WB sample, so data/text/ holds
    text files no longer sampled. A remedy is owed only to documents the
    analysis will read; reporting the strays as unfixable is what stopped the
    first post-SAP run (49 invisible, 55 stray, against the v1 index)."""
    for i in range(6):
        p = tmp_path / "pad" / "2015" / f"ok{i}.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(GOOD * 40, encoding="utf-8")
    for name in ("sampled", "stray"):
        q = tmp_path / "pad" / "2004" / f"{name}.txt"
        q.parent.mkdir(parents=True, exist_ok=True)
        q.write_text(GLUED * 40, encoding="utf-8")

    both = {r["id"] for r in rf.find_defective(tmp_path)}
    assert both == {"sampled", "stray"}                    # norm sees everything
    scoped = {r["id"] for r in rf.find_defective(tmp_path, index={"sampled"})}
    assert scoped == {"sampled"}                           # remedy is scoped


def test_the_index_is_the_analysis_corpus_not_the_sealed_sample():
    assert rf.FROZEN.name == "frozen_sampling_v2.csv"


def test_acceptance_is_two_sided_not_merely_downward(tmp_path):
    """The regression this exists for: mojibake tokens are SHORT, so replacing
    good text with garbage passes both one-sided tests — mean length falls and
    the long-token share falls to zero. Measured 2026-08-26, that accepted
    annual_report/2007/8514626 at mean length 3.05 against a corpus median of
    ~5.56. Landing far BELOW the band is a different failure, not a fix."""
    for i in range(8):
        p = tmp_path / "pad" / "2015" / f"ok{i}.txt"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(GOOD * 40, encoding="utf-8")
    lo, hi = rf.corpus_band(tmp_path)
    _, healthy, _ = rf.spacing_stats(GOOD * 40)
    assert lo <= healthy <= hi

    mojibake = "J>;MEHB:87DA I^bdg AZhiZ Idc\\ KVcjVij BdcVa BnVcbVg EVaVj "
    _, garbage_len, garbage_long = rf.spacing_stats(mojibake * 60)
    _, glued_len, glued_long = rf.spacing_stats(GLUED * 40)
    assert garbage_len < glued_len and garbage_long < glued_long   # both one-sided pass
    assert not (lo <= garbage_len <= hi), "the band is what refuses it"


def test_the_band_is_derived_from_the_corpus_not_hardcoded():
    src = (ROOT / "tools" / "refetch_server_txt_defects.py").read_text()
    assert "band_lo <= mean_len <= band_hi" in src
    assert "kept_original_outside_band" in src
