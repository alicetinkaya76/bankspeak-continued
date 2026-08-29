# Response to the first-round third-eye review (2026-08-08)

Point-by-point account of what was done after the first review. Every number below is
regenerated from the pipeline (`s10`–`s12`); the reviewer is invited to re-derive any of
them from the bundled tables.

## Audit findings

**A1 — FY2002 is a 12-token unit; FY2007 suspect.** CONFIRMED and fixed. FY2002's server
extractions were cover-sheet stamps only; FY2007 was a table/heading dump (46,723 tokens,
0.9% function-word share). A prespecified per-unit extraction-quality gate was added to the
config (`assembly_qc`: ≥5,000 tokens AND ≥15% function-word share; calibration: all
legitimate units ≥17,023 tokens and ≥20.1% share; the two defective units ≤0.9%). The
assembled series is now **71 units (1947–2024)**; per-unit QC values are released
(`robustness/ar_unit_qc.csv`). All AR-series numbers, tables, and figures were regenerated.
The draft now states the general lesson: provenance controls do not establish measurement
validity (Section 3.3).

**A2 — Two post-break observations cannot identify level + slope.** Accepted. The AR
primary specification is now level-only (`y = b0 + b1·t + b2·post`); n_post is disclosed in
every table; post-break-slope claims for AR were removed. On the QC-gated series the Tier-1
level shift is **+0.070/1k** (was +0.102 under the old spec on the defective series — the
review's prediction that the estimate would shrink was correct). Leave-one-year-out: b2
ranges 0.041–0.099; the most influential year is 2023 itself, disclosed as unavoidable with
n_post=2.

**A3 — "2023–2026" label vs. 2024 end of AR evidence.** Corrected everywhere to 2023–2024
for the Annual-Report stratum; the abstract and claims now distinguish AR (through 2024)
from ICR/PAD (through 2026).

## Major objections

**O3 — Placebo non-specificity.** The demanded empirical breakpoint ranking was
implemented (`robustness/breakpoint_scan_tier1.csv`, `breakpoint_rank_2023.csv`): the same
specification fitted at every admissible cut (≥5 pre, ≥2 post years). Result: 2023 ranks
**2nd of 72** cuts on assembled AR (top cut: **2022**, b2=0.076), **3rd of 27** on ICR and
**4th of 25** on PAD — where the strongest cuts are **2024–2025**; on the unassembled
doc-level AR series 2023 ranks 27th of 74. Consequence adopted in full: the paper no longer
claims a dated discontinuity; the headline reading is a **ramped post-2022 increase**
(maximal cuts cluster 2022–2025). Bai–Perron unknown-break estimation is cited and planned
for the comparator round.

**O4 — Banga/style-guide confound.** Unchanged position, now stated more strictly: the IMF
comparator is a publication gate (design decision D3), to be analyzed as a controlled
contrast; no RQ2 claim ships without it.

**O5 — Tier-1 circularity / concentration.** Per-word decomposition released
(`robustness/tier1_decomposition.csv`): the *underscore* family carries 43% and *pivotal*
15% of post-2022 Tier-1 mass. Leave-word-out: removing both, the pre→post rate still rises
**2.2× (ICR), 3.9× (PAD), 2.1× (AR doc-level)**. "Fingerprint" language removed throughout;
mechanism claims explicitly disclaimed. Negative-control word sets and concordance samples:
planned for the supplement.

**O6 — Perplexity validity.** Renamed **pre-LLM model surprise**; described as a deviation
measure, not a detector or econometric instrument. Median and 10%-trimmed aggregation
released (`robustness/robust_aggregation.csv`): the ICR/PAD rise survives medians (Pythia
ICR 2.400→2.533; PAD 2.450→2.599); the flat/declining doc-level AR panel is reported as-is.
Table/boilerplate stripping and validation on matched known-human vs. LLM-revised texts:
planned.

**O7 — Within-stratum composition.** Acknowledged as an untreated limitation applied to
ourselves (Section 7.5); requires metadata enrichment (region/sector/instrument are not in
the current field set) — scheduled with the comparator round.

**O8 — Multiplicity.** One confirmatory estimand declared (Tier-1 level shift at the
prespecified 2023 cut); everything else labeled exploratory; FDR control and block-
bootstrap inference planned before the comparator analysis.

**O10 — Residue informativeness.** Error taxonomy now in the draft (62 HTTP-4xx-class, 3
no-URL records; 6 zero-token extractions listed); missingness-by-year/format analysis
planned.

## Framing and references

Title, lead contribution, and abstract restructured per the review (measurement-discipline
lead; GIQ-oriented title option). All **25 suggested references were verified against
Crossref/publisher records (25/25 VERIFIED, none corrected)** and integrated into the
reference section by module.

## Explicitly NOT done in this round (planned, in order)
1. IMF comparator harvest + controlled-contrast analysis (s09; gates RQ2 publication).
2. Within-stratum composition adjustment (needs metadata enrichment).
3. Assembled-unit NLL panel (current AR NLL is doc-level).
4. Bai–Perron estimation, FDR family control, block bootstrap.
5. Negative-control lexicon + concordance supplement.
