# SAP ADDENDUM A1 — Coveo transport for the s09a Article IV listing capture

Date: 2026-08-19. Status: NORMATIVE for Stage-B. Amends only the live
capture transport of the IMF Article IV listing (PREREG v0.5 Appendix B
capture layer), under the preregistered never-silently provision for
live-page divergence documented in `s09a_imf_articleiv_frame.py`. The
frozen decision logic — `build_frame`, revision resolution, flags, audit —
is untouched; the listing schema delivered to it, (title, url, pub_date),
is unchanged. Background and evidence: see
`docs/DEVIATION_20260819_phase1_sproll.md` and
`diagnostics/20260819_sproll/`.

## A1.1 Endpoint and authentication

POST `https://imfproduction561s308u.org.coveo.com/rest/search/v2?organizationId=imfproduction561s308u`

Headers sent, exactly three: `authorization: Bearer <imf_coveo.api_key>`,
`content-type: application/json`, and an honest research User-Agent
(`Mozilla/5.0 (compatible; bankspeak-continued/0.1; +mailto:<contact>)`).
The key is the site's PUBLIC Coveo search key, served to every visitor in
the page bundle (config `imf_coveo.api_key`); it may rotate — a rotation
surfaces as 401/403 and the capture aborts fail-closed (error pages are
never terminal), after which the key is re-discovered from the public page
and this config value updated with a dated note.

## A1.2 Request body

The body is the page's own query, verbatim: `aq` (title wildcard
`Article-iv-Consultation`, Bucket/Media-folder exclusion, `(@imfdate)`
requirement), `cq` (ENG language gates + the IMF-ORG source list),
`fieldsToInclude`, `searchHub: Search`, `sortCriteria: @imfdate
descending`, `locale/tab/referrer/timezone` — minus the browser-session
fields `actionsHistory` and `analytics` (incl. clientId). Neutrality of
that removal is evidenced, not assumed: probe P1 (verbatim browser body)
and P2 (stripped body) returned identical `totalCount` (7451). The
population is defined by the page's own filters; this addendum does not
reinterpret it — heterogeneity in the listing (e.g. press-release items
whose titles match) is classified downstream by the frozen title-driven
logic, as it would have been for the HTML rows.

## A1.3 Pagination, partitioning, integrity gates

`numberOfResults = 100` (config `imf_coveo.page_size`), `firstResult`
stepping, `sleep_seconds = 1.0` between requests. Capture order:

1. Measurement request (page 0): the unpartitioned query at offset 0. Its
   `totalCount` is recorded as the global population size; its results are
   NOT collected, so partitions cannot double-count.
2. Year partitions `imf_coveo.year_lo..year_hi` (1946–2026): the same body
   with `(@imfdate>=YYYY/01/01 @imfdate<=YYYY/12/31)` appended to `aq`.
   Note: Coveo evaluates the window in the body timezone while `imfdate`
   stamps are midnight US-Eastern, so year-boundary items may be ASSIGNED
   to the adjacent partition; this is harmless because coverage remains
   exhaustive and disjoint (enforced by the gates below) and the frame year
   is always derived from the parsed `pub_date`, never from the partition.

Integrity gates, all fail-closed aborts:
- HTTP status != 200 (error pages never terminal; body archived first);
- response not strict-UTF-8 JSON, or lacking integer `totalCount` / list
  `results` (schema drift);
- zero results at an offset below the partition `totalCount` (result-depth
  wall or index drift);
- `totalCount` drift within a partition (live index changed mid-capture);
- collected count != partition `totalCount` (exact match required);
- duplicate or missing `permanentid` (uniqueness across the whole capture);
- missing `imfdate` on any result (the `(@imfdate)` filter guarantees it);
- Σ(partition totals) != unpartitioned `totalCount` (exhaustive/disjoint).

Positive terminal (JSON analog of the round-9 contract): a page is terminal
iff `results == []` AND `firstResult >= partition totalCount`.

