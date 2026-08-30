# Third-eye brief v4 — final pre-submission review for PLOS ONE

Supersedes `THIRD_EYE_PROMPT_v3_20260829.md`, which predates round 15.

**How to use.** Paste everything below the horizontal rule into a capable LLM
**with web access**, and attach `third_eye_kit.zip` (69 files, nine numbered
folders; `MANIFEST.md` explains each).

**Before you send it.** The bundle contains no IMF document text and none may be
added. The corpus is used under written permission forbidding redistribution of
documents or extracted text; counts, hashes, column names and log lines are
permitted derived outputs. `tools/build_third_eye_kit.py` refuses to build if a
staged file lies under an IMF tree or carries a document-text signature — rebuild
with it rather than adding files by hand.

---

You are a **third-eye reviewer**, brought in immediately before submission to
PLOS ONE. You have no stake in this paper's success and no obligation to be
encouraging.

**Fifteen adversarial rounds have already run**, the last of them six independent
reviewers with refute-by-default verification. Surface defects are gone. Repeating
back what the paper already says about itself is worthless, and it says a great
deal — read §7 Limitations and §8 in full *first* so that you do not.

Your value is in three things a self-audit structurally cannot reach: what a real
editor does in ninety seconds, whether a referee would believe this, and whether
the works it cites say what it claims they say.

## The material

`third_eye_kit/`, nine folders:

| folder | contents |
|---|---|
| `01_manuscript` | the paper — 9,678 words of prose, 10,868 with tables inline, **12 tables and 4 figures** — its nine-section supplement, and the single PDF an editor actually receives |
| `02_frozen_design` | Stage-A preregistration, Stage-B analysis plan, freeze record (DOI + SHA-256) |
| `03_decisions` | decisions D-1..D-13, both deviation records, the researcher-degrees-of-freedom self-audit, the pre-outcome power analysis, the confirmatory run's report, and `ROUND15_RESPONSE.md` |
| `04_tables` | the seven numbered tables, generated from data |
| `05_figures` | the four figures, generated from data |
| `06_machine_output` | both panel batteries, family verdict, panel cells, ITS results, the annual series, the citation audit, the dispersion calibration, the block-origin enumeration, the route tally, the access probe, and a post-hoc trend exploration deliberately **not** in the manuscript |
| `07_code` | the frozen inference engine, the validation battery, the standardization estimator, the generators, the audit tools |
| `08_venue_research` | the venue decision, the ÜAK rules quoted from source, and the round-15 review verbatim — attached for you to **attack**, not adopt |
| `09_submission` | cover letter, data-availability statement, PLOS compliance checklist, the Vancouver reference list, the 1,064-document access index |

Everything numeric regenerates from `06` via `07`. **If a number in the paper
disagrees with the machine output, the paper is wrong.**

## The paper, and what changed last

Single-authored. An independent reconstruction of Moretti and Pestre's
*Bankspeak* (2015) from primary World Bank documents, 1947–2025, plus a
preregistered test of whether post-2022 LLM-associated vocabulary shows a World
Bank discontinuity against an IMF Article IV comparator. The design is a
**single-comparator comparative interrupted time series**, not
difference-in-differences; `07_code/bootstrap_engine.py` is the authority on that.

Three results: the trajectories reproduce; a corpus-selection effect worth a
factor of three; and **a preregistered null** — no panel satisfies the decision
rule.

Round 15 changed four things, and they are the least-reviewed text in the bundle
because they are the newest:

1. **Supplement S9 and §6.2** now report that the frozen dispersion estimator
   recovers a seventh to a twentieth of dispersion that is really there, and that
   **PASS-P's size at a nominal 0.05 reaches 0.095** at the dispersion the data
   are consistent with. The one *p* that reached significance is therefore about
   twice as easy to trip as its label.
2. **Table 5c** gives the exact *p* at all three block origins, after an earlier
   draft named a one-year shift as a two-year one and omitted the partition that
   takes P2 to 0.0352.
3. **§2 and §4** were repaired on five citation counts.
4. The retrieval tally, the deposit's contents and the code DOI all changed.

---

# Your three tasks

## 1. The PLOS ONE editor — ninety seconds, then a decision

PLOS ONE evaluates **scientific validity and methodological soundness**, not
perceived importance. Its seven criteria contain no test of novelty or impact, so
a null is not a disqualification. An unsupported conclusion, an unintelligible
presentation, or a data-availability statement that fails the third-party-data
policy all are.

- Does the abstract earn a read of the introduction? Does the title describe the
  paper that follows?
- **The disclosure question, which is this draft's real risk.** The paper now
  tells the reader that its test over-rejects, that its dispersion estimator is
  blind, that one of its four conditions carries little information, that its
  headline *p* moves twentyfold with an arbitrary partition offset, and that its
  power was 0.16–0.22. Every one of those is true and every one was volunteered.
  **At what point does candour stop reading as rigour and start reading as an
  author who does not believe his own paper?** Say plainly whether this draft has
  crossed that line, and if it has, name the passages to cut or move.
- **Would you send this out, desk-reject it, or return it on data availability?**
  Answer as a decision, not a discussion.
- `09_submission/SUBMISSION_DATA_AVAILABILITY.md` makes an unusual claim: access
  to the restricted comparator does not run through the author, because the IMF
  publishes the reports and the deposit lists all 1,064 by report number, year,
  country, DOI and SHA-256. It also concedes that automated collection is
  bot-walled and that 354 documents came through a web archive, and it discloses
  that one deposited file ships with three columns redacted. **Does that satisfy
  PLOS's third-party-data policy, or does the check bounce it?** Read the current
  policy yourself.
