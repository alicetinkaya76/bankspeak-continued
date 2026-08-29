# Round-12 Third-Eye Review

**Project:** *Bankspeak, Continued*  
**Package:** `round12_package_20260813.zip`  
**Freeze fields:** `freeze_fields_r12.json`  
**Review prompt:** `THIRD_EYE_REVIEW_PROMPT_v12.md`  
**Reviewed commit:** `1b71b4fa9489fbab4e91d6d5f8441acda7202048`  
**Review date:** 2026-08-13  
**Mandate:** adversarial recomputation and a binary Stage-A ruling.

# Binary ruling

## **REJECT WITH REQUIRED CHANGES**

Round 12 is authentic, internally coherent, numerically reproducible, and materially better than Round 11. The ZIP and every internal checksum pass; the Git bundle is complete; the eight-ruling chain is present; the 173-test collection passes; the self-test is byte-identical; the Round-11 smoke signature reproduces; the production calibration independently recomputes to approximately `10^-14` relative agreement; the named Round-11 counterexamples have all been repaired; and freeze record v3.2 correctly replaces v3.1.

Those successes do **not** close Stage A. Two fresh counterexamples remain:

1. **C29/C31 is not enforced for the package's actual `calibration_ok=false` artifact.** External calibration hash verification, the verified-hash log line, the shared runtime schema, production-size checks, and binding checks all sit inside `if calibration_ok is True`. Consequently, the real frozen calibration produces byte-identical curve logs with no hash and with the correct hash; no verification line can appear. A schema-broken `calibration_ok=false` file with duplicate years and an unknown field is also accepted into the nested path even when its own correct hash is supplied. The scientific engine remains nested, but the promised executable byte-binding and runtime schema/provenance contract is absent precisely for the artifact that will actually be used at Stage B.
2. **C30 checks uniqueness on raw IDs, not canonical IDs.** The code tests non-emptiness through `str(rid).strip()` but inserts the original typed/untrimmed value into `seen_ids`. Thus `1` and `"1"`, or `"1"` and `" 1 "`, are accepted as distinct. The first pair then collapses to duplicate string IDs in downstream output. A declared total can therefore be certified using two raw values that are one canonical document identity.

The first defect violates the Round-12 execution/provenance claim; the second leaves acquisition completeness structurally bypassable. The package should not receive a Stage-A timestamp until both are repaired and covered by non-vacuous regressions.

---

# 1. Integrity gate — **PASS**

| Check | Independently recomputed result |
|---|---|
| ZIP SHA-256 | `f4b3ee241a817f8f004599ece29de63fdcadf3ebd7bb1517376cb98a67c07295` — exact match |
| ZIP bytes | `10,563,810` — exact match |
| ZIP entries | `170` — exact match |
| Duplicate entry names | none |
| Unsafe paths | none |
| Symlinks | none |
| ZIP CRC | no bad member |
| `SHA256SUMS` | `169` entries; `169/169` hashes pass |
| `MANIFEST.tsv` | `168` rows; every byte count and hash passes |
| `SHA256SUMS` SHA-256 | `856a63064f6bfc93bccb5a4bb5c14a6ebd90c2d694c5bd621cbfbf809616a9a8` — exact match |
| `MANIFEST.tsv` SHA-256 | `d7c426ba9985d4705bf94aa50e8f8aebd1b24bc1fdb0a089a7cf51881e6a41dc` — exact match |
| Superseded freeze record | v3.1 absent; v3.2 present |
| Ruling chain | rounds 2, 3, 4, 7, 8, 9, 10, and 11 all present |

## 1.1 Git evidence

`git bundle verify evidence/repo.bundle` reports a complete history. Both `HEAD` and `refs/heads/main` resolve to:

```text
1b71b4fa9489fbab4e91d6d5f8441acda7202048
```

The prior reviewed commit `10266bad12500df683c7b7618ce4eae3cba61d16` is available for differential probing. Of the repository files included in the audit package, all 130 tracked files are byte-identical to the Git objects at the declared commit; eight tracked repository-only files are omitted, with no included tracked mismatch.

