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

## S1. PASS-P size under a Poisson null

The engine is bespoke, so we simulated it rather than assert it.

The null data-generating process is the fitted confirmatory model with the post
coefficient set to zero and everything else retained — real token offsets, real
year effects, real differential trend — plus a year-level log-scale shock at the
preregistration's own σ_δ = 0.3205.

**That shock does nothing, and an earlier version of this section said the
opposite.** It claimed a pure Poisson null "would understate the variance the
design actually faces and would flatter the test." The shock is drawn once per
year and added to both institutions in that year, and the design carries a
saturated set of year dummies, so it is absorbed exactly and generates no
identifying variance. This is not a new discovery: `docs/PREREG_DRAFT_v0.5.md`
and `src/mde_sim.py` both record that "the previous common year shock was
absorbed by C(year) and generated no identifying dependence" — which is precisely
why the preregistration replaced it with a World-Bank-specific differential shock
for the power analysis. The calibration script reintroduced the retired one, and
the sentence justifying it survived into the paper.

The table below is therefore **a size check under a Poisson null**, correctly
labelled. Its numbers are unaffected; only the claim about what null they came
from was wrong. The dispersion that the design does face, and that the frozen
estimator cannot see, is measured separately in S9.

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

## S9. What the frozen dispersion estimator can see, and what PASS-P does when it cannot

`mom_alpha` is the frozen NB2 dispersion estimator,
max(0, Σ((y−μ)² − μ) / Σμ²), with no degrees-of-freedom correction. The
confirmatory design fits **30 parameters on 54 cells**, leaving 24 residual
degrees of freedom, so the fitted μ absorbs most of the variation the estimator
needs in order to see dispersion at all.

Two experiments, both simulated from the real design, offsets and fitted values,
1,000 replicates each, seeded from the frozen `SEED`
(`tools/dispersion_calibration.py`).

**Recovery** draws NB2 data at a known α, refits, and reports what `mom_alpha`
returns. **Size** imposes the null — the restricted fit's values as the mean —
adds NB2 noise at the same α, and runs the frozen PASS-P.

| panel | true α | recovered α̂ | shrunk by | PASS-P size at nominal 0.05 |
|---|---|---|---|---|
| P1 | 0.00 | 0.0000 | — | 0.057 |
| P1 | 0.05 | 0.0038 | 13.1× | **0.093** |
| P1 | 0.10 | 0.0115 | 8.7× | **0.095** |
| P1 | 0.25 | 0.0348 | 7.2× | **0.082** |
| P1 | 0.50 | 0.0638 | 7.8× | **0.079** |
| P2 | 0.00 | 0.0000 | — | 0.054 |
| P2 | 0.05 | 0.0025 | 20.4× | **0.072** |
| P2 | 0.10 | 0.0090 | 11.1× | **0.085** |
| P2 | 0.25 | 0.0296 | 8.4× | **0.080** |
| P2 | 0.50 | 0.0561 | 8.9× | **0.084** |

Bold marks a size more than two Monte Carlo standard errors above nominal
(MC SE ≈ 0.007 at 1,000 replicates).

Two readings, and the second is the one that matters.

**The estimator cannot see dispersion that is there.** At every non-zero α it
returns between a seventh and a twentieth of the truth. On the real data it
returns α̂ = 0.0121 (P1) and 0.0005 (P2), which on this evidence is what a true α of
roughly 0.10 looks like after the design has absorbed it. Condition 2's NB2 arm
therefore fits a model barely distinguishable from the Poisson primary; its pass
is real but nearly assured, and it is not evidence that the counts are
equidispersed.

**PASS-P over-rejects when it is.** At α = 0 the test holds (0.057 / 0.054). At
the dispersion the data are consistent with it reaches 0.095 (P1) and 0.085 (P2)
against a nominal 0.05. The single *p* that reached significance under the
preregistered rule — P1's 0.0142 — comes from a test roughly twice as easy to
trip as its label, so **that one result is less credible than its *p* suggests.**

It does **not** follow that the non-rejections are evidence of absence, and an
earlier version of this section said the size inflation made "the paper's
negative verdict safer", which was wrong twice over: an anti-conservative test
tells you nothing about the panels that did not reject, and low power still
governs what a non-rejection can mean. What the inflation does is remove the one
reading under which the paper might have been said to have found something.

Neither experiment was preregistered. Both are post-hoc measurements of a frozen
component, prompted by external review, and neither changes any reported
coefficient, interval or condition outcome.

## S10. Two post-freeze checks the review asked for

Neither was preregistered. Both leave `src/bootstrap_engine.py` untouched and
gate nothing; the confirmatory result stands as reported. They exist because a
reviewer was right that candour about a miscalibrated procedure is not the same
as showing the conclusion survives one.

### S10.1 A dispersion estimate that respects the degrees of freedom

