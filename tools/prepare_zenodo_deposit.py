#!/usr/bin/env python3
"""Assemble the Zenodo deposit: what may be published, and hashes for what may not.

The repository's data policy (`.gitignore`, and the note above the raw-archive
block) is that "git carries the decision and Zenodo carries the evidence". This
builds the Zenodo half. Uploading is Ali's — this produces the payload, the
manifest and the README, and stops.

## What goes in, and what deliberately does not

**Included** — World Bank material and our own derived artifacts. WB content is
public disclosure under the Access to Information Policy and mostly CC BY 3.0
IGO; the frames, frozen samples, power curves and drift reports are ours.

**Excluded, with hashes instead** — everything IMF. The permission of
2026-08-20 forbids redistributing "documents, extracted full text or substantial
portions", and permits publishing "derived non-substitutive outputs ... including
SHA-256 hashes". The 2.47 GB corpus is plainly out. The judgement call is the
raw Coveo listing archive: it is bibliographic metadata rather than document
text, so §5 arguably permits it — but it is verbatim IMF content, the benefit of
depositing it is only verifiability, and **verifiability is fully served by
depositing its hashes**. So the conservative reading is taken: hashes go, bytes
stay. Anyone can re-derive the archive from the recorded queries and check.

Nothing here decides anything that `docs/IMF_ACCESS_COMPLIANCE_20260820.md` has
not already recorded.
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "zenodo_deposit"

# (relative path, kind) — kind decides bytes-or-hashes
INCLUDE_TREES = [
    ("data/meta/wb_p1p2_raw", "WB API raw pages, write-once (A6 capture)"),
    ("data/meta/wb_p0_raw", "WB API raw pages, write-once (P0 capture)"),
    # The confirmatory outputs themselves (2026-08-27): panel cells, the two
    # batteries, the governing family verdict. Deposited because a bounded
    # negative is only checkable if its inputs and its verdict travel together.
    ("data/analysis/panels", "confirmatory panel cells, batteries, family verdict"),
    ("data/analysis/robustness", "robustness outputs"),
    # The C2 repair (2026-08-27). Deposited BESIDE the frozen panels rather than
    # instead of them: the whole point of the deviation record is that a reader
    # can see the defective run and the repaired one side by side.
    ("data/analysis/panels_country",
     "post-hoc sensitivity: PREREG §6 country grouping, NOT condition 2"),
]
INCLUDE_FILES = [
    "data/meta/wb_p1p2_frame.csv",
    "data/meta/frozen_sampling_wb_annual_report_v1.csv",
    "data/meta/frozen_sampling_wb_icr_v1.csv",
    "data/meta/frozen_sampling_wb_pad_v1.csv",
    "data/meta/frozen_sampling_v1.csv",
    "data/meta/a7_drift_report.csv",
    "data/meta/ocr_inventory.csv",
    "data/meta/ocr_calibration.csv",
    "data/meta/corpus_quality_flags.csv",
    "data/meta/intention_to_sample_exclusions.csv",
    "data/meta/d8_exclusions.csv",
    "data/meta/ocr_overrides.csv",
    "data/meta/d13_kept.csv",
    "data/meta/refetch_log.csv",
    "data/meta/ar_unit_qc.csv",
    "data/features/ar_fy_features.csv",
    "data/analysis/its_results.csv",
    "data/analysis/power.csv",
    "data/analysis/prereg_sensitivities.json",
    "data/analysis/rq1_decomposition.json",
    "data/analysis/trend_analysis.json",
    "data/analysis/passp_calibration.json",
    # Every analysis output that backs a numbered table or a supplement
    # section. These were absent until round 20, which meant a reader could
    # unpack the deposit and still not check S10.3, S10.4, S10.6-S10.9, Table
    # 3c, 3d, 3e, 5c or 5d -- the deposit carried the inputs to the frozen
    # pipeline and none of the inputs to the checks a reviewer actually asked
    # about. None of these files carries IMF document text, a verbatim title or
    # an imf.org URL; the frame publication holds column NAMES only.
    "data/analysis/joint_holm_calibration.json",
    "data/analysis/ar1_null_calibration.json",
    "data/analysis/functional_form_sensitivity.json",
    "data/analysis/ar_exclusion_classes.json",
    "data/analysis/ar_component_inventory.json",
    "data/analysis/companion_volume_adjudication.json",
    "data/analysis/tier2_item_provenance.json",
    "data/analysis/tier2_item_provenance.csv",
    "data/analysis/tier2_period_fairness.json",
    "data/analysis/imf_frame_publication.json",
    "data/analysis/imf_frame_publication.csv",
    "data/analysis/imf_cadence_balance.json",
    "data/analysis/passe_coverage.json",
    "data/analysis/block_origin_enumeration.json",
    "data/analysis/dispersion_calibration.json",
    "data/analysis/dispersion_robust_inference.json",
    "data/analysis/stage_a_exposure_sensitivity.json",
    "data/analysis/retrieval_route_tally.json",
    "requirements.txt",
    "README.md",
    "data/meta/country_ontology.csv",
    "data/meta/country_unresolved.csv",
    "data/meta/wb_country_api_raw.json",
    "data/meta/g2_metadata_report.json",
    "data/analysis/branch_decision.json",
    "data/analysis/mde_p1p2/curve_companion_zero.csv",
    "data/analysis/mde_p1p2/curve_companion_half.csv",
    "data/analysis/mde_p1p2/curve_companion_full.csv",
    "data/analysis/mde_p1p2/cells_wb_icr_pad.csv",
    "data/analysis/mde_p1p2/template_p1.csv",
    "data/analysis/mde_p1p2/template_p2.csv",
    "data/analysis/mde_p1p2/template_imf.csv",
]
# The code itself. The third-eye review of 2026-08-29 was right that a paper
# whose warrant is auditability cannot deposit evidence without the programs that
# produced it — "git carries the decision, Zenodo carries the evidence" is a
# working convention, not a defensible submission. Everything below is ours.
INCLUDE_TREES += [
    ("src", "analysis pipeline and the frozen inference engine"),
    ("tools", "retrieval, repair, table/figure generators, sensitivity studies"),
    ("config", "pinned configuration, family definitions, alias maps"),
    ("tests", "the test suite that pins the frozen contracts"),
]

# IMF-derived: hashes only, never bytes
HASH_ONLY_TREES = [
    ("data/meta/imf_articleiv_raw", "IMF Coveo listing archive — IMF content"),
    ("data/raw/imf_article_iv", "IMF Article IV corpus, 1,064 PDFs — licensed"),
]
# The access route, deposited rather than hashed. See
# tools/build_imf_access_index.py: report number, year, country, DOI and our
# SHA-256, with no title and no IMF URL. A hash list whose rows cannot be mapped
# to obtainable documents verifies nothing.
INCLUDE_FILES += ["data/meta/imf_document_index.csv"]

HASH_ONLY_FILES = [
    "data/meta/frozen_sampling_imf_v1.csv",
    "data/meta/imf_articleiv_frame.csv",
    "data/meta/imf_retrieval/_manifest.csv",
    "data/meta/imf_retrieval/_verification.csv",
    # The unredacted frozen sample. Its redacted twin is deposited at the same
    # path (see REDACT_FILES); the original is hashed here so a holder of the
    # licensed material can still confirm byte identity with what we analysed.
    "data/meta/frozen_sampling_v2.csv",
]

# --- the five inputs the table and figure generators read ------------------
#
# The data-availability statement promises that every table regenerates from the
# deposit by a named command. It could not: none of these was staged, and
# `make_paper_tables.py` died on a ZeroDivisionError because Table 1's
# denominator comes from a file that was not there.
#
# Four of the five travel unchanged. Their identifying column is a report
# number, which `data/meta/imf_document_index.csv` already publishes as permitted
# derived output, and their `path` column is `stratum/year/id` — it names no
# title and no URL.
INCLUDE_FILES += [
    "data/meta/extraction_log.csv",
    "data/meta/ocr_log.csv",
    "data/features/classic.csv",
    "data/features/family_counts.csv",
    # Table 3c's only source. It maps each Annual-Report file to the rule that
    # excluded it, and without it no outside reader can rebuild the
    # sibling/duplicate split the corpus-boundary result now rests on. It carries
    # ids, years, decisions and rules; the display_title column travels because
    # these are World Bank titles, public under the Access to Information Policy.
    "data/meta/ar_assembly_log.csv",
]

# The fifth cannot travel whole. `frozen_sampling_v2.csv` carries
# `display_title` and `pdfurl` for all 1,064 IMF documents — verbatim titles and
# imf.org document URLs, which is the bibliographic frame the permission forbids
# redistributing, and precisely what this project has refused to publish
# elsewhere.
#
# The decision is to drop those columns rather than the file, and to drop them
# for EVERY row rather than only the IMF ones. Two reasons. The World Bank's
# titles and URLs are public and could travel, but neither generator reads any of
# the three columns — checked, zero occurrences — so keeping them buys nothing,
# and the WB raw API captures are already deposited in full, so no provenance is
# lost. And a whole-column rule cannot leak through a misclassified row, which a
# row-conditional rule can.
#
# What survives is what Table 1 actually needs: id, stratum, year, docdt, repnb.
REDACT_FILES = [
    ("data/meta/frozen_sampling_v2.csv",
     ("display_title", "txturl", "pdfurl"),
     "redacted: IMF titles and document URLs dropped; unredacted original "
     "hashed above so byte identity stays verifiable"),
]

# Signatures that must not survive redaction. Checked on the written bytes, not
# on the plan, because the plan is what one believes and the bytes are what ships.
REDACT_MUST_NOT_CONTAIN = [
    (re.compile(r"imf\.org", re.I), "imf.org URL"),
    (re.compile(r"(?i)staff\s+report\s+for\s+the"), "Article IV title boilerplate"),
    (re.compile(r"(?i)article\s+iv\s+consultation"), "Article IV title boilerplate"),
    (re.compile(r"10\.5089/"), "IMF DOI prefix"),
]


def redact_csv(src: Path, drop: tuple[str, ...]) -> str:
    """Return the file's text with the named columns removed."""
    with src.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        keep = [c for c in (rd.fieldnames or []) if c not in drop]
        missing = [c for c in drop if c not in (rd.fieldnames or [])]
        if missing:
            raise SystemExit(f"[deposit] REFUSING: {src.name} has no column(s) "
                             f"{missing}; the redaction plan does not match the "
                             "file and would ship it unchanged")
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=keep, lineterminator="\n")
        w.writeheader()
        for r in rd:
            w.writerow({c: r[c] for c in keep})
    return buf.getvalue()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# Build residue and editor droppings are not evidence. A deposit carrying 71