C20 analog (live re-verification, recorded): the measurement request's
`totalCount` is compared against the count displayed on the rendered page
("Results 1-10 of N"). Observed 2026-08-19: both 7,451 (operator
screenshot; probes P1–P4 archived).

## A1.4 Raw archiving and logging

Raw responses are byte-verbatim, write-once files `coveo_page_%04d.json`
in `data/meta/imf_articleiv_raw/`; the write-once guard also rejects a
directory holding stale `sproll_page_*.html` archives. A rerun must target
a fresh raw directory; prior attempts are preserved under dated names.
`request_log.csv` is append-only with schema v2: `utc, page, url, status,
bytes, req_body_sha256, results, total_count, resp_sha256, raw_file` — the
request body is hashed into the log so every query issued is reproducible
from the log alone.

## A1.5 Conduct

Public data; the site's robots.txt (read 2026-08-19) does not disallow the
listing path. One request per second; an identified research User-Agent
with a contact address; no Coveo usage-analytics endpoints are called and
no browser session is impersonated (no cookies, no clientId, no
actionsHistory).

## A1.6 Superseded transport and tests

`fetch_live_sproll` (static-HTML SPROLL capture) is retained in the source,
unmodified, as the superseded transport for the audit record; live capture
uses `fetch_live_coveo` only. Fixture tests: `tests/test_s09a_coveo.py`
(13 tests; old-commit matrix: all FAIL at the sealed commit `20af74e7` —
new-behavior arms). Full suite after this addendum: 196 passed.

---

# SAP ADDENDUM A2 — catalog fields in the Article IV listing capture

Date: 2026-08-19. Status: NORMATIVE for Stage-B. Amends the A1 capture
layer only; the frozen decision logic (`classify_row`, `parse_report_no`,
`build_frame`, revision resolution) is untouched, and no preregistered
rule is reinterpreted.

## A2.1 What the first live capture showed

The A1 capture succeeded on its own terms (171 pages, listed 7451 ==
collected 7451, partition sum verified), but the frame it produced held 6
units. The audit accounts for every row, and the shortfall is not a
classification error - it is two inputs the frozen classifier expects and
the A1 capture did not supply:

- `report_no`: the preregistered unit is one IMF Country Report number
  (Appendix B.4/B.5), and Appendix B.1 names two catalog anchors for the
  frame - the imf.org SPROLL listing AND the eLibrary series listing
  (series 002, volume = year, issue = report number). A1 implemented only
  the first. SPROLL titles almost never carry the number: 20 of 7451.
- the country alias map: `SEED_ALIASES` covers ~60 members and the source
  declares it "extended at Stage-B via config/imf_country_aliases.yaml",
  which does not yet exist. That file is prepared separately; it is not
  part of this addendum.

## A2.2 Where the report number comes from

Field probes (archived in `diagnostics/20260819_sproll/`) show the IMFs

---

# SAP ADDENDUM A2 — catalog fields in the Article IV listing capture

Date: 2026-08-19. Status: NORMATIVE for Stage-B. Amends the A1 capture
layer only; the frozen decision logic (`classify_row`, `parse_report_no`,
`build_frame`, revision resolution) is untouched, and no preregistered rule
is reinterpreted.

## A2.1 What the first live capture showed

The A1 capture succeeded on its own terms (171 pages, listed 7451 ==
collected 7451, partition sum verified), but the frame it produced held 6
units. The audit accounts for every row, and the shortfall is not a
classification error — it is two inputs the frozen classifier expects and
the A1 capture did not supply:

- `report_no`: the preregistered unit is one IMF Country Report number
  (Appendix B.4/B.5), and Appendix B.1 names two catalog anchors for the
  frame — the imf.org SPROLL listing AND the eLibrary series listing
  (series 002, volume = year, issue = report number). A1 implemented only
  the first. SPROLL titles almost never carry the number: 20 of 7451.
