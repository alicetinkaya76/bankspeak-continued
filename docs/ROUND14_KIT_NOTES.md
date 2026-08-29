# ROUND-14 KIT NOTES (sprint-9)

| Round-13 blocker | Repair | Where |
|---|---|---|
| versionless fossil template + v0.11 outside the normative chain | fossil removed; single-template rule covers ALL names; record v3.4 (v0.11+v0.12 normative, literal round13 row) | docs, test_round11 (C36) |
| 12/4 matrix and docstring claims false | headers rewritten to 13/3 (r11) and 7/2 (r12) with named, docstring-marked preservation arms and per-arm reference commits | tests (C37) |
| archived reproducer dies on first correct ABORT | auditor-based portable script (subshell exits, split streams, unconditional verdicts, macOS sha shim) + verdict regression | docs, test_round13 (C38) |

Suite: 183 passed (both stacks; 182 + 1 reproducer regression);
selftest bit-identical; smoke numbers AND shape unchanged.

## Ali'nin sırası
```
# 0) Hakem dönüş raporunu repoya koyun (ruling zinciri round13 için):
#    ROUND13_THIRD_EYE_REVIEW.md -> docs/ROUND13_THIRD_EYE_REVIEW.md
unzip -o ~/Downloads/kit_sprint9_r14hazirlik_20260813.zip -d .
git rm docs/STAGE_A_FREEZE_RECORD.md docs/STAGE_A_FREEZE_RECORD_v3.3.md
git add -A && git commit -m "sprint-9: round-13 repairs (183 tests)"
python -m pytest tests/ -q                          # 183 passed
python tools/run_evidence.py environment.json --sigma-delta 0.1
python tools/build_audit_package.py --out round14_package_$(date +%Y%m%d).zip \
  --freeze-fields freeze_fields_r14.json \
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
  --ruling round13=docs/ROUND13_THIRD_EYE_REVIEW.md \
  --git-bundle
```
ff_r14.json + docs/ROUND13_THIRD_EYE_REVIEW.md dosyalarini birlikte
Claude kabul denetimine yükleyin (round13 ruling sha recompute için).
