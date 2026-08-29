"""SAP addendum A5 (2026-08-20): the --g2-report fail-open in s09b.

Old-commit classification matrix (round-13 honesty rule): at
20af74e71d7eedb0a23583d81982f816b645544f and at every commit up to
19a36abf67c7dfa4a2c653cfe0e9e24c55c8c727,
`test_write_outputs_emits_the_g2_report` FAILS (the live branch wrote the
frame and audit and returned, so the report was never written) and
`test_g2_report_without_imf_frame_is_refused` FAILS (no such guard existed).
`test_offline_path_still_writes_frame_and_audit` PASSES at those commits and
is the behaviour-preservation arm.

Fixture-only; no network.
"""
import json
import sys
import types
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import s09b_wb_p0_frame as s09b


def _frame():
    """Two genres: one with post years, one without."""
    rows = []
    for y in range(1999, 2026):
        rows.append({"institution": "wb", "genre": "cem", "year": y,
                     "id": f"cem{y}", "country_iso3": "NGA",
                     "title": f"CEM {y}", "docdt": f"{y}-06-01",
                     "doc_id": str(y), "volnb": 1})
    for y in (2015, 2016):
        rows.append({"institution": "wb", "genre": "scd", "year": y,
                     "id": f"scd{y}", "country_iso3": "NGA",
                     "title": f"SCD {y}", "docdt": f"{y}-06-01",
                     "doc_id": f"s{y}", "volnb": 1})
    return pd.DataFrame(rows)


def _imf_frame(lo=1999, hi=2025):
    return pd.DataFrame([{"institution": "imf", "genre": "articleiv",
                          "year": y, "id": f"CR{y}-001",
                          "country_iso3": "NGA", "title": f"T {y}"}
                         for y in range(lo, hi + 1)])


def _args(tmp_path, **over):
    a = types.SimpleNamespace(
        out_frame=str(tmp_path / "f.csv"), out_audit=str(tmp_path / "a.csv"),
        g2_report=None, imf_frame=None)
    for k, v in over.items():
        setattr(a, k, v)
    return a


def test_write_outputs_emits_the_g2_report(tmp_path):
    """The A5 repair: the shared writer emits the report, so the LIVE branch
    (which returns straight after this call) can no longer skip it."""
    imf = tmp_path / "imf.csv"
    _imf_frame().to_csv(imf, index=False)
    rep = tmp_path / "sub" / "g2.json"          # nested: dir must be created
    a = _args(tmp_path, g2_report=str(rep), imf_frame=str(imf))
    frame = _frame()
    s09b._write_outputs(frame, frame.assign(status="included"), a)
    assert rep.exists(), "G2 report was not written"
    d = json.loads(rep.read_text())
    assert set(d) == {"cem", "scd"}
    assert d["cem"]["common_pre_years_with_articleiv"] == 24   # 1999..2022
    assert d["cem"]["g2_metadata_ok"] is False                 # 24 < 25
    assert d["scd"]["common_pre_years_with_articleiv"] == 2


def test_g2_report_records_a_pass_when_the_overlap_is_wide_enough(tmp_path):
    """The gate is not hardwired to fail: widen the comparator by one year
    and the same genre passes. This keeps the A5 repair honest - it reports
    the quantity, it does not decide the outcome."""
    imf = tmp_path / "imf.csv"
    _imf_frame(lo=1998).to_csv(imf, index=False)               # 1998..2022
    rep = tmp_path / "g2.json"
    a = _args(tmp_path, g2_report=str(rep), imf_frame=str(imf))
    frame = _frame()
    s09b._write_outputs(frame, frame.assign(status="included"), a)
    d = json.loads(rep.read_text())
    assert d["cem"]["common_pre_years_with_articleiv"] == 24    # cem starts 1999
    frame2 = pd.concat([frame, pd.DataFrame([{
        "institution": "wb", "genre": "cem", "year": 1998, "id": "cem1998",
        "country_iso3": "NGA", "title": "CEM 1998", "docdt": "1998-06-01",
        "doc_id": "1998", "volnb": 1}])], ignore_index=True)
    s09b._write_outputs(frame2, frame2.assign(status="included"), a)
    d2 = json.loads(rep.read_text())
    assert d2["cem"]["common_pre_years_with_articleiv"] == 25
    assert d2["cem"]["g2_metadata_ok"] is True


def test_offline_path_still_writes_frame_and_audit(tmp_path):
    """Behaviour-preservation arm: the writer's original job is unchanged."""
    a = _args(tmp_path)
    frame = _frame()
    s09b._write_outputs(frame, frame.assign(status="included"), a)
    assert Path(a.out_frame).exists() and Path(a.out_audit).exists()
    assert len(pd.read_csv(a.out_frame)) == len(frame)


def test_no_g2_report_flag_writes_no_report(tmp_path):
    a = _args(tmp_path)
    frame = _frame()
    s09b._write_outputs(frame, frame.assign(status="included"), a)
    assert not list(tmp_path.glob("*.json"))


def test_g2_report_without_imf_frame_is_refused(monkeypatch, tmp_path):
    """Without the comparator the report omits g2_metadata_ok entirely, which
    a reader would take for 'no objection'. Refuse instead."""
    monkeypatch.setattr(sys, "argv", [
        "s09b", "--listing", str(tmp_path / "l.csv"),
        "--out-frame", str(tmp_path / "f.csv"),
        "--out-audit", str(tmp_path / "a.csv"),
        "--g2-report", str(tmp_path / "g2.json")])
    with pytest.raises(SystemExit, match="REFUSING --g2-report"):
        s09b.main()
    assert not (tmp_path / "g2.json").exists()
