# Round-11 Third-Eye Review

**Project:** *Bankspeak, Continued*  
**Package:** `round11_package_20260813.zip`  
**Freeze fields:** `freeze_fields_r11.json`  
**Review prompt:** `THIRD_EYE_REVIEW_PROMPT_v11.md`  
**Reviewed commit:** `10266bad12500df683c7b7618ce4eae3cba61d16`  
**Review date:** 2026-08-13  
**Mandate:** adversarial recomputation and a binary Stage-A ruling.

# Binary ruling

## **REJECT WITH REQUIRED CHANGES**

Round 11 genuinely repairs every named Round-10 regression in the submitted test file. The package is internally coherent; the Git bundle is complete and resolves the declared commit; all 157 tests pass; the self-test is byte-identical; the C25/C27.4 smoke signature reproduces; and the production `ncal=200, B=9999` calibration independently recomputes to the packaged values within approximately `10^-14` relative floating-point differences.

Those successes are real. They are not sufficient for a Stage-A timestamp because fresh counterexamples expose four remaining fail-open paths:

1. **C28 does not make the packaged calibration the only executable authority.** The file-hash argument is optional. A forged, production-sized calibration with the same binding, positive critical values, and `calibration_ok=true` opens `wald_shortcut` whenever `--calib-expected-sha256` is omitted. Supplying the frozen hash correctly refuses it, but omission is silently permissive rather than fail-closed.
2. **C26 acquisition remains structurally bypassable.** `<a/>No results` is accepted as an anchor-free terminal page; a WB record with no logical `id` is counted as one unique identifier (`None`) and accepted against `total=1`. Two additional acquisition items required in Round 10 also remain open: retryable WB response bodies are discarded before the page hook, and SPROLL archives decoded/re-encoded text rather than transport bytes.
3. **C28's calibration packager is not a strict recursive schema.** It accepted a calibration with `ncal=200.0`, `B=9999.0`, `p2_start_year="not-an-int-or-null"`, duplicate years, and a nonnumeric nested base rate. The current packaged artifact itself is well formed; the claimed fail-closed validator is not.
4. **C24's freeze-record template was not advanced for Round 11.** `STAGE_A_FREEZE_RECORD_v3.1.md` still defines the frozen object only through `PREREG_v0.8_AMENDMENTS`, and has no literal rows for `logs.smoke` or `rulings.round10`. It therefore no longer carries one placeholder per current freeze-field key and does not explicitly make `PREREG_v0.9_AMENDMENTS` normative.

The first finding directly permits the decision engine to change from the packaged `full_nested_pass_p` outcome to `wald_shortcut`. The second can certify incomplete or structurally invalid acquisition evidence. The third and fourth break the claimed freeze-governance closure. The package must not be timestamped in its present form.

---

# 1. Integrity gate — **PASS**

| Check | Independently recomputed result |
|---|---|
| ZIP SHA-256 | `cf25644fe19959005ea104404ac7e5a8675094dae2a93b160c03590bc81eda66` — matches |
| ZIP bytes | `10,513,258` — matches |
| ZIP entries | `163` — matches |
| Duplicate entry names | none |
| Unsafe paths | none |
| Symlinks / special entries | none |
| ZIP CRC test | no bad member |
| `SHA256SUMS` | 162 unique entries; exact archive inventory excluding itself; every hash passes |
| `MANIFEST.tsv` | 161 unique rows; exact archive inventory excluding itself and `SHA256SUMS`; every byte count and hash passes |
| `SHA256SUMS` hash | `229bd67ba01d775b5fd978ea83ab746870ef94a7a2d0d8afe0157b1cc23ade29` — matches |
| `MANIFEST.tsv` hash | `750908df79de7482fc94a664a96c34cd14ca7d525fde6fad4f6c97aa8ec21536` — matches |

## 1.1 Git evidence

`git bundle verify evidence/repo.bundle` reports a complete history. Both `refs/heads/main` and `HEAD` resolve to:

```text
10266bad12500df683c7b7618ce4eae3cba61d16
```

The prior reviewed commit `f24e0ef` is present. Of the package manifest's 161 files, 124 are tracked at the reviewed commit and all 124 are byte-identical to their Git objects. The other 37 are generated analysis/evidence files. Eight tracked repository-only files are intentionally omitted from the package; no included tracked file differs from the declared commit.

## 1.2 Freeze hashes and ruling chain

The `.python-version`, both requirement files, environment record, calibration, bundle, three staged logs, and all seven ruling artifacts independently match the external freeze JSON. The ruling chain is exactly rounds 2, 3, 4, 7, 8, 9, and 10; round 6 remains explicitly declared pending in the textual freeze record.

