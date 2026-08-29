# Round-7 third-eye review

**Package reviewed:** `round7_package_20260810.zip`  
**Freeze fields reviewed:** `freeze_fields_r7.json`  
**Primary question:** whether `docs/PREREG_DRAFT_v0.5.md` may be frozen as the Stage-A protocol.  
**Disposition:** the package passes its integrity and advertised smoke gates, but the executable protocol still diverges from v0.5 in acquisition, branch selection, P0 power, standardization support, event-study inference, family-state handling, and archive binding. These are not line-edit-only defects.

# Sprint verification

## 1. Package integrity

**RECOMPUTED — PASS.**

| Check | Result |
|---|---|
| ZIP SHA-256 | `3ebf7db6447b43e2e1e1d4f3481a3f7f57b316a931b6186c32756a649be174a3`; matches the attached JSON |
| ZIP bytes | `1,718,795`; matches |
| ZIP entries | `122`; matches |
| `SHA256SUMS` | 121 entries; zero failures |
| `MANIFEST.tsv` | 120 data rows; every listed byte count and SHA-256 recomputed correctly |
| MUST-EXIST paths | all present |
| Forbidden entries | no `.DS_Store`, `__pycache__`, or `*.pyc` in the supplied ZIP |

The 120 manifest rows, plus `MANIFEST.tsv` in `SHA256SUMS`, plus `SHA256SUMS` itself in the ZIP, explain the 120/121/122 counts. The generic JSON field name `entry_count` is therefore a ZIP-entry count, not a `SHA256SUMS` line count; the freeze record should name both explicitly.

## 2. Runtime gates

**RECOMPUTED — PASS on the available stack.**

- `python -m pytest tests/ -q` returned **50 passed**.
- `python src/bootstrap_engine.py --selftest` reproduced the four advertised cases and duplicate rejection:
  - null-large: beta = -0.137, p = 0.117, CI [-0.300, 0.011];
  - effect-large: beta = +0.765, p = 0.003, CI [0.623, 0.898];
  - null-small: beta = +1.104, p = 0.193, CI [0.157, 2.020], floored = 0.0316;
  - NB2-overdispersed: beta = -0.310, p = 0.257, alpha-hat = 0.035;
  - duplicate rejection: OK.
- The prescribed MDE smoke returned `calibration_ok: false` and then printed `curve decision engine: full_nested_pass_p`.
- `tests/test_battery.py` returned **7 passed**; the dedicated same-PASS-E trend test passed.

The available runner was Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, statsmodels 0.14.6, and pytest 9.0.2. The declared pinned stack is Python 3.11.9 with NumPy 1.26.4, pandas 2.2.2, statsmodels 0.14.2, and pytest 8.2.2. The exact pinned-stack rerun is therefore **NOT RECOMPUTABLE** here. Matching seeded values on this third stack are useful evidence, not a substitute for the standing pinned-stack obligation.

## 3. Code-prereg verification

### A. Acquisition and P0 branch construction — blocking

1. **The IMF live acquisition layer claimed by Appendix B does not exist.** `src/s09a_imf_articleiv_frame.py` requires `--listing`; `--i-am-in-stage-b` is parsed but unused. There is no request routine, pagination routine, request log, page-count log, or raw-HTML archive. The module is a deterministic transformer for an already captured CSV, not the frozen SPROLL/eLibrary capture layer described in its own docstring and Appendix B.1.

2. **The WB code does not archive every raw API page.** `s09b_wb_p0_frame.fetch_live` calls `s01_fetch_metadata.fetch_stratum_year`, which discards each HTTP payload and returns one combined record list. `s09b` then writes one parsed aggregate JSON file per genre-year. This is not page-level raw-response archiving and cannot reproduce request parameters, page boundaries, facets, `total`, or server payloads.

3. **The IMF exclusion rules are not implemented exactly.** A constructed title, `Canada: 2024 Article IV Consultation and Financial System Stability Assessment; IMF Country Report No. 24/321`, was marked `fssa_cotitled=True` but still returned `status='included'`, although Appendix B.3 excludes Financial System Stability Assessments.

