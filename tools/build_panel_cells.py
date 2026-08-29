#!/usr/bin/env python3
"""Build the P1/P2 confirmatory panel cells — and apply the exclusion rulings.

## Two jobs, one place, deliberately

**The cells.** `s13_validation_battery panel` and the frozen bootstrap engine
consume institution × year cells with columns `institution, year, count,
tokens`. Nothing produced them, so the confirmatory H-DIFF had not been computed
at all: `s08` gives a per-stratum ITS, which is a different quantity.

**The exclusions.** Rulings D-8 and D-11 exclude 20 documents; measured
2026-08-26, ten of them were still inside `family_counts.csv`, i.e. inside the
confirmatory outcome. The ledger recorded the ruling and nothing enforced it —
the same shape as the override gap, and the reason the two jobs live together:
the exclusion is applied at the point the confirmatory input is built, where it
can be counted rather than assumed.

Every drop is reported by class and written to the intention-to-sample ledger,
because an exclusion nobody counts is indistinguishable from a document that was
never sampled.

## The window

The confirmatory contrast is bounded below at **1999** — the IMF Article IV
frame's own start, the Fund having published no Article IV staff reports before
the April 1999 pilot — and above at **2025** by the §11.4 cutoff. That gives 24
pre-2023 years and 3 post, which is the window the preregistered power analysis
was run on (`docs/MDE_P1P2_20260820.md`).

P1 pairs WB `icr` against the IMF comparator; P2 pairs WB `pad`. `institution`
is `WB` or `IMF`, the labels the engine's `build_design(cells, wb_label="WB")`
expects.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "meta"
ANALYSIS = ROOT / "data" / "analysis"
COUNTS = ROOT / "data" / "features" / "family_counts.csv"
LEDGER = META / "intention_to_sample_exclusions.csv"

YEAR_LO, YEAR_HI = 1999, 2025
COMPARATOR = "imf_article_iv"
PANELS = {"P1": "icr", "P2": "pad"}


def load_exclusions() -> dict[str, str]:
    out = {}
    p = META / "d8_exclusions.csv"
    if p.exists():
        for r in csv.DictReader(p.open(encoding="utf-8")):
            out[r["id"]] = r["reason"]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(ANALYSIS / "panels"))
    ap.add_argument("--group-source", choices=("stratum_year", "country"),
                    default="stratum_year",
                    help="standardization stratum. `stratum_year` is what the "
                         "confirmatory run of 2026-08-27 used and is kept as "
                         "the default so that run stays reproducible; it cannot "
                         "have cross-institution support and makes condition 2 "
                         "infeasible by construction. `country` is the PREREG "
                         "SS6 grouping, region x income from "
                         "data/meta/country_ontology.csv")
    a = ap.parse_args(argv)
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(COUNTS.open(encoding="utf-8")))
    excl = load_exclusions()

    kept, dropped = [], []
    for r in rows:
        year = int(r["year"])
        if r["id"] in excl:
            dropped.append({**r, "drop_reason": excl[r["id"]]})
            continue
        if not (YEAR_LO <= year <= YEAR_HI):
            dropped.append({**r, "drop_reason": f"outside confirmatory window "
                                                f"{YEAR_LO}-{YEAR_HI}"})
            continue
        if str(r.get("analysis_eligible", "True")).lower() == "false":
            dropped.append({**r, "drop_reason": "analysis_eligible=False (§7)"})
            continue
        if int(float(r["eligible_tokens"])) <= 0:
            dropped.append({**r, "drop_reason": "zero eligible tokens (§7)"})
            continue
        kept.append(r)

    with LEDGER.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "stratum", "year",
                                           "eligible_tokens", "tier1_count",
                                           "drop_reason"])
        w.writeheader()
        for d in dropped:
            w.writerow({k: d.get(k, "") for k in w.fieldnames})

    by_reason: dict[str, int] = {}
    for d in dropped:
        key = d["drop_reason"].split("(")[0].strip()
        by_reason[key] = by_reason.get(key, 0) + 1
    print(f"[cells] {len(rows)} documents -> {len(kept)} kept, "
          f"{len(dropped)} dropped")
    for k in sorted(by_reason, key=lambda x: -by_reason[x]):
        print(f"    {by_reason[k]:4d}  {k}")
    n_ruled = sum(1 for d in dropped if d["id"] in excl)
    print(f"[cells] rulings D-8/D-11 enforced on {n_ruled} document(s)")
    print(f"[cells] ledger: {LEDGER.relative_to(ROOT)}")

    # §5 condition 3 needs the outcome refit with the guard family removed, and
    # its non-gating stress variant with underscore+pivotal removed. §3's
    # validation outcomes and the standardized variant need DOCUMENT rows. None
    # of it is a new measurement — every column below is an arithmetic view of
    # family_counts.csv, whose per-family columns already exist — but without
    # them s13 reports the conditions unevaluated, and an unevaluated condition
    # read as a failure is exactly what A5.7 forbids.
    FAMS = [c for c in rows[0] if c.startswith("fam_")]

    group_source = a.group_source
    ontology: dict[str, str] = {}
    if group_source == "country":
        onto = ROOT / "data" / "meta" / "country_ontology.csv"
        if not onto.exists():
            sys.exit("[cells] --group-source country needs "
                     "data/meta/country_ontology.csv; run "
                     "tools/build_country_ontology.py first")
        with onto.open(encoding="utf-8") as fh:
            ontology = {r["id"]: r["group"] for r in csv.DictReader(fh)}
        n = sum(1 for r in kept if ontology.get(r["id"], "unknown") != "unknown")
        print(f"[cells] country grouping: {n}/{len(kept)} kept documents "
              f"({n/len(kept):.1%}) carry a supported region x income group")

    def doc_rows(stratum: str, label: str) -> list[dict]:
        out = []
        for r in kept:
            if r["stratum"] != stratum:
                continue
            fams = {f: int(float(r[f])) for f in FAMS}
            out.append({
                "id": r["id"], "institution": label, "year": int(r["year"]),
                "tokens": int(float(r["eligible_tokens"])),
                "count": int(float(r["tier1_count"])),
                # §3: document prevalence and breadth. The column is named
                # `hit` because that is what s13 reads — the validation battery
                # is frozen Stage-A code and the producer adapts to it, never
                # the other way round.
                "hit": int(int(float(r["tier1_count"])) > 0),
                "breadth": sum(1 for v in fams.values() if v > 0),
                # The standardization stratum. PREREG SS6 fixes it as country
                # (ISO3) -> region x income; `stratum_year` was a stand-in
                # chosen on the belief that no country field existed for WB
                # documents. One did: the D&R `count` field is in the write-once
                # API capture, it was simply never carried into the frame. The
                # stand-in is institution-specific by construction, so
                # `build_pi` -- which keeps only groups supported in BOTH
                # institutions in BOTH periods -- retains nothing and reports
                # `no_common_support_groups`, a message that reads as a fact
                # about the corpora and is not one.
                "group": (ontology.get(r["id"], "unknown")
                          if group_source == "country"
                          else f'{r["stratum"]}:{r["year"]}'),
                **fams,
            })
        return out

    def cells_for(stratum: str, label: str) -> dict[int, list[int]]:
        agg: dict[int, list[int]] = {}
        for r in kept:
            if r["stratum"] != stratum:
                continue
            y = int(r["year"])
            a_ = agg.setdefault(y, [0, 0])
            a_[0] += int(float(r["tier1_count"]))
            a_[1] += int(float(r["eligible_tokens"]))
        return agg

    imf = cells_for(COMPARATOR, "IMF")
    for panel, stratum in PANELS.items():
        wb = cells_for(stratum, "WB")
        years = sorted(set(wb) & set(imf))
        if not years:
            sys.exit(f"[cells] {panel}: no common years — refusing to emit")
        wb_docs = doc_rows(stratum, "WB")
        imf_docs = doc_rows(COMPARATOR, "IMF")
        alldocs = [d for d in wb_docs + imf_docs if d["year"] in set(years)]

        def guard_sums(label: str, y: int, drop: tuple[str, ...]) -> int:
            return sum(d["count"] - sum(d[f] for f in drop)
                       for d in alldocs
                       if d["institution"] == label and d["year"] == y)

        out = out_dir / f"cells_{panel}.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["institution", "year", "count", "tokens",
                        "count_ex_underscore", "count_ex_underscore_pivotal"])
            for y in years:
                for label, agg in (("WB", wb), ("IMF", imf)):
                    w.writerow([label, y, agg[y][0], agg[y][1],
                                guard_sums(label, y, ("fam_underscore",)),
                                guard_sums(label, y, ("fam_underscore",
                                                      "fam_pivotal"))])

        dcols = ["id", "institution", "year", "tokens", "count",
                 "hit", "breadth", "group"]
        docs_out = out_dir / f"docs_{panel}.csv"
        with docs_out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=dcols, extrasaction="ignore")
            w.writeheader()
            w.writerows(alldocs)
        pre = [y for y in years if y < 2023]
        post = [y for y in years if y >= 2023]
        print(f"[cells] {panel} ({stratum} vs IMF): {len(years)} common years "
              f"({min(years)}-{max(years)}), pre-2023 {len(pre)}, post {len(post)}"
              f", {len(alldocs)} documents  ->  {out.name}, {docs_out.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
