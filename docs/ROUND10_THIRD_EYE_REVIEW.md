# Round-10 Third-Eye Review

**Project:** *Bankspeak, Continued*  
**Package:** `round10_package_20260812.zip`  
**Freeze fields:** `freeze_fields_r10.json`  
**Review prompt:** `THIRD_EYE_REVIEW_PROMPT_v10.md`  
**Reviewed commit:** `f24e0efbf9a5eee605f378308a3a083fbe1548ac`  
**Review date:** 2026-08-12  
**Mandate:** fresh adversarial recomputation and a binary Stage-A ruling.

# Binary ruling

## **REJECT WITH REQUIRED CHANGES**

Round 10 is substantially stronger than Round 9. The submitted ZIP is internally coherent and independently retrievable; its complete checksum inventories verify; the Git bundle is valid and resolves the declared commit; the Python 3.11.9 environment record matches all direct dependency pins; all **141** tests pass; the five-line self-test is byte-identical to the packaged log; the declared C25 smoke signature reproduces; and the production-shaped `ncal=200, B=9999` calibration independently recomputes to the supplied values within negligible cross-platform floating-point differences.

Those successes are genuine. They do **not** establish that the frozen Stage-B machinery is fail-closed. Fresh counterexamples expose remaining defects in three binding amendments:

1. **C20 acquisition is not write-once or structurally terminal on the IMF path.** A second SPROLL run overwrites raw pages and truncates its request log; `<a>No results found</a>` is accepted as an anchor-free terminal page because the implementation checks only the literal substring `"<a "`. Additional probes show row-count completeness can be satisfied by duplicate WB document IDs and retryable WB error bodies never reach the archive hook.
2. **C21 cannot execute or bind the frozen branch-specific inputs.** Any file-backed template reaches `NameError: Path is not defined`; the CLI cannot represent the preregistered common-year sequence when it contains calendar gaps; and `tokens_per_doc` changes the numerical exposure vector without changing the calibration binding.
3. **C21/C23 do not make the supplied failed production calibration authoritative.** A same-commit, edited pilot calibration with `ncal=1`, `B=19`, and `calibration_ok=true` is accepted by curve mode and reopens `wald_shortcut`. The claim that the supplied `calibration_ok=false` permanently forces full nested PASS-P is therefore false as an executable property.
4. **C23's “strict” calibration validator remains fail-open.** It accepts `NaN`, `Infinity`, a negative critical value, malformed nested binding types, and a binding that omits `p2_start_year`. The execution-provenance harness also captures only pytest and self-test, omitting the smoke and production-calibration runs required by the Round-9 ruling.

These are deterministic code-path failures, not documentation preferences. They affect immutable acquisition evidence, the exact inputs to the MDE decision, whether a disallowed Wald shortcut can be reopened, and whether malformed freeze evidence can pass the package gate. The present ZIP must not be timestamped as the approved Stage-A object.

---

# 1. Integrity gate — **PASS**

I recomputed the package identity and full internal inventories rather than trusting the external freeze JSON.

| Check | Independently recomputed result |
|---|---|
| ZIP SHA-256 | `0fe23f2988c0a286c352ffd6c097cc210d8700de137a8b963537c1f544f27e6b` — matches |
| ZIP bytes | `10,458,505` — matches |
| ZIP entries | `156` — matches |
| Duplicate entry names | none |
| Unsafe paths | none |
| Symlinks / special entries | none |
| ZIP CRC test | no bad member |
| `SHA256SUMS` | 155 entries; exact archive inventory excluding itself; every hash passes |
| `MANIFEST.tsv` | 154 rows; exact archive inventory excluding itself and `SHA256SUMS`; every byte count and hash passes |
| `SHA256SUMS` hash | `ada6b71b23b892ac92c5a0941add0d8830601feed380ab5fe25e4f7baffd9346` — matches |
| `MANIFEST.tsv` hash | `699f6e20ce2fd4739aa729271897f0c8edc08b3afec895384bfdfc0b40b61004` — matches |

## 1.1 Git evidence

`git bundle verify evidence/repo.bundle` reports:

```text
The bundle records a complete history.
refs/heads/main = f24e0efbf9a5eee605f378308a3a083fbe1548ac
HEAD            = f24e0efbf9a5eee605f378308a3a083fbe1548ac
```

The prior reviewed commit `7fb89a56f02a84d6b214ad8a991f96d76fbed0b9` is present in that history. Of the reviewed commit's 127 tracked files, 119 are intentionally included by the audit builder; all 119 packaged copies are byte-identical to the Git objects. The omitted tracked files are repository instructions/placeholders or non-package data stubs; no included tracked file differs from the recorded commit.

## 1.2 Environment, logs, calibration, and ruling chain

The following hashes independently match the freeze JSON:

| Artifact | SHA-256 |
|---|---|
| `.python-version` | `61141e9590171b900fdf709e7ea8f050d5c2a69198d4a4a1977d7c45186307e5` |
| `requirements.txt` | `770300e1fcfcc4ff39d491f23d4a50111eb6ce8dae44df89bd818f88640ed8c9` |
| `requirements-ppl.txt` | `01020da68a9be519ffba0acb4caf686cbb8081b6e8d2b5e2b92429b63368a04e` |
| `evidence/environment.json` | `ebfd1037c93b8c669de97f4a1560df668994655588f6c1202406b9e76046815d` |
| `evidence/calibration.json` | `1a2b81aabf11175065ccad310bc4954aa8ef4dffbbd48529714d5d3bfddff938` |
| `evidence/repo.bundle` | `eadee3845154b6b2cdaa95a86009900bff2bb6c85de67b441a8cb52c73c69ebb` |
| `evidence/tests.log` | `4e771f05378d4174a543f7548eb4fc32e751d416afc19cab6dcd48e9d1ba2ad4` |
| `evidence/selftest.log` | `8651f8f36048d0b3124911e932eaec96eb41053b0b380b6637c5130f66d3da40` |

The environment record says CPython 3.11.9 and exactly matches every direct version pin in `requirements.txt`. Its two staged run records have zero exit codes and hashes equal to the packaged pytest and self-test logs.

All supplied ruling hashes verify for rounds 2, 3, 4, 7, 8, and 9. Round 6 remains explicitly declared pending, rather than silently represented as present. The v3.1 freeze record contains the `built_utc` placeholder and the declared round-6 pending placeholder.

**Integrity disposition:** the submitted object is authentic, internally coherent, and linked to the declared commit. Rejection does not arise from a corrupt or substituted package.

---

# 2. Independent execution — **PASS, with one environment limitation stated**

The independent container provided Python 3.13.5 rather than an installable local Python 3.11.9 interpreter. I therefore performed two complementary checks:

1. validated the package's own Python 3.11.9 provenance, direct pins, zero-exit run records, and staged-log hashes; and
2. independently executed the code on the available clean Linux/Python stack.

## 2.1 Full suite

```text
141 passed, 1 warning in 17.40s
```

The warning is a `PerfectSeparationWarning` in an existing synthetic feasibility test and does not change the pass result.

## 2.2 Self-test

The independent output contains exactly five lines. Its SHA-256 is:

```text
8651f8f36048d0b3124911e932eaec96eb41053b0b380b6637c5130f66d3da40
```

It is byte-for-byte identical to `evidence/selftest.log`.

## 2.3 C25 smoke signature

The independently executed smoke run produced:

```text
crit_abs_z             = 5.820810382338811
crit_abs_z_half        = 5.820810382338811
boot_size_at_null      = 0.1
wald_boot_concordance  = 0.8
calibration_ok         = false
curve decision engine  = full_nested_pass_p
family MDE80           = 0.9
```

The critical value's relative difference from the declared container reference `5.8208103823388075` is approximately `6.1e-16`, well within the specified `1e-12` band. C25 passes.

## 2.4 Independent production-calibration recomputation

I independently reran all 200 family-null replicates with inner `B=9999`, including both P1 and P2 PASS-P streams and P2's `+150000+i` seed offset. The recomputation and packaged artifact agree as follows:

