# Round-6 build plan — nine blockers, status and gate (2026-08-09)

| # | Blocker | Status tonight | Acceptance test |
|---|---|---|---|
| 1 | Nested MDE fallback | **CLOSED** (mde_sim v3; nested is default) | smoke shows `engine=full_nested_pass_p` when calibration_ok=false |
| 2 | NB2 alpha + score | **CLOSED** (engine v3) | `test_nb2_valid_score_runs`; α̂ formula frozen |
| 3 | Duplicate cells | **CLOSED** (engine v3) | `test_duplicate_cells_rejected` |
| 4 | Standardization | **CORE CLOSED** (`standardize.py`; §6 text in amendments) | `test_round6_counterexample_repaired` must yield (0.5, 0.5) |
| 5 | IMF + WB-P0 frame builders, G1 module | **s09a + G1 CLOSED (fixture level)**; s09b + live-capture archiving = BUILD NEXT | `test_imf_frame` (statuses, flags, ISO3, revision resolution, CR parser) + `test_g1_audit` green; Stage-B obligation: archive raw listing HTML |
| 6 | Joint P1/P2 Holm MDE | **CLOSED core** (joint sim + Holm + δ_t + MoM σ) | smoke family powers; Stage-B templates wired |
| 7 | Family four-state rule | **CLOSED (text)** | §2/§11 replacement in amendments B6 |
| 8 | Validation/placebo algorithms | **SPEC CLOSED**; orchestration **BUILD NEXT** | executable battery + tests (breadth, prevalence, trend-CI, H-SHARED, event-study, 2016 placebo, guard, LOPO) |
| 9 | Freeze record/archive binding | **CLOSED (text)** (record v2) | archive-hash field list per amendments B9 |

Also closed tonight: convergence counting, small-count flag, ties-to-even
freezing, governing-CI naming, noninteger PASS-E mode (engine v3, tested);
Wald-branch Holm in mde. Deferred and declared: s06 NLL≥100 patch (step 4).

**Round-7 gate:** request round 7 only after (a) the item-5 builders and
item-8 orchestration exist with green fixtures, (b) full PREREG v0.5 is
assembled from v0.4 + these amendments, (c) the freeze record v2 fields are
populated by `tools/build_audit_package.py` output. Until then, no external
round — the reviewer's time is spent only on complete packages.
