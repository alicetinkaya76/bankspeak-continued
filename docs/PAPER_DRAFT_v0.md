# Auditing Institutional Prose in the LLM Era: Genre Composition and Stylistic Change at the World Bank, 1947–2026

**Draft v0.2 (2026-08-07).** Revised after the third-eye editorial review: the paper now leads
with genre-aware measurement discipline; "discontinuity" framing replaced by "post-2022
increase"; assembled-AR series regenerated under a prespecified extraction-quality gate;
AR breakpoint inference reduced to a level-only specification with post-break support
disclosed. All numbers regenerate from `src/s11_paper_artifacts.py` + `src/s12_robustness.py`.
`[REF: …]` slots are placeholders pending Crossref verification. RQ2 claims remain embargoed
until the IMF comparator (D3).

---

## Abstract (skeleton, ~150 words)

Public institutions increasingly use generative AI, yet their archives rarely disclose when
prose is machine-assisted. This creates a measurement problem: apparent stylistic change may
arise from changing document composition rather than writing practice. We construct a
reproducible, genre-stratified corpus of World Bank prose — 71 quality-gated Annual Report
fiscal-year units (1947–2024), 1,270 Implementation Completion and Results Reports
(1994–2026), and 1,160 Project Appraisal Documents (1996–2026); ~70 million tokens. We first
replicate historical Bankspeak trajectories and show two failure modes that reverse or
distort trends in naive designs: sibling-organization/volume mixture, and defective
extractions that survive provenance controls. We then triangulate post-2022 change with
provenance-tracked lexical tiers, frozen pre-ChatGPT language models, segmented regressions,
empirical breakpoint ranking, and a matched IMF comparator. `[Insert comparator-adjusted
result.]` Indicators do not move uniformly; maximal break statistics cluster in 2022–2025,
consistent with ramped adoption rather than a single break. The contribution is a
genre-aware audit design for institutional text change — not document-level AI detection or
causal attribution.

## 1. Introduction

- Lead contribution: a genre-aware, provenance-preserving **audit design** for measuring
  institutional text change, demonstrated on 79 years of World Bank prose. The corpus is
  infrastructure; the replication is a validation gate; the post-2022 finding is an
  application whose interpretation remains conditional on the IMF comparator.
- Motivating measurement lesson (previewed): the same archive yields opposite historical
  conclusions depending on composition handling (Section 6.1), and provenance controls alone
  do not guarantee measurement validity (Section 3.3).
- RQ1: does the Bankspeak trajectory continue 2008→2026? RQ2: does prose change after 2022,
  coinciding with documented enterprise LLM adoption [REF: WB IEG GPT-experiment note;
  enterprise "mAI" reporting — verify primary sources]?
- Vocabulary commitment: "post-2022 increase", "consistent with", "convergent evidence";
  never "is AI-generated", never causal attribution.

## 2. Related work `[TO-WRITE — verified reference list in preparation]`

Modules: (a) Bankspeak and organizational/institutional discourse; (b) LLM-associated
lexical shifts and excess-vocabulary estimation; (c) AI-text detection and its critiques —
the study performs population-level change measurement, not document classification;
(d) interrupted time series and structural-break methodology (prespecified intervention vs.
unknown-break estimation); (e) World Bank / IGO document studies; (f) reproducibility and
corpus representativeness.

## 3. Data

### 3.1 Source and sampling
World Bank Documents & Reports open API; English-only. Three genre strata, sampled and
analyzed separately, never pooled. Year-stratified random sampling (seed 20260806), caps of
40 docs/year for operational genres; Annual Reports uncapped. Write-once frozen sampling
CSV; append-only SHA256 manifest; pinned environment.

**Table 1 — Corpus composition (regenerated; `T1_corpus.csv`).**

| Stratum | Sampled | Downloaded | Coverage | Residue (logged) | Span | Tokens |
|---|---|---|---|---|---|---|
| Annual Reports (doc-level) | 331 | 323 | 97.6% | 8 | 1946–2025 | 9,986,888 |
| ICRs | 1,286 | 1,270 | 98.8% | 16 | 1994–2026 | 23,625,063 |
| PADs | 1,201 | 1,160 | 96.6% | 41 | 1996–2026 | 36,634,104 |

