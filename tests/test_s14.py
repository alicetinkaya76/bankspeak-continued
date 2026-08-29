import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pandas as pd
import pytest

import s09b_wb_p0_frame as s9b
from s14_branch_decision import decide, g3_support


def _wb(genres=("cem", "scd", "cpf"), iso=("KEN", "UGA"), years=None):
    years = years or list(range(1994, 2026))
    rows = [{"genre": g, "country_iso3": iso[i % len(iso)], "year": y}
            for g in genres for i, y in enumerate(years)]
    return pd.DataFrame(rows)


def _imf(iso=("KEN", "UGA"), years=None):
    years = years or list(range(1994, 2026))
    return pd.DataFrame([{"country_iso3": iso[i % len(iso)], "year": y}
                         for i, y in enumerate(years)])


G1_OK = {"g1_pass": True, "n": 20, "n_pass": 18, "sheet_size_valid": True}
G1_BAD = {"g1_pass": False, "n": 20, "n_pass": 10, "sheet_size_valid": True}


def test_g3_support_reading():
    wb = pd.DataFrame([{"genre": "cem", "country_iso3": c, "year": y}
                       for c, y in [("KEN", 2023), ("KEN", 2024),
                                    ("UGA", 2025), ("TZA", 2025)]])
    imf = pd.DataFrame([{"country_iso3": c, "year": 2024}
                        for c in ("KEN", "UGA")])
    r = g3_support(wb, imf)
    assert r["n_post_docs"] == 4 and r["n_supported"] == 3
    assert r["ok"] is False               # 0.75 < 0.80


def test_decide_first_pass_freezes_and_skips_later():
    wb, imf = _wb(), _imf()
    out = decide(wb, imf, {g: G1_OK for g in ("cem", "scd", "cpf")},
                 {"cem": 0.5, "scd": 0.5, "cpf": 0.5})
    assert out["family"] == {"P0": "cem"}
    assert out["candidates"]["scd"] == {"status":
                                        "not_evaluated_one_way_rule"}


def test_decide_priority_order_falls_through():
    wb, imf = _wb(), _imf()
    out = decide(wb, imf, {"cem": G1_BAD, "scd": G1_OK, "cpf": G1_OK},
                 {"cem": 0.5, "scd": 0.5, "cpf": 0.5})
    assert out["family"] == {"P0": "scd"}
    assert out["candidates"]["cem"]["passes_all"] is False


def test_decide_all_fail_gives_p1p2():
    wb, imf = _wb(), _imf()
    out = decide(wb, imf, {g: G1_OK for g in ("cem", "scd", "cpf")},
                 {"cem": 0.9, "scd": 0.9, "cpf": 0.9})   # G4 fails everywhere
    assert out["family"] == {"P1P2": True}


def test_decide_missing_g1_sheet_fails_gate():
    wb, imf = _wb(), _imf()
    out = decide(wb, imf, {}, {"cem": 0.5, "scd": 0.9, "cpf": 0.9})
    assert out["candidates"]["cem"]["g1"]["ok"] is False
    assert out["family"] == {"P1P2": True}


def test_cli_write_once(tmp_path, monkeypatch, capsys):
    import json, sys as _sys
    from s14_branch_decision import main
    wb = tmp_path / "wb.csv"; _wb().to_csv(wb, index=False)
    imf = tmp_path / "imf.csv"; _imf().to_csv(imf, index=False)
    g1 = tmp_path / "g1.json"
    g1.write_text(json.dumps({g: G1_OK for g in ("cem", "scd", "cpf")}))
    mde = tmp_path / "mde.json"
    mde.write_text(json.dumps({"cem": 0.5, "scd": 0.5, "cpf": 0.5}))
    out = tmp_path / "decision.json"
    argv = ["s14", "--wb-frame", str(wb), "--imf-frame", str(imf),
            "--g1-scores", str(g1), "--mde", str(mde), "--out", str(out)]
    monkeypatch.setattr(_sys, "argv", argv)
    main()
    assert out.exists()
    with pytest.raises(SystemExit):
        main()                                  # write-once refusal
