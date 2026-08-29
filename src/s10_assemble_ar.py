"""s10 — Annual Report fiscal-year assembly (D11) + sibling-organization filter.

Pre-freeze decision (2026-08-06, DESIGN_RATIONALE deviations log): sibling reports
(IFC/MIGA/ICSID) stay in the frozen sample and are filtered HERE, with every
decision logged to data/meta/ar_assembly_log.csv. Borderline titles are flagged
needs_review and EXCLUDED from the assembled series until a human approves them —
they are never silently resolved.

Output: data/text_assembled/annual_report/<year>.txt (volumes deduplicated by
(repnb, volnb), ordered, concatenated per fiscal-year bucket) and
data/features/ar_fy_features.csv (classic + marker features per assembled year).
"""
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path
from utils import ROOT, load_config
from textstats import compute_classic, compute_markers

# Ordered rules; first match wins. Provenance: title inventory of the 331 sampled
# AR-facet docs (2026-08-07). Anything unmatched -> needs_review, excluded.
EXCLUDE_RULES = [
    ("IFC", re.compile(r"international finance corporation|\bifc\b", re.I)),
    ("MIGA", re.compile(r"multilateral investment guarantee|\bmiga\b", re.I)),
    ("ICSID", re.compile(r"settlement of investment disputes|\bicsid\b|\bciadi\b", re.I)),
    ("ICSID_nonlatin", re.compile(r"[؀-ۿ]")),  # Arabic-script ICSID title
]
INCLUDE_RULES = [
    ("WB_AR", re.compile(r"^the world bank annual report", re.I)),
    ("WB_AR", re.compile(r"^world bank annual report", re.I)),
    ("WB_AR_early", re.compile(r"^world bank[ ,]+.*\bannual report\b", re.I)),
    ("IBRD_AR", re.compile(
        r"^international bank for reconstruction and development.*annual report", re.I)),
]

def classify(title: str) -> tuple[str, str]:
    """-> (decision, rule) with decision in {include, exclude, review}."""
    t = " ".join(title.split())
    for rule, rx in EXCLUDE_RULES:
        if rx.search(t):
            return "exclude", rule
    for rule, rx in INCLUDE_RULES:
        if rx.search(t):
            return "include", rule
    return "review", "unmatched_title"

# The seven borderline titles, resolved 2026-08-07 (decision delegated by Ali;
# per-document rationale in DESIGN_RATIONALE deviations log). id -> (decision, rule).
RESOLVED_REVIEW = {
    "438429":   ("exclude", "resolved:board_meeting_proceedings"),   # 1946 governors' meeting
    "1561354":  ("exclude", "resolved:IDA_separate_series"),         # IDA AR 1960-61
    "25251052": ("exclude", "resolved:IDA_separate_series"),         # IDA AR 1961-62
    "1561253":  ("exclude", "resolved:IDA_separate_series"),         # IDA AR 1962-63
    "439284":   ("exclude", "resolved:thematic_env_series"),         # WB & environment 1990
    "34063779": ("include", "resolved:AR_volume_by_repnb"),          # AR2008 Vol.5/32 (repnb 46256)
    "30458125": ("exclude", "resolved:translation_D11"),             # Relatório Principal 2018
}

def volume_sort_key(row: dict) -> tuple:
    return (str(row.get("repnb", "")), str(row.get("volnb", "")), str(row["id"]))

# Function-word set for the prose-likeness gate. Legitimate assembled AR units sit
# at >=0.20 share; cover-sheet-only and table-dump extractions sit at <=0.01
# (calibrated on all 73 pre-gate units, 2026-08-07 third-eye audit).
STOPWORDS = frozenset(["the", "of", "and", "to", "in", "a", "for", "on", "with",
                       "is", "by", "as", "that", "at", "from"])