| Field | Packaged | Recomputed | Disposition |
|---|---:|---:|---|
| `crit_abs_z` | 4.770137256837956 | 4.770137256837804 | relative difference `3.18e-14` |
| `crit_abs_z_half` | 5.5836590117385345 | 5.58365901173862 | relative difference `1.53e-14` |
| `boot_size_at_null` | 0.05 | 0.05 | exact |
| `wald_boot_concordance` | 0.91 | 0.91 | exact |
| `calibration_ok` | false | false | exact |
| `ncal` | 200 | 200 | exact |
| `B` | 9999 | 9999 | exact |
| `sigma_delta` | 0.1 | 0.1 | exact |

The supplied production calibration is therefore credible and correctly fails acceptance. The later rejection concerns the authority and validation of that artifact, not its numerical contents.

---

# 3. Round-9 named regression probes

## 3.1 Current commit

```text
pytest tests/test_round9_repairs.py -q
25 passed in 11.54s
```

The named repairs are not merely documentary: the current regression file is green.

## 3.2 Prior reviewed commit

The current test file was run against `7fb89a56...`. The old code kept `wald_holm2_decide` local to `main`, so I exposed the old function body at module scope solely to allow collection; no old runtime branch was changed. Result:

```text
22 failed, 3 passed
```

The three old-commit passes were:

- `test_declared_total_drift_raises`;
- `test_sproll_positive_terminal_ok`;
- `test_calibrated_holm_stepdown_semantics`.

This differs slightly from the prompt's anticipated behavior-preservation set: `test_event_study_healthy_still_ok` fails on the old commit because the new test also requires the newly added `failure_reasons` key, while the declared-total fixture already triggered an older generic final-count error. The exact Round-9 silent drift shape—first page total 3 with one row, later total 1 with zero rows—is nevertheless rejected by the current code. This mismatch is a test-specificity issue, not a basis for the present rejection.

## 3.3 Why 25 green tests are insufficient

The regression file tests the named Round-9 fixtures. It does not exercise all logically equivalent inputs or all Stage-B branches. The following direct probes stay within the same frozen contracts and expose paths that remain open.

---

# 4. Blocking finding A — C20 acquisition remains fail-open

## 4.1 IMF raw capture is not write-once and the request log is not append-only

C20 requires an existing per-page file or non-empty raw directory to abort, a fresh directory for a rerun, and an append-only request log. The current IMF implementation instead:

- creates/reuses `out_raw` without checking whether it is non-empty;
- writes each page with `Path.write_text`, which overwrites an existing file; and
- opens the request log with mode `"w"`, truncating prior history.

**Direct probe:** run two valid two-page captures into the same directory, with different first-page bodies.

```text
page1_hash_before = b6ff566e6ecde0a32fece331fd0f44755dc5cd4058df2bbf1bd32c31e9155c15
page1_hash_after  = c89f13459c5d01e3bbc8be44613bbd31f1d364281f0f2945ccf355274312bc29
log_lines_before  = 3
log_lines_after   = 3
```

The first raw page was replaced, and the second run replaced rather than appended the log. This is a direct violation of C20's immutable-evidence rule.

## 4.2 The “contains no anchors” condition is implemented as a bypassable substring test

The zero-row terminal branch checks:

```python
if "<a " in low:
    raise ...
```

That detects `<a href=...>` but not a valid anchor tag with no attributes. After one normal page, this page:

```html
<a>No results found</a>
```

was accepted as a legitimate terminal page and the partial one-row frame was returned:

```text
partial_frame_returned_rows=1
RESULT: FAIL-OPEN
```

C20 says the terminal page may contain **no anchors**, not merely no literal `"<a "` substring. The implementation must inspect HTML structure or, at minimum, recognize all syntactically valid `<a...>` openings.

## 4.3 WB completeness is based on row count rather than unique logical records

Two pages each returned a record with logical `id="1"`, while both declared `total=2`. Current code accepted:

```text
accepted_rows=2
unique_ids=1
ids=['1', '1']
```

The final `len(records) == declared_total` check can therefore certify a frame with only one unique document. A stable logical-ID uniqueness check is required before completeness can be claimed.

## 4.4 Retryable WB error bodies are not archived

The page hook is invoked only after `get_with_retry` returns a successful response. A final HTTP 500 response is consumed by the retry layer and then discarded:

```text
raised=RuntimeError: GET failed after 1 attempts ...
archived_attempt_bodies=0
```

This leaves no immutable server body for an acquisition failure. The raw-attempt archive must sit at or below the retry layer so every received response—status, headers, URL/params, and bytes—is preserved before retry or abort.

## 4.5 IMF still archives decoded/re-encoded text

The IMF path reads `response.text`, writes with `write_text`, and hashes `raw.encode()`. A UTF-16 transport body produced:

```text
transport_bytes = 228
archived_bytes  = 113
byte_identical  = false
```

C20's byte-verbatim clause is written specifically around the s01/WB hook, so this is an additional provenance defect rather than the sole basis for C20 failure. Given that the IMF files are also described as raw HTML evidence, the safer implementation is to archive `response.content` with `write_bytes` and parse a decoded copy separately.

## C20 disposition

**FAIL.** The named WB malformed-body/schema/total-drift/write-once tests and the documented IMF marker tests pass, but the IMF implementation directly violates the frozen write-once and no-anchor rules. The duplicate-ID and failed-attempt probes expose further completeness/provenance gaps.

---

# 5. Blocking finding B — C21 cannot execute or bind the exact frozen inputs

## 5.1 File-backed templates crash in binding construction

`_sha_file` calls `Path(path)`, but `Path` is not imported at module scope. It is imported only inside the `--out` branch after binding construction. A direct `build_binding` call with a valid `year,tokens` template raises:

```text
NameError: name 'Path' is not defined
```

The smoke run does not reveal this because it uses flat tokens. Stage-B's branch-specific `--cells-template` / `--template-{imf,p1,p2,p0}` path is therefore not executable as frozen.

## 5.2 Calendar-gap common-year sequences cannot be represented

The preregistration defines the frozen common-year sequence as an explicit ordered sequence and permits calendar gaps. The CLI accepts only one string parsed as:

```python
y0, y1 = (int(v) for v in a.years.split("-"))
years = np.arange(y0, y1 + 1)
```

A simple gap sequence such as `2018, 2020` is not representable:

```text
--years 2018,2020
ValueError: invalid literal for int() with base 10: '2018,2020'
```

Moreover, the binding stores only an endpoint string such as `"1994-2025"`, not the exact year vector. Even if a gap vector were injected internally, distinct interior sequences with the same endpoints would share a binding identity.

This remains open from the Round-9 requirement to accept and bind exact explicit year vectors for every active panel, including interior gaps.

## 5.3 `tokens_per_doc` changes the simulation but not its binding

For a `year,docs` template:

```text
--tokens-per-doc 1000 -> exposures [100000.0, 100000.0]
--tokens-per-doc 2000 -> exposures [200000.0, 200000.0]
```

After temporarily supplying the missing `Path` symbol solely to expose the next defect, the two `build_binding` outputs were identical. The template identity records only the CSV hash; it omits the multiplier that turns document counts into token exposures.

A calibration can therefore be reused after doubling the numerical exposure vector while passing binding equality. The robust solution is to bind both the raw inputs and a hash of each final, ordered numerical exposure vector.

## C21 input-contract disposition

**FAIL.** P1/P2 pooling, P2's seed offset, critical-value governance, cross-family refusal, and banner truth are real repairs. The actual Stage-B template path, exact gap-containing year vectors, and one material exposure parameter remain either unusable or unbound.

---

# 6. Blocking finding C — the failed production calibration does not permanently refuse Wald

The supplied production artifact is numerically sound and has `calibration_ok=false`. Under the intended package, smoke and ordinary curve execution use `full_nested_pass_p`.

However, curve mode does not require the packaged calibration's hash, production sizes, or provenance. It checks only:

- `calibration_ok is True`;
- numeric critical values; and
- equality of the current binding to the JSON's binding.

A same-commit JSON was constructed with:

```text
ncal = 1
B = 19
calibration_ok = true
crit_abs_z = 0
crit_abs_z_half = 0
binding = current same-commit binding
```

Curve mode accepted it:

```text
[mde] curve decision engine: wald_shortcut
[mde] family MDE80 = 0.0 (engine=wald_shortcut, ...)
```

