# PREREG v0.9 AMENDMENTS (C26–C28) — round-10 required changes

Binding on top of v0.5 + v0.6 (C1–C12) + v0.7 (C13–C19) + v0.8 (C20–C25).
Round-10 verdict: REJECT; three areas (C20/C21/C23). All seven reviewer
probes were independently reproduced before repair.

## C26 — Acquisition symmetry (closes the C20 residue)
1. The SPROLL (IMF) side now carries the SAME write-once contract as the
   WB side: a non-empty raw directory at run start RAISES; an existing
   per-page file RAISES; archived bytes and the request log survive a
   refused rerun untouched. The request log is append-only (mode "a";
   the header is written only on first creation) — history is never
   truncated.
2. Anchor detection is semantic, not typographic: a zero-row page is
   anchor-bearing if it matches the pattern `<a` followed by whitespace
   or `>`, so `<a>No results found</a>` can never pass as a terminal
   page.
3. WB completeness is counted over UNIQUE document ids: a duplicate id
   across pages RAISES as a pagination fault, and the final completeness
   check compares the unique-id count to the first-page declared total.

## C27 — Template and year-sequence binding (closes the C21 residue)
1. `pathlib.Path` is imported at module level in the simulator; the
   file-based template path (`--cells-template`, `--template-*`) is
   exercised by regression tests, including the binding's template
   sha256.
2. `--years` accepts comma-separated items mixing single years and a-b
   ranges ("1994-2025", "2018,2020", "1994-2000,2005-2025"); the
   expansion must be strictly increasing (duplicates/disorder abort).
   The binding stores the FULL year vector as a list of integers, not
   the endpoints.
3. `tokens_per_doc` is part of the binding (null when unused): a
   `year,docs` template with a doubled exposure factor can never share a
   calibration identity.
4. Declared smoke-shape change: the smoke calibrate block's `binding`
   now prints `years` as the full vector. All smoke NUMBERS
   (crit/boot/concordance/ok, curve decision, MDE80 = 0.9) are
   UNCHANGED from C25.

## C28 — The packaged production calibration is the ONLY licensed artifact (closes the C23 residue)
1. Curve-side Wald licensing additionally requires the calibration's
   ncal == 200 and B == 9999 (the preregistered production sizes) and
   strictly positive, finite critical values. A hand-edited pilot with a
   copied binding can no longer open the Wald path.
2. `--calib-expected-sha256` pins the calibration FILE hash; the Stage-B
   runbook passes the frozen `calibration_sha256` here, making the
   packaged artifact the single licensed source at execution time.
3. Packager finite-number discipline: NaN and ±Inf are rejected
   everywhere a number is required; crit values and sigma_delta must be
   strictly positive; the binding is TYPE-checked field by field
   (family/companion strings, years a list of ints, alpha/rho/sigma
   finite numbers, seed an int, base_rates/templates mappings,
   tokens_per_doc finite-or-null, git_commit a non-empty string), and
   `p2_start_year` joins the required key set.
4. The provenance harness covers ALL freeze evidence: run_evidence
   executes pytest, the selftest, the smoke AND the production
   calibration in one recorded session; the calibrate step records its
   artifact's sha256, and the packager cross-checks the staged
   calibration byte-hash against a zero-exit recorded run. `logs.smoke`
   becomes a mandatory freeze field, and the ruling chain adds round10.
