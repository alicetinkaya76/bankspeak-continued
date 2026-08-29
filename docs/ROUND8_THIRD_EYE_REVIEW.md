# Round-8 third-eye review

**Package:** `round8_package_20260810.zip`  
**Freeze fields:** `freeze_fields_r8.json`  
**Review date:** 2026-08-11  
**Mandate:** fresh binary ruling on Stage-A timestamping after the Round-7 repair sprint.

# Binary ruling

## **REJECT WITH REQUIRED CHANGES**

The package passes the integrity gate, the embedded Git bundle genuinely resolves the recorded commit, all 93 named tests pass, the five-line selftest is bit-identical, the smoke path is unchanged, and the seven Round-7 counterexamples no longer reproduce.

Those successes are real. They are not sufficient for approval. Fresh direct probes expose four substantive analysis-path failures and one evidence/governance closure failure:

1. the `{P1,P2}` MDE path parses but does not use the IMF-specific template or base rate;
2. the live acquisition layers can silently accept incomplete/error pages, WB does not archive the verbatim server response, and the docty “verification” file is not semantically validated;
3. an allowed gap-containing common-year sequence creates an unobserved event-study bin that is nevertheless reported with a spurious near-zero coefficient and CI;
4. the standardized path does not report the required diagnostics in all infeasible states and can mask an explicit zero-coverage post cell behind the aggregate support gate;
5. the package still lacks independently adequate pinned-stack/calibration evidence, and the freeze builder does not fully fail closed.

These defects affect frame completeness, G4 and branch selection, condition-2 feasibility, and an inferential display frozen into the preregistration. The current object must not be timestamped as Stage-A.

# 1. Integrity gate — PASS

I recomputed the archive and internal inventories rather than trusting the supplied fields.

| Item | Recomputed result |
|---|---:|
| ZIP SHA-256 | `bdc4b42e86d2f27852f3079b2a07a8cbacbbeab99cd527a9c8c34b65408d62b9` |
| ZIP bytes | `5,974,794` |
| ZIP entries | `135` |
| `SHA256SUMS` entries | `134`; every entry passed |
| `MANIFEST.tsv` rows | `133`; every byte count and hash passed |
| `SHA256SUMS` exact inventory | PASS |
| `MANIFEST.tsv` exact inventory | PASS |
| Unsafe paths / symlinks / special entries / packaged junk | none found |
| `evidence/tests.log` hash | matches freeze fields |
| `evidence/selftest.log` hash | matches freeze fields |
| `evidence/rulings/round7.md` hash | matches freeze fields |
| `evidence/repo.bundle` hash | matches freeze fields |

`git bundle verify` passed. The bundle contains a complete history and resolves both `HEAD` and `main` to recorded commit `56c972d0b626e87b19cfbb4ffe53810b21c19af4`. I compared packaged tracked blobs against that commit: **105/105 packaged tracked blobs were byte-identical; zero mismatches**. The remaining packaged files are generated analysis/data artifacts or embedded evidence.

**Integrity disposition:** no stop condition was triggered.

# 2. Runtime and Round-7 counterexamples

## 2.1 Re-executed runtime

On the available review runtime, Python 3.13.5:

- `python -m pytest tests/ -q` → **93 passed, 1 warning**;
- `python src/bootstrap_engine.py --selftest` → all five frozen lines byte-identical to `evidence/selftest.log`;
- `make smoke` → unchanged signature:
  - `calibration_ok=false`;
  - decision engine `full_nested_pass_p`;
  - null family power `0.033333`;
  - θ=0.9 family power `0.933333`;
  - MDE80 `0.9`.

The exact Python 3.11.9/pinned dependency stack could not be independently installed in this isolated review environment. That limitation does **not** drive the rejection: the substantive failures below are deterministic code-path defects. It does matter for the still-open evidence closure condition discussed in §7.

## 2.2 Seven named Round-7 counterexamples — all closed

