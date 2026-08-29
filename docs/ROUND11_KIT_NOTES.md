# ROUND-11 KIT NOTES (sprint-6)

| Round-10 blocker | Repair | Where |
|---|---|---|
| C20 SPROLL not write-once; `<a>` missed; duplicate ids | run-immutable dir + write-once pages + append-only log; semantic anchor regex; unique-id completeness | s09a, s01 (C26) |
| C21 Path NameError; endpoint-only years; tokens_per_doc unbound | pathlib import + tested file-template path; gap-aware --years + full vector in binding; tokens_per_doc in binding | mde_sim (C27) |
| C23 forged pilot opens Wald; NaN/Inf accepted; partial provenance | production-size + positive-finite licensing (+ optional sha pin); finite/typed packager v6 incl p2_start_year; 4-step run_evidence + calibration-run cross-bind + logs.smoke + round10 ruling | mde_sim, packager, run_evidence (C28) |

Suite: 157 passed (both stacks; 141 + 16 round-10 regressions); selftest
bit-identical; smoke numbers unchanged (binding.years now a full vector —
declared, C27.4).

## Ali'nin sırası (KISALDI — run_evidence artık kalibrasyonu da koşuyor)
```
unzip -o kit_sprint6_r11hazirlik_20260812.zip -d .
git add -A && git commit -m "sprint-6: round-10 repairs (157 tests)"
python -m pytest tests/ -q                          # 157 passed
python tools/run_evidence.py environment.json --sigma-delta 0.1
  # tek oturum: pytest.log + selftest.log + smoke.log + calibrate.log
  # + calibration_pinned.json  (calibrate adımı uzun: ~30-45 dk)
python tools/build_audit_package.py --out round11_package_$(date +%Y%m%d).zip \
  --freeze-fields freeze_fields_r11.json \
  --log tests=pytest.log --log selftest=selftest.log --log smoke=smoke.log \
  --env environment.json --calibration calibration_pinned.json \
  --ruling round2=docs/round2_external_review.md \
  --ruling round3=docs/ROUND3_THIRD_EYE_REVIEW.md \
  --ruling round4=docs/ROUND4_THIRD_EYE_REVIEW.md \
  --ruling round7=docs/ROUND7_THIRD_EYE_REVIEW.md \
  --ruling round8=docs/ROUND8_THIRD_EYE_REVIEW.md \
  --ruling round9=docs/ROUND9_THIRD_EYE_REVIEW.md \
  --ruling round10=docs/ROUND10_THIRD_EYE_REVIEW.md \
  --git-bundle
```
Not: run_evidence commit SONRASI koşar (binding.git_commit == HEAD ==
ff.git_commit zorunlu). ff_r11.json Claude kabul denetimine; GO sonrası
üçlü sevkiyat (v11 + zip + ff_r11).