def unit_qc(text: str, qc_cfg: dict) -> tuple[bool, int, float]:
    """Extraction-quality gate for an assembled fiscal-year unit.
    -> (passes, n_tokens, stopword_share). A frozen manifest guarantees provenance,
    not measurement validity — defective units must not enter the series."""
    toks = re.findall(r"[A-Za-z']+", text.lower())
    n = len(toks)
    share = (sum(1 for t in toks if t in STOPWORDS) / n) if n else 0.0
    ok = n >= qc_cfg["min_tokens"] and share >= qc_cfg["min_stopword_share"]
    return ok, n, share

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    cfg = load_config(ap.parse_args().config)
    frozen = ROOT / "data" / "meta" / f"frozen_sampling_v{cfg['sampling_version']}.csv"
    with open(frozen, newline="", encoding="utf-8") as f:
        ar = [r for r in csv.DictReader(f) if r["stratum"] == "annual_report"]
    # volnb lives in the full metadata dump, not the frozen CSV
    volnb = {}
    meta_path = ROOT / "data" / "meta" / "metadata_annual_report.jsonl"
    if meta_path.exists():
        import json
        with open(meta_path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                volnb[str(rec.get("id", ""))] = str(rec.get("volnb", ""))
    log_rows, per_year = [], {}
    for r in sorted(ar, key=lambda x: (x["year"], x["id"])):
        decision, rule = classify(r["display_title"])
        if r["id"] in RESOLVED_REVIEW:
            decision, rule = RESOLVED_REVIEW[r["id"]]
        txt = ROOT / "data" / "text" / "annual_report" / r["year"] / f"{r['id']}.txt"
        has_text = txt.exists() and txt.stat().st_size > 0
        row = dict(r, volnb=volnb.get(r["id"], ""), decision=decision, rule=rule,
                   has_text=int(has_text))
        log_rows.append(row)
        if decision == "include" and has_text:
            per_year.setdefault(r["year"], []).append(row)
    # promote review rows that are volumes of an included report (same year+repnb)
    for row in log_rows:
        if row["decision"] == "review" and row["has_text"]:
            kept = per_year.get(row["year"], [])
            if row["repnb"] and any(k["repnb"] == row["repnb"] for k in kept):
                row["decision"], row["rule"] = "include", "repnb_volume_of_AR"
                kept.append(row)
    out_dir = ROOT / "data" / "text_assembled" / "annual_report"
    out_dir.mkdir(parents=True, exist_ok=True)
    feat_rows, qc_rows = [], []
    for year in sorted(per_year):
        rows = sorted(per_year[year], key=volume_sort_key)
        seen, parts, ids = set(), [], []
        for r in rows:
            key = (r["repnb"], r["volnb"])
            if r["repnb"] and key in seen:      # duplicate volume record (D11)
                r["decision"], r["rule"] = "exclude", "duplicate_repnb_volnb"
                continue
            seen.add(key)
            p = ROOT / "data" / "text" / "annual_report" / year / f"{r['id']}.txt"
            parts.append(p.read_text(encoding="utf-8"))
            ids.append(r["id"])
        text = "\n\n".join(parts)
        (out_dir / f"{year}.txt").write_text(text, encoding="utf-8")
        ok, n_toks, sw_share = unit_qc(text, cfg["assembly_qc"])
        qc_rows.append({"year": year, "n_docs": len(ids), "tokens": n_toks,
                        "stopword_share": round(sw_share, 4),
                        "qc_pass": int(ok), "doc_ids": ";".join(ids)})
        if not ok:
            print(f"[s10] QC FAIL {year}: {n_toks} tokens, stopword share "
                  f"{sw_share:.3f} — unit EXCLUDED from series (text kept on disk)",
                  file=sys.stderr)
            continue
        feats = compute_classic(text, cfg["markers"]["mgmt_lexicon"])
        marks = compute_markers(text, cfg["markers"]["tier1"], cfg["markers"]["tier2"])
        marks.pop("tokens", None)
        feat_rows.append({"year": year, "n_docs": len(ids),
                          "doc_ids": ";".join(ids), **feats, **marks})
    qc_path = ROOT / "data" / "meta" / "ar_unit_qc.csv"
    with open(qc_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(qc_rows[0].keys()))
        w.writeheader(); w.writerows(qc_rows)
    log_path = ROOT / "data" / "meta" / "ar_assembly_log.csv"
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        cols = ["id", "year", "repnb", "volnb", "decision", "rule", "has_text",
                "display_title"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(log_rows)
    feat_path = ROOT / "data" / "features" / "ar_fy_features.csv"
    with open(feat_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(feat_rows[0].keys()))
        w.writeheader(); w.writerows(feat_rows)
    from collections import Counter
    c = Counter((r["decision"], r["rule"]) for r in log_rows)
    for k in sorted(c):
        print(f"[s10] {k[0]:>7} {k[1]:<22} {c[k]}")
    review = [r for r in log_rows if r["decision"] == "review"]
    print(f"[s10] assembled {len(feat_rows)} fiscal years -> {out_dir}")
    print(f"[s10] features -> {feat_path}; log -> {log_path}")
    if review:
        print(f"[s10] NEEDS_HUMAN_REVIEW ({len(review)} docs, excluded from series "
              f"until approved):", file=sys.stderr)
        for r in review:
            print(f"        {r['year']} {r['id']}: {r['display_title'][:90]}",
                  file=sys.stderr)

if __name__ == "__main__":
    main()
