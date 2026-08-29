# Ruling — status of the sealed WB analysis under the P1/P2 confirmatory family

Date: 2026-08-20. Decided by: Claude (session of 2026-08-20) on Ali Çetinkaya's
instruction to decide rather than defer. **Reversible by Ali**; it changes a
disclosure obligation in the paper, not any frozen artifact or code.

Question (handover §8): the sealed Stage-A package contains a full analysis of
the WB strata, labelled descriptive. P1/P2 is now the confirmatory family. Is
the confirmatory analysis a re-run on the same corpus, and how does prior
inspection cap the interpretation?

## Finding: the preregistration already reckoned with this, explicitly

The question reads like a latent defect. It is not. PREREG §3 discloses prior
inspection of the WB outcomes **in the preregistration's own text** and
constrains the design accordingly:

- The mandatory concentration-guard family is fixed as **underscore**, on the
  stated ground that it is "already known to dominate on the WB side (43.48% of
  post-period hits)". The figure is in the frozen document. The guard was fixed
  *because* the WB side had been seen, not in ignorance of it.
- §3 closes the matching escape hatch: "switching to breadth/prevalence now
  would itself be an outcome-informed primary change is adopted: occurrence
  count stays primary."
- §3 states the general rule: "No guard family is ever selected from unseen
  post-period outcomes."

So the WB-side prior inspection is a **disclosed, priced-in** feature of the
design, not an undisclosed contamination. What preregistration buys here is not
ignorance of the WB half; it is that the outcome definition, the guard family
and the primary model were locked before the contrast could be computed.

## Ruling

**1. Yes, it is a re-run on the WB side — and no, on the estimand.**

The confirmatory estimand is H-DIFF: "a differential post-2022 change between
the institutions" (§2). Its two halves are not equally seen:

| Half of the contrast | Status |
| --- | --- |
| WB (ICR, PAD) counts and their pre/post change | **Inspected** at Stage-A |
| IMF Article IV counts | **Never seen** — no IMF text has ever existed in this project |
| The interaction itself | **Never computed, and could not have been** |

The confirmatory quantity has not been observed. That is a genuine and stateable
claim, and it is the one the paper may make.

**2. Interpretation cap, in three parts.**

- WB-side main effects, WB pre/post changes, and any WB-only descriptive
  statement are **not confirmatory** and are reported as previously inspected.
  This is already the sealed package's own label; it must survive into the paper
  rather than being quietly upgraded when the same numbers reappear inside a
  P1/P2 table.
- The H-DIFF interaction is confirmatory, and carries an **explicit disclosure**
  that one half of the contrast was inspected at Stage-A, citing the PREREG §3
  guard-family passage as the concrete instance. A reader must not have to
  discover this from the repository.
- The existing non-equivalent-comparator cap (institution and genre confounded;
  Article IV is a falsification comparator) stands unchanged and is independent
  of this ruling. The two caps compound; neither replaces the other.

**3. The re-run is not literally on the same corpus, and the difference is
measurable.**

PREREG §7.6 requires the frame to be re-captured at the Stage-B snapshot date.
A6/A7 have now done so and measured it (`docs/A7_FRAME_DRIFT_20260820.md`):

> **748 of 2,738 documents (27.3%)** in the Stage-B confirmatory WB sample are
> the same documents whose outcomes were inspected at Stage-A.

Roughly three quarters of the confirmatory corpus was never looked at, so this
part of the ruling binds far less tightly than it appeared to. The reason is not
frame drift — the WB universe moved by 2 documents in fourteen days — but the
sampler: the sealed draw is provably `s01`'s single global RNG (reproduced
exactly, 2,818/2,818), whereas the Stage-B draw follows the preregistered
per-cell sampler of Appendix B.7. Changing to the preregistered sampler swaps
72.6% of the sample on its own.

That figure must be reported next to the disclosure in part 2, not buried in an
appendix, and with its cause named — otherwise "the corpus changed" reads as
instability when it is in fact compliance.

**4. One ordering tension, disclosed rather than resolved.**

PREREG §11.3 describes Stage-B as "metadata only; text and outcomes sealed" and
puts text download and feature processing *after* the Stage-B SAP timestamp. The
sealed Stage-A package nevertheless contains `data/features/*` and
`data/analysis/*` for the WB strata — that processing happened before. §11.1's
definition of Stage-A does not forbid it, and §3 openly relies on its results,
so the two sections are in tension over ordering, not over substance. The
resolution adopted: state the ordering plainly in the paper's preregistration-
deviation section. Do not reinterpret §11.3 to make the tension disappear, and
do not treat the Stage-A WB outputs as if they had been produced after the SAP.

## Consequent obligation (not yet discharged)

This ruling covers analytic choices the PREREG **locked**. It does not by itself
establish that no *unlocked* choice was made after the WB outcomes were seen.
That requires an audit: enumerate the analytic degrees of freedom actually
exercised (model form, covariate set, exclusion rules, the QC gate constants,
the stopword list, the 28→13 mapping) and check each against whether it was
fixed before or after the Stage-A WB analysis. Anything fixed after must be
named in the same disclosure. **Queued, not done.**

## What this ruling does not do

It does not change any frozen artifact, hash, seed, or line of code; it does not
alter the Holm family, the branch decision, or any gate. It adds disclosure
obligations to the paper and one queued audit.
