# What the paper is, after today's measurements

> **Superseded in part, 2026-08-27.** The confirmatory analysis has since run;
> `docs/RESULTS_20260827_confirmatory.md` carries the outcome and it CONFIRMS
> this document's recommendation rather than revising it. Two changes of fact:
> the family verdict is now measured (`family_pass = false`, no passing panel)
> rather than anticipated, and the RQ1 spine is stronger than described here —
> the D4 gate reproduces on the rebuilt corpus and the series gained five years.
> One thing this document could not have known: P1's signal is carried entirely
> by the `underscore` family, and the guard PREREG fixed in advance is what
> exposed it.

Date: 2026-08-20. Written under the instruction to make the calls with a
publishable GIQ/IP&M paper as the criterion. It rests on three measurements
made today or verified from artifacts today, not on preference.

## Three findings that point the same way

**1. The RQ1 gate passed.** D4 makes the internal replication a gate: "Before
extending past 2012, the 1946–2012 Annual Report series must qualitatively
reproduce the pamphlet's published trajectories. A failed internal replication
is a stop-and-diagnose event, not a footnote." It reproduces — temporal
anchoring falls ~40→~24 per 1k, nominalizations, acronyms, "and" and management
vocabulary rise (`docs/THIRD_EYE_REVIEW_PROMPT.md`, Findings 1). **RQ1 has a
validated spine**, and it carries a headline: Tier-2 rate on the assembled AR
series rises from ~0.25 per 1k (1946–65) to ~9.1 (2023–26).

**2. The placebo control fails on the confirmatory strata — and the one clean
result sits where no confirmatory claim can be made.** Read from
`data/analysis/paper/T2_its.csv`, which carries a `series` column that
`its_results.csv` does not. Tier-1 level shift at a 2023 breakpoint:

| series | stratum | shift | p | **placebo_sig_frac** | n_post |
| --- | --- | --- | --- | --- | --- |
| doc_level | annual_report | −0.0248 | 0.0705 | **1.00** | — |
| doc_level | **icr (P1)** | +0.0556 | 0.0000 | **1.00** | — |
| doc_level | **pad (P2)** | +0.0266 | 0.0103 | 0.50 | — |
| ar_assembled | annual_report | +0.0986 | 0.0000 | 0.83 | — |
| **ar_assembled_levelonly** | annual_report | **+0.0699** | 0.0000 | **0.00** | **2** |

`placebo_sig_frac = 1.00` on **icr**, the P1 panel, means every placebo
breakpoint tried on pre-2022 data is also "significant". Its p = 0.0000 is
therefore not evidence of a 2023 break; it is evidence that the model finds
breaks. pad is 0.50 — half.

The level-only specification on the assembled AR series is the one clean result:
placebo_sig_frac **0.00** alongside a significant +0.0699/1k shift. It cannot
carry a confirmatory claim on two independent grounds: §2 makes Annual Reports
**descriptive only**, and `ar_fy_features.csv` runs 1947–**2024**, giving **2
post years** against the design's ≥3.

So the finding is sharper than "the breakpoint fails its placebo test". It is:
**the specification with a clean placebo record is the one the design forbids
from carrying the claim, and the strata licensed to carry it are the ones whose
placebo control fails.** That is a real result, and it is not a null.

**3. The confirmatory design could not have detected the effect anyway.**
`docs/MDE_P1P2_20260820.md`: MDE₈₀ is unreachable on the preregistered θ grid,
power ≈ 0.50 at θ = 1.2 (3.3× the base rate), and tripling the documents changes
nothing because the binding constraint is a year-level shock (σ_δ = 0.3205).

**These are the same fact seen twice.** Strong autocorrelated year-level
variation in rare-marker rates makes single-year breaks look significant
anywhere (finding 2) and makes a differential design underpowered everywhere
(finding 3). One is a false-positive symptom, the other a false-negative
symptom, of one property of the data.

## What that makes publishable, and what it does not

**Not publishable:** a paper whose headline is "IFI prose shows an LLM-associated
discontinuity after 2022". On the confirmatory panels the placebo control fails
(icr 1.00, pad 0.50) and the differential test is underpowered. A competent GIQ
reviewer reaches both in an afternoon, and the project's own `CLAUDE.md` rule 3
already forbids the attribution language such a headline would need.

**Publishable, and stronger than it sounds:**

1. **RQ1 as the spine.** A preregistered, replication-validated extension of
   Moretti & Pestre's series from 1946 to 2026 — the first rigorous treatment of
   a widely-cited but methodologically loose pamphlet. Tier-2 bureaucratese
   rising 0.25 → 9.1 per 1k over eighty years is a finding in its own right and
   needs no LLM to be interesting.
2. **RQ2 as a bounded result, reported with the machinery that would have found
   an effect.** "We preregistered a test for a post-2022 discontinuity,
   adversarially reviewed it over fourteen rounds, and report: on the panels
   licensed to carry the claim the level shift is indistinguishable from placebo
   breaks; the one specification with a clean placebo record lies in a stratum
   the design confines to description and has two post years against a required
   three; and the differential design reaches 80% power for no effect size in the
   preregistered grid." That is publishable because the *bound* is informative
   and because almost nobody in this literature reports one.
3. **Two methods contributions that came out of the failures.** (a) The assembly
   artifact: the unassembled document-level AR series shows the OPPOSITE temporal
   trend to the assembled one — a genre/sibling composition effect that would
   silently reverse a published conclusion. (b) Document count is not the lever:
   measured, tripling documents moves power 0.48 → 0.53, because the constraint
   is year-level. Both are directly useful to anyone doing diachronic
   institutional text analysis, which is GIQ's readership.

## The honest framing sentence

> We preregistered a differential test for LLM-associated lexical change in
> international financial institution prose, and we report that it cannot be
> answered with the design's own evidentiary standard — while the eighty-year
> series it was built on is now measured, replicated and extended.

That paper survives peer review. The other one does not.

## Consequences to carry into the SAP

- The SAP must state the power bound **before** the analysis runs. It now can.
- The placebo result must sit next to any breakpoint estimate, not in an
  appendix. `placebo_sig_frac` is already computed and in the sealed outputs.
- **Discrepancy resolved (2026-08-20).** An earlier version of this document
  read `its_results.csv`'s annual_report row as the assembled series and called
  the sign clash unresolved. It is the **doc-level** series: `T2_its.csv` carries
  a `series` column that `its_results.csv` lacks, and the review prose's +0.102
  is `ar_assembled`'s +0.0986. The sign flip between −0.0248 (doc_level) and
  +0.0986 (ar_assembled) is the assembly artifact of contribution 3(a), not an
  inconsistency. Every reported number must name its series, because three
  co-exist and two of them disagree in sign.

## What is not decided here

Whether this formally triggers the §11.5 fallback to the RQ1/measurement paper
is a preregistration reading and Ali's call. The engineering position: the
confirmatory family cannot deliver a confirmatory claim at the standard the
design set, and the RQ1 spine is validated and ready.
