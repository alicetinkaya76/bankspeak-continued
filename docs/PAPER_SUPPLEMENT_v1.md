# Supplementary material

Companion to *Reconstructing Bankspeak: Eight Decades of World Bank Language, a
Corpus-Selection Effect, and an Unconfirmed Post-2022 Break*. Everything here was in the main text of an earlier draft
and was moved rather than cut: the material is evidence, but it is procedural
evidence, and a reader evaluating the claims does not need it inline.

Every figure regenerates from the deposited artifacts. Code archive:
`10.5281/zenodo.22152944` — the concept DOI, which always resolves to the latest
version. An earlier draft cited `10.5281/zenodo.22152945`, which is v1.0.0, the
one release cut before `data/meta/imf_document_index.csv` existed; a reader sent
there would not have found the access route the paper relies on. Stage-A preregistration `10.17605/OSF.IO/5C9J8`;
Stage-B analysis plan `10.5281/zenodo.22098259`.

---

## S1. PASS-P size under the null

The engine is bespoke, so we simulated it rather than assert it.

The null data-generating process is the fitted confirmatory model with the post
coefficient set to zero and everything else retained — real token offsets, real
year effects, real differential trend — plus a year-level log-scale shock at the
preregistration's own σ_δ = 0.3205. A pure Poisson null would understate the
variance the design actually faces and would flatter the test.

Each replicate's *p*-value is computed by enumerating all 512 sign patterns
exactly, so no simulation noise enters the inner loop and the only Monte Carlo
error is across replicates.

| nominal | P1 empirical | P2 empirical |
| --- | --- | --- |
| 0.01 | 0.0063 ± 0.0055 | 0.0050 ± 0.0049 |
| **0.05** | **0.0512 ± 0.0153** | **0.0425 ± 0.0140** |
| 0.10 | 0.1100 ± 0.0217 | 0.1100 ± 0.0217 |

Median null *p*: 0.336 (P1), 0.326 (P2). Reproduce with
`python tools/passp_calibration.py 800`.

## S2. Why condition 2's standardized arm was never evaluated

PREREG §6 fixes the standardization stratum as country (ISO3) mapped to region ×
income. The panel builder was instead given `<stratum>:<year>` — a key that is
institution-specific by construction, so `icr:2019` can never have IMF support and
`imf_article_iv:2019` can never have World Bank support. `build_pi` retained zero
groups and the battery recorded `pi_groups = 0` with zero post-period token
support in both institutions. Read literally that asserts the Bank and the Fund
share no common support. They do.

The premise recorded in the code — that World Bank documents carried no country
field — was false. The Documents & Reports `count` field holds the primary
country, is present on 2,406 of 2,407 sampled ICR/PAD documents, and had been in
the write-once API capture since the Stage-B harvest, never carried forward into
the frame.

The repaired ontology resolves 94.9% of sampled ICR/PAD documents to a region ×
income group, so 97.8% (P1) and 96.3% (P2) of panel documents carry one. It is
reported as a post-hoc sensitivity because §6 requires a year-matched income
classification and ours is current; substituting a different covariate after
seeing results is the degree of freedom this design exists to refuse.

It could not have moved the verdict in any case: C3 fails on merits in both
panels and C1 fails in P2, and a panel requires all four conditions.
Full record: `docs/DEVIATION_20260827_c2_standardization.md`.

## S3. Retrieval verification, and a measure rejected before use

Verification is a **ladder**, not four independent checks: each document is
resolved by exactly one rung and later rungs never run.

| rung | documents |
|---|---|
| R1 cover text | 869 |
| R2 scan-metadata stamp | 170 |
| R3 title similarity ≥ 0.80 | 16 |
| R4 country prefix + year | 9 |

Nine documents therefore rest on the weakest rung, which we state rather than
average away.

A token-set-overlap measure was proposed for the title rung and **rejected on a
negative control**: it scored a Finland 2004 report at 0.86 against a Tanzania
2004 report, above several true matches. The country-prefix rung replaced it, with
0 false positives in 300 mismatched pairs. The rejected measure is retained in the
test suite as a guard so it cannot be reintroduced.

## S4. The branch rule, and what it did and did not test

PREREG §2 makes a co-primary family conditional on a deterministic branch rule
over three World Bank policy-document candidates, in priority order CEM → SCD →
CPF, against four conjunctive gates G1–G4.

**No candidate passed G2**, which requires 25 pre-2023 years in common with the
Article IV frame. Measured: CEM 22, CPF 24, SCD 8. The ceiling of 24 is set by the
comparator frame's own span, so G2 was unsatisfiable for every candidate.