Thus the package's failed production result does **not** “permanently refuse” the Wald shortcut. A pilot or manually edited artifact can reopen the shortcut without a new commit or amendment.

This is not solved merely by making the packager reject pilot evidence, because Stage-B curve mode accepts an arbitrary path supplied through `--calib-json`. The runtime must enforce the authoritative frozen calibration identity and schema.

## Required authority rule

At least one of the following equivalent fail-closed designs is needed:

1. freeze an expected calibration SHA-256 in the SAP/config and require curve mode to match it; or
2. emit a signed/hashed calibration identifier into the freeze record and require that exact artifact; or
3. hard-code the accepted Stage-A result for this frozen commit—here, `calibration_ok=false`—so no alternate JSON can authorize Wald without a new timestamped amendment.

In all cases, runtime validation must require `ncal=200`, `B=9999`, exact family/input fingerprints, finite positive critical values, and the complete binding schema.

## C21/C23 authority disposition

**FAIL.** The actual production evidence is good; its authority over later execution is not enforced.

---

# 7. Blocking finding D — C23 freeze validation and provenance remain incomplete

## 7.1 “Strict” calibration validation accepts invalid numerical values

The packager's `_num` check accepts any Python `int` or `float` except booleans. It does not require finiteness or valid ranges for critical values and sigma. A production-sized JSON containing:

```text
crit_abs_z       = NaN
crit_abs_z_half  = -1.0
sigma_delta      = Infinity
ncal             = 200
B                = 9999
calibration_ok   = false
```

was accepted and staged as `evidence/calibration.json`.

The validator should reject non-standard JSON constants at parse time, then require `math.isfinite` and semantic ranges (`crit_abs_z > 0`, `crit_abs_z_half > 0`, `sigma_delta >= 0`, probabilities in `[0,1]`).

## 7.2 The complete binding schema is not required

C21 explicitly includes `p2_start_year` in the binding. `CAL_BINDING_KEYS` omits it. The same invalid probe omitted `p2_start_year` and was accepted.

The packager also validates only top-level key presence. It accepted:

- `years="not-a-vector"`;
- `alpha="wrong"`;
- `rho=null`;
- `companion=17`;
- `seed="wrong"`;
- `base_rates=[]`; and
- `templates="wrong"`.

A “complete binding” must be validated recursively for exact keys, types, ranges, and canonical year/exposure representations.

## 7.3 The single evidence harness omits two required runs

`tools/run_evidence.py` contains only:

```text
pytest.log
selftest.log
```

It does not execute or hash-bind:

- `make smoke`; or
- the production `ncal=200, B=9999` calibration.

The Round-9 required change called for one harness covering tests, self-test, smoke, and production calibration. The supplied environment record correspondingly has only two `runs[]` entries. The separate calibration JSON is internally valid and independently reproducible, but its command, start/end UTC, exit code, stdout/stderr log hash, and same-session interpreter are not in the provenance record.

## C23 disposition

**FAIL.** Required ruling names, bundle enforcement, commit equality, two staged-log cross-checks, and the actual package's production constants pass. Strict schema validation and complete execution provenance do not.

---

# 8. Amendments disposition

| Amendment | Disposition | Basis |
|---|---|---|
| **C10 — FSSA rule** | **PASS** | Co-titled Article IV/FSSA included with flag; standalone FSSA excluded; both direct tests pass. |
| **C13 → C20 — acquisition** | **FAIL** | IMF reruns overwrite/truncate; `<a>` anchor bypass accepted; additional unique-ID and failed-attempt gaps. |
| **C14 → C21 — calibration/input binding** | **FAIL** | File templates crash; gap vectors unsupported/unbound; `tokens_per_doc` omitted; alternate pilot can reopen Wald. |
| **C15 → C22 — event-study failure propagation** | **PASS** | Governing failure, zero-valid-CI, and healthy-path tests pass; top-level status propagation is repaired. |
| **C16 — universal diagnostics** | **PASS** | Every-return diagnostics and simultaneous-failure tests pass. |
| **C17 → C23 — freeze builder/provenance** | **FAIL** | NaN/negative/incomplete calibration accepted; smoke and production calibration absent from harness. |
| **C18 → C24 — freeze record v3.1** | **PASS** | Composite object definition and literal `built_utc`/other placeholders are present. |
| **C19 — ruling chain** | **PASS** | r2/r3/r4/r7/r8/r9 present and hash-valid; exact required-name enforcement exists; round 6 is explicitly pending. |
| **C25 — smoke change** | **PASS** | Declared calibrate block reproduced within tolerance; nested decision and MDE80 0.9 unchanged. |

