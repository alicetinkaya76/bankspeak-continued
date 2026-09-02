# Round 20 — response to the independent audit of the built package

The audit read `PLOS_ONE_submission(4).pdf`, `PLOS_ONE_supplement(1).pdf`, the
cover letter and `third_eye_kit(5).zip`, and returned **RETURN BEFORE REVIEW /
MAJOR REVISION**. Its methodological demand — audit the artifacts that would
actually be uploaded, not the working tree — is the reason four of the findings
below exist at all, and two of those four sit in files whose guards were green.

Nothing here is estimated. Every number regenerates from `data/` by a named
command, and where a claim could not be checked it says so.

---

## What the audit got right, and what changed

### 1. The sibling-organisation attribution was wrong (§6.1, abstract, intro, §7, §8)

The audit asked whether institution and genre are separable in the excluded
class. They are not — the corpus has no genre field, and 181 of the 184 sibling
files are titled "annual report", so the audit's own genre labels (portfolio,
financial statement, case registry) are not something this repository can
support. But the question was worth asking, because decomposing the class
**refutes the manuscript's own bolded sentence**.

`tools/ar_exclusion_classes.py` now reports each sibling separately, in the same
convention as Table 3c:

| | files | 1946–65 | 2020–24 | class change | own series | own change |
|---|---:|---:|---:|---:|---|---:|
| IFC | 92 | 21.65 | 12.35 | −42.9% | 1956–2022 | −19.7% |
| ICSID | 55 | — | 74.26 | — | 1967–2025 | −8.6% |
| MIGA | 37 | — | 10.12 | — | 1989–2024 | −35.2% |
| class without ICSID | 129 | 21.65 | 10.52 | **−51.4%** | | |

ICSID was founded in 1966 and MIGA in 1988, so the early window is ten IFC files
and nothing else. IFC — the only sibling observable in both windows — falls
42.9%, effectively the Bank's own −42.5%. **On its own series not one sibling
rises.** The class-level +64.4% is a change of membership between the windows: a
dense, date-heavy population that could not appear before 1966 appears late.

`**The opposing trend is entirely the sibling organisations**` has been
withdrawn. The factor-of-three finding is untouched — mixing a *higher-rate*
population into a falling one flattens the decline whether or not that population
is itself rising — and §6.1 now says that explicitly rather than relying on a
rise. This is the same error the paper already reports catching once, one level
further down, and it is reported in the row where it was made.

New: Table 3d. The old Table 3d (corpus definition × weighting) is now Table 3e.

### 2. The abstract's two ratios came from different conventions

Correct, and the diagnosis was already in S10.8 — it was the abstract that had
not been fixed. But the audit **mislabelled the quantity**: it called 9.4×/10.9×
"Tier 1". They are the twelve *period-plausible* terms, a subset of **Tier 2**.
Tier 1 is the disjoint 28-form set in `config/families.yaml`, whose real ratios
are 10.0× equal-year and 6.0× token-weighted; and no boundary-rule Tier-1
quantity exists in this repository at all. Publishing the audit's suggested
sentence verbatim would have put a false statement in the abstract.

The axis is also not the one named. "Thirtyfold" and "9- to 11-fold" differ on
**aggregation** (equal-year mean vs pooled), not on match rule. The temporal-
anchoring figures in the same sentence are equal-year, so the coherent fix keeps
equal-year throughout. `tools/tier2_item_provenance.py` now emits equal-year
cells beside the pooled ones, and the abstract reads **thirtyfold and 10.8-fold**
— one convention, both regenerable. Abstract: 299 words.

### 3. The Data Availability Statement over-claimed, and mis-described its own routes

Two of the audit's three grounds do not hold. The DAS never says "any reader can
retrieve"; and the DOI is described as resolving to the eLibrary landing page,
not to the document, which is exactly what the probe found. But the third holds:
**"no gatekeeper" is contradicted nine lines later by our own 403 and 202
findings**, and the claim that a browser user meets no friction was asserted with
no browser probe anywhere in the repository. Both are now stated as measured or
not stated at all.