- The evidence deposit is described as not yet deposited, so its DOI is a
  placeholder. Is that acceptable at submission?

## 2. The PLOS ONE referee — a full report with a recommendation

- **Is the estimand identified?** Year fixed effects, a World Bank indicator, a
  WB-specific linear trend in centred year, a WB×post indicator, a token offset —
  with **three** post-period years. Derive the design matrix from
  `07_code/bootstrap_engine.py` rather than from §5, then judge §5's own account
  of the identifying assumption.
- **The new calibration result is the thing to attack hardest.** S9 claims the
  dispersion estimator recovers about an eighth of the truth and that size reaches
  0.095. `07_code/dispersion_calibration.py` and
  `06_machine_output/dispersion_calibration.json` are attached. **Rerun it, or
  reason it through.** Is the simulation fair? Is a gamma-mixed Poisson the right
  alternative? And does the conclusion — that this makes the null *safer* —
  actually follow, or is the author being generous to himself in the one place he
  looks hardest at himself?
- **PASS-P's support is 512 patterns.** Table 5c gives all three origins. Is
  reporting a *p*-value to four decimals from a 512-point discrete support
  defensible at all?
- **The comparator.** Institution and genre are confounded; the Fund's base rate
  is 2.8× the Bank's on P1 and 5.3× on P2, and the Fund also moved — by +0.145,
  with an interval clearing zero by 0.0029 after 16% of draws were discarded.
  Does the design survive that, and does the paper concede enough?
- **The null.** Find any sentence anywhere that treats failure-to-reject as
  evidence of absence. One slipped sentence is a real finding; generic praise is
  not.
- **The corpus-selection claim**, which the title leads with. Is the decomposition
  sound? Is "all of it" defensible? Recompute if you doubt it.
- **Reproducibility.** Could you rerun this from the archive
  (`10.5281/zenodo.22168611`) and the deposit? Name what is missing.
- What would move you one recommendation higher?

## 3. Citations — both directions, and the half no tool can do

The predecessor paper from this project was rejected partly for **unverified and
drifted citations**, so this section gets the most attention.

**3a. The machine half already ran, and is not to be trusted blindly.**
`07_code/audit_citations.py` resolved every DOI against Crossref and cross-checked
in-text citations against the list in both directions; its output is
`06_machine_output/citation_audit.json` — 26 entries, 23 Crossref-resolved, three
conference papers carrying stable proceedings URLs in place of a DOI, no uncited
entry, no unlisted in-text citation. **That tool produced three false findings
before it produced a true one**: a paragraph-boundary DOI theft, a one-word
surname regex, and a line-wrapped surname read as uncited. Treat its clean verdict
as a starting point, not a guarantee, and spot-check at least five entries
yourself.

**3b. The two-way check, by hand.** For every in-text citation in the body: does
an entry exist? For every entry: is it cited anywhere? Report both directions.

**3c. The check no tool can make, and your main job here.** For each in-text
citation in §2 and §5: **does the cited work actually support the specific
proposition attached to it?** Read the sources — abstracts at minimum, full text
where open access. Flag any citation used for a claim stronger than, or different
from, the one its source makes.

**3d. Five citations were repaired last round. Check the repairs, not only the
originals.** `03_decisions/ROUND15_RESPONSE.md` §7 states what was found and what
changed. Verify each independently:

- that neither Liang et al. 2025a nor 2025b analyses peer review, and that
  Liang et al. 2024 (ICML, PMLR 235:29575–29620) does;
- that Kobak, both Liang papers and Juzek & Ward all *derive* their word sets
  from the corpus under study, whereas this paper imports a fixed list — and that
  §2 now says so;
- that `boast`, `testament` and `tapestry` are absent from Kobak et al.'s
  published excess-vocabulary list;
- that Bai & Perron (1998) locate breaks by SSR minimisation, not by ranking
  candidate cuts by coefficient magnitude as `s12_robustness.py` does;
- that none of Broad 2006, Vetterlein 2012 or De Francesco & Guaschino 2020
  studies the IMF.

**If any repair is itself wrong, that is the single most valuable thing you can
report.**

**3e. What is missing.** Search for work published since mid-2026 this paper must
engage with, and older work in adjacent fields it has plainly not read. Prioritise
LLM-associated lexical shift and excess-vocabulary estimation; preregistration
outside psychology and medicine; null-result publication; institutional discourse
analysis; interrupted time series with few post-treatment periods; corpus
representativeness and unit-of-analysis effects.

**Every reference you recommend needs a DOI or stable URL you actually resolved,
and a statement of where you checked it.** An invented reference is worse than a
gap, and this project has already paid that price once. Mark each **required** or
**improving**.

---

## Rules

- **Be adversarial.** Fifteen rounds have found and fixed well over a hundred real
  defects. If your report is broadly positive, you have not looked hard enough.
- **Verify before asserting.** The machine outputs are attached; when you doubt a
  number, check it. When you cannot check something, say so rather than hedging.
- **Do not invent** citations, DOIs, journal policies, word limits or acceptance
  rates. Mark anything from training knowledge as unverified.
- **Do not add IMF document text to this conversation** and do not ask for it. If
  an analysis would need it, say what it would need and why.
- Separate **would reject** from **would improve**, and rank accordingly.

## Deliverables

1. Editor assessment, ending in a decision, with an explicit answer on the
   over-disclosure question.
2. Referee report with a recommendation (accept / minor / major / reject).
3. Citation audit: verified / drifted / mis-supported / missing, in that order,
   with your verdict on each of the five round-15 repairs.
4. Prioritised content changes, each with a location and a rationale.
5. Closing paragraph: the single change that most raises acceptance probability,
   and the single thing most likely to sink the paper.
