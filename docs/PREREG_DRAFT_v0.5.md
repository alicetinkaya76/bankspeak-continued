# PREREG — Comparator round (DRAFT v0.5, 2026-08-10)

**Status: revised after the round-6 external review; candidate for the Stage-A freeze
pending the round-7 binary ruling; NOT yet frozen.**

**Change log v0.4 → v0.5 (all nine round-6 required changes adopted; the two
independently checkable defects were reproduced on the authors' stack before repair —
duplicate-cell acceptance: 65 rows silently entered a 32-year design; standardization
counterexample: weighted post shares (0.90, 0.10) against target (0.50, 0.50)):**
(1) §8 — the power curve's default decision engine is the full nested PASS-P bootstrap;
the Wald shortcut requires an accepted calibration record (`mde_sim.py`). (2) §4.2 —
the NB2 path is a valid QML score test with a frozen method-of-moments α̂ and a frozen
jackknife fallback (`bootstrap_engine.py`). (3) §4.1 — an explicit input contract
(duplicate institution×year cells raise; token/count validity; frozen rounding).
(4) §6 — the pre-based document weights are withdrawn and replaced by period-valid
direct standardization (`standardize.py`), with the ESS floor restated on cell token
masses under π in an exact executable form declared below. (5) Appendix B — executable
frame builders and the G1 module exist and are fixture-tested
(`s09a_imf_articleiv_frame.py`, `s09b_wb_p0_frame.py`, `g1_audit.py`); Appendix B.10
adds the WB-P0 acquisition protocol. (6) §2/§5 — the deterministic four-state family
rule with singleton levels. (7) §8 — joint P1/P2 simulation with a WB-specific
differential AR(1) shock and branch-specific templates (`make_cells_template.py`).
(8) §3/§9 — the validation and interpretive analyses are specified as exact algorithms
and implemented in one orchestration module (`s13_validation_battery.py`) with a frozen
seed-offset registry. (9) §11 — freeze governance: the Stage-A artifact never changes
after its timestamp; the archive-binding field list is emitted by
`tools/build_audit_package.py --freeze-fields`; the calendar wording is corrected; the
§7 NLL filter is disclosed as a deferred patch. Disclosure: the full round-6 report
reached the authors. Round 7 is asked to verify that this weave leaves no round-6
finding unaddressed, and to stress-test the declared ESS rendering in §6. v0.1–v0.3
are withdrawn and archived; post-freeze deviations are logged in
`DESIGN_RATIONALE.md` and demote the affected result to exploratory.

## 0. Epistemic status (unchanged from v0.2; E17)

Prospective only with respect to comparator data; outcome-informed on the World Bank
side (the 2023 cut, the Tier-1 lexicon, and the panel structure postdate observation of
WB outcomes). This is a *prospective external-comparator validation of an already
observed WB pattern*. Confirmatory interpretation is restricted to comparator
replication; "LLM-associated construct validity" remains exploratory. Where a design
constant below is informed by observed WB magnitudes (the MDE gate of §8), that
dependence is stated at the point of use rather than hidden.

## 1. Claims (mechanism-neutral; unchanged from v0.2)

- **H-DIFF (only confirmatory claim):** a differential post-2022 change between the
  prespecified WB and IMF series in the frozen lexical outcome; **mechanism
  unresolved.** Never described as enterprise-LLM-adoption evidence.
- **H-SHARED (descriptive companion):** the IMF's own pre/post change with CI; a
  similar IMF rise nulls H-DIFF while remaining informative about a shared post-2022
  shift. Reported separately, never conflated.
- Fixed success-language template: *"a differential post-2022 change between the
  prespecified WB and IMF series in the frozen lexical outcome; mechanism unresolved."*

## 2. Panels and the deterministic branch rule (round-4 change 2; round-6 changes 5, 6)

**Default co-primary family:** P1 = WB ICR vs IMF Article IV; P2 = WB PAD vs IMF
Article IV. Article IV remains a **non-equivalent falsification comparator**
(institution and genre confounded); interpretation capped accordingly.

**P0 branch (single genre-matched primary), decided at Stage-B on metadata only, under
a fully deterministic rule:**

1. **Fixed candidate priority, no merging:** (1) Country Economic Memorandum,
   (2) Systematic Country Diagnostic, (3) Country Partnership Framework — exact `docty`
   strings as returned by s00 facet discovery, recorded verbatim in
   `config/wb_p0_docty.yaml` before probing (the s09b pipeline is label-agnostic and
   consumes that map). Candidates are never combined across labels or successor
   series. The first candidate in priority order that passes ALL gates below becomes
   P0; later candidates are not evaluated further. (Note recorded in advance: SCD and
   CPF series begin circa 2014–15 and are therefore expected to fail gate G2 by
   construction; the priority order makes the branch effectively CEM-or-nothing.)