| Counterexample | Direct result |
|---|---|
| `1000000.4` in integer mode | raises `ValueError` |
| `Trinidad and Tobago` | resolves to `TTO` in both builders |
| `Kenya; Uganda` / `Western Africa` | remain excluded |
| 16-row G1 sheet | `sheet_size_valid=false`, `g1_pass=false`; draw refuses |
| invalid no-family state | raises; valid fallback remains reachable |
| `[1994]+[1997..2025]` | bins construct; reference is `[2008,2010]`; no `StopIteration` |
| 75% token support | infeasible with reported ~0.75 shares |
| zero-coverage post cell | explicit `zero_coverage_post_cell` in the named fixture |
| NB2 fallback failure | `jackknife_failed`, governing CI `failed`, `B_valid_ci=0` in both engines |

The synthetic `{P0}`, `{P1,P2}`, `{P1}`, `{P2}`, valid fallback, invalid-state, and priority/one-way branch scenarios also pass.

# 3. Blocking finding 1 — acquisition and docty verification remain fail-open

This blocks C11 and C12(e).

## 3.1 IMF SPROLL: HTTP/markup failure is silently treated as normal pagination end

`src/s09a_imf_articleiv_frame.py:177-209`:

- never calls `raise_for_status()` or otherwise requires a successful response;
- decodes `r.text`, parses it, and stops whenever the parser returns zero rows;
- therefore cannot distinguish the legitimate terminal page from HTTP failure, CAPTCHA, consent page, maintenance page, or markup drift.

**Direct counterexample:** a session returning HTTP 500 with an error HTML body produced no exception. The function archived the body, logged status 500, printed `page 1: 0 rows`, then returned a zero-row DataFrame as a completed capture.

That is incompatible with C11's promise that structural divergence is verified/amended and “never silently” accepted. A Stage-B structural assumption is an acceptable residual only when failure of that assumption is detectable and fail-closed. Here it is not.

Additional preservation defects:

- “raw” is reconstructed from decoded text rather than archived response bytes;
- the request log is opened with mode `w`, not append-only or run-isolated;
- fixed page filenames overwrite a prior attempt;
- exhaustion of `max_pages` is returned as success rather than an incomplete-capture state.

## 3.2 WB WDS: the archived object is parsed/canonicalized JSON, not the verbatim page

`src/s01_fetch_metadata.py:27-37` parses `.json()` before invoking the page hook. `src/s09b_wb_p0_frame.py:219-233` then serializes the Python object with sorted keys. Consequently the hook never sees response bytes, headers, or the original server serialization.

**Direct counterexample:** a deliberately formatted valid response and its parsed payload produced one returned record, but the archived page was not byte-equal to the server response. The response's ordering/whitespace was replaced by canonical JSON. This directly contradicts C11's “every raw API PAGE ... archived verbatim” language.

Completeness also fails closed inadequately: with `total=3` and an empty parsed documents page, `fetch_stratum_year` returned zero records without raising because `not batch` terminates the loop (`src/s01_fetch_metadata.py:34-37`). A truncated, malformed, or schema-shifted response can therefore become a successful empty stratum.

The append-only CSV does not cure this: fixed `{genre}_{year}_os{offset}.json` names overwrite raw pages on a rerun, while the log appends another record pointing to the overwritten filename.

## 3.3 Docty verification is existence-gated, not content-verified

C12(e) freezes a verification JSON with `verified_utc`, `source`, and complete `labels`. Yet `apply_docty_verification` (`src/s09b_wb_p0_frame.py:243-262`) accepts any JSON object.

**Direct counterexample:** `{}` was accepted without exception and the expected label was passed through unchanged. Thus `--docty-verified` presently means only “a readable JSON path was supplied,” not “the Stage-B facet probe verified all candidate labels.”

## Required repair

1. Require HTTP success, expected content type, parse/schema invariants, and explicit pagination-completeness invariants; all failures must abort with a recorded failed-capture state.
2. Archive `response.content` before parsing, hash those exact bytes, and preserve URL plus exact request parameters and response status/headers needed for audit.
3. Use immutable run-scoped filenames/directories and an append-only or write-once run manifest; no raw artifact may be overwritten by a retry/rerun.
4. Require an explicit terminal-page rule that cannot be mimicked by error markup, and fail when `max_pages` is exhausted.
5. Validate the docty JSON schema and semantics: nonempty `verified_utc`, approved `source`, exactly the expected genre keys, nonempty string labels, no unknown keys unless prespecified, and a binding to the probe artifact/hash.
6. Add regression tests for HTTP 500, 200-error/CAPTCHA HTML, parser drift, total/rows mismatch, max-page exhaustion, byte-verbatim preservation, rerun immutability, and empty/partial/malformed docty JSON.