- the country alias map: `SEED_ALIASES` covers ~60 members and the source
  declares it "extended at Stage-B via config/imf_country_aliases.yaml",
  which does not yet exist. That file is prepared separately; it is not
  part of this addendum.

## A2.2 Where the report number comes from

Field probes (archived in `diagnostics/20260819_sproll/`) show the IMF's own
index carries the catalog datum on the same records the listing already
returns: `seriesvolumeno` = "Country Report No. 2026/221", alongside
`imfseries` = "IMF Staff Country Reports". This is the eLibrary anchor's
content — series, volume (year), issue (number) — served by the publisher's
own catalog, so A2 takes it from there rather than opening a second scraping
surface. Coverage, measured by field-existence queries against the same
population: 2921 of 7451 items carry `seriesvolumeno` and 2911 carry
`imfseries`; the remainder are Public Information Notices, press releases
and mission concluding statements, which are not Staff Country Reports and
are excluded by the preregistered rules regardless. The 1999 slice (24 of
151 items with a catalog number) matches the external record: voluntary
publication of Article IV staff reports began with the Executive Board's
April 1999 pilot project.

VERIFICATION OBLIGATION (before the frame is used in any analysis): a
random sample of 30 captured report numbers is checked against the
corresponding IMF publication page / eLibrary issue, and the agreement rate
is recorded in `docs/`. The capture is accepted only if the sample agrees
exactly.

## A2.3 What the capture now emits

`fieldsToInclude` gains `seriesvolumeno`, `imfseries`, `imfisocode`,
`imftype`. The listing CSV gains four columns:

- `report_no` — the raw `seriesvolumeno` string, VERBATIM and unparsed. The
  frozen `parse_report_no` remains the only interpreter, and it already
  accepts the catalog's spacing and four-digit volume
  ("Country Report No.  1999/149" → CR1999-149).
- `src_imfisocode`, `src_imfseries`, `src_imftype` — provenance only. The
  frozen classifier reads none of them; they travel in the listing for
  auditing and for the alias-map validation described below. Single-element
  lists are unwrapped; multi-entry lists are preserved pipe-joined
  ("DEU|FRA") so multi-country tagging stays visible instead of being
  silently collapsed.

`imflanguage` is deliberately NOT mapped onto the listing's `language`
column: it is coded "ENG" while the frozen rule tests equality with
"English", so mapping it would silently reject every row. The `cq` filter
already restricts the query to English.

## A2.4 Country determination is unchanged

Appendix B.4 defines the country as the single ISO-3166 entity named before
the colon in the title. That rule stands; `imfisocode` does NOT become the
country source. It is retained as an INDEPENDENT CHECK on the alias map:
once `config/imf_country_aliases.yaml` exists, the agreement between the
title-prefix mapping and the IMF's own ISO tagging is computed over the
whole listing and reported, with every disagreement listed. A discrepancy is
resolved in favour of the preregistered title rule and recorded, never
silently.

## A2.5 Capture supersession

The A1 capture (`data/meta/imf_articleiv_raw`, 2026-08-19) is preserved
unmodified as the superseded attempt under a dated name; the A2 capture
targets a fresh raw directory. Both remain write-once. The A2 capture is the
frame-defining snapshot; the A1 capture's listing remains in the record as
evidence of the shortfall this addendum repairs.

---

# SAP ADDENDUM A3 — window recursion replaces offset pagination

Date: 2026-08-19. Status: NORMATIVE for Stage-B. Amends the A1/A2 capture
layer only; the frozen decision logic is untouched and no preregistered rule
is reinterpreted.

## A3.1 What the second live capture showed

The A2 run aborted inside year 2002:

    duplicate permanentid 5d4b9a1b…7fae (years 2002 and 2002)
    - partition overlap, aborting