2. **Gates (ALL required, metadata only):**
   - **G1 Genre adjudication (round-6 change 5):** an **outcome-blind** title/abstract
     audit of 20 candidate documents drawn by the GLOBAL deterministic draw of
     `src/g1_audit.py`: all candidate rows ranked by SHA256(seed | candidate_id)
     ascending, first 20 taken — independent of any per-cell sampler. The sheet
     carries audit keys, titles and abstracts only; institution/genre labels are not
     written. Four binary items per row — recurring country-level macroeconomic
     surveillance; not tied to a single project or operation; staff-authored
     analytical report; periodic cycle — scored before any year-by-outcome information
     is viewed; a blank or uncertain item scores 0; a row passes iff all four items
     are 1; rows lacking an abstract are flagged `title_only`. PASS requires ≥16/20.
   - **G2 Coverage:** ≥25 usable pre-2023 common years (calendar years with ≥1
     eligible document in BOTH the candidate genre and Article IV) and ≥3 completed
     post years (2023–2025). G2 is a **metadata-frame** eligibility gate; token-based
     (lexical) eligibility is a separate post-harvest locked condition (§6) and is
     never used to choose the branch.
   - **G3 Metadata support:** ≥80% of post-period candidate **documents** lie in
     country cells with support in both institutions.
   - **G4 Power:** the §8 simulation, run on the candidate's metadata cell counts,
     yields MDE₈₀ ≤ 0.60 log points.
3. **One-way switch and the four-state family (round-6 change 6):** if a candidate
   passes, the Holm family is frozen at the SAP as {P0} and P1/P2 become falsification
   analyses. If no candidate passes, the family is frozen as {P1, P2}. **After the SAP
   freeze there is no switchback in either direction.** The frozen four-state decision
   rule of §5 then governs: both P1 and P2 viable → Holm over {P1, P2}; exactly one
   viable → that singleton tested at α = 0.05; neither viable AND P0 failed → the
   fallback state (§11.5). A P0 selected at the SAP that later fails any locked
   post-harvest condition is a **failed confirmatory outcome**, not a family
   re-selection; P1/P2 are never promoted post-hoc. The "no active primary" state
   cannot arise.

**P-A (Annual Reports): descriptive only. NLL: exploratory only** (pending §7
regeneration). There is no secondary confirmatory family.

## 3. Outcome and validation outcomes (round-4 changes 7, 9; round-6 change 8)

- **Confirmatory outcome (unchanged): the family-occurrence count.** For document d,
  `count_d` = number of token occurrences matching any of the 28 forms under the single
  matching rule of Appendix A (there is exactly one rule). Aggregated under the fixed
  28→13 mapping; the total is invariant to family relabeling. Round-4's ruling that
  switching to breadth/prevalence now would itself be an outcome-informed primary
  change is adopted: occurrence count stays primary.
- **Concentration guard (fixed, per round 4):** the mandatory guard family is
  **underscore** — already known to dominate on the WB side (43.48% of post-period
  hits). Condition 3 of §5 refits the primary model with the underscore family removed
  from the outcome. A prespecified non-gating stress test additionally removes
  underscore+pivotal jointly. The full leave-each-family-out profile is exploratory.
  No guard family is ever selected from unseen post-period outcomes.
- **Mandatory validation outcomes (exact algorithms, round-6 change 8; implemented in
  `src/s13_validation_battery.py`; reported alongside every confirmatory result):**
  - **Document prevalence:** doc-level indicator of ≥1 Tier-1 family occurrence;
    statsmodels GLM **Binomial (logit)** with the §4 design (numeric WB indicator,
    C(year), WB differential trend, WB×post) plus `log tokens` as covariate; CI by
    delete-one-year jackknife over the common-year sequence with
    SE = √((T−1)/T · Σ(θ₍₋ₖ₎−θ̄)²).
  - **Family breadth:** number of distinct families present per document, modeled as
    GLM **Binomial with 13 trials** under the same design and `log tokens` covariate;
    the Pearson-scale quasi-dispersion (Pearson χ² / df) is computed and reported
    (the plain binomial assumption is not imposed on interpretation); same jackknife
    CI.
  - **Consistency rule (prespecified):** if either validation outcome's WB×post
    estimate has the opposite sign with a CI excluding 0, any confirmatory H-DIFF
    claim is downgraded to "count-specific" and reported as such.

## 4. Primary model and inference (round-4 changes 3, 4; round-6 changes 2, 3)

### 4.1 Estimable model and input contract (explicit numeric coding)

Define `WB_i ∈ {0,1}` (1 = World Bank; IMF is the reference institution). Analysis
cells are institution×year over the **frozen common-year sequence** Y = (t₁ < … < t_T):
calendar years in the panel span with one eligible cell in BOTH institutions
(recorded verbatim at the SAP; calendar gaps permitted). `c_year = year − m`, where m
is the median calendar year of Y (recorded at the SAP). `post = 1{2023 ≤ year ≤ 2025}`
(§11.4: 2026 is excluded from the confirmatory frame entirely).

