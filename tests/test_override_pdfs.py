"""OCR-override documents must have an artifact, not just a ledger row.

Old-commit classification matrix (round-13 honesty rule): ALL tests FAIL at
every commit up to and including b5c2173 — `tools/fetch_override_pdfs.py` does
not exist there. Every arm is new-behaviour.

The gap: rulings D-9/D-12 pin broken-CMap documents to the OCR path, but
`ocr_prepass --scan` inventories PDFs, and a `txturl`-only document has none.
Three of five overrides were invisible for that reason — OCR processed zero of
them while the quality gate passed, because the gate checks ledger rows. A
ruling recorded, a gate satisfied, and the remedy never applied.
"""
import csv
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


ov = _load("fetch_override_pdfs")


def _ledgers(tmp_path, overrides, index_rows):
    o = tmp_path / "ocr_overrides.csv"
    with o.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "native_text", "reason"])
        for i in overrides:
            w.writerow([i, "False", "test"])
    idx = tmp_path / "index.csv"
    with idx.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "stratum", "year", "pdfurl"])
        w.writeheader()
        w.writerows(index_rows)
    return o, idx


def test_an_override_with_no_pdfurl_is_refused_not_skipped(tmp_path, monkeypatch):
    """The whole point: a ledger row with no reachable artifact is a ruling in
    name only. It must stop the run, not pass quietly."""
    o, idx = _ledgers(tmp_path, ["a"],
                      [{"id": "a", "stratum": "icr", "year": "2014", "pdfurl": ""}])
    monkeypatch.setattr(ov, "OVR", o)
    monkeypatch.setattr(ov, "INDEX", idx)
    monkeypatch.setattr(ov, "RAW", tmp_path / "raw")
    with pytest.raises(SystemExit) as e:
        ov.main(["--i-have-frozen-the-sap"])
    assert "ruling in name only" in str(e.value)


def test_the_sap_gate_guards_the_fetch(tmp_path, monkeypatch):
    o, idx = _ledgers(tmp_path, ["a"],
                      [{"id": "a", "stratum": "icr", "year": "2014",
                        "pdfurl": "http://example.org/a.pdf"}])
    monkeypatch.setattr(ov, "OVR", o)
    monkeypatch.setattr(ov, "INDEX", idx)
    monkeypatch.setattr(ov, "RAW", tmp_path / "raw")
    with pytest.raises(SystemExit) as e:
        ov.main([])
    assert "SAP freeze" in str(e.value)


def test_a_document_that_already_has_its_pdf_is_left_alone(tmp_path, monkeypatch):
    raw = tmp_path / "raw" / "icr" / "2014"
    raw.mkdir(parents=True)
    (raw / "a.pdf").write_bytes(b"%PDF-1.7\n%%EOF\n")
    o, idx = _ledgers(tmp_path, ["a"],
                      [{"id": "a", "stratum": "icr", "year": "2014",
                        "pdfurl": "http://example.org/a.pdf"}])
    monkeypatch.setattr(ov, "OVR", o)
    monkeypatch.setattr(ov, "INDEX", idx)
    monkeypatch.setattr(ov, "RAW", tmp_path / "raw")
    assert ov.main(["--i-have-frozen-the-sap"]) == 0      # no fetch attempted


def test_overrides_outside_the_analysis_corpus_are_not_our_problem(tmp_path, monkeypatch):
    o, idx = _ledgers(tmp_path, ["gone"], [])            # id absent from the index
    monkeypatch.setattr(ov, "OVR", o)
    monkeypatch.setattr(ov, "INDEX", idx)
    monkeypatch.setattr(ov, "RAW", tmp_path / "raw")
    assert ov.main(["--i-have-frozen-the-sap"]) == 0


def test_the_driver_fetches_before_it_scans():
    """Order is the contract: scan inventories PDFs, so the fetch must precede
    it or the override matches nothing."""
    src = (ROOT / "tools" / "run_after_sap.py").read_text()
    assert src.index("fetch_override_pdfs") < src.index('"ocr_scan"')
