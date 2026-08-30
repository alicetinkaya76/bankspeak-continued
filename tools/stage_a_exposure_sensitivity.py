#!/usr/bin/env python3
"""Re-run the confirmatory panels without the documents seen at Stage A.

The paper reports that 748 of 2,738 Stage-B World Bank documents (27.3%) were
also in the Stage-A sample and had outcomes inspected there. An external review
made the right demand: that is not a design fixed before any outcome existed, and
the direct test of whether it matters is to drop those documents and look.

The 748 are exactly identifiable as the intersection of the two frozen sampling
frames, so no reconstruction or guesswork is involved.

This is a POST-FREEZE sensitivity. It gates nothing and the confirmatory result
stands as reported; the point is to say whether the prior exposure could have
carried the finding, rather than to argue that it could not.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bootstrap_engine import two_pass                               # noqa: E402

PANELS = {"P1": 0.025, "P2": 0.05}
OUT = ROOT / "data" / "analysis" / "stage_a_exposure_sensitivity.json"


def stage_a_ids() -> set[str]:
    def ids(p):
        return {r["id"] for r in csv.DictReader(p.open(encoding="utf-8"))}
    v1 = ids(ROOT / "data/meta/frozen_sampling_v1.csv")
    v2 = ids(ROOT / "data/meta/frozen_sampling_v2.csv")
    return v1 & v2


def cells_from_docs(docs: pd.DataFrame) -> pd.DataFrame:
    g = (docs.groupby(["institution", "year"], as_index=False)
              .agg(count=("count", "sum"), tokens=("tokens", "sum")))
    # The common-year rule: a year survives only if BOTH institutions have a cell,
    # which is what build_design enforces and what dropping documents can break.
    keep = (g.groupby("year")["institution"].nunique() == 2)
    return g[g["year"].isin(keep[keep].index)].reset_index(drop=True)


def main(B: int = 9999) -> int:
    seen = stage_a_ids()
    print(f"Stage-A-inspected documents identifiable in both frames: {len(seen)}")
    res = {"n_stage_a_inspected": len(seen), "B": B, "panels": {}}

    for panel, holm in PANELS.items():
        docs = pd.read_csv(ROOT / f"data/analysis/panels/docs_{panel}.csv",
                           dtype={"id": str})
        wb = docs[docs["institution"] == "WB"]
        dropped = wb["id"].isin(seen).sum()
        kept = docs[~((docs["institution"] == "WB") & (docs["id"].isin(seen)))]

        full = two_pass(cells_from_docs(docs), wb_label="WB", B=B)
        red = two_pass(cells_from_docs(kept), wb_label="WB", B=B)

        e = {"holm_alpha": holm, "wb_docs": int(len(wb)),
             "wb_docs_dropped": int(dropped),
             "full": {"beta": full["beta_hat"], "p": full["p_two_sided"],
                      "T": full["T_common_years"]},
             "reduced": {"beta": red["beta_hat"], "p": red["p_two_sided"],
                         "T": red["T_common_years"]},
             "c1_full": full["p_two_sided"] < holm,
             "c1_reduced": red["p_two_sided"] < holm}
        res["panels"][panel] = e
        print(f"\n{panel}  (Holm alpha {holm})")
        print(f"  World Bank documents {len(wb)}, of which Stage-A-inspected "
              f"{dropped} dropped")
        print(f"  full     beta {full['beta_hat']:+.4f}  p {full['p_two_sided']:.4f}"
              f"  years {full['T_common_years']}")
        print(f"  reduced  beta {red['beta_hat']:+.4f}  p {red['p_two_sided']:.4f}"
              f"  years {red['T_common_years']}")
        print(f"  condition 1  full {'PASS' if e['c1_full'] else 'fail'}"
              f"   reduced {'PASS' if e['c1_reduced'] else 'fail'}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n[stagea] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 9999))