Frozen estimable form (statsmodels GLM Poisson, patsy formula given verbatim):

    Count ~ C(year) + WB + WB:c_year + WB:post

with `offset = log(Tokens)` and `WB` a numeric 0/1 column (never a factor). The
intercept plus C(year) dummies absorb common year effects; there are no standalone
`post` or `c_year` main effects (collinear with C(year) and intentionally absent).
The design has exactly T + 3 columns: intercept, T−1 year dummies, WB, WB·c_year,
WB·post. **Estimand:** the coefficient on `WB:post`, on the log-rate scale; positive =
the WB post-2022 change exceeds the IMF's. NB2 with the same design is the
overdispersion sensitivity. Prespecified display: the event-study variant replacing
WB:c_year + WB:post with WB × 3-year-bin indicators (§9).

**Input contract (round-6 change 3; enforced in `build_design`):** exactly one cell
per institution×year — duplicates raise an error, never merge; tokens finite and > 0
in every cell; counts finite and ≥ 0, integer unless `allow_noninteger` is set (the
standardized-cell mode of §6), which also switches the PASS-E reconstruction rule to
NO rounding. Integer-cell reconstruction rounding is frozen as NumPy ties-to-even and
named in every output.

### 4.2 Primary inference: two-pass design (round-5 repair; round-6 change 2)

Rationale for two passes: null-imposed resampling is the correct device for a
p-value but is invalid inside estimator-CI formulas (it centers the basic-CI at
2β̂ — demonstrated in round 5 and reproduced by the authors). The p-value and the
CI therefore come from two separately specified procedures sharing the frozen
year index, seeds, and block length.

**PASS-P — p-value (decision-rule condition 1): studentized block wild score
bootstrap.**

1. Fit the restricted model M⁰ (§4.1 without `WB:post`) by QML (Poisson, or NB2
   for the sensitivity) → fitted means μ̂⁰ and QML weights W (Poisson: μ̂⁰;
   NB2: μ̂⁰/(1+α̂μ̂⁰)).
2. Partial the interaction column: x̃ = x_j − X_r(X_rᵀWX_r)⁻¹X_rᵀW x_j.
3. Score contributions s_it = x̃_it (y_it − μ̂⁰_it) / (1 + α̂μ̂⁰_it) — the NB2
   quasi-score factor; Poisson: α̂ = 0. Sum to year totals S_k over the frozen
   common-year index, then to **contiguous non-overlapping blocks of length 3**
   (last block may be short) → block sums S_B.
4. Observed statistic T = ΣS_B / √(ΣS_B²); replicate b draws Rademacher block
   weights η (seed 20260806+b) and computes T*_b = Ση_B S_B / √(ΣS_B²).
5. p = (1 + #{|T*_b| ≥ |T|}) / (B + 1), B = 9,999, two-sided. Degenerate
   denominator (ΣS_B² = 0) ⇒ p = 1. No pseudo-data are constructed; null
   imposition and flooring-immunity hold by construction.

**NB2 dispersion (frozen, round-6 change 2):**
α̂ = clip( Σ[(y−μ̂)²−μ̂] / Σμ̂², 0, 10 ) by method of moments from the Poisson QML
fit of the same pass.

**PASS-E — confidence interval (the CI clauses of conditions 2–4): estimation
bootstrap around the FULL fit.**

1. Fit the full §4.1 model → μ̂, family variance V̂ (Poisson: μ̂; NB2: full
   NegativeBinomial(α̂) fit with V̂ = μ̂+α̂μ̂²). NB2 non-convergence — checked via the
   fit's convergence flag and counted as failure — triggers the frozen fallback:
   the delete-one-year Poisson QML jackknife CI with
   SE = √((T−1)/T · Σ(θ₍₋ₖ₎−θ̄)²). If that also fails, the affected condition
   fails. Pearson residuals r = (y−μ̂)/√V̂.
2. Paired **circular moving-block** transplant of residual pairs over index
   positions (block 3; ⌈T/3⌉ wrap-around blocks truncated to T; replicate b
   seeded 20260806+500000+b). Wild weights require a fixed partition (PASS-P);
   position transplantation uses circular blocks to avoid edge effects — the
   asymmetry is intentional and frozen.
3. Reconstruction y* = max(0, round(μ̂ + √V̂·r*)) with NumPy ties-to-even rounding
   for integer cells and NO rounding under `allow_noninteger` (standardized
   cells); the **true floored share** (count of reconstructions < 0 over all
   cells × replicates) is reported with every CI. Refit the full model on y* →
   β*_b; replicate fits are counted as failures when the refit raises or its
   convergence flag is false.
4. **Percentile CI** [q₀.₀₂₅(β*), q₀.₉₇₅(β*)] governs the decision rule;
   β̂ ± 1.96·sd(β*) (Wald-boot CI) is reported alongside. Escalation: replicate
   failure > 1% ⇒ the Wald-boot CI governs; failure > 50% ⇒ the CI is declared
   failed and the affected condition fails. If the true floored share exceeds
   5%, the Wald-boot CI is reported with equal prominence and the small-count
   regime is flagged. The governing interval is NAMED in every output
   (`governing_ci`).
5. **Differential-trend recording (round-6 change 8):** the `WB:c_year`
   coefficient is recorded from the SAME PASS-E draws; its point estimate and
   percentile interval (`trend_beta_hat`, `trend_ci_percentile`) are the §9
   differential-trend CI. No separate simulation is run for it.

**Governance:** condition 1 is decided by PASS-P alone; every "95% CI excluding
0" clause in conditions 2–4 refers to the PASS-E percentile CI after the
escalation ladder. Near-boundary disagreement between the passes is possible at
very small counts and is reported, never adjudicated ad hoc.

**Reuse map (same seeds, blocks, B):** NB2 variant = both passes rerun with NB2
weights/variance; standardized variant = both passes on the §6 standardized cells
with π fixed across replicates and `allow_noninteger` set; concentration guard =
PASS-E on the underscore-removed outcome; LOPO deletions = PASS-P p on each
deletion set (the deleted year removed from the index before blocking).

Secondary sensitivity: HAC(3) OLS on the annual paired log-rate difference
d_k = log((y_WB+0.5)/Tokens_WB) − log((y_IMF+0.5)/Tokens_IMF) regressed on
{1, c_year, post} — the +0.5 continuity constant is the frozen zero-count rule.
Document-level QML with institution×year clustering is a reported sensitivity
only.

## 5. Decision rule, global success, and multiplicity families (round-4 change 5;
round-6 change 6)