## 1.2 Freeze fields

The external freeze JSON independently matches the package for the ZIP dimensions, manifest/checksum hashes, Python pin, requirements, three logs, eight rulings, bundle, environment, calibration, and Git commit. Freeze record v3.2 literally contains all 28 flattened freeze-field keys and makes both v0.9 and v0.10 amendments normative.

**Integrity disposition:** authentic and coherent. Rejection is not based on corruption, substitution, or missing evidence.

---

# 2. Independent execution — **PASS, with an explicit environment limitation**

The package records CPython `3.11.9` on macOS arm64 with exact direct dependency pins. The review container exposed CPython `3.13.5`; network isolation prevented installing 3.11.9. I therefore combined the package's hash-bound 3.11.9 execution evidence with independent execution on the available stack.

## 2.1 Test suite

The packaged pinned-environment log records:

```text
173 passed, 1 warning in 61.36s
```

In the review container, the same collected 173 tests were run as five disjoint groups because the wrapper terminated the monolithic invocation before completion without reporting a test failure:

| Group | Result |
|---|---:|
| Core tests | `68 passed` |
| Round-10 + Round-11 repair tests | `32 passed` |
| Round-7 repair tests | `25 passed, 1 warning` |
| Round-8 repair tests | `23 passed` |
| Round-9 repair tests | `25 passed` |
| **Total** | **173/173 passed** |

The sole warning is the existing `PerfectSeparationWarning` in the high-support standardization fixture; it is also present in the package log and is not a failure.

## 2.2 Self-test

The independently generated self-test has exactly five lines and SHA-256:

```text
8651f8f36048d0b3124911e932eaec96eb41053b0b380b6637c5130f66d3da40
```

It is byte-for-byte identical to `evidence/selftest.log`.

## 2.3 Smoke signature

Running from the bundle checkout produced:

```text
crit_abs_z             = 5.820810382338811
crit_abs_z_half        = 5.820810382338811
boot_size_at_null      = 0.1
wald_boot_concordance  = 0.8
calibration_ok         = false
curve decision engine  = full_nested_pass_p
family MDE80           = 0.9
binding.git_commit     = 1b71b4fa9489fbab4e91d6d5f8441acda7202048
binding.years          = full 32-integer vector, 1994..2025
```

The packaged critical value is `5.820810382338911`; the relative difference is approximately `1.7e-14`, well inside the required `1e-12` band. Governing values, output shape, nested engine, full year vector, and MDE80 are otherwise exact.

## 2.4 Independent production calibration

The production command was rerun from the packaged commit:

```text
python src/mde_sim.py --mode calibrate --sigma-delta 0.1 \
  --ncal 200 --B 9999 --out calibration_recomputed.json
```

| Field | Packaged | Recomputed | Disposition |
|---|---:|---:|---|
| `crit_abs_z` | `4.770137256837956` | `4.770137256837804` | relative difference `3.18e-14` |
| `crit_abs_z_half` | `5.5836590117385345` | `5.58365901173862` | relative difference `1.53e-14` |
| `boot_size_at_null` | `0.05` | `0.05` | exact |
| `wald_boot_concordance` | `0.91` | `0.91` | exact |
| `calibration_ok` | `false` | `false` | exact |
| `ncal` / `B` | `200` / `9999` | `200` / `9999` | exact |
| family / sigma | `p1p2` / `0.1` | `p1p2` / `0.1` | exact |
| complete binding | packaged | recomputed | exact, including Git commit |

**Numerical disposition:** credible and reproducible. The rejection does not challenge the smoke or production-calibration numbers.

---

# 3. Named Round-11 repair probes — **PASS**

The prior commit was checked out from the bundle, and the decisive Round-11 counterexamples were reproduced there before testing the current commit.

