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
way — the flat null has a *higher* ratio and less than half the error. Block-nine leverage runs the wrong way too: every inflated scenario sits at
0.334–0.371, below the well-behaved ones (0.297–0.477), where an equal split is
0.111; the rank correlation across the ladder is −0.73. The lowest-leverage
scenario of all is correctly sized, so this is a tendency and not a law. It runs the
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

S10.4 is retitled and rewritten; §6.2 rewritten. Across all twenty nulls the
rate runs 0.028 to 0.121; holding the preregistered dependence parameters and
varying only the mean structure it runs 0.037 to 0.094, and both brackets are
stated.

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
eligible units against 103–129 in the surrounding years, inclusion probability
0.909.
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
`tools/tier2_item_provenance.py` publishes what the repository can support, and
**three** of the nine fields it cannot. `source` and `source_location` read "not
recorded in repository" for all 35 terms, because the repository holds one
collective end-of-line comment at `config/config.yaml:76`. So does **`family`**:
there is no authoritative per-term family mapping, only a derived surface stem
the tool computes and labels as derived. And there is no true **`n_documents`**:
the published counts are fiscal-year-unit counts over 76 assembled units, not
document counts, which would need a per-document Tier-2 tally over 6,143 files
that no derived file holds. An earlier version of this response said only the
two source columns were missing. No term is attributed to Liang, Kobak or
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

**The early window rests on very few occurrences**: 130 hits against 3,301
(production rule) or 3,303 (boundary).
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

**MacKinnon & Webb (2017) is not missing.** It is cited as a boundary marker
rather than a quantitative account, which is exactly the status the reviewer
asked for. One clause is now narrowed: their small-treated-cluster result
predicts under-rejection, and which way our measurement runs depends on the
null — 0.0365 under the preregistered process, 0.086 under fitted means.

*Correction (round 20).* The sentence above previously said the citation "has
been cited since round 15". Git does not support that: `git log -S MacKinnon`
returns three commits, and the paper first carries the name at 9efaba9
(2026-09-01), the round-17 response to the v5 review. It was **declined** at
rounds 15 and 16 — commit 7b13387 is titled "Three of the reviewer's seven
citations do not belong" — and added at round 17. A false provenance claim in a
document whose first line promises that nothing in it is estimated is worse than
the omission it was defending against, so it is corrected here rather than
quietly deleted.

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

## 6b. What a second adversarial pass found, after all of the above

The round was verified again once the repairs were in. It found nineteen more
defects, four of them in the artifact that actually gets uploaded, and none of
them reported by the external reviewer.

**The submission PDF was losing characters off the right edge of the page.** The
title page printed **62 of the deposit's 64 sha256 hex digits**, so a reader
verifying the deposit against the printed hash would have got a mismatch. Four
more lines were clipped the same way, including the last sentence of S10.8 and a
reproduction command in S10.5. XeLaTeX reports an overfull box in its log and
draws the text anyway; nothing was reading either.

**Every semicolon in both PDFs was U+037E GREEK QUESTION MARK.** macOS Times New
Roman draws an ordinary semicolon and records it in ToUnicode as U+037E, which is
canonically equivalent to U+003B and therefore survives a notdef scan and any
reader that normalises. Eighty-five in the manuscript, thirty-two in the
supplement. The font probe now reads its sample back character by character and
rejects a font that changes one, and the probe's sample is **derived from the
manuscript's own non-ASCII inventory** rather than hand-written — which is what
would have caught this and the missing arrow glyph in the same pass. The
manuscript is now set in Charter; Times New Roman fails the probe.

**§7 asserted the two causal claims §6.2 had just withdrawn.** It still said
dispersion was not the problem and that the fault was serial dependence plus the
nine-block construction, quoting a 0.121 that is the family error at ρ = 0.7
rather than size at the preregistered ρ = 0.5. Rewritten.

**S10.3's sixteen-row coverage table was never regenerated** after the reseeded
rerun: fifteen of sixteen cells disagreed with the file, and the summary
paragraph four lines below it — which was updated — contradicted its own table.
Regenerated from the JSON.

**The 0.037–0.094 bracket was contradicted by two rows of its own table.**
Independent World Bank shocks give 0.119 and the corrected NB2 dispersion 0.102.
The paper now states both ranges: 0.028–0.121 across every null examined, and
0.037–0.094 across mean structures at the preregistered dependence parameters.

**A fourth seed collision.** A class-level test written for the three the
reviewer found located a fourth, in `dispersion_calibration.py`.

