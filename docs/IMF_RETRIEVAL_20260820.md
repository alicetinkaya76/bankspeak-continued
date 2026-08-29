# A8 (part) — IMF Article IV corpus retrieval: outcome and defects found

Date: 2026-08-20. Code: `tools/fetch_imf_cr_pdfs.py`, `tools/verify_imf_cr_pdfs.py`
(43 fixture tests). Conduct and access route: `docs/IMF_ACCESS_COMPLIANCE_20260820.md`.
Every number regenerates from `data/raw/imf_cr_pdf/{_manifest.csv,_verification.csv}`.

## Outcome

**All 1,064 preregistered documents retrieved and verified (100%)**, 2.47 GB.
No record outside the frozen sample was requested (permission condition 1,
asserted in the suite against `frozen_sampling_imf_v1.csv`).

Intention-to-sample (PREREG §7), imf × article_iv: **1,064 sampled → 1,064
downloaded → 1,064 verified**, 40/40 in every year (24 in 1999). `nonzero` and
`eligible` are feature-stage columns and are deliberately blank: they require
`s03`, which PREREG §11.3 places after the SAP freeze. Not run.

Resolution routes, labelled per record in the manifest so any subset stays
countable and reversible:

| rung | records | touches an archive |
| --- | --- | --- |
| L1 legacy static `/external/pubs/ft/scr/` | 705 | no |
| L1b same filename in the CMS media tree | 4 | no |
| L1c bounded sequence, verification-gated | 1 | no |
| L2/L2b IMF's own link via a Wayback capture | 354 | yes |
| unresolved | **0** | — |

Verification rungs, each named per record rather than collapsed to a boolean:
R1 cover text 869, R2 scan-metadata stamp 170, R3 title match 16, R4
country+year 9. **needs_human_review 0, integrity mismatch 0, unresolved 0.**

Reaching 100% took three passes. The first left 37 unresolved; L1b and the
snapshot walk took that to 3; ordering the walk by capture SIZE rather than by
date took it to 1; and the bounded sequence rung took the last one. Each step is
recorded below rather than presented as a single clean run.

## Three defects found, and what they cost

**1. Silent truncation (corpus-corrupting; fixed).** `fetch_pdf` accepted any
body beginning `%PDF-`. A connection cut mid-transfer leaves exactly that, so
five half-downloads were recorded `ok`: 2012/221 (1.2 MB of 2.8 MB), 2014/115,
2014/192, 2016/344, 2016/366. Both PyMuPDF and pdftotext failed on their XRef,
which is how they surfaced — the *verification* pass caught what the retrieval
pass had blessed. A complete PDF ends with `%%EOF`; that is now a download gate
with a retry. The five were withdrawn (recorded `truncated_withdrawn` in the
append-only manifest, not deleted from the record) and re-fetched complete.

**2. A verification measure that would have rubber-stamped wrong documents
(rejected before adoption).** 14 records failed R3, 9 of them wrongly: the
request list says "Staff Report for the 2002 Article IV Consultation" where the
IMF metadata says "2002 Article IV Consultation-Staff Report; Staff Statement;
Public Information Notice" — the same document, reordered, which
`SequenceMatcher` penalises.

The obvious repair was token-set overlap. It was tested against a negative
control and **failed**: Finland 2004 scored **0.86** against Tanzania 2004,
above several true matches. Article IV titles share nearly all their tokens, and
a short title inside a long one inflates the min-denominator overlap. Adopting
it would have marked mismatched documents "verified".

R4 requires instead the **country prefix** (PREREG B.4 takes it from the title's
first colon) plus a shared year. 9/9 of the true matches pass; **0 false
positives in 300 random mismatched pairs**. The rejected measure is kept in the
test suite as a guard, so a future "just loosen the threshold" fails loudly.

**3. Wrong targets in the sample list — scanned, and they cost nothing.**
`docs/IMF_permission_sample_list_1064.csv` was scanned in full after 2020/198
turned up pointing at a Debt Sustainability Analysis annex rather than the
Article IV staff report. **8 of 1,064 rows** carry a direct PDF URL under
`/-/media/files/dsa/...` instead of a publication page:

- pointing at a **DSA annex** (wrong genre): 2013/197 GNB, 2013/246 YEM,
  2014/038 TGO, 2020/198 COM
- pointing at the staff report under an odd `/dsa/` path: 2005/023 SLE,
  2006/274 SEN, 2014/301 COD, 2014/311 VNM

**None of them contaminated the corpus.** The retrieval derives the PDF URL from
the report number (L1) and falls back to the sample list's URL only for the
archive lookup, so 7 of the 8 resolved via L1 and every one verified by R1 —
the report number in its own cover text. The eighth (2020/198) simply had no
page to walk and was recovered by L1c. The defence that held here is that the
list's URL is never a *source* of a document, only a *hint*; verification is
what admits a file.

A second check found no further structural problem: every other row is a
`/en/publications/cr/issues/...` page. (657 rows have a page-URL year differing
from the report year — that is the page's posting date, not an error: 1999
reports were re-posted to imf.org in 2016.)

## Note for the feature stage

**194 of the retrieved documents (20.1%) are pre-OCR scans with no text layer —
12,004 pages**, against 56,815 pages that already carry text. They are cleanly
bounded: 1999-2003 entirely, 2004 partially (9 of 39), then essentially none.
OCR is a real work item that no stage of the plan currently budgets for.