4. **The frozen `" and "` regional token misclassifies real single-country names.** After adding the proper alias, `Trinidad and Tobago` was still rejected as `excluded_regional_multicountry` by both IMF and WB country resolvers. This is a deterministic frame error, not an alias-coverage issue.

5. **G1 does not enforce the required denominator.** A 16-row sheet with all four items equal to 1 returned `n=16`, `n_pass=16`, `g1_pass=True`. The frozen rule is at least 16 **of 20**. `draw` also silently returns fewer than 20 rows when the candidate frame is short. A short candidate pool must fail or enter a prespecified alternative state; it cannot be treated as 16/20.

6. **G3 and the priority-ordered four-gate P0 decision are not executable.** No module computes the requirement that at least 80% of post-period candidate documents lie in country cells supported in both institutions. No orchestration evaluates G1-G4 in priority order and freezes the first passing CEM/SCD/CPF candidate. `s09b` emits only G2 coverage inputs.

7. **The declared-open WB facet-label item is not safely governed.** `config/wb_p0_docty.yaml` contains expected labels and says corrections will be logged after the Stage-B probe, but the Stage-A archive is declared immutable and `s09b` has no separate Stage-B override/config-output argument. If a label differs, the current instructions require changing a frozen file or running unverified strings. A deterministic, separately timestamped Stage-B override artifact must be frozen now; “label-agnostic” code alone does not resolve the governance conflict.

The WB unit, latest-version tie-break, comma-inversion, cutoff, and fixture-mode Stage-B live gate are otherwise implemented as written.

### B. MDE and G4 — blocking

The failed-calibration fallback itself is repaired, but the branch-specific design required by v0.5 is not.

- `mde_sim.py` accepts one year-to-token vector and one `base_rate`; that same token vector and rate generate the IMF series, WB-P1, and WB-P2. It cannot consume distinct IMF/P1/P2 observed token sequences or panel-specific pre-period rates.
- `--cells-template` reads only one `tokens` series indexed by year. The `docs` column produced by `make_cells_template.py` is ignored by the simulation.
- Every power replicate calls the two-panel `holm2` procedure. There is no P0 singleton mode tested at alpha = 0.05. Consequently the P0 G4 gate cannot be computed under the family actually frozen for P0.
- The calibration check is marginal to one generated panel, while its result authorizes a Wald shortcut for a joint Holm-family curve. No family-level calibration fixture exists.
- No pytest test imports or exercises `mde_sim.py`; the command-line smoke proves only that the fallback branch fires, not that branch-specific/P0 power is correct.

`make_cells_template.py` correctly computes the isolated P0 projection `yearly document count × supplied pooled tokens/document`. The defect is the simulation interface and family logic into which that template is wired.

### C. Composition standardization and ESS — blocking implementation gap

The replacement direct-standardization estimand is a real repair. The exact ESS rendering is also mathematically faithful: if each token in group g receives weight pi-tilde-g divided by token-mass-g, the Kish effective token count is

`1 / sum_g(pi-tilde-g^2 / token-mass-g)`;

it equals total supported tokens when target weights match supported token shares and declines when target mass is concentrated on thin groups. The expression itself does not block the freeze.

The surrounding frozen support rule is absent, however. `standardized_variant` checks pi-mass cell coverage and the 0.50 ESS floor, but never computes or reports the actual fraction of post-period tokens in common-support groups. In a recomputed case where common-support groups contained only **75%** of each institution's post tokens, the code returned:

- `min_post_coverage = 1.0` for both institutions;
- ESS / total tokens = 0.75 for both post periods, hence ESS passed;
- `feasible = True`.

The preregistration requires failure below 0.80 and reporting the excluded token shares. The ESS floor is not a substitute for that separate gate. In addition, `standardize_cells` silently drops an institution-year with zero retained pi mass rather than returning an explicit infeasible result; that can alter or crash the frozen common-year sequence downstream.

### D. Event study and interpretation battery — blocking divergence

The trend CI, H-SHARED, and placebo components pass the requested checks:

- `WB_cyear` is recorded from the same PASS-E draws as the primary CI;
- H-SHARED implements the IMF-only pooled log-rate difference, +0.5 rule, circular block-3 resampling, and counts empty-period draws as failures;
- the 2016 placebo uses the <=2022 subset, substitutes `WB × post16`, and calls PASS-P;
- the registered PASS-P/PASS-E/event/H-SHARED seed ranges are disjoint at B=9,999, while the same-seed reuse across variants is expressly frozen.