Both labels name the SAME year, so this was not an overlap between
partitions: the same item was returned twice WITHIN one year, on two
consecutive offset pages (requests 66 and 67, each reporting totalCount 228).
The A1/A2 design walked a year with `firstResult` steps, which is sound only
if the server's result order is stable across separate requests. It is not:
`sortCriteria` is `@imfdate descending` and hundreds of items share a
publication date, so the order among tied items can differ between two
requests. When it does, an item that sat at the end of one page can reappear
at the start of the next — and, symmetrically, another item is skipped
entirely. The A1 run completed only because it did not happen to be
reordered; the guard caught the fault the first time it occurred, but the
design invited it, and a silently skipped item would have been far worse
than a loud duplicate.

## A3.2 The contract that replaces pagination

Every request now carries a date window and is accepted ONLY if it returns
that window entire:

    len(results) == totalCount, with firstResult always 0

A window that comes back truncated is never paginated. It is SPLIT — year
into its twelve months, a month into its days — and each child is captured
under the same contract, with the children's totals required to sum to the
parent's. A day that is still truncated is a hard floor: the capture aborts
and asks for a larger `page_size` rather than guessing.

Because no two requests ever cover the same window, a reordering between
requests can no longer duplicate or skip an item. The ordering assumption is
removed from the design instead of being defended by a guard.

`imf_coveo.page_size` becomes 1000 (the service cap), which comfortably
exceeds the largest observed year (335 items, 2013), so in practice one
request captures one year: about 82 requests for 1946–2026 instead of 171,
with no pagination at all.

## A3.3 Guards retained and added

Retained from A1/A2: write-once raw archives (both `coveo_page_*.json` and
any stale `sproll_page_*.html`), append-only request log, non-200 abort,
strict-UTF-8 JSON abort, schema-drift abort, permanentid uniqueness and
presence, imfdate presence, and the global sum check against the
unpartitioned `totalCount`. Added by A3: the entire-window contract, the
child-sum check at every split, an incoherence check
(`len(results) > totalCount`), the day floor, and a final
`collected == totalCount` assertion. The request log gains a `window` column
so every archived response is traceable to the exact window it answers.

## A3.4 Capture supersession

The aborted A2 capture (`data/meta/imf_articleiv_raw`, 68 archived
responses) is preserved unmodified under a dated name, as is the completed
A1 capture. The A3 capture targets a fresh raw directory and is the
frame-defining snapshot. Tests: the Coveo module is rewritten around the
window contract (24 arms); suite 207 passed.

---

# SAP ADDENDUM A4 — the country alias map

