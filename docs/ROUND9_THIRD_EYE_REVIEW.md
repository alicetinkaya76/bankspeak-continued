# Round-9 Third-Eye Review

**Package:** `round9_package_20260811.zip`  
**Freeze fields:** `freeze_fields_r9.json`  
**Review date:** 2026-08-11  
**Reviewed commit:** `7fb89a56f02a84d6b214ad8a991f96d76fbed0b9`  
**Mandate:** fresh recompute-don't-trust binary ruling after the Round-8 repair sprint.

# Binary ruling

## **REJECT WITH REQUIRED CHANGES**

Round 9 is materially stronger than Round 8. The ZIP identity and complete internal hash inventory verify; the Git bundle is valid and resolves the recorded commit; the supplied Python 3.11.9 environment record matches every direct `requirements.txt` pin; all **116** tests pass; the five self-test lines are bit-identical; the smoke signature remains on the full nested engine; and the Round-9 regression file fails on the old Round-8 commit as intended.

Those successes are genuine. They are still not sufficient for Stage-A timestamping. Fresh direct probes expose unresolved failures in four frozen areas:

1. **C13 acquisition/docty remains fail-open:** WB archives decoded/re-encoded text rather than transport bytes, a malformed response can fail before any raw body is preserved, reruns overwrite the supposedly raw page, declared-total drift and schema-less `{}` responses can silently succeed, the IMF terminal rule can still be mimicked by error/interstitial HTML, and `probe_sha256` is never recomputed against an archived probe artifact.
2. **C14 MDE/calibration is not bound to the family decision it authorizes:** `{P1,P2}` calibration still uses only the first returned panel, changing the P2 template/rate leaves calibration byte-identical, the supplied calibration omits all material input bindings and uses `B=999` rather than the frozen production `B=9,999`, and a missing `crit_abs_z_half` falls back functionally while still reporting `engine=wald_shortcut`.
3. **C15 failure governance is incomplete:** the interior-gap merge and estimability guards are repaired, but `event_study` still hard-codes top-level `status="ok"` when the governing PASS-E result is `failed` with zero valid intervals.
4. **C17/C18 freeze governance remains insufficiently fail-closed:** the packager accepts nonsensical calibration values, accepts a skeletal environment assertion with no execution provenance, accepts one arbitrary ruling as “complete,” does not require the Git bundle for a freeze, and the v3 freeze-record template lacks the `built_utc` placeholder despite claiming one placeholder per freeze field.

These are not cosmetic defects. They affect the auditability and completeness of live frames, the validity of any accepted Wald shortcut, the truthfulness of inferential status reporting, and the claim that the frozen object can be reproduced and independently verified. The present object must not be timestamped as Stage A.

# 1. Integrity gate — PASS

I recomputed the archive identity and internal inventories rather than trusting the supplied freeze JSON.

| Item | Recomputed result |
|---|---|
| ZIP SHA-256 | `9b001c5bbc97107492609b68541606898c573350c66a2a12fc8ae1fb49a54812` — matches |
| ZIP byte size | `10,384,405` — matches |
| ZIP entries | `148` — matches |
| Duplicate names | none |
| Unsafe paths / symlinks / special entries / packaged junk | none |
| `SHA256SUMS` entries | `147`; exact clean-archive inventory; every hash passed |
| `MANIFEST.tsv` rows | `146`; exact clean-archive inventory; every byte count and hash passed |
| `SHA256SUMS` SHA-256 | matches freeze fields |
| `MANIFEST.tsv` SHA-256 | matches freeze fields |
| `evidence/tests.log` / `selftest.log` | hashes match freeze fields |
| Rulings r2/r3/r4/r7/r8 | all present; each hash matches freeze fields |
| `evidence/environment.json` | present; hash matches freeze fields |
| `evidence/calibration.json` | present; hash matches freeze fields |
| `evidence/repo.bundle` | present; hash matches freeze fields |
| Mandatory null fields | none |
| Declared optional field | `requirements_lock_sha256 = null` |

`git bundle verify` passed and reported a complete history. `HEAD` and `refs/heads/main` resolve to the recorded commit `7fb89a56f02a84d6b214ad8a991f96d76fbed0b9`. Every packaged tracked blob compared against that commit was byte-identical; no package/commit mismatch was found.

**Integrity disposition:** no stop condition was triggered.

# 2. Runtime and regression execution

## 2.1 Supplied pinned-stack evidence

`evidence/environment.json` reports:

