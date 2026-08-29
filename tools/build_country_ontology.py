#!/usr/bin/env python3
"""The cross-institution grouping PREREG §6 actually specifies, built offline.

## Why this exists

PREREG v0.5 §6 fixes the standardization stratifier: "country (ISO3) mapped to
region x income group (WB groupings, year-matched)", with regional/multi-country
documents and missing fields sent to an explicit `unknown` group that counts as
UNSUPPORTED. The confirmatory run of 2026-08-27 did not use it. It was handed
`stratum:year` -- a variable that is institution-specific by construction, so
`icr:2019` can never have IMF support and `imf_article_iv:2019` can never have WB
support. `build_pi` keeps only groups with support in both institutions in both
periods, found none, and reported `pi_groups = 0`, `excluded_token_share = 1.0`
in every cell, primary reason `no_common_support_groups`.

That output is indistinguishable, in the JSON, from a genuine finding that the
two corpora share no common support. It is not one. It is an artifact of the
variable supplied, and reporting it as the preregistered infeasibility would
misdescribe the corpora. This module builds the real thing so the arm can be
evaluated and the distinction can be stated.

## What it does and does not settle

Region comes from the World Bank's own country endpoint, which also supplies the
canonical spelling of every country name -- the same authority that produced the
`count` field in the archived listing, so WB names are matched against WB names
rather than against a third-party gazetteer.

**Income group is the CURRENT classification, not year-matched.** The
year-matched series is the World Bank's OGHIST workbook, an .xlsx the pinned
environment cannot read without adding a dependency, and it was not assembled at
Stage-B. So the grouping produced here is `region x income(current)`, which is
NOT what §6 froze. Anything computed on it is a labelled post-hoc sensitivity and
is reported as one; it does not become condition 2. See
`docs/DEVIATION_20260827_c2_standardization.md`.

## Conservatism

Every unresolved name goes to `unknown`, which the estimator treats as
unsupported -- the direction §6 requires. Nothing is dropped to rescue coverage,
and the unresolved names are written out by name and count so the residue is
inspectable rather than merely counted.
"""
from __future__ import annotations

import argparse
import csv
import unicodedata
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "meta" / "wb_country_api_raw.json"
OUT = ROOT / "data" / "meta" / "country_ontology.csv"
UNRESOLVED = ROOT / "data" / "meta" / "country_unresolved.csv"
API = "https://api.worldbank.org/v2/country?format=json&per_page=400"

# WB writes the same country two ways across its own services: the D&R `count`
# field spells out "Republic"/"Democratic", the country endpoint abbreviates to
# "Rep."/"Dem.". Folding both to one token set matches them without fuzzy
# scoring -- which is the point, since fuzzy matching over country names is how
# Finland became Tanzania in the retrieval verifier.
FOLD = {
    "republic": "rep", "democratic": "dem", "peoples": "people",
    "islamic": "islamic", "federation": "fed", "federal": "fed",
    "kingdom": "kingdom", "arab": "arab", "the": "", "of": "",
}


def norm(s: str) -> str:
    # "Turkiye" in the country endpoint, "Turkiye" with a diaeresis in the D&R
    # listing: strip combining marks before folding, or the two never meet.
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("’", "'").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return " ".join(FOLD.get(w, w) for w in s.split() if FOLD.get(w, w))


def fetch_api(force: bool = False) -> list[dict]:
    """Write-once, like every other external capture in this repo."""
    if RAW.exists() and not force:
        return json.loads(RAW.read_text(encoding="utf-8"))[1]
    import requests
    r = requests.get(API, timeout=60)
    r.raise_for_status()
    RAW.parent.mkdir(parents=True, exist_ok=True)
    RAW.write_text(r.text, encoding="utf-8")
    print(f"[ontology] captured {RAW.relative_to(ROOT)}")
    return r.json()[1]


