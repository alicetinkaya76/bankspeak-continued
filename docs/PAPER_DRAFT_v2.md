# Reconstructing Bankspeak: Eight Decades of World Bank Language, a Corpus-Selection Effect, and an Unconfirmed Post-2022 Break

Statistical analysis plan frozen and externally timestamped **before** any
outcome reported here was computed: Zenodo `10.5281/zenodo.22098259`, sha256
`4aa122797f2db6ddd3e1dae5cb425958b231f02438f242bde174b25b20af2677`, published
2026-08-25T15:01:07Z. Stage-A preregistration: OSF `10.17605/OSF.IO/5C9J8`.

---

## Abstract

Moretti and Pestre's *Bankspeak* reported a long-run shift in World Bank prose
from temporally anchored description toward nominalised management language, on a
corpus and rules never released. We reconstruct it from primary
documents and extend the assembled Annual Report series through fiscal 2024.

The trajectories reproduce: mean temporal anchoring falls from 39.96 per
thousand tokens in 1946–65 to 22.97 in 2020–24, and a broader bureaucratic
register rises from 0.252 per thousand to 7.631 — a thirtyfold ratio but an
absolute rise of 7.38.

A second result concerns measurement, not the Bank. Over the same fiscal
years the same archive gives a 43% or a 14% decline, and decomposing that gap
assigns **all** of it to which files count as Annual Reports: the 195 excluded
sibling-organisation volumes trend upward while the Bank's own fall. Concatenating
volumes into fiscal-year units contributes nothing: for a token-normalised rate it
is arithmetically identical to a token-weighted mean.

We then test, under a plan sealed and timestamped before any outcome
existed, whether vocabulary associated with large language models shows a
post-2022 World Bank discontinuity against an International Monetary Fund
comparator. **No panel satisfies the prespecified decision rule.** One reaches
*p* = 0.0142, then fails the concentration guard — removing a single word family
sends the coefficient to −0.067 with an interval spanning zero — fails
leave-one-post-year-out, fails both preregistered secondary routes (*p* = 0.162
and 0.033 against a 0.025 threshold), and shows a pre-period event-study bin above
the estimate. The comparator also rose; ex ante power at that
effect size is 0.16–0.22.

The result bounds what a three-post-year, single-comparator design can
establish; it is not evidence of absence. A nominally significant aggregate break
can rest on one word family, one post-period year and one arbitrary block origin,
while a sealed multi-condition rule correctly withholds the claim.

---

## 1. Introduction

Institutions write, and what they write changes. *Bankspeak* (Moretti & Pestre
2015) made that observation quantitative for one institution, reporting a drift
in World Bank Annual Report prose away from concrete, agent-bearing description
toward abstract nominalisation and management vocabulary. The pamphlet has been
widely cited across the digital humanities and international-organisation
literatures. Its corpus, its feature definitions and its assembly rules were
never released, so the finding has been discussed far more often than it has
been checked.

Two developments make rechecking worth the effort now. The first is simply time:
the pamphlet's series ends in 2012, and the intervening fourteen years include a
financial crisis, a pandemic and a wholesale reorganisation of how development
institutions produce documents. The second is that since late 2022 large language
models have entered professional writing at scale, and a fast-growing literature
reports LLM-associated lexical shifts in scientific abstracts, peer reviews and
consumer complaints (Kobak et al. 2025; Liang et al. 2024, 2025a, 2025b; Juzek & Ward
2025). Whether the same shift reaches the drafting of institutional documents —
which are edited, templated, reviewed and legally constrained in ways that
journal abstracts are not — is an open and testable question.

**What this paper establishes, in the order it establishes it.**

**First, that the *Bankspeak* trajectory is real and continues.** Rebuilt from
primary documents and extended through fiscal 2024, the pamphlet's qualitative
claim survives independent re-measurement: temporal anchoring declines while
nominalisation, acronym density and management vocabulary rise. In ratio terms the fastest-growing register — a
broader bureaucratese vocabulary, rising thirtyfold — is not among the five
features the pamphlet named, though acronym density supplies the largest
*absolute* rise.

**Second, that the size of that finding is hostage to a decision almost nobody
reports.** Measured over the same fiscal years, the same archive gives a 43%
decline in temporal anchoring or a 14% decline, and decomposing the gap assigns
all of it to *which files count as Annual Reports* — the excluded
sibling-organisation volumes trend upward while the Bank's own volumes fall.
Concatenating volumes into fiscal-year units, the operation one would expect to
matter, contributes nothing. We state this early because it generalises past this
corpus: the unit of analysis can be inert while document selection is worth a
factor of three, and selection is usually one clause in a data section, if it
appears at all.

**Third, that a preregistered test of the post-2022 LLM hypothesis on this corpus
cannot support the claim** — and that saying so is worth more than the
alternative. One panel reaches *p* = 0.0142 and fails the two preregistered checks that
bear on the data, plus a third that failed on our own stratifier error.
The concentration guard is the informative one: with a single word family removed
the differential coefficient is −0.067 with an interval spanning zero. A study
without that guard would have published the *p*-value.

The apparatus that makes the third claim reportable — a two-stage sealed
preregistration, a frozen inference engine, ruled defect ledgers, and a deposit
that hash-lists a corpus it may not redistribute — is described in §§3 and 5. We
do not offer it as a finding. We offer it as the reason an unconfirmed result
could be written down at all, rather than quietly becoming a different paper.

Two commitments run through the paper. **On vocabulary:** we write "post-2022
increase", "consistent with", "convergent evidence"; we never write "is
AI-generated" and never assert causal attribution to any model or vendor. The
measurement is population-level change, not document classification, and §2
explains why that distinction is not cosmetic. **On numbers:** every count,
rate and coefficient reported here is regenerated from `data/` by committed code.
Where a source failed, was partial, or was ruled on, the paper says so in place
rather than in an appendix.

---

## 2. Related work

**Bankspeak and institutional discourse.** Moretti & Pestre (2015) is the direct
antecedent. The broader literature on how international organisations produce and
deploy language — Barnett & Finnemore (1999) on the authority effects of
bureaucratic expertise, Cornwall & Brock (2005) on the circulation of development
buzzwords, Mosse (2004) on the gap between policy text and practice — supplies
the interpretive frame within which a lexical drift is worth measuring at all.
Studies of Bank documents specifically (Broad 2006; Vetterlein 2012; De
Francesco & Guaschino 2020) establish that these texts are institutional
artifacts subject to internal review, which is precisely why an LLM signal in
them would be non-trivial and why its absence is not evidence that drafters are
not using the tools. **We have not located an equivalent literature on Fund staff
reports** — the third organisation in De Francesco and Guaschino is the OECD, not
the IMF — so the comparator's drafting constraints are assumed here rather than
established, which is a further sense in which it is non-equivalent (§7).

**LLM-associated lexical shift.** The methodological template we adopt comes from
excess-vocabulary estimation: Kobak et al. (2025) measure post-2022 excess word
frequencies in PubMed abstracts against pre-2022 baselines; Liang et al. (2024)
estimate LLM-modified text at the population level in machine-learning conference
peer reviews, and Liang et al. (2025a, 2025b) do the same for preprints and
published papers, and for consumer complaints, corporate press releases, job
postings and United Nations press releases — the last being the closest published
measurement to an international organisation's own prose; Juzek & Ward (2025) examine the same shift in scientific
writing. All of these estimate a *population* quantity from aggregate frequencies
rather than classifying individual documents. Our Tier-1/Tier-2 marker design
follows that logic with **two** departures, and the first is the larger.

Every one of those studies *derives* its word set from the corpus under study —
Kobak and colleagues from PubMed itself, Juzek and Ward by a three-step scan of
26.7 million abstracts, Liang and colleagues by fitting reference distributions
to each target corpus. **We do not.** Our list is fixed a priori from their
published lists and sealed before any of our text was measured, because a
confirmatory design cannot both discover its words in a corpus and then confirm
them on it. The estimation step is deleted, not adapted, and the cost is that the
list is calibrated to scientific prose and imported into institutional prose.
Second, because our corpus spans eight decades, we must separate an LLM-era shift
from a decades-long bureaucratese drift that was already underway, which is what
the two-tier split is for.

