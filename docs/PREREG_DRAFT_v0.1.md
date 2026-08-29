# PREREG — Comparator-round confirmatory analysis (DRAFT v0.1, 2026-08-09)

**Status: DRAFT, circulated for external critique (third-eye round 3, Role 2).** After one
revision round it will be FROZEN by a dated commit BEFORE any IMF document metadata or text
is downloaded. Post-freeze deviations must be logged in `DESIGN_RATIONALE.md` (dated, with
reason); any deviation demotes the affected result from confirmatory to exploratory.
Rationale: O4/O8 of the first-round review and action items 2 and 5 of the round-2 review
require the comparator estimand and multiplicity family to be fixed before results are seen.

## 1. Design

Comparative interrupted time series: two institutions (World Bank, IMF), harmonized genre
panels, document-level counts. The IMF is the D3 comparator: no leadership change at the
2023 cut (Georgieva 2019–), so the WB-specific leadership/style-guide confound is absent
there; both institutions share the ChatGPT-era exposure.

**Panels (never pooled across genres, per D1):**

- **P-O/ICR (primary):** WB Implementation Completion and Results Reports (1994–2026) vs
  IMF Article IV staff reports (country surveillance). Article IV is the closest available
  operational analog; the genre mismatch is acknowledged and identification relies on
  within-genre change over time within each institution, differenced between institutions
  — not on cross-genre level comparisons.
- **P-O/PAD (secondary):** WB Project Appraisal Documents (1996–2026) vs the same IMF
  Article IV series.
- **P-A (secondary/descriptive):** WB assembled Annual-Report fiscal-year units
  (1947–2024, QC-gated, n=71, n_post=2) vs IMF Annual Reports assembled by the same s10
  logic under the identical frozen QC gate. Reported with n_post disclosed; never primary,
  because two post-cut observations cannot support confirmatory inference.

Primary-panel choice, stated in advance: ICR carries the largest post-2022 Tier-1 mass
(417 hits) and the highest share of year-cells passing the D7 power gate; PAD is smaller
(338 hits) and AR is n_post-limited (20 hits over two units).

**IMF harvest discipline:** same frozen-sampling mechanism (year-stratified, cap 40/yr,
seed 20260806, `sampling_version` bump, write-once CSV, append-only SHA256 manifest),
txturl-first ingestion where the source offers text, extraction method logged per document
(D9/D10 applied unchanged).

## 2. Primary confirmatory hypothesis (exactly one)

**H1.** In P-O/ICR, the WB×post interaction on the confirmatory Tier-1 family rate is
positive.

**Model M1 (document level):** Poisson quasi-maximum likelihood,

    count_d ~ institution + year + post + institution×post
              + extraction_method + offset(log tokens_d)

with `post = year ≥ 2023` (prespecified; no scan feeds the confirmatory cut). Inference:
cluster-robust by institution×year, with wild cluster bootstrap (Rademacher weights) for
the interaction, given the small number of time clusters; NB2 re-estimation as
overdispersion sensitivity. `year` enters linearly; a restricted-cubic-spline variant is
prespecified as sensitivity S-M1a, not as the primary.

**Confirmatory lexicon (frozen; Appendix A):** the 13 Tier-1 lemma families currently in
`config/config.yaml`, collapsed so that morphological variants count once per family
(delve, underscore, showcase, pivotal, intricate, meticulous, boast, commendable, realm,
testament, tapestry, seamless, multifaceted). No family may be added or removed after
freeze; family collapse is the response to the round-2 concentration finding (underscore
43.5% of post-period form-level mass). The current index remains reported, but only as
exploratory.

**Decision rule (all three required for any confirmatory claim):**
1. **Pretrend gate:** the institution×year interaction estimated on pre-2023 data only
   does not reject at α = 0.10 (equivalence-style reporting: estimate with CI, not only
   the p-value). If the gate fails, all comparator results are reported descriptively and
   no confirmatory claim is made.
2. Wild-cluster-bootstrap p for the H1 interaction < 0.05.
3. Sign and order of magnitude stable under NB2 and under the composition-standardized
   variant (Section 5).

Claim vocabulary on success remains the D2 commitment: "WB-specific post-2022 increase
consistent with documented enterprise LLM adoption" — never authorship, never causality.

## 3. Secondary confirmatory family (Benjamini–Hochberg FDR, q = 0.05; enumerated now)

Exactly four members; BH is applied within this family and nowhere else at confirmatory
level:

- **S1.** P-O/PAD: WB×post interaction, model M1.
- **S2.** P-A: WB×post interaction under level-only specifications on both assembled
  series (n_post disclosed; interpretation capped at descriptive-plus).
- **S3.** P-O/ICR: WB×post interaction on reference-model NLL, Pythia-1.4b (document-level
  mean NLL as outcome, OLS analog of M1 with the same clustering/bootstrap).
- **S4.** As S3 with GPT-2.

## 4. Exploratory analyses (labeled as such; BH q = 0.05 within enumerated blocks)

Classic Bankspeak features × panels; deduplicated breakpoint scans (unique pre/post
designs only; trimmed candidate interval with min post ≥ 3; sup-Wald/QLR with bootstrap
critical values per Andrews 1993, Bai–Perron 1998/2003); explicit model comparison
no-change vs level step vs slope change vs ramp (BIC + bootstrap LR); Tier-2 series;
per-family decomposition with absolute rate differences, document prevalence, HHI;
missingness-by-year×format model; assembled-unit NLL panel.

## 5. Composition standardization

Where WB metadata enrichment yields region / sector / instrument: (a) M1-adj adds them as
covariates; (b) direct standardization reweights WB and IMF document cells to the pooled
pre-2023 composition as a robustness estimate. A template-era indicator is defined from
documented format changes and frozen before estimation. If enrichment fails for a field,
that field is dropped symmetrically for both institutions and the failure is logged.

## 6. Frozen inputs carried over unchanged

- Extraction-quality gate: min 5,000 tokens AND min 0.15 stopword share, applied to IMF
  assembled units exactly as to WB units, thresholds untouched (the round-2 requirement
  that the rule transfer without recalibration).
- Reference models: GPT-2 and Pythia-1.4b. **Amendment at freeze:** pin immutable HF
  revision hashes, not `revision: main` — "main" is a movable pointer and does not meet
  the D10 artifact discipline.
- Seed 20260806; `sorted()` iteration; write-once sampling artifacts.

## 7. Outcomes that would count against the LLM-era reading (stated in advance)

A similar or larger IMF increase; the interaction vanishing under composition
standardization; the interaction confined to one extraction method or template era;
pretrend-gate failure; the interaction driven by 2023 alone (leave-one-year-out on the
interaction); the confirmatory family rate rising only through a single lemma family
(leave-family-out on the interaction).

## 8. Out of scope

Mechanism and authorship attribution (D2); WB press releases (Phase 2, D8); any UNGDC
material (hard firewall).

## Appendix A — Confirmatory family list to be frozen

The 13 families above, expanded to the exact word forms in `config/config.yaml`
`markers.tier1` at the freeze commit; the commit hash and the verbatim list are pasted
here at freeze time and never edited afterward.
