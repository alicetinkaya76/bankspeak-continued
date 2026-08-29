import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from g1_audit import draw, score, ITEMS

def frame(n):
    return pd.DataFrame({"id": [f"CEM-{i:03d}" for i in range(n)],
                         "title": [f"Country {i}: Economic Memorandum" for i in range(n)]})

def test_draw_deterministic_and_stable():
    a = draw(frame(200)); b = draw(frame(200))
    assert list(a["id"]) == list(b["id"]) and len(a) == 20
    big = draw(frame(300))
    assert set(a["id"]) & set(big["id"])          # hash ranking, not order-based

def test_scoring_rule():
    sel = draw(frame(50))
    sheet = sel[["audit_key", "title"]].copy()
    sheet["title_only"] = True
    for c in ITEMS:
        sheet[c] = pd.Series([1] * len(sheet), dtype=object)   # CSV-like dtype
    sheet.loc[sheet.index[:3], ITEMS[1]] = ""      # 3 uncertain -> fail those rows
    r = score(sheet)
    assert r["n_pass"] == 17 and r["g1_pass"] is True
    sheet.loc[sheet.index[3:5], ITEMS[0]] = 0      # now 15 pass
    assert score(sheet)["g1_pass"] is False