The event study does not pass:

1. `make_bins` decides whether the earliest bin contains fewer than two **observed** years by testing its calendar span (`hi-lo+1`), so a two-year span with only one observed year is not merged.
2. With a valid gap-permitted sequence `[1994] + [1997,...,2025]`, it raises `StopIteration`: the median is 2010.5, lying between the integer-ended [2008,2010] and [2011,2013] bins. The preregistration explicitly permits calendar gaps.
3. Its transplant loop is not “otherwise identical to §4.2”: it does not report true flooring, the small-count flag, a Wald-bootstrap interval, the >1% governing-CI switch, the >50% failure state, noninteger reconstruction mode, or the NB2-to-jackknife fallback. It always returns raw percentile CIs if any draw survived.

The validation outcomes are implemented, but the CLI makes `--docs` optional and can return a passing confirmatory panel without running the mandatory prevalence/breadth consistency downgrade. The battery should fail closed when validation inputs required for a confirmatory report are absent.

### E. Input contract, fallback handling, and family states — blocking

1. **Integer validation is approximate rather than exact.** `build_design` uses `np.allclose(count, round(count))` with default relative tolerance. A count of `1,000,000.4` was accepted in integer mode. Use an exact integral-value test after finite/range validation, not scale-dependent tolerance.

2. **The NB2 fallback is not fail-closed.** Initial NB2 non-convergence enters `jackknife_ci`, but that function neither checks returned convergence flags nor catches deletion-fit failures. If the fallback also fails, the battery can raise and abort rather than return the frozen “affected condition fails” state.

3. **The impossible zero-family state is mislabeled.** `holm_family({}, [], p0_failed=False)` returns `state='fallback'`, identical to the valid `p0_failed=True` case. The preregistration states that fallback requires P0 failure and that “no active primary” cannot arise. Invalid state combinations must raise, not be silently converted to fallback.

4. In family CLI mode, each panel's embedded `panel_pass` is first computed at the default 0.05 before the family-level Holm decision is recomputed. The final family decision is generally correct, but the JSON can contain contradictory panel-level pass fields. The family result must be the sole governing pass field or the preliminary field must be clearly labeled non-governing.

## Ranked sprint actions

1. **Blocking:** implement genuine, gated IMF live capture and genuine page-level WB raw capture; add request/page logs; repair FSSA and single-country classification; enforce exactly 20 G1 rows; implement G3 and the priority-ordered G1-G4 branch decision.
2. **Blocking:** redesign `mde_sim.py` around separate IMF, P1, P2, and P0 templates/rates and explicit `{P1,P2}` Holm versus `{P0}` singleton modes; add deterministic pytest fixtures for each branch and calibration state.
3. **Blocking:** enforce the actual >=0.80 post-token common-support gate, report excluded shares, and fail explicitly on zero-coverage institution-years.
4. **Blocking:** repair gap-permitted event bins and route event-study inference through a generalized PASS-E implementation with the frozen escalation/failure mechanics.
5. **Blocking:** replace approximate integer checking; make the NB2 jackknife fallback convergence-aware and fail-closed; reject impossible family-state inputs.
6. Require mandatory validation inputs in confirmatory battery mode and remove contradictory pre-Holm `panel_pass` output.
7. Archive a full pinned-stack rerun after the code changes; do not treat the 50 green current tests as coverage of the counterexamples above.

# Stage-A ruling

## 1. v0.5 weave against v0.4 and the amendments

The prose diff is substantial and it touches all nine Round-6 themes. The change log is not the problem. Executable closure is:

| Round-6 item | Round-7 status |
|---|---|
| B1 failed-calibration nested curve | closed for the advertised fallback |
| B2 NB2 score/dispersion/fallback | score and dispersion closed; fallback-fails path incomplete |
| B3 input contract | duplicate/finite rules closed; exact integer rule defective |
| B4 direct standardization | estimand repaired; frozen token-support gate/reporting absent |
| B5 frame builders/G1 | not closed: IMF live layer absent, WB raw-page claim false, frame rules and G1 denominator defective, G3 absent |
| B6 four-state family | prose repaired; executable invalid-zero state and output governance remain |
| B7 joint branch-specific MDE | joint skeleton present; distinct templates/rates and P0 singleton gate absent |
| B8 validation/interpretive battery | trend/H-SHARED/placebo largely closed; event study and fail-closed orchestration not closed |
| B9 archive binding/governance | immutable wording and package hashes improved; evidence/ruling/log binding incomplete |