**Detection and its critiques.** We deliberately do *not* build on the AI-text
detection line (Gehrmann et al. 2019; Ippolito et al. 2020; Mitchell et al.
2023). The critiques are decisive for our purpose: detectors are biased against
non-native writers (Liang et al. 2023), perform unreliably in independent
evaluation (Weber-Wulff et al. 2023), and Wu et al. (2025) survey the gap between
reported and realised performance. A document-level detector applied to a corpus
where every document is edited and templated would produce a number we could not
interpret. Population-level change measurement is a weaker instrument that
answers a question it can actually answer.

**Interrupted time series and structural breaks.** The design distinguishes a
prespecified intervention point from an estimated one. For the former we follow
standard ITS practice (Wagner et al. 2002; Lopez Bernal et al. 2017, 2018) with
HAC standard errors (Newey & West 1987); for the latter, a descriptive breakpoint
scan enters only as a specificity check — we refit the same specification at every
admissible cut and rank 2023 among them by the magnitude of the fitted level
shift (§6.4). **That is a ranking, not structural-break estimation in the Bai and
Perron (1998) sense**, which locates breaks by global minimisation of the residual
sum of squares and settles their number by supF and sequential supF(l+1|l) tests;
`src/s12_robustness.py` sorts candidate cuts by |b₂| and discards the standard
error, so we claim none of their inferential guarantees and cite them as the
standard this check does not meet.

**Reproducibility and corpus design.** Biber (1993) on representativeness in
corpus design, Sandve et al. (2013) on reproducible computational research, and
Wilkinson et al. (2016) on FAIR data supply the standards this study's provenance
controls were built to meet. §3.3 reports a case in which all three were satisfied and the
measurement was still invalid — which is why the controls here extend to
measurement validity and not only to provenance.

---
## 3. Data

### 3.1 Sources, frames and sampling

Two institutions, four strata, English only, all sampled and analysed separately
and never pooled.

**World Bank.** The Documents & Reports open API, harvested per year into a
write-once raw capture (`data/meta/wb_p1p2_raw/`, with its request log) from
which every frame is rebuilt deterministically. Three genre strata: Annual
Reports (uncapped), Implementation Completion Reports and Project Appraisal
Documents (capped at 40 documents per year).

**International Monetary Fund.** Article IV consultation staff reports, framed
from the Fund's own publication listing and capped at 40 per year on the same
rule. Retrieval is documented in `docs/IMF_RETRIEVAL_20260820.md` and the access
position in `docs/IMF_ACCESS_COMPLIANCE_20260820.md`; 1,064 of 1,064 sampled
documents were obtained and verified against a four-rung ladder tried in order
until one rung resolves the document — cover text (869), scan metadata (170),
title similarity (16), country prefix plus year (9) — so nine documents rest on
the weakest rung. Supplement S3 gives the rungs, and the negative control that
caused a proposed title measure to be rejected before use.

The Stage-B sample is drawn per cell under the preregistered sampler (PREREG Appendix
B.7), which differs from the Stage-A global-RNG draw; the two overlap on 27.3% of
documents, disclosed in §7 rather than buried, because outcomes on the
overlapping documents were inspected at Stage-A.

**Table 1 — Corpus composition, Stage-B.**

| Stratum | Sampled | Extracted | Coverage | Span | Eligible tokens | Extraction method |
|---|---|---|---|---|---|---|
| WB Annual Reports (doc-level) | 331 | 329 | 99.4% | 1946–2025 | 10,525,261 | server_txt 291, pymupdf 36, ocr_tesseract 2 |
| WB ICRs | 1,246 | 1,239 | 99.4% | 1994–2025 | 23,211,090 | server_txt 1209, pymupdf 30 |
| WB PADs | 1,161 | 1,154 | 99.4% | 1996–2025 | 37,354,507 | server_txt 1118, pymupdf 36 |
| IMF Article IV | 1,064 | 1,064 | 100.0% | 1999–2025 | 25,102,941 | pymupdf 872, ocr_tesseract 192 |

Total 3,786/3,802 documents (99.6%), 96,193,799 eligible tokens. Every miss is
logged with its error.

### 3.2 Annual Report assembly

The Annual Report facet returns sibling-organisation reports (IFC, MIGA, ICSID),
excluded by logged per-document rules; remaining volumes are deduplicated by
report and volume number and concatenated per fiscal year. This produces the
assembled series on which RQ1 is measured. As §6.1 shows, the exclusions matter
far more than the concatenation: removing sibling-organisation volumes and
duplicates changes the headline diachronic magnitude by a factor of three, while
the concatenation itself changes it by nothing.

### 3.3 Extraction quality: provenance is not validity

An external audit of our own earlier release found two defective assembled units
that every provenance control had passed: fiscal 2002 (twelve tokens — cover
sheets only) and fiscal 2007 (46,723 tokens at a 0.9% function-word share — a
mojibake dump from a broken font encoding). Both had correct hashes, complete
manifests and pinned environments. **A frozen manifest guarantees provenance, not
measurement validity.**

The design therefore carries a prespecified per-unit gate (≥5,000 tokens, ≥15%
function-word share) and a corpus-wide diagnostic scan run before any outcome was
computed, over the full 6,143-document extraction pool — a superset of Table 1's
Stage-B sample. Every hard flag was adjudicated on record before the analysis ran,
and the gate refuses to proceed while any is unruled; supplement S6 gives the
full scan counts and the populations they are measured over.

**Table 1b — defect classes, detection and ruling.**

| Class | Detected | Ruling and effect |
|---|---|---|
| No text layer | 192 IMF documents, all 1999–2004 | OCR'd (SAP §S9). Method is collinear with the estimand, so the effect was bounded where era is held fixed: OCR recovers a median 1.012× the native token count over 20 paired documents, mean token length within 0.6%. Restored fiscal 2002 and 2007 to the AR series. |
| Lost inter-word spacing | 70 of 2,688 server-text documents; **0 of 437** from our own PDF extraction | Re-extracted from PDF, accepted only on measured two-sided improvement (D-7). Final: 61 replaced, 4 kept, of 65. |
| Non-English or bilingual | 20 ruled, 10 inside the Stage-B sample | Excluded by ruling (D-8/D-11); of the ten, seven fall inside 1999–2025 and leave the confirmatory panels. |
| Mojibake / table dump | 3 + 1 | Adjudicated individually; ledger `d13_kept.csv`. |

One row of that table is a finding rather than housekeeping: the spacing loss came
from the World Bank's **own** server-side plain text and not once from the PDF
path we had distrusted, which inverts the premise that a publisher's text is the
safer source.

**Table 2 — Exclusions applied to the analysis corpus.**

| Ledger | Rule | Documents | Strata touched |
|---|---|---|---|
| `d8_exclusions.csv` | D-8/D-11: non-English or bilingual documents | 20 ruled; **10 applied** (a subset of the 395 below) | icr, pad |
| `intention_to_sample_exclusions.csv` | PREREG §7 intention-to-sample | 395 | annual_report, icr, pad |
| `d13_kept.csv` | D-13: flagged, adjudicated, **KEPT** (listed for completeness; not an exclusion) | 1 | annual_report |

Of the 395 intention-to-sample exclusions, 382 are documents outside the
confirmatory window 1999–2025; the remainder are the language and eligibility
rulings above.

### 3.4 Access and redistribution

IMF documents are used under a written permission that forbids redistributing
documents or extracted text and permits publishing derived non-substitutive
outputs including SHA-256 hashes. The evidence deposit is therefore built to
carry the World Bank raw captures and all derived artifacts in full, and every
IMF-derived file by hash only, each listed by path so any holder of the originals
can verify byte-for-byte. It is prepared by `tools/prepare_zenodo_deposit.py` and
**will be deposited before publication**; §9 gives its contents, and its DOI is
inserted there once it is minted.

---

## 4. Measures

Three families, all computed per document and aggregated to institution-year
cells with token offsets.

**Classic Bankspeak features**, operationalising the pamphlet's qualitative
claims: nominalisation density, temporal anchoring (explicit dates and time
references), management vocabulary, acronym density, and function-word share.

