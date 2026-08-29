**SUPERSEDED by THIRD_EYE_PROMPT_v2_20260828.md.** This version was written while Government Information Quarterly was still the assumed target and PLOS ONE had not been identified. Kept for the record.

---

# Third-eye review brief — `PAPER_DRAFT_v2.md`

**How to use this.** Paste everything below the horizontal rule into a capable
LLM with web access, and attach the `third_eye_kit/` bundle. The kit is 36 files
in seven numbered folders; `MANIFEST.md` says what each one is for.

**Before you send it.** The bundle contains no IMF document text and none may be
added. The corpus is used under a written permission that forbids redistributing
documents or extracted text; counts, hashes, column names and log lines are
permitted derived outputs. `tools/build_third_eye_kit.py` refuses to build if a
staged file lies under an IMF tree or carries a document-text signature — rebuild
with it rather than adding files by hand.

---

You are acting as a **third-eye reviewer**: an independent expert brought in
before submission, with no stake in the paper's success and no obligation to be
encouraging. Two adversarial audit rounds have already run against this
manuscript and their findings are fixed, so surface-level errors are mostly gone.
Your value is in the things a self-audit structurally cannot see: venue fit,
disciplinary framing, what a real editor does in the ninety seconds before a desk
rejection, and whether the literature the paper stands on is the right literature.

## The material

Attached, in `third_eye_kit/`:

| folder | what it holds |
|---|---|
| `01_manuscript` | `PAPER_DRAFT_v2.md` — the paper under review, ~9,400 words |
| `02_frozen_design` | the Stage-A preregistration, the Stage-B analysis plan, and the freeze record (DOI + SHA-256) |
| `03_decisions` | decisions D-1..D-13, both deviation records, the researcher-degrees-of-freedom self-audit, the pre-outcome power analysis, and the confirmatory run's own report |
| `04_tables` | the seven numbered tables, generated from data |
| `05_figures` | the three figures, generated from data |
| `06_machine_output` | the two panel batteries, the family verdict, the panel cells, the ITS results, the 76-unit Annual Report series, and a post-hoc trend exploration that is deliberately NOT in the manuscript |
| `07_code` | the frozen inference engine, the validation battery, the standardization estimator, and both generators |
| `08_venue_research` | a prior venue-research pass whose conclusions the author has not acted on — attached for you to attack, not to adopt |

Everything numeric in the manuscript regenerates from `06` via `07`. If a number
in the paper disagrees with the machine output, the paper is wrong.

## What the paper is

A solo-authored study with three stacked contributions, in the author's order:

1. **An audit design** for measuring institutional language change: two-stage
   sealed preregistration, a frozen inference engine, ruled defect ledgers, and a
   deposit that hash-lists what it may not redistribute.
2. **RQ1, a replication and extension** of Moretti & Pestre's *Bankspeak* (2015)
   from primary World Bank documents. The trajectories reproduce; a bureaucratese
   register rises thirtyfold; and the same archive yields a 43% or a 14% decline
   in temporal anchoring depending only on whether Annual Report volumes are
   assembled into fiscal-year units.
3. **RQ2, a preregistered null.** A difference-in-differences test of post-2022
   LLM-associated vocabulary in World Bank operational documents against an IMF
   Article IV comparator. Two panels, four conjunctive conditions each, Holm
   across panels. No panel passes. One panel reaches *p* = 0.0142 and then fails
   the preregistered concentration guard, the influence check, and specification
   stability; a preregistered event study puts a pre-period bin above the headline
   estimate; and the design's own power analysis, computed before any outcome
   existed, gives 0.16–0.22 power at the observed effect size.

The author is a computational humanities researcher submitting solo, aiming to
place this by **March 2027** for a Turkish associate-professorship application,
which rewards articles in indexed journals. Current default target: *Government
Information Quarterly*, alternate *Information Processing & Management*.

## Your five tasks

### 1. Venue research — do this first, use the web, and treat the attached
research as a hypothesis to attack

`08_venue_research/VENUE_RESEARCH_20260828.md` is attached. It is one prior
research pass — two LLM reads with web access plus a synthesis — and it reaches
conclusions the author has **not** acted on. Do not accept it. Do not simply
restate it. Check it, and say where it is wrong.