# 4. Blocking finding 2 — C9 MDE is not actually per-panel in `{P1,P2}` mode

This directly affects family power, MDE80, and G4.

## 4.1 IMF template and base rate are parsed but ignored

The CLI loads `tok_imf` and `r_imf` at `src/mde_sim.py:181-186`. But both `{P1,P2}` calibration and curve calls invoke `simulate_joint(years, tokens, a.base_rate, ...)` at lines 205-209 and 262-266. Inside `simulate_joint`, the IMF series is generated from the legacy shared `tokens` and `base_rate` (`src/mde_sim.py:64-66`). There is no IMF-specific argument in that function.

**Direct counterexample:** I changed the IMF template from 1 token/year to `10^12` tokens/year and changed `--base-rate-imf` from `10^-12` to `0.1`, holding every other argument and seed fixed. The complete `{P1,P2}` power output was **byte-identical**. Therefore the advertised IMF inputs have no effect in the family that uses them.

C9's per-panel-input claim is false as implemented.

## 4.2 The calibrated shortcut does not apply the recorded critical value

The script reads `crit_abs_z` (`src/mde_sim.py:230-237`) but the curve decision uses ordinary two-sided normal p-values (`pw` at line 245) and Holm at lines 267-268. `crit` is never consulted.

**Direct counterexample:** two accepted calibration files differing only in `crit_abs_z` (`0.01` versus `100.0`) yielded byte-identical `wald_shortcut` power output. The calibration loop for `{P1,P2}` also computes acceptance only from the first returned panel (`cal, _` at line 205), despite panel-specific templates and P2's potentially shorter span.

Even if `crit_abs_z` was intended as diagnostic rather than governing, the supplied record does not bind and validate the actual two-panel/Holm shortcut decision rule used in the curve.

## 4.3 Missing template years are silently fabricated

`load_template` fills any absent year with `fallback_tokens` (`src/mde_sim.py:106-120`). A template containing 2023 and 2025 but omitting 2024 loaded as `[10, 999, 20]` rather than failing. This can silently invent exposure for a year absent from the frozen panel template/common-year sequence.

`--p2-start-year` handles a contiguous leading restriction, but the preregistration permits calendar gaps. The simulation interface still cannot consume an exact arbitrary frozen year sequence without fabricating missing years.

## Required repair

1. Pass `tokens_imf` and `rate_imf` through `simulate_joint` in both calibration and curve paths; add metamorphic tests proving each IMF/P1/P2/P0 template and each base rate changes the corresponding generated series/output.
2. Make template-year matching exact: duplicate years, missing requested years, extra/invalid years, nonpositive tokens, and invalid docs-derived exposures must fail closed. Accept an explicit exact-year sequence for gap-containing panels.
3. Calibrate the decision rule that will actually be used: both panel tests plus Holm/family rejection under the same templates, year subsets, rates, α, B, and seed registry. Bind these inputs in the calibration JSON and reject mismatches.
4. Either use the calibrated critical value in the shortcut or remove it and define/test a calibration criterion for the ordinary Wald/Holm rule. A field that can vary from 0.01 to 100 with no effect cannot be represented as governing calibration metadata.
5. Preserve and reassert the existing legacy smoke signature in a dedicated test.

# 5. Blocking finding 3 — allowed calendar gaps can generate a nonidentified event-study coefficient

C4 repairs only the earliest sparse bin. `make_bins` (`src/s13_validation_battery.py:215-241`) leaves interior bins untouched, including bins with zero observed common years. `event_study` nevertheless creates an interaction column for every nonreference bin and labels the result `status="ok"` (`src/s13_validation_battery.py:244-290`).

**Direct counterexample:** use the otherwise valid 1994–2025 sequence with 2002, 2003, and 2004 absent.

- usable pre-2023 years: **26** (therefore the ≥25 gate is met);
- post years: **2023, 2024, 2025**;
- generated bin `[2002,2004]`: **zero observed years**.