| Round-11 defect | Old commit | Round-12 commit | Disposition |
|---|---|---|---|
| Forged production calibration, no hash | opens `wald_shortcut` | emits missing-hash refusal and remains nested | repaired for `calibration_ok=true` |
| Correct hash provenance | no verified-hash line | verified hash printed; Wald licensed when all other gates pass | repaired |
| `<a/>No results` | accepted as terminal | structural parser raises | repaired |
| Missing/blank WB ID | counted toward completeness | raises schema failure | repaired for the submitted fixtures |
| Retried 5xx bodies | discarded before archive hook | every retry body reaches in-retry attempt hook | repaired |
| SPROLL transport bytes | decoded/re-encoded | verbatim bytes archived; invalid UTF-8 fails after archive | repaired |
| Recursive calibration schema | reviewer forgery accepted | runtime/packager reject the tested malformed `calibration_ok=true` artifact | repaired for the submitted fixture |
| Freeze record | v3.1 stale | v3.2 covers v0.9/v0.10, smoke, and round-10/11 ruling fields | repaired |

Manual full-artifact probes confirm these are real behavior changes, not merely text edits.

---

# 4. Evidence provenance — **PASS for the staged evidence**

`evidence/environment.json` contains four sequential zero-exit runs: pytest, self-test, smoke, and production calibration. Each staged log hash equals the corresponding zero-exit run's `log_sha256`. The staged calibration SHA-256:

```text
6fd91d8cb7ba48f578dd9244354a63ada707729082c57f317d0b4d7e25c3e474
```

matches the calibration run's `artifact_sha256`. The staged artifact validates under `src/calib_schema.py`, uses production dimensions, and has:

```text
binding.git_commit = 1b71b4fa9489fbab4e91d6d5f8441acda7202048
```

which equals the freeze JSON and bundle commit.

**Submitted-evidence disposition:** the packaged evidence is byte-bound and internally valid. Blocking finding A concerns what the Stage-B executable actually verifies and records when it consumes the real `calibration_ok=false` artifact.

---

# 5. Blocking finding A — C29/C31 gates are skipped for the actual frozen artifact

## 5.1 Root cause

In `src/mde_sim.py`, the external file is parsed first, but all of the following checks are nested under:

```python
if not a.force_nested and cal_data.get("calibration_ok") is True:
```

The guarded checks include:

- shared `validate_calibration(...)`;
- production `ncal/B` dimensions;
- mandatory `--calib-expected-sha256` for an external file;
- file-hash comparison;
- the verified-hash provenance line; and
- full decision-input binding comparison.

The package's actual frozen calibration has `calibration_ok=false`. Therefore none of those runtime checks executes in the real Stage-B path.

## 5.2 Reproducible probe A1 — actual frozen file

Using the packaged calibration and its frozen SHA-256:

```bash
CAL=evidence/calibration.json
SHA=$(sha256sum "$CAL" | awk '{print $1}')

python src/mde_sim.py --mode curve --family p1p2 \
  --theta-grid 0.0:0.0:1.0 --reps 2 --B 19 --sigma-delta 0.1 \
  --calib-json "$CAL" > no_hash.log

python src/mde_sim.py --mode curve --family p1p2 \
  --theta-grid 0.0:0.0:1.0 --reps 2 --B 19 --sigma-delta 0.1 \
  --calib-json "$CAL" --calib-expected-sha256 "$SHA" > correct_hash.log

cmp no_hash.log correct_hash.log
```

Result: `cmp` succeeds. Both logs contain only:

```text
[mde] curve decision engine: full_nested_pass_p
...
[mde] family MDE80 = nan (engine=full_nested_pass_p, ...)
```

There is no missing-hash refusal in the first run and no verified-hash line in the second. Supplying the frozen hash is operationally inert for the artifact that Stage B will actually consume.

## 5.3 Reproducible probe A2 — schema-broken false artifact

Starting from the packaged file, retain `calibration_ok=false`, add an unknown top-level field, and replace `binding.years` with duplicate years. Compute the modified file's own correct hash and run the same curve command.

Observed output:

```text
[mde] curve decision engine: full_nested_pass_p
...
```