**Holm family, frozen at the SAP — the four-state rule:** {P0} if the branch passed,
else {P1, P2}. With two viable panels, Holm at α = 0.05: the smaller p is tested at
0.025 and, only if it rejects, the larger at 0.05. With exactly one viable panel, that
singleton is tested at α = 0.05. With no viable panel and P0 failed, the §11.5
fallback state applies. A P0 selected at the SAP then failing a locked post-harvest
condition ⇒ P0 fails; P1/P2 are never promoted.

All four conditions required, per panel:

1. Holm-adjusted **PASS-P** wild-score p < its Holm level for `WB:post`.
2. **Stability:** |β_variant − β_M2| / |β_M2| < 0.50 on the log-rate scale, AND sign
   unchanged AND 95% **PASS-E percentile** CI excluding 0, under BOTH NB2 and the
   standardized variant. NB2 non-convergence ⇒ delete-one-year jackknife CI on QML;
   if that also fails, condition 2 fails. A standardized variant declared infeasible
   by the §6 hard-fail or ESS rules ⇒ condition 2 fails.
3. **Concentration guard:** underscore-removed refit retains sign with its 95%
   PASS-E percentile CI (after the escalation ladder) excluding 0.
4. **LOPO:** for each post-year deletion (2023, 2024, 2025 — three deletions), the
   refit retains sign and has **unadjusted** PASS-P p < 0.10. This is a
   per-panel stability condition, explicitly NOT a Holm family; its p-values come from
   the same bootstrap algorithm.

**Global success rule (explicit):** the confirmatory H-DIFF claim is panel-specific
and is made for every family panel that passes all four conditions at its Holm level.
The headline claim "a differential post-2022 change was confirmed" is permitted iff
≥1 family panel passes; if exactly one of {P1, P2} passes, the claim names that panel
and reports the other panel's estimate and CI in the same sentence. In a singleton
family the claim names the singleton and states why the other panel was not viable.
Failure of any condition in a panel ⇒ no confirmatory claim for that panel; results
reported descriptively with the failed condition named.

## 6. Composition standardization (round-6 change 4 — full replacement of the v0.4
weighting scheme)