**Integrity disposition:** authentic, coherent, and independently retrievable. Rejection does not arise from package substitution or corruption.

---

# 2. Independent execution — **PASS, with stated environment limitation**

The review container supplied Python 3.13.5. An attempted installation of exact CPython 3.11.9 failed because the isolated runtime could not resolve the download host. I therefore performed two complementary checks:

1. validated the package's CPython 3.11.9 provenance, exact direct dependency pins, four zero-exit run records, and staged-log/artifact hashes; and
2. independently executed the package on the available Linux/Python stack.

## 2.1 Full suite

```text
157 passed, 1 warning in 27.39s
```

The warning is the existing `PerfectSeparationWarning` in `test_std_high_support_feasible_and_reported`; it does not alter the pass result.

## 2.2 Self-test

The independent output has exactly five lines and SHA-256:

```text
8651f8f36048d0b3124911e932eaec96eb41053b0b380b6637c5130f66d3da40
```

It is byte-for-byte identical to `evidence/selftest.log`.

## 2.3 Smoke signature and C27.4 shape note

Running from the reviewed Git checkout produced:

```text
crit_abs_z             = 5.820810382338811
crit_abs_z_half        = 5.820810382338811
boot_size_at_null      = 0.1
wald_boot_concordance  = 0.8
calibration_ok         = false
curve decision engine  = full_nested_pass_p
family MDE80           = 0.9
binding.git_commit     = 10266bad12500df683c7b7618ce4eae3cba61d16
binding.years          = full 32-integer vector, 1994..2025
```

The staged critical value is `5.820810382338911`; relative difference is approximately `1.71e-14`, well inside the required `1e-12` band. All other governing numbers and the decision path are exact. The full-vector `binding.years` output is the declared C27.4 shape change.

## 2.4 Independent production calibration

The full production command was independently rerun from the reviewed commit:

```text
python src/mde_sim.py --mode calibrate --sigma-delta 0.1 \
  --ncal 200 --B 9999 --out calibration_recomputed.json
```

| Field | Packaged | Recomputed | Disposition |
|---|---:|---:|---|
| `crit_abs_z` | 4.770137256837956 | 4.770137256837804 | relative difference `3.18e-14` |
| `crit_abs_z_half` | 5.5836590117385345 | 5.58365901173862 | relative difference `1.53e-14` |
| `boot_size_at_null` | 0.05 | 0.05 | exact |
| `wald_boot_concordance` | 0.91 | 0.91 | exact |
| `calibration_ok` | false | false | exact |
| `ncal` | 200 | 200 | exact |
| `B` | 9999 | 9999 | exact |
| `family` | `p1p2` | `p1p2` | exact |
| complete binding | packaged | recomputed | exact |

The production calibration is numerically credible and legitimately refuses Wald. The rejection concerns whether that artifact is uniquely authoritative and whether malformed alternatives are fail-closed.

---

# 3. Round-10 regression flips — **PASS for the named fixtures**

## 3.1 Current commit

```text
pytest tests/test_round10_repairs.py -q
16 passed in 11.04s
```

The full suite reports 157 passes, exactly `141 + 16`.

## 3.2 Prior reviewed commit

The current regression file was transplanted onto `f24e0ef`. Because that commit has no module-level `parse_years`, a compatibility shim reproducing its endpoint-only inline parser was added solely to permit test collection; no old behavior was repaired. Result:

```text
16 failed in 11.16s
```

The failures reproduce the old overwrite/truncation, bare/newline-anchor acceptance, duplicate-ID acceptance, `Path` crash, endpoint-only years, missing `tokens_per_doc` identity, forged-pilot Wald opening, absent hash pin, permissive packager, absent calibration-run cross-bind, and two-step-only provenance harness.

**Regression disposition:** the submitted repairs are genuine behavior changes, not vacuous tests.

---

# 4. Evidence provenance — **PASS for the submitted artifacts**

`evidence/environment.json` records exactly four sequential runs, all with exit code zero:

1. pytest;
2. self-test;
3. smoke;
4. production calibration.

Every staged log hash equals a zero-exit run's `log_sha256`. The staged calibration hash

```text
49e97790c83d4c2f4aa6045514e1348e946a054be880f967709dfa6d00714723
```

equals the calibrate run's `artifact_sha256`. The environment's ten direct package versions exactly match `requirements.txt`. The packaged calibration is production-sized, has a complete currently expected binding, and its `binding.git_commit` equals the packaged commit.

**Submitted-evidence disposition:** provenance is internally valid. The remaining C28 defect is enforcement/validator generality, not substitution of the actual submitted calibration.

