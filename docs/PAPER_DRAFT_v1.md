# Eighty Years of Bankspeak, and a Preregistered Test That Could Not Confirm an LLM Break

**SUPERSEDED by `PAPER_DRAFT_v2.md` (complete manuscript). Kept for the record.**

**Draft v1 — 2026-08-27.** Supersedes `PAPER_DRAFT_v0.md`, which was written while
the IMF comparator was still embargoed. §§1–5 of v0 (introduction, related work,
data, measures, design) stand except where noted; §§6–8 below replace v0's
entirely, because the confirmatory analysis has now run.

Statistical analysis plan frozen and externally timestamped **before** any
outcome reported here was computed: Zenodo `10.5281/zenodo.22098259`, sha256
`4aa122797f2db6ddd3e1dae5cb425958b231f02438f242bde174b25b20af2677`, published
2026-08-25T15:01:07Z. Stage-A preregistration: OSF `10.17605/OSF.IO/5C9J8`.

---

## Abstract

Moretti and Pestre's *Bankspeak* (2015) diagnosed a drift in World Bank prose
from concrete description toward abstract, nominalised management language, on a
corpus and method never published in reproducible form. We rebuild that series
from primary documents, extend it from 1947 to 2026, and use it to ask a second,
timely question: did the arrival of large language models leave a measurable
discontinuity in institutional writing after 2022?

The first answer is affirmative and strong. The pamphlet's trajectories
reproduce — temporal anchoring falls from 39.96 to 22.97 occurrences per
thousand tokens while nominalisation, acronym density and management vocabulary
rise — and the drift has not plateaued: a Tier-2 bureaucratese register runs
0.252 per thousand in 1946–65 against 7.631 in 2020–26, a thirtyfold rise.

The second answer is a bounded negative, and the bound was set in advance. A
preregistered differential test against an International Monetary Fund
comparator yields **no confirmatory claim** (family Holm verdict: no passing
panel). The apparent World Bank rise does not survive the guard analysis the
preregistration mandated before the data existed: with a single word family
removed, the differential coefficient falls to −0.067 with a confidence interval
spanning zero. It depends on one post-period year. The comparator institution
rose as well. And the design's own power analysis, computed before any outcome
was visible, shows that an effect of the observed size would have been detected
roughly one time in five.

We report the bound rather than the finding, and argue that the apparatus which
produced it — preregistered guards, a non-equivalent comparator, and a corpus
whose every defect class was ruled on record before the numbers were read — is
the transferable contribution.

---

## 6. Results

### 6.1 RQ1 — the replication gate, then the continuation

D4 makes internal replication a **gate**, not a robustness check: the 1946–2012
series must qualitatively reproduce the pamphlet's published trajectories before
any extension past 2012 is reported. It does.

**Table 2 — assembled Annual Report era means** (`ar_fy_features.csv`, 76 fiscal
years, QC-gated).

| Era | Nominal./100 | Temporal/1k | Mgmt/1k | Tier-1/1k | Tier-2/1k |
| --- | --- | --- | --- | --- | --- |
| 1946–1965 | 5.98 | **39.96** | 1.11 | 0.009 | 0.252 |
| 2020–2026 | 7.71 | **22.97** | 4.47 | 0.094 | **7.631** |

Temporal anchoring falls by 43%; nominalisation, management vocabulary and the
bureaucratese register rise. The pamphlet's qualitative claim survives
independent re-measurement from primary documents.

Two features of this replication are worth stating because they are unusual.
First, it was computed on a corpus that had *since* been re-extracted, OCR'd,
re-fetched and pruned by ruling — and none of those repairs was made with this
comparison in view, which makes the agreement harder to attribute to analyst
choice than the first pass. Second, the series is materially more complete than
when the repairs began: **76 fiscal years against 71, with missing years down
from seven to two.** Fiscal 2002 had been two un-OCR'd scans yielding twelve
tokens and failing assembly QC; it is now 73,917 tokens at a 0.234 function-word
share. Fiscal 2007 had been 46,723 tokens of mojibake produced by a broken font
encoding; it is now 50,807 tokens at 0.254.