The v0.4 document weights w_d = π_g/p̂_{i,g} are **withdrawn**: they standardize only
the PRE distribution and, applied to post documents, produce arbitrary compositions
(the round-6 counterexample — target (0.5, 0.5) → weighted post shares (0.9, 0.1) —
was reproduced on the authors' stack before repair). The frozen replacement is
period-valid **direct standardization** (`src/standardize.py`,
counterexample fixture-tested):

- **Standardized rate:** R̃_it = Σ_g π_g · r_{i,g,t}, with r = count/tokens per
  (institution, group, year) cell. **Standardized cells:** C̃ount_it = R̃_it ·
  Tokens_it, analyzed with `allow_noninteger=True` (no rounding; §4.1 contract).
- **Target distribution:** π_g = pooled pre-2023 **TOKEN** shares over groups with
  support in BOTH institutions in BOTH periods. π is part of the frozen design and is
  fixed across bootstrap replicates.
- **Common ontology (fixed at Stage-B, metadata only):** country (ISO3) mapped to
  region × income group (WB groupings, year-matched), calendar year. WB-only fields
  (sector, instrument) are excluded from the cross-institution model by design and
  used only WB-internally. **Multi-country rule, extended to the WB side (round-6):**
  the ICR/PAD group is the D&R primary-country field mapped to (region × income);
  regional/multi-country projects and documents with a missing field go to an explicit
  `unknown` group that counts as unsupported (conservative). On the IMF side
  multi-country documents cannot occur (frame rule, Appendix B.4).
- **Per-cell coverage:** groups with zero tokens in a cell drop out and π renormalizes
  over the available groups; coverage_it (the π token-share retained) is reported for
  every cell. **Hard-fail:** minimum post-period coverage < 0.80 in either institution
  ⇒ the standardized variant is infeasible ⇒ condition 2 fails.
- **ESS floor (retained, computed on cell token masses under π; exact executable
  rendering, declared for round-7 stress-testing):** per institution×period, over the
  supported groups g with renormalized weights π̃_g and token masses tok_g,
  ESS_tok = 1 / Σ_g(π̃_g² / tok_g); the floor is ESS_tok ≥ 0.50 × (that
  institution×period's total tokens). ESS_tok equals the total token mass exactly
  when π̃ matches the token shares, and shrinks as π̃ concentrates on thin cells.
  Below floor ⇒ the standardized variant is infeasible ⇒ condition 2 fails.
- **Support:** Stage-B gate on documents (§2 G3). Post-harvest locked condition on
  tokens: ≥80% of post-period tokens in each institution must lie in common-support
  cells; below ⇒ condition 2 fails. Excluded zero-support cells and their token shares
  are reported. Fields are never dropped to rescue the analysis.

## 7. Document eligibility (round-4 defect 13 repaired; round-6 change 9 disclosure)

- Lexical counts: tokens ≥ 1 under the Appendix-A tokenizer (the six current WB
  zero-token records are excluded everywhere and logged).
- NLL (exploratory): the tokens ≥ 100 filter under the same tokenizer is a
  **DEFERRED step-4 patch**: it is specified here, is NOT yet applied in the archived
  s06 outputs, and takes effect at the §7 regeneration before any NLL reporting
  (missing model output ⇒ excluded from that model's panel and counted; no constant or
  imputed values — the five GPT-2 5.8744 records are purged on regeneration; one
  frozen document-sampling rule applied identically on every device — the
  hardware-dependent CPU subsample is abolished).
- **Duplicates/versions (corrected):** WB ICR/PAD: one unit per D&R document id (the
  frame already samples unique ids; no version system applies). WB P0 candidates: one
  unit per report number with the Appendix B.10 version rule. IMF: one unit per
  Country Report number, latest revision, per Appendix B.5.
- Assembled annual units: the QC gate (≥5,000 tokens AND ≥0.15 stopword share, 15-word
  frozen list, hash in Appendix A) transfers to IMF annual units unchanged.
- Intention-to-sample reporting: sampled → downloaded → nonzero → eligible, per
  institution×genre×year, in every analysis output.

## 8. Interaction MDE simulation (round-4 change 10; round-6 changes 1, 7)

- **Scale:** the WB:post coefficient in log points. **Post years:** 3 (2023–2025).
- **Joint DGP (round-6 change 7):** P1 and P2 are simulated JOINTLY. One IMF Article
  IV series is drawn and shared by both panels. A WB-specific differential AR(1)
  shock δ_t (ρ = 0.5), shared by both WB panels, enters the WB linear predictor —
  the previous common year shock was absorbed by C(year) and generated no identifying
  dependence. For each cell, Poisson counts with
  log μ_it = a_i + δ_t·WB_i + θ·WB_i·post + log Tokens_it; a_i and Tokens_it from
  observed data (P1/P2) or the metadata-projected template (P0); IMF baseline rate at
  parity with the WB pre-2023 rate. **Frozen MoM hook:**
  σ_δ = √ln(1+α̂), with α̂ from a Poisson trend-model fit
  (count ~ 1 + c_year, offset log tokens) on WB pre-2023 cells
  (`mde_sim.py --sigma-from-cells`). **Companion-effect grid:** the second panel's
  effect ∈ {0, θ/2, θ}; Holm decisions are applied per replicate; **family power** =
  P(≥1 Holm rejection); MDE₈₀ is read off the family power curve (per-panel curves
  reported alongside).
- **Branch-specific templates (round-6 change 7):** per-year document counts and
  tokens enter via `--cells-template`, built by `src/make_cells_template.py` from the
  Stage-B frame; the P0 projection is tokens/doc = the pooled WB ICR+PAD mean.
- **Decision replication (round-5 repair; round-6 change 1):** θ grid 0.00–1.20 by
  0.05; 1,000 simulated datasets per θ. **The default decision engine for the power
  curve is the FULL NESTED PASS-P bootstrap (inner B = 9,999, frozen).** The
  studentized Wald shortcut may be used ONLY when a supplied calibration record has
  `calibration_ok = true` under the explicit acceptance rule: the calibration step
  (200 full nested runs at θ = 0, seed 20260806) yields `boot_size_at_null` ∈
  [α/2, 2α] AND Wald–bootstrap decision concordance ≥ 0.95. `mde_sim.py` implements
  both branches and prints which engine ran; both calibration quantities are computed
  from the recorded nested p-values and published with the curve.
- **Outputs and gates:** MDE₈₀ = smallest θ with ≥80% family rejection. Branch gate
  G4: MDE₈₀ ≤ 0.60 log points — a WB-informed constant (≈ two-thirds of the smaller
  observed WB co-primary shift, ICR ≈ 0.90 log points), declared as such under §0.
  Active-panel gates: ≥25 usable pre-2023 cells and ≥3 post cells per institution;
  failure demotes that panel to descriptive. Simulation code is a Stage-A release
  precondition (§11.2).

## 9. Interpretation matrix (δ gate removed; round-4 change 8; round-6 change 8 —
exact algorithms, all implemented in `src/s13_validation_battery.py`)

The MDE-derived δ pretrend gate is **removed from the confirmatory decision rule**
(round-4 option 1 adopted). Instead:

- **Differential-trend CI:** the `WB:c_year` estimate with its 95% PASS-E percentile
  interval **from the SAME PASS-E draws as the primary CI** (§4.2 step 5; engine
  fields `trend_beta_hat` / `trend_ci_percentile`), reported prominently in every
  confirmatory output.
- Two **fixed, non-gating sensitivity analyses**:
  - **(a) Trend-form / event-study:** the §4.1 variant replacing WB:c_year + WB:post
    with WB × 3-year-bin indicators. Bins are anchored at [2023–2025] and counted
    backward in threes over the observed span; an earliest bin covering fewer than 2
    observed calendar years merges into its later neighbor; the reference bin is the
    bin containing m. Per-bin PASS-E percentile CIs from the event-study's own
    transplant run (seed offset 600,000), engine mechanics otherwise identical to
    §4.2.
  - **(b) 2016 placebo:** post16 = 1{2016 ≤ year ≤ 2018} estimated on pre-2023 common
    years only (the ≤2022 subset of the frozen index), by PASS-P with the §4.2
    algorithm and the placebo column substituted for WB×post. Expected null; reported.
- **H-SHARED (descriptive companion, exact):** the IMF's own pooled post-minus-pre
  log-rate difference, log((Σy_post+0.5)/ΣTok_post) − log((Σy_pre+0.5)/ΣTok_pre)
  (the frozen +0.5 continuity rule), with a circular block-3 bootstrap over the IMF
  year sequence ALONE (seed offset 700,000); replicates with an empty period are
  counted as failures.
- Fixed interpretive lines: IMF post/pre ratio ≥ WB's ⇒ H-DIFF null, reported as
  compatible with a shared shift (H-SHARED), not as generic evidence against an
  LLM-era reading. Condition-2 failure under standardization ⇒ composition explanation
  favored. Text-only subsample interaction losing sign or CI covering 0 ⇒ extraction
  explanation flagged. A differential-trend CI excluding 0 with |trend × post-window|
  comparable to the WB:post estimate ⇒ reported as a first-order extrapolation threat
  in the same paragraph as the estimate (no hard gate).

## 10. Exploratory blocks, per branch (round-4 change 11); executable orchestration

BH q = 0.05 within each block; two-sided; families are branch-specific and frozen at
the SAP.

- Family {P1, P2}: X1 classic features 7×2 = 14; X2 Tier-2 ×2 = 2; X3 NLL 2 models
  ×2 = 4 (only after §7 regeneration); X4 prevalence + breadth ×2 = 4.
- Family {P0}: X1 = 7; X2 = 1; X3 = 2; X4 = 2; plus P1/P2 falsification interactions
  reported with unadjusted CIs, labeled falsification (not members of any test block).
- **XW (WB-internal locked robustness, runs after the SAP under frozen rules):**
  deduplicated breakpoint scan with full support columns; **sup-Wald/QLR unknown-break
  test with bootstrap critical values — an inferential test with its own error rate,
  reported as exploratory inference (the v0.2 "no-error-rate descriptive" label is
  withdrawn)**; step-vs-ramp BIC + bootstrap LR comparison; QC threshold grid,
  token-only and independent-indicator QC variants, "and" independent-QC sensitivity;
  extraction-method covariate/interaction and text-only fits;
  missingness-by-year×format model. Descriptive diagnostics without error rates: HHI,
  family shares, prevalence tables, event-study plots.
- **Orchestration (round-6 change 8):** the §5 conditions, §3 validation outcomes and
  §9 analyses run as one battery, `src/s13_validation_battery.py`, whose CLI refuses
  to run without `--i-am-post-sap` (§11 freeze discipline; fixture tests import the
  functions directly). **Frozen seed-offset registry:** PASS-P seed+b; PASS-E
  seed+500,000+b; event-study PASS-E seed+600,000+b; H-SHARED seed+700,000+b. The
  differential-trend CI uses no offset of its own — it is read from the PASS-E draws.

## 11. Freeze protocol, calendar rule, and go/no-go (round-4 changes 1, 12; round-6
change 9)