---

# 5. Blocking finding A — C28 hash authority is optional, not fail-closed

`--calib-expected-sha256` defaults to `None`, and the file hash is checked only inside:

```python
if a.calib_expected_sha256:
    ... compare hash ...
```

A forged artifact was made from the independently recomputed binding, then changed only to:

```text
ncal = 200
B = 9999
calibration_ok = true
crit_abs_z = 1e-9
crit_abs_z_half = 1e-9
binding = exact current binding, including commit
```

### Probe without the expected hash

```text
[mde] curve decision engine: wald_shortcut
[mde] family MDE80 = 0.0 (engine=wald_shortcut, ...)
```

### Same file with the frozen packaged hash supplied

```text
[mde] Wald shortcut REFUSED (fail-closed): calibration file hash does not match --calib-expected-sha256 ...
[mde] curve decision engine: full_nested_pass_p
```

The hash mechanism works when invoked. The defect is that it is not required. A runbook sentence cannot make the package the **only executable authority** when omission silently licenses a same-binding alternative.

## Required repair

For any curve run that presents an external calibration and could otherwise authorize Wald:

- require a valid `--calib-expected-sha256` value; omission must refuse Wald;
- compare it with the file before accepting any decision fields;
- print/record the verified hash in the curve output/provenance; and
- add a regression asserting that a production-sized same-binding calibration cannot open Wald when the expected hash is absent.

Alternatively, place the frozen hash in an immutable Stage-B config read by the executable, but do not leave the authority check optional.

**C28 authority disposition: FAIL.**

---

# 6. Blocking finding B — C26 acquisition still has fail-open inputs

## 6.1 Self-closing anchor bypass

The terminal check is:

```python
re.search(r"<a[\s>]", low)
```

After one valid listing page, the zero-row page:

```html
<a/>No results
```

was accepted as a positive terminal page and returned the partial frame:

```text
RESULT=ACCEPTED rows=1
```

`<a/>` is still an anchor start/end token to an HTML parser. C20's governing condition is “contains no anchors,” not “contains no anchor whose next character is whitespace or `>`.”

## 6.2 Missing logical ID counts as unique completeness

A WB response with `total=1` and one document lacking `id` returned successfully:

```text
RESULT=ACCEPTED rows=1 id=None
```

The code inserts `None` into `seen_ids`; its cardinality is one, so `len(seen_ids) == first_total` passes. A missing/blank/noncanonical identifier must be a schema failure before uniqueness is evaluated.

## 6.3 Retryable WB bodies remain unarchived

A final HTTP 500 response raised after retry exhaustion, but the page hook received no body:

```text
archived_attempt_bodies=0
```

The hook is above `get_with_retry`, so only a returned HTTP-200 response reaches it. This was an explicit Round-10 required change: archive every received response attempt before retry or abort.

## 6.4 SPROLL raw evidence is still decoded/re-encoded text

A UTF-16 transport page produced:

```text
transport_bytes = 228
archived_bytes  = 113
byte_identical  = false
```

SPROLL uses `response.text`, `write_text`, `len(raw)`, and `sha256(raw.encode())`, rather than `response.content`, `write_bytes`, and a hash over saved transport bytes.

## Required repair

- Detect anchors structurally with an HTML parser, or at minimum cover slash syntax and add the direct `<a/>` regression.
- Require a non-empty canonical document ID for every WB record before deduplication.
- Move an attempt-archive callback into/below the retry layer so every 429/5xx/client-error response body and metadata survives.
- Archive SPROLL `response.content` with exclusive byte creation; parse a separately decoded copy; hash and count the saved bytes.

The first two findings alone defeat the stated C26 terminal/unique-ID contracts. The latter two remain unclosed items from the Round-10 required-change list.

**C20→C26 disposition: FAIL.**

---

# 7. Blocking finding C — C28 packager validation is not strict recursively

`stage_calibration` validates several top-level numbers and only the outer types of `years`, `base_rates`, and `templates`. It does not enforce integer JSON types for `ncal/B`, a type for `p2_start_year`, strictly increasing unique years, or finite/null nested rate values.

The following single calibration was accepted and staged:

```text
ncal = 200.0
B = 9999.0
binding.p2_start_year = "not-an-int-or-null"
binding.years = [1994, 1994]
binding.base_rates = {"shared": "not-a-number"}
```

Result:

```text
RESULT=ACCEPTED malformed-but-outer-typed calibration
```

This contradicts the stated “strictly typed” and fail-closed freeze-builder property. The current packaged calibration is valid; the builder is still capable of certifying malformed evidence.

