# Third-eye LLM review prompt (paste everything below the line into the external model)

Purpose: independent pre-submission review — venue fit, framing, literature, and
anticipated objections. Numbers below are final, regenerated from code; do not
recompute them. Every suggested reference will be verified against Crossref before
use; the prompt therefore demands DOIs and confidence labels.

---

You are acting as an experienced, skeptical journal editor and methods reviewer in
computational social science / information science. Review the study described
below and answer the five tasks at the end. Be blunt; optimize for what real
reviewers at SSCI/SCIE journals would say, not for encouragement.

## The study

**Title (working).** Bankspeak, Continued: A Genre-Stratified Diachronic Corpus of
World Bank Prose (1946–2026) and a Measured Post-2022 Stylistic Discontinuity.

**What it does.** Extends Moretti & Pestre's "Bankspeak" (Stanford Literary Lab
Pamphlet 9, 2015) time series of World Bank institutional prose from 2008 to 2026
(RQ1), and tests whether a stylistic discontinuity appears after 2022, coinciding
with documented enterprise LLM adoption at the Bank (RQ2). Solo author,
computational-methods profile. Vocabulary is deliberately constrained: the paper
claims a "measured discontinuity consistent with…", never that any document "is
AI-generated" and never causality.

**Corpus.** Three genre strata sampled separately and never pooled (genre-mixture
artifacts are shown to be real in our data): (a) Annual Reports assembled into 73
fiscal-year units 1947–2024, with IFC/MIGA/ICSID sibling-organization reports
excluded by logged rules; (b) Project Appraisal Documents (1996–2026, capped 40
docs/year, N=1,201 sampled); (c) Implementation Completion and Results Reports
(1994–2026, capped 40/year, N=1,286). Downloaded 2,753/2,818 sampled documents
(97.7%; misses are logged with reasons), ~70M word tokens. Reproducibility:
write-once frozen sampling CSVs, append-only SHA256 manifest, pinned environment,
fixed seed; every reported number regenerates from code.

**Measures.** (i) The pamphlet's classic features re-operationalized:
nominalization density, acronym density, "and" frequency, temporal-anchoring rate,
mean sentence length, MATTR, management-vocabulary rate. (ii) Two-tier lexical
markers with recorded provenance: Tier-1 = strong LLM-associated words (delve,
underscore, showcase, pivotal…; from the excess-word literature), Tier-2 =
bureaucratese shared by Bankspeak and LLM style (foster, leverage, robust,
resilient…). The tier split separates "more Bankspeak" from a candidate LLM
fingerprint. (iii) Perplexity under two frozen pre-ChatGPT instruments (GPT-2;
Pythia-1.4b), locally pinned — API models are never used as instruments.

**Analysis.** Interrupted time series per stratum × feature: segmented OLS with
Newey-West SEs, breakpoint 2023-01-01, pre-trend slopes reported, placebo
breakpoints 2016–2021 fitted on pre-2022 data only. A power gate (two-rate Poisson
test) requires ≥0.8 power before any Tier-1 claim: 41,981 tokens/group at
p0=2e-5 vs p1=2e-4; ICR/PAD year-cells all pass (≈0.7–1.5M tokens/cell); thin
early Annual-Report years are year-binned.

**Findings (final).**
1. Internal replication (gate for RQ1): on the assembled AR series the pamphlet's
   1946–2012 trajectories reproduce qualitatively — temporal anchoring falls
   ~40→~24 per 1k tokens, nominalizations, acronyms, "and", and management
   vocabulary rise. (Unassembled doc-level AR series showed the OPPOSITE temporal
   trend — a genre/sibling composition artifact we document as a methods point.)
2. Bankspeak inflation continues to 2026: Tier-2 rate on assembled AR rises from
   ~0.25 (1946–65) to ~9.1 per 1k (2023–26).
3. Tier-1 shows a 2023 level shift in all three series: assembled AR +0.102/1k
   (HAC p<1e-36), ICR +0.056 (p<1e-7), PAD +0.027 (p=0.01). HOWEVER, placebo
   breakpoints are also frequently "significant" on pre-2022 data
   (placebo_sig_frac 0.5–1.0): the placebo test does NOT cleanly isolate 2023.
   We report this as a specificity limitation, prominently.
4. Convergent instrument: mean NLL under BOTH frozen models rises from 2019–22 to
   2023–26 in ICR and PAD (e.g., Pythia ICR 2.43→2.53) — new prose is more
   surprising to pre-LLM instruments — while the AR series does not show this.
5. Known confounds, stated in the design: Ajay Banga's presidency begins June
   2023; style-guide and thematic pivots co-move. An IMF comparator series
   (Article IV consultations / IMF Annual Reports; same features) is REQUIRED by
   our own design before RQ2 claims are published, and is scheduled; the current
   RQ2 material is complete but embargoed until that comparator exists. Assume in
   your review that the IMF series will exist.

**Venues under consideration.** Government Information Quarterly (primary;
information-management framing) and Information Processing & Management
(alternate; measurement-methodology framing). Target submission: March 2027.

## Your five tasks

1. **Venue fit.** Rank 6–10 SSCI/SCIE-indexed journals for this paper (include
   GIQ and IP&M in the ranking; consider also e.g. Digital Scholarship in the
   Humanities, Quantitative Science Studies, Language Resources and Evaluation,
   Applied Corpus Linguistics, Policy & Internet, Big Data & Society, PLOS ONE).
   For each: fit rationale in 2–3 sentences, the framing that venue rewards,
   expected first-decision latency if you know it, and indexing/quartile as far
   as you know it — flag every indexing/quartile statement as "verify on
   Clarivate/JCR", do not assert it as fact.
2. **Framing.** Propose 3 title options and a 150-word abstract skeleton for the
   top venue. State which single contribution should lead (corpus? replication?
   discontinuity? measurement discipline?) and why.
3. **Literature.** Suggest 15–25 references grouped by module: (a) Bankspeak /
   organizational-institutional discourse; (b) LLM lexical fingerprints and
   excess-vocabulary estimation; (c) AI-text detection and its critiques
   (especially perplexity-based); (d) interrupted time series methodology;
   (e) World Bank / IGO document studies; (f) reproducibility in corpus work.
   HARD RULE: only cite works you are confident actually exist. For each, give
   authors, year, venue, and DOI if you know it, plus a confidence label
   (high/medium). If you are not sure a paper exists, say so explicitly or omit
   it. Fabricated or "reconstructed" citations are worse than gaps: every entry
   you output will be checked against Crossref, and hallucinated entries
   discredit the rest of your review.
4. **Anticipated objections.** List the 8–10 strongest reviewer objections
   (methodological and conceptual), each with: how the current design already
   answers it, or what additional analysis/text would be needed. Include at
   minimum: placebo non-specificity of the Tier-1 break; Banga/style-guide
   confound; word-list circularity (Tier-1 lists derived from LLM output could
   flag human adopters of LLM-popularized words); frozen-model perplexity as
   instrument validity; genre-composition drift within strata; single-institution
   generalizability; the 2.3% download residue.
5. **Cheap additions.** Name up to 5 analyses that would materially strengthen
   the paper at low cost given the existing per-document feature tables (e.g.,
   robustness variants, alternative breakpoints, document-length controls,
   median-based aggregation against outliers). For each: what it buys, and what
   result pattern would weaken the paper.

Answer in English, in the order above, with clear headings. Do not praise the
study; review it.