1. **Stage-A (acquisition preregistration):** freeze Appendix A (mapping + matching
   rule + stopword hash), Appendix B (the full acquisition protocol, B.10 included),
   the eligibility rules (§7), immutable model revision hashes, and the per-cell
   seeded sampler. External timestamp (OSF registration of the frozen PDF; fallback
   Zenodo/OpenTimestamps) BEFORE any IMF metadata access. **The Stage-A artifact
   NEVER changes after its timestamp**; Stage-B outputs live in a separately
   timestamped SAP artifact.
2. **Stage-A code preconditions (must exist before the timestamp):** machine-readable
   28→13 mapping in config/source with unit tests (including the `seamlessly` case);
   exact integer outputs `tier1_count`, per-family counts, `eligible_tokens`; the
   stable per-cell seed sampler (seed_cell = SHA256(master_seed | institution | genre
   | year)); provenance schema with `sampling_version`, `run_id`, `analysis_eligible`,
   source/version identifiers, branch/panel labels; the §4.2 engine, the §8
   simulation, the frame builders and G1 module (s09a, s09b, g1_audit), the §10
   battery (s13), and the template builder (make_cells_template) — all fixture-tested.
3. **Stage-B (metadata only; text and outcomes sealed):** facet probes and the §2
   deterministic branch decision; the §6 ontology and document-support diagnostics;
   the §8 MDE runs; the frozen common-year sequences. Ends with the final SAP (this
   document, every Stage-B constant filled), externally timestamped. Only then: text
   download and feature processing.