# .pyc files and .bak copies alongside the analysis code invites exactly the
# question a reproducibility claim cannot afford: which of these did you run?
SKIP_PARTS = {"__pycache__", ".git", ".ipynb_checkpoints", ".pytest_cache",
              ".venv", "node_modules"}
SKIP_SUFFIX = {".pyc", ".pyo", ".bak", ".swp", ".orig", ".rej", ".DS_Store"}


def walk(rel: str):
    p = ROOT / rel
    if p.is_dir():
        return sorted(q for q in p.rglob("*")
                      if q.is_file()
                      and not (SKIP_PARTS & set(q.parts))
                      and q.suffix not in SKIP_SUFFIX
                      and ".bak" not in q.name
                      and not q.name.startswith("."))
    return [p] if p.exists() else []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--copy", action="store_true",
                    help="copy the included payload; default lists it only")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    rows, n_inc, n_hash, bytes_inc = [], 0, 0, 0
    for rel, note in INCLUDE_TREES + [(f, "") for f in INCLUDE_FILES]:
        for f in walk(rel):
            r = f.relative_to(ROOT).as_posix()
            rows.append({"path": r, "disposition": "deposited",
                         "bytes": f.stat().st_size, "sha256": sha256(f),
                         "note": note})
            n_inc += 1
            bytes_inc += f.stat().st_size
            if a.copy:
                d = out / "payload" / r
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, d)
    # Redacted files go into the payload at their ORIGINAL path, so an unpacked
    # deposit is a working tree and `python tools/make_paper_tables.py` runs
    # against it with no rewiring. The manifest carries the redacted bytes' hash;
    # the original's hash is in the hash-only block.
    for rel, drop, note in REDACT_FILES:
        src = ROOT / rel
        if not src.exists():
            print(f"[deposit] missing, skipped: {rel}")
            continue
        text = redact_csv(src, drop)
        for pat, what in REDACT_MUST_NOT_CONTAIN:
            if pat.search(text):
                raise SystemExit(f"[deposit] REFUSING: {what} survived redaction "
                                 f"of {rel}. Dropping {drop} was not enough; the "
                                 "column plan is wrong, not the check.")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        rows.append({"path": rel, "disposition": "deposited_redacted",
                     "bytes": len(text.encode("utf-8")), "sha256": digest,
                     "note": note})
        n_inc += 1
        bytes_inc += len(text.encode("utf-8"))
        if a.copy:
            d = out / "payload" / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_text(text, encoding="utf-8")

    for rel, note in HASH_ONLY_TREES + [(f, "") for f in HASH_ONLY_FILES]:
        for f in walk(rel):
            rows.append({"path": f.relative_to(ROOT).as_posix(),
                         "disposition": "hash_only_not_deposited",
                         "bytes": f.stat().st_size, "sha256": sha256(f),
                         "note": note or "IMF-derived; permission forbids redistribution"})
            n_hash += 1

    man = out / "MANIFEST.csv"
    with man.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["path", "disposition", "bytes",
                                           "sha256", "note"])
        w.writeheader()
        w.writerows(rows)

    (out / "README.md").write_text(f"""# Bankspeak, Continued — Stage-B evidence deposit

Companion to the OSF registration `10.17605/OSF.IO/5C9J8`. The repository
carries the decisions; this deposit carries the evidence they were derived from.

**Deposited:** {n_inc} files, {bytes_inc/1e6:.1f} MB — World Bank raw API
archives (write-once, with their request logs) and our own derived artifacts:
frames, frozen samples, the power curves, the drift decomposition, the OCR
inventory and calibration, the quality-flag and exclusion ledgers, the
confirmatory panel cells, both validation batteries and the governing family
verdict. A bounded negative result is only checkable if the inputs and the
verdict travel together, so both are here.

**On IMF document identifiers.** Some deposited tables carry a row per analysed
document, IMF documents included, with our measurements against it — counts,
token totals, language shares. That is deliberate and it is not in tension with
the hash-only treatment of `imf_articleiv_frame.csv`. The frame is verbatim
IMF-supplied bibliographic content (titles, URLs, Coveo fields) and stays local;
what travels here is a report number plus numbers we computed, which §5 permits
as derived non-substitutive output. It also has to travel: a preregistered study
whose corpus membership cannot be inspected is not reproducible, and no reader
could otherwise check that the D-8 and D-11 exclusions were applied rather than
merely recorded. No document text, and no substantial portion of any document,
appears in any deposited file.

**Not deposited, hashes only:** {n_hash} files. Everything IMF-derived. The IMF's
permission of 2026-08-20 forbids redistributing documents or extracted text and
permits publishing derived non-substitutive outputs including SHA-256 hashes.
That covers the 1,064-document corpus, and the same conservative reading is
applied to the raw Coveo listing archive: verifiability is served by the hashes,
so the bytes stay local. Every excluded file appears in `MANIFEST.csv` with its
hash, so any holder of the originals can verify byte-for-byte.

Licences: WB content is public disclosure under the Access to Information Policy
and mostly CC BY 3.0 IGO. Derived artifacts are ours. See `docs/DATA_LICENSES.md`.

Reproduction: the WB frames regenerate byte-identically from the deposited raw
archives; `docs/A7_FRAME_DRIFT_20260820.md` and `docs/MDE_P1P2_20260820.md`
name the commands.
""", encoding="utf-8")

    print(f"[zenodo] deposited: {n_inc} files, {bytes_inc/1e6:.1f} MB")
    print(f"[zenodo] hash-only (IMF-derived, not deposited): {n_hash} files")
    print(f"[zenodo] wrote {man} and README.md")
    if not a.copy:
        print("[zenodo] manifest only; rerun with --copy to stage the payload")
    return 0


if __name__ == "__main__":
    sys.exit(main())
