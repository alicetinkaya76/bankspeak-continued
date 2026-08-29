# SAP — Stage-B constants, final draft

**Status: DRAFT for Ali's review and external timestamping. Not yet the SAP.**
Prepared 2026-08-20 by Claude under instruction to do everything that could be
done without the operator. Two things are deliberately left blank and are the
only things standing between this draft and the frozen SAP: §S12's timestamp
block, and Ali's confirmation of the rulings in §S10.

Binding on top of PREREG v0.5 and amendments v0.6–v0.12, and of SAP addenda
A1–A5. It completes PREREG §11.3 — "the final SAP (this document, every Stage-B
constant filled), externally timestamped. Only then: text download and feature
processing" — by filling every Stage-B constant. It changes no frozen decision
rule, no seed, no gate, and no line of `classify_row`, `build_frame` or
`parse_report_no`.

---

## S1 — Branch decision (write-once, unchanged)

Family = **{P1, P2}**. `data/analysis/branch_decision.json`, sha256
`d9ddbaec8a6e38dd1db5abe7913c9c40840224170a5e4a56d72193ad3aa5c985`.

G2 measured for every P0 candidate against the threshold of 25 pre-2023 common
years: cem 22, cpf 24, scd 8. The ceiling is 24 — the Article IV frame's own
span — so no candidate could pass. G3 passed for all three at 1.0. Per A5.7 the
G1 blind audit and the p0 MDE were NOT evaluated; their inputs carry
`evaluated:false` with the reason inside the artifact and must not be read as
tested-and-failed verdicts.

## S2 — Frames captured at the Stage-B snapshot date

| frame | units | span | sha256 |
| --- | --- | --- | --- |
| IMF Article IV | 2,788 | 1999–2025 | `5e465df668a8d940…6ae3` |
| WB P0 candidates | 491 | — | `c25ae6002ba37f95…370a` |
| **WB P1/P2 (A6, captured 2026-08-20)** | **15,385** | **1946–2026** | `d98424163dbe3c92…74d2` |

The WB frame was captured through the frozen `s01_fetch_metadata` stack; 365 raw
pages are archived write-once under `data/meta/wb_p1p2_raw/` with a 366-line
append-only request log. Counts reproduce the pre-Stage-B figures:
annual_report 331 exactly, icr +2, pad +3 over fourteen days.

**Calendar-2026** (§11.4): 315 WB records captured and flagged
confirmatory-ineligible. The flag is derived from each record's own `docdt`, not
from the query year; 0 records show a docdt-year/cell-year mismatch.

Recorded, not corrected: `pad` begins **1996**, one year before the config note
states (one record); **13** records carry neither `txturl` nor `pdfurl` and
belong in the §7 intention-to-sample table as sampled-but-not-downloadable.

## S3 — Frozen samples (write-once)

| sample | rows | panel | sha256 |
| --- | --- | --- | --- |
| IMF Article IV | 1,064 | comparator | `baa91fa7fa4b92af…3d7e` |
| WB annual_report | 331 | P-A descriptive | `77f1855cc4a31a7f…e13a` |
| WB icr | 1,246 | **P1** | `1b0c1698840fd5e5…abed` |
| WB pad | 1,161 | **P2** | `948f4ee1a559b171…9111` |

Drawn by `s09_frame_sampler` under Appendix B.7's per-cell sampler,
`run_id` `stageB-20260820`. Cross-validated: `tools/a7_frame_drift.py` and
`s09_frame_sampler` are independent implementations and agree on all 2,738 WB
rows.

## S4 — Sample drift from the sealed Stage-A draw, decomposed

Three causes, separated because one number would hide the largest
(`docs/A7_FRAME_DRIFT_20260820.md`):

- **Cutoff:** 80 sealed rows are dated 2026 and leave the confirmatory window.
- **Frame drift:** negligible — icr +2, annual_report 0, pad 0.
- **Sampler:** dominant. The sealed draw is provably `s01`'s single global RNG —
  replaying its exact procedure reproduces `frozen_sampling_v1.csv` **2,818 of
  2,818, zero on either side**. Appendix B.7 specifies the per-cell sampler
  instead, and redrawing under it swaps **1,987 of 2,738 (72.6%)**.