- CPython **3.11.9**;
- macOS arm64;
- the project `.venv/bin/python` executable;
- exact matches for all ten direct pins in `requirements.txt`:
  `numpy 1.26.4`, `pandas 2.2.2`, `statsmodels 0.14.2`, `scipy 1.13.1`, `PyYAML 6.0.2`, `requests 2.32.3`, `pytest 8.2.2`, `matplotlib 3.9.0`, `PyMuPDF 1.24.9`, and `tqdm 4.66.4`.

The package's pinned-run log reports:

```text
116 passed, 1 warning in 56.55s
```

The five self-test lines are present and hash-bound.

### Explicit pinned-stack disposition

I **accept the narrow pin-consistency claim**: the environment JSON says Python 3.11.9 and every direct `requirements.txt` pin agrees with the declared file.

I **do not accept that JSON alone as complete same-session execution provenance**. It contains no executed commands, exit codes, start/end timestamps, stdout/stderr hashes, or binding from that runtime record to the supplied test/self-test logs. Its validator accepts a handcrafted record containing only `python_version` and a `packages` map. This limitation is an evidence-governance defect, but the rejection does not depend on it: the substantive counterexamples below reproduce directly from the reviewed code.

## 2.2 Independent execution

The isolated review environment had Python 3.13.5, not an installable local Python 3.11.9 runtime. On that independent runtime:

- `python -m pytest tests/ -q` → **116 passed, 1 warning**;
- `python src/bootstrap_engine.py --selftest` → all five lines byte-identical to `evidence/selftest.log`;
- `make smoke` → unchanged governing signature:
  - `calibration_ok=false`;
  - `curve decision engine: full_nested_pass_p`;
  - null family power `0.033333`;
  - θ=0.9 family power `0.933333`;
  - MDE80 `0.9`.

## 2.3 Regression flip against the reviewed Round-8 commit

The Round-9 repair tests were executed against the prior reviewed commit `56c972d`. Result: **21 failed, 2 passed**. The two passes are the intended legitimate behavior fixtures; the claimed repair assertions fail on the old object. This supports that the new tests are not merely vacuous additions.

# 3. What Round 9 genuinely closes

The following repairs survived direct execution rather than only source inspection:

| Round-8 area | Round-9 direct disposition |
|---|---|
| SPROLL HTTP 500 | raises |
| SPROLL empty first page | raises |
| SPROLL later page with a normal `<a href=...>` but zero parsed rows | raises |
| SPROLL `max_pages` exhaustion | raises |
| The supplied legitimate anchor-free terminal fixture | works |
| WB constant declared-total mismatch fixture | raises |
| Empty/partial docty JSON | rejected |
| IMF-specific rate/tokens enter generated IMF cells | passes |
| Changing IMF rate can change full `{P1,P2}` curve output | passes |
| Default IMF inputs reproduce legacy draws | passes |
| Missing requested template year | raises |
| Low versus huge accepted critical values alter actual curve decisions | passes |
| Interior event-study gap | merges forward; no empty bin or near-zero-width interval |
| All-zero requested coefficient | raises |
| Rank-deficient design | raises |
| Standardization simultaneous failures | both zero-cell and support failure reported |
| Standardization universal diagnostic keys | present in exercised infeasible paths |
| Git-status execution failure | aborts |
| `--freeze-fields` with `--allow-dirty` | aborts |
| Null listed mandatory freeze field | aborts |
| Current package ruling hashes, environment hash, calibration hash, and bundle hash | all verify |

C15's bin construction/estimability core and C16's diagnostic/failure-list core are therefore real repairs. The rejection is not based on denying those gains.

# 4. Blocking finding 1 — C13 acquisition and docty binding remain fail-open

## 4.1 WB “verbatim transport bytes” claim is false

The acquisition hook receives `resp.text`, not `resp.content` (`src/s01_fetch_metadata.py:32-35`). The WB frame then writes that decoded string with `Path.write_text` and hashes `raw.encode()` (`src/s09b_wb_p0_frame.py:219-235`). That is decoded/re-encoded text, not the original transport body.

**Direct counterexample:** a valid JSON response transported as UTF-16 produced:

```text
transport bytes: 318
archived bytes:  158
transport SHA-256: 5d118c7d17f572103487fda3b7b841f8421163bded39487c053fd0d54dfcf043
archive SHA-256:   a30468c368fb48a5f9de8ddaaba0e15b40435516678a926a59c676b1371888ea
byte-identical: false
```

