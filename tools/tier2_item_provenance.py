#!/usr/bin/env python3
"""Item-level provenance for the 35 Tier-2 terms: what the repository records,
what it does not record, and where it records two incompatible things.

An external reviewer asked for a per-term table (term, family, source,
source_location, match_rule, early/late counts, unit counts, leave-one-out
effect). Producing that table honestly turns up two facts that a table alone
would hide, so both are measured here rather than asserted:

1. THERE IS NO PER-TERM SOURCE. The whole repository's Tier-2 provenance is one
   end-of-line YAML comment at config/config.yaml:76 -- "provenance: Pamphlet 9
   vocabulary + WB usage" -- which names two sources for the list as a whole and
   none for any single term. The `source` and `source_location` columns are
   therefore emitted as an explicit not-recorded marker for all 35 terms. The
   named attributions that do exist in the repository (the excess-word
   literature on config/config.yaml:69) are declared for Tier-1 and are not
   transferable: back-filling them onto Tier-2 rows would be invention, not
   provenance. The list-level comment is carried in its own columns so the
   reviewer can see it without it being mistaken for per-term evidence.

2. THE MATCH RULE IS UNSPECIFIED FOR TIER-2, AND THE REPOSITORY IMPLEMENTS TWO.
   The production path (src/textstats.py:14-23) tokenises with [A-Za-z']+ on
   lowercased text and tests exact set membership, over a denominator of that
   token list. The fairness tool (tools/tier2_period_fairness.py:70,75) runs a
   case-insensitive \\b-delimited regex over the raw text, over a denominator of
   txt.split(). config/families.yaml:5-9 freezes "membership: exact_token" and
   states that \\b matching is NOT used -- but that block is declared for the
   Tier-1 outcome, so Tier-2 inherits nothing from it. Every count below is
   computed under BOTH rules and the disagreement is reported per term and in
   aggregate. The numbers already in the manuscript's S10.6 came from the
   boundary rule; the sanity-check block re-derives them and says so.

Corpus: data/text_assembled/annual_report/*.txt only -- the assembled World Bank
fiscal-year units, public disclosure under the Bank's Access to Information
Policy, the same corpus tools/tier2_period_fairness.py reads. No IMF Article IV
text is opened, read, counted or referenced by this tool.

Windows, the period-plausibility judgement and the MODERN_STEMS that encode it
are imported from tools/tier2_period_fairness.py rather than restated, so the
two tools cannot drift apart.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from textstats import tokens                                # noqa: E402
from tier2_period_fairness import EARLY, LATE, MODERN_STEMS, is_modern  # noqa: E402

TEXT = ROOT / "data" / "text_assembled" / "annual_report"
OUT_JSON = ROOT / "data" / "analysis" / "tier2_item_provenance.json"
OUT_CSV = ROOT / "data" / "analysis" / "tier2_item_provenance.csv"
FAIRNESS_JSON = ROOT / "data" / "analysis" / "tier2_period_fairness.json"

NOT_RECORDED = "not recorded in repository"
LIST_PROVENANCE_LOCATION = "config/config.yaml:76"
LIST_PROVENANCE_TEXT = (
    "bureaucratese shared by Bankspeak and LLM style; "
    "provenance: Pamphlet 9 vocabulary + WB usage"
)

RULE_PRODUCTION = (
    "production (src/textstats.py:14-23): tokens = re.compile(r\"[A-Za-z']+\")"
    ".findall(text.lower()); a hit is exact membership of a token in the "
    "35-form set; denominator = len(that token list)"
)
RULE_BOUNDARY = (
    "boundary (tools/tier2_period_fairness.py:70,75): "
    "re.compile(rf\"\\b{re.escape(t)}\\b\", re.I).findall(raw text); "
    "denominator = len(txt.split())"
)
RULE_AMBIGUOUS = (
    "AMBIGUOUS: the repository implements two divergent Tier-2 match rules "
    "(production and boundary, both below) and freezes neither for Tier-2; "
    "config/families.yaml:5-9 freezes exact_token for the Tier-1 outcome only. "
    "Both are computed for every term."
)

# Surface families are DERIVED here, not read from anywhere: config/families.yaml
# declares families for Tier-1 and stops there, and config.yaml's tier2 is a flat
# list. Single-linkage on a shared prefix of this length is enough to recover the
# obvious inflectional groups (foster/fosters/fostering) without merging
# unrelated stems; the groups are printed so a human can veto them.
FAMILY_MIN_PREFIX = 4


def load_tier2() -> list[str]:
    """Same discovery path as tools/tier2_period_fairness.py:56-62."""
    cfg = yaml.safe_load((ROOT / "config" / "config.yaml").read_text())
    for v in cfg.values():
        if isinstance(v, dict) and "tier2" in v:
            return sorted(v["tier2"])
    raise SystemExit("[prov] no tier2 list in config/config.yaml")


def list_sha256(terms: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(terms)).encode("utf-8")).hexdigest()


def _shared_prefix_len(a: str, b: str) -> int:
    n = 0
    while n < len(a) and n < len(b) and a[n] == b[n]:
        n += 1
    return n


def surface_families(terms: list[str]) -> dict[str, str]:
    parent = {t: t for t in terms}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, a in enumerate(terms):
        for b in terms[i + 1:]:
            if _shared_prefix_len(a, b) >= FAMILY_MIN_PREFIX:
                parent[find(a)] = find(b)

    groups: dict[str, list[str]] = defaultdict(list)
    for t in terms:
        groups[find(t)].append(t)

    label: dict[str, str] = {}
    for members in groups.values():
        pre = members[0]
        for m in members[1:]:
            pre = pre[:_shared_prefix_len(pre, m)]
        for m in members:
            label[m] = pre if len(members) > 1 else members[0]
    return label


def read_corpus(terms: list[str]) -> tuple[dict[int, dict], list[str]]:
    pats = {t: re.compile(rf"\b{re.escape(t)}\b", re.I) for t in terms}
    per_year: dict[int, dict] = {}
    skipped: list[str] = []
    for f in sorted(TEXT.glob("*.txt")):
        year = int(f.stem)
        txt = f.read_text(encoding="utf-8", errors="replace")
        n_boundary = len(txt.split())
        if n_boundary == 0:                      # the skip the fairness tool makes
            skipped.append(f.name)
            continue
        toks = tokens(txt)
        tok_counts = Counter(toks)
        per_year[year] = {
            "tokens_production": len(toks),
            "tokens_boundary": n_boundary,
            "production": {t: tok_counts[t] for t in terms},
            "boundary": {t: len(pats[t].findall(txt)) for t in terms},
        }
    return per_year, skipped


def window_years(per_year: dict[int, dict], win: tuple[int, int]) -> list[int]:
    return [y for y in sorted(per_year) if win[0] <= y <= win[1]]


def rate_per1k(per_year: dict[int, dict], terms, win: tuple[int, int],
               rule: str) -> float:
    """Pooled rate: summed hits over summed tokens, exactly as the fairness tool
    computes it (num/den pooled across the window, not a mean of per-year rates)."""
    num = den = 0
    for y in window_years(per_year, win):
        d = per_year[y]
        num += sum(d[rule][t] for t in terms)
        den += d["tokens_production" if rule == "production" else "tokens_boundary"]
    return 1000 * num / den if den else float("nan")


def rate_per1k_equalyear(per_year: dict[int, dict], terms, win: tuple[int, int],
                         rule: str) -> float:
    """Mean of the per-year rates, giving each fiscal year equal weight.

    This is a second aggregation axis, independent of the match rule, and the
    reason it is here is that the abstract needed it. Section 6.1's era figures
    -- including the "thirtyfold" Tier-2 rise and the temporal-anchoring 39.96
    and 22.97 beside it -- are equal-year means, while the four ratios this tool
    published were pooled. An external review noticed that the abstract paired
    an equal-year figure with a pooled one and read the mismatch as a match-rule
    problem; it is an aggregation problem. Publishing both axes from one code
    path is what lets the abstract quote a matched pair.
    """
    vals = []
    for y in window_years(per_year, win):
        d = per_year[y]
        den = d["tokens_production" if rule == "production" else "tokens_boundary"]
        if den:
            vals.append(1000 * sum(d[rule][t] for t in terms) / den)
    return sum(vals) / len(vals) if vals else float("nan")


def subset_block(per_year: dict[int, dict], terms, rule: str) -> dict:
    early = rate_per1k(per_year, terms, EARLY, rule)
    late = rate_per1k(per_year, terms, LATE, rule)
    e_eq = rate_per1k_equalyear(per_year, terms, EARLY, rule)
    l_eq = rate_per1k_equalyear(per_year, terms, LATE, rule)
    return {"early": early, "late": late,
            "ratio": (late / early) if early else float("inf"),
            "early_equal_year": e_eq, "late_equal_year": l_eq,
            "ratio_equal_year": (l_eq / e_eq) if e_eq else float("inf"),
            "n_terms": len(terms)}


def main() -> int:
    tier2 = load_tier2()
    fam = surface_families(tier2)
    plausible = [t for t in tier2 if not is_modern(t)]
    modern = [t for t in tier2 if is_modern(t)]

    per_year, skipped = read_corpus(tier2)
    yrs_early = window_years(per_year, EARLY)
    yrs_late = window_years(per_year, LATE)
    n_files = len(per_year)

    print(f"[prov] {len(tier2)} Tier-2 terms, sha256(sorted list)="
          f"{list_sha256(tier2)[:16]}...")
    print(f"[prov] corpus {TEXT.relative_to(ROOT)}: {n_files} fiscal-year units"
          f"{f' ({len(skipped)} skipped for zero tokens)' if skipped else ''}")
    print(f"[prov] early {EARLY[0]}-{EARLY[1]}: {len(yrs_early)} units "
          f"({yrs_early[0]}-{yrs_early[-1]}); "
          f"late {LATE[0]}-{LATE[1]}: {len(yrs_late)} units")
    print(f"[prov] source / source_location for all 35 terms: {NOT_RECORDED}")
    print("[prov] derived surface families (NOT repository-recorded):")
    for lab in sorted(set(fam.values())):
        members = sorted(t for t in tier2 if fam[t] == lab)
        if len(members) > 1:
            print(f"         {lab:<12s} {', '.join(members)}")

    all_blocks = {r: subset_block(per_year, tier2, r)
                  for r in ("production", "boundary")}
    plaus_blocks = {r: subset_block(per_year, plausible, r)
                    for r in ("production", "boundary")}
    modern_blocks = {r: subset_block(per_year, modern, r)
                     for r in ("production", "boundary")}

    rows = []
    for t in tier2:
        rest = [x for x in tier2 if x != t]
        row = {
            "term": t,
            "family": NOT_RECORDED,
            "family_derived_surface_stem": fam[t],
            "period_plausible": not is_modern(t),
            "source": NOT_RECORDED,
            "source_location": NOT_RECORDED,
            "list_level_provenance": LIST_PROVENANCE_TEXT,
            "list_level_provenance_location": LIST_PROVENANCE_LOCATION,
            "match_rule": RULE_AMBIGUOUS,
        }
        for rule, tag in (("production", "production"), ("boundary", "boundary")):
            key = "tokens_production" if rule == "production" else "tokens_boundary"
            e = sum(per_year[y][rule][t] for y in yrs_early)
            l = sum(per_year[y][rule][t] for y in yrs_late)
            den_e = sum(per_year[y][key] for y in yrs_early)
            den_l = sum(per_year[y][key] for y in yrs_late)
            loo = subset_block(per_year, rest, rule)
            row[f"early_count_{tag}"] = e
            row[f"late_count_{tag}"] = l
            row[f"early_rate_per1k_{tag}"] = 1000 * e / den_e if den_e else float("nan")
            row[f"late_rate_per1k_{tag}"] = 1000 * l / den_l if den_l else float("nan")
            row[f"n_fy_units_with_hit_early_{tag}"] = sum(
                1 for y in yrs_early if per_year[y][rule][t])
            row[f"n_fy_units_with_hit_late_{tag}"] = sum(
                1 for y in yrs_late if per_year[y][rule][t])
            # NOT n_documents. One assembled fiscal-year unit concatenates
            # several volumes -- 134 documents sit behind these 76 units (the
            # assembly log has 135 include rows, one of which carries no text)
            # -- so this is a unit count and is named as one. A true per-term
            # document count needs a per-document Tier-2 tally, which no
            # derived file holds.
            row[f"n_fy_units_with_hit_{tag}"] = sum(
                1 for y in per_year if per_year[y][rule][t])
            row[f"leave_one_out_ratio_{tag}"] = loo["ratio"]
            row[f"leave_one_out_delta_{tag}"] = loo["ratio"] - all_blocks[rule]["ratio"]
        row["rule_disagreement_total"] = sum(
            abs(per_year[y]["production"][t] - per_year[y]["boundary"][t])
            for y in per_year)
        row["n_fy_units_early"] = len(yrs_early)
        row["n_fy_units_late"] = len(yrs_late)
        row["n_fy_units_total"] = n_files
        rows.append(row)

    absent_early = {r: [t for t in tier2
                        if sum(per_year[y][r][t] for y in yrs_early) == 0]
                    for r in ("production", "boundary")}

    largest_loo = {}
    for rule, tag in (("production", "production"), ("boundary", "boundary")):
        top = max(rows, key=lambda r: abs(r[f"leave_one_out_delta_{tag}"]))
        largest_loo[rule] = {"term": top["term"],
                             "leave_one_out_delta": top[f"leave_one_out_delta_{tag}"],
                             "leave_one_out_ratio": top[f"leave_one_out_ratio_{tag}"],
                             "all35_ratio": all_blocks[rule]["ratio"]}

    # The boundary rule is what S10.6 ran, so this block must land on the numbers
    # already in data/analysis/tier2_period_fairness.json. A mismatch is a finding,
    # not something to tune away.
    check = {"compared_against": str(FAIRNESS_JSON.relative_to(ROOT)),
             "rule_compared": "boundary", "tolerance_rel": 1e-9}
    if FAIRNESS_JSON.exists():
        ref = json.loads(FAIRNESS_JSON.read_text(encoding="utf-8"))
        pairs = [("all 35 terms", all_blocks["boundary"]),
                 ("period-plausible only", plaus_blocks["boundary"]),
                 ("modern register only", modern_blocks["boundary"])]
        diffs = {}
        for label, mine in pairs:
            theirs = ref["subsets"][label]
            for k in ("early", "late", "ratio"):
                d = abs(mine[k] - theirs[k])
                scale = max(abs(theirs[k]), 1e-30)
                diffs[f"{label}|{k}"] = {"mine": mine[k], "reference": theirs[k],
                                         "abs_diff": d, "rel_diff": d / scale}
        check["numeric"] = diffs
        check["numeric_all_match"] = all(v["rel_diff"] <= 1e-9 for v in diffs.values())
        check["absent_in_early_window_matches"] = (
            sorted(absent_early["boundary"]) == sorted(ref["absent_in_early_window"]))
        check["reference_absent_n"] = len(ref["absent_in_early_window"])
    else:
        check["status"] = f"{NOT_RECORDED}: {FAIRNESS_JSON.name} absent"

    out = {
        "tool": "tools/tier2_item_provenance.py",
        "randomness": "none; this tool is deterministic and consumes no seed",
        "corpus": {
            "dir": str(TEXT.relative_to(ROOT)),
            "note": ("World Bank assembled fiscal-year annual-report units, public "
                     "under the Bank's Access to Information Policy; no IMF text "
                     "is read by this tool"),
            "n_fy_units_total": n_files,
            "n_fy_units_skipped_zero_tokens": len(skipped),
            "skipped_files": skipped,
            "early_window": list(EARLY),
            "late_window": list(LATE),
            "n_fy_units_early": len(yrs_early),
            "n_fy_units_late": len(yrs_late),
            "years_early": yrs_early,
            "years_late": yrs_late,
        },
        "provenance": {
            "per_term_source": NOT_RECORDED,
            "per_term_source_location": NOT_RECORDED,
            "list_level_record": LIST_PROVENANCE_TEXT,
            "list_level_record_location": LIST_PROVENANCE_LOCATION,
            "list_level_record_names_sources_collectively": True,
            "tier1_attributions_not_transferable": (
                "config/config.yaml:69 attributes Tier-1 to the excess-word "
                "literature; the repository makes no such attribution for Tier-2 "
                "and none is asserted here"),
            "tier2_sha256_sorted_newline": list_sha256(tier2),
            "n_terms": len(tier2),
        },
        "match_rules": {
            "production": RULE_PRODUCTION,
            "boundary": RULE_BOUNDARY,
            "used_by_existing_s10_6_numbers": "boundary",
            "frozen_for_tier2": NOT_RECORDED,
            "families_yaml_note": ("config/families.yaml:5-9 freezes "
                                   "membership: exact_token and states that \\b "
                                   "matching is NOT used, but that block is "
                                   "declared for the Tier-1 outcome only"),
        },
        "families": {
            "recorded_in_repository": NOT_RECORDED,
            "note": ("config/families.yaml declares families for Tier-1 only; the "
                     "column family_derived_surface_stem below is derived by this "
                     "tool, single-linkage on a shared prefix of "
                     f"{FAMILY_MIN_PREFIX}+ characters, and is not authority"),
            "derived": {lab: sorted(t for t in tier2 if fam[t] == lab)
                        for lab in sorted(set(fam.values()))},
        },
        "column_notes": {
            "source / source_location": "explicit not-recorded marker for all 35 terms",
            "family": ("explicit not-recorded marker; see "
                       "family_derived_surface_stem for the derived grouping"),
            "match_rule": ("single value per row is ambiguous in this repository; "
                           "counts are split into _production and _boundary"),
            "early_count / late_count / n_fy_units / rate_per1k": (
                "split into _production and _boundary because the two repository "
                "rules disagree"),
            "leave_one_out_effect": ("split into leave_one_out_ratio (early->late "
                                     "ratio of the other 34 terms) and "
                                     "leave_one_out_delta (that minus the all-35 "
                                     "ratio), per rule"),
        },
        "terms": rows,
        "aggregate": {
            "all_35": all_blocks,
            "period_plausible_subset": {"terms": plausible, **plaus_blocks},
            "modern_register_subset": {"terms": modern, **modern_blocks},
            "absent_in_early_window": {
                r: {"n": len(absent_early[r]), "terms": absent_early[r]}
                for r in absent_early},
            "largest_leave_one_out_delta": largest_loo,
            "rule_disagreement_total_all_terms": sum(
                r["rule_disagreement_total"] for r in rows),
            "n_terms_with_rule_disagreement": sum(
                1 for r in rows if r["rule_disagreement_total"]),
        },
        "sanity_check_vs_tier2_period_fairness": check,
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=1), encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\n{'subset':24s} {'rule':11s} {'1946-65':>9s} {'2020-24':>9s} {'ratio':>9s}")
    for label, blocks in (("all 35 terms", all_blocks),
                          ("period-plausible only", plaus_blocks),
                          ("modern register only", modern_blocks)):
        for rule in ("production", "boundary"):
            b = blocks[rule]
            print(f"  {label:22s} {rule:11s} {b['early']:9.4f} {b['late']:9.4f} "
                  f"{b['ratio']:8.2f}x")
    print(f"\n[prov] absent in {EARLY[0]}-{EARLY[1]}: "
          f"production {len(absent_early['production'])}/35, "
          f"boundary {len(absent_early['boundary'])}/35")
    print(f"[prov] rule disagreement: {out['aggregate']['rule_disagreement_total_all_terms']} "
          f"hits over {n_files} units, "
          f"{out['aggregate']['n_terms_with_rule_disagreement']}/35 terms affected")
    for rule, d in largest_loo.items():
        print(f"[prov] largest leave-one-out delta ({rule}): {d['term']} "
              f"{d['leave_one_out_delta']:+.3f} (34-term ratio {d['leave_one_out_ratio']:.2f}x "
              f"vs all-35 {d['all35_ratio']:.2f}x)")
    if "numeric_all_match" in check:
        print(f"[prov] reproduces tier2_period_fairness.json (boundary rule): "
              f"numbers={check['numeric_all_match']}, "
              f"absent-list={check['absent_in_early_window_matches']}")
    print(f"[prov] wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"[prov] wrote {OUT_CSV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
