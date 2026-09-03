#!/usr/bin/env python3
"""Publish the IMF Article IV sampling frame so a reviewer can audit it without us.

A referee reads "40 documents per year" and reasonably suspects a convenience
cross-section: a cap with no stated rule looks like a cap chosen after seeing the
data. Every fact that answers the charge already exists in this repository --
the eligible frame, the preregistered cap, the sampler, the per-cell seeds, the
disposition of every listing hit -- but it exists scattered across a CSV, a
markdown section and two modules, which is not an answer anyone can check.

This tool assembles one artifact and, crucially, RECOMPUTES every number in it
rather than restating what other files claim. The draw is replayed through the
production sampler and diffed against the frozen sample, because "reproducible"
is a claim that has to be executed to mean anything.

It also measures something the design does NOT protect against, and says so.
percell_seed guarantees independence ACROSS cells: adding a stratum cannot
disturb another cell's draw. It guarantees nothing WITHIN a cell -- random
sample() consumes randomness as a function of population length, so removing a
single eligible row that was never selected still reshuffles the selection. The
size of that effect is measured here rather than left for a referee to find.

Reads metadata columns and counts only. No IMF document text is opened, and none
could be: the frame CSVs carry identifiers, dates and titles, and this tool
reports column NAMES and row COUNTS, never document content.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

# The within-cell fragility check used to write the report number of the
# unselected document it dropped ("dropped_id"). Those are identifiers of
# documents this study never retrieved, and none of them is in the published
# index of the 1,064 it did; the public-mirror content scan refused the file on
# exactly that, and ruling D-14 had asserted the file carried no identifier.
# The number a reader needs is the fragility estimate, not which document was
# dropped, so the id is withheld here and the decision record was corrected.

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from s09_frame_sampler import sample_frame                    # noqa: E402
from percell_seed import MASTER_SEED, cell_seed               # noqa: E402

META = ROOT / "data" / "meta"
AUDIT = META / "imf_articleiv_audit.csv"
FRAME = META / "imf_articleiv_frame.csv"
FROZEN = META / "frozen_sampling_imf_v1.csv"
REQLOG = META / "imf_articleiv_raw" / "request_log.csv"
ONTOLOGY = META / "country_ontology.csv"
SAMPLER_SRC = ROOT / "src" / "s09_frame_sampler.py"
BUILDER_SRC = ROOT / "src" / "s09a_imf_articleiv_frame.py"
PREREG = ROOT / "docs" / "PREREG_DRAFT_v0.5.md"

OUT_JSON = ROOT / "data" / "analysis" / "imf_frame_publication.json"
OUT_CSV = ROOT / "data" / "analysis" / "imf_frame_publication.csv"

INSTITUTION = "imf"
GENRE = "article_iv"

# The eleven dispositions classify_row() and resolve_revisions() can assign, in
# the order the code tests them, with the literal predicate that triggers each.
# The ORDER is load-bearing: a row carries the label of the FIRST test it fails,
# so these counts are not independent reasons for exclusion.
STATUS_RULES = [
    ("excluded_selected_issues", 92,
     "title contains 'selected issues'"),
    ("excluded_not_article_iv", 94,
     "title lacks 'article iv consultation'"),
    ("excluded_language", 96,
     "language field is not English -- STRUCTURALLY UNREACHABLE: "
     "data/meta/imf_articleiv_listing.csv has no language column, and "
     "src/s09a_imf_articleiv_frame.py:85 defaults every row to 'English', so "
     "this test cannot fire and its count of 0 is not evidence that every "
     "listed document is in English"),
    ("excluded_no_country_prefix", 99,
     "title has no colon at all, so no country prefix can be split off "
     "(src/s09a_imf_articleiv_frame.py:98 yields an empty prefix only in the "
     "no-colon case; all 1,896 rows in this class contain no colon, and none "
     "is a colon with an empty prefix)"),
    ("excluded_regional_multicountry", 103,
     "title prefix is unmapped and matches a REGIONAL_TOKEN (currency/monetary "
     "union, euro area, CEMAC, WAEMU, ECCU, common policies, ' and ')"),
    ("unmapped_country", 104,
     "title prefix is not a key in the country alias table"),
    ("excluded_no_report_number", 107,
     "no Country Report number parseable from title or report_no field"),
    ("excluded_after_cutoff", 109,
     "pub_date later than the confirmatory cutoff 2025-12-31"),
    ("excluded_year_window", 111,
     "year outside the declared build window [year_lo, year_hi]"),
    ("included", 112,
     "passed every test above; carried into the eligible frame"),
    ("superseded_revision", 125,
     "shares a Country Report number with a later-dated retained row "
     "(one unit per report number)"),
]

# Fields the referee asked us to standardise on. Checked against the actual
# column lists, not against memory.
REQUESTED_STANDARDISATION = ["region", "income_group", "programme_status"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cap_default_from_source(path: Path) -> tuple[int, int]:
    """Lift the --cap default out of the sampler's AST, with its line number.

    Read rather than retyped: the published cap has to be the constant the code
    actually runs with, not a number that happened to agree when this was
    written. No fallback -- if the argument moves, this must fail loudly.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and getattr(node.func, "attr", None) == "add_argument"):
            continue
        if not (node.args and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == "--cap"):
            continue
        for kw in node.keywords:
            if kw.arg == "default" and isinstance(kw.value, ast.Constant):
                return int(kw.value.value), node.lineno
    raise RuntimeError(f"no --cap default found in {path}")