**Two-tier lexical markers.** *Tier-1* is the LLM-associated set (`delve`,
`underscore`, `showcase`, `pivotal`, `intricate`, `meticulous`, `boast`,
`commendable`, `realm`, `testament`, `tapestry`, `seamless`, `multifaceted`).
**Its provenance is mixed and we state it rather than round it up.** Ten of the
thirteen appear in Kobak et al.'s published excess-vocabulary list; `boast`,
`testament` and `tapestry` do not, and the frozen configuration attributes the
set to "Kousha & Thelwall-style lists" alongside the distributional work, a
source this paper does not otherwise cite. An earlier draft called this heading
"with per-word provenance" and described the whole set as what the
excess-vocabulary literature reports rising after 2022; `config/families.yaml`
records one blanket attribution for all thirteen and no per-word field, so
neither was true. Nothing about the frozen list changes — it was sealed at
Stage-A and is the list the confirmatory run used — only the description of where
it came from. *Tier-2* is shared bureaucratese, which an
institution can drift toward with no LLM involvement at all. Keeping them
separate is what allows §6.1's thirtyfold Tier-2 rise and §6.2's failure to
establish a Tier-1 differential to be stated as different facts rather than
averaged into one.

**Pre-LLM model surprise**: mean negative log-likelihood under two frozen
pre-2022 models (GPT-2, Pythia-1.4b). This is a deviation measure, not a
detector and not an econometric instrument. PREREG §7 (the NLL eligibility bullet) defers a patch to its computation, and
decision D-4 rules that no NLL number appears in any output until that
regeneration has run; none is reported here. One further declared arm was also
not executed: the A5.4 SAR sensitivity, declared before any document text was read
and reaffirmed at Stage-B close. Decision D-5 records why — SAR is the PAD
series' pre-1997 predecessor and contributes no year inside the 1999–2025 common
window — and the declaration is public inside the frozen SAP at the DOI cited
above.

---

## 5. Analysis design

The design was fixed in two sealed stages: Stage-A preregistration (OSF
`10.17605/OSF.IO/5C9J8`) and a Stage-B statistical analysis plan frozen and
externally timestamped before any confirmatory outcome was computed (Zenodo
`10.5281/zenodo.22098259`).

**How the family was selected.** {P1, P2} is the preregistration's *default*
confirmatory family. A co-primary family was conditional on a deterministic branch
rule over three World Bank policy-document candidates against four conjunctive
gates; none passed, because the gate requiring 25 pre-2023 common years is
unsatisfiable against a comparator frame spanning 24. The fallback in PREREG §11.5
was not triggered on its literal text, and a purposive reading that would have
triggered it was considered and deliberately rejected — reinterpreting a frozen
rule after measuring an inconvenient quantity is the failure the freeze exists to
prevent (decision D-1). Supplement S4 gives the measured gate values and what was
and was not evaluated.

**Panels.** Two confirmatory panels, each a World Bank operational stratum
against the IMF comparator: **P1** = ICR × Article IV, **P2** = PAD × Article IV.
Annual Reports are descriptive only. The comparator is explicitly *non-equivalent*
— institution and genre are confounded — and the preregistration caps
interpretation accordingly in advance rather than after the fact.

**Estimand, and what to call it.** This is a **single-comparator comparative
interrupted time series** — a differential interrupted trend — and not a
difference-in-differences design, which is why we do not use that name. There are
two units, not many; the comparator is non-equivalent by construction; and with
year fixed effects and annual aggregation the model reduces to a regression on
the annual World Bank–IMF log-rate contrast. The frozen design is

    log E[count_it] = year FE + γ·WB + τ·(WB × centred year) + β·(WB × post)
                      + offset log(tokens_it)

with the year centred at the median common year (2012 in both panels) and *post*
= 1 for 2023–2025. **β is not a pre/post contrast.** It is the post-2023
deviation of the World Bank series *from its own fitted differential trend* τ,
which the specification carries across the whole 1999–2025 window. That
distinction does most of the work in §6.2, and PREREG §9 requires τ to be
reported with its interval in every confirmatory output, which is why it appears
in Table 4 rather than in a supplement.

**The identifying assumption, stated plainly.** β is the post-2023 departure from
the World Bank–IMF differential trend *extrapolated linearly* from 1999–2022.
With three post-period observations, β and τ are separated almost entirely by
that functional form; the data do not adjudicate between "a break in 2023" and
"the pre-existing divergence continued". We therefore do not use causal treatment
language anywhere, and §6.4's event study — whose bins impose no trend form — is
the closest the design comes to letting the data speak on this point.

**Figure 4 plots that contrast directly**, with the pre-2023 line fitted and
extrapolated across the post window, because the identification question is
visible in it and not in the raw institutional rates.

**Inference.** PASS-P, a nested bootstrap with B = 9,999 and a wild score
block procedure, Holm-adjusted across the two panels at α = 0.05. One property of
that procedure is worth stating in the design section rather than the results:
with 27 common years and three-year blocks there are nine blocks, so the sign
support has exactly 2⁹ = 512 points. The 9,999 draws sample that support with
replacement; they do not add information beyond it, and the achievable resolution
is 1/512. §6.2 reports the exact enumeration and the sensitivity of the result to
where the block partition begins.

**The four conditions.** A panel supports a claim only if *all four* hold:

- **C1** — Holm-adjusted significance of the differential.
- **C2** — specification stability, in two arms: a negative-binomial refit, and a
  composition-standardized refit over country → region × income groups.
- **C3** — the **concentration guard**: refit with the mandatory guard family
  removed. `underscore` was named as that family **after Stage-A World Bank
  outcomes had been inspected** — the preregistration records that it already
  accounted for 43.48% of post-period hits — and **frozen before the IMF
  contrast and the sealed Stage-B confirmatory run**. That two-stage chronology
  is stated wherever the guard appears; see §6.2.
- **C4** — leave-one-post-year-out influence.

The family verdict is Holm over panels, and it emits a `headline_template` only
when a panel passes. There is no branch in which a failed condition is reported
as a qualified success.

**One deviation from the sealing order, stated here rather than in an appendix.**
PREREG §11.3 places text download *after* the SAP is externally timestamped. The
IMF corpus was retrieved on **2026-08-20**, five days before the SAP freeze of
2026-08-25T15:01:07Z. The ordering was wrong and we do not claim otherwise. What
held is the part that matters for the seal: extraction (`s03`) and every
downstream stage were left unrun until the freeze, and the post-SAP run log opens
with the download stage stamped with the SAP's DOI and SHA-256 on 2026-08-26, so
no feature and no outcome existed before the plan was fixed. Recorded in
`docs/DEVIATION_20260820_stageb_retrieval.md`.

**Mandatory validation outcomes.** Document prevalence (a binomial-logit fit on
whether a document carries any Tier-1 hit) and family breadth (distinct families
per document, binomial with 13 trials), both under the same design with a
delete-one-year jackknife interval, and both required by PREREG §3 to be reported
beside every confirmatory result. A prespecified consistency rule downgrades the
result to count-specific if either opposes the primary with an interval excluding
zero.

**Descriptive companions, prespecified as non-gating.** H-SHARED asks whether the
comparator moved too. Placebo cuts at pre-2023 dates, and an empirical breakpoint
ranking over every admissible cut, ask whether the specification identifies 2023
in particular or fires at any date. A trend-form event study, replacing
`WB:c_year` and `WB:post` with World-Bank × 3-year-bin indicators referenced to
the bin containing the centring year, asks the same question without imposing a
trend form (PREREG §9, sensitivity (a)). Like the placebo, it gates nothing.

**Power, computed before outcomes.** The minimum detectable effect was computed on
the preregistered grid under three companion settings before any confirmatory
number existed, and is reported in §6.3 beside the estimate rather than after it.

---
## 6. Results

### 6.1 RQ1 — the replication gate, then the continuation

D4 makes internal replication a **gate**, not a robustness check: the 1946–2012
series must qualitatively reproduce the pamphlet's published trajectories before
any extension past 2012 is reported. It does.

**Table 3 — assembled Annual Report era means** (`ar_fy_features.csv`, 76 fiscal
years 1947–2024, QC-gated, missing 2000 and 2010). Cells are the **unweighted
mean of fiscal-year rates**; the token-weighted value follows in parentheses.

| Era | Years present | Nominal./100 | Temporal/1k | Acronym/1k | Mgmt/1k | Tier-1/1k | Tier-2/1k |
|---|---|---|---|---|---|---|---|
| 1946–1965 | 19 (1947–1965) | 5.981 (5.989) | **39.963** (38.451) | 15.818 (15.789) | 1.112 (1.135) | 0.009 (0.010) | 0.252 (0.260) |
| 2020–2026 | 5 (2020–2024) | 7.710 (7.722) | **22.971** (27.767) | 39.803 (41.957) | 4.466 (3.949) | 0.094 (0.060) | 7.631 (6.353) |

