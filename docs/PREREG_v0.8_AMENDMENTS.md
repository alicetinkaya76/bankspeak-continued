# PREREG v0.8 AMENDMENTS (C20–C25) — round-9 required changes

Binding on top of v0.5 + v0.6 (C1–C12) + v0.7 (C13–C19). Round-9 verdict:
REJECT; four areas. All eleven reviewer probes were independently
reproduced before repair.

## C20 — Acquisition is byte-verbatim, write-once, schema-checked (supersedes the acquisition half of C13)
1. The s01 page hook fires BEFORE any parsing and receives the VERBATIM
   transport BYTES (`response.content`); a transport without a raw byte
   body aborts. Text re-encoding is forbidden; archived bytes are the
   server bytes. A malformed body is therefore archived before its parse
   failure propagates.
2. Schema minimum: a WB payload lacking `total` or `documents` RAISES —
   a schemaless response is never an empty result.
3. The declared total is fixed by the FIRST page; any later page declaring
   a different total RAISES (drift), and completeness is checked against
   the first-page total.
4. Raw archives are write-once: an existing per-page file, or a non-empty
   raw directory at run start, RAISES. A rerun must target a fresh
   directory. The request log remains append-only; its row count and
   payload hash are computed over the raw bytes (row counts are
   informational; decision data comes from s01's own parse).
5. IMF SPROLL positive-terminal contract: a zero-row page is a legal
   terminal page ONLY if it (a) contains no anchors, (b) matches no
   documented INTERSTITIAL_MARKERS (captcha/unavailable/maintenance/
   access denied/forbidden/rate limit/temporarily/error), and (c)
   POSITIVELY matches a documented TERMINAL_MARKERS entry ("no results").
   Anything else RAISES. Stage-B capture re-verifies the marker sets
   against the live page before reliance.
6. docty verification binds to the REAL s00 probe: `--docty-probe-artifact`
   is required with `--docty-verified`; the artifact's sha256 is
   RECOMPUTED and must equal `probe_sha256`, else abort.

## C21 — Family-bound, input-bound calibration (supersedes the calibration half of C14)
1. The {P1,P2} calibration consumes BOTH panels: the null |z| sample pools
   z1 and z2 (n_null = 2·ncal; the same order-statistic rule with n_null),
   and the nested reference decision is the FAMILY Holm decision from
   nested PASS-P p-values of both panels. `boot_size_at_null` and
   `wald_boot_concordance` are family-level. The P0 family calibrates on
   its own singleton draw as before.
2. Seed-offset registry addition: the P2 nested stream in calibration uses
   `SEED + 150000 + i`.
3. The calibration artifact carries a `binding` block: family, years,
   alpha, rho, sigma_delta, companion, seed, p2_start_year, base_rates,
   template identities (file sha256 or flat token value), git_commit.
4. A curve run may take the Wald shortcut ONLY when calibration_ok is
   strictly true, the required critical values are numeric, and the
   run's own binding EQUALS the calibration's binding (git commit
   included, non-null). Any mismatch refuses (fail-closed) to nested.
5. Engine-banner truth: the decision engine is resolved COMPLETELY before
   it is announced; refusal reasons print before a single banner line and
   the final MDE line reports the same engine. A run can never print
   `wald_shortcut` and then refuse.
6. Templates must cover EXACTLY the simulation grid (missing OR extra
   years abort) and every token value must be finite and > 0.

## C22 — Event-study failure propagation (closes C15)
`event_study` propagates the governing PASS-E state: `governing_ci ==
"failed"`, a failed/jackknife_failed `method_ci`, or `B_valid_ci == 0`
forces top-level `status: "failed"` with `failure_reasons`; `"ok"` is
only reported when none hold.

## C23 — Fail-closed freeze builder + execution provenance (supersedes C17)
1. Production calibration constants are frozen: ncal = 200, B = 9999. The
   packaged calibration must be strictly typed (numeric crit_abs_z AND
   crit_abs_z_half; boot_size/concordance in [0,1]; calibration_ok a
   strict boolean), at the production sizes, and carry a complete binding
   block with a non-null commit. A pilot (e.g. B=999) aborts.
2. The packaged calibration's `binding.git_commit` must EQUAL the packaged
   HEAD. Evidence outputs (calibration_pinned.json, environment.json,
   logs, zips, freeze-field JSONs) are .gitignored so they are generated
   AT the packaged commit with a clean tree.
3. `tools/run_evidence.py` executes the evidence commands itself and
   writes an environment record with `runs[]` (command, exit_code,
   log_sha256, started/ended UTC). The packager requires `runs[]` and
   cross-checks every staged log hash against a zero-exit recorded run.
4. The ruling chain must include round2, round3, round4, round7, round8,
   round9 (round6 remains a pending textual item, declared, not silently
   absent). `--freeze-fields` requires `--git-bundle`.

## C24 — Freeze record v3.1 (closes C18)
`STAGE_A_FREEZE_RECORD_v3.1.md` carries a literal placeholder for EVERY
freeze-field key, `built_utc` included. The Stage-A object is
PREREG_DRAFT_v0.5.md + v0.6 + v0.7 + v0.8 amendments + the approved
package zip.

## C25 — Declared smoke-signature change (calibrate block only)
Family pooling (C21) changes the smoke calibrate outputs BY DESIGN:
container reference `crit_abs_z = crit_abs_z_half = 5.8208103823388075`
(pinned venv `5.820810382339013`; platform band: relative ≤ 1e-12),
`boot_size_at_null = 0.1`, `wald_boot_concordance = 0.8`,
`calibration_ok = false`, plus `family` and `binding` fields. The
DECISION path is unchanged: the smoke curve still runs
`full_nested_pass_p` and `family MDE80 = 0.9` exactly as before; the
engine selftest is untouched and remains bit-identical.
