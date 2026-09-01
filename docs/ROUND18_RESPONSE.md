# Round 18 — response to the v6 third-eye review

Editorial verdict was RETURN BEFORE REVIEW, referee verdict MAJOR REVISION with
a hard condition on S10.4, the IMF sampling frame and data access. This records
what was done, what the review got right, what it got wrong, and what is left
for the author.

Every number below is regenerated from `data/`. Nothing here is estimated.

---

## 1. The review's central charge is correct, and the repair changes the answer

**Charge.** S10.4 measured per-panel raw rejection at 0.05, in separate loops,
with a sampled inner *p*, and the manuscript reported it as the size of the
governing test.

**Confirmed, on all three counts, and one of them is worse than stated.** The
panels do not merely resemble each other: P1 is ICR × IMF and P2 is PAD × IMF,
and the comparator arm is the *same twenty-seven cells* — identical years,
counts and token totals, verified in
`tests/test_round18_checks.py::test_the_two_panels_really_do_share_their_comparator_arm`.
Half of every panel is shared and the separate loops threw that away.

**Repair.** `tools/joint_holm_calibration.py` draws both panels in one
replicate from one comparator draw, applies the preregistered Holm step-down
(α/2 then α) every replicate, and enumerates all 512 sign patterns instead of
sampling them. It also runs the rungs between, because the answer is not one
number.

| null | P1 raw .05 | P2 raw .05 | family error | MC SE |
|---|---:|---:|---:|---:|
| S10.4 as built | 0.113 | 0.095 | 0.103 | 0.005 |
| + exact 512-point inner *p* | 0.113 | 0.088 | 0.107 | 0.005 |
| + the preregistered Holm step-down | 0.115 | 0.100 | 0.114 | 0.005 |
| + drawn jointly, shared comparator and shock | 0.118 | 0.093 | **0.086** | 0.004 |
| no serial shock, same fitted means | 0.051 | 0.055 | 0.045 | 0.003 |
| flat means, each series at its pooled rate | 0.041 | 0.037 | 0.031 | 0.003 |
| PREREG §8 literally, as `src/mde_sim.py` runs it | 0.046 | 0.049 | **0.037** | 0.003 |

4,000 replicates per row. Twenty rows in
`data/analysis/joint_holm_calibration.json`.

**Three findings the reviewer did not anticipate.**

*Enumerating the inner p changes nothing.* 0.113 either way. The criticism is
formally right and empirically inert here.

*Applying Holm to jointly drawn panels lowers the family error*, 0.114 → 0.086.
A shared comparator makes the two *p*-values positively dependent, and for two
hypotheses Holm's worst case is independence. Repairing the construction made
the governing rule look better.

*The reviewer's two scenarios are both reproduced, and so is the repository's
own August figure.* Their literal-preregistration run gave 0.0335 ± 0.0040;
ours gives 0.0365 ± 0.0030; `docs/MDE_P1P2_20260820.md` recorded 0.039 at θ = 0
in August, from `src/mde_sim.py`, which had implemented the joint structure all
along. Three independent implementations, one number. **The preregistration's
own power machinery was joint and the post-hoc size study departed from it.**

**What the ladder shows instead.** The family error turns on the null's mean
structure by a factor of three, and nobody preregistered that choice. Component
scenarios isolate it: removing the fitted World Bank differential trend costs
more (0.086 → 0.049) than flattening the year profile (0.086 → 0.074), and
removing both lands on the flat null (0.028), which the independently
constructed `observed_rates_flat` reproduces at 0.031.

**Two mechanisms were tried and both are refuted by the tool's own
diagnostics**, which is why neither is asserted. Shock-to-noise runs the wrong
way — the flat null has a *higher* ratio and less than half the error. Block-nine
leverage runs the wrong way too: 0.33–0.37 in the inflated scenarios against
0.44–0.48 in the well-behaved ones, where an equal split is 0.111. It runs the
wrong way for a reason: when one block dominates the studentised denominator,
almost every sign pattern counts as a hit and the test goes conservative.

**What is claimed, and it is less than before.** Roughly two fifths of the excess
survives at ρ = 0 — an i.i.d. one-armed overdispersion, no serial dependence
anywhere, 0.063 against 0.045. So *"the size problem is serial dependence"* is
withdrawn, and so is *"the block construction is where it lives"*.

**Calibrated tail probability of P1's *p*.** Its exact 8/512 = 0.0156
corresponds to 0.014 under the preregistered null and 0.042 under the fitted
one. Under neither does it approach the 0.025 the Holm step demanded.

