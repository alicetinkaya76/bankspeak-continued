# PREREG v0.11 AMENDMENTS (C33–C35) — round-12 required changes

Binding on top of v0.5–v0.10. Round-12 verdict: REJECT; two blockers and
two test-quality findings. All three decidable probes were reproduced.

## C33 — The external-artifact provenance gate runs BEFORE calibration_ok (closes the C29/C31 residue)
Every curve run with an external `--calib-json` now passes, before
`calibration_ok` is even consulted: (1) the artifact bytes are read
ONCE; (2) `--calib-expected-sha256` is MANDATORY; (3) the hash of those
same bytes must match it; (4) the SAME bytes are strict-parsed with
nonstandard JSON constants rejected; (5) the shared recursive schema,
the preregistered production sizes (ncal=200, B=9999) and the
decision-input binding are enforced; (6) the verified hash is written to
the run log UNCONDITIONALLY (`[mde] calibration artifact sha256
verified: <hash>`); (7) only then does calibration_ok (or
--force-nested, which skips loading entirely) select the engine. Any
gate failure ABORTS the run (SystemExit): a Stage-B run must be able to
PROVE which calibration bytes it consumed — including on the real
`calibration_ok=false` frozen artifact, whose nested runs now carry the
provenance line. The former ok=true-branch checks are superseded by
this gate; regression fixtures use a FULLY VALID production-shaped
ok=false artifact as the reviewer required.

## C34 — Canonical STRING document ids (closes the C30 residue)
A WB document id must be a JSON string; non-string ids are a schema
failure. The id must equal its own strip() (surrounding whitespace is a
schema failure) and be non-empty; uniqueness, completeness, ordering and
downstream output all consume this single canonical value. The
`1` vs `"1"` and `"1"` vs `" 1 "` collision probes now RAISE.

## C35 — Test-classification honesty and the byte-count column
1. The round-11 file is declared as "16 tests" whose old-commit result
   is 12 failed / 4 passed: the UTF-8 positive-archive arm and the
   canonical-output arms are behavior-preservation, not flips
   (docstring-marked). The NaN packager fixture is rebuilt on a fully
   valid artifact so its rejection is attributable to the parse-layer
   constant ban alone, and a transport-forgery flip
   (content ≠ text) proves byte-sourced archiving.
2. The SPROLL request-log `bytes` column records `len(raw_bytes)` (true
   transport bytes), never the decoded character count.
3. Freeze record v3.3 supersedes v3.2: one literal ruling row per
   completed round (round12 added; the table grows by one row each
   round before rebuild).
