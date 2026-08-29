# Framing option B — RQ1 leads, the audit design becomes the warrant

**Status: an option, not a change.** `PAPER_DRAFT_v2.md` is untouched. This file
exists so the choice is between two things you can read side by side rather than
between a draft and a description of a draft.

## Why this exists

Two independent venue passes reached the same conclusion without prompting:
**leading with the audit design is wrong at every venue on the shortlist.**
Preregistration, frozen engines and defect ledgers are *warrants* — they license
a claim, they are not the claim. No editor commissions a paper about how
carefully someone measured. At *Digital Scholarship in the Humanities* it is
worse than a weak choice: the journal's out-of-scope rule explicitly excludes
methodology descriptions, so an apparatus-first opening is a desk-reject trigger.

`docs/VENUE_RESEARCH_20260828.md` records the reasoning and its uncertainty.

## What changes, and what does not

Nothing in §§3–9 moves. No number, table, figure or verdict changes. What changes
is **§1, the abstract, and one paragraph of §8** — the order in which the paper
tells you what it did.

- **Option A (current):** audit design → RQ1 as a validation gate on it → RQ2 as
  an application of it.
- **Option B (below):** RQ1 and the unit-definition result → RQ2 as a designed,
  disclosed null → audit design named where it does its work, which is in
  licensing the null as reportable.

The strongest argument for A is honest: the apparatus really is the most
transferable thing here, and B risks burying it. The strongest argument for B is
that A asks an editor to care about method before showing them a result, and
editors do not read in that order.

---

## Abstract — option B

> Moretti and Pestre's *Bankspeak* (2015) diagnosed a drift in World Bank prose
> from concrete description toward abstract, nominalised management language, on
> a corpus and method never published in reproducible form. We rebuild that
> series from primary documents and extend it to 2025.
>
> The trajectories reproduce. Temporal anchoring falls from 39.96 to 22.97
> occurrences per thousand tokens across the assembled Annual Report series while
> nominalisation, acronym density and management vocabulary rise, and the drift
> has not plateaued: a bureaucratese register runs 0.252 per thousand in 1946–65
> against 7.631 in 2020–26, a thirtyfold rise.
>
> Rebuilding it also produces a result about measurement rather than about the
> World Bank. **The same archive yields a 43% decline or a 14% decline in
> temporal anchoring depending on nothing but whether Annual Report volumes are
> assembled into fiscal-year units** — a threefold difference in the headline
> quantity, produced by a corpus-construction decision that diachronic studies
> rarely report. Two further measurement findings follow the same pattern: the
> publisher's own plain text was *less* reliable than our extraction, and twice a
> recorded remedy passed its audit gate without ever reaching the corpus.
>
> We then use the rebuilt corpus for a preregistered test of a timely claim: did
> large language models leave a measurable discontinuity in institutional writing
> after 2022? A differential design against an International Monetary Fund
> comparator, with the analysis plan sealed and externally timestamped before any
> outcome existed, returns **no confirmed effect**. One panel reaches *p* =
> 0.0142 and then fails the concentration guard fixed in advance — removing a
> single word family sends the coefficient to −0.067 with an interval spanning
> zero — fails leave-one-post-year-out, and shows a pre-period event-study bin
> larger than the estimate itself. The comparator institution also rose. The
> design's own power analysis, computed before any outcome was visible, would
> have detected an effect of the observed size roughly one time in five.
>
> We report the bound rather than the finding. The transferable result is not the
> null but the guard that produced it: **a lexicon-based indicator of LLM
> influence that rests on one word family is not robust**, and a design without a
> preregistered concentration check would have reported *p* = 0.0142 as a
> discovery.

## §1 Introduction — option B, replacement for the contributions block

Keep the first two paragraphs of the current §1 unchanged. Replace the block
beginning "**This paper makes three contributions, and the order matters.**"
with:

> **What this paper establishes, in the order it establishes it.**
>
> First, that the *Bankspeak* trajectory is real and continues. Rebuilt from
> primary documents and extended to 2025, the pamphlet's qualitative claim
> survives independent re-measurement, and the register that grows fastest over
> eighty years is not the one the pamphlet named.
>
> Second, that the size of that finding is hostage to a decision almost nobody
> reports. Measured over the same fiscal years, the same archive gives a 43%
> decline in temporal anchoring or a 14% decline depending only on whether Annual
> Report volumes are assembled into fiscal-year units. We state this early
> because it generalises past this corpus: a diachronic magnitude can be tripled
> or thirded by a unit definition, and the unit definition is usually a sentence
> in a data section, if it appears at all.
>
> Third, that a preregistered test of the post-2022 LLM hypothesis on this corpus
> **cannot support the claim** — and that saying so is worth more than the
> alternative. One panel reaches *p* = 0.0142 and fails three preregistered
> checks. The concentration guard, fixed before the data existed, is the
> informative one: with a single word family removed the differential coefficient
> is −0.067 with an interval spanning zero. A study without that guard would have
> published the *p*-value.
>
> The apparatus that makes the third claim reportable — a two-stage sealed
> preregistration, a frozen inference engine, ruled defect ledgers, and a deposit
> that hash-lists what it may not redistribute — is described in §§3 and 5. We do
> not present it as a finding. We present it as the reason an unconfirmed result
> could be written down at all, rather than quietly becoming a different paper.

Then keep the "Two commitments run through the paper" paragraph unchanged.

## §8 Discussion — the one paragraph that must move

The current §8 opens with "What a bounded negative is worth". Under option B that
stays, but the measurement-lessons subsection is **promoted above it**, because
under B those lessons are results rather than by-products.

## What option B costs

- The audit design stops being the headline. If the intended readership is
  metascience or research methods, that is a real loss and option A is better.
- §1 becomes less unusual. A currently reads as a paper with a thesis about how
  to do this kind of work; B reads as a more conventional empirical paper. Some
  of the project's distinctiveness lives in that unusualness.
- The word "audit" leaves the abstract, and with it the signal to a reader who
  would have been drawn by it.

## What it buys

- It survives a desk screen at four of the five shortlisted venues instead of
  one, and it does not trip DSH's methodology-description exclusion.
- It leads with a result a reader can disagree with, which is what makes a paper
  citable.
- It puts the transferable lesson — single-family lexicon indicators are not
  robust — in the abstract, where the venue research says it belongs.

## Decision

Ali's. The third-eye brief asks an independent reviewer to adjudicate A against B
and commit to an answer; that answer should arrive before this is acted on.