**C2 and C3 are not simulated and every family rate is an upper bound.** C4 is,
because it is computable from the same cells: adding it takes the joint rate
0.086 → 0.064 and the independent-panel rate 0.114 → 0.086.

S10.4 is retitled and rewritten; §6.2 rewritten; the abstract now reports the
0.037–0.094 range.

---

## 2. The IMF frame — every demand met from the repository

The reviewer asked for the full eligible annual frame, the reason for the cap,
the selection algorithm, seeds, inclusion probabilities and tie-breaking.
All of it existed and none of it was in the paper. `tools/imf_frame_publication.py`
publishes it (S10.7) and **recomputes rather than asserts**:

- 7,451 audited listing hits → 2,788 eligible units → 1,064 drawn.
- Cap 40 per year-genre cell, preregistered at `docs/PREREG_DRAFT_v0.5.md:548`.
- Equal-probability SRS without replacement inside each cell, per-cell seed
  `sha256("20260806|imf|article_iv|<year>")`, published per year.
- Inclusion probabilities **0.310 to 1.000**. The design weights years by cap,
  not by the Fund's output.
- 1999 is short at 24 because its universe was 24. The cap binds in the other 26.
- **The draw replays exactly**: zero in the replay and not in the frozen file,
  zero the other way, in all 27 years.

**Three limits the reviewer did not ask about and would have found.**

*Fiscal 2020 is a compositional outlier and it is inside the pre-period* — 44
eligible units against 99–129 in neighbouring years, inclusion probability 0.909.
The catch-up disturbance S10.5 looked for on the post side shows up here on the
pre side.

*The per-cell seed does not make the sample reproducible from a refreshed frame.*
Deleting one never-selected eligible row and redrawing leaves on average 18.4 of
that year's 40 in place if it sorts first, 29.6 mid-order, 35.8 last. An
independent redraw retains 16.4. **The frozen CSV, not the seed, is what makes
this draw recoverable.**

*2,788 is a lower bound.* 2,341 hits could not be placed to a country — 31.4% of
all listing hits, but **42.2% of the 5,542 rows that reached the alias lookup**,
and the narrower denominator is the one the sentence is about.

Region, income group and programme status are not columns of either CSV, so the
standardisations asked for cannot be run from the deposited artifacts. Stated,
not worked around.

---

## 3. Tier-2 provenance — what exists, and the honest gap

The reviewer wanted `term, family, source, source_location, match_rule,
early_count, late_count, n_documents, leave_one_out_effect`.
`tools/tier2_item_provenance.py` publishes all of it except the two source
columns, which read **"not recorded in repository"** for every one of the 35
terms, because that is what the repository holds: one collective end-of-line
comment at `config/config.yaml:76`. No term is attributed to Liang, Kobak or
Juzek & Ward — those attributions are Tier-1's and are not transferable, and a
test now fails if any of those names appears in the artifact.

**Two match rules were in use and nobody had noticed.** Production counts exact
token membership; S10.6 used `\b`-anchored regex with a whitespace-split
denominator. The frozen spec forbids `\b` — but only for Tier-1, so Tier-2's
rule is genuinely unspecified and this supplement does not decide it.

**The gap between them is 99.6% denominator and 0.4% matching.** The numerators
differ by 4 hits in 14,986. `txt.split()` inflates the early window's token count
by 27.4% and the late window's by 9.7%, because early Bank text is far more
tabular. So the boundary rule's 28.4× exceeds the production rule's 24.4× for a
reason about 1950s page layout, not about the Bank's prose.

**The abstract's two headline figures were computed under different conventions
from each other**: "thirtyfold" is the equal-year production rule, "11-fold" was
the token-weighted boundary rule. Matched, they are 24.4× and 9.4×, or 28.4× and
10.9×. The abstract now says 9- to 11-fold.

**The early window rests on very few occurrences**: 130 hits against 3,303.
`vital` alone carries 26.2% and the top three carry 61.5%, which is why removing
`vital` takes the ratio *up*, to 32.8×. Three of the twelve period-plausible
terms have no attested early occurrences at all.

---

## 4. RQ1 — the weighting axis the reviewer asked for, and what it costs us

Every figure this paper reported for the eight-decade contrast was the
equal-year mean and it never said so.

| corpus | equal-year | token-weighted |
|---|---:|---:|
| as assembled (frozen) | −42.5% | −27.8% |
| **narrative volume only** | −58.8% | **−58.0%** |
| full family | −35.4% | −24.3% |