Temporal anchoring falls by 43%; nominalisation, acronym density (15.8 → 39.8 per
thousand), management vocabulary and the bureaucratese register rise. The pamphlet's qualitative claim survives
independent re-measurement from primary documents.

**The aggregation is stated because it is not innocent.** Weighting by tokens
instead of by year gives a temporal fall of 38.45 → 27.77 — 28%, not 43% —
because recent Annual Reports are far larger and pull the late era toward their
own value. Every direction in the table survives both aggregations; two of the
magnitudes do not. We quote the unweighted figures, which treat each fiscal year
as one observation of institutional practice, and print the weighted ones beside
them so the choice is visible rather than absorbed.

Two features of this agreement are worth stating. It was computed on a corpus
that had since been re-extracted, OCR'd, re-fetched and pruned by ruling, none of
it with this comparison in view; and the series is materially more complete than
when those repairs began — **76 fiscal years against 71, missing years down from
seven to two** (supplement S8).

**The composition result, decomposed — and it is not the result we first
claimed.** Measured over the same fiscal years, the assembled series falls
42.5% (39.96 → 22.97 per thousand) while the whole Annual-Report document pool
falls only 13.8% (35.70 → 30.76). A factor of three. Earlier drafts of this paper
attributed that gap to *unit definition* — whether volumes are concatenated into
fiscal-year units. **That attribution is wrong, and decomposing it produces a
sharper finding.**

**Table 3b — where the factor of three comes from.** Each step is applied to the
previous step's output, over the assembled series' own fiscal years.

| Step | 1946–65 → 2020–26 | change | contribution |
|---|---|---|---|
| 1. whole document pool, token-weighted | 35.70 → 30.76 | −13.8% | — |
| 2. + restrict to files that enter assembly | 39.96 → 22.97 | −42.5% | **−28.7 pp** |
| 3. + concatenate into fiscal-year units | 39.96 → 22.97 | −42.5% | **−0.0 pp** |
| 4. + weight eras by tokens, not by year | 38.45 → 27.77 | −27.8% | +14.7 pp |

**Concatenation contributes nothing at all.** For a token-normalised rate,
assembling documents and taking a token-weighted mean of their individual rates
are the same arithmetic; across all 76 fiscal years the two agree to within
0.0006 per thousand. The operation everyone worries about — the unit of analysis —
is a no-op here.

**The entire factor of three is document selection.** Of the 329 files the
Annual-Report facet returns, 134 enter the assembled series; the other 195 are
sibling-organisation volumes (IFC, MIGA, ICSID) and duplicates, removed by logged
ruling. Those excluded files do not merely add noise: **they trend in the opposite
direction.** Over the assembled series' own fiscal years their rate runs 22.23 per thousand in
1946–65 against 33.53 in 2020–24 — rising — while the Bank's own volumes fall from
39.96 to 22.97. (Both are unweighted means of per-year token-weighted rates,
matched to the same years, which is the aggregation Table 3b and Figure 1 use. An
earlier draft quoted 38.25 for the late window by taking each series over its own
available years, and that figure was inflated by a single fiscal-2025 file — the
same year-set error §8 records us making once already.) Figure 1 plots all three series. Mixing a rising population into a falling
one flattens the decline, and that is the whole mechanism.

The transferable lesson is therefore not the one we started with, and it is more
useful. A diachronic magnitude here is untouched by the unit of analysis and
changed threefold by **what counts as a document of this institution** — a
decision that is usually one clause in a data section, if it appears at all. It
is also a decision with no neutral setting: including sibling-organisation
reports is defensible, excluding them is defensible, and the two defensible
choices differ by a factor of three.

### 6.2 RQ2 — the preregistered differential test

**Figure 2** plots both panels. It is drawn to scale on purpose: twenty-four
pre-period years against three post-period ones is the whole design, and no
amount of statistical machinery makes that asymmetry go away.

**Table 4 — governing verdict** (`s13_validation_battery family`, Holm over two
panels, α = 0.05).

| | P1 (ICR vs IMF) | P2 (PAD vs IMF) |
| --- | --- | --- |
| α_Holm | 0.025 | 0.05 |
| θ (WB:post, log points) | 0.586 | 0.332 |
| PASS-E percentile interval (nominal 95%; coverage not established, §7) | [0.267, 0.921] | [0.017, 0.622] |
| PASS-P *p* | **0.0142** | 0.0929 |
| C1 Holm | passes | fails |
| C2 stability | **fails** (NB2 arm passes, but see §6.2 on what that pass can detect; standardized arm not evaluated) | **fails** (same) |
| C3 concentration guard | **fails** | fails |
| C4 leave-one-post-year-out | **fails** | fails |
| **panel** | **no claim** | **no claim** |
| τ̂ WB differential trend (log pts/yr) | 0.0371 [0.019, 0.055] | 0.0483 [0.033, 0.064] |
| PREREG §9 extrapolation trigger | 0.445 vs β̂ 0.586 — **fires** | 0.579 vs β̂ 0.332 — **fires** |

`family_pass = false`; no passing panel; no headline. Under PREREG §5, failure
of any condition means the panel is reported descriptively with the failed
condition named.

**C3 is the substantive one.** The preregistration fixed `underscore` as the
mandatory concentration guard before the Stage-B data existed, and recorded its
reason in the frozen text: the family was "already known to dominate on the WB
side (43.48% of post-period hits)". That justification is **outcome-informed and
we say so** — the 43.48% comes from Stage-A material whose outcomes had been
seen. The preregistration handles it the only way that works: by naming the guard
in advance and disclosing the basis, rather than choosing it after the fact, and
by closing the adjacent exit at the same time: occurrence count stays primary, so
the analysis cannot later slide to breadth or prevalence — both of which were
nonetheless estimated and are reported below, since foreclosing an axis as the
primary outcome is not the same as leaving it unmeasured. On the Stage-B corpus
the family's post-period share is 36.6% on ICR and 41.1% on PAD — lower than the
figure that motivated the guard, and still large enough to carry the result
single-handed.

Refitting without it, the differential coefficient is **β = −0.067, CI
[−0.509, 0.398]** — the estimand does not merely shrink, it crosses zero with a
wide interval. P2 behaves the same way and more sharply (β = −0.439, CI
[−0.934, 0.051]). The guard was set for this contingency and it caught it, in
both panels, which is the relevant fact: this is not one panel misbehaving.

This must be stated precisely, because a cruder statistic points the other way.
Removing `underscore`, the raw pre/post rate ratios still favour the World Bank.

**Table 5 — the raw ratio and the fitted interaction are different quantities.**
Rates are Tier-1 counts per thousand eligible tokens, pooled within period.

| | all Tier-1 | excluding `underscore` |
| --- | --- | --- |
| P1: WB | ×3.26 | ×2.68 |
| P1: IMF | ×1.16 | ×1.55 |
| **P1: ratio of ratios** | **2.83** | **1.74** |
| P2: ratio of ratios | 2.52 | 1.50 |

The Bank's rate still rises faster than the Fund's. What collapses is the
*modelled differential*, and the reason is **not** the Fund's own rise. The Fund
is already divided out in the ratio of ratios above: its larger proportional
increase once `underscore` is removed (×1.55 against ×1.16) accounts for about
60% of what takes 2.83 down to 1.74 — −0.29 of the −0.49 log-point fall, with the
Bank's own ratio dropping from ×3.26 to ×2.68 supplying the rest — and it is
spent there. It cannot also explain the further fall
to β = −0.067.

**The term that absorbs the rest is τ, the World Bank's own differential trend.**
Refitting the frozen design with τ deleted returns β = 1.042 on P1 — essentially
the raw log ratio of ratios, 1.039 — which locates the entire gap in that one
coefficient. And removing `underscore` does not flatten the trend; it *steepens*
it, from τ̂ = 0.0371 to 0.0489 on P1 and from 0.0483 to 0.0669 on P2. The Bank's
Tier-1 rate has been climbing about 4% a year faster than the Fund's since 1999,
and once the single dominant word family is set aside, the post-2023 elevation is
no longer distinguishable from that long-running trend.

So the honest reading of C3 is sharper than "the effect disappears". It is:
**without one word family, the post-2023 rise is indistinguishable from a
differential trend that has been running since 1999.** A raw ratio, a fitted
deviation from trend, and a pre/post contrast are three different quantities;
only the second was preregistered.