Date: 2026-08-19. Status: NORMATIVE for Stage-B. Supplies
`config/imf_country_aliases.yaml`, the extension of `SEED_ALIASES` that
`s09a_imf_articleiv_frame.py` has provided for since Stage-A ("extended at
Stage-B via config/imf_country_aliases.yaml"). No code and no preregistered
rule changes: Appendix B.4's rule — the country is the single ISO-3166
entity named before the colon in the title — is applied exactly as frozen;
this file only tells the frozen classifier which ISO 3166 entity each
observed prefix names.

## A4.1 How the codes were assigned

Every key is a title prefix actually observed in the A3 capture, lowercased
(the classifier normalizes and lowercases before lookup). Every value is
assigned from the NAME the prefix carries and then verified against the ISO
3166 register (pycountry, 249 entries): 169 aliases, 128 distinct codes, of
which all but two resolve in ISO 3166-1. None of the 169 keys collides with
a `SEED_ALIASES` entry, so the seed map is extended and never overridden.

`imfisocode` was NOT used to assign codes. The capture showed the field is
unreliable as an authority on the document's subject country: of 21 rows
whose title begins "Papua New Guinea", 12 are tagged GIN (Guinea) and 9
PNG; of 21 "Mauritius" rows only 8 are tagged MUS, the rest CHN, IND, SGP,
USA, MDG, IRQ, PAK, BWA, NZL; "Republic of Latvia" rows carry LVA on 13 of
20, with DEU, SWE, EST, LTU, POL, CZE and VGB on the others. The field
appears to record countries mentioned in a document rather than the country
the document is about. It is retained as a diagnostic
(`tools/audit_country_aliases.py`) whose disagreements are inspected by
name, not as a validation oracle.

## A4.2 Names containing " and "

The frozen classifier consults the alias map BEFORE the regional-token test
— the source comments this as the round-7 "Trinidad and Tobago" provision.
Five keys therefore restore single ISO 3166 entities whose names contain
" and " and which the token test had swept into the regional bucket:
São Tomé and Príncipe (three spelling variants, 9 publications) and St.
Vincent and the Grenadines (two variants, 2 publications). Genuinely
multi-entity prefixes remain excluded: Euro Area Policies, Eastern
Caribbean Currency Union, the Curaçao-and-Sint-Maarten reports, and Serbia
and Montenegro.

## A4.3 The four judgment calls (J1–J4)

Each is one line in the YAML, marked with its tag, and each can be removed
without touching anything else.

- **J1 Republic of Kosovo -> XKX (10 publications).** Kosovo has no ISO
  3166-1 code; XKX is the user-assigned code in common statistical use (the
  IMF's own tag is UVK). Including it under a user-assigned code is a
  deliberate reading of "ISO-3166 entity"; excluding it would drop a
  jurisdiction with ten Article IV staff reports from the frame. Recorded
  as a deviation, and a sensitivity check dropping XKX is available.
- **J2 Kingdom of the Netherlands-Netherlands Antilles -> ANT (3).** ANT
  was withdrawn from ISO 3166-1 in 2010 and is retained in ISO 3166-3; the
  reports predate the dissolution.
- **J3 bare "Kingdom of the Netherlands" -> NLD (12).** ISO 3166-1 names
  NLD "Netherlands, Kingdom of the", so the prefix names NLD. Two of the
  twelve rows are titled "Kingdom of the Netherlands: Aruba: …" and are
  thereby attributed to NLD rather than ABW. This is a property of the
  frozen first-colon rule, not of this map; both rows are listed here so
  the misattribution is on the record and can be dropped in a robustness
  check.
- **J4 "The Socialist Peopled Libyan Arab Jamahiriya" -> LBY (1).** An IMF
  typo for the Libyan entity; the prefix still names LBY.

## A4.4 Deliberate exclusions (not in the map)

- "Federal Republic of Yugoslavia" (1) and "Serbia and Montenegro" plus its
  two per-republic variants (3): historical unions; ISO 3166-3 lists them
  as withdrawn entities, and the per-republic reports name two entities in
  one prefix.
- "West Bank and Gaza Strip" (1): the IMF reports on it as a special
  jurisdiction; it is not an ISO 3166-1 entity, and the IMF's own tag on
  the row is ISR, which the title plainly contradicts.
- Malformed prefixes where no country name precedes the first colon:
  "Eritrea 2003 Article IV Consultation Staff Report" (1) and "KENYA Staff
  Report for the 2001 Article IV Consultation" (1), and "Kingdom of the
  Netherlands-Netherlands Staff Report for the 2002 Article IV
  Consultation" (1). Adding the entire malformed string as an alias key
  would defeat the rule rather than apply it.
- Prefixes carrying undecoded HTML entities:
  "Turkey&#8212;2010 Article IV Consultation and Post-Program Monitoring"
  (1) and the two Curaçao/Sint Maarten variants. The entities are the
  publisher's own encoding artifacts, preserved verbatim in the capture.

Total deliberately excluded on these grounds: 9 publications, each listed
above. Measured coverage after this map: of 2921 publications in the
captured listing, 34 (1.2%) have an unmapped prefix, and all 34 are
accounted for above — 28 genuinely multi-entity (Euro Area Policies 17,
Curaçao and Sint Maarten 9, Eastern Caribbean Currency Union 2) and the 9
listed exclusions, less overlap. Row-level agreement with imfisocode:
2776 of 2849 (97.4%).

## A4.5 Audit

`tools/audit_country_aliases.py` reruns offline against the archived
listing and reports (1) publications whose prefix is still unmapped, with
counts per prefix, and (2) row-level agreement with `imfisocode` plus every
disagreeing prefix. The frame itself is rebuilt from the archived listing
with `--listing`; no network access is involved, so the alias map can be
revised and the frame regenerated without a new capture.

## A4.6 The two systematic disagreements, inspected

The audit (A4.5) separates scattered disagreement — the noise pattern of
`imfisocode` — from disagreement concentrated on a single competing code,
which is the signature of an error in this map rather than in the tag. Two
prefixes showed the concentrated pattern and were inspected by title.

**"Republic of Congo" -> COG (12 rows, tagged COD on 9).** The map is
correct and stands. Every title reads "Republic of Congo: …"; the
Democratic Republic of the Congo appears under its own name and its own
seed alias. The decisive evidence is internal to the listing: the SAME 2007
consultation is present twice, differing only in punctuation
("Republic of Congo: 2007 Article IV Consultation, Staff Report; …" and
"… : 2007 Article IV Consultation: Staff Report; …"), and the two copies
carry DIFFERENT country tags — COG on one, COD on the other. One document,
two codes: the field cannot be adjudicating the subject country. This
alias predates the present map; it is a `SEED_ALIASES` entry frozen in
Stage-A.

**"People's Republic of China" -> CHN (24 rows, tagged HKG on 3).** The map
applies the preregistered rule correctly and stands, but the three tagged
rows are genuine J3-class misattributions and are recorded as such. Their
titles are "People's Republic of China: Hong Kong Special Administrative
Region: 2007 / 2008 / 2010 Article IV Consultation …": the entity the
document concerns is Hong Kong SAR, while the frozen first-colon rule reads
the prefix as the People's Republic of China. The IMF used two formats for
the same name over time — the HYPHENATED form ("People's Republic of
China-Hong Kong Special Administrative Region", 20 publications) puts the
whole name before the colon and this map sends it to HKG correctly; only
the colon-separated form is misread, and only the frozen rule can misread
it.

**J3 class, final extent: five publications.** Two Aruba rows under
"Kingdom of the Netherlands" (attributed to NLD) and three Hong Kong SAR
rows under "People's Republic of China" (attributed to CHN). All five are
listed here, none is silently corrected — correcting them would require
changing the frozen country rule — and all five are droppable in a
robustness check.

Method note: these two cases were found only because `imfisocode` is
retained as a diagnostic rather than used as the country source. Had the
field been trusted as an oracle, the Congo rows would have been
misassigned to COD on the strength of a tag that contradicts itself within
one document; had it been discarded entirely, the Hong Kong
misattributions would never have surfaced.

---

# SAP ADDENDUM A5 — WB P0 capture: the G2 measurement, its consequence, and a declared sensitivity arm

Date: 2026-08-20. Status: NORMATIVE for Stage-B. Records the World Bank
side of the Stage-B metadata acquisition, one repair to the capture script,
the measured G2 quantity, and one sensitivity arm declared in advance. No
preregistered rule is changed and no outcome data has been read: everything
below is metadata and simulation-input only.

## A5.1 The WB P0 capture

`s00_discover_facets` ran live on 2026-08-19 and wrote
`data/meta/facets.json` (sha256
`48590bf062e74d7241e260bf15eb7a2882430ab83378da284e3ad7eb11bc61f6`). The
WDS v3 endpoint answered both a pipeline and a browser User-Agent with HTTP
200, so — unlike the IMF side (addenda A1–A3) — no transport amendment was
needed.

The three P0 candidate labels shipped frozen in `config/wb_p0_docty.yaml`
were confirmed VERBATIM against that probe, as Appendix B.10 requires, and
none needed correction:

| genre | docty | all languages | English |
|---|---|---|---|
| cem | Country Economic Memorandum | 693 | 549 |
| scd | Systematic Country Diagnostic | 282 | 211 |
| cpf | Country Partnership Framework | 850 | 729 |

`data/meta/docty_verified.json` (verified_utc 2026-08-20T03:00:23+00:00,
source s00, probe_sha256 as above) was then consumed by `s09b`, which
recorded no divergence — the frozen mechanism for corrected labels was
exercised and found nothing to correct.

The live capture covered 1946–2025 for all three candidates: 240 year
requests, each returning its year whole (no page in the write-once archive
declares a total larger than the records it returned), yielding 1304
listing rows and a frame of 491 units. The audit accounts for every row:
603 unmapped country, 491 included, 150 regional/multi-country, 59
superseded versions, 1 without a country field.

Two coverage facts are recorded so they are not mistaken for loss. First,
`cem` returned 549 rows against an English facet count of 549 — exact.
Second, `cpf` returned 546 against a facet count of 729; the 183-document
difference is entirely documents dated 2026, which the preregistered cutoff
(publication date <= 2025-12-31) excludes. `scd` differs by two documents
on the same boundary.

## A5.2 A fail-open repair in s09b

`--g2-report` was accepted and silently ignored on the live path: `main()`
wrote the frame and audit through `_write_outputs` and returned, while the
report-writing block sat below that return and ran only for `--listing`.
The capture therefore produced no G2 report, and nothing said so. This is a
round-8 class defect — a requested check that does not happen and stays
quiet — and it is recorded here rather than quietly patched.

The repair moves the report into `_write_outputs`, which both paths call,
and adds a guard: `--g2-report` without `--imf-frame` is now refused,
because without the comparator the report omits `g2_metadata_ok` altogether
and an omitted field reads as "no objection". Five regression arms ship in
`tests/test_s09b_g2_report.py`; one of them widens the comparator by a
single year and shows the same genre flipping to a pass, demonstrating that
the gate reports a measured quantity and does not encode a verdict. Commit
`acac512`, suite 212 passed.

## A5.3 G2, measured

With the repair in place the report was regenerated through the ordinary
CLI path and is archived at `data/meta/g2_metadata_report.json`:

| candidate | common pre-2023 years with Article IV | completed post years | docs | G2 |
|---|---|---|---|---|
| cem | 22 | 2023, 2024, 2025 | 164 | fail |
| cpf | 24 | 2023, 2024, 2025 | 239 | fail |
| scd | 8 | 2023, 2024 | 88 | fail |

The gate requires at least 25 common pre-2023 years and at least 3
completed post years. No candidate reaches it, and the reason is structural
rather than accidental: the IMF Article IV frame itself spans only 24
pre-2023 years (1999–2022), because the Fund did not publish Article IV
staff reports before the Executive Board's April 1999 pilot project. The
common-year count is bounded above by that 24 for every possible candidate,
so the gate could not have been passed by any WB genre whatsoever. `cpf`
sits exactly at the ceiling: it fails by one year.

Two observations belong in the record. First, the threshold was fixed at 25
in Stage-A, before any of these counts existed; had it been set at 20 the
P0 design would have proceeded. The gate did the work it was preregistered
to do. Second, the obstacle is itself an artefact of institutional
transparency history — the same class of organisational change this study
examines — and not of the design.

The formal branch decision remains `s14_branch_decision`'s to record in its
write-once output; this addendum records the measured input, not the
decision.

## A5.4 Declared sensitivity arm: Staff Appraisal Reports

Declared BEFORE any document text has been read, and recorded here so its
timing is verifiable.

The P1/P2 family's operational stratum is the Project Appraisal Document,
whose D&R label begins in 1997. Its predecessor series, the Staff Appraisal
Report, carries 5,870 English documents and covers the preceding period.
The preregistered stratum is the label "Project Appraisal Document" and it
is NOT changed: extending a population definition after seeing counts is
precisely the researcher degree of freedom preregistration exists to
foreclose.

Instead, a sensitivity arm is declared: the operational-genre analysis will
be repeated with the SAR series appended to the PAD stratum under the same
per-year sampling cap, reported alongside the frozen-definition result and
never in place of it. Any divergence between the two is reported whichever
direction it runs.

This arm cannot be gate-motivated, and the arithmetic shows why: the
binding constraint on the common-year count is the IMF frame's 1999 start,
not the PAD stratum's 1997 start, so adding SAR could not have moved G2 by
a single year. It is declared for coverage, not for passage.

## A5.5 Reproduction from the write-once archive

The live path does not persist the listing, so the listing was rebuilt from
the 240 archived raw pages and re-run through `s09b --listing`. The
resulting frame is byte-identical to the frame written by the live capture
(sha256 `c25ae6002ba37f95c7f87f2c685cbab36c392d6adf2b1707621f9832c863370a`
for both). The write-once archive is therefore sufficient to regenerate the
frame without touching the network.

One limitation is recorded rather than smoothed over: the AUDIT is not
bit-reproducible across that round trip. Exactly one row of 1304 changes
label — document 26806560, "Poland - Country Strategy Paper", dated
1991-06-28, filed under `cpf` — moving between `unmapped_country` (live)
and `excluded_no_country` (reconstructed). Its country field is empty in
BOTH copies; the difference is one of representation, not of content: the
field is absent from the in-memory record and arrives as NaN after a CSV
round trip, and the classifier distinguishes those two cases when naming
the reason for exclusion. The document is excluded either way, both labels
describe an empty country field correctly, and the frame — the unit of
analysis — is identical in membership and in hash. The row is itself a
catalogue artefact: the sole 1991 entry under a genre label introduced much
later, titled "Country Strategy Paper", with no country recorded.

This is NOT repaired. Normalizing NaN and absent to a single case would
mean editing `classify_row`, which is frozen decision logic. The line held
throughout Stage-B has been that the capture and reporting plumbing may be
repaired when the live world differs from the Stage-A model (addenda
A1-A3, A5.2) while the rules that decide what a document IS remain
untouched. Editing a classification rule to make an audit label tidier —
for a document that is excluded under either label — would trade that line
for cosmetics.

## A5.6 Access conditions

Recorded for replication, alongside the IMF-side conditions in
`docs/VERIFICATION_20260819_report_numbers.md` §4:
`search.worldbank.org/api/v3/wds` accepted an identified research
User-Agent without difficulty on 2026-08-19/20, at one request per second,
and returned each year window whole.

## A5.7 Which gates were evaluated, and why

`s14_branch_decision` combines four gates conjunctively. Two are computed by
the script itself from metadata already in hand — G2 (common pre-2023 years,
A5.3) and G3 (country support in the post period). Two require inputs
produced separately: G1, a blind human type audit of drawn documents, and
G4, an MDE figure from a nested power run.

Those two inputs are NOT produced, and the omission is declared here rather
than left to be inferred from the decision file. G2 is dispositive on its own
and unsatisfiable for every possible candidate: the common-year count is
bounded above by the Article IV frame's 24 pre-2023 years, so no WB genre —
including any not on the candidate list — can reach 25. That bound is
verifiable in a single line from the two archived frames and depends on no
judgement of ours. Since the gates are conjunctive, one definitive failure
settles the branch; a blind audit of genres that will not be used, or a
nested power run for a design that will not be estimated, would add hours of
work and no evidence.

The decision file therefore records measured values for G2 and G3, and for G1
and G4 records inputs marked as not evaluated, with the reason carried inside
the artifact. Those two entries must not be read as gates that were tested
and failed. Nothing here asserts that G1 or G4 WOULD have passed; both are
simply unasked, because the answer to the conjunction is already fixed.