**The claimed range widens from −35…−59% to −24…−59%.** But the like-for-like
series — one document a year throughout — is nearly invariant to weighting, while
the other two move by fifteen and eleven points. The weighting sensitivity is a
property of the packaging, and the series with no packaging heterogeneity has
almost none of it.

---

## 5. Where the review is answered rather than accepted

**Four of its twenty pinpoint edits target text that is not in the paper.**
"95% CI", "balance test", "IMF control series", "institutional corpus-selection
effect" and "the design bounds the answer" are all absent; "size-controlled" was
removed two rounds ago. Where the reviewer inferred a claim from a paraphrase,
the paper already said the narrower thing — §5 reports that the comparator
**fails** Linden's balance criterion, on the design's own published standard.

**MacKinnon & Webb (2017) is not missing.** It has been cited since round 15,
as a boundary marker rather than a quantitative account, which is exactly the
status the reviewer asked for. One clause is now narrowed: their small-treated-
cluster result predicts under-rejection, and which way our measurement runs
depends on the null — 0.037 under the preregistered process, 0.086 under fitted
means.

**Webb (2023) was mis-filed** in the reference list, under interrupted time
series rather than bootstrap inference where the body cites it. Moved.

---

## 6. Defects found in this round that no reviewer reported

**Four calibration tools derived their random streams by adding a label's
*length* to the frozen seed.** `len("P1") == len("P2")`, so both panels ran on
one stream; `len("poisson") == len("ar1_nb2")`, so two arms were coupled while
the pair the conclusion rested on was not — the opposite of what the docstring
claimed. An external reading found three instances; a class-level test written
here found the fourth, in `dispersion_calibration.py`. All now hash the labels
(`src/percell_seed.stream_seed`), all four studies were rerun, every figure in
S9, S10.1, S10.3 and S10.4 is from the rerun, and no verdict changed.

**The placeholder guard read two Markdown files while the brackets sat on page
one of the built PDF**, and printed "MANUSCRIPT: no placeholders". It now reads
the rendered PDF and exits 2 — correct as built, not submittable.

**The count guard did not read the checklist, the PDF or the kit manifest**, all
three of which had drifted (25 pages against 32; "23 of 25 references resolved"
against 31 of 34; 91 kit files against 92). It reads all three now, and it
immediately caught a duplicate kit entry the same day.

**The cross-reference guard scanned only the paper for supplement references**,
so a dangling `S6.3` inside the supplement passed for two rounds.

**`docs/DESIGN_RATIONALE.md` claimed the marker lists carry "a source tag per
word".** They never did, for either tier. Corrected. The manuscript also
attributed the Tier-1 blanket citation to `config/families.yaml`, which carries
no attribution at all.

**Four post-freeze result files were gitignored**, so every figure in S10 lived
only in the working tree. Now tracked.

**The submission PDF carried a table of contents**, which reads as a technical
report. Removed. **The supplement shipped as raw Markdown** through seventeen
rounds, which would have gone to PLOS untypeset and without the glyph check that
caught "2⁹ = 512" being typeset as "2 = 512". It now builds through the same
path.

---

## 7. Package state

| item | state |
|---|---|
| manuscript | 32 pages, 34 references, 31 Crossref-resolved |
| supplement | 16 pages, S1–S10.8, built PDF |
| tests | **420 passing** |
| PLOS compliance | **0 blockers**, 2 accept-stage items |
| stated counts | every one derived and checked |
| cross-references | all resolve |
| placeholders | exit 2 — affiliation and ORCID, by design |

## 8. What is left, and it is the author's

1. **Affiliation, ORCID, funding and competing-interest statements.** These are
   identity facts and are left as visible brackets on purpose; the guard now
   refuses to call the package submittable until they are filled.
2. **Upload the evidence deposit** and put the DOI in via
   `tools/record_evidence_doi.py`. Until then a referee cannot open it, which
   is the reviewer's real data-access objection and the one thing here that
   cannot be closed from the repository.
3. **Four decisions the tools deliberately did not make**, flagged
   `needs_human_review` in `data/analysis/imf_frame_publication.json`: whether
   1999 is a design boundary or a coverage limit; whether to extend the alias
   table before quoting 2,788 as the eligible universe; whether inclusion
   probabilities enter the estimator as weights; and whether to join region and
   income group given that the available vintage is anachronistic. A fifth, in
   the Tier-2 output: which match rule is normative.
