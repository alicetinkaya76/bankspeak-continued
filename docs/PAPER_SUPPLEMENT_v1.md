# Supplementary material

Companion to *Reconstructing Bankspeak: Eight Decades of World Bank Language, a Corpus-Selection Effect, and an Unconfirmed 2023-2025 Differential Shift*. Everything here was in the main text of an earlier draft
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

Decision D-1 records the consequence. The PREREG §11.5 fallback is triggered by literal
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
1,000 replicates each (`tools/dispersion_calibration.py`). The streams are
hashed per panel and per α; they were previously derived by adding the panel
label's length to the frozen seed, which gave P1 and P2 one stream, and every
figure in this table is from the rerun (S10's opening note).

**Recovery** draws NB2 data at a known α, refits, and reports what `mom_alpha`
returns. **Size** imposes the null — the restricted fit's values as the mean —
adds NB2 noise at the same α, and runs the frozen PASS-P.

| panel | true α | recovered α̂ | shrunk by | PASS-P size at nominal 0.05 |
|---|---|---|---|---|
| P1 | 0.00 | 0.0000 | — | 0.061 |
| P1 | 0.05 | 0.0036 | 14.0× | **0.082** |
| P1 | 0.10 | 0.0125 | 8.0× | **0.107** |
| P1 | 0.25 | 0.0355 | 7.0× | **0.102** |
| P1 | 0.50 | 0.0651 | 7.7× | **0.111** |
| P2 | 0.00 | 0.0000 | — | 0.040 |
| P2 | 0.05 | 0.0021 | 23.3× | **0.068** |
| P2 | 0.10 | 0.0094 | 10.6× | **0.075** |
| P2 | 0.25 | 0.0293 | 8.5× | 0.055 |
| P2 | 0.50 | 0.0567 | 8.8× | **0.072** |

Bold marks a size more than two Monte Carlo standard errors above nominal
(MC SE ≈ 0.007 at 1,000 replicates).

Two readings, and the second is the one that matters.

**The estimator cannot see dispersion that is there.** At every non-zero α it
returns between a seventh and a twenty-third of the truth. On the real data it
returns α̂ = 0.0121 (P1) and 0.0005 (P2), which on this evidence is what a true α of
roughly 0.10 looks like after the design has absorbed it. Condition 2's NB2 arm
therefore fits a model barely distinguishable from the Poisson primary; its pass
is real but nearly assured, and it is not evidence that the counts are
equidispersed.

**PASS-P over-rejects when it is.** At α = 0 the test holds (0.061 / 0.040). At
the dispersion the data are consistent with it reaches 0.107 (P1) and 0.075 (P2)
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

## S10. Post-freeze checks the review asked for

None was preregistered. All leave `src/bootstrap_engine.py` untouched and gate
nothing; the confirmatory result stands as reported. They exist because a
reviewer was right that candour about a miscalibrated procedure is not the same
as showing the conclusion survives one.

**A defect that ran through three of them, and what it moved.** Each
post-freeze simulation derived its random stream by adding a label's *length*
to the frozen seed. `len("P1") == len("P2")`, so S10.1's two panels ran their
entire size studies on one stream and were never independent estimates.
`len("poisson") == len("ar1_nb2")`, so two of S10.4's three arms were coupled
while the pair its conclusion rested on was not — the opposite of what its own
docstring claimed. S10.3's seed omitted the panel altogether. All three now
hash the labels (`src/percell_seed.stream_seed`) and every figure below is from
the rerun. The numbers moved by one to three Monte Carlo standard errors and no
verdict changed, which is what should happen when a defect affects
independence rather than location — but it was found by an external reading of
the code, not by any check in this repository, and the ones that report shared
streams as independent are the ones worth stating.

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
| P1 | 0.0121 | 0.0520 | 8/512 | 8/512 | 0.076 | 0.078 |
| P2 | 0.0005 | 0.0425 | 50/512 | 46/512 | 0.064 | 0.066 |

**The verdict is robust and the size is not repaired.** The corrected α is 4.3×
the frozen one on P1 and 85× on P2, yet the exact *p* moves by at most four
patterns in 512 and no condition-1 outcome changes. Meanwhile empirical size
stays near 0.076–0.078 on P1 against a nominal 0.05 whichever estimator is used.

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
way. **This does not rule out selection**, and an earlier version of this
sentence said it did. Selection can move an estimate either way, and the check
covers only the identified World Bank Stage-A files — not IMF selection, source
availability, the report-family rules, or the wider set of analytic choices. What
it establishes is narrower and still worth having: **the estimate did not
attenuate when the Stage-A-inspected files were removed.**

Reproduce with `python tools/dispersion_robust_inference.py 3000` and
`python tools/stage_a_exposure_sensitivity.py`.

### S10.3 What the PASS-E intervals actually cover

Table 4 labelled them nominal because no coverage study existed. They are still
read — §6.2's H-SHARED paragraph turns on a lower bound clearing zero by 0.0029
— so this measures it.
Simulate at a known β from the real design, run the frozen PASS-E, count how often
the interval contains the truth. Four nulls, because S10.4 showed that an i.i.d.
null cannot test a block procedure: Poisson, NB2 at the corrected dispersion, the
**preregistered differential AR(1)**, and AR(1) with that dispersion. 200
replicates, B reduced to 299 from the frozen 9,999 to make the study feasible.

| panel | truth | null | coverage (nominal 0.95) |
|---|---|---|---:|
| P1 | β = 0 | i.i.d. Poisson | 0.875 ± 0.023 |
| P1 | β = 0 | i.i.d. NB2 at the corrected α | 0.845 ± 0.026 |
| P1 | β = 0 | preregistered AR(1) | 0.770 ± 0.030 |
| P1 | β = 0 | AR(1) + corrected α | 0.760 ± 0.030 |
| P1 | β = observed | i.i.d. Poisson | 0.860 ± 0.025 |
| P1 | β = observed | i.i.d. NB2 at the corrected α | 0.780 ± 0.029 |
| P1 | β = observed | preregistered AR(1) | 0.705 ± 0.032 |
| P1 | β = observed | AR(1) + corrected α | 0.750 ± 0.031 |
| P2 | β = 0 | i.i.d. Poisson | 0.910 ± 0.020 |
| P2 | β = 0 | i.i.d. NB2 at the corrected α | 0.815 ± 0.027 |
| P2 | β = 0 | preregistered AR(1) | 0.745 ± 0.031 |
| P2 | β = 0 | AR(1) + corrected α | 0.765 ± 0.030 |
| P2 | β = observed | i.i.d. Poisson | 0.890 ± 0.022 |
| P2 | β = observed | i.i.d. NB2 at the corrected α | 0.825 ± 0.027 |
| P2 | β = observed | preregistered AR(1) | 0.790 ± 0.029 |
| P2 | β = observed | AR(1) + corrected α | 0.745 ± 0.031 |

**They under-cover under every null, and worst under the preregistered
one.** 0.860–0.910 under i.i.d. Poisson, 0.780–0.845 with the corrected
dispersion, **0.705–0.790 under the AR(1) shock**, and 0.745–0.765 with both.
An earlier version of this paragraph called that fall monotonic. It is not: mean
coverage runs 0.884, 0.816, 0.753, 0.755, so the fourth step rises slightly, and
the AR(1) arm alone is the worst of the four. Adding dispersion on top of the
serial shock does not compound it. Against a nominal 0.95 that is a shortfall of four to twenty-five points,
and the ordering is the whole point: the closer the null gets to the process the
design was preregistered against, the worse the intervals cover.

Which way it cuts, precisely. Narrow intervals make it *easier* to exclude zero,
and exclusion of zero is a conjunct of conditions 2 and 3 — so the error is
permissive, and both conditions failed anyway on the refitted coefficient's sign
and magnitude rather than on width. What does not survive is any reading that
treats a barely-clearing bound as evidence: §6.2's H-SHARED interval rests on
draws that are not a neutral subsample — 1,607 of 9,999 were discarded and every
one failed the same way. That much is measured. Whether the H-SHARED bootstrap
under-covers as the PASS-E procedure does is not: it is a different bootstrap,
on the comparator series alone, and no coverage study of it exists.

Reproduce with `python tools/passe_coverage.py 200 299`.

### S10.4 An upper bound on the governing rule's error rate, and what it turns on

An earlier version of this section reported that "the governing test rejects
about twice as often as it claims". It did not measure the governing test, and
the sentence has been withdrawn. This section reports what was measured, an
upper bound on the governing rule's error rate, and — the part that matters
most — how much that bound depends on a choice nobody preregistered.

**What the earlier study did.** `tools/ar1_null_calibration.py` simulated P1 and
P2 in separate loops, each under its own restricted fit, and counted how often
each panel's raw two-sided *p* fell below 0.05. External review named three ways
that differs from the preregistered rule.

*The panels are not independent.* P1 is ICR against the Fund and P2 is PAD
against the Fund, and the comparator arm is not merely similar across the two —
it is the same twenty-seven cells, the same counts, the same token totals. Half
of every panel is shared. Separate loops replace a strongly dependent pair with
an independent one.

*The rule is not a raw threshold.* PREREG §5, as `holm_family` implements it,
sorts the two *p*-values and rejects the smaller only at α/2 = 0.025 and the
larger only at α = 0.05, and confirms the family only if some panel clears Holm
*and* C2 *and* C3 *and* C4.

*The inner p does not need sampling.* Twenty-seven years give nine blocks, so
the support is exactly 512 and the *p*-value is a count. The study drew 999
signs from a set of 512.

All three are correct. `tools/joint_holm_calibration.py` repairs all three and
adds the rungs between, because the result is not one number.

**The decision rule, on one set of replicates.** S10.4's own null — each panel
under its own restricted fit, the two panels drawn independently — evaluated
four ways on *the same* 4,000 synthetic datasets. Common random numbers, so any
gap between rows is the rule and not the draw.

| decision rule, on identical data | rate |
|---|---:|
| at least one panel below a raw 0.05 | 0.190 |
| **the preregistered Holm step-down (C1)** | **0.109** |
| Holm C1 together with C4 | 0.083 |
| the same datasets, inner *p* sampled at B = 999 rather than enumerated | 0.103 |

The step-down rejects less often than the raw threshold, as a step-down must,
and adding C4 removes about a fifth of what remains. Sampling the inner *p*
instead of enumerating it moves the family rate by 0.006
and the per-panel rate by 0.001 — the criticism is correct
and, on this design, empirically inert.

*An earlier version of this table split these four numbers across three
scenarios with three different seeds, labelled two of them "no Holm", and
computed a Holm rate in all three. The movement between those rows isolated
nothing. External review found it; the rows above replace them.*

**The same rule under other nulls.** Everything below is the Holm C1 rate.

| null | P1 raw .05 | P2 raw .05 | any panel raw .05 | Holm C1 | MC SE |
|---|---:|---:|---:|---:|---:|
| **drawn jointly**: one comparator draw, one shared shock | 0.118 | 0.092 | 0.150 | **0.086** | 0.004 |
| the same, with independent World Bank shocks | 0.116 | 0.100 | 0.204 | 0.119 | 0.005 |
| the same, with the corrected NB2 dispersion | 0.110 | 0.104 | 0.172 | 0.102 | 0.005 |
| **no serial shock at all**, same fitted means | 0.051 | 0.055 | 0.101 | 0.045 | 0.003 |
| fitted means, differential trend removed | 0.068 | 0.058 | 0.092 | 0.049 | 0.003 |
| fitted means, year profile flattened | 0.089 | 0.076 | 0.122 | 0.074 | 0.004 |
| both removed | 0.045 | 0.032 | 0.060 | 0.028 | 0.003 |
| **flat rates**: each series at its own pooled rate | 0.041 | 0.037 | 0.060 | 0.030 | 0.003 |
| PREREG §8's parity rate on observed tokens | 0.046 | 0.046 | 0.073 | 0.036 | 0.003 |
| **PREREG §8 literally**, as `src/mde_sim.py` runs it | 0.046 | 0.049 | 0.075 | **0.036** | 0.003 |

4,000 replicates each, exact 512-point inner *p*, the preregistered Holm
step-down applied every replicate.

**What this rate is, and is not.** It is the probability that the Holm step-down
rejects at least one panel. It is **not** the governing rule's error rate. The
governing rule is C1 *and* C2 *and* C3 *and* C4; C2 needs a standardised
document-level redraw and C3 the guard count series, and inventing null
processes for those would be modelling rather than calibration. A conjunction
can only reject less often than its first condition, so every rate here is an
**upper bound** on the full rule's false-positive rate. Where C4 is simulated it
is reported, and it lowers the bound: 0.109 → 0.083 under
S10.4's null, 0.086 → 0.064 under the joint one. The full rule's actual
error rate is not measured by this study.

**What moves it is the null's mean structure, by a factor of three.** The
preregistered process gives 0.0365; the same rule, the same shock, the same
ρ and σ, under means fitted to the observed series, gives 0.086. Both are
defensible nulls and the design specified neither for this purpose. The
preregistered power run recorded 0.039 for exactly this quantity in August
(`docs/MDE_P1P2_20260820.md`, θ = 0); an external reviewer's independent
implementation returned 0.0335 ± 0.0040; this one returns
0.0365 ± 0.0030. Three implementations, one number. The
disagreement is not about arithmetic. (146 of 4,000 replicates is an exact
rounding tie at three decimals; the table above prints 0.036 and the manuscript
0.0365, so the fourth digit is given here to keep one quantity from being
resolved two ways in two documents.)

**On the dependence comparison, narrowly.** Drawing the panels jointly with one
shared World Bank shock gives 0.086; the same shared comparator draw with
*independent* World Bank shocks gives 0.119. An earlier version explained that
by asserting that independence is Holm's worst case for two hypotheses. That is
false and is withdrawn: under the global null "at least one Holm rejection" is
min(*p*₁, *p*₂) ≤ α/2, which is α − α²/4 under independence, α/2 under perfect
positive dependence, and approaches α when the two lower-tail events are
disjoint. Independence is near the top of that range, not its maximum. The
comparison above is a property of the modelled dependence — specifically of
handing both World Bank arms the same shock, which is what PREREG §8 specifies —
and not a general fact about Holm.

**Two explanations were tried and both are refuted by the tool's own
diagnostics**, which is why neither appears above as a mechanism.

The first was a signal-to-noise account: the preregistered simulation put the
Fund arm at parity with the Bank's rate, about 27 marker counts a year, where it
actually carries about 110, and Poisson noise on the log scale falls as 1/√μ.
That is true and it is reported per scenario, but it does not track the ladder —
the flat-means null carries a *higher* ratio than the fitted-means null and less
than half the family error.

The second was leverage: the joint fit gives the Bank arm a differential trend
of about 5.7 log points a year, so its mean roughly quadruples across the window
and the score's variance should concentrate in the last block, which is exactly
the post window. The share is measured and it runs the wrong way — every
inflated scenario sits at 0.334 to 0.371, below the well-behaved ones, where an
equal split would be 0.111. The rank correlation across the ladder is −0.73 (*p*
= 0.005): more leverage, *less* size. It runs that way for a reason. When one
block dominates the studentised denominator, nearly every sign pattern produces
a statistic as large as the observed one, and the test goes *conservative*.

One well-behaved scenario is a genuine counterexample and is reported as one.
`fitted_joint_poisson_only` carries the lowest leverage in the whole study,
0.297, and is nonetheless correctly sized at 0.045 — so the well-behaved range
is 0.297 to 0.477, not the tight 0.44 to 0.48 an earlier version of this
paragraph quoted by silently dropping it. The inverse relation is the tendency
across the ladder, not a law, and the row that breaks it is the row with no
serial shock in it at all.

No third explanation is offered here. What can be stated is bounded and
measured:

- Under the fitted means the test is correctly sized with no shock at all
  (0.045) and anti-conservative with one.
- **Roughly two fifths of the excess survives at ρ = 0** — an i.i.d.
  multiplicative World Bank overdispersion with no serial dependence anywhere,
  giving 0.063 against 0.045. So *"serial dependence is the cause"* is too
  strong, and the earlier version of this section said it. Unmodelled
  one-armed overdispersion does a large part of the work.
- With both the year profile and the differential trend removed, the same shock at the same ρ and σ produces 0.028, below nominal — and the independently constructed flat-rate null reproduces that at 0.031.
- The error rate is sensitive to ρ in the direction expected: 0.063 at ρ = 0,
  0.077 at 0.3, 0.086 at 0.5, 0.121 at 0.7. Redrawing ρ ~ U(0.2, 0.8) and
  σ ~ U(0.20, 0.45) every replicate — the frozen pair is a point estimate that
  was never given an interval — gives 0.094.

**What this does to P1's *p*.** The useful quantity is not a size but a
calibrated tail probability: how often a null replicate produces a *p* at least
as extreme as the one observed. P1's exact *p* is 8/512 = 0.0156. Under the preregistered null that tail is
0.014 — essentially unchanged, and marginally *smaller* than the nominal figure
rather than larger. Under the fitted-means joint null it is 0.042, which is
**above** the 0.025 the Holm step demanded: on that calibration condition 1
would not have passed on P1 either. An earlier version of this paragraph called
both figures weaker than 0.0156 and said neither approached 0.025. Neither claim
survives the numbers. Both are model-dependent calibrated tails and neither
replaces the preregistered test's *p*.

**C2 and C3 are not simulated, and every family rate above is therefore an upper
bound.** C2 needs a standardized document-level redraw and C3 needs the guard
count series; inventing null processes for those would be modelling, not
calibration. C4 *is* computable from the same cells and is simulated: adding it
takes the joint family rate from 0.086 to 0.064 and the independent-panel rate
from 0.114 to 0.086. The conjunction is genuinely tighter than its first
conjunct, which is what a conjunctive rule is for.

**What follows for the manuscript.** The claim that the governing test rejects
twice as often as it claims is withdrawn: it rested on a per-panel raw threshold
under one fitted null. The claim that survives is weaker and better supported —
across the eighteen nulls examined the Holm C1 rejection rate — an upper bound
on the preregistered rule's error rate — runs
from 0.028 to 0.121, it is above nominal under every null fitted to the observed
series, and P1's *p* is worth less than its face value under all of them.
Holding the preregistered dependence parameters and varying only the mean
structure — the axis this section is about — the range is 0.0365 to 0.086. Both
brackets are stated because the wider one is what a reader checking the table
will compute, and three rows of that table sit above the narrower one for
reasons that are *not* mean structure: independent World Bank shocks at 0.119
and the corrected NB2 dispersion at 0.102 change the dependence and the
variance function, and redrawing ρ ~ U(0.2, 0.8) and σ ~ U(0.20, 0.45) gives
0.094 by varying the dependence parameters themselves. An earlier version of
this sentence put that 0.094 inside the mean-structure bracket, which is where
it does not belong. §6.2's block-construction sentence is narrowed accordingly: blocks fail
to absorb the dependence under the fitted means and absorb it more than
adequately under the preregistered ones, and this study cannot say which is the
right null to hold the design to.

Reproduce with `python tools/joint_holm_calibration.py 4000 4000`; the per-panel
study it replaces is still runnable as `python tools/ar1_null_calibration.py
3000 999`.

### S10.5 Is the post-window comparator a catch-up cohort?

Article IV consultations lapsed widely through 2020–21, so a 2023–25 roster could
be substantially delayed reports — different in subject, urgency and length from a
routine cycle even within the same country. Country and year effects absorb level
differences, not a change in what kind of document a country-year contains. An
external review raised this as a live alternative explanation and it is a fair
one.

**The screen needs a baseline, and with one it does not fire.** Measuring, for
every country-year in the index, the gap since that country's previous sampled
observation:

| window | country-years | gap ≥ 3 years or first appearance |
|---|---:|---:|
| pre-2023 | 934 | **61.7%** |
| 2023–25 | 118 | **56.8%** |

The post window is *less* delayed than the pre-period, not more. Our comparator
samples about forty documents a year across roughly forty countries, so a
multi-year gap is the normal condition throughout the span rather than a
post-2020 anomaly. A screen reporting 56.8% in the post window looks alarming
until the 61.7% baseline is put beside it.

**The estimate is robust to balancing anyway; its *p* is not.** Restricting the
comparator to countries with at least one routine post observation (gap under
three years) drops 793 of 1,064 IMF documents:

| panel | β full | β balanced | *p* full | *p* balanced |
|---|---:|---:|---:|---:|
| P1 | +0.5856 | +0.5807 | 0.0127 | 0.0310 |
| P2 | +0.3319 | +0.4050 | 0.0913 | 0.2383 |

β moves by 0.005 on P1. The *p*-value rises because the balanced comparator is a
quarter of the size, which is a precision loss rather than evidence of bias — and
on P1 it is enough to cross the Holm threshold, so condition 1 would not pass on
the balanced comparator. Neither panel passed the full rule regardless.

Reproduce with `python tools/imf_cadence_balance.py`.

### S10.6 Is the Tier-2 register measurable across eight decades?

A fixed contemporary word list is not automatically a period-neutral instrument
against a 1946–65 baseline: a word form existing early does not mean its
institutional sense, or the occasion for using it, existed too. An external
review raised this, and its examples were wrong — `alignment`, `augment`,
`calibrate`, `chatbot`, `corpus`, `digital` and `hallucination` were named and
none is in the list — but the objection itself is right, so it is measured here
on the actual 35 terms.

The split is a judgement and is made in the open. **Modern register** is
development-and-management vocabulary whose current sense postdates the early
window: stakeholder, sustainable, governance in the Bank's own later sense,
empower, leverage as a verb, holistic, transformative, resilience as policy,
scalable, unlock, vibrant, landscape as metaphor, innovative, harness.
**Period-plausible** is ordinary English with a stable institutional sense:
accelerate, bold, crucial, foster, robust, strengthen, vital.

Counts are from the assembled World Bank fiscal-year texts, which are public
disclosure. No IMF text is involved.

| subset | terms | 1946–65 | 2020–24 | ratio |
|---|---:|---:|---:|---:|
| all Tier-2 | 35 | 0.204 | 5.797 | **28.4×** |
| period-plausible only | 12 | 0.192 | 2.083 | **10.9×** |
| modern register only | 23 | 0.013 | 3.714 | 295× |

**The thirtyfold headline is substantially a modern-vocabulary effect.** On the
period-plausible subset the rise is **10.9×** — still large, still real, and about
a third of the headline. The modern subset rises from 0.013 per thousand, which
is a base so near zero that its ratio is a statement about absence rather than
about growth.

**22 of the 35 terms do not occur at all in 1946–65.** Not rare: absent. For those
terms the early-window measurement is structurally zero, so the comparison is
between a register that existed and one that had not yet been coined in this
sense.

The honest description of Tier-2 is therefore **a prespecified contemporary
institutional register**, not a timeless measure of bureaucratic style, and §6.1's
Tier-2 rise should be read with the period-plausible figure beside it and with
the convention named: thirtyfold is the equal-year production rule, 10.9× the
token-weighted boundary rule.
The Tier-1/Tier-2 separation the design turns on is unaffected: Tier-2 exists to
show that a register can rise for reasons having nothing to do with language
models, and it does that whichever subset is used.

Reproduce with `python tools/tier2_period_fairness.py`.

### S10.7 The comparator's sampling frame, published

The comparator is not an annual census of Article IV staff reports and the
manuscript never said what it was instead. It is a **capped annual
cross-section**: a preregistered ceiling of 40 documents per year-genre cell
(PREREG §7, `docs/PREREG_DRAFT_v0.5.md:548`; the literal constant is the CLI
default at `src/s09_frame_sampler.py:39`), applied by equal-probability simple
random sampling without replacement inside each cell.

**Every piece of that is in the repository and none of it was in the paper.**

The Fund's own listing returned 7,451 hits, a number the harvester logs and then
enforces: the per-year windows must sum to the global `totalCount` or the build
refuses (`src/s09a_imf_articleiv_frame.py:612-620`). Every one of the 7,451
carries a disposition. 2,788 survive as eligible units across 1999–2025, and
1,064 are drawn.

| fiscal year | listing hits | eligible | sampled | inclusion probability | cap binds |
|---|---:|---:|---:|---:|---|
| 1999 | 151 | 24 | 24 | 1.000 | no |
| 2000 | 158 | 49 | 40 | 0.816 | yes |
| 2005 | 296 | 111 | 40 | 0.360 | yes |
| 2010 | 322 | 126 | 40 | 0.317 | yes |
| 2015 | 258 | 113 | 40 | 0.354 | yes |
| **2020** | 99 | **44** | 40 | **0.909** | yes |
| 2021 | 229 | 103 | 40 | 0.388 | yes |
| 2022 | 244 | 113 | 40 | 0.354 | yes |
| 2023 | 266 | 117 | 40 | 0.342 | yes |
| 2024 | 287 | 128 | 40 | 0.312 | yes |
| 2025 | 276 | 129 | 40 | 0.310 | yes |

Every year 1999–2025 is in `data/analysis/imf_frame_publication.csv` with its
cell seed. Three things in that table matter.

**1999 is short because the universe was short, not because of the cap.** It is
the only year in the window below 40 and every eligible unit was taken. The cap
binds in the other twenty-six.

**Whether 1999 is a design boundary or a coverage limit is not settled here.**
The frame builder's declared window is 1994–2025 and the data begin in 1999; 137
listing hits dated before 1999 exist and all 137 were excluded at the
country-name step. Those are different claims — the Fund publishing no Article
IV staff reports before the April 1999 pilot, and this pipeline being unable to
place the earlier ones — and nothing in the repository decides between them. The
tool flags it `needs_human_review` and this supplement leaves it flagged.

**Inclusion probabilities run from 0.310 to 1.000, so the design weights years
by cap rather than by the Fund's output.** A year with 129 eligible documents
and a year with 44 contribute the same 40. Nothing in the analysis reweights for
this, and any pooled comparator statistic should be read as "40 documents a
year", not "the Fund's Article IV output".

**Fiscal 2020 is the outlier and it sits inside the pre-period.** Only 44
eligible units against 103 to 129 in the surrounding years — the Fund published
far fewer Article IV consultations that year — so 2020's inclusion probability is
0.909 where its neighbours are near 0.33. S10.5 tests the post window for a
catch-up cohort and finds the pre-window more delayed than the post; this is the
same disturbance seen from the frame side, and it is on the pre side of the cut.

**The draw is exactly reproducible from the published code and frame, and this
is checked rather than asserted.** Replaying `sample_frame` on the eligible frame
at cap 40 returns the frozen 1,064 ids exactly: zero in the replay and not in the
frozen file, zero the other way, in every one of the twenty-seven years. Selection
order comes from a lexicographic sort of Country Report numbers, which are
unique, so there are no ties in the draw; ties are broken earlier, when
`resolve_revisions` keeps one unit per report number by latest publication date,
then a corrigendum or revised title, then the smallest URL. The seed is per cell,
`sha256("20260806|imf|article_iv|<year>")`, published per year in the CSV.

**Reproducible from this frame is not the same as reproducible from a refreshed
one, and the difference is large.** The per-cell seed protects a cell against
changes in *other* cells; it does nothing against a change in the cell's own
population, because `random.Random.sample` draws positional indices and the
positions move when the population does. Deleting one eligible row that was
never selected, and redrawing, leaves on average 18.4 of that year's 40
selections in place if the deleted row sorts first, 29.6 if it sorts mid-order
and 35.8 if it sorts last — measured across all twenty-six capped cells. An
independent redraw would retain 16.4. **It is the frozen CSV, not the seed, that
makes this sample recoverable.**

**1,064 is documents drawn.** The frozen sample carries an `analysis_eligible`
column and it is blank in all 1,064 rows — the sampler writes the column and
nothing backfills it. What closes the gap is the retrieval record, not the
column: `docs/IMF_RETRIEVAL_20260820.md` logs 1,064 sampled, 1,064 downloaded,
1,064 verified.

**What the frame does not carry.** Both CSVs record report number, country, ISO3
code, publication date, title and URL. Region, income group and programme status
are not columns of either; region and a single-vintage income classification are
reachable only by joining `data/meta/country_ontology.csv`, and programme status
is not in the repository at all. So the standardisations an external reader might
ask for — region, income group, programme — cannot be run from the deposited
artifacts as they stand, and the income vintage would be anachronistic for the
early years even if they could.

**And 2,788 is a lower bound, not the universe.** 2,341 listing hits are
labelled `unmapped_country`: the title's country prefix did not match the alias
table. An earlier version of this paragraph said those were not established
non-Article-IV documents but documents the pipeline could not place. That was
more agnostic than our own metadata warrants, and it understated the frame.
The listing carries the Fund's own content-type label, and joining it back
places all 2,341: **1,736 Public Information Notices, 538 press releases, 44
mission concluding statements, 13 standard pages, 5 transcripts, 3 issue pages
and 2 rows typed only `Pdf`** — and `src_imfseries` is empty for 2,338 of them.
So 2,788 is a lower bound because the alias table did not place a country
prefix on rows that are, with two exceptions, established non-staff-report
publication types; it is not a lower bound because the excluded rows might be
Article IV staff reports. The share depends on which denominator is meant,
and the wide one flatters us: 31.4% of all 7,451 hits, but **42.2% of the 5,542
rows that actually reached the alias lookup**, because the classifier returns on
its first failure. The narrower figure is the one the sentence is about.
Whether extending the alias table would raise the eligible frame, and by how
much, is not settled here and is flagged `needs_human_review` in the tool's
output. The disposition counts are ordered-first-failure labels throughout, so
they partition the hits rather than tally independent reasons — and one of them
partitions nothing: `excluded_language` reads 0, but the Fund's listing CSV has
no language column at all and every row is defaulted to English, so that test
can never fire. A zero there is not evidence that every listed document is in
English, and the tool now says so in the same breath as the count.

**And whether the failures are era-selective, which is the question that
matters.** A frame losing documents mostly from the pre-period would bias a
pre/post contrast, so the unmapped rows are tallied by year as well as by type.
The share swings enormously: **82.3% of
1999's listing hits are unmapped against
2.3% of 2024's**, and the aggregate
runs 55.1% for 1999–2016 against
1.9% for 2017–2025. Taken alone that looks alarming.

It is not era-selective failure on staff reports. It is the lifecycle of two
publication types. **Public Information Notices appear in 1999 and stop in
2013**; press releases in this listing run to 2016 and stop. Together they are
**97.9% of every unmapped row
before 2017**. From 2017 the unmapped count is a handful a year — a mission
concluding statement here, a standard page there — and 2022 has none at all. If
the alias table were failing on Article IV staff reports, the residue would be
staff reports. It is not one.

The per-year table, with each year's type breakdown, is the
`unmapped_country_by_year` block of the tool's output.

Reproduce with `python tools/imf_frame_publication.py`; the type tally is the
`unmapped_country_types` block of its output.

### S10.8 The Tier-2 word list, term by term

A reviewer asked for item-level provenance of the 35 Tier-2 terms: source,
location in that source, match rule, early and late counts, document counts and
a leave-one-out effect. Most of that is now published. **The source columns are
not, and the honest reason is that they do not exist.**

**Tier-2 has no per-term provenance in this repository and none is invented
here.** The entire record is one end-of-line comment, `config/config.yaml:76`:
"bureaucratese shared by Bankspeak and LLM style; provenance: Pamphlet 9
vocabulary + WB usage". That names two sources collectively for all 35 terms,
with no location in either, and no file anywhere maps a term to a source. Nothing
verifies that any of the 35 appears in Moretti and Pestre at all — the equivalent
check *was* run for Tier-1 against Kobak et al., which is how we know three of
those thirteen are not in the published list. The `source` and
`source_location` columns of `data/analysis/tier2_item_provenance.csv` therefore
read "not recorded in repository" for every term. Tier-1's attributions do not
transfer: `config/config.yaml:69` attributes Tier-1 to the excess-word
literature, and no comparable claim is made for Tier-2 by the repository or by
us. `docs/DESIGN_RATIONALE.md` said these lists carry "a source tag per word";
they never did, for either tier, and that entry is corrected.

**Two match rules were in use and nobody had noticed.** The production pipeline
tokenises with `[A-Za-z']+` on lowercased text and counts exact set membership,
with that token count as the denominator (`src/textstats.py:14-23`). S10.6's
period-fairness study used case-insensitive `\b`-anchored regex on raw text with
a whitespace-split denominator (`tools/tier2_period_fairness.py:70,75`). The
frozen spec at `config/families.yaml:5-9` fixes exact-token membership and says
in as many words that `\b` matching is not used — but that block is declared for
the Tier-1 outcome, so Tier-2's rule is genuinely unspecified.

**The two rules disagree by four hits in 14,986, across two terms** —
`stakeholders` and `sustainable`. The matching is not where they differ. Where
they differ is the **denominator**: `txt.split()` inflates the early window's
token count by 27.4% and the late window's by only 9.7%, because early Bank text
is far more tabular and numeric, and a whitespace split counts figures and rule
characters that the `[A-Za-z']+` tokeniser does not. Decomposed, **99.6% of the
16.2% gap between the two rules' headline ratios is the denominator definition
and 0.4% is the matching.** So the boundary rule's 28.4× exceeds the production
rule's 24.4× for a reason that is a fact about tabular layout in 1950s annual
reports, not about the Bank's prose. Both are reported below; which rule is
normative for Tier-2 is a human call the repository never made, and this
supplement does not make it either.

| subset | terms | rule | 1946–65 | 2020–24 | ratio |
|---|---:|---|---:|---:|---:|
| all Tier-2 | 35 | production | 0.260 | 6.353 | **24.4×** |
| all Tier-2 | 35 | boundary (S10.6) | 0.204 | 5.797 | 28.4× |
| period-plausible | 12 | production | 0.244 | 2.285 | **9.4×** |
| period-plausible | 12 | boundary (S10.6) | 0.192 | 2.083 | 10.9× |
| modern-register | 23 | production | 0.016 | 4.069 | 254× |
| modern-register | 23 | boundary (S10.6) | 0.013 | 3.714 | 295× |

**The abstract's two headline figures used to be computed under different
conventions from each other, and the axis was not the one it looked like.**
"Thirtyfold" is the *equal-year mean* of the production rule
(0.252 → 7.631,
30.2×); the subset figure it was paired with was
*token-weighted*. The two differ on **aggregation**, not on the match rule, and
the temporal-anchoring figures in the same abstract sentence are equal-year
too — so the coherent repair keeps equal-year throughout rather than moving
everything to the pooled convention. **The abstract now reports
30.2× and 10.8×, both equal-year,
both the production rule.** Matched pooled conventions would instead give
24.4× and 9.4×, or 28.4× and
10.9× on the boundary rule; this tool publishes all four cells on
both aggregations and chooses between none of them. An external review found
the mismatch and read it as a match-rule problem, which is why the two axes are
now named separately. The tool's production-rule aggregate reproduces
`data/features/ar_fy_features.csv` to four decimal places, which is the
cross-check that the two paths are computing the same quantity.

**22 of the 35 terms do not occur at all in 1946–65** — the same 22 under both
rules. The early window is 19 fiscal-year units, not 20: the assembled corpus
has no fiscal-1946 file, and none for 2000 or 2010 either. The late window is 5.
Both denominators are in the output rather than left implicit.

**The unit counts in that table are fiscal-year units, not documents.** An assembled unit concatenates several volumes — 134 documents sit behind these
76 units; the assembly log has 135 include rows and one of them carries no text
— so the columns are named
`n_fy_units_*`. A genuine per-term document count is one of the things below
that cannot be produced.

**The early window rests on very few occurrences, and that is what the
leave-one-out column is really measuring.** There are 130 Tier-2 hits in the whole early window against 3,301 in the late
one under the production rule, 3,303 under the boundary rule. `vital` alone carries 34 of
those 130 — 26.2% — and `vital`, `strengthen` and `strengthening` together carry
80, or 61.5%. So removing `vital` takes the all-35 ratio *up*, from 24.4× to
32.8× (production) and 28.4× to 38.1× (boundary), because it shrinks the base
rather than the endpoint. The largest move the other way is `sustainable`, which
takes the boundary ratio down to 22.9×. One term, `harnesses`, has zero hits in
both windows and a leave-one-out delta of exactly zero; it appears in 2 of the
76 units corpus-wide.

**Three of the twelve period-plausible terms have no attested early
occurrences at all** — `fosters`, `robust` and `strengthens`. The
period-plausible flag is a judgement about whether a *sense* was available before
1965, not about whether the word is *attested*, so the 9.4× is not carried by
twelve terms evenly and the subset is not a clean historical control.

**What is still missing, and what it would cost.** Per-term document-level
prevalence across all four strata is not computable from any derived file: no
document-level artifact holds a per-term Tier-2 count, only an aggregate rate per
document. Producing one means re-reading 6,143 corpus files, one stratum of which
is IMF Article IV — so it needs a permission decision before it can be run at
all, and this tool is deliberately scoped to the 76 World Bank assembled
fiscal-year units, which are public under the Bank's Access to Information
Policy. No IMF text is read by it.

Reproduce with `python tools/tier2_item_provenance.py`; the per-term table is
`data/analysis/tier2_item_provenance.csv`.

### S10.9 What a fiscal-year unit is, year by year

An external review observed that the assembled series ends in single documents of
29–45 thousand tokens where fiscal 2020 and 2021 are three-document assemblies of
185–217 thousand, and asked whether part of the headline decline is publication
packaging rather than language. The inventory that answers it existed
(`data/features/ar_fy_features.csv`) but was never printed, so it is printed
here in full.

**Table S10.9 — every assembled fiscal-year unit: documents and tokens**
(76 units, 6,177,817 tokens; fiscal 1946, 2000 and
2010 have no unit.)

| yr | n | tokens | yr | n | tokens | yr | n | tokens | yr | n | tokens |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1947 | 1 | 17,023 | 1966 | 1 | 29,405 | 1985 | 1 | 105,441 | 2005 | 2 | 65,078 |
| 1948 | 1 | 22,513 | 1967 | 1 | 30,134 | 1986 | 1 | 92,982 | 2006 | 2 | 69,343 |
| 1949 | 1 | 22,402 | 1968 | 1 | 41,266 | 1987 | 1 | 98,407 | 2007 | 2 | 50,807 |
| 1950 | 1 | 27,925 | 1969 | 1 | 36,982 | 1988 | 1 | 94,189 | 2008 | 30 | 133,820 |
| 1951 | 1 | 27,925 | 1970 | 1 | 48,439 | 1989 | 1 | 112,087 | 2009 | 2 | 139,432 |
| 1952 | 1 | 24,213 | 1971 | 1 | 43,758 | 1990 | 1 | 116,339 | 2011 | 1 | 32,042 |
| 1953 | 1 | 28,073 | 1972 | 1 | 56,134 | 1991 | 1 | 120,872 | 2012 | 3 | 129,292 |
| 1954 | 1 | 30,801 | 1973 | 1 | 65,525 | 1992 | 1 | 128,787 | 2013 | 3 | 74,546 |
| 1955 | 2 | 34,609 | 1974 | 1 | 62,563 | 1993 | 1 | 123,047 | 2014 | 3 | 164,769 |
| 1956 | 1 | 25,725 | 1975 | 1 | 65,299 | 1994 | 1 | 121,457 | 2015 | 1 | 25,651 |
| 1957 | 1 | 25,701 | 1976 | 1 | 77,343 | 1995 | 1 | 104,270 | 2016 | 3 | 171,618 |
| 1958 | 1 | 29,567 | 1977 | 1 | 80,728 | 1996 | 1 | 106,643 | 2017 | 3 | 185,908 |
| 1959 | 1 | 24,910 | 1978 | 1 | 89,412 | 1997 | 1 | 99,387 | 2018 | 3 | 194,973 |
| 1960 | 1 | 20,821 | 1979 | 1 | 92,320 | 1998 | 1 | 112,457 | 2019 | 3 | 196,164 |
| 1961 | 1 | 19,314 | 1980 | 1 | 89,905 | 1999 | 1 | 143,694 | 2020 | 3 | 217,404 |
| 1962 | 1 | 20,381 | 1981 | 1 | 91,479 | 2001 | 4 | 252,812 | 2021 | 3 | 184,775 |
| 1963 | 1 | 21,720 | 1982 | 1 | 87,150 | 2002 | 2 | 73,917 | 2022 | 1 | 44,574 |
| 1964 | 1 | 31,280 | 1983 | 1 | 101,589 | 2003 | 2 | 131,713 | 2023 | 1 | 43,795 |
| 1965 | 1 | 44,740 | 1984 | 1 | 102,171 | 2004 | 2 | 95,052 | 2024 | 1 | 29,028 |

**The observation is correct and the inference does not follow.** Fifty-seven
units are a single document, eight are two, nine are three, one is four and one
is thirty. The endpoint years are exactly as described: 2020 and 2021 carry
three components each, 2022 through 2024 carry one. Fiscal 2008 carries thirty, which
is the largest departure in the table and sits in neither comparison window.

But the direction is the opposite of the worry. The like-for-like series — the
narrative volume alone, the one construction that compares the same kind of text
across eight decades — declines **more** than the as-assembled series, −58.8%
equal-year against −42.5%, and the two weightings almost coincide on it because
the narrative volume is one file per year across both comparison windows bar
fiscal 1955. If packaging were manufacturing the decline, removing the packaging
would shrink it; removing the packaging enlarges it. §6.1 states this and Table
3e gives the six cells. Packaging was concealing part of the decline rather than
producing it, and the table above is why that can be checked rather than
asserted.

Reproduce the inventory with `python tools/ar_component_inventory.py`; the table
is a direct read of `data/features/ar_fy_features.csv` columns `year`, `n_docs`
and `tokens`.