4. **Calendar rule (2026):** the confirmatory post window is the completed years
   **2023–2025** (three post cells; meets the ≥3 gate). Calendar-2026 is excluded from
   the confirmatory frame (Appendix B cutoff: publication date ≤ 2025-12-31). A
   prespecified **descriptive update** uses a second frame snapshot on 2027-01-15 and
   covers **all 2026-dated records indexed at that snapshot**; it is reported in an
   appendix and never pooled into any confirmatory analysis. The August-2026 partial
   year is never counted as a post cell.
5. **Go/no-go (round-4 editor rule adopted):** hard Stage-B deadline **31 October
   2026** — Stage-A frozen, branch decided, support and MDE diagnostics complete, SAP
   frozen. The RQ1/measurement-paper fallback triggers iff **neither branch** ({P0}
   nor {P1, P2}) survives the Stage-B gates by that date; P0 failing its gates alone
   is not a fallback trigger (the family is then {P1, P2}). No comparator rescue work
   after 31 October 2026.
6. **Archive binding (round-6 change 9):** the timestamped object is the complete
   Stage-A archive. The freeze record carries, populated by
   `tools/build_audit_package.py --freeze-fields`: the package zip SHA-256 and byte
   size; the SHA256SUMS digest and entry count; the full file inventory
   (MANIFEST.tsv digest); the `.python-version` content and hash and the pinned
   environment hashes (`requirements.txt`, `requirements-ppl.txt` — the recovered
   scaffold pins; a transitive pip-freeze `requirements.lock.txt` hash is recorded
   additionally when present); machine-readable test/selftest/calibration log
   hashes; the
   round-ruling artifact hash; and the immutable commit plus a retrievable archive
   (the registration upload itself).

## 12. Out of scope

Mechanism/authorship (D2); WB press releases (D8); UNGDC (hard firewall); AR
confirmatory claims; NLL confirmatory claims; any 2026 confirmatory use.

## Appendix A — Outcome definition artifacts (frozen at Stage-A)

**28→13 family mapping** (verbatim; machine-readable copy in config, content-hashed):

    delve        <- delve, delves, delved, delving
    underscore   <- underscore, underscores, underscored, underscoring
    showcase     <- showcase, showcases, showcased, showcasing
    pivotal      <- pivotal
    intricate    <- intricate, intricacies
    meticulous   <- meticulous, meticulously
    boast        <- boast, boasts, boasted
    commendable  <- commendable
    realm        <- realm, realms
    testament    <- testament
    tapestry     <- tapestry
    seamless     <- seamless, seamlessly
    multifaceted <- multifaceted

**The single matching rule** (the only rule; used everywhere): text lowercased;
tokenized with `[A-Za-z']+` (`src/textstats.py` TOKEN_RE); a hit is exact token
membership in the 28-form set; repeated occurrences counted; no lemmatization. Known
consequences accepted and frozen: `pivotal's` tokenizes to `pivotal's` and does NOT
count; `pivotalé` tokenizes to `pivotal` and DOES count. QC stopword share uses the
same tokenizer with the frozen 15-word list in `src/s10_assemble_ar.py`
(sha256 of the sorted newline-joined list:
`3b5d2b51754f73011aeb20ce28bcfcdeb2908ea9380d3d49decf6ee2bb22c41a`).