**The composition lesson stands, and is the methodological core of §6.1.** On
*unassembled* document-level Annual Report files, temporal anchoring **rises**
over the same eras — the opposite of the assembled series and of the pamphlet.
The reversal is produced entirely by sibling volumes and financial annexes
entering the document pool. A diachronic claim about institutional language can
be inverted by a decision about what counts as one document, and that decision is
rarely reported.

### 6.2 RQ2 — the preregistered differential test

**Table 3 — governing verdict** (`s13_validation_battery family`, Holm over two
panels, α = 0.05).

| | P1 (ICR vs IMF) | P2 (PAD vs IMF) |
| --- | --- | --- |
| α_Holm | 0.025 | 0.05 |
| θ (WB:post, log points) | 0.586 | 0.332 |
| PASS-P *p* | **0.0142** | 0.0929 |
| C1 Holm | passes | fails |
| C2 stability | **fails** (NB2 arm passes; standardized arm not evaluated) | **fails** (same) |
| C3 concentration guard | **fails** | fails |
| C4 leave-one-post-year-out | **fails** | fails |
| **panel** | **no claim** | **no claim** |

`family_pass = false`; no passing panel; no headline. Under PREREG §5, failure
of any condition means the panel is reported descriptively with the failed
condition named.

**C3 is the substantive one.** The preregistration fixed `underscore` as the
mandatory concentration guard *before the data existed*, on the openly stated
ground that it already dominated the World Bank side at 43.48% of post-period
hits. Refitting without it, the differential coefficient is **β = −0.067, CI
[−0.509, 0.398]** — the estimand does not merely shrink, it crosses zero with a
wide interval. The guard was set for this contingency and it caught it.

This must be stated precisely, because a cruder statistic points the other way.
Removing `underscore`, the raw pre/post rate ratios still favour the World Bank:

| | all Tier-1 | excluding `underscore` |
| --- | --- | --- |
| P1: WB | ×3.26 | ×2.68 |
| P1: IMF | ×1.16 | ×1.55 |
| **P1: ratio of ratios** | **2.83** | **1.74** |
| P2: ratio of ratios | 2.52 | 1.50 |

The Bank's rate still rises faster than the Fund's. What collapses is the
*modelled differential* — the preregistered estimand, which carries year effects
and the differential shock structure the design specified — because the Fund's
own rise is proportionally larger once `underscore` is removed (×1.55 against
×1.16). A raw ratio and a fitted interaction are different quantities, and only
the second was preregistered.

**C2 is a failure of ours, not of the data, and is reported as one.** The
condition has two arms. The NB2 arm passes in both panels (P1 β = 0.542 against
0.586, CI [0.210, 0.900]). The composition-standardized arm returned
`no_common_support_groups` with `pi_groups = 0` and zero post-period token
support in both institutions — which, read literally, asserts that the Bank and
the Fund share no common support. They do. PREREG §6 fixes the standardization
stratum as country (ISO3) mapped to region × income; the panel builder was
instead given `<stratum>:<year>`, a key that is institution-specific by
construction, so no group could be supported on both sides and the estimator
correctly reported that none was. The premise recorded in the code — that the
World Bank documents carried no country field — was false: the Documents &
Reports `count` field holds the primary country, is present on 2,406 of 2,407
sampled ICR/PAD documents, and had been in the write-once API capture since the
Stage-B harvest, never carried forward into the frame.

We report this rather than repair it into the confirmatory result. The frozen
artifacts are unchanged and the defective run remains reproducible. A repaired
grouping — the §6 ontology rebuilt offline, 91.0% of kept documents landing in a
supported region × income group — is reported as a **post-hoc sensitivity** in
§6.5 and is not condition 2, because one element of §6 still cannot be met: the
income classification here is current rather than year-matched, the year-matched
series not having been assembled at Stage-B. Substituting a different covariate
after seeing results is the degree of freedom this design exists to refuse.
Condition 2 therefore continues to fail exactly as recorded; what the repair
changes is only what we are entitled to say about why. It cannot affect the
verdict in any case: C3 fails on merits in both panels and C1 fails in P2, and a
panel requires all four.

