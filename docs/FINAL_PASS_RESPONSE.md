# Final pass before submission, 2026-09-03

The author asked for four things: remove every trace of machine-drafted prose,
em dashes first; double-check the references and the in-text citations; check
the package against the target journal's format; and close the items that had
been left as his. This records what was done, what was verified, and the two
things that remain and why.

## Prose

Twelve section-sized rewrites, one agent each, under a rule set that allowed
only mechanical changes: every em dash resolved with a comma, a full stop, a
colon or parentheses; every semicolon joining two clauses split into two
sentences, semicolons kept only inside citation groups, table rows and code;
listed filler phrases removed. Numbers, table rows, headings, code spans,
en dashes in ranges, minus signs and every sentence the test suite pins were
declared untouchable. A reassembly script then checked the four documents as
wholes and refused until they passed.

| document | em dashes | clause semicolons | words |
|---|---:|---:|---:|
| manuscript | 202 to 0 in prose (18 remain as table cell markers) | 109 to 0 | abstract 296 |
| supplement | 79 to 0 (2 in code) | 43 to 0 | |
| cover letter | 6 to 0 | 4 to 0 | 542 |
| data availability | 9 to 0 | 7 to 0 | |

Three guards keyed on an em dash and would have gone quiet: the figure and
table definitions in the cross-reference check and the figure count in the
stated-counts check. They were moved to the new forms before the rewrite ran.

## References and citations

Every DOI re-resolved live against Crossref on 2026-09-03: 31 of 35 resolve,
the four without a DOI (three proceedings papers and the Literary Lab pamphlet)
return HTTP 200 at their stable URLs, and the one "drift" is the known
print-versus-online year on Lopez Bernal (2017). No entry is uncited; no
in-text citation lacks an entry; a separate pass found zero in-text years that
disagree with the entry's year. The reference block is now bounded at the next
heading, because the new supporting-information caption after it was being
parsed as a 36th entry.

## Format, against the live PLOS ONE guidelines

Done: title under 250 characters; abstract under 300 words; opening and
closing section order (title page, abstract, introduction; acknowledgments,
references, supporting-information caption); AI disclosure as a dedicated
methods subsection (5.1) naming the tool, its use and how outputs were
verified, with the author's attestation; line numbers and double spacing in
the manuscript file (the front block with the analysis-plan hash exempted,
because the wrapped hash was absorbing a line-number digit in the text layer);
figures as separate 300-dpi TIFF files with "Fig N." captions placed after
first citation; one supporting-information file captioned S1 Text; funding,
competing interests, CRediT, ethics and the short title prepared for the
submission form in `docs/SUBMISSION_FORM_FIELDS.md`, which PLOS wants outside
the manuscript.

Deferred to acceptance, deliberately: numbered Vancouver references in the
text. The list is generated (`docs/REFERENCES_vancouver.md`, 35 entries in
first-appearance order); converting about eighty in-text citations is a
mechanical job with one judgement in it, since Moretti and Pestre (2015) now
resolves to two publication objects, and PLOS applies formatting at that
stage.

## The items that were the author's

- Attestation in 5.1: written as his statement at his instruction, affirming
  what the record supports: the question, design, hypotheses and the decision
  to report a null are his; the assistant's methodological choices were made
  under his standing instruction and adopted by him across twenty-one review
  rounds he commissioned and acted on.
- Affiliation and email: filled from his own materials.
- ORCID: 0000-0002-7747-6854, supplied by the author after the registry lookup had
  returned three Selçuk-affiliated candidates; the email is the institutional
  one, ali.cetinkaya@selcuk.edu.tr.
- Funding and competing interests: declarations of none, prepared for the
  form; they are statements in his name that he confirms by submitting.
- D-14, the three IMF-derived aggregates: ruled redistributable as derived
  outputs under the permission, then corrected the same day when the public
  mirror's content scan found 78 report numbers of unselected documents in the
  frame file. Those ids disclosed nothing the evidence deposit does not (the
  deposit carries the eligible frame's identifiers so the draw can be
  replayed), but they broke the mirror's own rule, so the tool withholds them;
  the file, the deposit and the mirror were rebuilt.

## The release, and what remains

**The version DOI is filled: `10.5281/zenodo.22272212`, v1.3.1.** The first
attempt at the release was blocked by the harness as an outward-facing
publish; on the author's renewed instruction it was cut, and it was cut twice.
A v1.3.0 release already existed by then, created at 06:53 UTC with its tag at
the round-19 commit `0d3ba98` rather than at the head of `main`, so its Zenodo
archive (`10.5281/zenodo.22271589`) predates everything from round 20 on, which
is the defect the audit had raised about v1.2.0. A Zenodo record cannot be
withdrawn, so v1.3.0 is named beside v1.2.0 in the manuscript, the checklist
and the public README as an archive not to be cited for these results, and
v1.3.1 was cut from `2406e4b`, the head of `main`, with the ORCID and
affiliation in its metadata. `tools/fill_version_doi.py` verified the DOI
against the record (version v1.3.1 of the concept DOI) before writing it into
the manuscript, the cover letter and the data-availability statement; it
refused the v1.3.0 DOI in a check run first. The evidence deposit's metadata
declares itself a supplement to v1.3.1.

**One thing remains, and it is the author's by construction.** The evidence
deposit (`build/zenodo_evidence_deposit.zip`, 831 files, verified against its
list, identifier-free) needs a Zenodo token with `deposit:write` to upload;
`.env` holds a placeholder, and the uploader's own text says the token is not
its to create. Upload by hand at zenodo.org, or put the token in `.env` and run
`python tools/upload_evidence_deposit.py --publish`; then
`python tools/record_evidence_doi.py <DOI>`, rebuild the PDFs, and the last
bracket in the data-availability statement is gone.

Suite: 479. Guards: placeholder report clean on the manuscript and the built
PDF, metadata, counts and cross-references all green.
