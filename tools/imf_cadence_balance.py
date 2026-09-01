#!/usr/bin/env python3
"""Is the post-window comparator the Fund at business as usual, or a catch-up cohort?

Article IV consultations lapsed widely through 2020-21, so a 2023-25 roster can be
substantially delayed reports — different in subject matter, urgency and length
from a routine cycle, even within the same country. Country and year effects do
not neutralise that: they absorb level differences, not a change in what kind of
document a country-year contains.

Two things here. A DIAGNOSTIC — the distribution of gaps since each country's
previous observation, split by post status. And a RE-RUN of both confirmatory
panels restricted to countries whose post-window observations follow a
comparable cadence, which is the check the diagnostic exists to justify.

The index carries report number, year and country and no document text, so this
runs entirely on permitted derived output.

A gap is measured within the sampled index, not within the Fund's full
consultation history: "no prior year" means only "not sampled earlier here".
The diagnostic is therefore about the composition of OUR comparator, which is the
thing that matters for the estimate, and not about the Fund's actual cadence.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bootstrap_engine import two_pass, POST_LO, POST_HI          # noqa: E402

INDEX = ROOT / "data" / "meta" / "imf_document_index.csv"
OUT = ROOT / "data" / "analysis" / "imf_cadence_balance.json"
MAX_GAP = 3          # a post observation is "routine" if it follows within 3 years


def gaps():
    rows = list(csv.DictReader(INDEX.open(encoding="utf-8")))
    by_country = defaultdict(list)
    for r in rows:
        by_country[r["country_iso3"]].append(int(r["year"]))
    out = {}
    for c, yrs in by_country.items():
        ys = sorted(set(yrs))
        for i, y in enumerate(ys):
            out[(c, y)] = None if i == 0 else y - ys[i - 1]
    return rows, out


def main(B: int = 9999) -> int:
    rows, gap = gaps()
    post = [(r["country_iso3"], int(r["year"])) for r in rows
            if POST_LO <= int(r["year"]) <= POST_HI]
    pre = [(r["country_iso3"], int(r["year"])) for r in rows
           if int(r["year"]) < POST_LO]
    post_cy, pre_cy = sorted(set(post)), sorted(set(pre))

    def share(cys, pred):
        vals = [gap[k] for k in cys]
        return sum(1 for v in vals if pred(v)) / len(vals), len(vals)

    s_post, n_post = share(post_cy, lambda v: v is None or v >= MAX_GAP)
    s_pre, n_pre = share(pre_cy, lambda v: v is None or v >= MAX_GAP)
    print(f"country-years: {n_pre} pre, {n_post} post\n")
    print(f"  gap >= {MAX_GAP} years or first appearance")
    print(f"    pre-window  {s_pre:6.1%}")
    print(f"    post-window {s_post:6.1%}   <- the catch-up screen")

    # Countries whose post observations follow a routine cadence.
    routine = {c for (c, y) in post_cy if (gap[(c, y)] or 99) < MAX_GAP}
    print(f"\n  countries with at least one routine post observation: {len(routine)}")

    res = {"max_gap": MAX_GAP, "n_pre_country_years": n_pre,
           "n_post_country_years": n_post,
           "share_delayed_pre": s_pre, "share_delayed_post": s_post,
           "n_routine_countries": len(routine), "panels": {}}

    for panel, holm in (("P1", 0.025), ("P2", 0.05)):
        docs = pd.read_csv(ROOT / f"data/analysis/panels/docs_{panel}.csv",
                           dtype={"id": str})
        idx = {r["report_no"]: r["country_iso3"] for r in rows}
        # IMF ids in the panel are report numbers with '/' replaced by '-'.
        def ctry(i):
            return idx.get(i.replace("CR", "").replace("-", "/"), None)
        imf = docs["institution"] == "IMF"
        keep_mask = ~imf | docs["id"].map(lambda i: ctry(i) in routine)
        dropped = int((~keep_mask).sum())

        def cells(d):
            g = (d.groupby(["institution", "year"], as_index=False)
                   .agg(count=("count", "sum"), tokens=("tokens", "sum")))
            ok = g.groupby("year")["institution"].nunique() == 2
            return g[g["year"].isin(ok[ok].index)].reset_index(drop=True)

        full = two_pass(cells(docs), wb_label="WB", B=B)
        red = two_pass(cells(docs[keep_mask]), wb_label="WB", B=B)
        res["panels"][panel] = {
            "imf_docs_dropped": dropped,
            "full": {"beta": full["beta_hat"], "p": full["p_two_sided"],
                     "T": full["T_common_years"]},
            "cadence_balanced": {"beta": red["beta_hat"], "p": red["p_two_sided"],
                                 "T": red["T_common_years"]},
            "c1_full": full["p_two_sided"] < holm,
            "c1_balanced": red["p_two_sided"] < holm}
        e = res["panels"][panel]
        print(f"\n{panel}  (Holm alpha {holm}); {dropped} IMF documents dropped")
        print(f"  full              beta {full['beta_hat']:+.4f}  p {full['p_two_sided']:.4f}  years {full['T_common_years']}")
        print(f"  cadence-balanced  beta {red['beta_hat']:+.4f}  p {red['p_two_sided']:.4f}  years {red['T_common_years']}")
        print(f"  condition 1  full {'PASS' if e['c1_full'] else 'fail'}"
              f"   balanced {'PASS' if e['c1_balanced'] else 'fail'}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n[cadence] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 9999))
