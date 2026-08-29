# PREREG v0.10 AMENDMENTS (C29–C32) — round-11 required changes

Binding on top of v0.5 + v0.6 + v0.7 + v0.8 + v0.9. Round-11 verdict:
REJECT; four blockers. All six decidable reviewer probes were
independently reproduced before repair.

## C29 — The frozen calibration hash is MANDATORY at execution (closes C28's licensing residue)
1. Any curve run whose calibration comes from an EXTERNAL file may take
   the Wald shortcut ONLY when `--calib-expected-sha256` is supplied and
   the file's sha256 matches it; a missing hash argument refuses
   fail-closed to nested. The Stage-B runbook passes the frozen
   `calibration_sha256` here.
2. On a successful match the verified hash is printed
   (`[mde] calibration artifact sha256 verified: <hash>`) so the run's
   own log carries the provenance line.
3. Runtime licensing additionally validates the artifact against the
   shared recursive schema (C31): a schema-broken artifact is refused
   even with a correct hash.

## C30 — Acquisition structural closure (closes C26's residue)
1. Anchor detection is STRUCTURAL: an HTML parser walks start and
   self-closing tags, so `<a>`, `<a/>`, `<A HREF=...>` and
   newline-attribute variants all count as anchors; the typographic
   regex (now `<a[\s>/]`) remains as a second net, and a parser failure
   counts as anchor-bearing (fail-closed).
2. Canonical ids: a WB record with a missing or blank `id` is a schema
   failure and RAISES; completeness continues to count unique canonical
   ids only.
3. Every retried 429/5xx response body is archived VERBATIM from INSIDE
   the retry layer via an attempt hook
   (`{genre}_{year}_os{os}_attempt{n}_status{code}.json`, write-once,
   logged); a retried response without a raw byte body aborts.
4. SPROLL archives the VERBATIM transport bytes
   (`response.content → write_bytes → bytes-sha256`); parsing decodes
   strict UTF-8 and a decode failure aborts AFTER the bytes are
   archived.

## C31 — One recursive strict calibration schema (closes C28's validator residue)
`src/calib_schema.py` is the single schema consumed by BOTH the runtime
and the packager: ncal/B are REAL positive JSON integers (bool/float
forms rejected); every number is finite (NaN/±Infinity never validate,
and the packager loads calibration JSON with nonstandard constants
rejected at parse time); `p2_start_year` is integer-or-null; `years` is
a list of ≥2 integers, unique and strictly increasing; `family` and
`companion` are closed enums; `base_rates`/`templates` carry EXACT key
sets with typed values (template identities are exactly
`{sha256: 64-hex}` or `{flat_tokens_per_year: finite>0}` or null);
`tokens_per_doc` is finite-positive-or-null; `git_commit` a non-empty
string; unknown decision-bearing fields at either level are rejected.

## C32 — Freeze record v3.2 (closes C24)
`STAGE_A_FREEZE_RECORD_v3.2.md` supersedes v3.1: the frozen-object
definition includes the v0.9 and v0.10 amendments, and literal
placeholder rows exist for `logs.smoke`, `rulings.round10`,
`rulings.round11` and every other freeze field. The superseded v3.1
template is removed from the package.