The preregistration also fixed a **non-gating** joint stress, removing
`underscore` *and* `pivotal` together. It was computed and frozen and had not been
reported: β = −0.264, CI [−0.732, 0.239] on P1; β = −0.465, CI [−1.024, 0.092] on
P2. It gates nothing by design, and it points the same way as C3.

**The two secondary sensitivities the plan promised, and what they do to the
picture.** PREREG §4 fixed two reported sensitivities beside the confirmatory
test: HAC(3) OLS on the annual paired log-rate difference, and document-level QML
with institution×year clustering. Neither appeared in earlier drafts of this
paper — an omission found by external review, and a serious one in a study whose
warrant is adherence to a frozen plan. Both are reported here.

**Table 5b — three inference routes, same data** (*p* for the WB×post term).
Bold marks a *p* below that panel's Holm threshold — 0.025 on P1, 0.05 on P2 —
not below 0.05 unconditionally.

| | PASS-P (governing) | HAC(3) annual | doc-level QML |
| --- | --- | --- | --- |
| P1, all Tier-1 | **0.0142** | 0.1617 | 0.0333 |
| P1, excl. `underscore` | — | 0.3984 | 0.8311 |
| P2, all Tier-1 | 0.0929 | **0.0095** | 0.0798 |
| P2, excl. `underscore` | — | **0.0123** | **0.0431** |

**Which panel looks significant depends on the inference route.** PASS-P makes P1
significant and P2 not; HAC(3) does the reverse. And with the guard family
removed, HAC(3) and the clustered document-level fit both return a *significant
negative* on P2 — the Bank falling relative to the Fund. The document-level point
estimates reproduce the confirmatory coefficients exactly (+0.586, −0.067,
+0.332, −0.439), so the disagreement is entirely about standard errors, which is
to say about how much information twenty-seven annual observations actually
carry. PASS-P remains the governing test, as frozen. But a result that changes
panels when the variance estimator changes is the same instability C3 and C4
found, arriving by a third and fourth route.

**The block partition is arbitrary and the *p*-value moves with it.** PASS-P
resamples signs over non-overlapping three-year blocks: 27 years gives nine
blocks, so the test statistic has a support of exactly 2⁹ = 512 sign patterns,
and 9,999 Monte Carlo draws sample that support with replacement rather than
adding information. Enumerating all 512 exactly, at the frozen block origin,
gives P1 = 8/512 = **0.0156** and P2 = 50/512 = **0.0977** — close to the Monte
Carlo values, so the simulation is faithful.

Twenty-seven years in three-year blocks admit exactly three distinct partitions,
and all three are given here. An earlier draft reported one of them, described it
as a two-year shift when it is a one-year shift, and omitted the partition that
moves the other panel.

**Table 5c — exact PASS-P *p* at every available block origin.** Enumeration over
all 512 sign patterns; `tools/block_origin_enumeration.py` regenerates it.

| origin offset | P1 | P2 |
| --- | --- | --- |
| 0 — preregistered | **8/512 = 0.0156** | 50/512 = 0.0977 |
| 1 year | 164/512 = 0.3203 | 78/512 = 0.1523 |
| 2 years | 8/512 = 0.0156 | **18/512 = 0.0352** |

The preregistered origin governs and we do not substitute another. But the table
cuts both ways and both directions belong in it. A one-year shift moves P1's
headline twentyfold, 0.0156 to 0.3203. A two-year shift leaves P1 exactly where
the frozen origin puts it and takes **P2 to 0.0352, below the 0.05 threshold Holm
would set for that panel** — so the partition that would have made the second
panel nominally significant is one an arbitrary earlier choice ruled out. A
convention that can move one panel's *p* by a factor of twenty and carry the
other across its own threshold is not a nuisance; it is a reason the single
reported *p* should not be read as a measurement.

**The engine holds its size under a Poisson null, and not under a mildly
overdispersed one.** An 800-replicate study gives empirical size 0.0512 (P1) and
0.0425 (P2) against a nominal 0.05, and 0.0063 / 0.0050 against 0.01
(supplement S1). That study's null is Poisson: the year-level shock it adds is
drawn once per year and applied to both institutions, and a design carrying
saturated year dummies absorbs it exactly — as this project's own preregistration
had already recorded before the calibration script reintroduced it.

Asked the question the frozen design never asked itself, the answer is worse and
it is against us. The frozen dispersion estimator carries no degrees-of-freedom
correction and is applied to 54 cells fitted with 30 parameters, and it recovers
between a seventh and a twentieth of a dispersion that is really there
(supplement S9, `tools/dispersion_calibration.py`, 1,000 replicates). **At the
dispersion our own data are consistent with, PASS-P's size at a nominal 0.05 is
0.095 on P1 and 0.085 on P2** — close to double.

Two consequences, and both cut the same way. Condition 2's NB2 arm ran with
α̂ = 0.012 (P1) and 0.0005 (P2), so it fitted a model barely distinguishable from
the Poisson primary, and its **pass carries little information**; we report it as
a pass because it is one, and say here what it can detect. And the single *p*
that reached significance, P1's 0.0142, comes from a test that is roughly twice
as easy to trip as its nominal level suggests. **A result the preregistered rule
already declined to confirm is, on this evidence, weaker still.**

The null *p*-value distribution is also **not uniform** — median 0.336 and 0.326 —
which is what a statistic on a 512-point discrete support does. PASS-P is valid
for the accept/reject decision it was built to make; its *p*-value is not a
continuous measure of evidence strength.

**The preregistered extrapolation trigger fires, in both panels.** PREREG §9
fixes that a differential-trend CI excluding zero, with |τ × post-window|
comparable to the WB:post estimate, must be "reported as a first-order
extrapolation threat in the same paragraph as the estimate". Both CIs exclude
zero. Measured from the design's centring year to the post window, |τ × window| =
**0.445 against β̂ = 0.586 on P1**, and **0.579 against β̂ = 0.332 on P2** — on
P2 the trend contribution is larger than the estimate itself. We report it here,
as the preregistration requires: the post-period estimate on these panels is a
short extrapolation off a steep fitted trend, and should be read as one.

**C2 fails on our error, not on the data.** Its NB2 arm passes in both panels
(P1 β = 0.542 against 0.586). Its composition-standardized arm was handed a
stratifier that cannot have cross-institution support, so it reported
`no_common_support_groups` — a message that reads as a fact about the corpora and
is not one. The frozen artifacts are left as they are; a repaired grouping is
reported as a post-hoc sensitivity in §6.5 and is not condition 2, because §6's
income variable is year-matched and ours is current. Supplement S2 gives the
mechanism, the false premise behind it, and why the repair cannot move the
verdict.

**C4** deletes each post year in turn: 2023 → *p* = 0.0103, **2024 → *p* =
0.1815 with β falling from 0.586 to 0.207**, 2025 → *p* = 0.0142. The result
rests on a single year.

**And the year it rests on is not the year the design named.** The prespecified
break is 2023. The World Bank series does not rise there. Tier-1 markers per
thousand tokens, by year:

| | 2021 | 2022 | **2023** | **2024** | **2025** |
| --- | --- | --- | --- | --- | --- |
| WB ICR (P1) | 0.054 | 0.090 | **0.038** | **0.208** | **0.176** |
| WB PAD (P2) | 0.024 | 0.038 | **0.035** | **0.085** | **0.077** |
| IMF Article IV | 0.103 | 0.115 | **0.128** | **0.112** | **0.160** |

In both panels the Bank's rate in 2023 is at or *below* its 2022 value — on ICR
it more than halves — and the increase arrives in 2024.

The same shape appears in the estimand itself (Figure 4). Against a line fitted
through the 1999–2022 contrast and extrapolated forward, P1's 2023 observation
sits **0.54 log points below** the trend, 2024 sits 1.25 above it, and 2025 falls
back to 0.70 above — elevated, but a single displaced year rather than a level
shift, which is what C4 records arithmetically below. That fitted line is an
unweighted least-squares display fit on the continuity-corrected annual contrast
(+0.031 per year on P1, +0.048 on P2); it is **not** the frozen model's τ̂, which
Table 4 gives as 0.0371 and 0.0483. Whatever produced the
post-period rise did not begin at the boundary the design placed it at, which is
visible in Figure 2 and is the same fact C4 detects arithmetically. A
discontinuity story indexed to the public release of general-purpose chat models
in late 2022 does not fit a series that falls through 2023 and jumps a year
later. Diffusion into institutional drafting could plausibly lag by a year; so
could a dozen other things, including changes in what these documents are for.
The design cannot distinguish them, and we do not attempt to.