No hash verification, schema refusal, production-size check, or binding refusal is emitted. Thus the claimed shared runtime schema is conditional on an artifact already claiming `calibration_ok=true`; it is not a general runtime input gate.

## 5.4 Why this blocks Stage A

This is not a claim that the false calibration improperly opens Wald—it does not. The defect is freeze provenance and executable authority:

- a Stage-B log cannot demonstrate that the nested decision was made while consuming the frozen bytes;
- passing the frozen hash cannot produce the required verified-hash line;
- malformed false artifacts bypass the shared runtime schema entirely; and
- the executable does not distinguish “the frozen calibration was verified and found false” from “an arbitrary or malformed external object claimed false.”

The staged packager evidence is valid, but the actual execution contract promised by C29/C31 is not implemented for the actual frozen artifact.

## 5.5 Required repair

For every external `--calib-json`, before checking `calibration_ok` or selecting an engine:

1. read the file bytes once;
2. require `--calib-expected-sha256`; omission emits an explicit fail-closed refusal and selects nested;
3. hash those same bytes and compare with the expected hash;
4. strict-parse those same bytes with nonstandard constants rejected;
5. validate the shared recursive schema, production dimensions, and binding;
6. print the verified SHA-256 whenever the match succeeds; and only then
7. use `calibration_ok` plus `--force-nested` to decide whether Wald is eligible.

Reading/hash/parsing one byte buffer also removes a parse-versus-hash time-of-check/time-of-use gap.

Add regressions built from a complete, otherwise valid **`calibration_ok=false`** production artifact:

- no hash → explicit refusal + nested;
- correct hash → verified-hash line + nested;
- correct hash but schema-broken false artifact → schema refusal + nested;
- wrong hash → hash refusal + nested.

**C29/C31 disposition: FAIL.**

---

# 6. Blocking finding B — C30 uniqueness is evaluated before canonicalization

## 6.1 Root cause

`src/s01_fetch_metadata.py` currently performs:

```python
rid = rec.get("id")
if rid is None or not str(rid).strip():
    raise RuntimeError(...)
if rid in seen_ids:
    raise RuntimeError(...)
seen_ids.add(rid)
```

The non-empty check uses a normalized string view, but duplicate detection uses the original JSON value. Later, output construction casts the value to `str(...)`. There is no single canonical identity used consistently for validation, uniqueness, completeness, sorting, and output.

## 6.2 Reproducible probe

A one-page fixture declares `total=2` and returns either pair:

```text
1       and "1"
"1"     and " 1 "
```

Observed result:

```text
int-vs-string ACCEPTED [('int', '1'), ('str', "'1'")]
downstream_string_ids= ['1', '1']

trim-variant ACCEPTED [('str', "'1'"), ('str', "' 1 '")]
```

The first pair is especially decisive: completeness is certified as two unique raw IDs, but downstream string conversion produces the same ID twice.

## 6.3 Required repair

Define the canonical ID contract explicitly and apply it once before any counting. A strict option is preferable:

```python
rid_raw = rec.get("id")
if not isinstance(rid_raw, str):
    raise RuntimeError(...)
rid = rid_raw.strip()
if not rid or rid != rid_raw:
    raise RuntimeError(...)
```

Then use `rid` for `seen_ids`, sorting, output, and any archive/log identity. An alternative is to normalize permissible source values, but the normalized value—not the raw object—must govern uniqueness and completeness.

Add regressions for:

- integer `1` plus string `"1"`;
- `"1"` plus `" 1 "`;
- a non-string ID alone; and
- two pages whose raw IDs differ but canonical IDs collide.

**C26→C30 disposition: FAIL.**

---

# 7. Old-commit differential check — **qualified, not a separate blocker**

The 16 new Round-11 test functions were transplanted onto commit `10266ba`. With audit-only compatibility exposure for symbols absent on that commit, the result was:

```text
12 failed, 4 passed
```

The four old-commit passes were:

1. attribute/plain-div anchor behavior;
2. the valid-UTF-8 SPROLL byte test;
3. schema acceptance of a real calibration output; and
4. the nonstandard-constant packager test.