Total: 2,753/2,818 documents (97.7%), ~70.2M tokens. Every miss is logged with its error
(62 server-side 403/404-class errors; 3 records advertise no retrievable URL); 2,747/2,753
extracted documents (99.78%) have nonzero tokens. Server-side plain text covers 89.5% of the
analysed corpus (≥88.5% in every decade); within the Annual-Report stratum the share drops
to 56% in the 2020s; extraction method is logged per document.

### 3.2 Annual Report assembly
The Annual Report facet also returns sibling-organization reports (IFC, MIGA, ICSID),
excluded by logged per-document rules; remaining volumes are deduplicated by report/volume
number and concatenated per fiscal year (135 documents adjudicated in-series, 130 with
retrieved text; 7 borderline titles individually adjudicated and logged).

### 3.3 Extraction-quality gate (provenance ≠ validity)
An external audit of our own release caught two defective assembled units that all
provenance controls had passed: FY2002 (12 tokens — cover-sheet-only server extractions)
and FY2007 (46,723 tokens but function-word share 0.9% — a table/heading dump). We
therefore impose a prespecified per-unit gate — ≥5,000 tokens and ≥15% function-word share
(legitimate units: ≥17k tokens, ≥20% share; defective units: ≤0.9%) — yielding **71
fiscal-year units, 1947–2024** (gaps and exclusions logged in `ar_unit_qc.csv`). The
methodological point generalizes: a frozen manifest guarantees provenance, not measurement
validity; quality gates must be part of the audit design.

## 4. Measures
As v0.1: classic Bankspeak features; two-tier lexical markers with per-word provenance
(Tier-1 LLM-associated; Tier-2 shared bureaucratese); mean NLL under two frozen pre-2022
models (GPT-2, Pythia-1.4b) — termed **pre-LLM model surprise**, a deviation measure, not a
detector and not an econometric instrument.

## 5. Analysis design

- **ITS, prespecified breakpoint 2023** per stratum × feature: segmented OLS with HAC(2)
  SEs; pre-trend slopes reported. **Annual-Report series: level-only specification**
  (`y = b0 + b1·t + b2·post`) is primary — with only two post-break years (2023–2024) a
  post-break slope is not identified; n_post is disclosed in every table.
- **Placebo cuts** (2016–2021, pre-2023 data only) and — added after review — **empirical
  breakpoint ranking**: the same specification fitted at every admissible cut (≥5 pre-years,
  ≥2 post-years); 2023's statistic is ranked against the full candidate distribution.
- **Power gate**: 41,981 tokens/group for 0.8 power (p0=2e-5, p1=2e-4). ICR/PAD year-cells
  typically ~0.6–1.5M tokens; all pass except PAD 1996 (16k); 22/144 doc-level cells below
  0.8 (21 AR years + PAD 1996); 27/71 assembled AR years below the token gate — all
  below-gate cells year-binned for Tier-1 inference.
- **Robustness battery** (`s12`): leave-one-year-out influence; median/10%-trimmed/mean
  aggregation; Tier-1 per-word decomposition with leave-word-out contrasts.

## 6. Results

### 6.1 RQ1 — Replication gate, then continuation

**Table 2 — Assembled AR era means, QC-gated series (regenerated; `ar_fy_features.csv`).**

