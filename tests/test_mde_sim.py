import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
import pandas as pd
import pytest

from mde_sim import (simulate_joint, simulate_p0, load_template, holm2,
                     pass_p, SEED)


def test_load_template_strict_and_docs(tmp_path):
    p1 = tmp_path / "docs.csv"
    p1.write_text("year,docs\n2024,10\n2025,20\n")
    with pytest.raises(SystemExit):                   # round-8: missing year
        load_template(p1, np.array([2023, 2024, 2025]),
                      tokens_per_doc=1000.0)          # 2023 absent -> raise
    tok = load_template(p1, np.array([2024, 2025]), tokens_per_doc=1000.0)
    assert list(tok) == [10_000.0, 20_000.0]          # docs x tpd honored
    p2 = tmp_path / "tok.csv"
    p2.write_text("year,tokens,docs\n2024,5000,10\n")
    tok2 = load_template(p2, np.array([2024]), tokens_per_doc=1000.0)
    assert list(tok2) == [5000.0]                     # tokens column wins
    p3 = tmp_path / "bad.csv"
    p3.write_text("year,docs\n2024,10\n")
    with pytest.raises(SystemExit):
        load_template(p3, np.array([2024]), tokens_per_doc=None)


def test_simulate_joint_branch_specific_and_shared_imf():
    years = np.arange(2018, 2026)
    rng = np.random.default_rng(SEED)
    t_p1 = np.full(len(years), 100_000.0)
    t_p2 = np.full(len(years), 400_000.0)
    c1, c2 = simulate_joint(years, np.full(len(years), 200_000.0), 2e-4,
                            0.0, 0.0, 0.35, 0.0, rng,
                            tokens_p1=t_p1, tokens_p2=t_p2,
                            rate_p1=1e-4, rate_p2=4e-4)
    wb1 = c1[c1["institution"] == "WB"]["tokens"].unique()
    wb2 = c2[c2["institution"] == "WB"]["tokens"].unique()
    assert list(wb1) == [100_000.0] and list(wb2) == [400_000.0]
    imf1 = c1[c1["institution"] == "IMF"].reset_index(drop=True)
    imf2 = c2[c2["institution"] == "IMF"].reset_index(drop=True)
    pd.testing.assert_frame_equal(imf1, imf2)         # SAME IMF draws


def test_simulate_joint_p2_start_year_subset():
    years = np.arange(1994, 2000)
    rng = np.random.default_rng(SEED)
    _c1, c2 = simulate_joint(years, np.full(len(years), 1e5), 2e-4,
                             0.0, 0.0, 0.35, 0.0, rng,
                             p2_years=years[years >= 1996])
    assert c2["year"].min() == 1996


def test_singleton_alpha_vs_holm_pair():
    r1, r2 = holm2(0.03, 0.20, 0.05)
    assert (r1, r2) == (False, False)     # Holm gate: 0.03 >= 0.025
    assert 0.03 < 0.05                    # singleton at alpha WOULD reject


def test_simulate_p0_end_to_end_micro():
    years = np.arange(2015, 2026)
    rng = np.random.default_rng(SEED + 1)
    cells = simulate_p0(years, np.full(len(years), 2e6),
                        np.full(len(years), 2e6), 3e-4, 3e-4,
                        0.9, 0.35, 0.05, rng)
    assert set(cells["institution"]) == {"WB", "IMF"}
    p = pass_p(cells, 49, SEED + 1)
    assert 0.0 <= p < 0.5                 # strong effect, tiny-B sanity