**Prior-inspection constant: 748 of 2,738 (27.3%)** of the Stage-B confirmatory
WB sample are the same documents whose outcomes were inspected at Stage-A.

## S5 — IMF corpus

**1,064 of 1,064 retrieved and verified**, 2.47 GB. Manifest
`adc0ecdd…7e39`, verification `92b5d742…5118`. Routes: L1 legacy static 705,
L1b media tree 4, L1c bounded verification-gated sequence 1, L2/L2b IMF link via
a public archive 354, unresolved **0**. Verification rungs: R1 cover text 869,
R2 scan-metadata stamp 170, R3 title match 16, R4 country+year 9;
needs_human_review 0, integrity mismatch 0.

Landed at `data/raw/imf_article_iv/<year>/<id>.pdf`, binned by the frozen
sample's year; every file re-verified by re-derived sha256 after the move.
Access conditions and the operator ruling on permission condition 3:
`docs/IMF_ACCESS_COMPLIANCE_20260820.md`.

## S6 — Power: the preregistered bound (the constant that matters)

Measured **before any outcome was computed**
(`docs/MDE_P1P2_20260820.md`). Full nested PASS-P, 1,000 replicates,
B = 9,999, θ grid by 0.05, calibration bound to `cf033e2f…3203`. Inputs are
preregistration-specified: window 1999–2025 (24 pre-2023 years, 3 post), base
rate **2.767e-5/token** (the observed WB pre-2023 rate, IMF at parity), σ_δ =
**0.3205** from the frozen MoM hook on WB institution×genre×year cells, ρ = 0.5.

| θ | companion=zero | half | full |
| --- | --- | --- | --- |
| 0.00 | 0.039 | 0.039 | 0.039 |
| **0.60** — G4's own threshold | **0.159** | **0.158** | **0.216** |
| 1.20 | 0.483 | 0.485 | 0.569 |

**MDE₈₀ is unreachable on the preregistered θ grid under every companion
setting.** At θ = 0.60 — the value the design chose as its branch-selection
standard — the family attains 0.159–0.216 where 0.80 was required.

Two facts fixed alongside it: σ_δ is the whole cause (at σ_δ = 0 the same setup
gives MDE₈₀ = 0.65), and **sampling more documents is not a remedy** — tripling
every panel moves power at θ = 1.2 from 0.48 to 0.53, because the binding
constraint is a year-level shock and there are three post years.

## S7 — What must accompany every confirmatory result

Not an appendix, not a footnote:

1. **The §S6 power bound**, adjacent to every H-DIFF estimate. A null is reported
   as uninformative, never as absence of effect. A rejection is reported with its
   winner's-curse caveat.
2. **`placebo_sig_frac`**, next to any breakpoint estimate. Already computed:
   icr **1.00**, pad 0.50, ar_assembled 0.83, ar_assembled_levelonly **0.00**.
3. **The series label.** Three series co-exist (`doc_level`, `ar_assembled`,
   `ar_assembled_levelonly`) and two disagree in sign on the same quantity. No
   number is reported without naming which.
4. **The §S8 disclosure.**

## S8 — Prior inspection, disclosed

Ruling: `docs/RULING_20260820_prior_inspection.md`. The WB half of the H-DIFF
contrast was inspected at Stage-A; the IMF half has never existed in this
project and the interaction has never been computed. PREREG §3 already discloses
the exposure in its own frozen text (the guard family is fixed as `underscore`
because it was "already known to dominate on the WB side (43.48% of post-period
hits)").

Audited against git history rather than recollection
(`docs/AUDIT_20260820_researcher_dof.md`): the outcome definition
(`config.yaml: markers`) is **byte-identical** across the 2026-08-07 09:13
boundary and `s05_features_markers.py` has one commit ever. What changed
afterwards lands outside the confirmatory family, is provably neutral to the
primary outcome, or is a dated adversarial-review repair. The audit states its
own limit: git certifies only what it holds.

## S9 — Extraction, and a collinearity that logging cannot fix

**192 of the 1,064 IMF documents have no text layer, all in 1999–2004**; WB has
2 such documents, icr and pad none (`data/meta/ocr_inventory.csv`; 12,055 pages
to OCR).

