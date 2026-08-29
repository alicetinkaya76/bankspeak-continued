# Venue research, 2026-08-28 — the default target is probably wrong

**Status: input to a decision, not the decision.** Produced by two independent
LLM passes with web access (a broad scan and a hostile-editor read) plus a
synthesis. Journal scope statements and recent tables of contents were rendered
directly; several other items were **not** verified and are marked as such below.
Nothing here should be acted on without checking the marked items. The venue
choice is Ali's.

## Headline

**Government Information Quarterly is the wrong primary target**, and the reason
is structural rather than about the null result. GIQ's scope is built end to end
on a **citizen–state relation**. The World Bank has no citizens, no electorate,
and no FOI statute in GIQ's sense; the IMF comparator makes it worse, since both
panels are international financial institutions. Both passes scored GIQ low
(4/10 and 3/10) after reading actual tables of contents rather than the scope
statement: 40+ recent research articles, all digital-government and public-sector
AI, methodologically survey / conjoint / case study / framework, with **zero**
diachronic corpus work and zero studies of an international organisation.

Once the object is off-scope, the usual editorial rescue for a null — *the
question matters to our readers even if the answer is no* — is unavailable.

## Ranked shortlist

| # | Venue | Why | Honest risk |
|---|---|---|---|
| 1 | **Humanities and Social Sciences Communications** (Springer Nature) | The only venue whose *published policy* names both of this paper's hardest features: negative results and academically justified replication. Cross-cutting scope includes digital humanities. SSCI + AHCI. Timeline plausibly clears March 2027. | Desk editor reading it as two papers stapled together; mega-journal discount in some Turkish committees; **APC unresolved — one pass reports ~£1,240, the other ~£3,500. Check the journal's own APC page.** |
| 2 | **PLOS ONE** | Explicit long-standing policy accepting nulls and replications, judged on validity. **No word, table or figure limit** — the manuscript goes as written. Scope effectively unbounded, so no desk-reject-on-scope risk. SCIE. | **Data availability is the real exposure**: the 1,064 Article IV reports under non-redistribution permission must go through the restricted-data exception, and *the current wording of that exception was not verified*. Check before submitting, not at revision. |
| 3 | **Digital Scholarship in the Humanities** (OUP/EADH) | The native intellectual home — Bankspeak is a Literary Lab product and this replicates it from primary sources. The 43%/14% unitisation result is a first-order finding here and a footnote elsewhere. ~9,000-word cap fits as written. | **Speed** — OUP humanities queues likely miss March 2027. Out-of-scope rule excludes *methodology descriptions*, so an apparatus-first framing is a desk-reject trigger. The reviewer pool cannot referee the difference-in-differences. |
| 4 | **Government Information Quarterly** | Fast desk decision, and the RQ2 question is genuinely live in GIQ's current pages: recent issues are saturated with generative-AI-in-the-public-sector work and **not one article asks whether LLM-shaped language has actually entered official documents**. | 75–85% desk reject (*editorial judgement, not a statistic*). No null policy, no replication policy, no research-note route. |
| 5 | **Research & Politics** (SAGE) | Best policy match for RQ2 *alone*: encourages replication, runs a real two-stage Registered Report track, mandates data deposit. SSCI. | 4,000 words including notes and references. A purpose-built standalone paper, not this one. |

**Dropped:** *Information Processing & Management* — the alternate in the
original plan. It would require the paper to become a reusable, evaluated
measurement instrument benchmarked against naive baselines, with the World Bank
demoted to a validation case. That is a rewrite, not a reframing.

**Not established:** *Journal of Cultural Analytics* is the best intellectual fit
and is fast and free, but **no Web of Science Core Collection listing was
established** — viable only if Scopus alone satisfies the ÜAK criteria for this
field, which was also not verified. *Journal of Documentation* was raised from
training knowledge with nothing verified; worth a short check as a
better-standing DSH substitute, but do not act on it as reported.

## The finding that is about the paper, not the venue

> **Leading with the audit design is wrong at every venue.**

Both passes reached this independently. Preregistration, frozen engines and
defect ledgers are *warrants*, not findings; no editor commissions a paper about
how carefully someone measured. The temptation is strongest at DSH and must be
resisted hardest there, because DSH's out-of-scope rule explicitly excludes
methodology descriptions.

`PAPER_DRAFT_v2.md` §1 currently states the audit design as **the lead
contribution**. If this recommendation is accepted, §1 and the abstract need
restructuring, not editing: RQ1 plus the 43%/14% unitisation artefact would lead,
RQ2 would be the disclosed designed null, and the audit design would become the
warrant that makes an unconfirmed result reportable rather than discardable.