The logged hash matched the rewritten archive, not the server bytes. This directly contradicts C13(b)'s “VERBATIM transport body” and “raw server bytes” language.

The package's regression assertion does not test this property. `tests/test_wb_frame.py:123-128` compares `read_text()` with a fake response's `.text`; it never supplies transport bytes whose encoding/serialization differs from that string.

## 4.2 WB can fail before preserving the raw response

`fetch_stratum_year` calls `resp.json()` before invoking `page_hook` (`src/s01_fetch_metadata.py:32-35`). A malformed JSON/error body therefore raises before any raw artifact is written.

**Direct counterexample:** a response body `<html>gateway error</html>` with `.json()` raising `ValueError` left:

```text
raw_files = []
request_log lines = 1   # header only
```

A failed live page is exactly the evidence that must be preserved for a fail-closed acquisition audit. The current order loses it.

## 4.3 WB declared-total drift and schema-less payloads can silently succeed

The code resets `total` from each page rather than freezing the first declared total (`src/s01_fetch_metadata.py:36-49`).

**Direct counterexample:** page 1 declared `total=3` and returned one record; page 2 declared `total=1` and returned no records. The function returned the one record without raising. The later reduced total erased the original completeness obligation.

A response `{}` is also accepted as a complete zero-record stratum because absent `total` defaults to zero and absent documents yields an empty batch. Thus a schema-shifted/probe-less API response can become a silent success.

Required behavior is to validate the response schema, freeze the initial declared total, require subsequent totals to agree, and compare the final unique record count against that invariant.

## 4.4 Raw-page immutability is still absent

WB raw paths are fixed as `{genre}_{year}_os{offset}.json` and are written without an existence guard (`src/s09b_wb_p0_frame.py:225-228`). The CSV log appends, but the raw object is overwritten.

**Direct counterexample:** two runs with different transport bodies produced one raw file whose SHA changed after the second run, while the log retained two data rows pointing to that same filename.

IMF has the same basic issue: `sproll_page_%04d.html` is written with `write_text`, and its request log is opened with mode `w` (`src/s09a_imf_articleiv_frame.py:188-202`). A rerun truncates prior evidence.

Round 8 expressly required immutable run-scoped artifacts. This remains open.

## 4.5 The IMF terminal criterion can still be mimicked by error markup

The only positive/negative distinction for a later zero-row HTTP-200 page is the literal substring `"<a "` (`src/s09a_imf_articleiv_frame.py:210-222`). Any anchor-free maintenance/access-denied page is therefore a legal terminal page. An interstitial using `<a>` without attributes also bypasses the detector.

**Direct counterexamples:** after one valid listing page, each of these was accepted as normal completion and returned the partial first-page frame:

```html
<div>maintenance outage</div>
<html><h1>Access denied</h1></html>
<html><a>Continue</a></html>
```

The named `<a href=...>` regression passes, but the prior closure requirement was stronger: the terminal condition must be a positive pagination/schema condition that cannot be mimicked by generic error HTML. Anchor absence is not such a condition.

## 4.6 `probe_sha256` is format-checked, not bound

`apply_docty_verification` verifies that `probe_sha256` is 64 lowercase hex characters (`src/s09b_wb_p0_frame.py:254-278`). It receives no probe-artifact path and never recomputes a hash.

A docty file containing `probe_sha256 = "00...00"` with otherwise valid fields is accepted and can alter runtime labels. Therefore the field does not “bind the archived s00 probe artifact,” as C13(d) states; it is an unverified assertion.

## C13 disposition

**FAIL.** The basic named fixtures improved, but byte-verbatim preservation, preserve-before-parse, immutable attempts, stable completeness, positive terminal validation, and real probe-artifact binding remain unsatisfied.

# 5. Blocking finding 2 — C14 calibration is not the family decision calibration it claims to be

## 5.1 The curve now consumes IMF inputs, and critical values now govern

Two important repairs are confirmed:

- `simulate_joint` now uses `tokens_imf` and `rate_imf` when generating IMF counts.
- The actual curve uses `crit_abs_z` and `crit_abs_z_half`; low versus enormous critical values produced different family-power output.

Those were real Round-8 defects and are closed.

## 5.2 `{P1,P2}` calibration still ignores P2

In calibrate/smoke mode the code calls:

```python
cal, _ = simulate_joint(...)
```

and computes both `zs` and nested `ps` from `cal` only (`src/mde_sim.py:211-240`). P2's statistic, P2's shorter year span, and the joint Holm-family decision are absent from the calibration.