Two qualifications matter:

- The valid-UTF-8 SPROLL test cannot distinguish decoded/re-encoded text because valid UTF-8 round-trips byte-identically. The separate UTF-16/non-UTF-8 test does distinguish the repair and fails on the old commit.
- The NaN packager fixture contains only `{"crit_abs_z": NaN}`. The old packager already exits because all other required fields are absent, so the test passes vacuously and does not isolate strict JSON constant rejection.

The manual full-artifact probes establish that both underlying repairs are genuine. Nevertheless, the package should describe these as **16 Round-11 tests**, not 16 old-failing regressions, unless the fixtures are strengthened. Replace the NaN fixture with a complete otherwise-valid production artifact containing exactly one `NaN` token; use a valid multibyte UTF-8 body and assert the request log/archive byte count and hash if the positive SPROLL arm is intended as a byte-semantic regression.

---

# 8. Non-blocking implementation note

The SPROLL request log column is named `bytes`, but the implementation writes `len(raw)` after UTF-8 decoding rather than `len(raw_bytes)`. For non-ASCII valid UTF-8, the logged number is a character count, not a byte count, although the archived file and SHA-256 are correct. Change it to `len(raw_bytes)` or rename the column to `characters`.

---

# 9. Amendment disposition

| Amendment | Disposition | Basis |
|---|---|---|
| **C10 — FSSA rule** | **PASS** | Existing direct tests and prior closure remain green. |
| **C26 → C30 — acquisition structural closure** | **FAIL** | Named missing/blank-ID probes are fixed, but uniqueness is still computed on raw rather than canonical identity; `1` and `"1"` can certify false completeness. |
| **C27 — template/year binding** | **PASS** | File templates execute and bind their identities; full year vector and `tokens_per_doc` identity remain green. |
| **C22 — event-study failure propagation** | **PASS** | Governing failure and healthy paths remain green in the 173-test collection. |
| **C16 — universal diagnostics** | **PASS** | Existing simultaneous-failure and every-return diagnostics remain green. |
| **C28 → C29 + C31 — calibration authority/schema** | **FAIL** | `calibration_ok=true` licensing is repaired, but the actual false artifact bypasses hash verification, provenance logging, runtime schema, production-size, and binding gates. |
| **C24 → C32 — freeze record** | **PASS** | v3.2 is present, v3.1 absent, v0.9/v0.10 normative, all current freeze fields represented. |
| **C19 — ruling chain** | **PASS** | Eight supplied rulings are present and hash-valid; round 6 remains explicitly pending as declared. |
| **C25 — smoke numbers** | **PASS** | Critical values within `1e-12`; boot/concordance/ok, nested engine, shape, and MDE80 unchanged. |
| **C27.4 — declared shape note** | **PASS** | `binding.years` is the full 32-integer vector and the smoke numerical signature is unchanged. |

---

# 10. Required changes before resubmission

1. **Move external calibration byte/hash/strict-JSON/schema/production/binding verification ahead of the `calibration_ok` branch.** Ensure the actual false frozen artifact produces the verified-hash provenance line when the correct hash is passed and an explicit fail-closed line when it is absent/wrong/malformed.
2. **Canonicalize or strictly type document IDs before uniqueness/completeness.** Use the same canonical value in `seen_ids` and downstream output; add type and whitespace collision regressions.
3. **Strengthen and accurately describe the differential tests.** Make the NaN fixture otherwise valid, and call the set “16 Round-11 tests” unless the intended old-commit failure matrix is actually achieved. Correct the SPROLL request-log byte count.
4. Rerun the full pinned four-run harness, rebuild the package, advance the amendment/freeze record and ruling chain as required, and provide a new external freeze JSON.

# Final ruling

## **REJECT WITH REQUIRED CHANGES**

The Round-11 blockers are substantially repaired, and the evidence/numerics are sound. Stage A remains open because the actual frozen calibration is not runtime-verified or runtime-schema-checked in its real `calibration_ok=false` path, and acquisition completeness still does not operate on canonical document identities.