**This has not been done.** It is a strategic call about what the paper is for,
and it rests on one research pass; the third-eye reviewer is asked to adjudicate
it independently.

## Lead contribution, per venue

| Venue | Leads | Demoted |
|---|---|---|
| HSSC | RQ1 replication + 43%/14% artefact | audit design → warrant, detail to SI |
| PLOS ONE | RQ1 + artefact, RQ2's full apparatus as validity evidence | — (apparatus welcome here) |
| DSH | RQ1 + artefact | RQ2 → one section |
| GIQ | RQ2 + the negative verdict | RQ1 → context |
| Research & Politics | RQ2 alone, as a lexicon-robustness lesson | RQ1 absent |

## The binding constraint neither pass priced correctly

March 2027, against a start of 2026-08-28: roughly seven months for submit →
review → decision → revision → acceptance. **What ÜAK requires — published,
accepted, or online-first — was not verified and Ali must check it for this
field.** On the assumption of ~7 months, the author gets **two serious attempts,
not four**, which is what demotes GIQ: the GIQ-viable version needs RQ2 to lead,
which is the opposite front half from every other venue on the list. That is not
a cover letter, it is a second manuscript, and none of it transfers.

## Cover letter requirements for a null result (HSSC)

Six things, in order, none optional:

1. **Sentence one names the negative result.** An editor who finds the null in
   paragraph four reads the first three as concealment.
2. **Cite the journal's own policy by name** and map it: RQ1 is the replication,
   RQ2 is the negative result. Make the decision a policy application rather than
   a judgement call.
3. **Give the OSF DOI and the separately timestamped Zenodo SAP in the letter
   body**, with the explicit sentence that the plan was sealed before any outcome
   existed.
4. **Put the 0.16–0.22 power forward as a design property computed in advance**,
   never as a post-hoc apology. Met first in the discussion it reads as an
   excuse; met in the cover letter it reads as competence.
5. **Pre-empt the "two papers stapled together" read in its own paragraph.**
6. **Name what a reader should do differently now** — that single-word-family
   lexicon detectors of LLM influence are not robust, since the concentration
   guard sends the coefficient to −0.067 with a CI spanning zero. That is more
   useful than the null and it is what makes the paper citable.

Plus one compliance line in the submission itself: declare the 1,064 Article IV
reports held under written permission forbidding redistribution, and name the
hash-list deposit as the substitute. An editor discovering the restriction at
revision is avoidable at every venue on this list.

## Where the two passes disagreed

- **Attempt GIQ at all?** Broad scan: demote. Hostile editor: cheap, worth a shot
  under strict conditions. *Synthesis: skip* — the hostile editor priced the time
  cost right and the framing cost not at all.
- **One paper or two?** Hostile editor wanted a split ("two papers stapled
  together by an apparatus"). *Synthesis: single paper first, split held in
  reserve* — the split sacrifices the claim that the audit design is what makes
  the null reportable, and two pipelines is slower to a first acceptance than one.
- **DSH indexing.** Broad scan rendered the About page and reports **SSCI listed,
  AHCI not listed and not to be assumed**; the hostile editor said AHCI. Direct
  contradiction, and it matters for the docentlik file. *Prefer the rendered
  page; verify before relying on either.*

## All five unverified items are now RESOLVED

See `VENUE_FACTS_VERIFIED_20260828.md`. Every item below was checked against a
primary source on 2026-08-28 and several answers differ from what this document
assumed:

- **ÜAK requires PUBLISHED, not accepted.** Early access, online-first and
  "available online" are explicitly excluded, and a DOI is not sufficient. This
  changes the timetable: March 2027 is a publication deadline, not a decision one.
- **Scopus-only DOES count** — 10 points, and single-authored it clears the
  madde-1 minimum alone.
- **HSSC's APC is £1,390 / $1,990 / €1,590**, priced at acceptance. Both figures
  guessed below were wrong.
- **PLOS ONE's third-party exception exists in policy** and covers exactly this
  case; whether a given submission clears it remains an editorial judgement.
- **DSH is in SSCI *and* AHCI** — the apparent contradiction was an omission on
  OUP's own page, not a conflict.
- **Journal of Cultural Analytics is NOT in Web of Science** but IS in Scopus
  (2019–2026) and is diamond open access with no fees at all.

The original list is kept below for the record.

## What Ali must verify before acting (superseded — see above)

1. The ÜAK criterion for this field — published vs accepted vs online-first.
2. HSSC's actual APC (the two passes differ by roughly a factor of three).
3. PLOS ONE's current restricted-data exception wording, against the IMF permission.
4. DSH's index listing (SSCI vs AHCI).
5. Whether Scopus-only indexing would satisfy the file, which decides *Journal of
   Cultural Analytics*.