def prereg_cap_line(path: Path) -> dict:
    """Locate the preregistered cap sentence and confirm no amendment moved it."""
    hit = None
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "Cap 40/year/genre" in line:
            hit = {"file": str(path.relative_to(ROOT)), "line": i,
                   "text": line.strip()}
            break
    if hit is None:
        raise RuntimeError(f"preregistered cap sentence not found in {path}")
    pat = re.compile(r"cap\s+(of\s+)?\d+|/year/genre", re.I)
    amended = sorted(p.name for p in (ROOT / "docs").glob("PREREG_v0.*_AMENDMENTS.md")
                     if pat.search(p.read_text(encoding="utf-8")))
    hit["amendment_files_checked"] = sorted(
        p.name for p in (ROOT / "docs").glob("PREREG_v0.*_AMENDMENTS.md"))
    hit["amendments_touching_the_cap"] = amended
    return hit


def listing_hits_by_year(path: Path) -> tuple[dict[int, int], dict]:
    """Per-year listing size as the search API itself reported it (total_count).

    Not our row count of the harvest: the point of quoting the API's own total is
    that it is the one number we did not compute, so agreement with the audit
    file is evidence the harvest was complete rather than an assumption.
    """
    log = pd.read_csv(path)
    per_year = {}
    for _, row in log.iterrows():
        window = str(row["window"])
        if window.startswith("year "):
            per_year[int(window.split()[1])] = int(row["total_count"])
    glob = log.loc[log["window"] == "global", "total_count"]
    summary = {
        "requests_logged": int(len(log)),
        "non_200_responses": int((log["status"] != 200).sum()),
        "global_window_total_count": int(glob.iloc[0]) if len(glob) else None,
        "per_year_windows": len(per_year),
        "year_window_span": [min(per_year), max(per_year)] if per_year else None,
        "sum_of_per_year_total_count": int(sum(per_year.values())),
    }
    return per_year, summary


def disposition_table(audit: pd.DataFrame) -> dict:
    counts = audit["status"].value_counts().to_dict()
    known = {name for name, _, _ in STATUS_RULES}
    rows = [{"status": name,
             "n": int(counts.get(name, 0)),
             "assigned_at": f"src/s09a_imf_articleiv_frame.py:{line}",
             "rule": rule}
            for name, line, rule in STATUS_RULES]
    unexpected = sorted(set(counts) - known)
    return {
        "n_listing_hits_audited": int(len(audit)),
        "n_accounted_for": int(sum(r["n"] for r in rows)),
        "statuses_declared_in_code": len(STATUS_RULES),
        "statuses_observed": int(audit["status"].nunique()),
        "statuses_never_triggered": [r["status"] for r in rows if r["n"] == 0],
        "unexpected_statuses_not_in_code_map": unexpected,
        "ordering_caveat": "classify_row() tests these conditions in the order "
                           "listed and returns on the first failure, so a row is "
                           "labelled by its first disqualifying property, not by "
                           "every property it lacks. The counts are a partition "
                           "of the 7,451 listing hits, not independent tallies.",
        "rows": rows,
    }