**The audit also repeated a factual error that is ours, not its.** It says 354
documents were "obtained via a public web archive". No document was. The
manifest records `pdf_url` host `www.imf.org` for **all 1,064**, and
`tools/fetch_imf_cr_pdfs.py` states the rule: the archive supplied the link the
IMF itself published on the report's own page, because the live page is
WAF-blocked; the PDF is then fetched from imf.org, never from the archive. Our
wording — "354 through a public web archive" — invited precisely that reading,
and produced it in a published review. Corrected in the DAS, the manuscript and
the author note, with the positive statement added rather than the old phrase
merely deleted.

### 4. The archive did not represent the current manuscript, and two documents disagreed

Correct, and worse than stated: `SUBMISSION_DATA_AVAILABILITY.md` named
`10.5281/zenodo.22168611` as the archive of record while the manuscript said that
release "must not be cited for" these results. Each document was internally
consistent, so nothing caught it. Reconciled; the checklist and public README
corrected; `tools/package_evidence_deposit.py` no longer bakes the superseded
version DOI into the deposit metadata.

**Still open and the author's** — see the closing section.

### 5. The AI-use disclosure

Rewritten to factual sentences with the governance framing removed, and **the
scope not narrowed**: the assistant drafted the preregistration and the analysis
plan, wrote essentially all the code, ran the analyses, drafted the manuscript
and supplement, and made methodological choices under a standing instruction from
the author. The detailed provenance stays in `docs/`. The attestation bracket is
untouched; it is the author's.

### 6. The functional-form sensitivities

Two of the five requested were already in the manuscript — leave-one-post-year-out
**is** preregistered condition C4, and the trend-free descriptive contrast is
Table 6b's event study. The other three are new, in **Table 5d**
(`tools/functional_form_sensitivity.py`).

Running them produced a finding the request did not anticipate. **Deleting a year
renumbers every later year, so it moves the block partition as well as the data**,
and a single *p* cannot separate the two. Each row is therefore evaluated at all
three block origins. At the frozen origin, dropping fiscal 2020 sends P1 from
0.0156 to 0.3164 — apparently fatal. At the other two origins the same deletion
returns 0.0117 and 0.0195. What moved was the partition. A reader given only the
frozen-origin column would have drawn the wrong conclusion.

What does move P1 is exactly what §5 and §7 already name as the identification
problem: deleting the institution trend (β 0.586 → 1.042, *p* → 0.0586) and
deleting fiscal 2024 (β → 0.207, *p* → 0.1797).

One row carries a flag: at a 15-year window there are five blocks, so the support
is 2⁵ = 32 and the smallest attainable *p* is 0.0625. **That row cannot be
significant however the data fall.** Any window shorter than sixteen common years
has this property.

### 7. Smaller repairs

- **Test count.** The manuscript said 437; pytest collects 438. The manuscript
  now states no count at all — a number that drifts should not be typed into
  prose — and `check_submission_metadata.py` enforces any count that is.
- **The reference QA paragraph** left the bibliography for the checklist. Its
  claim "matching first author and year" was also wrong: first author matches on
  31 of 31, the year on 30 (Lopez Bernal resolves to a 2016 online-first record).
- **Moretti & Pestre** split into two entries. DOI `10.64590/167` resolves to
  *New Left Review* only. Pamphlet 9 now carries its own URL, verified on
  2026-09-02: HTTP 200, `application/pdf`, 25 pages, authors and title checked
  against the file.
- **Lopez Bernal corrigendum.** The 2020 correction concerns the post-intervention
  slope term. The confirmatory design carries no such term; the descriptive scan
  that does (`src/s08_its_analysis.py`) already enters it as (*t* − *T*₀)
  truncated at zero, the corrected form. Stated in §2. No corrigendum DOI is
  cited, because none could be verified offline.
- **0.0365 vs 0.036.** 146/4,000 is an exact rounding tie that the paper and the
  supplement were resolving in opposite directions. One form now.