Thus the items from the Round-6 report still materially unaddressed are: executable source acquisition and branch gating; truly branch-specific P1/P2/P0 MDE; complete support/ESS enforcement; exact singleton/fallback implementation; fully specified event-study PASS-E behavior; and a complete, independently retrievable freeze evidence bundle. The direct-standardization formula, NB2 quasi-score factor, duplicate rejection, full-nested fallback, calendar wording, and explicit NLL deferral are real repairs.

## 2. Declared-open items

1. **WB docty labels — blocks as currently governed.** Verification at Stage-B is legitimate, but the package lacks a frozen mechanism for placing corrected labels in a new Stage-B artifact without editing the immutable Stage-A config. Add that mechanism and deterministic rule before freezing.
2. **Pinned environment — conditionally nonblocking in design, unsatisfied in evidence.** `.python-version` and both direct requirement files are present and hashed; a missing optional transitive lock is transparently null. The exact pinned-stack rerun and its retrievable logs remain a pre-timestamp obligation and are not independently available here.
3. **External timestamp channel — nonblocking logistics.** OSF versus Zenodo/OpenTimestamps does not change the analysis protocol, provided the complete archive, record, and evidence are timestamped together.
4. **ESS rendering — formula nonblocking; implementation blocking.** The formula is correct. The separate 0.80 token-support condition is missing.
5. **NLL >=100 filter — nonblocking.** v0.5 now explicitly says the archived s06 outputs have not yet received the filter and freezes regeneration before any NLL reporting. It remains exploratory.

## 3. Stress-test disposition

- **ESS_tok:** faithful expression; correct thin-cell failure direction; incomplete surrounding gate.
- **Four-state family:** Holm pair and singleton thresholds work on covered fixtures; invalid zero state is silently converted to fallback, and singleton headline/reason output is incomplete.
- **Event-study bins/PASS-E:** fail under allowed calendar gaps and omit frozen PASS-E escalation mechanics.
- **H-SHARED:** passes the exact estimand/resampling/failure check.
- **2016 placebo:** passes the prescribed subset/column-substitution/PASS-P check.
- **Seed registry:** no registered offset collision at B=9,999; same-PASS-E trend sharing and same-seed variant reuse are intentional. The MDE script has its own undeclared common-random-number reuse across theta values, which should be frozen explicitly if retained.
- **Appendix B.10:** unit, deterministic version rule, cutoff, and basic Stage-B gate pass; raw-page archiving and country classification do not.
- **Archive binding:** the ZIP hash is sufficient to detect a post-timestamp edit to that exact ZIP, but the current record does not yet make all claimed evidence independently retrievable and does not distinguish the two ruling hashes.

The failures change who enters the comparator frame, whether P0 is selected, what G4 means, whether condition 2 is feasible, how event-study intervals are formed, and whether fallback is legally entered. Freezing v0.5 now would timestamp multiple analysis paths that the released code does not implement.

## Ranked Stage-A actions

1. **Blocking:** close the acquisition/G1/G3/branch-decision defects and add counterexample tests for FSSA, `Trinidad and Tobago`, fewer-than-20 G1 candidates, and page-level raw-response preservation.
2. **Blocking:** implement distinct P1/P2/IMF templates and a P0 singleton MDE mode; make G4 an executable branch-specific decision rather than a generic two-panel curve.
3. **Blocking:** implement and test the 0.80 actual token-support gate and zero-coverage failure state.
4. **Blocking:** repair event-study construction for arbitrary frozen common-year sequences and reuse the complete PASS-E escalation/failure engine.
5. **Blocking:** repair exact integer validation, NB2 fallback failure handling, and invalid family-state rejection.
6. **Blocking before timestamp:** regenerate a complete archive that includes or externally co-binds retrievable test, selftest, and calibration evidence, both ruling hashes, and a verifiable commit/archive relation; rerun the entire suite on Python 3.11.9 with the declared pins.
7. Submit the exact repaired package to a new binary freeze review; do not apply these as unreviewed post-approval edits.

