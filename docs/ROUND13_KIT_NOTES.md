# ROUND-13 KIT NOTES (sprint-8)

| Round-12 blocker | Repair | Where |
|---|---|---|
| C29/C31 gates only on the ok=true branch — real ok=false artifact consumed unverified | provenance gate BEFORE calibration_ok: read-once bytes, mandatory+matching hash, strict parse, schema+sizes+binding, unconditional verified-hash log line, SystemExit on any failure | mde_sim (C33) |
| raw-value uniqueness vs stringified emptiness — 1/"1" and "1"/" 1 " collide | canonical STRING id contract (typed, trimmed==raw, unique) | s01 (C34) |
| 12/16 old-commit flips; NaN fixture vacuous; log bytes=chars | docstring-marked preservation arms; NaN on a fully valid artifact ("strict JSON" attribution); transport-forgery flip; len(raw_bytes) column | tests, s09a (C35) |

Suite: 182 passed (both stacks; 173 + 9 round-12); selftest bit-identical;
smoke numbers AND shape unchanged. Freeze record v3.3 (round12 row).

## Ali'nin sırası
```
unzip -o ~/Downloads/kit_sprint8_r13hazirlik_20260813.zip -d .
git rm docs/STAGE_A_FREEZE_RECORD_v3.2.md
git add -A && git commit -m "sprint-8: round-12 repairs (182 tests)"
python -m pytest tests/ -q                          # 182 passed
python tools/run_evidence.py environment.json --sigma-delta 0.1
python tools/build_audit_package.py --out round13_package_$(date +%Y%m%d).zip \
  --freeze-fields freeze_fields_r13.json \
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
  --ruling round12=docs/ROUND12_THIRD_EYE_REVIEW.md \
  --git-bundle
```
run_evidence commit SONRASI. ff_r13.json Claude kabul denetimine; GO
sonrası üçlü sevkiyat (v13 + zip + ff_r13).
