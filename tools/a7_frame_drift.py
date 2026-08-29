#!/usr/bin/env python3
"""A7 — sample the Stage-B WB frame and decompose its drift from the sealed one.

The sealed WB sample (`data/meta/frozen_sampling_v1.csv`, 2,818 rows) and the
Stage-B sample differ for TWO independent reasons, and reporting one number for
both would hide the more interesting one:

  FRAME drift    the world changed -- documents published, withdrawn or
                 re-catalogued between the Stage-A capture (2026-08-06,
                 `data/meta/metadata_{stratum}.jsonl`) and the Stage-B capture
                 (`data/meta/wb_p1p2_frame.csv`).

  SAMPLER change the sealed sample was drawn by `s01`'s SINGLE GLOBAL RNG
                 consumed across strata. PREREG Appendix B.7 specifies the
                 stable per-cell sampler, seed_cell =
                 SHA256("20260806|{institution}|{genre}|{year}"), under which
                 "adding or removing any other stratum cannot change a cell's
                 draw". The sealed draw does not satisfy that rule; the Stage-B
                 draw does. So a document can leave the sample without anything
                 in the world having changed.

The decomposition isolates them by re-drawing the OLD frame under the NEW
sampler:

    sealed            vs  percell(A)   -> sampler change alone
    percell(A)        vs  percell(B)   -> frame drift alone
    sealed            vs  percell(B)   -> combined (what the analysis runs on)

The headline the prior-inspection ruling needs (docs/RULING_20260820_prior_
inspection.md §3) is the last row's overlap: of the documents the confirmatory
P1/P2 analysis will run on, how many are the same documents whose outcomes were
inspected at Stage-A.

Caps and cutoff follow the preregistration: 40/year/genre for icr and pad,
uncapped for annual_report (`per_year_cap: null`), confirmatory cutoff
publication date <= 2025-12-31 (§11.4). This tool REPORTS; it writes no frozen
sample. Freezing is `s09_frame_sampler`'s job, run deliberately.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from percell_seed import cell_rng  # noqa: E402

INSTITUTION = "wb"
CUTOFF = "2025-12-31"
STRATA = {"annual_report": None, "icr": 40, "pad": 40}   # None = uncapped


def eligible(docdt: str) -> bool:
    d = (docdt or "").strip()[:10]
    return len(d) == 10 and d[4] == "-" and d[7] == "-" and d <= CUTOFF


def load_stage_a() -> dict[tuple[str, int], set[str]]:
    """Stage-A universe from the s01 jsonl dumps, keyed (genre, year)."""
    cells: dict[tuple[str, int], set[str]] = {}
    for genre in STRATA:
        path = ROOT / "data" / "meta" / f"metadata_{genre}.jsonl"
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                r = json.loads(line)
                docdt = str(r.get("docdt", ""))
                if not eligible(docdt):
                    continue
                cells.setdefault((genre, int(docdt[:4])), set()).add(str(r["id"]))
    return cells


def load_stage_b() -> dict[tuple[str, int], set[str]]:
    cells: dict[tuple[str, int], set[str]] = {}
    with (ROOT / "data" / "meta" / "wb_p1p2_frame.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["confirmatory_eligible"] != "True":
                continue
            cells.setdefault((r["genre"], int(r["year"])), set()).add(r["id"])
    return cells


def load_sealed(apply_cutoff: bool = True):
    """The sealed sample, optionally reduced to the confirmatory window.

    The Stage-A draw predates the §11.4 cutoff and carries 2026 rows (40 icr +
    40 pad). Comparing it raw against a cutoff-applied redraw would charge those
    80 rows to the sampler, which did not cause them. They are reported as their
    own component instead."""
    cells: dict[tuple[str, int], set[str]] = {}
    dropped = 0
    with (ROOT / "data" / "meta" / "frozen_sampling_v1.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if apply_cutoff and not eligible(r.get("docdt", "")):
                dropped += 1
                continue
            cells.setdefault((r["stratum"], int(r["year"])), set()).add(r["id"])
    return cells, dropped


def percell_sample(cells: dict[tuple[str, int], set[str]]) -> dict[tuple[str, int], set[str]]:
    """PREREG App. B.7 draw: independent RNG per cell, cap per stratum."""
    out = {}
    for (genre, year), ids in cells.items():
        cap = STRATA[genre]
        sid = sorted(ids)
        if cap is not None and len(sid) > cap:
            sid = sorted(cell_rng(INSTITUTION, genre, year).sample(sid, cap))
        out[(genre, year)] = set(sid)
    return out


def flatten(cells) -> set[tuple[str, int, str]]:
    return {(g, y, i) for (g, y), ids in cells.items() for i in ids}


def compare(label, left, right, rows):
    L, R = flatten(left), flatten(right)
    both = L & R
    rows.append({
        "comparison": label,
        "left_n": len(L), "right_n": len(R),
        "shared": len(both),
        "only_left": len(L - R), "only_right": len(R - L),
        "share_of_right_already_in_left": (f"{len(both) / len(R):.4f}" if R else ""),
    })
    return L, R


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "data" / "meta" / "a7_drift_report.csv"))
    args = ap.parse_args()

    A, B = load_stage_a(), load_stage_b()
    sealed, sealed_dropped = load_sealed(apply_cutoff=True)
    pA, pB = percell_sample(A), percell_sample(B)
    print(f"CUTOFF component: {sealed_dropped} sealed row(s) fall outside the "
          f"confirmatory window (docdt > {CUTOFF}) and are excluded by PREREG "
          f"§11.4 before any other comparison.\n")

    # ---- frame-level drift, per stratum
    frame_rows = []
    for genre in sorted(STRATA):
        a = {i for (g, _), ids in A.items() if g == genre for i in ids}
        b = {i for (g, _), ids in B.items() if g == genre for i in ids}
        frame_rows.append({"stratum": genre, "stage_a": len(a), "stage_b": len(b),
                           "added": len(b - a), "withdrawn": len(a - b),
                           "unchanged": len(a & b)})

    print("FRAME drift (confirmatory-eligible universe, docdt <= %s)" % CUTOFF)
    print(f"{'stratum':16s} {'stage_A':>8s} {'stage_B':>8s} {'added':>7s} "
          f"{'withdrawn':>10s} {'unchanged':>10s}")
    for r in frame_rows:
        print(f"{r['stratum']:16s} {r['stage_a']:8d} {r['stage_b']:8d} "
              f"{r['added']:7d} {r['withdrawn']:10d} {r['unchanged']:10d}")

    # ---- sample-level decomposition
    rows = []
    compare("sealedCUT_vs_percell_stageA__SAMPLER_ONLY", sealed, pA, rows)
    compare("percellA_vs_percellB__FRAME_ONLY", pA, pB, rows)
    compare("sealedCUT_vs_percell_stageB__COMBINED", sealed, pB, rows)

    print("\nSAMPLE drift decomposition")
    for r in rows:
        print(f"  {r['comparison']:42s} left={r['left_n']:5d} right={r['right_n']:5d} "
              f"shared={r['shared']:5d} only_left={r['only_left']:5d} "
              f"only_right={r['only_right']:5d}")

    combined = rows[-1]
    print(f"\nPRIOR-INSPECTION HEADLINE (ruling §3): "
          f"{combined['shared']} of {combined['right_n']} documents in the "
          f"Stage-B confirmatory sample "
          f"({float(combined['share_of_right_already_in_left']):.1%}) are the same "
          f"documents whose outcomes were inspected at Stage-A.")

    out = Path(args.out)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(frame_rows[0]))
        w.writeheader()
        w.writerows(frame_rows)
        fh.write("\n")
        w2 = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w2.writeheader()
        w2.writerows(rows)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
