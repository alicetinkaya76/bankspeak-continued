# PREREG v0.7 — Binding amendments over v0.6 (round-8 repair sprint)

v0.7 = v0.5 + PREREG_v0.6_AMENDMENTS.md + the amendments below. Submitted for
a fresh binary ruling. Date: 2026-08-11.

## C13 (App B / SS11) — Acquisition is byte-verbatim, complete, fail-closed
"(a) IMF SPROLL live capture ABORTS on any non-200 response, on a first page
parsing zero rows, on any later page that parses zero rows while containing
anchors (markup drift / CAPTCHA / interstitial), and on max-page exhaustion;
only an anchor-free zero-row page is a legal terminal page. (b) WB page
archives are the VERBATIM transport body (the hook receives the raw server
bytes; re-serialization is forbidden; a transport without a raw body aborts).
(c) Completeness contract: an empty page while collected < declared total,
or a final count differing from the declared total, RAISES — partial strata
are never silent successes. (d) The docty verification JSON is schema-
validated fail-closed: ISO-8601 verified_utc, source='s00', a 64-hex
probe_sha256 binding the archived s00 probe artifact, and labels covering
EXACTLY {cem, scd, cpf} with non-empty strings." Anchors:
test_sproll_*, test_fetch_*, test_docty_schema_*, verbatim assertion in
test_page_hook_archives_every_raw_page.

## C14 (SS8) — MDE inputs bind; templates strict; calibration governs Wald
"(a) simulate_joint consumes IMF-specific tokens_imf / rate_imf; the joint
{P1,P2} simulation is genuinely four-input (IMF, P1, P2 [, P0]); defaults
reproduce the legacy shared behavior draw-for-draw (smoke signature
unchanged). (b) Templates are STRICT: a supplied template must cover every
simulation year; silent flat-filling is removed. (c) The Wald shortcut, when
calibration is accepted, is decided BY the calibrated critical values:
singleton rejection iff |z| >= crit_abs_z; the Holm pair by calibrated
step-down (larger |z| vs crit_abs_z_half, then smaller vs crit_abs_z), both
order-statistic quantiles of the same null |z| sample; a calibration lacking
either value REFUSES the shortcut (fail-closed -> nested pass_p)."
Anchors: test_imf_*, test_template_missing_year_raises,
test_calibrated_wald_crit_governs.

## C15 (SS4.1/SS9) — No bin without observations; estimability guards
"No event-study bin may contain zero observed years: an empty bin merges
into its immediately LATER neighbor (the last bin, if ever empty, merges
backward), run to a fixpoint together with the earliest-bin >=2 rule; the
lower-median reference rule is unchanged. The generalized PASS-E refuses any
design whose requested coefficient column is all-zero or whose design matrix
is rank deficient — numerical residue is never reported as an estimate."
Anchors: test_make_bins_interior_gap_merges_forward,
test_event_study_interior_gap_estimable, test_passe_multi_rank_guard,
test_passe_multi_zero_support_guard.

## C16 (SS6) — Universal diagnostics; no failure masking
"EVERY standardized-variant return — feasible or infeasible, whatever the
primary reason — carries post_token_support, excluded_token_shares,
dropped_cells, min_post_coverage, ess and pi_groups. ALL simultaneously
failed gates are listed in `failures`; the primary reason follows the frozen
order no_common_support_groups -> zero_coverage_post_cell ->
post_token_support_below_0.80 -> post_coverage_below_floor ->
ess_below_floor. A zero-retained-pi post cell is therefore never masked by
the aggregate support gate." Anchors: test_std_every_return_carries_
diagnostics, test_std_simultaneous_failures_not_masked.

## C17 (SS11.6) — Freeze discipline v4
"(a) A git-status failure ABORTS a freeze run (never assumed clean).
(b) --freeze-fields and --allow-dirty are mutually exclusive. (c) Freeze
fields have a mandatory non-null set (zip identity, checksum identities,
python and requirements identities, git_commit, environment_sha256,
calibration_sha256, logs.tests, logs.selftest, non-empty rulings); any null
ABORTS. requirements_lock_sha256 remains the single declared-optional field.
(d) The machine-readable runtime record (tools/capture_env.py) is REQUIRED
with --freeze-fields, validated against .python-version and every
requirements.txt pin, and shipped as evidence/environment.json. (e) The
accepted calibration JSON is REQUIRED with --freeze-fields, sanity-checked,
and shipped as evidence/calibration.json." Anchors: test_git_status_
failure_aborts, test_freeze_completeness_enforced, test_env_validation,
test_calibration_staged_and_checked.

## C18 (SS11) — Stage-A object definition and freeze record v3
"The Stage-A object is DEFINED as: PREREG_DRAFT_v0.5.md +
PREREG_v0.6_AMENDMENTS.md + PREREG_v0.7_AMENDMENTS.md (jointly, v0.7)
+ the approved package zip identified by the freeze-fields JSON.
STAGE_A_FREEZE_RECORD_v3.md states this definition and carries one
placeholder per freeze field, to be populated ONLY after an approving
ruling, under the permitted-changes boundary."

## C19 (SS11) — Ruling-chain completeness
"The freeze package must carry every available round ruling under
evidence/rulings/ (rounds 2, 3, 4, 7, 8 now; round 6 upon export; round 5
verification JSONs already in docs/). The freeze checklist enumerates them;
absence of an available ruling blocks the freeze."

## Declared unchanged
Estimand, thresholds, seed 20260806 and the full offset registry, UNGDC
firewall, 31 Oct 2026 Stage-B deadline, NLL deferral, SS11.1 ordering, and
the accepted C10 FSSA rule (co-titled IN + flag + Stage-B flagged-exclusion
sensitivity, standalone excluded).