def wb_countries_from_capture() -> dict[str, str]:
    """doc id -> D&R `count` value, read from the write-once API pages. No new
    request: the field was in the capture all along, it was simply never carried
    into the frame."""
    out = {}
    for f in glob.glob(str(ROOT / "data/meta/wb_p1p2_raw/*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        docs = d.get("documents", d)
        for k, rec in docs.items():
            if k == "facets" or not isinstance(rec, dict):
                continue
            if rec.get("id") and rec.get("count"):
                out[str(rec["id"])] = str(rec["count"])
    return out


def build_lookup(api: list[dict]):
    by_name, by_iso = {}, {}
    for r in api:
        agg = r["region"]["value"] == "Aggregates"
        rec = {"iso3": r["id"], "region": r["region"]["value"].strip(),
               "income": r["incomeLevel"]["value"].strip(), "aggregate": agg}
        by_name[norm(r["name"])] = rec
        by_iso[r["id"]] = rec
    return by_name, by_iso


def group_of(rec: dict | None) -> str:
    if rec is None or rec["aggregate"]:
        return "unknown"
    if not rec["region"] or not rec["income"] or rec["income"] == "Not classified":
        return "unknown"
    return f"{rec['region']}|{rec['income']}"


def resolve(name: str, by_name: dict, by_iso: dict, alias: dict):
    """One country, or not one country. Returns (record|None, source).

    The `count` field holds a single country most of the time and a
    comma-joined list the rest of the time ("Senegal,World"), while several
    single countries carry a comma of their own ("Yemen, Republic of"). Splitting
    first would shred the second kind, so the whole string is tried first and the
    split is only a fallback. A fallback that resolves two or more DISTINCT
    countries is multi-country, which PREREG SS6 sends to `unknown` -- labelled
    as such, not as an unresolved name, because the two mean different things:
    one is a property of the document, the other is a gap in our map."""
    if not name:
        return None, "no_country_field"
    k = norm(name)
    if k in by_name:
        return by_name[k], "wb_country_endpoint"
    if k in alias:
        return by_iso.get(alias[k]), "wb_country_aliases.yaml"
    # prefix form: D&R "Somalia" against the endpoint's "Somalia, Fed. Rep."
    pre = [v for n, v in by_name.items()
           if n.split(" ")[0] == k and not v["aggregate"]]
    if len(pre) == 1 and " " not in k:
        return pre[0], "wb_country_endpoint_prefix"
    parts = [p.strip() for p in name.split(",") if p.strip()]
    if len(parts) > 1:
        # Aggregates are not countries. "Senegal,World" and
        # "Mongolia,East Asia and Pacific" each name ONE country beside a
        # regional tag, and "Turkiye,Turkiye" names one country twice; only a
        # value naming two or more DISTINCT countries is multi-country. Reading
        # the region tag as a second country would send ordinary
        # single-country documents to `unknown`.
        hits = [by_name[norm(p)] for p in parts if norm(p) in by_name]
        iso = {h["iso3"] for h in hits if not h["aggregate"]}
        if len(iso) > 1:
            return None, "multi_country"
        if len(iso) == 1:
            return next(h for h in hits if h["iso3"] in iso), "wb_country_endpoint_part"
    return None, "unresolved"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true",
                    help="re-capture the WB country endpoint")
    a = ap.parse_args(argv)

    api = fetch_api(force=a.refresh)
    by_name, by_iso = build_lookup(api)

    sys.path.insert(0, str(ROOT / "src"))
    import yaml
    from s09a_imf_articleiv_frame import SEED_ALIASES  # noqa: E402
    alias = {norm(k): v for k, v in SEED_ALIASES.items()}
    f = ROOT / "config" / "wb_country_aliases.yaml"
    if f.exists():
        alias.update({norm(k): v for k, v in
                      (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).items()})

    names = wb_countries_from_capture()
    rows, unresolved = [], {}

    def emit(doc_id, inst, name, rec, source):
        rows.append({"id": doc_id, "institution": inst, "country_name": name,
                     "iso3": (rec or {}).get("iso3", ""),
                     "region": (rec or {}).get("region", ""),
                     "income_current": (rec or {}).get("income", ""),
                     "group": group_of(rec), "source": source})

    for r in csv.DictReader((ROOT / "data/meta/frozen_sampling_v2.csv")
                            .open(encoding="utf-8")):
        if r["stratum"] not in ("icr", "pad"):
            continue
        name = names.get(r["id"], "")
        rec, src = resolve(name, by_name, by_iso, alias)
        if src == "unresolved" and name:
            unresolved[name] = unresolved.get(name, 0) + 1
        emit(r["id"], "WB", name, rec, src)

    imf = ROOT / "data/meta/imf_articleiv_frame.csv"
    if imf.exists():
        for r in csv.DictReader(imf.open(encoding="utf-8")):
            rec = by_iso.get(r.get("country_iso3", ""))
            if rec is None and r.get("country_iso3"):
                unresolved[f"[iso3] {r['country_iso3']}"] = \
                    unresolved.get(f"[iso3] {r['country_iso3']}", 0) + 1
            emit(r["id"], "IMF", r.get("country_iso3", ""), rec,
                 "imf_frame_iso3" if rec else "unresolved")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "institution", "country_name",
                                           "iso3", "region", "income_current",
                                           "group", "source"])
        w.writeheader()
        w.writerows(rows)
    with UNRESOLVED.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["country_name_or_iso3", "documents"])
        w.writerows(sorted(unresolved.items(), key=lambda x: -x[1]))

    n_unknown = sum(1 for r in rows if r["group"] == "unknown")
    print(f"[ontology] {len(rows)} documents; "
          f"{len({r['group'] for r in rows}) - 1} real groups; "
          f"{n_unknown} -> unknown ({n_unknown/len(rows):.1%})")
    print(f"[ontology] unresolved names: {len(unresolved)} distinct, "
          f"{sum(unresolved.values())} documents -> "
          f"{UNRESOLVED.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
