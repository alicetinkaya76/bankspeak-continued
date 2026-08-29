# Corpus quality: 27 documents no existing gate catches

Date: 2026-08-20. Tool: `tools/corpus_quality_scan.py` (9 fixture tests).
Artifact: `data/meta/corpus_quality_flags.csv`. Nothing is excluded — every
finding is written with its class and its evidence for a human to rule on.

## How it surfaced

`tools/run_after_sap.py` refuses to start if a scanned document already has a
near-empty extract, because `s03` skips outputs that exist and would strand them
forever. That check fired on the WB corpus: two Annual Report scans already had
such extracts from the 2026-08-07 run. Pulling that thread produced everything
below.

## The gap in the gates

`s10_assemble_ar.unit_qc` enforces a prose-likeness gate — ≥5,000 tokens AND
≥0.15 English function-word share — but only on **assembled Annual Report
units**. For `icr` and `pad`, the **P1 and P2 confirmatory panels**, the sole
eligibility rule is PREREG §7's "tokens ≥ 1". A document with 70,000 tokens of
unusable text passes it.

## What the scan found

3,145 extracted documents; median English function-word share **0.259**.
**27 flagged**, of which **17 are in the confirmatory strata**:

| class | annual_report | **icr (P1)** | **pad (P2)** |
| --- | --- | --- | --- |
| **non_english_suspected** | — | **11** | **1** |
| mojibake_suspected | 1 | — | 1 |
| table_dump_suspected | 1 | — | — |
| low_prose_borderline | 8 | 2 | 2 |

The five worst, with their causes — four different failures, which is why one
threshold was never going to be enough:

- **`pad/2018/29809040`** — 5,951 tokens of **mojibake**. `ŽĐƵŵĞŶƚŽĨ dŚĞtŽƌůĚĂŶŬ`
  is "Document of The World Bank" through a broken ToUnicode CMap.
- **`annual_report/2007/8514715`** — 44,516 tokens, a *different* mojibake
  substitution: `GHS8` is "NOTE", `4RTFF4QX` is "A SUMMARY", `4hhxwfpi` is
  "Accumulated".
- **`pad/2005/6336275`** — 29,070 tokens of **French**: "Traduction non
  officielle du texte en anglais".
- **`icr/2004/5527314`** — 70,526 tokens, English cover sheet, **French body**.
- **`annual_report/2008/34063917`** — a genuine lending-data **table dump**.

## The finding that matters most

**Twelve documents are suspected non-English, eleven of them in `icr` (P1).**
DESIGN_RATIONALE D11 makes the corpus English-only and `s01` queries the D&R API
with `lang_exact: English`. These documents came back *through* that filter. The
defect is inherited from World Bank metadata rather than introduced here, but it
lands inside the confirmatory panel either way.

## Two years the Annual Report series can get back

The AR series spans 1947–2024 with **7 missing years**: 1971, 1981, 1990, 2000,
2002, 2007, 2010. They are not one problem:

- **1971, 1981, 1990, 2000, 2010** — no QC record at all, i.e. no documents in
  the frame. A coverage gap, not an extraction gap.
- **2002** — its only two volumes are un-OCR'd scans totalling **12 tokens**;
  `qc_pass=0`, correctly. **OCR-recoverable** (180 pages).
- **2007** — 46,723 tokens but a 0.0094 function-word share, because the
  extraction is mojibake. **Also OCR-recoverable**: rasterising bypasses the
  broken CMap entirely.

So the OCR pass is not only about the IMF's 1999–2004 block. It can return **two
years to the eighty-year series RQ1 rests on**.

The QC gate deserves credit here: it caught both, and the 12-token document never
entered the assembled series. What it could not do is say *why*, and the "why"
decides the remedy — a scan and a broken CMap both look like "not prose".

## For the SAP

1. The 27 flagged documents need a ruling **before** the confirmatory analysis
   runs. Excluding them after seeing the corpus is a researcher degree of
   freedom; the exclusion rule belongs in the SAP.
2. `s10`'s prose gate covers only Annual Reports. Whether an equivalent gate
   should apply to `icr`/`pad` is a design question, and answering it now — before
   any outcome is computed — is the only time it can be answered cleanly.
3. The same scan must run on the IMF corpus once `s03` has extracted it. It has
   never been run on IMF text, which does not exist yet.
