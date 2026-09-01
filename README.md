# Bankspeak, Continued — analysis code and design record

Code, tests, and the complete frozen design record for *Reconstructing Bankspeak: Eight
Decades of World Bank Language, a Corpus-Selection Effect, and an Unconfirmed
Post-2022 Break* — an
independent reconstruction of Moretti and Pestre's *Bankspeak* (2015) from
primary World Bank documents, extended to fiscal 2024, plus a preregistered test
of whether post-2022 LLM-associated vocabulary shows a World Bank discontinuity
relative to an IMF Article IV comparator.

The confirmatory result is **negative**: no panel satisfies the preregistered
decision rule. This repository exists so that conclusion can be checked rather
than trusted.

## Preregistration

| | |
|---|---|
| Stage-A preregistration | [`10.17605/OSF.IO/5C9J8`](https://doi.org/10.17605/OSF.IO/5C9J8) |
| Stage-B statistical analysis plan | [`10.5281/zenodo.22098259`](https://doi.org/10.5281/zenodo.22098259) |
| SAP SHA-256 | `4aa122797f2db6ddd3e1dae5cb425958b231f02438f242bde174b25b20af2677` |
| SAP timestamped | 2026-08-25T15:01:07Z, **before any outcome reported in the paper was computed** |

## What is here

```
src/      the analysis pipeline and the frozen inference engine
tools/    retrieval, corpus repair, table and figure generators, sensitivity studies
tests/    the suite that pins the frozen contracts (386 tests; 19 need
          permission-gated or deposited inputs and skip here, naming the file)
config/   pinned configuration, marker family definitions, alias maps
docs/     preregistration drafts and amendments, the frozen SAP and its freeze
          record, decisions D-1..D-13, deviation records, third-eye review
          rounds, generated tables and figures, and the manuscript draft
```

`docs/DECISIONS_20260820_stageb_close.md` and the two `DEVIATION_*` files are the
ones to read if you want to know what was decided, when, and on what basis —
including the decisions that went against the study's own interest.

## What is not here, and why

**The access route IS here.** `data/meta/imf_document_index.csv` lists all 1,064
IMF documents by report number, year, country, DOI and SHA-256. The IMF publishes
these reports itself, so a reader resolves each DOI, downloads from the
publisher, and hashes their copy to confirm byte identity with the one analysed —
without going through the author. The index carries no title and no IMF URL.

**No corpus, and no IMF bibliographic data.** The 1,064 IMF Article IV staff
reports are used under a written permission that forbids redistributing documents
or extracted text. The permission does allow derived non-substitutive outputs,
including SHA-256 hashes and counts — but the frame that carries every document
title and URL is verbatim IMF content, and it is not published here.

**No World Bank raw archives.** These are public and re-derivable, but they are
46 MB of API pages and belong in the evidence deposit rather than in git.

Both live in the Zenodo evidence deposit, whose manifest lists every IMF-derived
file by SHA-256 so that a researcher who lawfully obtains the same documents can
verify byte identity before rerunning anything. `tools/prepare_zenodo_deposit.py`
builds it. The split is deliberate and long-standing in this project: **git
carries the decision, Zenodo carries the evidence.**

`tools/build_public_repo.py` produced this repository and refuses to build if a
staged file exceeds a density threshold for IMF report numbers, DOIs, URLs or
document titles. Naming a document is citation; shipping the frame is
redistribution, and the tool enforces the difference rather than trusting it.

## Reproducing

The pipeline cannot be rerun end-to-end without the restricted corpus. What can
be checked from this repository alone:

```bash
pip install -r requirements.txt
python -m pytest tests/ -q                 # 346 pass, 11 skip without the
                                           # permission-gated inputs
python tools/plos_compliance.py            # manuscript against the venue's stated limits
python tools/make_vancouver_refs.py        # numbered reference list, built from Crossref
python tools/build_submission_pdf.py       # the single submission PDF, glyph-checked
```

`make_vancouver_refs.py` is the only one of those that reaches the network. It
resolves each reference DOI and refuses to invent an entry it cannot resolve.

With the Zenodo deposit unpacked into `data/`:

```bash
python tools/make_paper_tables.py          # regenerates Tables 1-7
python tools/make_paper_figures.py         # regenerates Figures 1-3
python tools/prereg_sensitivities.py       # PREREG §4 secondary sensitivities
python tools/rq1_decomposition.py          # the RQ1 corpus-construction decomposition
python tools/passp_calibration.py 800      # PASS-P size under the null
python tools/probe_imf_access.py 12        # records the live IMF access routes
```

Every number in the manuscript regenerates from these. If a table and the code
disagree, the table is wrong.

## Design notes worth knowing before reading the code

- **`src/bootstrap_engine.py`** holds the frozen design matrix. The model is
  `year FE + WB + WB×centred_year + WB×post` with a token offset. This is a
  single-comparator comparative interrupted time series, not a
  difference-in-differences design, and the code is the authority on that.
- **PASS-P** resamples signs over nine three-year blocks, so its support is
  exactly 2⁹ = 512 patterns. `tools/passp_calibration.py` shows it holds nominal
  size at 0.05, and that its null p-value distribution is not uniform.
- **Seeds are fixed** (`seed=42`) and every stage is deterministic.

## Licence

**Code** (`src/`, `tools/`, `tests/`, `config/`) — MIT, see [`LICENSE`](LICENSE).
**Documentation** (`docs/`) — CC BY 4.0, see [`LICENSE-docs`](LICENSE-docs).

Neither licence extends to World Bank or IMF material, none of which is in this
repository. The IMF corpus is held under a permission forbidding redistribution;
World Bank content is public disclosure under its Access to Information Policy.

## Citation

This repository is archived with a DOI:

> Çetinkaya, A. (2026). *Bankspeak, Continued — analysis code and frozen design
> record*. Zenodo. https://doi.org/10.5281/zenodo.22152944

That is the **concept DOI**: it always resolves to the latest version, so it
cannot go stale the way a version DOI in a file inside that same version does.
The current release is v1.2.0 (`10.5281/zenodo.22168611`).

**Do not cite v1.0.0 or v1.1.0.** Neither archive can run its own test suite:
`pytest tests/ -q` in either dies with twelve collection errors and runs zero
tests, because the export filter stripped two of this project's own source
modules. v1.2.0 is the first release that runs. `CITATION.cff` carries machine-readable metadata. Until the paper is
published, cite the preregistration DOIs above alongside it.