**Direct counterexample:** holding every other input and seed fixed, changing the P2 template from `10^5` to `10^8` tokens/year and the P2 rate from `10^-6` to `10^-2` produced **byte-identical calibration JSON**.

Yet that record can authorize a two-panel Wald/Holm shortcut in curve mode. The authorization is therefore not calibrated to the family decision it governs.

## 5.3 The calibration artifact is materially unbound

The packaged artifact contains only:

```text
crit_abs_z, crit_abs_z_half, boot_size_at_null,
wald_boot_concordance, calibration_ok, ncal, B, sigma_delta
```

It does **not** bind:

- family (`p0` versus `p1p2`);
- exact years or P2 subset;
- IMF/P1/P2/P0 template hashes;
- base rates;
- α;
- ρ;
- companion effect rule;
- seed/offset registry;
- reviewed Git commit;
- code or requirements identity.

The curve loader checks only whether `calibration_ok` is truthy and then reads critical values. The same invented “accepted” JSON is therefore reusable under incompatible families, years, templates, rates, correlation, or code.

This is the input-binding defect explicitly identified in Round 8; it remains open.

## 5.4 The supplied calibration is not the frozen production calibration

The frozen preregistration specifies `ncal=200` and inner `B=9,999`. The shipped artifact records:

```text
ncal = 200
B = 999
calibration_ok = false
```

Because `calibration_ok=false`, the current smoke correctly uses the nested path. But this JSON cannot serve as evidence that the prespecified production calibration was executed. It is a lower-B failed-calibration record, not the frozen calibration run.

It should be described as a hash-bound failed pilot calibration unless regenerated with the frozen constants and complete input binding.

## 5.5 Missing-half fallback is functionally correct but reported falsely

When an otherwise accepted calibration lacks `crit_abs_z_half`, the code sets `use_wald=False` and uses nested PASS-P. However `decision` is computed and printed before that fallback and never updated (`src/mde_sim.py:257-287`). The final MDE line also uses the stale value (`src/mde_sim.py:327-329`).

Observed output:

```text
[mde] curve decision engine: wald_shortcut
[mde] calibration lacks crit_abs_z_half — Wald shortcut REFUSED ... using nested pass_p
...
[mde] family MDE80 = nan (engine=wald_shortcut, ...)
```

The numerical route is fail-closed; the machine/user-facing governance record is not. The preregistration expressly requires the program to print which engine actually ran.

## 5.6 Exact year/template contract remains incomplete

`--years` accepts only a contiguous `start-end` range, and P2 can only drop a leading segment through `--p2-start-year` (`src/mde_sim.py:145-202`). It still cannot represent an arbitrary gap-containing frozen common-year sequence.

`load_template` checks only that every requested year appears. It does not reject duplicate years, extra years, noninteger years, nonfinite values, or nonpositive token/doc exposures. Fresh probes showed extra-year and nonpositive templates were accepted at load time.

This is weaker than the exact gap-permitting, fail-closed template contract required in the Round-8 ruling.

## C14 disposition

**FAIL.** IMF input flow and critical-value governance are repaired, but family-level calibration, input binding, frozen production constants, exact-year representation, and truthful engine reporting are not.

# 6. Blocking finding 3 — C15 core estimability passes, but failed inference is still labeled “ok”

The prescribed interior-gap construction now works:

- `[1994..2025] − {2002,2003,2004}` produces no empty bin;
- the empty calendar bin is merged forward into `[2002,2007]`;
- the reference bin is `[2011,2013]`;
- every nonreference percentile interval has positive width;
- direct all-zero and rank-deficient requested designs raise.

However, `event_study` always returns `{"status": "ok", ...}` regardless of the governing PASS-E result (`src/s13_validation_battery.py:289-307`).

**Direct counterexample:** forcing the PASS-E interval engine to produce no valid intervals yielded:

```text
status = ok
governing_ci = failed
B_valid_ci = 0
```

Round 8 required the wrapper to propagate the governing failed state rather than hard-code `ok`. A consumer can otherwise treat a failed inferential display as a successful event study.

## C15 disposition

**PARTIAL / FAIL AS A FREEZE CONDITION.** The gap and design-identification defects are closed; top-level failure propagation is not.

# 7. C16 standardization diagnostics — PASS

The masking construction now returns:

```text
feasible = false
reason = zero_coverage_post_cell
failures = [zero_coverage_post_cell, post_token_support_below_0.80]
```

