#!/usr/bin/env python3
"""Build the Stage-B runtime: the v2 index, the Stage-B config, and the ledgers.

## The gap this closes

`s02`/`s04`/`s10`/`s12` all read `frozen_sampling_v{sampling_version}.csv` and
silently skip any document not in it. With `sampling_version: 1` that index is
the SEALED Stage-A WB sample — so a post-SAP run would have dropped **all 1,064
IMF documents** and most of the Stage-B WB redraw without a word. Worse, the
Stage-B WB samples were never downloaded at all: only 748 of their 2,738
documents overlap the sealed sample, so ~1,990 texts do not exist yet.

`config.yaml` anticipates exactly this mechanism: "bump [sampling_version] on
any sampling-design change; never overwrite frozen CSVs". The Stage-B per-cell
redraw IS that change. This builder therefore produces:

1. **`data/meta/frozen_sampling_v2.csv`** (write-once) — the union index:
   the three Stage-B WB frozen samples (stratum := genre) plus the IMF sample,
   in the v1 column shape `s02`/`s04` read. The frozen samples themselves are
   untouched; this is plumbing over them, not a new draw.
2. **`config/config.stageb.yaml`** — `config.yaml` with `sampling_version: 2`.
   The main config stays byte-identical so nothing outside the Stage-B driver
   changes behaviour.
3. **Manifest rows for the IMF corpus** (append-only, per its own rule).
   `s02` skips by manifest id; the IMF files are on disk and verified but were
   retrieved outside `s02`, so without these rows `s02` would re-download all
   1,064 from imf.org at the WB cadence (0.6 s) — faster than the 1 request/s
   the IMF permission allows. Each row carries the retrieval's own sha256 and
   resolved URL, so the append is provenance, not fabrication.
4. **`data/meta/d8_exclusions.csv`** — ruling D-8's exclusion ledger, derived
   from the quality flags (verdict `non_english_suspected`), one row per id
   with the reason. Applied at analysis; nothing is deleted.
5. **`data/meta/ocr_overrides.csv`** — ruling D-9's ledger: the two broken-CMap
   documents forced to `native_text=False` so any inventory regeneration keeps
   them on the OCR path.

Idempotent: every artifact is guarded; a rerun changes nothing.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "meta"
V2 = META / "frozen_sampling_v2.csv"
CFG_MAIN = ROOT / "config" / "config.yaml"
CFG_B = ROOT / "config" / "config.stageb.yaml"
MANIFEST = META / "manifest.tsv"
D8 = META / "d8_exclusions.csv"
OVR = META / "ocr_overrides.csv"

V1_COLS = ["id", "stratum", "year", "docdt", "repnb", "display_title",
           "txturl", "pdfurl"]
WB_SAMPLES = [("annual_report", "frozen_sampling_wb_annual_report_v1.csv"),
              ("icr", "frozen_sampling_wb_icr_v1.csv"),
              ("pad", "frozen_sampling_wb_pad_v1.csv")]
D9_IDS = {"8514715": "D-9 broken ToUnicode CMap (annual_report/2007)",
          "29809040": "D-9 broken ToUnicode CMap (pad/2018)"}


def build_v2() -> int:
    if V2.exists():
        print(f"[stageb] {V2.name} exists — write-once, left alone")
        return sum(1 for _ in open(V2)) - 1
    rows = []
    for stratum, fname in WB_SAMPLES:
        for r in csv.DictReader((META / fname).open(encoding="utf-8")):
            rows.append({"id": r["id"], "stratum": stratum, "year": r["year"],
                         "docdt": r.get("docdt", ""), "repnb": r.get("repnb", ""),
                         "display_title": (r.get("display_title") or "")[:200],
                         "txturl": r.get("txturl", ""), "pdfurl": r.get("pdfurl", "")})
    for r in csv.DictReader((META / "frozen_sampling_imf_v1_s02.csv").open(encoding="utf-8")):
        rows.append({k: r.get(k, "") for k in V1_COLS})
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise RuntimeError("[stageb] duplicate ids across samples — refusing")
    rows.sort(key=lambda r: (r["stratum"], r["year"], r["id"]))
    with V2.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=V1_COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"[stageb] wrote {V2.name}: {len(rows)} rows "
          f"(WB {sum(1 for r in rows if r['stratum'] != 'imf_article_iv')} + "
          f"IMF {sum(1 for r in rows if r['stratum'] == 'imf_article_iv')})")
    return len(rows)


def build_cfg() -> None:
    if CFG_B.exists():
        print(f"[stageb] {CFG_B.name} exists — left alone")
        return
    text = CFG_MAIN.read_text(encoding="utf-8")
    needle = "sampling_version: 1"
    if needle not in text:
        raise RuntimeError("[stageb] config.yaml does not carry "
                           "'sampling_version: 1' — refusing to guess")
    CFG_B.write_text(text.replace(
        needle,
        "sampling_version: 2  # Stage-B runtime copy; see tools/build_stageb_runtime.py",
        1), encoding="utf-8")
    print(f"[stageb] wrote {CFG_B.name} (sampling_version: 2; main config untouched)")


def append_imf_manifest() -> None:
    have = set()
    with MANIFEST.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                have.add(line.split("\t", 1)[0])
    ret = {}
    with (META / "imf_retrieval" / "_manifest.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):          # append-only: last row wins
            ret[r["report_no"]] = r
    frozen = {r["id"]: r for r in csv.DictReader(
        (META / "frozen_sampling_imf_v1_s02.csv").open(encoding="utf-8"))}
    added = 0
    with MANIFEST.open("a", encoding="utf-8") as fh:
        for report_no, r in sorted(ret.items()):
            if r.get("status") != "ok":
                continue
            doc_id = "CR" + report_no.replace("/", "-")
            if doc_id in have:
                continue
            year = frozen[doc_id]["year"]
            path = f"data/raw/imf_article_iv/{year}/{doc_id}.pdf"
            if not (ROOT / path).exists():
                raise RuntimeError(f"[stageb] {path} missing — refusing to "
                                   "manifest a file that is not there")
            fh.write(f"{doc_id}\t{r['sha256']}\t{r['pdf_url']}\t{path}\t"
                     f"{r['utc'][:10]}\n")
            added += 1
    print(f"[stageb] manifest.tsv: {added} IMF row(s) appended "
          f"({'already present' if added == 0 else 'retrieval sha256 + resolved URL'})")


def build_d8() -> None:
    if D8.exists():
        print(f"[stageb] {D8.name} exists — left alone")
        return
    flags = list(csv.DictReader((META / "corpus_quality_flags.csv").open(encoding="utf-8")))
    rows = [{"id": r["id"], "stratum": r["stratum"], "year": r["year"],
             "path": r["path"], "reason": "D-8 " + (
                 "wholly non-English (D11)" if r["id"] == "6336275"
                 else "bilingual: English report + non-English annexes"),
             "evidence": r["evidence"]}
            for r in flags if r["verdict"] == "non_english_suspected"]
    if len(rows) != 12:
        raise RuntimeError(f"[stageb] expected the 12 ruled language cases, "
                           f"found {len(rows)} — flags file has drifted; re-rule")
    with D8.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"[stageb] wrote {D8.name}: {len(rows)} exclusions (ruling D-8)")


def build_overrides() -> None:
    if OVR.exists():
        print(f"[stageb] {OVR.name} exists — left alone")
        return
    with OVR.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "native_text", "reason"])
        for i, why in sorted(D9_IDS.items()):
            w.writerow([i, "False", why])
    print(f"[stageb] wrote {OVR.name}: {len(D9_IDS)} D-9 overrides")


def main() -> int:
    build_v2()
    build_cfg()
    append_imf_manifest()
    build_d8()
    build_overrides()
    return 0


if __name__ == "__main__":
    sys.exit(main())
