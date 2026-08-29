# Third-eye review instructions — Round 8 (post round-7 repair sprint)

You are the same independent methodological auditor. Round 7 returned REJECT
WITH REQUIRED CHANGES on five blocking areas plus two closure conditions.
This package claims to close ALL of them. Your job is a fresh BINARY ruling:
APPROVE FOR STAGE-A TIMESTAMPING or REJECT WITH REQUIRED CHANGES. Recompute,
don't trust — including everything we assert below.

## 0) Integrity gate (as before)
Verify zip sha256/size against the attached freeze_fields JSON; SHA256SUMS
and MANIFEST.tsv in full; no forbidden entries. NEW: the freeze fields now
use zip_entry_count / sha256sums_entries / manifest_rows (disambiguated per
your round-7 note) and every referenced log and ruling is INSIDE the package
under evidence/ — recompute their hashes from the contained files. If
evidence/repo.bundle is present, verify git_bundle_sha256 and that the bundle
resolves the recorded commit.

## 1) Verify the seven round-7 counterexamples now FAIL to reproduce
Each has a named regression test; rerun the suite AND re-run your original
counterexample inputs directly:
 (a) integer 1000000.4 -> ValueError (test_integer_contract_exact_rejects_
     near_integer);
 (b) "Trinidad and Tobago" -> TTO in BOTH builders; "Kenya; Uganda" and
     "Western Africa" still excluded (test_tto_*, test_true_multi_*);
 (c) 16-row G1 sheet -> g1_pass=false + sheet_size_valid=false; draw refuses
     <20 (test_g1_*);
 (d) holm_family({}, [], p0_failed=False) -> raises invalid-state; valid
     fallback preserved (test_family_*);
 (e) [1994]+[1997..2025] -> bins fine, reference (2008,2010), no
     StopIteration (test_make_bins_gap_sequence_no_stopiteration);
 (f) 75% actual post-token support -> infeasible with reported shares
     (test_std_75pct_support_infeasible); zero-coverage post cell ->
     explicit infeasible (test_std_zero_coverage_post_cell_explicit);
 (g) NB2 fallback fail-closed (test_estimation_ci_jackknife_failed_state,
     test_jackknife_multi_fail_closed).

## 2) Rule on the five blocking areas
 (1) Acquisition: s09b archives EVERY raw page + request log (fixture
     test_page_hook_archives_every_raw_page); s09a now has a genuine
     paginated SPROLL live layer with per-page raw HTML archiving and an
     operational --i-am-in-stage-b gate (test_fetch_live_sproll_*). Note the
     DECLARED structural-assumption status of the SPROLL row pattern
     (amendment C11) and rule on whether Stage-B verification of the markup
     is an acceptable residual.
 (2) MDE: per-panel templates/rates, docs-column honoring, --p2-start-year,
     and --family p0 SINGLETON mode at alpha=0.05 under which G4 is computed
     (amendment C9; tests test_mde_sim.py). Confirm the smoke path is
     numerically unchanged.
 (3) Standardization: the distinct ACTUAL >=0.80 post-token support gate,
     reported shares, explicit zero-coverage failure (C8). Re-run your 75%
     construction.
 (4) Event study: observed-count bin merge, lower-median reference, and full
     PASS-E machinery via bootstrap_engine.passe_multi with offset 600000
     (C4/C5). Verify the estimation_ci selftest remained bit-identical (the
     five frozen lines) — the refactor deliberately left its loop untouched
     and single-sources only the escalation constants.
 (5) Contract/NB2/family: C6/C7.

## 3) Rule on the amendments
PREREG_v0.6_AMENDMENTS.md defines v0.6 over v0.5. C10 (FSSA co-titled
include-with-flag + sensitivity, standalone excluded) is EXPLICITLY submitted
for your ruling as a text-code reconciliation — accept, or direct exclusion.
C12(e) is the frozen Stage-B docty mechanism you required. Rule on each
amendment's adequacy, not only its existence.

## 4) Branch decision + family states
s14_branch_decision: priority order, one-way rule, write-once (test_s14).
The synthetic family-state run you required — {P0}, {P1,P2}, {P1}, {P2},
valid fallback, invalid raise — is test_family_five_states_synthetic.

## 5) Runtime
python -m pytest tests/ -q (expect 93 passed), the selftest (five frozen
lines, bit-identical), make smoke (calibration_ok=false ->
full_nested_pass_p; unchanged numbers). Evidence of the pinned-3.11.9 rerun:
evidence/tests.log and evidence/selftest.log inside the package. Cross-stack
drift <=1e-13 on |z| statistics remains the documented tolerance.

## 6) Ruling
Binary, with ranked required changes if REJECT. The Stage-A object will only
ever be timestamped from a package you have approved; post-approval changes
remain limited to the enumerated corrections, immutable metadata, and
typography, exactly as your round-7 editor section defines.
