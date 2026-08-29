# ROUND-12 KIT NOTES (sprint-7)

| Round-11 blocker | Repair | Where |
|---|---|---|
| C28a hash optional → forged production artifact licensed Wald | external calibration REQUIRES --calib-expected-sha256 (fail-closed) + verified-hash provenance line + schema gate | mde_sim (C29) |
| C26 four acquisition gaps | structural HTMLParser anchors; canonical non-empty ids; in-retry attempt archiving (write-once, logged); SPROLL verbatim bytes + strict-UTF-8 parse | s09a, s01, utils, s09b (C30) |
| C28b non-recursive validator | shared src/calib_schema.py (strict ints, finite numbers, exact key sets, enums, template shapes, unknown-field rejection, NaN/Inf parse rejection) used by runtime AND packager | calib_schema, mde_sim, packager (C31) |
| C24 record template behind schema | STAGE_A_FREEZE_RECORD_v3.2 (v0.9+v0.10 normative; logs.smoke, rulings.round10/11 rows); v3.1 removed | docs (C32) |

Suite: 173 passed (both stacks; 157 + 16 round-11 regressions); selftest
bit-identical; smoke numbers AND shape unchanged this sprint.

## Ali'nin sırası
```
unzip -o ~/Downloads/kit_sprint7_r12hazirlik_20260813.zip -d .
git rm docs/STAGE_A_FREEZE_RECORD_v3.1.md
git add -A && git commit -m "sprint-7: round-11 repairs (173 tests)"
python -m pytest tests/ -q                          # 173 passed
python tools/run_evidence.py environment.json --sigma-delta 0.1
python tools/build_audit_package.py --out round12_package_$(date +%Y%m%d).zip \
  --freeze-fields freeze_fields_r12.json \
  --log tests=pytest.log --log selftest=selftest.log --log smoke=smoke.log \
  --env environment.json --calibration calibration_pinned.json \
  --ruling round2=docs/round2_external_review.md \
  --ruling round3=docs/ROUND3_THIRD_EYE_REVIEW.md \
  --ruling round4=docs/ROUND4_THIRD_EYE_REVIEW.md \
  --ruling round7=docs/ROUND7_THIRD_EYE_REVIEW.md \
  --ruling round8=docs/ROUND8_THIRD_EYE_REVIEW.md \
  --ruling round9=docs/ROUND9_THIRD_EYE_REVIEW.md \
  --ruling round10=docs/ROUND10_THIRD_EYE_REVIEW.md \
  --ruling round11=docs/ROUND11_THIRD_EYE_REVIEW.md \
  --git-bundle
```
run_evidence commit SONRASI (binding.git_commit == HEAD == ff.git_commit).
ff_r12.json Claude kabul denetimine; GO sonrası üçlü sevkiyat (v12 + zip
+ ff_r12).