**C4** deletes each post year in turn: 2023 → *p* = 0.0103, **2024 → *p* =
0.1815 with β falling from 0.586 to 0.207**, 2025 → *p* = 0.0142. The result
rests on a single year.

**H-SHARED, the §2 descriptive companion: the comparator moved too.** The IMF's
own pre/post change is +0.145 log points, CI [0.003, 0.356] — modest, but its
interval excludes zero. And the Fund's pre-period rate is nearly three times the
Bank's (0.1153 against 0.0416 per thousand). The two institutions were never on
one level, which is what §2 means in calling this a *non-equivalent* comparator
with institution and genre confounded, and why interpretation was capped in
advance rather than after the fact.

### 6.3 Power, reported with the estimate rather than after it

The minimum detectable effect was computed **before any outcome existed**, at
full precision (1,000 replicates, B = 9,999 nested PASS-P, all three companion
settings the preregistration specifies).

| θ | companion = zero | half | full |
| --- | --- | --- | --- |
| 0.00 | 0.039 | 0.039 | 0.039 |
| **0.60** | **0.159** | **0.158** | **0.216** |
| 1.20 | 0.483 | 0.485 | 0.569 |

**MDE₈₀ is unreachable on the preregistered grid under every setting.** θ = 0.60
is the threshold the design chose for its own branch-selection gate, and it is
almost exactly P1's point estimate of 0.586. At that value, family power is
0.159–0.216 where 0.80 was required.

Two consequences follow, and both are reported rather than chosen. A null here
would be **uninformative**, not evidence of absence. And P1's rejection at
*p* = 0.0142, arriving from a design with roughly 16% power at the observed
effect size, carries severe winner's-curse inflation: the point estimate is a
poor guide to magnitude even if the effect is real.

The binding constraint is structural, not budgetary. Power is governed by a
year-level differential shock (σ_δ = 0.3205 from the preregistration's own
method-of-moments hook); **tripling every panel's documents moves power at
θ = 1.2 from 0.48 to 0.53.** More sampling is not the remedy. The remedy is post
period years, of which the design has three.

### 6.4 Breakpoint specificity

`placebo_sig_frac` on the Tier-1 breakpoint, by stratum: annual_report **1.00**,
ICR **1.00**, IMF Article IV 0.67, PAD 0.33. On P1's own stratum, *every* placebo
breakpoint tried on pre-2022 data is also significant — a test that fires at any
date does not identify 2023. The panel-level placebo at 2016 is cleaner
(P1 *p* = 0.1674, P2 *p* = 0.4782). The two disagree, and both are reported.

---

## 7. Limitations

1. **Power.** The design cannot reach 80% power for any effect in its
   preregistered grid. This is stated first because it conditions everything
   above.
2. **Breakpoint specificity.** Placebo fractions of 1.00 on two strata limit any
   2023-specific reading.
3. **Non-equivalent comparator.** Institution and genre are confounded; the Fund's
   base rate is ~3× the Bank's and the Fund also rose. A positive differential
   would license far less than it appears to.
4. **Mechanism.** Lexical tiers cannot separate direct LLM assistance from human
   adoption of LLM-popularised vocabulary. We measure population-level change,
   not authorship, and no output in this project claims a document "is
   AI-generated".
5. **Extraction, and a collinearity we could bound but not remove.** 192 IMF
   documents had no text layer and are OCR'd; every one is pre-period, so
   extraction method is collinear with the estimand and cannot be controlled
   against era. We estimated the method effect where era is held fixed instead:
   OCR recovers 1.012× the native token count with mean token length within
   0.6%. The confound is real in structure and small in size.
6. **Exclusions are pre-period-weighted.** Eighteen ICR documents leave P1 by
   language ruling, all pre-2023. Removing pre-period documents from one arm is
   not neutral to a pre/post contrast; per-year counts are in the
   intention-to-sample ledger.