Because the gates are conjunctive, G1's blind audit and the P0 minimum detectable
effect were recorded `evaluated: false` and **must not be read as
tested-and-failed** (SAP addendum A5.7). G3 returned 1.0 for all three.

Decision D-1 records the consequence. The §11.5 fallback is triggered by literal
text that was not met; the purposive reading under which the family had "not
survived the Stage-B gates" was rejected. The confirmatory analysis ran as
preregistered on the default family — and §6.3 reports that the same design's own
power gate G4 (MDE₈₀ ≤ 0.60 log points) is missed by a factor of four to five.
Machine record: `data/analysis/branch_decision.json`.

## S5. Standardized-arm coverage, per cell

Worst-cell π coverage under the repaired country grouping: 0.844 (P1 IMF), 0.849
(P1 WB), 0.816 (P2 IMF), 0.880 (P2 WB).

Effective sample size as a fraction of the institution × period token mass, floor
0.50: P1 IMF post 0.498, P1 IMF pre 0.608, P1 WB post 0.583, P1 WB pre 0.596;
P2 IMF post 0.439, P2 IMF pre 0.574, P2 WB post 0.675, P2 WB pre 0.778.

The two failures are both the Fund's post period — the same fact seen twice, not
two independent problems.

Machine record: `data/analysis/panels_country/P*_battery.json`, key
`conditions.c2_stability.variants.standardized`.

## S6. Corpus quality scan, full counts

The scan walks the full 6,143-document extraction pool, a superset of the
3,802-document Stage-B sample, and returned: 6,078 `ok`, 23 too short to judge,
20 non-English suspected, 18 low-prose borderline, 3 mojibake suspected, 1 table
dump.

Restricted to the analysis corpus the flags number 48, of which ten are
non-English documents inside the Stage-B sample. Seven of those ten fall inside
the 1999–2025 confirmatory window and leave the panels; three (1997, 1997, 1998)
were already outside it.

Spacing-loss counts (70 of 2,688 server-text; 0 of 437 PyMuPDF) are measured over
the 3,125-document pre-freeze World Bank pool scanned for that defect, not over
the Table 1 sample. In the worst case whole-word matching missed 78% of its hits.

Machine records: `data/meta/corpus_quality_flags.csv`,
`data/meta/refetch_log.csv`, `data/meta/ocr_calibration.csv`.

## S7. Mandatory validation outcomes, full

PREREG §3 designates document prevalence and family breadth as validation
outcomes "reported alongside every confirmatory result", on the round-4 reasoning
that occurrence mass can be driven by repeated wording in a few documents.
Delete-one-year jackknife intervals.

| | P1 | P2 |
| --- | --- | --- |
| prevalence β (≥1 Tier-1 hit per document) | −0.637 [−3.859, 2.585] | −0.333 [−2.260, 1.594] |
| breadth β (distinct families per document) | +0.228 [−0.712, 1.167] | +0.124 [−0.465, 0.713] |
| quasi-dispersion (prevalence / breadth) | 1.038 / 0.827 | 1.011 / 0.777 |
| documents | 2,130 | 2,142 |
| count-specific downgrade triggered | no | no |

The intervals are roughly ten times the primary's bootstrap SD of 0.167. We
therefore neither claim the sign pattern establishes a marker-heavy-document
mechanism — the two validations disagree with each other — nor treat the
non-firing of the consistency rule as evidence that occurrence mass is well
spread.

Machine record: `data/analysis/panels/P*_battery.json`, key `validation`.

## S8. What the corpus repairs recovered for the RQ1 series

The assembled Annual Report series grew from 71 fiscal-year units to 76, with
missing years falling from seven to two (2000 and 2010 remain absent).

Two recoveries account for most of that, and both had previously passed every
provenance control while failing measurement validity:

- **Fiscal 2002** had been two un-OCR'd scans yielding twelve tokens and failing
  assembly QC. After OCR: 73,917 tokens at a 0.234 function-word share.
- **Fiscal 2007** had been 46,723 tokens of mojibake produced by a broken font
  encoding, which is what the broken ToUnicode CMap produced. OCR bypassed the
  encoding entirely: 50,807 tokens at 0.254.

None of the repairs was made with the RQ1 comparison in view, which is why the
agreement with the pamphlet is harder to attribute to analyst choice than a first
pass would be.

Machine record: `data/meta/ar_unit_qc.csv`, `data/features/ar_fy_features.csv`.
