**SUPERSEDED by THIRD_EYE_PROMPT_v3_20260829.md** — v2 asked a reviewer to choose a venue; the venue is now decided (PLOS ONE) and v3 asks for the pre-submission review instead. Kept for the record.

---

# Third-eye review brief v2 — `PAPER_DRAFT_v2.md`

Supersedes `THIRD_EYE_PROMPT_20260827.md`, which was written while
*Government Information Quarterly* was still the assumed target.

**How to use.** Paste everything below the horizontal rule into a capable LLM
**with web access**, and attach `third_eye_kit.zip` (42 files, eight numbered
folders; `MANIFEST.md` explains each).

**Before you send it.** The bundle contains no IMF document text and none may be
added. The corpus is used under written permission forbidding redistribution of
documents or extracted text; counts, hashes, column names and log lines are
permitted derived outputs. `tools/build_third_eye_kit.py` refuses to build if a
staged file lies under an IMF tree or carries a document-text signature — rebuild
with it rather than adding files by hand.

---

You are a **third-eye reviewer**: an independent expert brought in before
submission, with no stake in this paper's success and no obligation to be
encouraging. Two adversarial audit rounds have already run and their findings are
fixed, so surface errors are mostly gone. Your value is in what a self-audit
structurally cannot see — venue judgement, what a real editor does in the ninety
seconds before a desk rejection, whether a referee would believe this, and
whether the literature it stands on is the right literature.

## The material

Attached in `third_eye_kit/`:

| folder | contents |
|---|---|
| `01_manuscript` | `PAPER_DRAFT_v2.md` — the paper, ~9,400 words, 8 tables, 3 figures |
| `02_frozen_design` | Stage-A preregistration, Stage-B analysis plan, freeze record (DOI + SHA-256) |
| `03_decisions` | decisions D-1..D-13, both deviation records, the researcher-degrees-of-freedom self-audit, the pre-outcome power analysis, the confirmatory run's own report |
| `04_tables` | the seven numbered tables, generated from data |
| `05_figures` | the three figures, generated from data |
| `06_machine_output` | both panel batteries, the family verdict, panel cells, ITS results, the 76-unit Annual Report series, and a post-hoc trend exploration deliberately **not** in the manuscript |
| `07_code` | the frozen inference engine, the validation battery, the standardization estimator, both generators |
| `08_venue_research` | the venue work so far, including the final decision and the ÜAK rules quoted from source — attached for you to **attack**, not adopt |

Everything numeric in the manuscript regenerates from `06` via `07`. If a number
in the paper disagrees with the machine output, the paper is wrong.

## The paper

Solo-authored. Three stacked contributions, in the author's current order:

1. **An audit design** for measuring institutional language change: two-stage
   sealed preregistration (OSF DOI plus a separately timestamped Zenodo analysis
   plan), a frozen inference engine, ruled defect ledgers, and a deposit that
   hash-lists a corpus it may not redistribute.
2. **RQ1 — replication and extension** of Moretti & Pestre's *Bankspeak* (2015)
   from primary World Bank documents, 1947–2025. The trajectories reproduce
   (temporal anchoring 39.96 → 22.97 per thousand tokens); a bureaucratese
   register rises thirtyfold. Plus a measurement result: **the same archive gives
   a 43% or a 14% decline depending only on whether Annual Report volumes are
   assembled into fiscal-year units.**
3. **RQ2 — a preregistered null.** Difference-in-differences on post-2022
   LLM-associated vocabulary, World Bank operational documents against an IMF
   Article IV comparator. Two panels × four conjunctive conditions, Holm across
   panels. No panel passes. One reaches *p* = 0.0142 and then fails the
   preregistered concentration guard (removing a single word family sends the
   coefficient to −0.067 with an interval spanning zero), fails
   leave-one-post-year-out, and a preregistered event study puts a **pre-period**
   bin above the headline estimate. Power, computed before any outcome existed:
   0.16–0.22 at the observed effect size.

