# Round 21 — response to the independent package audit of 2026-09-03

Verdict received: **NO-GO — RETURN BEFORE REVIEW / MAJOR REVISION**, with the
scientific core judged intact. Nothing here is estimated; every number below
regenerates from `data/` by a named tool, and the two things that were wrong in
our own work are stated first.

## What the audit found that we had wrong

### The block-origin sweep wrapped the series (§2 of the audit — blocking)

Correct, and reproduced to the digit. `tools/block_origin_enumeration.py` shifted
the origin by rotating the year vector (`np.roll`) before cutting nine blocks of
three. That put fiscal 1999 in the same block as 2024 and 2025 at offset 1, and
with 2025 and 2000 at offset 2 — a block bootstrap groups dependent neighbours,
and rotation manufactures one. `tools/functional_form_sensitivity.py` copied the
same helper, so the origin column of Table 5d carried the same defect.

Both tools now keep time order: a shifted origin leaves a short block at each
end, so it has ten blocks and a support of 1,024 rather than nine and 512. The
frozen origin never wrapped anything and is unchanged; the preregistered result
is exactly what it was.

| offset | P1 rotated → time-ordered | P2 rotated → time-ordered | blocks | support |
|---|---|---|---:|---:|
| 0 (frozen) | 8/512 = 0.0156 → same | 50/512 = 0.0977 → same | 9 | 512 |
| 1 | 164/512 = 0.3203 → **324/1024 = 0.3164** | 78/512 = 0.1523 → **178/1024 = 0.1738** | 10 | 1,024 |
| 2 | 8/512 = 0.0156 → **8/1024 = 0.0078** | 18/512 = 0.0352 → **38/1024 = 0.0371** | 10 | 1,024 |

The audit's four time-ordered cells are these four. What changed in the prose:
"a two-year shift leaves P1 exactly where the frozen origin puts it" was false
and is withdrawn — the shift halves P1's *p*; "exactly three distinct
partitions" with nine blocks each is replaced by three origins with 9/10/10
blocks; and at offset 2 the smaller *p* now clears Holm's 0.025 and the larger
its 0.05, so the sentence about the partition that would have carried a panel
through condition 1 got stronger, not weaker. The rotated values are kept in the
tool's JSON under `circular_rotation_as_previously_published` so the correction
can be checked rather than trusted.

Table 5d was regenerated from the corrected sweep. Every P1 origin count is
unchanged; one P2 count moves (no-trend row, 1/3 → 2/3). The reading in §6.2 —
single-year deletions move the partition, not the evidence — survives with new
figures (dropping 2020: 0.3164 at the frozen origin, 0.0098 and 0.0195 at the
other two). The † footnote on the 15-year row now says "at the frozen origin",
because a shifted origin gives that window six blocks and a floor of 0.031.

`tests/test_round21_checks.py` pins the helper's no-wrap property, the four
reproduced cells, the doubled support, and the withdrawn sentence.

### The evidence deposit did not carry what its list said (§1/§4 — blocking)

Partly the audit's misreading and partly a real defect of ours.

The zip the audit examined had 99 files and a 36-page manuscript; the kit we
delivered has 114 files and the 38-page manuscript with the same SHA-256 as the
uploaded PDF (`685401fe26ef…`), so the version skew described in §1 was between
two different zips. But the audit's method — open the artifact — found two
things that were true of ours:

1. Six tools the manuscript names were not in the kit
   (`block_origin_enumeration.py`, `check_submission_metadata.py`,
   `placeholder_report.py`, `package_evidence_deposit.py`,
   `build_public_repo.py`, `build_third_eye_kit.py`). They are now; the kit is
   110 staged files.
2. Worse: the **evidence deposit** zip carried none of the eighteen analysis
   outputs added to its list in round 20 — no input to S10.3–S10.9 or Tables
   3c–5d. `package_evidence_deposit.py` zipped a staging directory that only
   `prepare_zenodo_deposit.py --copy` refreshes, and round 20 ran the former
   without the latter. The packager now stages, zips and verifies the zip
   against the list in one command, and refuses if any listed file is absent.
   `tests/test_evidence_deposit_freshness.py` reads the built zip.

### Visible inconsistencies (non-blocking, all closed)

- Table 3's late-era label read "2020–2026" beside a cell saying five years,
  2020–2024: a search bound in `make_paper_tables.py` leaking into a label.
  The bound now equals the window every other table uses.
- 0.036 / 0.0365 and 0.093 / 0.094 were the same two quantities rounded two
  ways. They are 146/4,000 = 0.0365 and 374/4,000 = 0.0935 everywhere, with
  the fraction at first mention as the audit suggested.
- The supplement's opening sentence claimed everything in it had been moved
  from the main text; S10 was written in answer to review. It now says so.

## What the audit asked for that is done

- **AI disclosure moved into the methods** as §5.1, where PLOS asks for it; §9
  points to it. The scope is unchanged — the audit was explicit that it must
  not be narrowed — and the attestation bracket that closes it is still empty,
  because only the author can sign it.
- **The three IMF-derived aggregates** (`imf_frame_publication.{json,csv}`,
  `imf_cadence_balance.json`): the public mirror's include and deny lists
  disagreed about them and the build printed a note and went on. The lists now
  agree — they are off the mirror's include list — and a disagreement refuses
  the build. They travel in the evidence deposit as counts, and S10.5 and S10.7
  now say "reproduce from the evidence deposit" and why the mirror omits them.
  Whether the mirror may *also* carry them is the licence ruling the audit
  correctly says cannot be made by guessing; it is Ali's, against the written
  permission, and stays `needs_human_review`.

## What remains, and whose it is

All six of the audit's blocking items that are not the two above reduce to the
same four actions, none of which a tool may take:

1. Sign the attestation in §5.1 after the line-by-line review the audit
   describes; amend the paragraph above it wherever it over- or understates.
2. Cut the release; let Zenodo mint the version DOI; fill it in the manuscript,
   the checklist, the cover letter and the DAS. `check_submission_metadata.py`
   refuses until then and refuses if v1.2.0 is named anywhere as the archive.
3. Upload the evidence deposit (`build/zenodo_evidence_deposit.zip`, now
   verified against its list) or provide a private reviewer link; run
   `tools/record_evidence_doi.py`.
4. Affiliation, ORCID, corresponding email, funding, competing interests,
   CRediT; and the IMF licence ruling on the three aggregates.

Then rebuild everything from that one commit and run the guards on the files
that will actually be uploaded — which is the audit's closing instruction and
the discipline this round was short of.

Suite: 471 collected. Guards: `placeholder_report` red on the four author
brackets; `check_submission_metadata` red on the version DOI; cross-references,
stated counts, citation audit, kit freshness and the public mirror green.