Its central claims, for you to test:

- ***Government Information Quarterly* is the wrong primary target**, not because
  of the null but because GIQ's scope is built on a citizen–state relation and the
  World Bank has no citizens, no electorate and no FOI statute in that sense. It
  reports 40+ recent GIQ research articles with zero diachronic corpus work and
  zero studies of an international organisation.
- **Humanities and Social Sciences Communications** is the recommended primary,
  on the grounds that its published policy names both negative results and
  academically justified replication.
- **PLOS ONE** as deadline insurance, with the restricted-data exception as the
  real exposure given the IMF permission.
- **Digital Scholarship in the Humanities** is the right intellectual home but
  probably too slow for a March 2027 deadline.
- ***Information Processing & Management* should be dropped entirely** — it would
  need the paper to become an evaluated measurement instrument benchmarked against
  baselines, which is a rewrite rather than a reframing.

Do not rely on training knowledge for scope or policy; it goes stale and stale
journal advice is worse than none. **Search.** For each venue you consider, check
the current aims-and-scope statement and at least two 2025–2026 issues yourself.

Deliver your own ranked shortlist of **at most five** venues. For each: fit, the
honest reason it might reject, stated or observed attitude to null results and to
preregistration, article types available (is there a registered-report or
research-note route?), word and format limits, and indexing status. State
explicitly where you could not verify something.

Then answer directly, in your own voice: **is GIQ the right target, or is the
author defaulting to it because it is indexed?** If you disagree with the attached
research, say so and show your evidence — an independent contradiction is worth
more to the author than a second agreement.

**Five items that research could not verify have since been resolved against
primary sources** — see `08_venue_research/VENUE_FACTS_VERIFIED_20260828.md`,
which supersedes the research pass wherever they differ. In particular:

- **ÜAK requires the article to be PUBLISHED.** Accepted, in press, online-first
  and "available online" are explicitly excluded by name, and a DOI is not
  sufficient. **So March 2027 is a publication deadline, not a decision one**, and
  every venue must be judged on submission-to-publication. Weigh this: it is the
  binding constraint and the research pass did not have it.
- Scopus-only counts (10 points), and single-authored it clears the minimum alone.
- HSSC's APC is £1,390 / $1,990 / €1,590, priced at acceptance.
- PLOS ONE's third-party-data exception exists and covers this case in policy.
- DSH is in **both** SSCI and AHCI; *Journal of Cultural Analytics* is in Scopus
  but **not** in Web of Science, and charges no fees at all.

Check these if you can — but spend your effort on what they do not settle:
**actual submission-to-publication times** at your shortlisted venues, which no
policy page states and which decides this case. Recent articles' received /
accepted / published dates are the available evidence.

### 2. The editor's ninety seconds

For your top-ranked venue and for GIQ, read as the handling editor deciding
whether to desk-reject.

- Does the abstract earn a read of the introduction?
- **A null result is a desk-rejection risk almost everywhere.** What would the
  cover letter have to say for you to send this out? Draft that cover letter, in
  full, for your top-ranked venue.
- Which of the three contributions should **lead**? The author leads with the
  audit design. Is that right for this venue, or is it a retrofit after the
  headline finding failed — and would an editor read it as one?

  **The attached venue research says leading with the audit design is wrong at
  every venue** — that preregistration, frozen engines and defect ledgers are
  warrants rather than findings, and that no editor commissions a paper about how
  carefully someone measured. Accepting that would mean restructuring §1 and the
  abstract, not editing them: RQ1 plus the unitisation artefact would lead, RQ2
  would become the disclosed designed null, and the audit design would become the
  warrant that makes an unconfirmed result reportable. **The author has not done
  this and is waiting for an independent view. Adjudicate it, and commit to an
  answer.**

  To make that concrete, `08_venue_research/FRAMING_OPTION_B_20260828.md` carries
  a **drafted** option B — a full alternative abstract and a replacement for §1's
  contributions block — so you are choosing between two texts rather than between
  a text and a description of one. Read both. Say which you would send out, and
  if it is B, say what else in the paper has to move with it. If neither, write
  the opening you would actually want.
- Is the title working? Propose two alternatives and say what each buys.

### 3. The reviewer's report

