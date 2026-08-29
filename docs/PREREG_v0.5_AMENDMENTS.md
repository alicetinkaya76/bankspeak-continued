# PREREG v0.4 → v0.5 amendments (round-6 required changes; 2026-08-09)

All nine round-6 blockers accepted; the two independently checkable ones were
reproduced on the authors' stack before repair (duplicate-cell acceptance: 65
rows silently entered a 32-year design; standardization counterexample:
weighted post shares (0.90, 0.10) against target (0.50, 0.50)). Items marked
[CODE] are implemented and tested in this kit; [BUILD] items are specified here
and scheduled in ROUND6_BUILD_PLAN.md; full v0.5 is assembled when the [BUILD]
modules exist, and round 7 is requested only after that.

## B1 [CODE] §8 — failed-calibration nested curve
The power curve's default decision engine is the FULL NESTED PASS-P bootstrap
(inner B = 9,999, frozen); the Wald shortcut may be used only when a supplied
calibration record has `calibration_ok = true` (size ∈ [α/2, 2α] AND
concordance ≥ 0.95). `mde_sim.py` implements both branches and prints which
engine ran; the smoke default is now nested.

## B2 [CODE] §4.2 — valid NB2 QML score and fallback
Frozen dispersion estimator α̂ = clip( Σ[(y−μ̂)²−μ̂] / Σμ̂², 0, 10 ) from the
Poisson QML fit of the same pass. PASS-P NB2: weights W = μ̂⁰/(1+α̂μ̂⁰) in the
partialling AND the factor 1/(1+α̂μ̂⁰) in the score contribution
s = x̃(y−μ̂⁰)/(1+α̂μ̂⁰). PASS-E NB2: full NegativeBinomial(α̂) fit with
V̂ = μ̂+α̂μ̂²; non-convergence (checked via the fit's convergence flag, counted
as failure) triggers the frozen fallback: delete-one-year Poisson QML jackknife
CI, SE = √((T−1)/T Σ(θ₍₋ₖ₎−θ̄)²). NB2 fixture test included.

## B3 [CODE] §4.1 — input contract
Exactly one cell per institution×year (duplicates raise), tokens finite > 0,
counts finite ≥ 0 and integer unless `allow_noninteger` (standardized cells),
which also sets the PASS-E reconstruction rule to NO rounding. Integer-cell
rounding is frozen as NumPy ties-to-even and named in the output.

## B4 [CODE core + text] §6 replaced — period-valid standardization
The pre-based document weights are withdrawn. Frozen estimator
(`src/standardize.py`, counterexample fixture-tested):
R̃_it = Σ_g π_g·r_{i,g,t} with r = count/tokens per (institution, group, year)
cell; standardized cells C̃ount_it = R̃_it·Tokens_it are analyzed with
`allow_noninteger=True` (no rounding). π_g = pooled pre-2023 TOKEN shares over
groups with support in both institutions in BOTH periods. Per-cell coverage
(π-mass retained) is reported; π renormalizes over available groups within a
cell; hard-fail: min post-period coverage < 0.80 in either institution ⇒
condition-2 standardized variant infeasible ⇒ condition 2 fails. Multi-country
rule extended to WB: ICR/PAD group = the D&R primary-country field mapped to
(region × income); regional/multi-country projects and missing fields go to an
explicit `unknown` group that counts as unsupported. ESS floor retained,
computed on cell token masses under π.

## B5 [BUILD] Appendix B — executable frame builders
`s09a_imf_articleiv_frame.py` (exact SPROLL/eLibrary request layer with
pagination + logging, title normalizer, "Article IV Consultation" matcher,
Country Report number parser, revision resolver, combined-report flagger,
single-ISO3 extractor with alias map, cutoff filter, fixture-mode tests);
`s09b_wb_p0_frame.py` (D&R docty-filtered frame reusing the s01 fetch layer;
unit/country/title/version/cutoff/dedup rules mirrored for CEM/SCD/CPF);
`g1_audit.py` (global draw: rank candidates by SHA256(seed|candidate_id), take
20; outcome-blind sheet with institution/genre labels masked; four binary
items, uncertain = fail, missing abstract ⇒ title-only flagged; PASS ≥ 16/20).
"Blind" is replaced by "outcome-blind" throughout; G2 splits metadata-frame
eligibility from post-harvest lexical eligibility explicitly.

## B6 [TEXT] §2/§11 — deterministic family states
Frozen four-state rule: viable P1 & P2 → {P1,P2}, Holm (0.025/0.05); only one
viable → that singleton at α = 0.05; neither viable AND P0 failed → fallback.
P0 selected then failing a locked post-harvest condition ⇒ P0 fails; P1/P2 are
never promoted. The go/no-go sentence is restated with the singleton states.

## B7 [CODE partial + BUILD] §8 — joint branch-specific MDE
Implemented: joint P1/P2 simulation sharing one IMF Article IV series; a
WB-specific differential AR(1) shock δ_t (ρ = 0.5) shared by both WB panels —
the previous common shock was absorbed by C(year) and generated no identifying
dependence; frozen MoM hook σ_δ = √ln(1+α̂) with α̂ from a trend-model Poisson
fit of WB pre-2023 cells; companion-effect grid {0, θ/2, θ}; Holm decisions;
family power = P(≥1 Holm rejection). [BUILD]: branch-specific token/doc
templates from Stage-B metadata and the P0 projection
(tokens/doc = pooled WB ICR+PAD mean) wired via `--cells-template`.

## B8 [TEXT] validation and interpretive algorithms (exact)
Breadth: GLM Binomial(13) with Pearson-scale quasi-dispersion, statsmodels,
delete-one-year jackknife CI (formula as in B2). Prevalence: doc-level logit,
same design + log tokens, same jackknife. Differential-trend CI: the PASS-E
percentile interval of the `WB:c_year` coefficient from the SAME PASS-E draws.
H-SHARED: IMF-only post−pre log-rate difference with a circular block-3
bootstrap on the IMF series alone. Event-study: 3-year bins anchored at
[2023–25] counting backward; an earliest bin shorter than 2 years merges into
its neighbor; PASS-E percentile CIs per bin. 2016 placebo: post16 =
1{2016 ≤ year ≤ 2018} estimated on pre-2023 common years with PASS-P.
[BUILD]: executable orchestration + tests for these, the guard, and full LOPO.

## B9 [TEXT] freeze governance and calendar wording
The Stage-A artifact NEVER changes after its timestamp; Stage-B outputs live in
a separately timestamped SAP artifact. The timestamped object is the complete
Stage-A archive: package zip SHA-256, SHA256SUMS digest + entry count, full
file inventory, dependency-lock and Python-version hashes, machine-readable
test/selftest/calibration log hashes, the round-ruling artifact hash, and the
immutable commit plus a retrievable archive (the registration upload itself).
§11/App-B: "full calendar-2026" → "all 2026-dated records indexed at the
2027-01-15 snapshot". §7: the s06 NLL ≥ 100-token filter is explicitly a
DEFERRED step-4 patch, not claimed as already applied.