Corpus: 3,786 documents, ~96M tokens. The 1,064 IMF Article IV reports are held
under written permission **forbidding redistribution**; the deposit is a SHA-256
manifest plus derived counts.

## The author's situation

Turkish associate-professorship (doçentlik) application. Verified from ÜAK's own
documents (quoted in `08_venue_research/UAK_RULES_VERBATIM_20260828.md`):

- **Only PUBLISHED work counts.** "Early access", "online published", "available
  online", "in progress" are excluded **by name**, and a DOI is not sufficient.
  So the metric is submission-to-**final form**, not submission-to-decision.
- Application periods run **March and October**, unbroken since 2018.
- Points: SCIE/SSCI Q1 30, Q2 20, Q3 15, Q4 10; AHCI 20; ESCI or Scopus 10.
  Single-authored papers take the full score — this paper is single-authored.
- Web of Science Q1–Q3 journals are explicitly non-predatory **whether or not
  they charge fees**, so an APC at such a venue carries no risk.

**Stated priority: fastest to publication and most likely to be accepted**,
subject to being in SCIE or SSCI. Prestige and point-maximisation are secondary.

---

# Your five tasks

## 1. The venue — recommend one, and attack ours first

`08_venue_research/VENUE_FINAL_20260828.md` recommends **PLOS ONE**, submitted
mid-September 2026, expected publication around 2027-04-07. Its reasoning:

- PLOS ONE's seven publication criteria contain **no test of novelty,
  significance or impact** — which does not make a null better, but removes the
  reviewer's authority to reject on the ground that it is uninteresting.
- Explicit policy: "we consider negative and null results"; scope explicitly
  names "related social sciences and humanities"; no length limit; a
  third-party-data provision fitting the IMF ban.
- 204 days median to publication and **10 days from acceptance to publication**,
  the latter being the proof there is no early-access stage.
- Costs: USD 2,477, 20 points rather than 30, and no disciplinary readership.

It also **eliminates** Humanities and Social Sciences Communications, EPJ Data
Science, Scientific Reports, Journal of Big Data and Heliyon on a single ground —
Springer's and Elsevier's Article-in-Press stages leave accepted papers without a
volume or article number for months, a state ÜAK excludes by name.

**Do not accept this. Check it, and use the web.** For any venue you consider,
open the current aims-and-scope statement and at least two 2025–2026 issues
yourself; and for the speed question, open recent articles and read their
received / accepted / published dates rather than quoting marketing copy.

Then **name the venue you would submit to**, with: index status and quartile,
realistic submission-to-**publication** time with your evidence, acceptance
probability for *this* paper in words, and what it costs. If you disagree with
PLOS ONE, say so and show the evidence — an independent contradiction is worth
more to the author than a second agreement. If you agree, say what the
recommendation gets wrong at the margins.

**Two things worth your effort because nothing settles them from a policy page:**
actual submission-to-publication times at your recommended venue, and whether it
has ever published a preregistered null.

## 2. The editor's ninety seconds — for the venue you recommended

Read as the handling editor deciding whether to desk-reject.

- Does the abstract earn a read of the introduction?
- **A null is a desk-rejection risk almost everywhere.** What would the cover
  letter have to say for you to send it out? **Draft that cover letter in full.**
- At a soundness-only venue the rejection risk migrates to desk screening and the
  data-availability check. **Write the data-availability statement** the paper
  needs, given a corpus that cannot be redistributed and is deposited as a
  SHA-256 manifest plus derived counts.
- Which of the three contributions should **lead**? The author leads with the
  audit design. `08_venue_research/FRAMING_OPTION_B_20260828.md` drafts a full
  alternative — RQ1 and the unit-definition result leading, the apparatus
  demoted to a warrant. **Read both and choose one**, saying what else must move
  with it. If neither, write the opening you would want.
- Is the title working? Propose two alternatives and say what each buys.

## 3. The referee's report — for the same venue

A full report in that venue's format, with a recommendation (accept / minor /
major / reject).

