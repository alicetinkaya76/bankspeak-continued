# PREREG v0.6 — Binding amendments over v0.5 (round-7 repair sprint)

v0.6 = PREREG_DRAFT_v0.5.md + the amendments below. Each item names the
governing section, gives the binding replacement/additional language, and the
executable anchor. All are pre-freeze changes submitted for a fresh binary
ruling per the round-7 instruction ("submit the exact repaired package for
another binary review"). Date: 2026-08-10.

## C1 (SS2) — G1 is >=16 OF EXACTLY 20
"The G1 sheet contains exactly 20 drawn candidates. A frame offering fewer
than 20 candidates makes G1 FAIL by construction; the audit tool refuses the
draw and the gate is recorded as failed. A sheet of any size other than 20
scores g1_pass = false (sheet_size_valid flag)." Anchor: g1_audit.draw/score;
tests test_g1_*.

## C2 (SS2) — G3 executable reading + module
"G3: at least 80% of the candidate genre's post-period (2023-2025) documents
must lie in country cells supported in BOTH institutions, where 'supported'
means the ISO3 appears at least once in each institution's full included
frame. Computed by s14_branch_decision.g3_support." Anchor: test_s14.

## C3 (SS2) — Priority-ordered one-way branch decision
"The branch decision is executed by src/s14_branch_decision.py: candidates
are evaluated in the frozen priority order (cem, scd, cpf) against G1..G4;
the FIRST candidate passing all four gates is frozen as P0 and later
candidates are never evaluated (one-way rule); if none passes, the family is
{P1, P2}. The decision file is write-once." Anchor: test_s14 (4 scenarios).

## C4 (SS4.1/SS9) — Event-study bins and reference
"Bins are 3-year calendar bins anchored at the post window, counted backward.
The earliest bin must contain at least 2 OBSERVED common years; otherwise it
merges into its later neighbor, cascading. The reference bin is the bin
containing the LOWER-MEDIAN observed year (a deterministic observed integer),
well-defined for every permitted gap-containing common-year sequence."
Anchor: make_bins; tests test_make_bins_*.

## C5 (SS4.1/SS4.2) — Event-study inference = full PASS-E machinery
"Event-study uncertainty is produced by the generalized PASS-E implementation
(bootstrap_engine.passe_multi, seed offset 600000): Poisson QML -> frozen MoM
alpha -> NB2; convergence-counted paired circular block transplant; TRUE
floored share and small-count flag; percentile and Wald-bootstrap intervals
under the governing escalation ladder (>1% failures -> Wald-boot governs;
>50% or zero valid -> failed state); NB2 full-fit non-convergence -> the
delete-one-year Poisson jackknife, itself fail-closed; noninteger
reconstruction mode for standardized inputs. The shared escalation constants
(FAIL_HARD=0.5, FAIL_SOFT=0.01, FLOOR_FLAG=0.05) are single-sourced in the
engine." Anchor: test_event_study_*, test_passe_multi_*.

## C6 (SS4.2) — Exact integer contract; fail-closed NB2 fallback
"Counts in integer mode must equal their rounded values EXACTLY; tolerance-
based comparison is not used." AND "The jackknife fallback is fail-closed:
non-convergence of the full fit or of ANY deletion fit makes the affected
condition FAIL (method_ci='jackknife_failed', governing CI 'failed'); it is
never silently reported as a valid interval." Anchor:
test_integer_contract_*, test_estimation_ci_jackknife_failed_state,
test_jackknife_multi_fail_closed.

## C7 (SS5/SS11) — Invalid family zero-state
"'No viable panels' while P0 has NOT failed is an impossible state under
SS2/SS5/SS11 and raises an invalid-state error; state='fallback' is reachable
only after recorded P0 failure." Anchor: test_family_zero_state_*,
test_family_five_states_synthetic.

## C8 (SS6) — Two distinct feasibility gates + explicit zero coverage
"Condition 2's standardized variant enforces TWO distinct gates: (i) minimum
post-period pi-coverage >= 0.80 per institution-year (as before), and (ii)
ACTUAL post-period token common support >= 0.80 per institution — the share
of each institution's post tokens lying in common-support groups. Both the
support shares and the excluded token shares (institution x period) are
reported in feasible and infeasible outcomes alike. Any institution-year
whose retained pi mass is zero is an EXPLICIT infeasible state
(zero_coverage_post_cell), never a silent drop; the standardizer reports
dropped cells as the full-set difference." Anchor: test_std_*.

## C9 (SS8) — Branch-specific MDE and the {P0} singleton mode
"The power simulation accepts per-panel inputs: --template-{imf,p1,p2,p0}
(year,tokens[,docs]; a docs column is honored via --tokens-per-doc),
per-panel base rates, and --p2-start-year for the P2 common-year subset.
--family selects the decision rule the gate is computed under: p1p2 = the
two-panel Holm family; p0 = the SINGLETON decision at alpha = 0.05 (no Holm).
G4 for a P0 candidate is computed in p0 mode — the family that would actually
be frozen. The legacy shared-template path is numerically unchanged (the
smoke signature is preserved draw-for-draw). P0 PASS-P replicates use seed
offset SEED+50000+i (registered)." Anchor: test_mde_sim.py.

## C10 (App B.2/B.3) — FSSA reconciliation [EXPLICITLY SUBMITTED FOR RULING]
v0.5's App B.3 exclusion line ("Financial System Stability Assessments") and
the code's include-with-flag behavior diverged (round-7 finding). v0.6
resolves the ambiguity SYMMETRICALLY to the combined-with-program rule:
"Article IV reports co-titled with an FSSA are IN frame, flagged
fssa_cotitled=true, with a prespecified sensitivity re-estimating the IMF
series excluding them. STANDALONE FSSAs (titles lacking 'Article IV
Consultation') remain excluded." Rationale: the unit is the Country Report;
an Article IV co-published with its FSSA is Article IV surveillance, and
exclusion would delete legitimate coverage on the FSSA cycle. We flag this
choice for the round-8 ruling explicitly. Anchor: test_fssa_*.

## C11 (App B) — Live acquisition obligations now executable
"WB: every raw API PAGE is archived verbatim (query params, totals, facets,
server payload) via the s01 page hook to data/meta/wb_p0_raw/, with an
append-only request log and page counts. IMF: s09a implements the SPROLL
live layer — paginated capture archiving every raw HTML page plus request
log and page-count log, gated by --i-am-in-stage-b (now operational), with
the captured listing CSV archived before frame construction. The
markup-specific SPROLL row pattern is a documented structural assumption
verified at Stage-B via an s00-style probe before the frame snapshot; any
divergence is amended in the Stage-B SAP addendum, never silently."
Anchor: test_page_hook_*, test_fetch_live_sproll_*, test_parse_sproll_*.

## C12 (SS11.6 + App B) — Evidence binding v3; docty Stage-B mechanism
"(a) The package builder FAILS CLOSED: regeneration failure, a missing
referenced log or ruling, or (in freeze-fields runs) a dirty working tree
aborts packaging. (b) Referenced logs and round rulings are COPIED into the
package (evidence/*.log, evidence/rulings/*.md) before the manifest is
written, so every recorded hash is verifiable from inside the zip. (c) Freeze
fields are disambiguated: zip_entry_count, sha256sums_entries, manifest_rows;
rulings is a name->sha256 map covering every archived round ruling. (d) An
optional git bundle (evidence/repo.bundle, --git-bundle) makes the recorded
commit independently verifiable; git_bundle_sha256 is recorded. (e) WB docty
labels: Stage-A ships EXPECTED strings in config/wb_p0_docty.yaml
(immutable). Stage-B runs the s00 probe and writes a verification JSON
(verified_utc, source, labels) that is timestamped inside the Stage-B SAP.
Live capture REFUSES to run without --docty-verified; corrected labels are
applied at runtime with every divergence logged. The Stage-A object is never
edited." Anchor: test_packager v3 tests, test_docty_verification_*.

## Declared unchanged
Estimand, priors on direction, thresholds, seed 20260806, offset registry
(now including P0 PASS-P +50000), UNGDC firewall, the 31 Oct 2026 Stage-B
deadline, the NLL >=100-token deferral, and the SS11.1 ordering (timestamp
BEFORE any comparator metadata acquisition).