D9 prescribes logging extraction method so era × method can be controlled. Here
that is **insufficient**: the OCR block sits in one arm (IMF) of one period
(pre) of the very interaction H-DIFF estimates, so method is collinear with the
estimand rather than merely correlated with era, and a collinear variable cannot
be controlled for.

**Binding:** the 1999–2004 IMF block does not enter any comparison until
`tools/ocr_prepass.py --calibrate` has estimated the OCR-versus-native method
effect on documents that carry both, with era held fixed. Calibration computes
extraction-fidelity descriptors only and no study outcome. Method is logged per
document as `ocr_tesseract` or `pymupdf` in the D9 log.

**A second era-nested defect, found the same day and diagnosed to source
(`docs/EXTRACTION_DEFECTS_20260820.md`):** 70 WB documents carry lost word
spacing (`PROJECTAPPRAISALDOCUMENT`), 65 of them in `pad` (P2), concentrated in
2003–2009 and absent from 2010 on. Whole-word matching — how marker families are
counted — misses 40–78% of its hits in them, measured with neutral words absent
from the marker lists. The defect is in the World Bank's own server-side text
(`server_txt` 70/2,688 affected; `pymupdf` 0/437), so the remedy is D9's own
`pdfurl` fallback, verified per document (ruling D-7). A corpus-wide quality
scan (`tools/corpus_quality_scan.py`) additionally flags 1 wholly-French
document, 11 bilinguals and 2 broken-CMap documents; rulings D-8/D-9/D-10 cover
them, and the scan is a mandatory diagnostic that re-runs on every corpus
(the IMF corpus included) before features.

## S10 — Rulings carried into this SAP (Ali to confirm)

`docs/DECISIONS_20260820_stageb_close.md`, all marked reversible:

- **D-1 The §11.5 fallback is NOT triggered.** §11.5 fires "iff neither branch
  survives" and states that P0 failing alone is not a trigger. G1–G4 are P0
  candidate gates; {P1, P2} is the family that obtains when no candidate passes.
  The purposive reading was rejected because it would reinterpret a frozen rule
  after measuring an inconvenient quantity. **The confirmatory analysis runs.**
- **D-4** §7.4 does not gate this freeze; no NLL number appears in any output
  until the regeneration has run.
- **D-5** The A11 SAR arm keeps A5.4's role and cannot rescue power — SAR
  precedes 1997 while the confirmatory window is bounded below at 1999.
- **D-6** The §11.4 descriptive update uses a **2027-01-15** snapshot.
- **D-7** The 70 spacing-loss documents are re-extracted via D9's own `pdfurl`
  fallback, replacement conditional on measured improvement; failures are
  excluded and counted in the intention-to-sample table.
- **D-8** The wholly-French document is excluded under D11 (existing precedent:
  `resolved:translation_D11`); the 11 bilinguals are excluded whole as the
  primary rule with an include-whole sensitivity arm. Confirmatory cost: ten
  documents in P1's pre-period, disclosed.
- **D-9** The 2 broken-CMap documents go through OCR under the same
  accept-only-if-better criterion; the 2002 and 2007 AR units are reassembled,
  returning two years to the RQ1 series.
- **D-10** No new automatic gate is added to `icr`/`pad` — that would itself be
  a post-inspection degree of freedom — but the quality scan is a mandatory
  diagnostic whose every flag gets a recorded ruling; the 12 borderline
  documents are kept.

## S11 — Deviations of record

`docs/DEVIATION_20260819_phase1_sproll.md` (D1–D7) and
`docs/DEVIATION_20260820_stageb_retrieval.md` (D1–D6). The second records, as
its first item, that the IMF corpus was retrieved **before** this document was
frozen, contrary to §11.3's ordering; no feature was computed and `s03` has
never run against it.

## S12 — Timestamp block (Ali)

```
SAP frozen ..............................  [date, UTC]
External timestamp ......................  [OSF registration DOI / Zenodo DOI]
Timestamp UTC ...........................  [ISO-8601]
This document sha256 ....................  [shasum -a 256 of the final file]
Package sha256 ..........................  [if deposited as an archive]
Operator ................................  Ali Çetinkaya
```

Until this block is filled, `s03` and everything downstream — OCR of the 12,055
scanned pages included — stay unrun.
