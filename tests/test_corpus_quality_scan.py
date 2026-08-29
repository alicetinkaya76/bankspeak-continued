"""Corpus quality scan: the classes it must tell apart (2026-08-20).

Old-commit classification matrix (round-13 honesty rule): ALL tests FAIL at every
commit up to and including 8b82787 — `tools/corpus_quality_scan.py` does not
exist there. Every arm is new-behaviour.

Fixture-only; the texts below are short synthetic samples in the shape of the
real defects, not corpus excerpts.

The scan exists because `s10_assemble_ar`'s prose gate covers only the assembled
Annual Report units, while `icr` and `pad` — the P1/P2 confirmatory panels — are
governed solely by PREREG §7's "tokens >= 1". A 70,000-token unusable document
passes that.
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


q = _load("corpus_quality_scan")


def _long(sample: str, n: int = 60) -> str:
    return " ".join([sample] * n)


def test_english_prose_passes():
    t = _long("the report of the bank on the project in the region is based on "
              "a review of the data and the findings from the mission at that time")
    assert q.classify(t)["verdict"] == "ok"


def test_french_is_flagged_as_non_english_not_as_mojibake():
    """pad/2005 carries 'Traduction non officielle du texte en anglais'. It is
    real prose in the wrong language, and D11 is the rule it breaks — calling it
    mojibake would send it to the wrong remedy."""
    t = _long("le rapport de la banque sur le projet dans la region est fonde sur "
              "une revue des donnees et des conclusions de la mission a ce moment")
    r = q.classify(t)
    assert r["verdict"] == "non_english_suspected"
    assert r["fr_share"] > r["en_share"]
    assert "D11" in r["evidence"]


def test_mojibake_matches_no_language_and_is_flagged_as_such():
    """The real shape: annual_report/2007 renders 'NOTE' as 'GHS8' through a
    broken ToUnicode CMap, so it is words in no language at all."""
    t = _long("hhxwfpi Sfywfty ippwtyr xpxgp hytp fiuxpy pqwphpi xpspytp "
              "Byhxp RTFFQX qwhfty typp pwpfty hffht qtwp hytyfww")
    r = q.classify(t)
    assert r["verdict"] == "mojibake_suspected"
    assert r["en_share"] < q.SUSPECT and r["fr_share"] < q.SUSPECT


def test_a_table_dump_is_separated_from_mojibake_by_digit_density():
    t = _long("Ghana 103631 100.0 100 Guatemala 101311 250.5 250 Peru 104567 "
              "75.25 75 Kenya 109988 300.0 300 Nepal 110234 42.5 42")
    r = q.classify(t)
    assert r["verdict"] == "table_dump_suspected"
    assert r["digit_frac"] >= q.TABLE_DIGIT_FRAC


def test_the_digit_threshold_sits_in_the_observed_gap():
    """Calibrated, not guessed: the two real mojibake documents carry digit
    fractions 0.0024 and 0.0321, the real table dump 0.1499."""
    assert 0.0321 < q.TABLE_DIGIT_FRAC < 0.1499


def test_a_cmap_that_maps_letters_onto_digits_is_the_known_ambiguity():
    """2007 renders "A" as "4" and "E" as "8", so a digit-heavy substitution can
    push mojibake toward the table signature. Both verdicts are therefore
    'suspected' and neither excludes anything."""
    heavy = _long("GHS8 4RTFF4QX 8h4wf 4444 8888 4h4 8p8 44h 88w 4RT 8GS")
    assert q.classify(heavy)["verdict"].endswith("_suspected")


def test_a_short_document_is_not_judged_rather_than_guessed_at():
    assert q.classify("the bank and the project")["verdict"] == "too_short_to_judge"


def test_borderline_prose_is_named_borderline_not_condemned():
    """Between the 0.05 alarm and s10's own 0.15 gate the honest answer is
    'look at it', not a verdict."""
    t = _long("bank project region review data findings mission report credit "
              "loan disbursement of the appraisal component output indicator")
    r = q.classify(t)
    assert r["verdict"] == "low_prose_borderline"
    assert q.SUSPECT <= r["en_share"] < q.EN_LOW


def test_the_scan_excludes_nothing(tmp_path):
    """Standing project rule: borderline cases are flagged for a human, never
    auto-resolved. The tool writes verdicts and returns; it must not delete,
    move or filter."""
    root = tmp_path / "text" / "icr" / "2004"
    root.mkdir(parents=True)
    (root / "x.txt").write_text(_long("le rapport de la banque sur le projet"),
                                encoding="utf-8")
    q.main(["--text-root", str(tmp_path / "text"), "--out", str(tmp_path / "f.csv")])
    assert (root / "x.txt").exists()
    import csv
    rows = list(csv.DictReader((tmp_path / "f.csv").open()))
    assert rows[0]["verdict"] == "non_english_suspected"
    assert rows[0]["stratum"] == "icr" and rows[0]["year"] == "2004"