def replay_draw(frame: pd.DataFrame, frozen: pd.DataFrame, cap: int) -> dict:
    """Re-run the production sampler on the eligible frame and diff the id sets."""
    replay = sample_frame(frame, cap)
    a = set(replay["id"].astype(str))
    b = set(frozen["id"].astype(str))
    per_year = []
    for year in sorted(set(frozen["year"])):
        ra = set(replay.loc[replay["year"] == year, "id"].astype(str))
        rb = set(frozen.loc[frozen["year"] == year, "id"].astype(str))
        per_year.append({"year": int(year),
                         "n_replay": len(ra), "n_frozen": len(rb),
                         "in_replay_not_frozen": len(ra - rb),
                         "in_frozen_not_replay": len(rb - ra)})
    return {
        "sampler": "src/s09_frame_sampler.py:sample_frame",
        "cap_used": cap,
        "n_replay_rows": int(len(replay)),
        "n_frozen_rows": int(len(frozen)),
        "in_replay_not_in_frozen": len(a - b),
        "in_frozen_not_in_replay": len(b - a),
        "n_intersection": len(a & b),
        "exact_match": (a == b) and len(replay) == len(frozen),
        "per_year": per_year,
    }


def within_cell_fragility(frame: pd.DataFrame, frozen: pd.DataFrame,
                          cap: int) -> dict:
    """How much of a cell's draw survives deleting one row that was never drawn?

    The perturbation is deliberately null under the design's own logic: the
    deleted row is an eligible document the sampler did NOT select, so a
    selection-stable procedure would return the identical 40. Any loss measured
    here is the index-shift effect of random.Random.sample over a shorter
    population, which the per-cell seed does not and cannot address.

    Which row to delete is fixed deterministically (the lexicographically first,
    median and last unselected eligible id) so the probe carries no randomness of
    its own. Three positions are run because the damage turns out to depend
    sharply on where in the sorted order the deleted row sits, and a single
    choice would have reported that as one number and hidden the mechanism.
    """
    selected = {int(y): set(g["id"].astype(str))
                for y, g in frozen.groupby("year")}
    cells, isolation_ok = [], True
    for year in sorted(selected):
        cell = frame[frame["year"] == year]
        n_elig = int(len(cell))
        if n_elig <= cap:
            continue                       # nothing was drawn; nothing to disturb
        keep = selected[year]
        # Isolating the cell must reproduce the frozen 40; otherwise the
        # perturbation below would be measuring cell isolation, not deletion.
        isolated = set(sample_frame(cell, cap)["id"].astype(str))
        isolation_ok &= (isolated == keep)
        unselected = sorted(set(cell["id"].astype(str)) - keep)
        entry = {"year": year, "n_eligible": n_elig, "n_selected": len(keep),
                 "isolated_cell_reproduces_frozen_draw": isolated == keep,
                 # An independent redraw of `cap` from the surviving n-1 rows
                 # would retain cap*cap/(n-1) of the original in expectation;
                 # printed so the measured overlap can be read against chance.
                 "expected_overlap_if_redraw_were_independent":
                     round(cap * cap / (n_elig - 1), 2)}
        for label, dropped in (("drop_first_unselected", unselected[0]),
                               ("drop_median_unselected",
                                unselected[len(unselected) // 2]),
                               ("drop_last_unselected", unselected[-1])):
            perturbed = cell[cell["id"].astype(str) != dropped]
            new = set(sample_frame(perturbed, cap)["id"].astype(str))
            order = sorted(cell["id"].astype(str))
            entry[label] = {"dropped_id": "withheld",
                            # position of the deleted row in the sorted cell:
                            # everything after it shifts down by one, which is
                            # what actually perturbs the draw
                            "dropped_rank_in_sorted_cell": order.index(dropped),
                            "rows_shifted_by_deletion":
                                n_elig - 1 - order.index(dropped),
                            "n_eligible_after": int(len(perturbed)),
                            "survivors_of_original_draw": len(new & keep),
                            "displaced": len(keep - new)}
        cells.append(entry)

    def stats(label: str) -> dict:
        vals = [c[label]["survivors_of_original_draw"] for c in cells]
        return {"mean_survivors": round(sum(vals) / len(vals), 3),
                "min_survivors": min(vals), "max_survivors": max(vals),
                "mean_share_of_draw_retained": round(sum(vals) / len(vals) / cap, 4)}

    exp = [c["expected_overlap_if_redraw_were_independent"] for c in cells]
    return {
        "probe": "delete one UNSELECTED eligible row from a cap-binding year "
                 "cell, redraw that cell through sample_frame at the same cap, "
                 "count how many of the original selections survive",
        "cells_probed": len(cells),
        "years_probed": [c["year"] for c in cells],
        "all_isolated_cells_reproduced_frozen_draw": bool(isolation_ok),
        "drop_first_unselected": stats("drop_first_unselected"),
        "drop_median_unselected": stats("drop_median_unselected"),
        "drop_last_unselected": stats("drop_last_unselected"),
        "mean_expected_overlap_if_redraw_were_independent":
            round(sum(exp) / len(exp), 3),
        "reading": "The per-cell seed buys no stability against a change in the "
                   "population of the cell itself, and the size of the loss "
                   "depends on WHERE the deleted row sits in the sorted cell. "
                   "sample() draws positional indices into the sorted id list, "
                   "so deleting a row shifts the position of every row after it "
                   "and the same index stream then lands on different "
                   "documents. Delete the first unselected id and nearly the "
                   "whole cell shifts, giving survival close to what an "
                   "independent redraw would produce; delete the last and "
                   "almost nothing shifts, so most of the draw survives. Both "
                   "are reported because the favourable case is not evidence of "
                   "stability -- a real frame refresh adds and removes rows "
                   "throughout the order, not only at its end. The seed's "
                   "guarantee is across cells (src/percell_seed.py:1-2) and "
                   "that guarantee holds; this is the complementary weakness, "
                   "stated with numbers rather than left implicit.",
        "cells": cells,
    }


def column_inventory(frame: pd.DataFrame, audit: pd.DataFrame,
                     frozen: pd.DataFrame) -> dict:
    frame_cols = list(frame.columns)
    audit_cols = list(audit.columns)
    present = {c.lower() for c in frame_cols} | {c.lower() for c in audit_cols}
    absent = [f for f in REQUESTED_STANDARDISATION if f not in present]

    ont = None
    if ONTOLOGY.exists():
        o = pd.read_csv(ONTOLOGY)
        # data/meta/country_ontology.csv stores 'IMF' while the frame and
        # the sampler use 'imf'. Matching one casing worked by coincidence, and
        # an empty slice reports "0 missing", which is the most reassuring
        # possible answer to a broken join. Fold the case and refuse an empty
        # result outright.
        imf = o[o["institution"].astype(str).str.lower() == "imf"]
        if imf.empty:
            raise SystemExit("[imf-frame] the country_ontology join returned no "
                             "IMF rows; refusing to report coverage from an "
                             "empty slice")
        ont = {
            "file": str(ONTOLOGY.relative_to(ROOT)),
            "columns": list(o.columns),
            "imf_slice_rows": int(len(imf)),
            "imf_ids_match_frame_exactly":
                set(imf["id"].astype(str)) == set(frame["id"].astype(str)),
            "region_missing_in_imf_slice": int(imf["region"].isna().sum()),
            "income_missing_in_imf_slice": int(imf["income_current"].isna().sum()),
            "caveat": "income_current is a single current-vintage classification "
                      "applied to documents spanning 1999-2025; it is not the "
                      "income group in force in each document's own year.",
        }

    return {
        "frame_columns": frame_cols,
        "audit_columns": audit_cols,
        "frozen_sample_columns": list(frozen.columns),
        "provenance_columns_added_by_sampler":
            [c for c in frozen.columns if c not in frame_cols],
        "requested_by_reviewer": REQUESTED_STANDARDISATION,
        "requested_and_absent_from_both_csvs": absent,
        "title_derived_flags_in_frame": {
            "combined_with_program_true": int(frame["combined_with_program"].sum()),
            "combined_with_program_false":
                int((~frame["combined_with_program"]).sum()),
            "fssa_cotitled_true": int(frame["fssa_cotitled"].sum()),
            "fssa_cotitled_false": int((~frame["fssa_cotitled"]).sum()),
        },
        "combined_with_program_is_not_programme_status":
            "combined_with_program is a TITLE-token flag set at "
            "src/s09a_imf_articleiv_frame.py:49 and 86 when the title matches "
            "'review under', 'arrangement', 'extended credit', 'stand-by', "
            "'extended fund facility', 'policy coordination instrument' or "
            "'flexible credit line'. It records that a document is co-titled "
            "with a programme review. It is NOT a classification of whether the "
            "country was under a Fund programme, and must not be read as one.",
        "programme_status_in_repository": "not recorded in repository; no "
            "country-level or document-level Fund-programme status field exists "
            "in data/meta or config, and no code produces one.",
        "region_and_income_available_by_join": ont,
    }


def main() -> int:
    audit = pd.read_csv(AUDIT)
    frame = pd.read_csv(FRAME)
    frozen = pd.read_csv(FROZEN)

    cap, cap_line = cap_default_from_source(SAMPLER_SRC)
    prereg = prereg_cap_line(PREREG)
    hits, harvest = listing_hits_by_year(REQLOG)

    years = sorted(set(frame["year"]) | set(frozen["year"]))
    elig = frame["year"].value_counts().to_dict()
    samp = frozen["year"].value_counts().to_dict()

    per_year = []
    for y in years:
        n_e, n_s = int(elig.get(y, 0)), int(samp.get(y, 0))
        per_year.append({
            "year": int(y),
            "n_listing_hits": hits.get(int(y)),
            "n_eligible": n_e,
            "n_sampled": n_s,
            "inclusion_probability": round(n_s / n_e, 6) if n_e else None,
            "cap_binds": n_e > cap,
            "cell_seed": cell_seed(INSTITUTION, GENRE, int(y)),
        })

    below_cap = [r["year"] for r in per_year if r["n_eligible"] < cap]
    census_years = [r["year"] for r in per_year if r["inclusion_probability"] == 1.0]

    result = {
        "question": "Is the IMF Article IV comparator a capped annual "
                    "cross-section, and if so under what published rule, from "
                    "what eligible frame, with what inclusion probabilities?",
        "answer_in_one_line":
            f"It is a capped annual cross-section: a preregistered cap of {cap} "
            f"per year-genre cell applied by equal-probability SRS without "
            f"replacement inside each cell, drawn from a {len(frame)}-row "
            f"eligible frame that was itself distilled from "
            f"{len(audit)} audited listing hits.",
        "inputs": {str(p.relative_to(ROOT)): {"rows": n, "sha256": sha256_file(p)}
                   for p, n in ((AUDIT, len(audit)), (FRAME, len(frame)),
                                (FROZEN, len(frozen)),
                                (REQLOG, harvest["requests_logged"]))},
        "cap": {
            "value": cap,
            "literal_constant_at": f"src/s09_frame_sampler.py:{cap_line}",
            "preregistered_at": prereg,
            "reason": "Preregistered before Stage-B retrieval as a fixed "
                      "per-cell ceiling. It bounds retrieval cost and keeps "
                      "year cells comparable in size, so that the later years "
                      "cannot dominate a pooled estimate through sheer volume.",
            "eligible_spread_measured": {
                # An earlier version said later years hold "three to five
                # times" the eligible documents of 1999-2001. That was an
                # estimate, and this tool's own table contradicts it. Measured.
                "mean_eligible_1999_2001": round(
                    float(frame[frame["year"] <= 2001]
                          .groupby("year").size().mean()), 3),
                "mean_eligible_2002_2025": round(
                    float(frame[frame["year"] >= 2002]
                          .groupby("year").size().mean()), 3),
                "min_eligible_2002_2025": int(
                    frame[frame["year"] >= 2002].groupby("year").size().min()),
                "max_eligible_2002_2025": int(
                    frame[frame["year"] >= 2002].groupby("year").size().max()),
                "ratio_of_means": round(
                    float(frame[frame["year"] >= 2002].groupby("year").size().mean()
                          / frame[frame["year"] <= 2001].groupby("year").size().mean()),
                    3),
            },
            "cap_is_not_the_reason_1999_is_short":
                "1999 carries 24 documents because the eligible universe for "
                "1999 is 24. The cap never bound there.",
        },
        "selection_algorithm": {
            "design": "equal-probability simple random sampling WITHOUT "
                      "replacement within each (institution, genre, year) cell",
            "implementation": "src/s09_frame_sampler.py:26-31",
            "steps": [
                "group the eligible frame by (institution, genre, year), sorted",
                "sort the cell's ids lexicographically as strings -- this fixes "
                "the population order independently of input row order",
                "if the cell holds more than cap ids, draw cap of them with "
                "percell_seed.cell_rng(institution, genre, year).sample",
                "sort the drawn ids again and keep the matching rows",
            ],
            "tie_breaking":
                "There are no ties to break in the draw itself: ids are unique "
                "Country Report numbers, so the lexicographic sort at "
                "src/s09_frame_sampler.py:28 is a total order and the sampler "
                "refuses duplicate ids outright (line 23-24). Ties are broken "
                "earlier, when the frame is built: resolve_revisions "
                "(src/s09a_imf_articleiv_frame.py:115-126) keeps one unit per "
                "report number by latest pub_date, then a corrigendum/revised "
                "title, then the lexicographically smallest url.",
        },
        "seeds": {
            "master_seed": MASTER_SEED,
            "declared_at": "src/percell_seed.py:6",
            "derivation": 'cell_seed = int(sha256(f"{master}|{institution}|'
                          '{genre}|{year}").hexdigest()[:16], 16), seeding an '
                          "independent random.Random per cell "
                          "(src/percell_seed.py:10-11, 13-15)",
            "scope": "per cell, not global -- adding, removing or reordering any "
                     "other stratum cannot change this cell's draw",
            "per_year_cell_seeds_published_in": "the per-year table, column "
                                                "cell_seed",
        },
        "harvest": harvest,
        "harvest_reconciliation": {
            "audit_rows": int(len(audit)),
            "sum_of_per_year_listing_total_count":
                harvest["sum_of_per_year_total_count"],
            "global_window_total_count": harvest["global_window_total_count"],
            "per_year_total_count_matches_audit_rows_every_year": bool(all(
                int(audit[audit["year"] == y].shape[0]) == c
                for y, c in hits.items())),
            "note": "The per-year windows, not the global window, are the "
                    "harvest: the global request returned one page of 1000 "
                    "against a reported total of 7,451, so it was never the "
                    "retrieval path.",
        },
        "per_year_table": per_year,
        "per_year_table_notes": {
            "n_listing_hits": "the search API's own total_count for that year "
                              "window, from the request log -- not our count",
            "inclusion_probability": "n_sampled / n_eligible, the design "
                                     "probability for that cell",
            "window": f"{years[0]}-{years[-1]}",
            "years_below_cap": below_cap,
            "years_sampled_as_a_census": census_years,
            "declared_build_window": "1994-2025 (--year-lo / --year-hi defaults, "
                                     "src/s09a_imf_articleiv_frame.py:644-645); "
                                     "the frame starts at 1999 because no "
                                     "earlier listing hit survived eligibility, "
                                     "not because 1999 was chosen as a start.",
        },
        "disposition_of_all_listing_hits": disposition_table(audit),
        "reproducibility_replay": replay_draw(frame, frozen, cap),
        "within_cell_fragility": within_cell_fragility(frame, frozen, cap),
        "columns": column_inventory(frame, audit, frozen),
    }

    pre99 = audit[audit["year"] < 1999]
    result["limitations"] = [
        "The comparator is a capped cross-section, not a census, in every year "
        "except 1999. Inclusion probabilities range from "
        f"{min(r['inclusion_probability'] for r in per_year):.3f} to "
        f"{max(r['inclusion_probability'] for r in per_year):.3f} and are "
        "published per year above; any pooled statistic that ignores them is "
        "weighting years by cap, not by the Fund's output.",
        "The per-cell seed protects across cells only. Deleting a single "
        "eligible row that was never selected leaves, on average over the 26 "
        "capped cells, "
        f"{result['within_cell_fragility']['drop_first_unselected']['mean_survivors']}"
        f", "
        f"{result['within_cell_fragility']['drop_median_unselected']['mean_survivors']}"
        f" or "
        f"{result['within_cell_fragility']['drop_last_unselected']['mean_survivors']}"
        f" of that cell's {cap} selections in place, depending on whether the "
        "deleted row sits first, mid-order or last in the sorted cell. A future "
        "frame refresh that adds or drops rows will therefore not reproduce "
        "this sample, even with the same seed and the same code. The frozen "
        "CSV, not the seed, is what makes this draw recoverable.",
        "Disposition counts are ordered-first-failure labels, not independent "
        "reasons: a title with no country prefix is never also tested for a "
        "report number.",
        f"{len(pre99)} listing hits dated before 1999 were all excluded, "
        f"{int(pre99['status'].isin(['unmapped_country', 'excluded_no_country_prefix', 'excluded_regional_multicountry']).sum())} "
        "of them at the country-name step -- excluded_regional_multicountry is "
        "assigned inside the alias lookup's own failure branch "
        "(src/s09a_imf_articleiv_frame.py:103), so it belongs to that step. "
        "Whether that is a genuine absence of Article IV listings in that "
        "period or an alias-table gap is not settled by anything in this "
        "repository.",
        "region and income group are not columns of either CSV; they are "
        "available only through a join to data/meta/country_ontology.csv, and "
        "the income classification there is single-vintage. Programme status is "
        "not recorded in the repository at all.",
        f"The frozen sample carries an analysis_eligible column and it is blank "
        f"in all {len(frozen)} rows -- the sampler writes the column and nothing "
        f"backfills it. So this file records documents DRAWN, not documents "
        f"analysed, and the two happen to coincide only because "
        f"docs/IMF_RETRIEVAL_20260820.md records {len(frozen)} sampled -> "
        f"{len(frozen)} downloaded -> {len(frozen)} verified. That retrieval "
        f"record, not this column, is what closes the gap.",
    ]
    result["needs_human_review"] = [
        "Whether the 1999 start is reported as a design boundary or as a "
        "coverage limit. The build window was declared 1994-2025 and the data "
        "produced 1999; these are different claims and a historian should pick "
        "the wording.",
        f"Whether the {int((audit['status'] == 'unmapped_country').sum())} "
        f"unmapped_country rows should be worked down by extending the alias "
        f"table before the manuscript quotes {len(frame)} as the eligible "
        f"universe. classify_row returns on first failure, so the share "
        f"depends on which denominator is meant, and the wider one understates "
        f"the gap: "
        f"{100 * (audit['status'] == 'unmapped_country').mean():.1f} percent of "
        f"all {len(audit)} listing hits, but "
        f"{100 * (audit['status'] == 'unmapped_country').sum() / int((~audit['status'].isin(['excluded_selected_issues', 'excluded_not_article_iv', 'excluded_language', 'excluded_no_country_prefix'])).sum()):.1f} "
        f"percent of the "
        f"{int((~audit['status'].isin(['excluded_selected_issues', 'excluded_not_article_iv', 'excluded_language', 'excluded_no_country_prefix'])).sum())} "
        f"rows that actually reached the alias lookup. The frame is a lower "
        f"bound until that is decided.",
        "Whether inclusion probabilities should be carried into the estimator "
        "as weights, or the cap defended as a deliberate equal-cell design. "
        "This tool publishes the probabilities and takes no position.",
        "Whether region and income group are joined in for standardisation "
        "given that the available income classification is current-vintage and "
        "therefore anachronistic for the early years.",
    ]

    # What the unmapped rows actually are.
    #
    # The open question above asks whether the alias table should be worked down
    # before 2,788 is quoted as an eligible universe, and the manuscript answered
    # it by calling those rows "documents the pipeline could not place". That was
    # more agnostic than the evidence requires and it made our own frame look
    # weaker than it is: the listing carries a document-type field, and joining
    # it back settles all but a couple of rows. Reported here so the sentence in
    # the supplement is regenerated rather than asserted.
    LISTING = ROOT / "data" / "meta" / "imf_articleiv_listing.csv"
    if LISTING.exists():
        listing = pd.read_csv(LISTING, low_memory=False)
        if {"url", "src_imftype", "src_imfseries"} <= set(listing.columns):
            um = audit[audit["status"] == "unmapped_country"]
            j = um.merge(listing[["url", "src_imftype", "src_imfseries"]],
                         on="url", how="left")
            # And by YEAR, because the reviewer's real question is whether the
            # alias failures are era-selective -- a frame that loses documents
            # mostly in the pre-period would bias a pre/post contrast. The
            # share does swing enormously (over 80% in 1999, near zero from
            # 2017), so the by-type breakdown has to be read per year before
            # anything is concluded from it.
            j["_year"] = j["year"]
            by_year = {}
            for yy, g in j[(j["year"] >= 1999) & (j["year"] <= 2025)].groupby("year"):
                inc = int(((audit["status"] == "included") &
                           (audit["year"] == yy)).sum())
                types = {str(k): int(v) for k, v in
                         g["src_imftype"].value_counts(dropna=False).items()}
                by_year[int(yy)] = {
                    "included": inc, "unmapped": int(len(g)),
                    "unmapped_share": round(len(g) / (inc + len(g)), 4)
                    if inc + len(g) else None,
                    "by_type": types,
                }
            DISCONTINUED = ("Public Information Notice", "Press Release")
            early = [v for k, v in by_year.items() if k <= 2016]
            n_early = sum(v["unmapped"] for v in early)
            n_early_disc = sum(sum(v["by_type"].get(t, 0) for t in DISCONTINUED)
                               for v in early)
            result["unmapped_country_by_year"] = {
                "years": by_year,
                "share_1999_2016": round(
                    n_early / (sum(v["included"] for v in early) + n_early), 4),
                "share_2017_2025": round(
                    sum(v["unmapped"] for k, v in by_year.items() if k >= 2017)
                    / max(1, sum(v["included"] + v["unmapped"]
                                 for k, v in by_year.items() if k >= 2017)), 4),
                "discontinued_share_of_early_unmapped":
                    round(n_early_disc / n_early, 4) if n_early else None,
                "reading": (
                    "The era gradient is the lifecycle of two publication types, "
                    "not era-selective failure on staff reports. Public "
                    "Information Notices appear 1999-2013 and stop; press "
                    "releases run to 2016 and stop. Together they are the great "
                    "majority of every unmapped row before 2017, after which "
                    "the unmapped count is a handful a year. If the alias table "
                    "were failing on Article IV staff reports we would expect "
                    "the residue to be staff reports; it is not."),
            }
            result["unmapped_country_types"] = {
                "n": int(len(um)),
                "n_joined": int(j["src_imftype"].notna().sum()),
                "by_src_imftype": {str(k): int(v) for k, v in
                                   j["src_imftype"].value_counts(dropna=False).items()},
                "n_with_empty_src_imfseries": int(j["src_imfseries"].isna().sum()),
                "reading": ("src_imftype is the IMF's own content-type label on "
                            "the listing row. These rows are established "
                            "non-staff-report publication types, not documents "
                            "of unknown kind: 2,788 is a lower bound because "
                            "the alias table did not place a country prefix, "
                            "not because the excluded rows might be Article IV "
                            "staff reports."),
            }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=1), encoding="utf-8")

    fields = ["year", "n_listing_hits", "n_eligible", "n_sampled",
              "inclusion_probability", "cap_binds", "cell_seed"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in per_year:
            w.writerow(row)

    rep = result["reproducibility_replay"]
    frag = result["within_cell_fragility"]
    print(f"[frame-pub] cap {cap} (src/s09_frame_sampler.py:{cap_line}; "
          f"prereg {prereg['file']}:{prereg['line']})")
    print(f"[frame-pub] {len(audit)} listing hits -> {len(frame)} eligible "
          f"-> {len(frozen)} sampled over {years[0]}-{years[-1]}")
    print(f"[frame-pub] replay vs frozen: +{rep['in_replay_not_in_frozen']} "
          f"-{rep['in_frozen_not_in_replay']}  exact_match={rep['exact_match']}")
    print(f"[frame-pub] within-cell fragility over {frag['cells_probed']} cells, "
          f"mean of {cap} selections surviving one unselected deletion: "
          f"first {frag['drop_first_unselected']['mean_survivors']}, "
          f"median {frag['drop_median_unselected']['mean_survivors']}, "
          f"last {frag['drop_last_unselected']['mean_survivors']} "
          f"(independent-redraw expectation "
          f"{frag['mean_expected_overlap_if_redraw_were_independent']})")
    print(f"[frame-pub] absent columns: "
          f"{result['columns']['requested_and_absent_from_both_csvs']}")
    print(f"[frame-pub] wrote {OUT_JSON.relative_to(ROOT)} and "
          f"{OUT_CSV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