## Required repair

Use one exact recursive schema shared by packager and runtime:

- `ncal` and `B`: JSON integers, not booleans/floats, with exact production values;
- `p2_start_year`: integer or null;
- `years`: integers, strictly increasing, unique, canonical, and consistent with `p2_start_year`;
- `family` and `companion`: allowed enums, not arbitrary strings;
- nested `base_rates`: exact keys, each finite positive number or null according to the frozen contract;
- nested `templates`: exact keys and exact source-identity object shapes;
- reject unknown decision-bearing keys and nonstandard JSON constants.

Add direct regressions for the accepted counterexample above.

**C23→C28 strict-validation disposition: FAIL.**

---

# 8. Blocking finding D — C24 freeze record is stale after C28

`docs/STAGE_A_FREEZE_RECORD_v3.1.md` still states:

```text
Frozen object = PREREG_DRAFT_v0.5 + v0.6 + v0.7 + v0.8 + approved ZIP
```

It does not name `PREREG_v0.9_AMENDMENTS (C26–C28)`. Its table has `logs.tests` and `logs.selftest`, but no `logs.smoke`; it has rulings through round 9, but no `rulings.round10`.

C24's governing property was one literal placeholder for every freeze-field key. C28 expanded the actual schema, so the old template no longer satisfies C24.

## Required repair

Create a new freeze-record version before rebuilding the package that:

- explicitly includes `PREREG_v0.9_AMENDMENTS.md` in the normative frozen object;
- adds literal rows for `logs.smoke` and `rulings.round10`;
- preserves the declared-pending round-6 row and the future approving-ruling/OSF fields; and
- is included in the rebuilt immutable ZIP before approval.

**C24 disposition: FAIL.**

---

# 9. Amendment disposition

| Amendment | Disposition | Basis |
|---|---|---|
| **C10 — FSSA rule** | **PASS** | Existing direct tests and prior closure remain green. |
| **C20 → C26 — acquisition symmetry** | **FAIL** | `<a/>` terminal bypass; missing IDs count as unique; retry bodies unarchived; SPROLL bytes re-encoded. |
| **C21 → C27 — template/year binding** | **PASS for the stated Round-11 closure** | File templates execute and bind their hash; calendar gaps parse; full year vector binds; `tokens_per_doc` changes identity. |
| **C22 — event-study failure propagation** | **PASS** | Governing failure paths and healthy path remain green in the 157-test suite. |
| **C16 — universal diagnostics** | **PASS** | Existing simultaneous-failure and every-return diagnostics remain green. |
| **C23 → C28 — calibration authority/provenance** | **FAIL** | Submitted four-run provenance passes, but hash authority is optional and recursive strict validation remains fail-open. |
| **C24 — freeze record** | **FAIL** | Template omits v0.9, `logs.smoke`, and `rulings.round10`. |
| **C19 — ruling chain** | **PASS** | Seven supplied rulings are present and hash-valid; round 6 remains explicitly pending. |
| **C25 — smoke numbers** | **PASS** | Critical values within `1e-12`; boot/concordance/ok, nested engine, and MDE80 unchanged. |
| **C27.4 — declared shape note** | **PASS** | `binding.years` is the full 32-integer vector; governing smoke numbers are unchanged. |

---

# 10. Required changes before another binary review

1. **Make the calibration hash mandatory for Wald licensing.** Omission must refuse; add the production-sized forged-artifact/no-hash regression.
2. **Close C26 structurally.** Parse all anchors, reject missing IDs, archive every WB attempt, and store SPROLL transport bytes.
3. **Replace outer-type checks with one recursive calibration schema.** Add regressions for float production counts, malformed `p2_start_year`, duplicate years, and malformed nested rates/templates.
4. **Advance the freeze-record template.** Explicitly bind v0.9, `logs.smoke`, and `rulings.round10` before package construction.
5. Commit first, regenerate the four-run evidence at the clean final commit, rebuild the ZIP/freeze JSON, and rerun the old-commit flip check plus the new counterexamples.

These repairs add no data source, analysis branch, or scientific scope. They only make the already declared Stage-A rules executable and recordable.

---

# Final ruling

## **REJECT WITH REQUIRED CHANGES**

Round 11 is numerically reproducible and closes the named Round-10 fixtures, but it is not yet safe to timestamp. The packaged failed calibration is not the only executable authority unless an optional argument is remembered; acquisition still accepts structurally invalid terminal/ID cases; the packager can stage malformed calibration bindings; and the freeze-record template does not represent the Round-11 schema.

**Do not timestamp or register `round11_package_20260813.zip` as the approved Stage-A object.**