7. **The standardized stability arm was not evaluated, and the reason is our
   error.** It was supplied `<stratum>:<year>`, which cannot have
   cross-institution support, rather than the country → region × income
   stratifier PREREG §6 fixes; the World Bank country field existed all along in
   the archived API capture. The frozen artifacts keep the defect and the
   repaired grouping is reported separately as a post-hoc sensitivity, because
   the §6 income variable is year-matched and ours is current. We flag the
   general hazard as much as the instance: an estimator that declines an
   infeasible computation still emits a *reason*, and a reason phrased as a
   property of the data ("no common support") will be read as a finding unless
   someone checks what was actually handed to it.
8. **Prior inspection.** 748 of 2,738 documents (27.3%) in the Stage-B World Bank
   sample are documents whose outcomes were inspected at Stage-A. The IMF half of
   the contrast had never been computed before this analysis, so the interaction
   itself was unseen — but the disclosure belongs next to the estimate.
9. **Within-stratum composition** (region, sector, instrument, template era)
   remains untreated — a lesson of §6.1 that this paper has not yet applied to
   itself.

---

## 8. Discussion

### What a bounded negative is worth

The literature on LLM-associated vocabulary has grown quickly and reports
positives almost exclusively. Our design was built to be able to fail, and it
did: a guard fixed before the data existed removed a single word family and the
preregistered estimand crossed zero; a leave-one-out check showed the result
resting on one year; a comparator chosen to absorb sector-wide drift moved in the
same direction as the treated arm.

None of those checks would have been reached had the analysis stopped at
*p* = 0.0142. All three were specified in advance, which is the only condition
under which their verdicts mean anything.

### The measurement lessons transfer further than the finding

Three results here are about method rather than about the World Bank, and each
was found by measurement rather than suspicion:

- **Unit definition can invert a diachronic conclusion.** Assembled versus
  document-level Annual Report series give opposite signs on temporal anchoring.
- **The source's own plain text is not safer than your extraction.** D9 preferred
  server-side text precisely to avoid extraction noise; 70 documents arrived with
  word spacing destroyed, concentrated in 2003–2009 and absent after 2010, and
  the PDF path we had distrusted was clean (0 of 437 against 70 of 2,688). In the
  worst case whole-word matching missed 78% of its hits.
- **A recorded ruling is not an applied one.** Twice, an exclusion or an
  extraction remedy was written to a ledger, satisfied its gate, and never
  reached the corpus. Both were caught because a downstream count disagreed with
  an upstream one, not because anything raised an error.

### What we do not claim

We do not claim the World Bank's prose was unaffected by LLMs. We claim that this
design, with this corpus and this comparator, cannot answer that question at the
evidentiary standard it set for itself, and that the honest report of such a
design is its bound. The eighty-year series stands on its own.

---

## 9. Data and code availability

Preregistration OSF `10.17605/OSF.IO/5C9J8`; SAP Zenodo
`10.5281/zenodo.22098259`. Analysis code, frames, frozen samples, power curves,
quality flags and per-document exclusion ledgers are deposited. The IMF Article
IV corpus was retrieved under written permission from the International Monetary
Fund (2026-08-20) and is **not** redistributed; its SHA-256 manifest is
deposited so any holder of the originals can verify byte-for-byte. World Bank
content is public disclosure under the Access to Information Policy.

**Acknowledgement.** Contains IMF Staff Country Reports retrieved from
www.imf.org under written permission from the International Monetary Fund
(2026-08-20), accessed 2026-08-20. The IMF is not responsible for any analysis or
conclusions drawn from these documents.

---

## Author note on remaining work

`[TO-WRITE]` §2 related work; §§1, 3–5 to be lifted from v0 with the Stage-B
corpus figures substituted. NLL/perplexity results are deliberately absent
pending the PREREG §7.4 regeneration (decision D-4): no NLL number appears in any
output until that has run.
