#!/usr/bin/env python3
"""The post-SAP pipeline, in the one order that is correct, behind the one gate.

Everything downstream of the SAP freeze is sequenced here so the order cannot be
got wrong under time pressure, and so the freeze evidence is recorded in the same
act that consumes it.

## The gate

There is no `--i-know-what-im-doing` flag. The driver requires the SAP's external
timestamp and the frozen document's SHA-256 as arguments, and records both in the
run log. If the SAP has not been frozen the operator has nothing to pass, which
is the point: the gate is the evidence, not a promise.

## Why the order is what it is

**OCR before s03, and this is the trap worth naming.** `s03_extract_text` walks
`data/raw/` and skips any output that already exists (`if out.exists():
continue`). Run it first and it writes a near-empty .txt for each of the 194
scanned documents, marks them `pymupdf`, and then skips them forever — silently
losing the whole 1999-2004 IMF block into files that look extracted. Run the OCR
pass first and it deposits real text at exactly those paths, so s03 leaves them
alone and handles only the native-text documents. Same mechanism, opposite
outcome, decided entirely by order.

**Calibration before anything compares the scanned era.** SAP §S9: extraction
method is collinear with the estimand — every scan is IMF and pre-period — so
the OCR-versus-native effect must be estimated where era is held fixed before the
1999-2004 block enters a comparison. Calibration is cheap and runs first.

**Features before power and ITS**, and `s06` is NOT in this chain: PREREG §7.4
defers its step-4 patch, and D-4 rules that no NLL number appears in any output
until that regeneration has run. It is a separate, deliberate act.

Recorded here too, from the handover's small-debt list: the old phase numbering
had PHASE 4 consuming `data/analysis/mde_p0.json`, which is PHASE 5's output, so
the real order was 3 -> 5(p0) -> 4. That inversion does not arise below, where
each stage consumes only what an earlier line produced.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "bin" / "python")
# Stage-B runtime config: sampling_version 2 -> the v2 union index (Stage-B WB
# samples + IMF sample). The main config stays untouched; see
# tools/build_stageb_runtime.py for why v1 would have silently dropped every
# IMF document and most of the Stage-B redraw.
CFG = str(ROOT / "config" / "config.stageb.yaml")
RUN_LOG = ROOT / "data" / "meta" / "post_sap_run_log.jsonl"
TEXT = ROOT / "data" / "text"

DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")

# (label, argv, note) — order is the contract
STAGES = [
    ("s02_download_texts", [PY, "src/s02_download_texts.py", "--config", CFG],
     "download the ~1,990 Stage-B WB texts that Stage-A never fetched; the IMF "
     "corpus and the 748 overlapping WB docs are already manifested and skip"),
    ("fetch_override_pdfs",
     [PY, "tools/fetch_override_pdfs.py", "--i-have-frozen-the-sap"],
     "rulings D-9/D-12 pin documents to the OCR path, but a server_txt-only "
     "document has no PDF to OCR; without this the ledger is satisfied and the "
     "remedy never applied"),
    ("ocr_scan", [PY, "tools/ocr_prepass.py", "--scan"],
     "regenerate the inventory over the enlarged raw tree; D-9 overrides applied"),
    ("ocr_calibrate",
     [PY, "tools/ocr_prepass.py", "--calibrate", "-n", "20",
      "--i-have-frozen-the-sap"],
     "estimate the OCR-vs-native method effect with era held fixed (SAP §S9)"),
    ("ocr_run",
     [PY, "tools/ocr_prepass.py", "--run", "--i-have-frozen-the-sap"],
     "OCR every scan INTO data/text/ so s03 skips them"),
    ("s03_extract_text", [PY, "src/s03_extract_text.py", "--config", CFG],
     "native-text documents only; the OCR'd outputs already exist"),
    ("refetch_spacing",
     [PY, "tools/refetch_server_txt_defects.py", "--i-have-frozen-the-sap"],
     "ruling D-7: re-extract lost-spacing server_txt docs from their pdfurl, "
     "replacement conditional on measured improvement"),
    ("quality_scan", [PY, "tools/corpus_quality_scan.py"],
     "ruling D-10: the mandatory diagnostic, over the full corpus IMF included"),
    ("quality_gate", [PY, "tools/quality_gate.py"],
     "STOPS if any hard flag in the analysis corpus lacks a recorded ruling"),
    ("s10_assemble_ar", [PY, "src/s10_assemble_ar.py", "--config", CFG],
     "reassemble AR fiscal-year units after OCR so the recovered 2002 and 2007 "
     "volumes (ruling D-9) enter the series"),
    ("s04_features_classic", [PY, "src/s04_features_classic.py", "--config", CFG], ""),
    ("s05_features_markers", [PY, "src/s05_features_markers.py", "--config", CFG], ""),
    ("s05b_family_counts",
     [PY, "src/s05b_family_counts.py", "--sampling-version", "2"],
     "takes no --config; its frozen index was hardcoded to v1 (the sealed "
     "Stage-A sample) and would have dropped every IMF document"),
    ("s07_power_analysis", [PY, "src/s07_power_analysis.py", "--config", CFG], ""),
    ("s08_its_analysis", [PY, "src/s08_its_analysis.py", "--config", CFG], ""),
    ("s12_robustness", [PY, "src/s12_robustness.py", "--config", CFG], ""),
    ("build_panel_cells", [PY, "tools/build_panel_cells.py"],
     "the confirmatory H-DIFF input, which nothing produced (s08 is a "
     "per-stratum ITS, a different quantity) — and where rulings D-8/D-11 are "
     "ENFORCED rather than merely recorded"),
    ("s13_panel_P1",
     [PY, "src/s13_validation_battery.py", "panel",
      "--cells", "data/analysis/panels/cells_P1.csv",
      "--docs", "data/analysis/panels/docs_P1.csv",
      "--std-docs", "data/analysis/panels/docs_P1.csv",
      "--panel", "P1", "--i-am-post-sap",
      "--out", "data/analysis/panels/P1_battery.json"], ""),
    ("s13_panel_P2",
     [PY, "src/s13_validation_battery.py", "panel",
      "--cells", "data/analysis/panels/cells_P2.csv",
      "--docs", "data/analysis/panels/docs_P2.csv",
      "--std-docs", "data/analysis/panels/docs_P2.csv",
      "--panel", "P2", "--i-am-post-sap",
      "--out", "data/analysis/panels/P2_battery.json"], ""),
    ("s13_family_verdict",
     [PY, "src/s13_validation_battery.py", "family",
      "--spec", "data/analysis/panels/family_spec.yaml", "--i-am-post-sap",
      "--out", "data/analysis/panels/family_verdict.json"],
     "the GOVERNING decision: Holm over the two panels"),
]


def ocr_would_be_clobbered() -> list[str]:
    """Outputs s03 would have to create for scanned documents. Non-empty after
    the OCR pass means the pass did its job; non-empty BEFORE it means s03 ran
    first and the scanned era is already lost to empty files."""
    inv = ROOT / "data" / "meta" / "ocr_inventory.csv"
    if not inv.exists():
        return []
    import csv
    bad = []
    with inv.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["native_text"] == "True":
                continue
            out = (TEXT / r["path"]).with_suffix(".txt")
            if out.exists() and out.stat().st_size < 500:
                bad.append(r["path"])
    return bad


def log(event: dict) -> None:
    event["utc"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with RUN_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sap-doi", required=True,
                    help="the SAP's external timestamp DOI (OSF or Zenodo)")
    ap.add_argument("--sap-sha256", required=True,
                    help="sha256 of the frozen SAP document")
    ap.add_argument("--from-stage", default="",
                    help="resume at this stage label")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    if not DOI_RE.match(a.sap_doi):
        sys.exit(f"[post-sap] --sap-doi does not look like a DOI: {a.sap_doi!r}. "
                 "The gate is the freeze evidence; there is no way past it.")
    if not SHA_RE.match(a.sap_sha256):
        sys.exit("[post-sap] --sap-sha256 must be 64 hex characters")

    stages = STAGES
    if a.from_stage:
        labels = [s[0] for s in STAGES]
        if a.from_stage not in labels:
            sys.exit(f"[post-sap] unknown stage {a.from_stage!r}; one of {labels}")
        stages = STAGES[labels.index(a.from_stage):]

    clobbered = ocr_would_be_clobbered()
    if clobbered and not a.from_stage:
        sys.exit(f"[post-sap] REFUSING: {len(clobbered)} scanned document(s) "
                 f"already have a near-empty extract in data/text/ (e.g. "
                 f"{clobbered[0]}). s03 ran before the OCR pass and will now skip "
                 "them forever. Delete those outputs and start from ocr_calibrate.")

    print(f"[post-sap] SAP {a.sap_doi}, sha256 {a.sap_sha256[:16]}…")
    for label, argv_, note in stages:
        print(f"[post-sap] -> {label}" + (f"  ({note})" if note else ""))
        if a.dry_run:
            continue
        r = subprocess.run(argv_, cwd=ROOT)
        log({"stage": label, "returncode": r.returncode, "argv": argv_,
             "sap_doi": a.sap_doi, "sap_sha256": a.sap_sha256})
        if r.returncode != 0:
            sys.exit(f"[post-sap] {label} failed (rc={r.returncode}); stopping. "
                     f"Fix, then resume with --from-stage {label}")
    if a.dry_run:
        print("[post-sap] dry run — nothing executed")
        return 0
    print("[post-sap] all stages completed; "
          "s06/NLL deliberately NOT run (PREREG §7.4, decision D-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