**Five guards failed their own negative controls.** A dangling reference inside
the *supplement* passed, because three of four counters read only the paper. The
placeholder scanner's keyword whitelist missed `[FIXME]`, `[TK]` and `[PENDING
FINAL RUN]`. Two guards reported a *cleaner* verdict when the artifact they check
was missing than when it was present — absence read as success. "Resolved from
Crossref" was checked against entries carrying a DOI field, so a 404 counted as
resolved. And `tools/audit_citations.py --offline` had no offline mode at all:
the flag was accepted by the shell, ignored by the program, and thirty-one live
requests went to Crossref during what was meant to be a read-only audit. All five
are fixed and all five now have the control that broke them as a test.

**Four packaging defects.** The four figure pages embedded a **Type 3 font**,
matplotlib's default and a rejection in several journal production pipelines.
`data/analysis/panels_country/P*_battery.json`, from which S5 quotes twelve
numbers, were still unreachable — negating a file inside an excluded directory
does nothing, because git does not descend into one. The public export was
dropping two tools the supplement tells readers to run. And the review kit had
drifted from the repository in four files with nothing able to see it, since the
kit is gitignored; the builder now records a sha256 per staged file and
`tools/check_kit_freshness.py` compares them.

Suite 432.

## 6c. Round 19 — an independent audit found the central repair itself was wrong

A third party audited round 18's own repairs and returned RETURN BEFORE REVIEW.
Its central finding is correct and it is the second time the same section has
had to be rebuilt.

**F1 (confirmed, blocker). The ladder's opening rungs were not a decomposition.**
`holm2()` ran unconditionally, so rows labelled "no Holm" reported a Holm rate
anyway; `c4=True` added a field rather than switching the decision rule; and the
three rungs used three different seeds, so the 0.103 → 0.107 → 0.114 movement
mixed the stated change with Monte Carlo noise. The rungs are now **one
scenario** reading four decision rules off **one set of replicates**, on common
random numbers:

| decision rule, identical data | rate |
|---|---:|
| at least one panel below a raw 0.05 | 0.190 |
| the preregistered Holm step-down (C1) | **0.109** |
| Holm C1 with C4 | 0.083 |
| same data, inner *p* sampled not enumerated | 0.103 |

The auditor predicted the raw event would sit near 0.20 if it were really being
measured. It is 0.190.

**F2 (confirmed). The rate is not the governing rule's error rate.** C2 and C3
are not simulated, so every figure is the **Holm-adjusted C1 family rejection
rate — an upper bound** on the full C1–C4 rule's false-positive rate. Renamed in
the JSON, the supplement, §6.2 and the abstract; a test now fails if the old
name returns or if either manuscript calls it the governing rule's error rate.

**F3 (confirmed). "Holm's worst case over two hypotheses is independence" is
false** and is withdrawn. Under the global null the event is min(*p*₁,*p*₂) ≤
α/2: α − α²/4 under independence, α/2 under perfect positive dependence, and it
approaches α when the lower tails are disjoint. The shared-shock/independent-shock
comparison (0.086 against 0.119) is a property of the modelled dependence, not of Holm.

**F4 (confirmed). The calibrated tails were read backwards.** P1's exact *p* is
0.0156; the calibrated tails are 0.014 and 0.042. The text called both weaker
than face value and said neither approached 0.025. The first is marginally
*smaller* than 0.0156, and the second is **above** 0.025 — the opposite
direction. Both halves were wrong; both are corrected.

**F5 (confirmed, and it was my own repair that broke it).** I ran a
whitespace-normalising markdown editor over a Python file, which collapsed a
multi-line comment into prose and left `tools/tier2_item_provenance.py` raising
`SyntaxError` — while the supplement told readers to run it. 438 tests passed
with a broken script in the bundle because nothing parsed the scripts. Fixed,
and two tests now parse every `.py` in the repository and every `.py` in the
review kit.

**F6–F8 (confirmed).** The Tier-2 gap is three fields, not two: `family` is also
unrecorded and there is no true `n_documents` — the published counts are
fiscal-year-unit counts. The retitle left the checklist, the cover letter and
the public README behind, along with a stale supplement page count, abstract
word count, archive version and a "replication" label the manuscript
contradicts. The cover letter was 817 words against PLOS ONE's one page, and
argued with anticipated objections; it is now 495 and describes the work.
`tools/check_submission_metadata.py` derives title, page counts, abstract length
and test count from the manuscript and the artifacts and refuses when any
document disagrees — it reproduces every one of these findings on its own.

**F10 (confirmed, and the right fix is disclosure, not deletion).** The public
record carries AI provenance in the SAP, two deviation records, a ruling and 108
commit trailers. The manuscript now carries a **Use of AI assistance** paragraph
naming the tool, what it did — drafting the plan, writing the code, running the
analyses, drafting the manuscript, and deciding under standing instruction — and
how the outputs were verified. Nothing in the frozen record is altered. It ends
in an author attestation that only Ali can sign, and `placeholder_report.py`
now refuses while that bracket is unfilled.

**F9 and F11 remain open and are the author's.** The archived v1.2.0 predates
this work, so the version DOI the manuscript cites does not contain these
results; the metadata guard refuses while that is true. Cutting the release and
minting the new DOI is outward-facing and is Ali's to do.

Suite 438.

## 7. Package state

| item | state |
|---|---|
| manuscript | 34 pages, 34 references, 31 Crossref-resolved |
| supplement | 17 pages, S1–S10.8, built PDF |
| tests | **432 passing** |
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