| Era | n years | Nominal./100 | Temporal/1k | "and"/100 | Acronyms/1k | Mgmt/1k | Tier-1/1k | Tier-2/1k |
|---|---|---|---|---|---|---|---|---|
| 1946–1965 | 19 | 5.98 | 39.96 | 2.95 | 15.82 | 1.11 | 0.009 | 0.25 |
| 1966–1985 | 18 | 6.22 | 34.26 | 3.38 | 17.04 | 0.60 | 0.009 | 0.51 |
| 1986–2005 | 17 | 6.84 | 26.10 | 3.72 | 27.97 | 2.53 | 0.032 | 2.01 |
| 2006–2012 | 5 | 7.51 | 27.99 | 4.20 | 41.34 | 4.08 | 0.061 | 3.76 |
| 2013–2022 | 10 | 7.79 | 28.29 | 4.54 | 38.03 | 4.09 | 0.063 | 5.17 |
| 2023–2024 | 2 | 7.93 | 18.11 | 5.25 | 38.85 | 5.50 | 0.132 | 9.09 |

Temporal anchoring falls ~35% from the founding era to 1986–2012 (39.96 → ~26–28 per 1k)
while nominalizations, acronyms, "and", and the management register rise — qualitatively
reproducing the pamphlet. (After quality-gating, the era path is no longer strictly
monotone: part of the apparent late-period decline in the ungated series came from the two
defective years.) The composition lesson stands with the corrected numbers: on unassembled
document-level AR files, temporal anchoring RISES (~32.7 → ~47.5) over the same eras —
sibling and financial-volume mixture reverses the historical conclusion.

**Continuation.** Tier-2 reaches 9.09/1k in 2023–24 (36× the 1946–65 level); "and",
management vocabulary, and sentence length sit at series highs. Bankspeak did not plateau.

### 6.2 RQ2 — Post-2022 change, described (embargoed pending IMF comparator, D3)

**Table 3 — Tier-1 at the prespecified 2023 cut (regenerated; `T2_its.csv`).**

| Series | Spec | n_post | Level shift b2 (/1k) | p(b2) | Placebo sig. frac. |
|---|---|---|---|---|---|
| AR (assembled, QC-gated, 71 yrs) | level-only | 2 | +0.070 | <0.001 | 0.00 |
| ICR (doc-level yearly) | full segmented | 4 | +0.056 | <0.001 | 1.00 |
| PAD (doc-level yearly) | full segmented | 4 | +0.027 | 0.010 | 0.50 |

**Empirical breakpoint ranking** (all admissible cuts, same spec; `s12`): 2023 ranks 2nd of
72 candidate cuts on the assembled AR series (top cut: 2022), 3rd of 27 on ICR and 4th of
25 on PAD — where the strongest cuts are 2024–2025. On the unassembled doc-level AR series
(siblings included) 2023 ranks 27th of 74, again showing what composition noise does.
Reading: maximal break statistics cluster in **2022–2025 across series — a ramped post-2022
increase, not a single sharp 2023 break**. We therefore describe a post-2022 increase and
do not claim a dated discontinuity.

**Robust aggregation.** The ICR/PAD Tier-1 rise survives medians and 10%-trimmed means
(ICR median 0.038→0.102; PAD median 0.000→0.059 per 1k, 2019–22 vs 2023–26); pre-LLM model
surprise rises under medians too (Pythia ICR 2.400→2.533; PAD 2.450→2.599; GPT-2 likewise);
the doc-level AR panel falls under all Tier-1 aggregators and under mean/median NLL
(GPT-2 trimmed-mean NLL is flat: 3.831→3.833); assembled-unit NLL is future work.

**Lexicon decomposition.** Post-2022 Tier-1 mass is concentrated: the *underscore* family
carries 43% and *pivotal* 15%. The increase is not a one-word artifact — removing both, the
pre→post rate still rises 2.2× (ICR), 3.9× (PAD), 2.1× (AR doc-level) — but per-word
contributions and concordance samples belong in the supplement, and "fingerprint" language
is avoided throughout.

**Influence.** Leave-one-year-out on the assembled-AR level fit: b2 ranges 0.041–0.099
around the base 0.070; the most influential year is 2023 itself — unavoidable with n_post=2
and disclosed as such.

## 7. Limitations
1. **Breakpoint specificity**: full-spec placebo fractions of 0.50–1.00 and the 2022–2025
   clustering of maximal cuts limit any 2023-specific reading (hence "post-2022 increase").
