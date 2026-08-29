#!/usr/bin/env python3
"""SAP addendum A4: audit the country alias map against the captured listing.

Offline. Reads the archived listing, applies the SAME alias map the frozen
classifier uses, and reports:

  1. coverage - how many publication rows (rows carrying a catalog report
     number) still have an unmapped title prefix, and which prefixes;
  2. agreement with the IMF's own imfisocode tagging, per row and per
     prefix. This is a DIAGNOSTIC, not ground truth: the capture showed
     imfisocode is unreliable (Papua New Guinea rows tagged GIN on 12 of 21,
     Mauritius tagged MUS on only 8 of 21), so a disagreement is evidence
     about the tag at least as often as about the map. Every disagreeing
     prefix is listed so it can be inspected by name.

Usage:
  python tools/audit_country_aliases.py \
      --listing data/meta/imf_articleiv_listing.csv
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from s09a_imf_articleiv_frame import load_aliases, norm


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listing", default="data/meta/imf_articleiv_listing.csv")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()

    aliases = load_aliases(Path(a.root))
    lst = pd.read_csv(a.listing)
    lst["prefix"] = (lst["title"].astype(str).str.split(":").str[0]
                     .map(lambda s: norm(s).strip().lower()))
    lst["iso_map"] = lst["prefix"].map(aliases)
    pub = lst[lst["report_no"].notna()
              & lst["report_no"].astype(str).str.strip().ne("")].copy()

    print(f"alias map: {len(aliases)} entries")
    print(f"listing: {len(lst)} rows, of which {len(pub)} carry a catalog "
          f"report number")
    unmapped = pub[pub["iso_map"].isna()]
    print(f"\n1) COVERAGE - publications with an unmapped prefix: "
          f"{len(unmapped)} ({len(unmapped) / max(len(pub), 1):.1%})")
    if len(unmapped):
        print(unmapped.groupby("prefix").size().sort_values(ascending=False)
              .head(40).to_string())

    mapped = pub[pub["iso_map"].notna()
                 & pub["src_imfisocode"].notna()
                 & pub["src_imfisocode"].astype(str).str.strip().ne("")].copy()
    mapped["iso_imf"] = mapped["src_imfisocode"].astype(str)
    mapped["agree"] = [m in i.split("|")
                       for m, i in zip(mapped["iso_map"], mapped["iso_imf"])]
    print(f"\n2) AGREEMENT with imfisocode (diagnostic only): "
          f"{mapped['agree'].sum()}/{len(mapped)} "
          f"({mapped['agree'].mean():.1%})")
    dis = (mapped[~mapped["agree"]]
           .groupby(["prefix", "iso_map"])
           .agg(n=("agree", "size"),
                imf_tags=("iso_imf",
                          lambda s: "/".join(sorted(set(s))[:4])))
           .sort_values("n", ascending=False))
    print(f"disagreeing prefixes: {len(dis)}")
    if len(dis):
        print(dis.head(40).to_string())


if __name__ == "__main__":
    main()
