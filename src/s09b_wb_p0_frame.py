"""WB P0-candidate frame builder (PREREG v0.5 SS2 + Appendix B.10; round-6
blocker 5, second half).

Deterministic pipeline (fixture-tested here): D&R listing rows -> normalized,
country-resolved, flagged, version-resolved frame + full audit trail, mirroring
s09a's rule order for CEM / SCD / CPF. The candidate docty strings live in
config/wb_p0_docty.yaml in frozen priority order and MUST be confirmed
verbatim against the s00 facet probe at Stage-B before any live use (the
pipeline itself is label-agnostic and takes the map from config).

The LIVE capture layer reuses the s01 fetch stack (utils.session_for /
get_with_retry / iter_documents via s01_fetch_metadata.fetch_stratum_year);
it refuses to run without --i-am-in-stage-b and archives every raw API page
to data/meta/wb_p0_raw/ (round-6 archiving obligation).

Rules mirrored from Appendix B (IMF) to the WB side:
 - unit: one unit per report number (repnb; fallback: D&R id when repnb is
   missing); multi-volume rows collapse to one unit;
 - version: latest docdt wins; ties -> a 'revised'/'corrig' title wins; then
   the smallest volume number; then the smallest id (deterministic sort+tail);
 - country: the D&R primary-country field; single-ISO3 rule with a frozen
   comma-inversion suffix list ("Egypt, Arab Republic of" -> "arab republic
   of egypt"); ';' or a non-suffix comma part -> regional/multi-country
   exclusion; unmapped names -> logged exclusion, alias map extended via
   config/wb_country_aliases.yaml;
 - cutoff: publication (docdt) <= 2025-12-31; year window CLI-set.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
import yaml

from s09a_imf_articleiv_frame import SEED_ALIASES, _field, norm

INSTITUTION = "wb"

INVERSION_SUFFIXES = {  # frozen: "X, <suffix>" rotates to "<suffix> X"
    "republic of", "the republic of", "arab republic of",
    "islamic republic of", "democratic republic of",
    "federal democratic republic of", "people's republic of",
    "democratic people's republic of", "lao people's democratic republic",
    "socialist republic of", "united republic of", "co-operative republic of",
    "bolivarian republic of", "plurinational state of", "state of",
    "federated states of", "kingdom of", "hashemite kingdom of",
    "sultanate of", "grand duchy of", "principality of", "commonwealth of",
    "union of", "independent state of", "the",
}
REGIONAL_TOKENS = [  # extended at Stage-B via config; substring match
    "africa", "middle east", "north africa", "latin america", "caribbean",
    "europe and central asia", "south asia", "east asia", "pacific islands",
    "pacific", "oecs", "world", "region", "sahel", "central america",
    " and ",
]


def load_docty_map(root: Path) -> list[dict]:
    f = root / "config" / "wb_p0_docty.yaml"
    cfg = yaml.safe_load(f.read_text())
    return cfg["priority"]


def load_wb_aliases(root: Path) -> dict:
    m = dict(SEED_ALIASES)
    f = root / "config" / "wb_country_aliases.yaml"
    if f.exists():
        extra = yaml.safe_load(f.read_text()) or {}
        m.update({norm(k).lower(): v for k, v in extra.items()})
    return m


def resolve_country(raw: str, aliases: dict):
    """Single-ISO3 rule. Returns (iso3, status): status is None on success,
    otherwise the exclusion label."""
    c = norm(raw).lower().strip()
    if not c:
        return None, "excluded_no_country"
    if ";" in c:
        return None, "excluded_regional_multicountry"
    if "," in c:
        left, right = (p.strip() for p in c.split(",", 1))
        if right in INVERSION_SUFFIXES:
            c = f"{right} {left}".strip()
        else:
            return None, "excluded_regional_multicountry"
    iso = aliases.get(c)               # alias FIRST (round-7 T&T class)
    if iso is not None:
        return iso, None
    if any(t in c for t in REGIONAL_TOKENS):
        return None, "excluded_regional_multicountry"
    return None, "unmapped_country"


def classify_row(row: dict, docty_map: list[dict], aliases: dict, cutoff: str,
                 y_lo: int, y_hi: int) -> dict:
    docty = norm(_field(row.get("docty"), ""))
    title = norm(_field(row.get("display_title"), ""))
    docdt = str(_field(row.get("docdt"), ""))[:10]
    out = {"institution": INSTITUTION, "docty": docty, "title": title,
           "docdt": docdt, "doc_id": str(_field(row.get("id"), "")),
           "repnb": norm(_field(row.get("repnb"), "")),
           "volnb": pd.to_numeric(_field(row.get("volnb"), "1"),
                                  errors="coerce"),
           "country_raw": norm(_field(row.get("count"), ""))}
    out["year"] = int(docdt[:4]) if docdt[:4].isdigit() else None
    genre = next((d["genre"] for d in docty_map if d["docty"] == docty), None)

    def rej(reason):
        out["status"] = reason
        return out

    if genre is None:
        return rej("excluded_docty")
    out["genre"] = genre
    lang = norm(_field(row.get("lang"), "English"))
    if lang.lower() != "english":
        return rej("excluded_language")
    iso, err = resolve_country(out["country_raw"], aliases)
    if err:
        return rej(err)
    out["country_iso3"] = iso
    out["unit"] = out["repnb"] if out["repnb"] else f"id:{out['doc_id']}"
    if docdt > cutoff:                      # frame-defining boundary first
        return rej("excluded_after_cutoff")
    if out["year"] is None or not (y_lo <= out["year"] <= y_hi):
        return rej("excluded_year_window")
    out["status"] = "included"
    return out


def resolve_versions(df: pd.DataFrame):
    """One row per (genre, unit): latest docdt; tie -> revised/corrig title;
    tie -> smallest volume number; tie -> smallest doc id. Deterministic
    sort+tail, no tuple-apply (pandas-version-proof; s09a pattern)."""
    d = df.copy()
    d["_rev"] = d["title"].str.lower().str.contains("corrig|revised").astype(int)
    d["_vol"] = pd.to_numeric(d["volnb"], errors="coerce").fillna(1)
    d = d.sort_values(["genre", "unit", "docdt", "_rev", "_vol", "doc_id"],
                      ascending=[True, True, True, True, False, False],
                      kind="mergesort")
    keep = (d.groupby(["genre", "unit"], sort=False).tail(1)
            .drop(columns=["_rev", "_vol"]))
    sup = d.loc[~d.index.isin(keep.index)].drop(columns=["_rev", "_vol"]).copy()
    sup["status"] = "superseded_version"
    return keep, sup


def build_frame(listing: pd.DataFrame, root: Path = Path("."),
                cutoff: str = "2025-12-31", y_lo: int = 1946,
                y_hi: int = 2025, docty_map=None):
    docty_map = docty_map if docty_map is not None else load_docty_map(root)
    aliases = load_wb_aliases(root)
    rows = [classify_row(r, docty_map, aliases, cutoff, y_lo, y_hi)
            for r in listing.to_dict("records")]
    audit = pd.DataFrame(rows)
    inc = audit[audit["status"] == "included"].copy()
    if len(inc):
        inc, sup = resolve_versions(inc)
        if len(sup):
            audit = pd.concat([audit[audit["status"] != "included"], inc, sup],
                              ignore_index=True)
    frame = inc.rename(columns={"unit": "id"})[
        ["institution", "genre", "year", "id", "country_iso3", "title",
         "docdt", "doc_id", "volnb"]
    ].sort_values(["genre", "year", "id"]).reset_index(drop=True)
    return frame, audit.sort_values(["status", "docdt"]).reset_index(drop=True)


def g2_coverage(frame: pd.DataFrame, imf_frame: pd.DataFrame | None = None,
                post=(2023, 2025)) -> dict:
    """Metadata-side G2 inputs per genre: pre-2023 years with >=1 included
    doc, post years present, and -- when the Article IV frame is supplied --
    COMMON pre-2023 years with it (the gate quantity: >=25 common pre years
    AND >=3 completed post years)."""
    out = {}
    imf_years = (set(imf_frame["year"].tolist())
                 if imf_frame is not None else None)
    for genre, sub in frame.groupby("genre"):
        yrs = set(int(v) for v in sub["year"].tolist())
        pre = {y for y in yrs if y < 2023}
        post_y = {y for y in yrs if post[0] <= y <= post[1]}
        rec = {"pre2023_years": len(pre), "post_years": sorted(post_y),
               "n_docs": int(len(sub))}
        if imf_years is not None:
            common = pre & {y for y in imf_years if y < 2023}
            rec["common_pre_years_with_articleiv"] = len(common)
            rec["g2_metadata_ok"] = bool(len(common) >= 25
                                         and len(post_y) >= 3)
        out[genre] = rec
    return out


def fetch_live(cfg: dict, docty_map: list[dict], y_lo: int, y_hi: int,
               raw_dir: Path, log_csv: Path | None = None) -> pd.DataFrame:
    """LIVE capture via the s01 fetch stack. Round-7 repair: archives EVERY
    raw API PAGE verbatim (query params, facets, totals, server payload) to
    raw_dir/{genre}_{year}_os{offset}.json plus an append-only request log
    (utc, genre, year, os, total, rows_returned, payload_sha256, raw_file,
    params_json) and a per-stratum page-count line. Stage-B only."""
    import csv as _csv, hashlib as _h, datetime as _dt
    from utils import session_for
    from s01_fetch_metadata import fetch_stratum_year
    sess = session_for(cfg)
    raw_dir.mkdir(parents=True, exist_ok=True)
    _leftover = sorted(p.name for p in raw_dir.glob("*.json"))
    if _leftover:                             # round-9: run-immutable target
        raise RuntimeError(f"[s09b] raw directory already holds "
                           f"{len(_leftover)} archive(s) (e.g. "
                           f"{_leftover[0]}) — raw archives are write-once; "
                           "a rerun must target a fresh raw directory")
    log_csv = log_csv or (raw_dir / "request_log.csv")
    log_csv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_csv.exists()
    rows = []
    with open(log_csv, "a", newline="", encoding="utf-8") as lf:
        w = _csv.writer(lf)
        if write_header:
            w.writerow(["utc", "genre", "year", "os", "total",
                        "rows_returned", "payload_sha256", "raw_file",
                        "params_json"])
        for d in docty_map:
            for year in range(y_lo, y_hi + 1):
                pages = []

                _att_n = [0]

                def attempt_hook(params, raw_bytes, status,
                                 _g=d["genre"], _y=year, _w=w):
                    """Round-11 (C30): every retried 429/5xx body is
                    archived verbatim, write-once, and logged."""
                    _att_n[0] += 1
                    os_ = params.get("os", 0)
                    fn = raw_dir / (f"{_g}_{_y}_os{os_}_attempt"
                                    f"{_att_n[0]}_status{status}.json")
                    if fn.exists():
                        raise RuntimeError(f"[s09b] {fn.name} already "
                                           "exists — attempt archives are "
                                           "write-once")
                    fn.write_bytes(raw_bytes)
                    _w.writerow([_dt.datetime.now(_dt.timezone.utc)
                                 .isoformat(timespec="seconds"),
                                 _g, _y, os_, "", f"attempt:{status}",
                                 _h.sha256(raw_bytes).hexdigest(),
                                 fn.name, json.dumps(params,
                                                     sort_keys=True)])

                def hook(params, raw_bytes, _g=d["genre"], _y=year,
                         _w=w, _pages=pages):
                    if raw_bytes is None:     # round-9: verbatim BYTES only
                        raise RuntimeError("[s09b] transport supplied no raw "
                                           "byte body; live capture requires "
                                           "the VERBATIM server bytes")
                    raw = raw_bytes
                    os_ = params.get("os", 0)
                    fn = raw_dir / f"{_g}_{_y}_os{os_}.json"
                    if fn.exists():           # round-9: run-immutable
                        raise RuntimeError(f"[s09b] {fn.name} already "
                                           "exists — raw archives are "
                                           "write-once; a rerun must target "
                                           "a fresh raw directory")
                    fn.write_bytes(raw)
                    try:                      # informational only: decision
                        pl = json.loads(raw)  # data comes from s01's parse
                        docs = pl.get("documents") or {}
                        nrows = len([k for k in docs if k != "facets"])
                        tot = pl.get("total", "")
                    except Exception:
                        nrows, tot = "unparsed", ""
                    _w.writerow([_dt.datetime.now(_dt.timezone.utc)
                                 .isoformat(timespec="seconds"),
                                 _g, _y, os_, tot,
                                 nrows, _h.sha256(raw).hexdigest(),
                                 fn.name, json.dumps(params, sort_keys=True)])
                    _pages.append(os_)

                recs = fetch_stratum_year(sess, cfg, [d["docty"]], year,
                                          page_hook=hook,
                                           attempt_hook=attempt_hook)
                print(f"[s09b] {d['genre']} {year}: {len(recs)} records over "
                      f"{len(pages)} raw page(s) archived")
                rows.extend(recs)
    return pd.DataFrame(rows)


def apply_docty_verification(docty_map: list[dict], path: str,
                             probe_artifact: str | None = None) -> list[dict]:
    """Round-7 frozen Stage-B mechanism for the declared-open docty labels:
    Stage-A ships EXPECTED strings in config/wb_p0_docty.yaml (immutable);
    Stage-B runs the s00-style probe and writes a verification JSON
    ({verified_utc, source:'s00', labels:{cem,scd,cpf}}) that is timestamped
    inside the Stage-B SAP addendum. Live capture consumes that file, applies
    corrected labels AT RUNTIME, and logs every divergence. The Stage-A
    config is never edited."""
    v = json.loads(Path(path).read_text())
    # round-8: full schema + probe binding, fail-closed --------------------
    import datetime as _dtv
    import re as _rev
    errs = []
    try:
        _dtv.datetime.fromisoformat(str(v.get("verified_utc", ""))
                                    .replace("Z", "+00:00"))
    except Exception:
        errs.append("verified_utc missing or not ISO-8601")
    if v.get("source") != "s00":
        errs.append("source must be 's00'")
    if not _rev.fullmatch(r"[0-9a-f]{64}", str(v.get("probe_sha256", ""))):
        errs.append("probe_sha256 missing or not sha256 hex (archived s00 "
                    "probe binding)")
    elif probe_artifact is None:
        errs.append("probe artifact path required (round-9): the archived "
                    "s00 probe file must be supplied so its hash can be "
                    "RECOMPUTED, not merely format-checked")
    elif not Path(probe_artifact).exists():
        errs.append(f"probe artifact {probe_artifact} missing")
    else:
        import hashlib as _hpv
        got = _hpv.sha256(Path(probe_artifact).read_bytes()).hexdigest()
        if got != v["probe_sha256"]:
            errs.append(f"probe artifact hash mismatch: recomputed "
                        f"{got[:16]}..., verification JSON claims "
                        f"{str(v['probe_sha256'])[:16]}...")
    labels = v.get("labels")
    need = {"cem", "scd", "cpf"}
    if (not isinstance(labels, dict) or set(labels) != need
            or not all(isinstance(labels[k], str) and labels[k].strip()
                       for k in need)):
        errs.append("labels must map EXACTLY {cem, scd, cpf} to non-empty "
                    "strings")
    if errs:
        raise SystemExit("[s09b] docty verification JSON rejected: "
                         + "; ".join(errs))
    out = []
    for d in docty_map:
        nd = dict(d)
        if d["genre"] in labels and labels[d["genre"]] != d["docty"]:
            print(f"[s09b] docty divergence ({d['genre']}): config "
                  f"{d['docty']!r} -> verified {labels[d['genre']]!r} "
                  f"(source={v.get('source')}, utc={v.get('verified_utc')})")
            nd["docty"] = labels[d["genre"]]
        out.append(nd)
    return out


def _write_outputs(frame, audit, a) -> None:
    """SAP addendum A5 (2026-08-20): the G2 report is written HERE, not in
    main()'s offline tail. The live branch returned immediately after writing
    the frame and audit, so `--g2-report` was accepted and then silently
    ignored on exactly the path that needs it — a round-8 class fail-open
    (a requested check that does not happen and says nothing). Both paths now
    share this tail, so the flag means the same thing wherever it is passed."""
    Path(a.out_frame).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(a.out_frame, index=False)
    audit.to_csv(a.out_audit, index=False)
    print(f"[s09b] frame={len(frame)} included; audit rows={len(audit)}; "
          f"statuses={audit['status'].value_counts().to_dict()}")
    if getattr(a, "g2_report", None):
        imf = pd.read_csv(a.imf_frame) if getattr(a, "imf_frame", None) else None
        rep = g2_coverage(frame, imf)
        Path(a.g2_report).parent.mkdir(parents=True, exist_ok=True)
        Path(a.g2_report).write_text(json.dumps(rep, indent=2))
        print(f"[s09b] G2 metadata report -> {a.g2_report}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listing",
                    help="captured D&R metadata CSV "
                         "(id,docty,count,display_title,docdt,repnb,volnb"
                         "[,lang]); omit for LIVE capture (Stage-B only)")
    ap.add_argument("--out-frame", required=True)
    ap.add_argument("--out-audit", required=True)
    ap.add_argument("--g2-report", help="optional JSON output path")
    ap.add_argument("--imf-frame", help="s09a frame CSV for common-year G2")
    ap.add_argument("--cutoff", default="2025-12-31")
    ap.add_argument("--year-lo", type=int, default=1946)
    ap.add_argument("--year-hi", type=int, default=2025)
    ap.add_argument("--config", default="config/config.yaml")
    ap.add_argument("--i-am-in-stage-b", action="store_true",
                    help="required for LIVE capture; fixture runs consume "
                         "--listing only")
    ap.add_argument("--docty-probe-artifact",
                    help="path to the ARCHIVED s00 probe artifact whose "
                         "sha256 the verification JSON binds (round-9: "
                         "recomputed, required with --docty-verified)")
    ap.add_argument("--docty-verified",
                    help="Stage-B verification JSON (s00 probe output); "
                         "REQUIRED in live mode — the frozen mechanism for "
                         "corrected docty labels without editing Stage-A "
                         "config")
    a = ap.parse_args()
    if a.g2_report and not a.imf_frame:
        raise SystemExit("[s09b] REFUSING --g2-report without --imf-frame: "
                         "the G2 gate quantity is the number of pre-2023 "
                         "years COMMON with the Article IV frame; without it "
                         "the report would omit g2_metadata_ok and read as a "
                         "silent pass.")
    root = Path(".")
    if a.listing:
        listing = pd.read_csv(a.listing)
    else:
        if not a.i_am_in_stage_b:
            raise SystemExit("[s09b] REFUSING live capture without "
                             "--i-am-in-stage-b (PREREG SS11: metadata "
                             "acquisition is a Stage-B act).")
        if not a.docty_verified:
            raise SystemExit("[s09b] REFUSING live capture without "
                             "--docty-verified (PREREG SS11/App B: docty "
                             "labels must be Stage-B-verified via the frozen "
                             "mechanism; Stage-A config is immutable).")
        from utils import load_config
        dm = apply_docty_verification(load_docty_map(root), a.docty_verified,
                                      probe_artifact=a.docty_probe_artifact)
        listing = fetch_live(load_config(a.config), dm, a.year_lo, a.year_hi,
                             root / "data" / "meta" / "wb_p0_raw")
        frame, audit = build_frame(listing, root, a.cutoff, a.year_lo,
                                   a.year_hi, docty_map=dm)
        _write_outputs(frame, audit, a)
        return
    frame, audit = build_frame(listing, root, a.cutoff, a.year_lo, a.year_hi)
    _write_outputs(frame, audit, a)


if __name__ == "__main__":
    main()