**The two mandatory validation outcomes.** PREREG §3 requires document prevalence
and family breadth beside every confirmatory result. Prevalence carries the
*opposite* sign to the primary in both panels (P1 β = −0.637, P2 −0.333) and
breadth agrees in sign (+0.228, +0.124); the prespecified count-specific
downgrade did not fire. **That is not reassurance.** The jackknife intervals are
roughly ten times the primary's bootstrap SD, so the rule could scarcely have
fired whatever the truth was — a failure to reject standing in for a pass. Full
intervals in supplement S7.

**H-SHARED, the §5 descriptive companion fixed in PREREG §9: the comparator moved
too.** The IMF's own pre/post change is +0.145 log points, CI [0.003, 0.356] —
modest, and its interval excludes zero **by 0.0029 log points**, after 1,607 of
9,999 bootstrap draws failed to converge and were discarded (`fail_rate` 0.161,
`B_valid` 8,392). Neither figure appeared in an earlier draft, and both belong
next to the claim: an exclusion of zero by three thousandths, on 84% of the
intended draws, is a direction and not a demonstration. And the Fund's pre-period rate is 2.8× the
ICR rate and 5.3× the PAD rate (0.1153 against 0.0416 and 0.0218 per thousand):
the non-equivalence is worse on P2, not uniform across the design. The two
institutions were never on one level, which is what §5 means in calling this a
*non-equivalent* comparator
with institution and genre confounded, and why interpretation was capped in
advance rather than after the fact.

### 6.3 Power, reported with the estimate rather than after it

The minimum detectable effect was computed **before any outcome existed**, at
full precision (1,000 replicates, B = 9,999 nested PASS-P, all three companion
settings the preregistration specifies).

| θ | companion = zero | half | full |
| --- | --- | --- | --- |
| 0.00 | 0.039 | 0.039 | 0.039 |
| **0.60** | **0.159** | **0.158** | **0.216** |
| 1.20 | 0.483 | 0.485 | 0.569 |

**MDE₈₀ is unreachable on the preregistered grid under every setting.** θ = 0.60
is the threshold the design chose for its own branch-selection gate, and it is
almost exactly P1's point estimate of 0.586. At that value, family power is
0.159–0.216 where 0.80 was required.

**Figure 3** places the observed P1 estimate on the curve computed before it
existed. The two nearly coincide, which is the least comfortable image in the
paper.

Two consequences follow, and both are reported rather than chosen. A null here
would be **uninformative**, not evidence of absence. And P1's rejection at
*p* = 0.0142, arriving from a design with roughly 16% power at the observed
effect size, carries severe winner's-curse inflation: the point estimate is a
poor guide to magnitude even if the effect is real.

The binding constraint is structural, not budgetary. Power is governed by a
year-level differential shock (σ_δ = 0.3205 from the preregistration's own
method-of-moments hook); **tripling every panel's documents moves power at
θ = 1.2 from 0.48 to 0.53.** That last comparison comes from a 100-replicate,
B = 999 pilot rather than the full-precision grid above, and we flag it rather
than let it borrow the neighbouring precision claim: Monte Carlo error on the
difference is about 0.07, so the change is not distinguishable from zero. The
conclusion does not turn on it — even the optimistic end of that interval leaves
the design short of 0.80. More sampling is not the remedy. The remedy is
post-period years, of which the design has three.

### 6.4 Breakpoint specificity

The design preregistered two independent checks on whether the specification
identifies 2023 in particular, and they do not agree.

**Table 6 — breakpoint specificity, both checks.** `placebo_sig_frac` is the
share of false pre-2023 cuts that are also significant (lower is better); the
rank places 2023 among all admissible cuts by |b₂| (higher percentile is better).
**The denominator is six** — the placebo years frozen in `config/config.yaml` are
2016 through 2021 — so 1.00 means six of six and 0.33 means two of six. Six is a
small denominator and the reader should weigh the column accordingly; it is
stated here because an earlier draft gave the fractions without it.

| Series | placebo_sig_frac | 2023 rank | of cuts | percentile |
|---|---|---|---|---|
| AR (assembled) | — | 2 | 72 | 98.6 |
| AR (doc-level) | 1.00 | 21 | 74 | 72.6 |
| ICR — P1's WB arm | 1.00 | 10 | 26 | 64.0 |
| PAD — P2's WB arm | 0.33 | 2 | 24 | 95.7 |
| IMF Article IV | 0.67 | 9 | 21 | 60.0 |

(The assembled series has no current placebo figure: `s08` fits document-level
strata, and the assembled series' placebo exists only in a pre-OCR 71-year table
that the post-SAP pipeline does not regenerate. We leave the cell empty rather
than quote a stale number.)

**Read the ICR row, because that is the one the confirmatory result rests on.**
ICR is the World Bank arm of P1 — the only panel that reached significance — and
it is the weakest row on both checks: **all six** false breakpoints tried on
pre-2022 data are also significant, and 2023 ranks tenth of twenty-six admissible
cuts. A
test that fires at any date does not identify 2023. Meanwhile PAD and the
assembled Annual Report series place 2023 second of all candidate cuts — and
neither carries a passing panel. Specificity is strongest exactly where there is
no claim to support, and weakest where there would have been one.

The panel-level placebo at 2016 is cleaner (P1 *p* = 0.1674, P2 *p* = 0.4782).
The checks disagree; all of them are reported.

**The trend-form arm, and its most awkward cell.** PREREG §9 fixes a second
non-gating sensitivity beside the placebo: World-Bank × 3-year-bin indicators in
place of `WB:c_year` and `WB:post`, referenced to the bin holding the centring
year. It asks the same question without imposing a trend form. It ran and
returned `status: ok` with no failure reasons; intervals are PASS-E percentile.

**Table 6b — trend-form event study** (prespecified, non-gating). β against the
2011–13 reference bin.

| Bin | P1 β [CI] | P2 β [CI] |
|---|---|---|
| 1999–2001 | −0.272 [−0.672, 0.154] | −0.581 [−0.960, −0.221] |
| 2002–2004 | +0.029 [−0.483, 0.434] | −0.398 [−0.748, −0.071] |
| 2005–2007 | −0.216 [−0.654, 0.188] | −0.481 [−0.805, −0.140] |
| 2008–2010 | +0.426 [0.074, 0.815] | +0.221 [−0.078, 0.537] |
| 2011–2013 | reference | reference |
| 2014–2016 | +0.102 [−0.270, 0.495] | +0.094 [−0.218, 0.415] |
| 2017–2019 | +0.248 [−0.084, 0.641] | +0.398 [0.116, 0.710] |
| 2020–2022 | **+0.661 [0.319, 1.057]** | +0.359 [0.075, 0.674] |
| 2023–2025 | +1.213 [0.900, 1.598] | +0.938 [0.687, 1.221] |

Two readings follow and the second is not in our favour. First, the divergence is
visible without any line being fitted, and it starts long before 2023: on P2 the
three earliest bins sit *below* the 2011–13 reference with intervals excluding
zero, and the 2020–22 bin sits above it in both panels. The bins are **not**
monotone — P1 runs −0.272, +0.029, −0.216 across the first three — so we describe
the ordering and claim nothing about its shape. Second, and more pointedly: **P1's 2020–22 bin, which is pre-period,
exceeds the headline estimate for the post window itself** (+0.661 against
β̂ = 0.586). A pre-period bin larger than the effect the design was built to
detect carries the same message as C4, the placebo fractions and the 2023 rank,
arriving here by a fourth independent route.

What this arm does *not* do is separate β from τ. Its terminal bin is exactly
[2023, 2025] — the same three post years — so dropping the linear form adds no
post-period information, and §7's identification limitation stands unchanged.

### 6.5 A post-hoc sensitivity: what the standardized arm says once it can run

§6.2 reported that condition 2's composition-standardized arm was supplied the
wrong stratifier. Repairing it is worth doing even though it cannot change the
verdict, because the repaired arm answers a question the failed one only appeared
to answer.

**Table 7 — The composition-standardized arm under both groupings.** The
right-hand rows are a **post-hoc sensitivity, not condition 2**: PREREG §6
requires a year-matched income classification and this one is current.