**REJECT WITH REQUIRED CHANGES.**

# Editor

## 1. Freeze record and attached JSON

The record's governance sentence is corrected: the Stage-A object is immutable and Stage-B values belong in a new timestamped SAP. The template is not yet a completed freeze record.

**Recomputed and matching non-null fields:**

- ZIP SHA-256, bytes, and 122-entry count;
- `SHA256SUMS` SHA-256;
- `MANIFEST.tsv` SHA-256;
- Python-version content and SHA-256;
- `requirements.txt` and `requirements-ppl.txt` SHA-256s.

**Transparent null:** `requirements_lock_sha256`; v0.5 describes this as optional when no lock exists.

**NOT RECOMPUTABLE from the package held:**

- `git_commit`: the ZIP has no repository metadata or retrievable commit object against which to verify `bfbfd0827a923910acfc35e53987fe5852001e26`;
- `logs.tests` and `logs.selftest`: their source files are absent from the ZIP and attachments, so the hashes bind unknown bytes;
- a calibration log: the record requires it, but the JSON has no calibration-log field;
- the relation between the attached JSON and the eventual timestamped freeze record, because the record still contains placeholders.

`ruling_sha256` is null, as expected before this ruling, but one generic field is insufficient for the record's separately named Round-6 and approving-round ruling hashes. `ROUND6_THIRD_EYE_REVIEW.md` is not in the supplied archive. The record should also distinguish `zip_entry_count=122`, `sha256sums_entry_count=121`, and `manifest_rows=120`.

The packager now really writes `MANIFEST.tsv`, which closes the prior doc-code mismatch. A new mismatch remains: `regeneration_check` catches any exception, prints a warning, and continues packaging. A freeze builder must fail closed on a failed required regeneration check.

## 2. What may change before a future timestamp

Because this ruling is rejection, the current package must not be frozen or timestamped as Stage-A.

After a later approval, the approval-to-timestamp interval may contain only:

1. corrections expressly enumerated in that approving ruling;
2. insertion of immutable hashes, dates, commit/build metadata, and external registration identifiers;
3. typography or formatting with no semantic effect.

It may not introduce or alter docty labels, requests, frame rules, branch results, G1 decisions, support/ESS results, common-year sequences, MDE/calibration results, active families, thresholds, estimators, or code behavior unless the approving ruling explicitly reviewed those exact changes. Stage-B values go only into the new SAP.

## 3. Deadline, fallback, and deferred work

The hard **31 October 2026** Stage-B go/no-go date survives v0.5. Read together, §§2, 5, and 11 now specify the intended prose rule: P0 failure alone activates the viable P1/P2 family; one viable comparator becomes a singleton; fallback occurs only when P0 failed and neither comparator is viable; a selected P0 that later fails is not replaced. The executable zero-state defect must be repaired before relying on that rule.

The deferred full s12 diagnostics, NLL regeneration including the >=100-token filter, QC grid, and method interactions remain legitimate post-SAP work. They contain no hidden Stage-A blocker as presently disclosed. The blocking findings above define acquisition, branch selection, condition-2 feasibility, G4 power, primary-family state, and frozen inference; they are not deferred robustness work.

## 4. Ranked editor actions

1. Do not freeze, register, or begin comparator metadata acquisition under the current v0.5 package.
2. Require one repair sprint addressing every blocking counterexample in this report, with regression tests that fail on the current code.
3. Require a genuine branch-decision dry run on synthetic metadata covering `{P0}`, `{P1,P2}`, `{P1}`, `{P2}`, and valid fallback, without accessing live outcomes.
4. Require the complete pinned-stack logs, family-level MDE fixtures, raw-page capture fixtures, both ruling artifacts, and a verifiable commit/archive relation in the next package.
5. Make the package builder fail closed on regeneration, missing required evidence, invalid state combinations, and unpopulated final freeze fields.
6. Preserve the 31 October 2026 deadline and the explicit NLL deferral; neither should be reopened while repairing the Stage-A blockers.