The function did not fail or merge/remove the bin. It returned:

- `status="ok"`;
- β ≈ `−7.48×10^-18`;
- percentile CI ≈ `[−5.16×10^-17, 4.60×10^-17]`;
- Wald-bootstrap CI ≈ `[−6.80×10^-17, 5.31×10^-17]`.

Those values are numerical artifacts of an all-zero, nonidentified design column, not an estimate. This violates the gap-permitted input contract and makes the event-study display potentially misleading even though the shared PASS-E machinery itself is present.

## Required repair

1. Define deterministic handling for **every** empty/under-supported bin, not only the earliest one: merge by a frozen rule or omit before the reference is chosen.
2. Before estimation, assert positive observed support and nonzero variance for every retained interaction; assert full design rank or an explicitly frozen estimability criterion.
3. Fail closed when any requested coefficient is absent/nonidentified.
4. Propagate the governing PASS-E failed state into the wrapper's top-level status rather than hard-coding `ok`.
5. Add fixtures for interior three-year gaps, multiple disjoint gaps, a gap containing the provisional reference, and failed PASS-E/NB2 escalation.

# 6. Blocking finding 4 — C8 reporting and zero-cell semantics remain incomplete

The original 75% support and straightforward zero-cell fixtures now pass. The amendment, however, requires support shares and excluded token shares in **feasible and infeasible outcomes alike**, and every zero-retained-π post cell to be explicit.

`standardized_variant` (`src/s13_validation_battery.py:341-390`) returns early in several paths:

- `no_common_support_groups` contains neither required diagnostic;
- `post_coverage_below_floor` returns only coverage;
- `ess_below_floor` returns only ESS.

**Direct probes:** both the coverage-failure and ESS-failure results lacked `post_token_support` and `excluded_token_shares`.

The order of checks also masks zero cells. Aggregate post-token support is tested before `standardize_cells` computes `dropped_cells`. In a construction with a zero-retained-π WB-2025 cell plus large unsupported token mass, the result was `post_token_support_below_0.80` and contained no `dropped_cells`. C8 says such a cell is an **explicit** infeasible state, never a silent drop.

## Required repair

1. Compute the full diagnostic object once before returning: π/common-support status, support shares, excluded shares, coverage by institution-year, dropped-cell full-set difference, and ESS.
2. Attach all available diagnostics to every feasible and infeasible return.
3. Report multiple simultaneous failure reasons, or freeze a priority rule that still always exposes zero-coverage post cells explicitly.
4. Add tests in which zero coverage co-occurs with aggregate support failure, coverage-floor failure, ESS failure, and no-common-support.

# 7. Blocking-before-timestamp finding — evidence binding and builder fail-closed semantics remain incomplete

The current archive is much stronger than Round 7: internal logs and the Round-7 ruling are hash-verifiable, the bundle resolves the commit, and packaged tracked files match that commit. C12(b)-(d) are substantially closed.

The closure condition is nevertheless not complete:

1. **Pinned runtime not independently attested.** `evidence/tests.log` shows a `python3.11` site-packages path, but records neither `python --version` nor installed package versions/hashes. It cannot establish Python **3.11.9 with the declared pins**. The exact version in `.python-version` is a declaration, not execution evidence.
2. **Calibration evidence is absent.** The freeze record and Round-7 closure condition require test, selftest, and calibration evidence. The package contains only `tests.log` and `selftest.log`; the freeze fields likewise contain no calibration entry.
3. **The earlier required ruling chain is incomplete.** Only `round7.md` is embedded. The freeze-record template separately names the Round-6 and later approving ruling artifacts.
4. **Clean-tree check fails open.** `require_clean_tree` treats a failing `git status` as clean (`tools/build_audit_package.py:120-131`). A direct non-Git-directory probe returned normally. The CLI also permits `--allow-dirty` during a `--freeze-fields` run despite the declared “never dirty” rule.
5. **Null final fields warn rather than abort.** `freeze_fields` prints a warning when `git_commit` or requirements are null and still emits a freeze record (`tools/build_audit_package.py:199-204`). Required evidence names are not enforced; an invocation can omit calibration/rulings entirely.
6. **The freeze record remains a semantically stale template.** `docs/STAGE_A_FREEZE_RECORD_v2.md` still says `TEMPLATE`, contains placeholders, and describes “PREREG v1.0 (= approved v0.5)” rather than the actual composite object `v0.5 + v0.6 amendments`.

