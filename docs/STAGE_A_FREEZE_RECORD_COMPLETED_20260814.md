# STAGE-A FREEZE RECORD — COMPLETED (round-14 APPROVE)

**Status:** APPROVED FOR STAGE-A TIMESTAMP by the third-eye review on
2026-08-14 (approving ruling: ROUND14_THIRD_EYE_REVIEW.md). Prepared
OUTSIDE the approved package: the approved ZIP is NOT rebuilt or
modified. Timestamp this record together with the exact ZIP, the freeze
JSON (freeze_fields_r14.json) and the approving ruling.

**Frozen object** = PREREG_DRAFT_v0.5.md + PREREG_v0.6_AMENDMENTS
(C1–C12) + PREREG_v0.7_AMENDMENTS (C13–C19) + PREREG_v0.8_AMENDMENTS
(C20–C25) + PREREG_v0.9_AMENDMENTS (C26–C28) + PREREG_v0.10_AMENDMENTS
(C29–C32) + PREREG_v0.11_AMENDMENTS (C33–C35) + PREREG_v0.12_AMENDMENTS
(C36–C38) + round14_package_20260814.zip (the approved audit package).

**Frozen object identity**

| freeze field | value |
|---|---|
| zip_sha256 | `0ca03b605b5515151828613b65a06b8fd538b0c3ddb94db65504bd308e721114` |
| zip_bytes | `10654013` |
| zip_entry_count | `181` |
| sha256sums_entries | `180` |
| manifest_rows | `179` |
| sha256sums_sha256 | `6083c0ce7936cd56698d605b3ea715a194fb03d73f9057ccf25e618a00fafb90` |
| manifest_sha256 | `9229d9b9c00c892586886f2720ae5600f9168131946260b41f1ab640242b8245` |
| python_version | `3.11.9` |
| python_version_sha256 | `61141e9590171b900fdf709e7ea8f050d5c2a69198d4a4a1977d7c45186307e5` |
| requirements_sha256 | `770300e1fcfcc4ff39d491f23d4a50111eb6ce8dae44df89bd818f88640ed8c9` |
| requirements_ppl_sha256 | `01020da68a9be519ffba0acb4caf686cbb8081b6e8d2b5e2b92429b63368a04e` |
| requirements_lock_sha256 | `declared-absent (no lock file in the frozen object)` |
| git_commit | `20af74e71d7eedb0a23583d81982f816b645544f` |
| git_bundle_sha256 | `2ae58ff9096094c30cd447f1f47e4b19894ef01567b5a4a79aac75c2c2ed9179` |
| logs.tests | `55baf4976f6dec8b426527ef41210b80042373891b9fd7b956f116b424e8f640` |
| logs.selftest | `8651f8f36048d0b3124911e932eaec96eb41053b0b380b6637c5130f66d3da40` |
| logs.smoke | `872cb5335c8af58054cb680281805cc6386b4049c819ecd9fe7bd5c6a736cefa` |
| rulings.round2 | `fd4f9cddefef9bdda2f12906b98203ae822d0ebda6a2d88ad253fee68e87faf6` |
| rulings.round3 | `12f8237ae02377c79d7d125e869c076e7f7bdc9aa2ad15b990a4014c156a5092` |
| rulings.round4 | `faacb346d790d762b6e01be143573f3837c4d9472b9b46a4c3f189fc7e92f4c5` |
| rulings.round6 | `PENDING — declared: report text not yet exported; no ruling artifact exists` |
| rulings.round7 | `59ae722d92fb638020161536fd34c5d8f45e14924c74c53d243944ab7af9090b` |
| rulings.round8 | `a8f25fd3ce29517fe1bb2842ef5c68647473ead2bb80c894fa0a75787717eebc` |
| rulings.round9 | `8d8a5655624d2b0d02e0d990d80210f4efa86b80e9afe3dfa2bed841fbc17310` |
| rulings.round10 | `f586b4d3ff36bcd5ba33c0c798c73c7e760266baa07a2368615c4c2cf3c02af8` |
| rulings.round11 | `fd358adc3b7d13187d95c5f6a1dc0fcccb9067dbfdc236dff49cf8220935e6ff` |
| rulings.round12 | `039d2162a3b9a4b32e66c26fab593d303f4a1eac5273d148e86afad423b79970` |
| rulings.round13 | `0ee73a6ec7b2fbfc5b44e2f9c5bae9bcf1a5fe8743628daf4952b9f0335233c9` |
| rulings.approving | `0e0aadbfd5e2b9aac2292d8701c16804850b03882bc34f78d5cd4827f34e2b58  (ROUND14_THIRD_EYE_REVIEW.md — APPROVE)` |
| environment_sha256 | `77e3e3425bf9ab8f21288bc6ff444bced2f63965602f0f74d72462c15d679a41` |
| calibration_sha256 | `cf033e2fb8ab0bfbd496e9aa9516902c17bada13398166a19b78749db3150203` |
| built_utc | `2026-08-14T06:44:58+00:00` |
| osf_timestamp | `2026-08-16T04:21+00:00` |
| osf_registration_doi | `10.17605/OSF.IO/5C9J8` |

## Binding execution conditions carried into Stage-B

1. No analysis of real World Bank outcome data occurred before this
   timestamp; live IMF metadata access begins only after it (§11.1).
2. The production calibration returned `calibration_ok = false`
   (boot size 0.05 inside band; Wald–bootstrap concordance 0.91 below
   the preregistered 0.95). The Wald shortcut is therefore permanently
   unlicensed: production and Stage-B power/curve runs use full nested
   PASS-P.
3. Every Stage-B curve run passes
   `--calib-expected-sha256 cf033e2fb8ab0bfbd496e9aa9516902c17bada13398166a19b78749db3150203`
   and its log must carry the resulting
   `[mde] calibration artifact sha256 verified: <hash>` line.
4. Live acquisition runs only with `--i-am-in-stage-b`,
   `--docty-verified` and `--docty-probe-artifact`; raw archives are
   write-once and byte-verbatim, request logs append-only.
5. Round 6 remains a declared pending ruling artifact: the report text
   is to be exported and archived; its absence is recorded here, not
   silently omitted.

## Post-freeze maintenance backlog (non-blocking; NEVER rebuild the approved ZIP)

* freeze-record test docstring still references the older `_v*.md`
  glob wording; the code itself uses the correct wider glob.
* the C38 reproducer regression asserts the four verdict lines but does
  not additionally assert the script's exit code (the reviewer's own
  run exited 0).
Both are queued for the FIRST post-freeze package, not for this one.
