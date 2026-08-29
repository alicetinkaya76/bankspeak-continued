import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from standardize import standardize_cells

def test_round6_counterexample_repaired():
    """Reviewer's two-cell case: target (.5,.5), pre (.25,.75), post (.75,.25).
    The valid estimator must weight each period's OWN rates by pi, making the
    standardized rate independent of the post composition."""
    rows = []
    for year, shares in [(2020, (0.25, 0.75)), (2024, (0.75, 0.25))]:
        for g, sh, rate in zip("AB", shares, (0.10, 0.02)):
            tok = 1_000_000 * sh
            rows.append({"institution": "WB", "year": year, "group": g,
                         "count": rate * tok, "tokens": tok})
    pi = pd.Series({"A": 0.5, "B": 0.5})
    cells = standardize_cells(pd.DataFrame(rows), pi=pi)
    for _, r in cells.iterrows():
        assert abs(r["std_rate"] - (0.5 * 0.10 + 0.5 * 0.02)) < 1e-12
        assert abs(r["coverage"] - 1.0) < 1e-12

def test_partial_coverage_renormalizes_and_reports():
    rows = [{"institution": "WB", "year": 2024, "group": "A",
             "count": 100, "tokens": 1_000_000}]      # group B absent this cell
    pi = pd.Series({"A": 0.5, "B": 0.5})
    cells = standardize_cells(pd.DataFrame(rows), pi=pi)
    assert abs(cells.iloc[0]["coverage"] - 0.5) < 1e-12
    assert abs(cells.iloc[0]["std_rate"] - 1e-4) < 1e-12
