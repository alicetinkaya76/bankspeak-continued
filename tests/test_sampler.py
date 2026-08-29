import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from s09_frame_sampler import sample_frame

def frame(genres):
    rows = []
    for g in genres:
        for y in (2000, 2001):
            for i in range(60):
                rows.append({"institution": "imf", "genre": g, "year": y,
                             "id": f"{g}-{y}-{i:03d}"})
    return pd.DataFrame(rows)

def test_cap_and_determinism():
    s1 = sample_frame(frame(["article_iv"]), cap=40)
    s2 = sample_frame(frame(["article_iv"]), cap=40)
    assert len(s1) == 80 and s1.equals(s2)
    assert (s1.groupby(["genre", "year"]).size() == 40).all()

def test_adding_stratum_does_not_change_existing_cells():
    base = sample_frame(frame(["article_iv"]), cap=40)
    plus = sample_frame(frame(["article_iv", "cem"]), cap=40)
    a = set(base[base.genre == "article_iv"]["id"])
    b = set(plus[plus.genre == "article_iv"]["id"])
    assert a == b