---

# 9. Required changes before another binary review

## 9.1 Close C20 acquisition paths

1. **Make IMF archives run-immutable.** Abort if the raw target contains any page/log artifact; write page bytes with exclusive creation (`xb` or equivalent atomic create); make the request log append-only or, preferably, write a new run-scoped log and immutable run identifier.
2. **Parse anchors structurally.** Use an HTML parser to detect every anchor element. Do not rely on a literal substring. Keep the positive terminal marker and interstitial exclusions, but bind the accepted terminal structure to the Stage-B probe artifact.
3. **Archive IMF transport bytes.** Save `response.content` with `write_bytes`; parse a separately decoded representation; log content type/encoding and hash the saved bytes.
4. **Validate WB logical uniqueness.** Define the canonical record key, reject duplicates across pages, and compare the final **unique** count with the first declared total.
5. **Archive every WB response attempt.** Move the raw-response hook into the retry layer or return an attempt callback so 429/5xx bodies and metadata are preserved before retry/abort.

## 9.2 Make C21 inputs executable and collision-resistant

1. Import `Path` at module scope and add end-to-end CLI tests using every template option.
2. Accept exact ordered year vectors for P1, P2, P0, and IMF—through a canonical CSV/JSON file or a strict comma-list—and allow interior gaps. Reject duplicates, disorder, out-of-window years, and panel inconsistencies.
3. Bind the exact vectors rather than endpoint strings.
4. Include `tokens_per_doc`, all transformation rules, and hashes of the final ordered token vectors in the binding.
5. Add metamorphic tests showing that changing any year, template byte, multiplier, base rate, alpha, rho, sigma, companion rule, family, seed offset, commit, or final exposure vector changes/refuses the binding.

## 9.3 Make the failed production calibration authoritative

1. Freeze and enforce the exact calibration artifact SHA-256 at curve load.
2. Require production `ncal=200`, `B=9999`, complete schema/version, and the exact current input fingerprint before any shortcut can be considered.
3. Because the frozen artifact says `calibration_ok=false`, make Wald unreachable for this frozen object. Reopening it must require a new code/evidence object and a timestamped amendment.
4. Reject nonfinite or nonpositive critical values in both packager and runtime.

## 9.4 Finish C23 strict validation and provenance

1. Validate calibration and environment records with strict recursive schemas: exact required keys, no unknown decision fields, correct JSON types, finite values, valid ranges, canonical hash/commit formats, exact year vectors, and complete nested binding fields including `p2_start_year`.
2. Reject `NaN`, `Infinity`, and `-Infinity` during JSON parsing.
3. Extend `tools/run_evidence.py` to execute and hash-bind pytest, self-test, smoke, and the production calibration in one environment record, including exact commands, interpreter, exit codes, start/end UTC, and log hashes.
4. Add regression tests for every probe in the accompanying script/log, and run them against both the repaired and prior commits.

## 9.5 Rebuild immutably

Commit the repairs first, generate all evidence at that clean commit, build a new ZIP and freeze JSON, and submit the new immutable package. Do not patch the present ZIP after this ruling.

---

# 10. Final ruling

## **REJECT WITH REQUIRED CHANGES**

The package's integrity and much of its numerical evidence are excellent. C10, C15/C22, C16, C18/C24, C19, and C25 are ready. Stage-A approval is blocked by executable C20, C21, and C23 failures: mutable IMF evidence, a bypassable terminal rule, unusable/unbound exact MDE inputs, a non-authoritative failed calibration, and a calibration/provenance validator that still accepts malformed evidence.

**Do not timestamp or register `round10_package_20260812.zip` as the approved Stage-A object.**