It also includes the full diagnostic set: `post_token_support`, `excluded_token_shares`, `dropped_cells`, `min_post_coverage`, `ess`, `pi_groups`, and `failures`. The explicit WB-2025 zero-retained-π cell is reported rather than masked.

## C16 disposition

**PASS.** No new counterexample was found in the reviewed return paths.

# 8. Blocking finding 4 — C17/C18 freeze and evidence governance remain insufficiently fail-closed

## 8.1 Calibration “sanity check” is only a three-key existence check

`stage_calibration` requires only `crit_abs_z`, `boot_size_at_null`, and `calibration_ok` (`tools/build_audit_package.py:124-139`). It does not require `crit_abs_z_half`, validate types, require finite/positive critical values, constrain size to `[0,1]`, require a Boolean, or validate/bind the production inputs.

**Direct counterexamples accepted and staged:**

```json
{"crit_abs_z":"not-a-number", "boot_size_at_null":-7,
 "calibration_ok":"truthy-string"}
```

and an allegedly accepted Holm-family calibration with no `crit_abs_z_half`.

Therefore C17(e)'s “sanity-checked” accepted calibration requirement is not implemented fail-closed.

## 8.2 Environment validation proves declared direct-version consistency, not execution provenance

`validate_and_stage_env` checks `python_version` and the direct `requirements.txt` package map (`tools/build_audit_package.py:87-121`). A record containing only:

```json
{"python_version":"3.11.9", "packages":{"numpy":"1.26.4"}}
```

was accepted in a matching one-pin fixture. Implementation, executable, platform, capture time, commands, exit statuses, and log bindings are not required.

For the current package, the supplied record is richer and its direct pins match. The mechanism nevertheless does not establish that the test/self-test logs were generated in the recorded session.

## 8.3 Ruling-chain completeness is not enforced

`enforce_freeze_completeness` checks only that `rulings` is nonempty (`tools/build_audit_package.py:151-163`). A map containing one arbitrary key, `{"only_one":"x"}`, was accepted.

The **current package** does carry r2/r3/r4/r7/r8 and their hashes all verify, so its inventory passes. The freeze builder does not implement C19's rule that absence of an available required ruling blocks the freeze.

## 8.4 Git bundle is optional even for a final freeze

`--git-bundle` is optional, and `git_bundle_sha256` is not among the mandatory freeze fields. The present package includes a valid bundle, but the builder can produce a purported final freeze with a Git commit assertion that is not independently retrievable from the package.

This leaves the future freeze mechanism fail-open relative to the prior requirement for a verifiable commit/archive relation.

## 8.5 Freeze-record v3 omits a freeze-field placeholder

C18 says the record carries one placeholder per freeze field. `freeze_fields_r9.json` contains `built_utc`; `docs/STAGE_A_FREEZE_RECORD_v3.md` has no `built_utc` placeholder.

The composite Stage-A object definition itself is correct. The claimed one-to-one placeholder completeness is not.

## C17/C18/C19 disposition

- **C17: FAIL.** Current hashes are valid, but calibration validation and complete execution provenance are not fail-closed.
- **C18: PARTIAL.** Object definition is correct; placeholder completeness is false because `built_utc` is omitted.
- **C19: PASS FOR THIS PACKAGE'S INVENTORY; FAIL AS A BUILDER GUARANTEE.** The current r2/r3/r4/r7/r8 chain verifies, but the packager accepts any nonempty map.

# 9. Amendment disposition

| Amendment | Ruling | Basis |
|---|---|---|
| C10 | **REMAINS ACCEPTED** | Not reopened; declared unchanged. |
| C13 | **FAIL** | WB not transport-byte verbatim; preserve-before-parse absent; total drift/schema-less success; overwrite; weak IMF terminal rule; docty hash not recomputed. |
| C14 | **FAIL** | P2 absent from calibration; artifact unbound and `B=999`; stale engine reporting; no exact gap-year interface; template validation incomplete. |
| C15 | **PARTIAL / FAIL FOR FREEZE** | Gap merge and estimability guards pass; failed PASS-E is still top-level `status="ok"`. |
| C16 | **PASS** | Universal diagnostics and simultaneous failure reporting reproduced. |
| C17 | **FAIL** | Calibration/environment evidence validators are too weak; final-freeze bundle/ruling guarantees incomplete. |
| C18 | **PARTIAL** | Stage-A object definition correct; `built_utc` placeholder missing. |
| C19 | **PASS CURRENT INVENTORY / MECHANISM INCOMPLETE** | r2/r3/r4/r7/r8 present and verified; builder enforces only nonempty rulings. |

