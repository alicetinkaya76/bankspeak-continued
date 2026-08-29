# VERIFICATION — 2026-08-19 — Article IV report numbers (SAP addendum A2.2)

Discharges the verification obligation recorded in
`docs/SAP_ADDENDUM_A1_coveo_transport.md` §A2.2: before the IMF Article IV
frame is used in any analysis, a random sample of 30 captured report
numbers is checked against an independent record and the agreement rate is
recorded here. Result: **30 of 30 confirmed, 0 contradictions.**

## 1. What was verified, and against what

The captured report number is the `seriesvolumeno` string the IMF's own
Coveo index returns ("Country Report No. 2026/221"), parsed by the frozen
`parse_report_no` into the frame's unit id (`CR2026-221`). Verifying that
string against the same index would be circular, so the reference is
**Crossref**, the DOI registration agency for the IMF's own deposits under
prefix 10.5089 — an independent authority, and one reachable from the
operator's network (see §4).

Crossref carries the catalogue metadata at the ISSUE-level DOI, not the
article-level one: `10.5089/<ISBN>.002` returns
`container-title: IMF Staff Country Reports`, `volume`, `issue`; the
sibling `10.5089/<ISBN>.002.a001` is typed `component` and carries no
bibliographic fields.

Direction of the check matters. The query is NOT "look up our number and
see what it says" — that would let a wrong number confirm itself. The
sample was queried by COUNTRY and YEAR against the journal's own record
(ISSN 1934-7685), and the record whose volume equals our year and whose
issue equals our number was then required to name OUR country. A wrong
report number would either match no record or match a different country.

## 2. Sample

Drawn from `data/meta/imf_articleiv_frame.csv` (2788 units) with
`pandas.DataFrame.sample(n=30, random_state=20260806)` — the study's global
seed, so the draw is reproducible. Sample retained at
`/tmp/a22_sample.csv` during the session and reproducible from the frame
and the seed alone.

## 3. Result

| pass | n | note |
|---|---|---|
| first pass (country-restricted query, 4-digit volume) | 22 | volume/issue matched and the record named our country |
| second pass (volume-format normalized) | 8 | all eight matched on normalization; see below |
| **total confirmed** | **30/30** | |
| contradictions (record naming a different country) | **0** | |

The eight that failed the first pass were a FORMAT artefact of the
reference, not a discrepancy in our numbers. Crossref holds IMF volumes in
two shapes — the same year appears as both `2003` and `03`, and the 2020
slice also contains a malformed `192020` and a `9999` — so a search for
volume `2020` misses a record stored under `20`. Normalizing a two-digit
volume to its four-digit form resolved all eight, each naming our country
at our issue number:

    CR2006-022  Vietnam                 crossref 2006/022   10.5089/9781451840322.002
    CR2012-037  Kingdom of Swaziland    crossref 2012/037   10.5089/9781463940386.002
    CR2020-091  Belgium                 crossref   20/91    10.5089/9781513538839.002
    CR2004-089  Spain                   crossref 2004/089   10.5089/9781451812060.002
    CR2009-039  Finland                 crossref 2009/039   10.5089/9781451813302.002
    CR2003-049  Belgium                 crossref 2003/049   10.5089/9781451803129.002
    CR2025-030  Republic of Kazakhstan  crossref 2025/030   10.5089/9798400299483.002
    CR2022-058  Republic of Poland      crossref 2022/058   10.5089/9798400203688.002

Note that the ISBNs differ across records, so the eight are distinct
deposits and not an artefact of one lookup.

Reference-quality caveat, recorded because it bounds what this check can
prove: the two volume shapes, the `192020` value and the `9999` volume are
defects in Crossref's IMF deposits, not in the captured numbers. They
affect how a record is FOUND, never which country it names, so they cannot
manufacture a false confirmation — a wrong number would still have to
collide with a real record naming the right country.

## 4. Access conditions at verification time

From the operator's network on 2026-08-19: `www.imf.org` returns HTTP 403
to every non-browser client (three User-Agents plus robots.txt);
`elibrary.imf.org` returns HTTP 202 with a zero-byte body (a silent bot
gate); the IMF's public Coveo endpoint and `api.crossref.org` both respond
normally. This is recorded so a later replication knows which doors were
open — the eLibrary anchor named in PREREG Appendix B.1 was not directly
reachable, and Crossref stands in for it as the independent catalogue of
record.

## 5. Verdict

§A2.2 required exact agreement on the sample. Thirty of thirty confirmed,
no contradiction, and the eight second-pass matches are documented as a
reference-format artefact rather than reported as agreement obtained by
loosening the test. The IMF Article IV frame is cleared for use.