S9 showed the frozen `mom_alpha` recovers a fraction of the dispersion present.
The standard repair is the moment condition that accounts for the fitted
parameters — choose α so that

  Σ (y − μ)² / (μ + α μ²) = n − p

instead of dividing by *n*. With 30 parameters on 54 cells the two differ a great
deal. Size is measured under a null carrying the dispersion the corrected
estimator itself reports, 3,000 replicates, Monte Carlo standard error 0.004.

| panel | α frozen | α corrected | exact hits, frozen | exact hits, corrected | size@0.05 frozen | size@0.05 corrected |
|---|---:|---:|---:|---:|---:|---:|
| P1 | 0.0121 | 0.0520 | 8/512 | 8/512 | 0.081 | 0.078 |
| P2 | 0.0005 | 0.0425 | 50/512 | 46/512 | 0.065 | 0.065 |

**The verdict is robust and the size is not repaired.** The corrected α is 4.3×
the frozen one on P1 and 85× on P2, yet the exact *p* moves by at most four
patterns in 512 and no condition-1 outcome changes. Meanwhile empirical size
stays near 0.078–0.081 on P1 against a nominal 0.05 whichever estimator is used.

The inflation therefore does **not** originate in the dispersion estimator, and
the remedy a referee would naturally prescribe does not deliver a correctly sized
test on this design. What is left is the block construction itself: nine blocks,
a 512-point support, and a studentisation whose denominator is estimated from the
same nine sums the numerator uses. A design wanting a correctly sized test here
needs more blocks — which means more years — not a better dispersion estimate.

### S10.2 Dropping every document seen at Stage A

748 Stage-B World Bank documents were also in the Stage-A frame. They are exactly
the intersection of the two frozen sampling frames, so the set needs no
reconstruction. Panels are rebuilt from document-level counts with those
documents removed from the Bank arm; the comparator is untouched. Both panels
retain all 27 common years, so nothing is lost to the common-year rule.

| panel | WB docs | dropped | β full | β reduced | *p* full | *p* reduced | condition 1 |
|---|---:|---:|---:|---:|---:|---:|---|
| P1 | 1066 | 164 | +0.5856 | +0.6130 | 0.0142 | 0.0103 | pass → pass |
| P2 | 1078 | 192 | +0.3319 | +0.3206 | 0.0929 | 0.0611 | fail → fail |

**Removing the exposed documents strengthens both estimates.** If prior exposure
had manufactured the effect, dropping it would shrink the coefficient; it grows
on P1 and the *p*-values fall on both panels. Condition 1 is unchanged either
way. This does not make the design outcome-naïve — it was not — but it rules out
the specific worry that Stage-A inspection produced the Stage-B contrast.

Reproduce with `python tools/dispersion_robust_inference.py 3000` and
`python tools/stage_a_exposure_sensitivity.py`.

### S10.3 What the PASS-E intervals actually cover

Table 4 labels them nominal because no coverage study existed. They are still
read — §6.3 turns on a lower bound clearing zero by 0.0029 — so this measures it.
Simulate at a known β from the real design, run the frozen PASS-E, count how often
the interval contains the truth. Two nulls: Poisson, and NB2 at the dispersion
the degrees-of-freedom-corrected estimator reports (S10.1), since S9 established
the frozen estimator cannot see it. 400 replicates, B reduced to 499 from the
frozen 9,999 to make the study feasible.

| panel | truth | null | coverage (nominal 0.95) |
|---|---|---|---:|
| P1 | β = 0 | Poisson | 0.873 ± 0.017 |
| P1 | β = 0 | NB2 at the corrected α | 0.848 ± 0.018 |
| P1 | β = observed | Poisson | 0.858 ± 0.017 |
| P1 | β = observed | NB2 at the corrected α | 0.805 ± 0.020 |
| P2 | β = 0 | Poisson | 0.890 ± 0.016 |
| P2 | β = 0 | NB2 at the corrected α | 0.830 ± 0.019 |
| P2 | β = observed | Poisson | 0.907 ± 0.014 |
| P2 | β = observed | NB2 at the corrected α | 0.820 ± 0.019 |

**They under-cover everywhere, by six to fifteen points.** Under a Poisson null
coverage runs 0.858–0.907; under the dispersion the data are consistent with it
falls to 0.805–0.848. The intervals are too narrow, not too wide.

Which way this cuts is worth stating precisely. Narrow intervals make it *easier*
to exclude zero, and exclusion of zero is a conjunct of conditions 2 and 3 — so
the error is permissive, and both conditions failed anyway, on the sign and
magnitude of the refitted coefficient rather than on interval width. The reading
that does not survive is any that treats a bound barely clearing zero as evidence:
§6.3's H-SHARED interval is narrower than a 95% interval would be, on draws that
S6.3 shows are not a neutral subsample, and both facts point the same way.

Reproduce with `python tools/passe_coverage.py 400 499`.