| Panel | Grouping | π groups | Post token support (WB / IMF) | Floor | Preregistered floors breached |
|---|---|---|---|---|---|
| P1 | `<stratum>:<year>` (as run) | 0 | 0.000 / 0.000 | 0.80 | `no_common_support_groups` |
| P1 | country → region × income (repaired) | 12 | 0.889 / 0.785 | 0.80 | `post_token_support_below_0.80`, `ess_below_floor` |
| P2 | `<stratum>:<year>` (as run) | 0 | 0.000 / 0.000 | 0.80 | `no_common_support_groups` |
| P2 | country → region × income (repaired) | 12 | 0.834 / 0.744 | 0.80 | `post_token_support_below_0.80`, `ess_below_floor` |

The arm remains infeasible either way, and the two reasons have nothing in
common. Under the grouping used, π retained no group at all — the estimator could
not have run whatever the corpora contained. Under the repaired grouping it
retains twelve groups and stops because **the Fund's post-2022 documents
concentrate in country groups where the Bank has little presence**: IMF
post-period token support 0.785 (P1) and 0.744 (P2) against a floor of 0.80, and
a second preregistered floor — effective sample size ≥ half the token mass —
breached in the same two cells at 0.498 and 0.439. Six of the eight institution ×
period cells pass both.

That is a finding about the comparator and it reinforces §6.2's caution from a
second direction: the two post-2022 populations differ in *country* composition
by enough to breach a support floor set in advance, and a differential estimated
across them carries that divergence whether or not it is standardized away. On P1
both margins are narrow (0.785 against 0.80; 0.498 against 0.500), so the
year-matched classification §6 specifies could fall either side and we do not
claim to know which; on P2 they are not. Supplement S5 gives per-cell coverage.

---

## 7. Limitations

Grouped by what they threaten, because a numbered list reads as accumulation
rather than as argument.

**Identification — what the design cannot separate.** The comparator is
non-equivalent: institution and genre are confounded, the Fund's pre-period base
rate is 2.8× the Bank's on P1 and 5.3× on P2, and the Fund also rose. The
estimate is a short extrapolation off a steep fitted trend — over the post window
the trend contributes 0.445 against β̂ = 0.586 on P1 and 0.579 against 0.332 on
P2, larger than the estimate itself — and with three post years β and τ are
separated almost entirely by functional form. Lexical tiers cannot distinguish
direct LLM assistance from human adoption of LLM-popularised vocabulary; we
measure population-level change, not authorship, and no output here claims a
document "is AI-generated". PREREG §9 further fixes that a condition-2 failure
under standardization favours the composition explanation over the LLM-era
reading; condition 2 did fail, and §6.5 shows the two post-2022 populations
diverge in country composition, which we report as the preregistration directs
without treating it as established.

**Measurement — what the corpus does to the estimate.** 192 IMF documents had no
text layer and are OCR'd; every one is pre-period, so extraction method is
collinear with the estimand and cannot be controlled against era. We bounded it
instead where era is held fixed: OCR recovers a median 1.012× the native token count over 20 paired documents with
mean token length within 0.6%. Exclusions are pre-period-weighted — seven
documents leave the panels by language ruling, all ICR, all 2000–2005 — and
removing pre-period documents from one arm is not neutral to a pre/post contrast,
in the direction that favours our own estimate. Within-stratum composition
(region, sector, instrument, template era) remains untreated, which is §6.1's own
lesson not yet applied to §6.2. And RQ1 is an **independent reconstruction, not a
strict replication**: the pamphlet's corpus, features and assembly rules were
never released, so there is no workflow to re-execute; we claim qualitative
directional agreement, and the era figures are means over broad windows rather
than original endpoints.

**Inference — what the machinery can and cannot carry.** The design cannot reach
80% power for any effect in its preregistered grid, which conditions everything
above. Placebo fractions of 1.00 on two strata limit any 2023-specific reading.
The engine is calibrated for size under a Poisson null only, and not at all for
interval coverage. §6.2 and supplement S9 report that PASS-P holds nominal size
when the counts are Poisson and **loses it under mild overdispersion** — 0.095
against a nominal 0.05 on P1 at the dispersion the data are consistent with —
because the frozen dispersion estimator recovers roughly an eighth of what is
there at 30 parameters on 54 cells. We report no coverage study for the PASS-E
intervals at all, which is why Table 4 labels them nominal. A reader treating the
apparatus as reusable should establish both first, should give the dispersion
estimator a degrees-of-freedom correction, and should note that the null
*p*-value distribution is not uniform.

**Provenance and access.** 748 of 2,738 documents (27.3%) in the Stage-B World
Bank sample had their outcomes inspected at Stage-A. The IMF half of the contrast
had never been computed before this analysis, so the interaction itself was
unseen, but the exposure belongs beside the estimate rather than in an appendix.
The comparator corpus cannot be redistributed; §9 gives the route by which it can
be obtained from the publisher and verified against our hashes.

---

## 8. Discussion

### What the reconstruction establishes

The pamphlet's central claim survives independent re-measurement from primary
documents, which is not nothing: *Bankspeak* has been cited across the digital
humanities and international-organisation literatures for a decade on a corpus
nobody could inspect. What we offer is a **reconstruction, not a replication**
(§7): the original features and assembly rules were never released, so there is no
workflow to re-execute and no numerical target to hit. The agreement is
qualitative and directional, and that is the strongest form available when the
predecessor's method is unavailable.

Extension through fiscal 2024 adds the part the pamphlet could not have: the
drift did not stop when the series did. And the reconstruction earns its keep a
second time by making the corpus-selection result visible at all — that finding
exists only because rebuilding forced a decision about what counts as an Annual
Report, and then made both answers computable.

### Three method results, and how far they travel

Three results here are about method rather than about the World Bank, and each
was found by measurement rather than suspicion:

- **Document selection triples a diachronic magnitude; the unit of analysis
  changes nothing.** Assembled and pool Annual-Report series give a 43% and a 14%
  decline over the same fiscal years, and decomposition assigns the entire gap to
  which files are included — the excluded sibling-organisation volumes trend
  *upward* while the Bank's own volumes fall. Concatenation into fiscal-year
  units contributes 0.0 percentage points, because for a token-normalised rate it
  is arithmetically identical to a token-weighted mean. We claimed the opposite in
  two earlier drafts, and an unmatched year set briefly made the pool series
  appear to rise at all. Both errors are instructive in the same direction: the
  operations that sound methodologically weighty can be inert, and the ones
  recorded in a single clause of a data section can be worth a factor of three.
- **The source's own plain text is not safer than your extraction.** D9 preferred
  server-side text precisely to avoid extraction noise; 70 documents arrived with
  word spacing destroyed, concentrated in 2003–2009 and absent after 2010, and
  the PDF path we had distrusted was clean (0 of 437 against 70 of 2,688, over
  the pre-freeze pool). In the worst case whole-word matching missed 78% of its
  hits.
- **A recorded ruling is not an applied one.** Twice, an exclusion or an
  extraction remedy was written to a ledger, satisfied its gate, and never
  reached the corpus. Both were caught because a downstream count disagreed with
  an upstream one, not because anything raised an error.

### What a bounded negative is worth

The literature on LLM-associated vocabulary has grown quickly and reports
positives almost exclusively. Our design was built to be able to fail, and it
did: a guard fixed before the comparison existed removed a single word family and the
preregistered estimand crossed zero; a leave-one-out check showed the result
resting on one year; a comparator chosen to absorb sector-wide drift moved in the
same direction as the treated arm.

None of those checks would have been reached had the analysis stopped at
*p* = 0.0142. All three were specified in advance, which is the only condition
under which their verdicts mean anything.

The case result worth carrying away is narrower than "LLMs did or did not change
institutional prose", and more useful: **a nominally significant aggregate
lexical break can be produced here by one word family, one post-period year, and
one block origin, while a sealed multi-condition rule correctly withholds the
claim.** Each of those three is a routine choice that a study without a frozen
decision rule would make silently and defensibly. We do not know how often that
combination arises elsewhere; we know it arose here, and that a design without
the guard would have reported the *p*-value.

### What we do not claim

We do not claim the World Bank's prose was unaffected by LLMs. We claim that this
design, with this corpus and this comparator, cannot answer that question at the
evidentiary standard it set for itself, and that the honest report of such a
design is its bound. The reconstructed series stands on its own.

---

## Figures