## Required repair

1. Add one machine-readable environment record generated in the same command/session as the final tests: exact interpreter build, platform, dependency versions, hashes or lock, commands, exit codes, start/end UTC, and hashes of stdout/stderr artifacts.
2. Embed the actual calibration JSON/log and its complete input binding; include its hash in freeze fields.
3. Embed the complete required ruling chain; after a future approval, add the approving ruling only as the expressly allowed immutable metadata attachment.
4. Abort a freeze run when Git status/rev-parse fails, when the tree is dirty, when `--allow-dirty` is combined with `--freeze-fields`, when required logs/rulings are absent, or when any mandatory freeze field is null.
5. Finalize the freeze record for the actual composite preregistration object and hash both base document and amendment document (or one canonical rendered composite).

# 8. Amendment-by-amendment ruling

| Amendment | Ruling | Basis |
|---|---|---|
| C1 — G1 exactly 20 | **PASS** | 16-row score fails; draw refuses fewer than 20. |
| C2 — G3 executable | **PASS** | executable support calculation and tests present. |
| C3 — priority/one-way/write-once | **PASS** | synthetic branch scenarios pass. |
| C4 — bins/reference | **FAIL** | named leading-gap case fixed, but allowed interior empty bins remain nonidentified. |
| C5 — full PASS-E event machinery | **PARTIAL / NOT ADEQUATE** | shared machinery and constants are present; wrapper can request/report an unestimable coefficient and hard-codes top-level success. |
| C6 — exact integer/NB2 fallback | **PASS** | direct integer and dual fallback probes pass fail-closed. |
| C7 — invalid family state | **PASS** | invalid state raises; valid fallback preserved. |
| C8 — standardization gates/reporting | **FAIL** | diagnostics missing in several infeasible states; zero post cell can be masked. |
| C9 — branch-specific MDE | **FAIL** | IMF template/rate ignored in `{P1,P2}`; shortcut/calibration and year-template binding inadequate. |
| C10 — FSSA reconciliation | **ACCEPT** | co-titled Article IV+FSSA is included and flagged; standalone FSSA excluded. The frozen exclusion sensitivity must be emitted at Stage-B. |
| C11 — live acquisition | **FAIL** | silent HTTP/markup/total failure paths; WB page not verbatim raw response. |
| C12 — evidence/docty | **PARTIAL / FAIL AS A WHOLE** | hashes, internal evidence copies, disambiguated counts, and bundle pass; C12(a), C12(e), and closure evidence do not. |

# 9. Ranked required changes for Round 9

1. **Acquisition/docty:** make IMF and WB capture byte-verbatim, completeness-checked, run-immutable, and fail-closed; enforce the docty verification schema and probe binding.
2. **MDE/G4:** actually use IMF-specific inputs in `{P1,P2}`, require exact year/template matching, and calibrate/bind the same family decision rule used by the curve.
3. **Event study:** eliminate or deterministically merge every unsupported bin and enforce estimability/rank before PASS-E; propagate failed states.
4. **Standardization:** produce complete diagnostics in every outcome and explicitly surface zero-retained-π post cells even when another gate also fails.
5. **Freeze evidence/builder:** provide complete pinned-stack and calibration evidence, complete the ruling chain, make every mandatory freeze condition abortive, and correct the final record to the v0.6 composite object.

Each repair needs a regression test that fails on commit `56c972d0...`, plus the original 93-test suite, selftest, smoke, and direct counterexamples rerun on the exact pinned stack.

# 10. Final editor instruction

Do **not** freeze, timestamp, register, or begin comparator metadata acquisition under this Round-8 object. Submit one exact repaired package for a fresh binary review. Preserve the already closed items and do not reopen C10, the 31 October 2026 deadline, the NLL deferral, the estimand, thresholds, seed registry, or the accepted branch/family logic except where the ranked repairs above expressly require code-path correction.

## **FINAL RULING: REJECT WITH REQUIRED CHANGES**