## Appendix B — Stage-A acquisition protocol (round-4 change 1; round-6 change 5)

1. **Sources.** IMF Article IV staff reports: the *IMF Staff Country Reports* series —
   catalog anchors: IMF eLibrary series listing (elibrary.imf.org, series 002,
   volume = year, issue = report number) and the imf.org rolling list
   "Article IV Staff Reports" (imf.org/en/Publications/SPROLLs/Article-iv-staff-reports);
   secondary frame-verification mirror: RePEc `imf/imfscr`. IMF Annual Reports (P-A
   descriptive only): imf.org Annual Report archive. The exact query strings /
   navigation paths executed are captured verbatim into the frozen Stage-A record at
   execution, with page-count and per-year record-count logs. The executable frame
   logic is `src/s09a_imf_articleiv_frame.py` (fixture-tested); the live capture layer
   refuses to run without `--i-am-in-stage-b` and archives the raw listing pages.
2. **Inclusion (Article IV frame).** Series = IMF Staff Country Reports; title
   contains "Article IV Consultation"; language English; publication year 1994–2025
   (P1 span; the P2 common-year sequence starts 1996). Combined reports (Article IV
   plus program reviews in one Country Report) are IN frame with a recorded flag
   `combined_with_program` = title contains "Review Under" or "Arrangement";
   a prespecified sensitivity re-estimates excluding flagged documents.
3. **Exclusion.** Selected Issues papers; standalone press releases, statements,
   supplements, corrigenda; Financial System Stability Assessments; any report whose
   title lacks "Article IV Consultation".
4. **Unit, country, and year.** One unit per Country Report number (the combined
   publication is the unit). Country: the single ISO-3166 entity named before the
   colon in the title; titles naming a currency union, region, or multiple countries
   are excluded (deterministic single-country rule). Year: the publication (cover)
   date year.
5. **Versions and duplicates.** One unit per Country Report number; where a
   corrigendum or revised issue shares the base number, the latest revision at the
   frame snapshot is kept and the supersession is logged.
6. **Frame and cutoff.** A complete metadata listing per year is captured and hashed
   at the Stage-B snapshot date (recorded); confirmatory cutoff: publication date
   ≤ 2025-12-31. The 2027-01-15 snapshot (§11.4) builds the 2026 descriptive frame
   under identical rules.
7. **Sampling.** Cap 40/year/genre by the stable per-cell sampler:
   seed_cell = SHA256("20260806|{institution}|{genre}|{year}") → 64-bit int seeding an
   independent RNG per cell; adding or removing any other stratum cannot change a
   cell's draw. Frozen sampling CSV, write-once, with the append-only SHA256 manifest.
   (The G1 audit draw is separate and global: §2, `src/g1_audit.py`.)
8. **Retrieval and logging.** Text URL preferred where the source offers text;
   otherwise PDF with PyMuPDF extraction; per-document logging of method, source
   identifiers, `sampling_version`, `run_id`, `analysis_eligible`, branch/panel
   labels; failures retried across resumable passes and reported in the
   intention-to-sample table.
9. **Metadata retained for Stage-B:** title, country, series, report number,
   publication date, department, language, URL(s), DOI where present.
10. **WB P0 candidate frame (round-6 change 5; `src/s09b_wb_p0_frame.py`,
    fixture-tested).** Source: the D&R WDS API v3 (search.worldbank.org/api/v3/wds)
    through the s01 fetch stack, with every raw API page archived to
    `data/meta/wb_p0_raw/` at capture (Stage-B only; the live layer refuses to run
    without `--i-am-in-stage-b`). Inclusion: `docty` equal to a candidate label from
    `config/wb_p0_docty.yaml` (recorded verbatim from the s00 facet probe before
    live use); language English. **Unit:** one unit per report number (`repnb`;
    fallback: the D&R document id when `repnb` is missing); multi-volume rows
    collapse to one unit. **Version rule (deterministic):** latest `docdt` wins; ties
    → a title containing "revised"/"corrig" wins; then the smallest volume number;
    then the smallest document id; supersessions are logged. **Country
    (single-ISO3):** the D&R primary-country field; a comma part matching the frozen
    inversion-suffix set rotates ("Egypt, Arab Republic of" → "arab republic of
    egypt"); a semicolon, a non-suffix comma part, or a regional token ⇒
    excluded_regional_multicountry; an empty field ⇒ excluded_no_country; unmapped
    names are logged and resolved only by extending
    `config/wb_country_aliases.yaml` with a recorded note. **Cutoff:** publication
    (`docdt`) ≤ 2025-12-31; year window recorded at capture. The builder emits the
    per-genre G2 metadata report (pre-2023 years, post years, common pre-years with
    the Article IV frame).
