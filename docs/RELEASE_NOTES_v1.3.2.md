Analysis code, test suite and frozen design record behind the PLOS ONE submission of *Reconstructing Bankspeak*. This is the release the manuscript cites.

It supersedes v1.3.1, which carries the same results but whose test fixtures quoted real IMF document titles and IMF-published filenames; those fixtures are synthetic in this release, the compliance record withholds its probe filenames, and a test now refuses any shipped text that names an IMF document. Do not cite v1.2.0 or v1.3.0 for the reported results (their archives predate them).

Suite: 481 tests. The evidence deposit is a separate Zenodo record (repository alicetinkaya76/bankspeak-evidence-deposit). The IMF Article IV documents are not redistributed under the written permission and are listed by report number, DOI and SHA-256 in `data/meta/imf_document_index.csv`.