Write a full referee report in the format that venue uses, with a recommendation
(accept / minor / major / reject). Cover:

- **Novelty and contribution.** Is the audit design genuinely transferable, or is
  it project-specific scaffolding described as a method? Be hard on this — it is
  the paper's lead claim.
- **Methods.** The design carries a World-Bank-specific linear trend alongside the
  post-2022 indicator, with only three post-period years. Is the estimand
  identified? Is the paper right that its own estimate is a short extrapolation
  off a steep fitted trend? Check `07_code/bootstrap_engine.py` for the actual
  design matrix rather than taking §5's word for it.
- **The comparator.** Institution and genre are confounded; the Fund's base rate
  is 2.8× the Bank's on one panel and 5.3× on the other, and the Fund's own rate
  also moved. Does the difference-in-differences survive that, and does the paper
  concede enough?
- **The null.** Is the failure to establish an effect reported as a bound rather
  than as evidence of absence, everywhere? Find any sentence that slips.
- **RQ1.** Is the replication convincing as a validation gate? Is the
  assembled-versus-document-level measurement result a real methodological
  finding or a corpus-construction footnote inflated into one?
- **Reproducibility.** Could you rerun this? What is missing?
- What would make you move from your recommendation to the next one up?

### 4. Content recommendations

Concrete and prioritised. For each: what to change, where, and why it improves
the paper's chances. Cover at minimum:

- What to **cut**. The paper is ~9,400 words and discloses a great deal. Name the
  passages that cost more than they earn.
- What to **strengthen or promote**. Is anything under-claimed? Note in
  particular `06_machine_output/trend_analysis.json`: a differential trend of
  roughly 4% a year between the two institutions, which survives on 1999–2022
  data alone and strengthens when the guard family is removed. The author
  deliberately did **not** promote this, on the grounds that it is unpreregistered
  post-hoc and that the event study cannot separate it from the post-period
  estimate. **Was that the right call?** Argue both sides and decide.
- **Structure.** Does §6 hold together, or has it become a chain of caveats?
- Anything **missing** a reviewer will demand: a figure, an analysis, a
  robustness check, a comparison.

### 5. References — and this is where the predecessor failed

The previous paper from this project was rejected partly for **unverified and
drifted citations**. The current reference list is 25 entries, closed and checked
on 2026-08-07, and the manuscript says so deliberately.

Your job:

- **Verify what is there.** Check each entry resolves — DOI, journal, year,
  volume, pages. Flag anything that has drifted, been retracted, or been
  superseded.
- **Find what is missing.** Search for work published since mid-2026 that this
  paper must engage with, and for older work in adjacent fields the author has
  plainly not read. Prioritise: LLM-associated lexical shift and
  excess-vocabulary estimation; preregistration and registered reports outside
  psychology and medicine; null-result publication in information science;
  institutional and organisational discourse analysis; difference-in-differences
  with few post-treatment periods; corpus representativeness and unit-of-analysis
  effects.
- **For every reference you recommend, give a verifiable DOI or a stable URL, and
  say where you verified it.** Do not produce a citation you have not checked
  resolves. An invented or misremembered reference is worse than a gap, and this
  project has already paid that price once.
- Say which recommendations are **required** to survive review and which are
  merely improving.

## Rules

- **Be adversarial.** Two audit rounds already caught 41 real defects between
  them. If your report is broadly positive, you have not looked hard enough —
  find the things they could not.
- **Verify before asserting.** The machine outputs are attached; when you doubt a
  number, check it. When you cannot check something, say so rather than hedging.
- **Do not invent citations, DOIs, journal policies, word limits, or acceptance
  rates.** Mark anything from training knowledge as unverified.
- **Do not add IMF document text to this conversation**, and do not ask for it.
  If an analysis you want would require it, say what it would require and why.
- Separate **would reject** from **would improve**. Rank accordingly.

## Output

1. Venue shortlist with the GIQ verdict, stated plainly.
2. Editor assessment plus a full draft cover letter for the recommended venue.
3. Referee report with a recommendation.
4. Prioritised content changes, each with location and rationale.
5. Reference audit: verified, drifted, missing — the last with DOIs you checked.
6. A closing paragraph: the single change that most raises the acceptance
   probability, and the single thing most likely to sink it.