All four regenerate from `data/` via `tools/make_paper_figures.py`; PNG and PDF
in `docs/figures/`.

- **Figure 1** — `fig1_composition`. Temporal anchoring per thousand tokens over
  common fiscal years, in three panels: the assembled series (the Bank's own
  volumes), the whole document pool, and the 195 files the assembly excludes.
  The excluded files trend upward while the assembled series falls, which is what
  produces the factor of three.
- **Figure 2** — `fig2_panels`. Tier-1 markers per thousand tokens by
  institution, both confirmatory panels, with the prespecified 2023 break marked.
- **Figure 3** — `fig3_power`. The preregistered power curve under three
  companion settings, with the 0.80 requirement and the observed θ̂ = 0.586.
- **Figure 4** — `fig4_contrast`. The estimand itself: the annual World Bank–IMF
  log-rate contrast for both panels, with the pre-2023 trend fitted and
  extrapolated across the post window. Drawn without a confidence band, because
  the band would come from the frozen bootstrap and this is a display, not a
  second inference.

---

## 9. Data and code availability

**Preregistration.** Stage-A OSF `10.17605/OSF.IO/5C9J8`. Stage-B analysis plan
Zenodo `10.5281/zenodo.22098259`, sha256 `4aa12279…2677`, timestamped
2026-08-25T15:01:07Z, before any outcome reported here was computed.

**Code and design record.** `10.5281/zenodo.22168611` (concept DOI
`10.5281/zenodo.22152944`, which always resolves to the latest version), archived
from
`github.com/alicetinkaya76/bankspeak-continued` at release v1.2.0: the frozen
inference engine, the validation battery, the full pipeline, the 357 tests that
release carries — 346 pass in the archive and 11 skip, each naming the licensed
or deposited input it needs — every preregistration draft and amendment,
decisions D-1..D-13,
both deviation records, and the generators that produce every table and figure
here. Code MIT; documents CC BY 4.0.

**Evidence deposit.** Frames, frozen samples, raw World Bank API captures, power
curves, quality flags, per-document exclusion ledgers, panel cells, both
validation batteries and the family verdict. **Not yet deposited at the time of
writing: DOI to be inserted here before publication.** It is built by
`tools/prepare_zenodo_deposit.py`, which also writes the SHA-256 manifest listing
every IMF-derived file by hash without depositing its bytes.

**Access to the comparator corpus.** The permission of 2026-08-20 governs bulk
retrieval and redistribution, not access: the IMF publishes these reports and any
reader can obtain them from the Fund's website by country and report number, or
by the DOI, which identifies the document and resolves to its eLibrary landing
page. Automated collection is another matter and we report it as we met it. The site is
bot-protected and its failures are silent: an absent report redirects to an error
page served at **HTTP 200 with `text/html`**, so a status code alone reports
success for a document that is not there — a byte-checked probe of 20 sampled documents on 2026-08-29 found the static path serving a real PDF for 16 and an error page for four, and the DOI resolving to a document for none (`data/meta/imf_access_probe.json`). Our own retrieval needed a
documented ladder in which **705 documents came from static paths, four through a
media tree, one through a bounded verification-gated sequence and 354 through a
public web archive**, a split the probe reproduces
(`tools/retrieval_route_tally.py`). `data/meta/imf_document_index.csv` lists all
1,064 by report number, year, country, DOI and SHA-256, so a reader who obtains a
document by any route can hash it against that index and confirm byte identity
with the copy analysed here. Seven carry no DOI and are located by country and
report number.

The index carries **no title and no IMF URL**, which is the line this study draws
throughout: the catalogue frame with every title and link is verbatim IMF content
and is not published, while a report number, a DOI and a hash we computed are
derived non-substitutive outputs of the kind the permission allows.

**Acknowledgement.** Contains IMF Staff Country Reports retrieved from www.imf.org
under written permission from the International Monetary Fund (2026-08-20). The
IMF is not responsible for any analysis or conclusions drawn from these documents.
World Bank content is public disclosure under its Access to Information Policy.

---

## References

*Audited by `tools/audit_citations.py` on 2026-08-30: all 26 entries parsed,
23 resolved against Crossref with matching first author and year, three
conference papers carry stable proceedings URLs in place of a DOI, and every
entry is cited in the body with no in-text citation missing from the list.
The Lopez Bernal (2017) Crossref record is the online-first one and carries no
print pagination; the printed citation here is the fuller one.*

**Bankspeak and institutional discourse.** Moretti, F. & Pestre, D. (2015).
Bankspeak: The language of World Bank reports. *Literary Lab Pamphlet 9*; also
*New Left Review* 92:75–99. DOI 10.64590/167. · Barnett, M. & Finnemore, M.
(1999). The politics, power, and pathologies of international organizations.
*International Organization* 53(4):699–732. DOI 10.1162/002081899551048. ·
Cornwall, A. & Brock, K. (2005). What do buzzwords do for development policy?
*Third World Quarterly* 26(7):1043–1060. DOI 10.1080/01436590500235603. · Mosse,
D. (2004). Is good policy unimplementable? *Development and Change*
35(4):639–671. DOI 10.1111/j.0012-155X.2004.00374.x.

**LLM-associated lexical shift.** Kobak, D. et al. (2025). *Science Advances*
11(27):eadt3813. DOI 10.1126/sciadv.adt3813. · Liang, W. et al. (2024). Monitoring
AI-modified content at scale: a case study on the impact of ChatGPT on AI
conference peer reviews. *Proceedings of the 41st International Conference on
Machine Learning*, PMLR 235:29575–29620.
https://proceedings.mlr.press/v235/liang24b.html
· Liang, W. et al. (2025a). *Nature
Human Behaviour* 9:2599–2609. DOI 10.1038/s41562-025-02273-8. · Liang, W. et al.
(2025b). *Patterns* 6(12):101366. DOI 10.1016/j.patter.2025.101366. · Juzek, T. &
Ward, Z. (2025). *COLING 2025*:6397–6411.

**Detection and critiques.** Gehrmann, S. et al. (2019). *ACL system
demonstrations*. DOI 10.18653/v1/P19-3019. · Ippolito, D. et al. (2020). *ACL*.
DOI 10.18653/v1/2020.acl-main.164. · Mitchell, E. et al. (2023). DetectGPT:
zero-shot machine-generated text detection using probability curvature.
*Proceedings of ICML*, PMLR 202:24950–24962.
https://proceedings.mlr.press/v202/mitchell23a.html · Liang, W. et al. (2023). *Patterns* 4(7):100779. DOI
10.1016/j.patter.2023.100779. · Weber-Wulff, D. et al. (2023). *International
Journal for Educational Integrity* 19:26. DOI 10.1007/s40979-023-00146-z. · Wu,
J. et al. (2025). *Computational Linguistics* 51(1):275–338. DOI
10.1162/coli_a_00549.

**Interrupted time series and structural breaks.** Wagner, A. K. et al. (2002).
*Journal of Clinical Pharmacy and Therapeutics* 27(4):299–309. DOI
10.1046/j.1365-2710.2002.00430.x. · Lopez Bernal, J. et al. (2017).
*International Journal of Epidemiology* 46(1):348–355. DOI 10.1093/ije/dyw098. ·
Lopez Bernal, J. et al. (2018). *IJE* 47(6):2082–2093. DOI 10.1093/ije/dyy135. ·
Newey, W. K. & West, K. D. (1987). *Econometrica* 55(3):703–708. DOI
10.2307/1913610. · Bai, J. & Perron, P. (1998). *Econometrica* 66(1):47–78. DOI
10.2307/2998540.

**IGO document studies.** Broad, R. (2006). *Review of International Political
Economy* 13(3):387–419. DOI 10.1080/09692290600769260. · Vetterlein, A. (2012).
*New Political Economy* 17(1):35–58. DOI 10.1080/13563467.2011.569023. · De
Francesco, F. & Guaschino, E. (2020). *Policy and Society* 39(1):113–128. DOI
10.1080/14494035.2019.1609391.

**Reproducibility and corpus design.** Biber, D. (1993). *Literary and Linguistic
Computing* 8(4):243–257. DOI 10.1093/llc/8.4.243. · Sandve, G. K. et al. (2013).
*PLOS Computational Biology* 9(10):e1003285. DOI 10.1371/journal.pcbi.1003285. ·
Wilkinson, M. D. et al. (2016). *Scientific Data* 3:160018. DOI
10.1038/sdata.2016.18.

