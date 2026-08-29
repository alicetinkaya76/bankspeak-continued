# SAP FREEZE RECORD — 2026-08-25

The Stage-B SAP is **frozen and externally timestamped**. This record is the
§S12 companion: the deposited file itself is left byte-identical to the deposit
— filling §S12's block inside it would change the hash it was deposited under —
so the freeze evidence lives here, in the repository, next to the file.

```
Frozen document ......  docs/SAP_FINAL_DRAFT_20260820.md
SHA-256 ..............  4aa122797f2db6ddd3e1dae5cb425958b231f02438f242bde174b25b20af2677
MD5 (deposit) ........  c515e7e7521c69dbfdaccb9e8608cb74
DOI (version) ........  10.5281/zenodo.22098259
DOI (concept) ........  10.5281/zenodo.22098258
Published ............  2026-08-25T15:01:07Z (Zenodo)
Operator .............  Ali Çetinkaya (deposit made from his Zenodo account)
Rulings confirmed ....  D-1..D-10 (operator delegated; deposit constitutes the
                        confirmation §S10 asked for — the deposited file lists
                        all ten)
```

Verification performed before anything downstream ran, all three independent:
the local file's SHA-256 equals the value above; the git-committed copy's
SHA-256 equals it too; and Zenodo's own file checksum
(`md5:c515e7e7521c69dbfdaccb9e8608cb74`, 11,947 bytes) equals the local MD5 —
the deposited bytes are the frozen bytes.

## Acts performed at the freeze boundary, before the pipeline

1. **D-9 implemented.** The two broken-CMap documents' PDFs were fetched from
   their `pdfurl` and both re-checked: PyMuPDF still yields mojibake
   (29809040) / a stub text layer (8514715), confirming OCR as the only route.
   Their defective extracts were deleted for regeneration and
   `data/meta/ocr_overrides.csv` pins them to the OCR path across inventory
   rescans. Two near-empty Stage-A scan extracts (2017572, 33464456) were
   likewise deleted so OCR can fill them.
2. **The v1-index gap closed** (`tools/build_stageb_runtime.py`). `s02`/`s04`/
   `s10`/`s12` index on `frozen_sampling_v{version}.csv`; at v1 that is the
   sealed Stage-A sample, which would have silently dropped all 1,064 IMF
   documents and most of the Stage-B redraw — and the Stage-B WB texts were
   never downloaded (748 of 2,738 overlap the sealed sample). Built:
   `frozen_sampling_v2.csv` (3,802 rows, write-once, a plumbing union over the
   unchanged frozen samples), `config/config.stageb.yaml` (sampling_version 2;
   main config untouched), 1,064 IMF manifest rows (append-only, carrying the
   retrieval's own sha256s, so `s02` cannot re-download from imf.org at the WB
   cadence and breach the 1 req/s condition), and the D-8 exclusion ledger.
3. **The driver rebuilt to the full Stage-B order** (16 stages):
   s02 → ocr scan/calibrate/run → s03 → D-7 refetch → quality scan →
   **quality gate** (stops on any unruled hard flag, per D-10) → s10 →
   s04/s05/s05b → s07/s08/s12/s13. `s06`/NLL stays out (§7.4, D-4).

Every downstream act logs the DOI and SHA-256 above into
`data/meta/post_sap_run_log.jsonl` (the driver requires them as arguments — the
gate is the evidence).