# 10. Ranked required changes

## 1. Make acquisition evidence genuinely byte-verbatim, preserve-first, complete, and immutable

1. Pass `response.content` to the archive hook; write with `write_bytes`; hash exactly those bytes.
2. Archive and log the response **before** JSON/HTML parsing, including failed/malformed pages.
3. Record status, content type, URL, exact parameters, relevant headers, byte count, and transport-byte SHA-256.
4. Freeze the first valid WB declared total; require every later page to agree; validate required payload schema; deduplicate/validate record IDs; final unique count must equal the frozen total.
5. Replace “absence of literal `<a `” with a positive IMF terminal/pagination invariant that generic error HTML cannot satisfy.
6. Use run-ID/write-once directories and exclusive file creation. A retry or rerun must never overwrite an earlier raw page or truncate its log.
7. Supply the s00 probe artifact to docty verification and recompute its SHA-256; reject a mismatch.
8. Add regression tests for alternative encodings, malformed JSON preservation, declared-total drift, `{}` payload, `<a>` without attributes, maintenance/access-denied HTML, repeated-run overwrite, and fake probe hashes.

## 2. Calibrate and bind the exact MDE family decision

1. In `{P1,P2}` calibration, generate and evaluate **both** panels and the actual Holm/family rejection rule under their exact year subsets and templates.
2. Bind in the calibration JSON: schema version, family, exact year vectors, template hashes, base rates, α, ρ, σ rule/value, companion rule, ncal, B, reps, seed/offset registry, Git commit, code hash, and environment/requirements identity.
3. At curve load, recompute the current input fingerprint and reject any mismatch.
4. Run the frozen production calibration with `ncal=200`, inner `B=9,999`, and the frozen seed. If it fails acceptance, bind that failed result and always use nested PASS-P.
5. Recompute `decision` after any fallback and print/write the engine that actually ran.
6. Accept exact explicit year vectors for every active panel, including interior gaps; reject duplicate/extra/invalid years and nonfinite/nonpositive exposures.
7. Replace source-string/local-reimplementation tests with end-to-end CLI metamorphic tests for all panels, rates, critical values, fallback states, and calibration-input mismatch.

## 3. Propagate inferential failure states

`event_study` must return a failed top-level status whenever the governing PASS-E result fails or produces no valid governing interval. Add tests for NB2/jackknife failure, zero valid bootstrap intervals, and wrapper-level status propagation.

## 4. Make freeze-evidence validation schema-complete and mandatory

1. Define and validate strict JSON Schemas for environment and calibration records, including types, ranges, required fields, and input fingerprints.
2. Use one harness to capture environment plus commands, exact interpreter build, start/end UTC, exit codes, and stdout/stderr hashes for tests, self-test, smoke, and production calibration.
3. Require the Git bundle and `git_bundle_sha256` in any `--freeze-fields` run.
4. Require the exact ruling-name set appropriate to the round and an approving ruling before finalization; do not accept merely nonempty maps.
5. Add `built_utc` to `STAGE_A_FREEZE_RECORD_v3.md` and mechanically verify one placeholder per freeze-field path.

## 5. Regenerate and resubmit one new immutable package

Rebuild from a clean commit, run the exact Python 3.11.9 locked environment, execute the full suite, self-test, smoke, production calibration, and the adversarial probes above, then generate a new ZIP/freeze JSON/ruling chain. Do not patch the current ZIP after this rejection.

# 11. Permitted-changes boundary

Because this ruling is a rejection, the current package must not be registered or timestamped as the approved Stage-A object.

A later approving round may permit only:

1. corrections expressly reviewed and enumerated in that approving ruling;
2. insertion of immutable hashes, build/registration metadata, and the approving ruling identity;
3. typography/formatting without semantic effect.

No unreviewed change may alter acquisition requests, labels, frame rules, common-year sequences, branch states, support/ESS results, MDE/calibration inputs or outputs, active families, thresholds, estimators, or code behavior. Stage-B values remain confined to the separately timestamped SAP addendum.

# Final ruling

## **REJECT WITH REQUIRED CHANGES**

The Round-9 archive is internally authentic and demonstrates meaningful repairs, but the remaining deterministic counterexamples prevent a defensible Stage-A freeze. The next round should be narrow: byte-verbatim immutable acquisition, real docty probe binding, exact family-level calibration/input binding, truthful event-study failure status, and schema-complete freeze evidence.