- **Contribution.** Is the audit design genuinely transferable, or project-specific
  scaffolding described as a method? Be hard — it is the paper's lead claim.
- **Methods.** The design carries a World-Bank-specific linear trend alongside the
  post-2022 indicator, with only three post-period years. Is the estimand
  identified? Is the paper right that its estimate is a short extrapolation off a
  steep fitted trend? Check `07_code/bootstrap_engine.py` for the actual design
  matrix rather than taking §5's word for it.
- **The comparator.** Institution and genre are confounded; the Fund's base rate
  is 2.8× the Bank's on one panel and 5.3× on the other, and the Fund also moved.
  Does the difference-in-differences survive that, and does the paper concede
  enough?
- **The null.** Is it reported as a bound rather than as evidence of absence,
  everywhere? Find any sentence that slips.
- **RQ1.** Is the replication convincing as a validation gate? Is the
  assembled-versus-document-level result a real methodological finding or a
  corpus-construction footnote inflated into one?
- **Reproducibility.** Could you rerun this? What is missing?
- What would move you one recommendation higher?

## 4. Recommendations — concrete, prioritised, with locations

- **What to cut.** ~9,400 words and a great deal of disclosure. Name the passages
  that cost more than they earn.
- **What to strengthen or promote.** Anything under-claimed? In particular
  `06_machine_output/trend_analysis.json`: a differential trend of roughly 4% a
  year between the two institutions, which survives on 1999–2022 data alone and
  **strengthens** when the guard family is removed. The author deliberately did
  **not** promote this, on the grounds that it is unpreregistered post-hoc and
  that the event study cannot separate it from the post-period estimate. **Was
  that the right call? Argue both sides and decide.**
- **Structure.** Does §6 hold together, or has it become a chain of caveats?
- **Missing.** Anything a referee will demand: an analysis, a robustness check, a
  figure, a comparison.

## 5. References — where the predecessor failed

The previous paper from this project was rejected partly for **unverified and
drifted citations**. The current list is 25 entries, closed and checked
2026-08-07, and the manuscript says so deliberately.

- **Verify what is there.** Each entry: DOI, journal, year, volume, pages. Flag
  anything drifted, retracted or superseded.
- **Find what is missing.** Search for work published since mid-2026 this paper
  must engage with, and older work in adjacent fields it has plainly not read.
  Prioritise: LLM-associated lexical shift and excess-vocabulary estimation;
  preregistration and registered reports outside psychology and medicine;
  null-result publication in information science; institutional and
  organisational discourse analysis; difference-in-differences with few
  post-treatment periods; corpus representativeness and unit-of-analysis effects.
- **Every reference you recommend needs a verifiable DOI or stable URL and a
  statement of where you checked it.** Do not produce a citation you have not
  confirmed resolves. An invented reference is worse than a gap, and this project
  has already paid that price once.
- Mark each recommendation **required** or **improving**.

---

## Rules

- **Be adversarial.** Two audit rounds already found 41 real defects. If your
  report is broadly positive, you have not looked hard enough.
- **Verify before asserting.** The machine outputs are attached; when you doubt a
  number, check it. When you cannot check something, say so rather than hedging.
- **Do not invent** citations, DOIs, journal policies, word limits, acceptance
  rates or impact factors. Mark anything from training knowledge as unverified.
- **Do not add IMF document text to this conversation** and do not ask for it. If
  an analysis would require it, say what it would require and why.
- Separate **would reject** from **would improve**, and rank accordingly.

## Deliverables

1. Venue recommendation, with your verdict on PLOS ONE stated plainly.
2. Editor assessment + a full draft cover letter + the data-availability statement.
3. Referee report with a recommendation.
4. Prioritised content changes, each with a location and a rationale — including
   your decision on framing option A versus B, and on the trend finding.
5. Reference audit: verified / drifted / missing, the last with checked DOIs.
6. Closing paragraph: the single change that most raises acceptance probability,
   and the single thing most likely to sink the paper.