2. **Confounding**: leadership change (June 2023), style-guide and thematic pivots co-move
   with LLM adoption; the IMF comparator is the design answer and gates publication (D3).
3. **Mechanism**: lexical tiers cannot separate direct LLM assistance from human adoption of
   LLM-popularized vocabulary; we measure population-level change, not authorship.
4. **AR post-break support**: two years; level-only inference, descriptive beyond that.
5. **Within-stratum composition** (region, sector, instrument, template era) remains
   untreated pending metadata enrichment; a signature lesson of this paper applied to itself.
6. **Multiplicity**: one confirmatory estimand (Tier-1 level shift, prespecified 2023 cut)
   to be declared before comparator analysis; all else exploratory; FDR control planned.
7. Residue 2.3% and 6 zero-token docs, logged; missingness-by-format analysis planned.

## 8. Discussion `[TO-WRITE]`
## 9. Data and code availability — as v0.1.
## References (all 25 entries Crossref/publisher-verified, 2026-08-07)

**Bankspeak & institutional discourse.** Moretti & Pestre 2015 (Literary Lab Pamphlet 9;
also *New Left Review* 92:75–99, DOI 10.64590/167) · Barnett & Finnemore 1999 (*Int.
Organization* 53(4):699–732, 10.1162/002081899551048) · Cornwall & Brock 2005 (*Third World
Q.* 26(7):1043–1060, 10.1080/01436590500235603) · Mosse 2004 (*Development and Change*
35(4):639–671, 10.1111/j.0012-155X.2004.00374.x).
**LLM lexical shifts.** Kobak et al. 2025 (*Science Advances* 11(27):eadt3813,
10.1126/sciadv.adt3813) · Liang et al. 2025 (*Nature Human Behaviour* 9:2599–2609,
10.1038/s41562-025-02273-8) · Liang et al. 2025 (*Patterns* 6(12):101366,
10.1016/j.patter.2025.101366) · Juzek & Ward 2025 (COLING 2025:6397–6411).
**Detection & critiques.** Gehrmann et al. 2019 (ACL demos, 10.18653/v1/P19-3019) ·
Ippolito et al. 2020 (ACL, 10.18653/v1/2020.acl-main.164) · Mitchell et al. 2023 (ICML,
PMLR 202:24950–24962) · Liang et al. 2023 (*Patterns* 4(7):100779,
10.1016/j.patter.2023.100779) · Weber-Wulff et al. 2023 (*Int. J. Educ. Integrity* 19:26,
10.1007/s40979-023-00146-z) · Wu et al. 2025 (*Computational Linguistics* 51(1):275–338,
10.1162/coli_a_00549).
**ITS & structural breaks.** Wagner et al. 2002 (*J. Clin. Pharmacy & Therapeutics*
27(4):299–309, 10.1046/j.1365-2710.2002.00430.x) · Lopez Bernal et al. 2017 (*IJE*
46(1):348–355, 10.1093/ije/dyw098) · Lopez Bernal et al. 2018 (*IJE* 47(6):2082–2093,
10.1093/ije/dyy135) · Newey & West 1987 (*Econometrica* 55(3):703–708, 10.2307/1913610) ·
Bai & Perron 1998 (*Econometrica* 66(1):47–78, 10.2307/2998540).
**IGO document studies.** Broad 2006 (*RIPE* 13(3):387–419, 10.1080/09692290600769260) ·
Vetterlein 2012 (*New Political Economy* 17(1):35–58, 10.1080/13563467.2011.569023) ·
De Francesco & Guaschino 2020 (*Policy and Society* 39(1):113–128,
10.1080/14494035.2019.1609391).
**Reproducibility & corpus design.** Biber 1993 (*LLC* 8(4):243–257, 10.1093/llc/8.4.243) ·
Sandve et al. 2013 (*PLOS Comp. Biol.* 9(10):e1003285, 10.1371/journal.pcbi.1003285) ·
Wilkinson et al. 2016 (*Scientific Data* 3:160018, 10.1038/sdata.2016.18).