- **The mean-structure bracket** said 0.037–0.094. The 0.094 comes from redrawing
  ρ and σ, which is a *dependence* change, not a mean-structure one. Corrected to
  0.0365–0.086, with the 0.094 named for what it varies.
- **The 2,341 unmapped frame rows** were called "documents the pipeline could not
  place". The listing types all of them: 1,736 Public Information Notices, 538
  press releases, 44 mission concluding statements, 13 standard pages, 5
  transcripts, 3 issue pages, 2 typed only `Pdf`. That was more agnostic than our
  own metadata warrants and it understated the frame.
- **"the narrative volume is one document a year throughout"** is false; fiscal
  2008 carries fourteen. Corrected, and the full per-year inventory is published
  as **Table S10.9** — the audit's request, and it runs against the audit's
  hypothesis: the like-for-like series declines *more*, not less.
- **Inverse-probability weighting of the comparator**, also asked for, is
  degenerate here and Table 5d now shows why. Inflating a sampled IMF cell to
  its population total scales the count *and* the token offset by the same
  1/π; the estimand is a rate, so β moves by 0.0001 on P1 and 0.0010 on P2 —
  the rounding of counts back to integers. Scaling counts without tokens does
  move β, to +0.543, but that is a numerator without its denominator. Both
  rows are in the table so the difference is visible rather than argued.
- **The unmapped rows tallied by year**, which the audit asked for twice. The
  share swings from 82% in 1999 to 2% in 2024 — 55% for 1999–2016 against 1.9%
  for 2017–2025 — which alone reads as a frame that loses pre-period documents
  and would bias a pre/post contrast. It does not. Public Information Notices
  run 1999–2013 and stop; press releases run to 2016 and stop; together they are
  97.9% of every unmapped row before 2017, and the residue after it is a handful
  a year, not one of them a staff report. The gradient is two publication
  lifecycles, not selective failure. In S10.7, with the per-year table.
- **The evidence deposit** carried no input for any table added since round 13:
  a reader could unpack it and still not check S10.3, S10.4, S10.6–S10.9 or
  Tables 3c–3e, 5c and 5d. Eighteen analysis outputs added, bringing that
  directory to 33 files and the deposit to 782.
- **A negative control was testing a number, not a guard.** The control that
  proves `check_stated_counts` notices an unresolvable DOI asserted the literal
  string "30 of 34", so splitting the Moretti and Pestre record broke it even
  though the guard behaved correctly. Its expectation is now derived from the
  audit object. A control that fails when an unrelated true number changes is
  the mirror image of a guard that passes when its pattern stops matching.
- **Eleven `__pycache__` files were tracked** despite `.gitignore` declaring
  them ignored — committed before the rule, and one of them was being modified
  as a side effect of running a tool, so compiled bytecode was entering the
  provenance record and would have entered the permanent archive. Removed from
  the index; the files stay on disk.
- **`audit_citations.py`** exited 1 on every run it had ever had, so its exit code
  carried no information. Five documented non-defects are named; anything else
  fails as before.

---

## Where the audit is answered rather than followed

- **"Present the block-origin sensitivity as fragility, not robustness."** The
  manuscript never called it robustness. §6.2's passage is headed "The block
  partition is arbitrary" and ends "not a nuisance; it is a reason the single
  reported *p* should not be read as a measurement". No relabel, because a
  relabel would misrepresent what the text said.
- **"PASS-E intervals must not be presented as validated 95% CIs."** They never
  are. Table 4 labels them nominal and §7 gives the measured range, 0.705–0.910.
- **"RQ1 should be a corpus × weighting matrix, not a single percentage."** It
  already is: Table 3e, and §6.1 refuses the point estimate in as many words —
  "We report all six cells and claim the range −24% to −59%, not the point
  −42.5%."
- **"Describe β as a model-based differential shift, not a causal break."**
  Already done, in bold, in §5: "the data do not adjudicate between 'a break in
  2023' and 'the pre-existing divergence continued'… We therefore do not use
  causal treatment language anywhere."
