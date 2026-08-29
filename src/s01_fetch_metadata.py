"""s01 — stratified, year-bucketed metadata harvest + write-once sampling CSV.
Design: D1 (strata), D10 (frozen artifacts), D11 (English only).
Year-by-year strdate/enddate queries keep pages small and the run resumable."""
from __future__ import annotations
import argparse, csv, random, sys
from pathlib import Path
from utils import (ROOT, load_config, session_for, get_with_retry,
                   iter_documents, write_jsonl)

def fetch_stratum_year(sess, cfg, docty_labels, year: int,
                       page_hook=None, attempt_hook=None) -> list[dict]:
    """page_hook(params_dict, raw_bytes) fires once per raw API page BEFORE
    any parsing, receiving the VERBATIM transport BYTES (round-9: text
    re-encoding is forbidden; a transport without .content aborts), so a
    malformed body is archived before its parse failure propagates. Round-9
    schema minimum: a payload lacking 'total' or 'documents' keys RAISES.
    Round-9 drift rule: the declared total is fixed by the FIRST page; any
    later page declaring a different total RAISES. Completeness (round-8):
    an empty page while fewer records than the declared total have been
    collected, or a final count differing from the declared total, RAISES."""
    api = cfg["api"]
    records, os_, first_total = [], 0, None
    seen_ids = set()
    params_base = {
        "format": api["format"],
        "rows": api["rows_per_page"],
        "lang_exact": api["lang_exact"],
        "docty_exact": "^".join(docty_labels),   # ^ is the API's OR separator
        "strdate": f"{year}-01-01",
        "enddate": f"{year}-12-31",
        "fl": ",".join(api["fields"]),
        "sort": "docdt", "order": "asc",
    }
    while True:
        params = dict(params_base, os=os_)
        resp = get_with_retry(sess, api["base_url"], params, cfg,
                              attempt_hook=attempt_hook)
        if page_hook is not None:                 # round-9: archive FIRST,
            raw = getattr(resp, "content", None)  # verbatim BYTES only
            if raw is None:
                raise RuntimeError("[s01] transport exposes no raw byte "
                                   "body (.content); live capture requires "
                                   "the VERBATIM server bytes")
            page_hook(dict(params), raw)
        payload = resp.json()                     # parse failures propagate
        if "total" not in payload or "documents" not in payload:
            raise RuntimeError("[s01] schema failure: payload lacks "
                               "'total'/'documents' — a schemaless response "
                               "is never an empty result")
        total = int(payload["total"])
        if first_total is None:
            first_total = total
        elif total != first_total:                # round-9: drift RAISES
            raise RuntimeError(f"[s01] declared-total drift: first page "
                               f"said {first_total}, a later page says "
                               f"{total}")
        batch = list(iter_documents(payload))
        if not batch and len(records) < first_total:   # round-8
            raise RuntimeError(
                f"[s01] completeness failure: server declared total="
                f"{first_total} but an empty page arrived after "
                f"{len(records)} record(s)")
        for rec in batch:                        # round-12: ids are
            rid_raw = rec.get("id")               # canonical STRINGS —
            if not isinstance(rid_raw, str):      # typed, trimmed, unique
                raise RuntimeError(
                    f"[s01] document id must be a string, got "
                    f"{type(rid_raw).__name__} — schema failure "
                    "(canonical-id contract, round-12)")
            rid = rid_raw.strip()
            if not rid or rid != rid_raw:
                raise RuntimeError(
                    "[s01] document id is empty or carries surrounding "
                    "whitespace — non-canonical id, schema failure "
                    "(round-12)")
            if rid in seen_ids:
                raise RuntimeError(f"[s01] duplicate document id {rid!r} "
                                   "across pages — pagination fault or "
                                   "drift; refusing to double-count")
            seen_ids.add(rid)
        records.extend(batch)
        os_ += api["rows_per_page"]
        if os_ >= first_total or not batch:
            break
    if len(seen_ids) != first_total:             # round-10: completeness
        raise RuntimeError(f"[s01] completeness failure: "
                           f"{len(seen_ids)} unique document id(s) but the "
                           f"server declared total={first_total}")
    return records

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    cfg = load_config(ap.parse_args().config)
    frozen = ROOT / "data" / "meta" / f"frozen_sampling_v{cfg['sampling_version']}.csv"
    if frozen.exists():
        sys.exit(f"[s01] REFUSING to overwrite {frozen} (D10). "
                 f"Bump sampling_version in config if the design changed.")
    sess = session_for(cfg)
    rng = random.Random(cfg["seed"])
    rows_out = []
    for stratum, spec in sorted(cfg["strata"].items()):
        all_recs = []
        for year in range(cfg["years"]["start"], cfg["years"]["end"] + 1):
            recs = fetch_stratum_year(sess, cfg, spec["docty_exact"], year)
            recs.sort(key=lambda r: (str(r.get("docdt", "")), str(r.get("id", ""))))
            cap = spec.get("per_year_cap")
            chosen = recs if cap is None or len(recs) <= cap else rng.sample(recs, cap)
            chosen.sort(key=lambda r: str(r.get("id", "")))
            n_all, n_sel = len(recs), len(chosen)
            flag = " LOW" if 0 < n_all < cfg["sampling"]["min_docs_per_cell"] else ""
            print(f"[s01] {stratum} {year}: {n_all} found, {n_sel} sampled{flag}")
            all_recs.extend(recs)
            for r in chosen:
                rows_out.append({
                    "id": str(r.get("id", "")), "stratum": stratum, "year": year,
                    "docdt": str(r.get("docdt", "")),
                    "repnb": str(r.get("repnb", "")),
                    "display_title": str(r.get("display_title", ""))[:200],
                    "txturl": str(r.get("txturl", "")),
                    "pdfurl": str(r.get("pdfurl", "")),
                })
        write_jsonl(ROOT / "data" / "meta" / f"metadata_{stratum}.jsonl",
                    sorted(all_recs, key=lambda r: (str(r.get("docdt","")), str(r.get("id","")))))
    rows_out.sort(key=lambda r: (r["stratum"], r["year"], r["id"]))
    with open(frozen, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader(); w.writerows(rows_out)
    print(f"[s01] wrote {frozen} ({len(rows_out)} sampled docs). This file is now FROZEN.")

if __name__ == "__main__":
    main()
