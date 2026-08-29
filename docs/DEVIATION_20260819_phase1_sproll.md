# DEVIATION NOTE — 2026-08-19 — PHASE 1 first attempt (s09a live SPROLL)

Recorded per STAGE_B_RUNBOOK_v1.md ("any deviation gets a dated deviation
note in docs/"). Operator: Ali Çetinkaya. Assistant: Claude (session of
2026-08-16/19).

## D1 — Runbook-ordering slip

The first live run of `s09a` (2026-08-19, ~15:5x TRT) was executed before
GATE 0 check #3 (verification that `round14_package_20260814.zip` appears in
the OSF registration's archived file list, plus a re-download hash check)
had been confirmed. The substantive preregistration gate (§11.1) was NOT
violated: the OSF registration was final and timestamped
`2026-08-16T04:21+00:00` (Registration DOI `10.17605/OSF.IO/5C9J8`) before
any live request was sent. The violation is one of runbook ordering only.
Remedy: check #3 must be completed and its hash result recorded before the
Coveo rerun is executed; this note records the slip rather than hiding it.

## D2 — Attempt-1 outcome (fail-closed, as designed)

Page 1 of the SPROLL HTML capture returned HTTP 403. The engine behaved
exactly per the round-8 contract: the verbatim 403 body was archived
(`sproll_page_0001.html`) and logged before the status check, the error page
was never treated as a terminal page, and no listing/frame/audit output was
written. The attempt-1 raw directory is preserved unmodified under the dated
name `data/meta/imf_articleiv_raw.attempt1-403-20260819` (write-once
archives are never deleted).

## D3 — Out-of-pipeline diagnostics (archived in diagnostics/20260819_sproll/)

Performed to identify the cause; none of these responses enters the corpus.

1. Operator-side curl probes: pipeline UA / browser UA / hybrid UA all
   returned HTTP 403 with an identical 442-byte body; even
   `https://www.imf.org/robots.txt` returned 403 (379 bytes) from the
   operator's network. Conclusion: the block does not discriminate on
   User-Agent.
2. Assistant-side fetch of the same SPROLL URL returned HTTP 200 — but the
   HTML is a client-side-rendered shell (a "Loading component" placeholder
   where the listing belongs; no anchor+date rows). The static-HTML
   structural assumption documented in `parse_sproll_html` therefore does
   not hold on the live page, precisely the divergence scenario the module
   docstring anticipates ("verified against the live page at Stage-B …
   amended in the Stage-B SAP addendum — never silently").
3. Assistant-side read of `www.imf.org/robots.txt`: the
   `/en/Publications/SPROLLs/` path is not disallowed; a sitemap is
   declared. Polite, identified access to the listing is robots-consistent.
4. Browser test on the operator's machine: the page renders fully
   ("Results 1-10 of 7,451"), excluding an IP-level block; the curl 403s
   are therefore client-fingerprint-level (bot management that
   distinguishes non-browser TLS clients regardless of UA).
5. DevTools network inspection identified the listing's data source: the
   site's public Coveo Search API
   (`imfproduction561s308u.org.coveo.com/rest/search/v2`). Probes P1–P4
   from the operator's machine: all HTTP 200; `totalCount = 7451`, equal to
   the count displayed on the rendered page; P1 (the browser's own request
   body, verbatim) vs P2 (browser-session analytics fields stripped)
   returned identical totalCount — the stripped fields are
   population-neutral; the minimal header set (authorization +
   content-type) suffices, and an honest research User-Agent is accepted.

## D4 — Remediation

Transport moved to the site's own data endpoint per
`docs/SAP_ADDENDUM_A1_coveo_transport.md` (normative spec) in the commit
that introduces this note. The frozen decision logic (`build_frame` and
everything downstream) is untouched; the listing schema it consumes —
(title, url, pub_date) — is unchanged. `fetch_live_sproll` is retained
unmodified in the source as the superseded transport.

## D5 — Residual obligations

GATE 0 check #3 (registration-archive zip verification + re-download
`shasum` = `0ca03b60…21114`) remains open at the time of writing and gates
the live rerun. The rerun targets a fresh raw directory (attempt-1 archive
preserved as above).

## D6 — Apply/verify ordering reversed on the transport patch (recorded 2026-08-19)

The kit implementing SAP addendum A1 was applied and committed
(`a1b41ad`) before the kit-side gates had been run in a visible session:
an earlier terminal session had already unzipped the kit, so the
apply-script hash gate correctly refused ("mevcut s09a beklenen orijinal
degil"), and the commit step was then executed past that refusal. The
gates were therefore run POST-HOC, against the committed tree, and all
passed:

- the five kit files hash exactly as shipped
  (`s09a` 6a076184…, `test_s09a_coveo.py` 08c033b5…, `config.yaml`
  b712826f…, this note bb0abb19…, the addendum e3ad9a94…);
- `git show --stat HEAD` = the five expected files, 619 insertions,
  2 deletions;
- the live-capture refusal rehearsal still fails closed (exit 1);
- the test suite ran 195 passed / 1 failed — see below.

No content divergence was found; the commit stands. The residual risk of
this ordering (committing something whose identity has not yet been
checked) is recorded here rather than silently repaired.

## D7 — Fossil-guard drift surfaced by the completed freeze record

The single failing test,
`test_round11_repairs.py::test_freeze_record_covers_current_schema`, was
NOT caused by the transport patch. Its round-12 fossil guard asserted that
`docs/STAGE_A_FREEZE_RECORD*.md` matches exactly one file, to stop a
superseded template from living on unnoticed. Commit `291d156` legitimately
added the completed record (the template with `osf_timestamp` and
`osf_registration_doi` filled in) next to the template, so the glob began
matching two files. The container copy used to build the kit had no
completed record, which is why the kit measured 196 passed there and 195
here.

The guard is split rather than relaxed: exactly one VERSIONED template
(the fossil condition round 12 actually targeted — a second template, or a
versionless one, still fails), at most one COMPLETED record, nothing else
in the family; the schema assertion stays on the template, and the
completed record must carry the same schema with both OSF rows no longer
placeholders. Verified against five trees: template+completed passes;
template-only passes (old behaviour preserved); two templates fail; a
versionless fossil fails; a completed record still holding placeholders
fails. Full suite after the repair: 196 passed.