- **"The IMF estimand is unclear."** §3.1 names it in bold — "a capped annual
  cross-section, not a census" — and S10.7 publishes the per-year frame, the
  inclusion probabilities, the per-cell seeds and an executed replay of the draw.
  Region, income group and programme status are genuinely absent from the CSVs
  and S10.7 says so; those standardisations cannot be run, and we do not claim
  they can.
- **"Gries (2008) and Egbert & Biber (2019) were correctly rejected."** They are
  not rejected — both are cited in §4, added at commit `9efaba9`, and cited for
  the auditor's own point: corpus spread is not statistical overdispersion. The
  ruling appears to describe `docs/THIRD_EYE_PROMPT_v5_20260830.md`, a historical
  brief, rather than the manuscript in the kit. Acting on it literally would have
  deleted two correctly-used citations.
- **"Tier-2 should be called an LLM-associated candidate lexicon."** The tiers are
  reversed in the request: Tier-2 is the deliberately LLM-free bureaucratese
  control. Tier-1 carries the LLM association and was already worded
  "LLM-associated"; the one unhedged instance, in the abstract, is now "an
  LLM-associated candidate lexicon", and §4 says "candidate set".

## One correction to our own previous response

`docs/ROUND18_RESPONSE.md` said MacKinnon & Webb (2017) "has been cited since
round 15". Git does not support that: the paper first carries the name at
`9efaba9` (2026-09-01), and commit `7b13387` is titled "Three of the reviewer's
seven citations do not belong". It was declined at rounds 15–16 and added at
round 17. A false provenance claim in a document that opens by promising nothing
is estimated is worse than the omission it was defending against, so it is
corrected there rather than deleted.

---

## One item flagged `needs_human_review`, not decided

Building the public archive after these repairs surfaced a contradiction inside
`tools/build_public_repo.py`: three files are named individually on its include
list and then dropped by a path rule that denies any basename beginning `imf`.

    data/analysis/imf_cadence_balance.json      (S10.5's input)
    data/analysis/imf_frame_publication.json    (S10.7's input)
    data/analysis/imf_frame_publication.csv     (the published per-year frame)

Their contents are counts, inclusion probabilities, per-cell seeds and column
*names*; the content scan passes them, and the supplement tells a reader to
reproduce both sections from the tools that write them. So the archive currently
withholds the inputs to two supplement sections a reader is invited to check.

Whether an IMF-derived aggregate may be redistributed is a licensing judgement,
not a coding one, so the pattern has not been loosened. What changed is that the
contradiction is now printed on every export run instead of happening in
silence, and the cross-package test records the three with the reason rather
than passing over them. **The call is the author's**: either narrow the DENY
pattern or remove the three from the include list.

---

## The gate — what is closed and what is not

Closed in code: the sibling decomposition, the abstract conventions, the DAS,
the functional-form table, the metadata reconciliation, the reference repairs,
the deposit contents, and the guards that let three of these through.

There is also a sixth item that is not the author's and not closed: the
licensing call recorded above under `needs_human_review`.

**Open, and the author's alone:**

1. **Cut the release and mint the version DOI.** Nothing downstream can go green
   first. `tools/check_submission_metadata.py` exits 1 until the manuscript, the
   checklist and the cover letter carry it, and now also refuses if any
   submission document still names v1.2.0 as the archive of record.
2. **Sign the author attestation.** `tools/placeholder_report.py` exits non-zero
   until then. Deliberately not filled here.
3. **Upload the evidence deposit** (`build/zenodo_evidence_deposit.zip`, 11.8 MB)
   or supply a reviewer access link, then run `tools/record_evidence_doi.py`.
4. **Affiliation, ORCID, corresponding email, funding, competing interests,
   CRediT.**
5. **Rebuild the PDFs and rerun every guard on the artifacts that will actually
   be uploaded**, after 1–4. That is the audit's own methodological point and it
   found real defects the working tree hid.
