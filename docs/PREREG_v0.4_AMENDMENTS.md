# PREREG v0.3 → v0.4 amendments (round-5 method defects; 2026-08-09)

Round-5's three demonstrated defects are accepted; all were reproduced
independently on the authors' engine before repair. Final v0.4 will be assembled
once the round-5 report text (binary ruling + any further line edits) is in
hand; these amendments are the method-level content.

## A1 — §4.2 replaced: two-pass inference

The v0.3 single-pass design invalidly reused null-imposed draws in the basic-CI
formula (producing a 2β̂-centered interval that can exclude β̂ itself — verified:
θ=0.9 synthetic gives β̂=+0.765 with v0.3-CI [1.15, 1.83]). Replacement:

- **PASS-P (p-value; decision-rule condition 1):** studentized block WILD SCORE
  bootstrap under the restricted QML fit. Partialled interaction score
  x̃ = x_j − X_r(X_rᵀWX_r)⁻¹X_rᵀW x_j with QML weights W (Poisson: μ̂⁰; NB2:
  μ̂⁰/(1+αμ̂⁰)); score contributions s = x̃(y − μ̂⁰) summed to year totals, then to
  contiguous non-overlapping blocks of length 3 over the frozen year index;
  Rademacher block weights η_B, statistic T* = Ση_B S_B / √(ΣS_B²);
  p = (1+#{|T*| ≥ |T_obs|})/(B+1), B = 9,999, replicate b seeded 20260806+b.
  No pseudo-data are constructed; null imposition is by construction.
- **PASS-E (CI; the CI clauses of conditions 2–4):** estimation bootstrap
  around the FULL fit — paired circular moving-block transplant of Pearson
  residuals (block 3; replicate b seeded 20260806+500000+b), reconstruction
  y* = max(0, round(μ̂ + √V̂·r*)) with V̂ the family variance, refit of the full
  model, **percentile CI** [q.025, q.975] of β*. Reported alongside:
  β̂ ± 1.96·sd(β*) (Wald-boot CI) and the **true floored-reconstruction share**
  (count of recon < 0 events over all cells × replicates). Escalation: replicate
  failure > 1% ⇒ Wald-boot CI governs; failure > 50% ⇒ CI declared failed.
- Governance sentence: condition 1 is decided by PASS-P alone; every "95% CI
  excluding 0" clause in conditions 2–4 refers to the PASS-E percentile CI.
  Near-boundary disagreement between the two passes is possible at very small
  counts and is reported, not adjudicated ad hoc.

## A2 — §4.2 diagnostic corrected

v0.3's floored-share diagnostic was computed from the original residuals and is
identically ≈0 (μ̂⁰+√μ̂⁰·r ≡ y). The true per-replicate share (reviewer's
example: 22.0% in a small-count configuration; authors' reproduction: 3.2% at
μ≈2.4) is now accumulated and reported. If the PASS-E true floored share
exceeds 5%, the Wald-boot CI is reported with equal prominence and the
small-count regime is flagged in the output.

## A3 — §8 calibration made real

v0.3's "calibrated against 200 full nested bootstrap runs" was not implemented:
the recorded nested p-values were unused. The calibrate step now outputs
`boot_size_at_null` = mean(p_boot < α) and `wald_boot_concordance` =
agreement rate between {p_boot < α} and {|z| > crit}; **acceptance rule:**
the Wald shortcut may drive the power curve only if α/2 ≤ boot_size ≤ 2α AND
concordance ≥ 0.95; otherwise the curve is computed with the full nested
PASS-P bootstrap. Production constants unchanged (ncal = 200, B = 9,999,
reps = 1,000, seed 20260806).

## A4 — platform-agreement wording

"Bit-identical across platforms" is withdrawn. Verified statement: the MDE
calibration statistic agrees to ≤ 4×10⁻¹⁴ across three independent stacks
(Linux x86-64 / macOS arm64 / reviewer's Linux, numpy 2.3.5) — last-ulp BLAS
reduction-order differences only. Seeded p-values and sample selections remain
exactly reproducible.
