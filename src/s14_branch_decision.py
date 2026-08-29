"""Deterministic P0 branch decision (PREREG v0.6 SS2; round-7 blockers on G3
and orchestration). Evaluates G1..G4 per candidate genre in the FROZEN
priority order (cem, scd, cpf), freezes the FIRST candidate passing all four
gates as P0 and never evaluates later candidates (one-way rule); if none
passes, the family is {P1, P2}. Metadata- and simulation-input only; no
outcome data. The output is write-once: an existing decision file refuses to
be overwritten (SS11 immutability).

Executable G3 reading (declared in v0.6 SS2): a country cell is "supported in
both institutions" iff its ISO3 appears at least once in EACH institution's
full included frame; the gate requires >= 80% of the candidate's post-period
(2023-2025) documents to lie in supported cells.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

G2_MIN_COMMON_PRE, G2_MIN_POST = 25, 3
G3_MIN_SUPPORT = 0.80
G4_MAX_MDE80 = 0.60
PRIORITY = ("cem", "scd", "cpf")
POST = (2023, 2025)


def g3_support(cand_frame: pd.DataFrame, imf_frame: pd.DataFrame,
               post=POST) -> dict:
    wb_c = set(cand_frame["country_iso3"].dropna())
    imf_c = set(imf_frame["country_iso3"].dropna())
    both = wb_c & imf_c
    pmask = (cand_frame["year"] >= post[0]) & (cand_frame["year"] <= post[1])
    post_docs = cand_frame[pmask]
    n = int(len(post_docs))
    k = int(post_docs["country_iso3"].isin(both).sum())
    share = k / n if n else 0.0
    return {"n_post_docs": n, "n_supported": k, "share": share,
            "ok": bool(n > 0 and share >= G3_MIN_SUPPORT)}


def decide(wb_frame: pd.DataFrame, imf_frame: pd.DataFrame,
           g1_scores: dict, mde80: dict,
           priority=PRIORITY) -> dict:
    from s09b_wb_p0_frame import g2_coverage
    g2_all = g2_coverage(wb_frame, imf_frame) or {}
    out = {"priority": list(priority), "candidates": {}, "family": None}
    for idx, genre in enumerate(priority):
        cand = wb_frame[wb_frame["genre"] == genre]
        g1 = g1_scores.get(genre)
        rec = {"g1": {"ok": bool(g1 and g1.get("g1_pass")), "detail": g1}}
        g2 = (g2_all.get("per_genre", {}) or {}).get(genre, g2_all.get(genre, {}))
        rec["g2"] = {"ok": bool(g2.get("g2_metadata_ok")), "detail": g2}
        rec["g3"] = (g3_support(cand, imf_frame) if len(cand)
                     else {"ok": False, "n_post_docs": 0, "n_supported": 0,
                           "share": 0.0})
        m = mde80.get(genre)
        rec["g4"] = {"ok": bool(m is not None and m <= G4_MAX_MDE80),
                     "mde80": m}
        rec["passes_all"] = all(rec[g]["ok"] for g in ("g1", "g2", "g3", "g4"))
        out["candidates"][genre] = rec
        if rec["passes_all"]:
            out["family"] = {"P0": genre}
            for later in priority[idx + 1:]:
                out["candidates"][later] = {
                    "status": "not_evaluated_one_way_rule"}
            break
    if out["family"] is None:
        out["family"] = {"P1P2": True}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wb-frame", required=True)
    ap.add_argument("--imf-frame", required=True)
    ap.add_argument("--g1-scores", required=True,
                    help="JSON: {genre: g1_audit.score() dict}")
    ap.add_argument("--mde", required=True,
                    help="JSON: {genre: mde80 float} from mde_sim --family p0")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"[s14] REFUSING to overwrite existing decision "
                         f"{out} (SS11 write-once).")
    res = decide(pd.read_csv(a.wb_frame), pd.read_csv(a.imf_frame),
                 json.loads(Path(a.g1_scores).read_text()),
                 json.loads(Path(a.mde).read_text()))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2))
    print(f"[s14] family decision: {res['family']} -> {out}")


if __name__ == "__main__":
    main()
