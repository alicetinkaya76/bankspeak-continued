# ROUND-10 KIT NOTES (sprint-5)

| Round-9 blocker | Repair | Where |
|---|---|---|
| C13 acquisition fail-open | bytes-verbatim pre-parse hook; schema minimum; first-total drift; write-once archives; positive-terminal markers; docty probe recompute | s01, s09b, s09a (C20) |
| C14 calibration unbound | family-pooled null (P2 offset +150000+i); binding block; curve-side binding enforcement; single truthful banner; exact-grid positive templates | mde_sim (C21) |
| C15 status=ok on failure | governing/method/B_valid propagation + failure_reasons | s13 (C22) |
| C17/C18 freeze evidence | strict-typed production calibration (ncal=200, B=9999) + binding+commit equality; runs[] provenance + log cross-check; REQUIRED_RULINGS incl round9; bundle mandatory; record v3.1 full placeholders | packager v5, run_evidence.py (C23/C24) |

Suite: 141 passed (both stacks); selftest bit-identical; smoke calibrate
block changed BY DESIGN (C25), curve decision + MDE80 = 0.9 unchanged.

## Ali'nin sırası (SIRA DEĞİŞTİ — commit ÖNCE, kanıt SONRA)
```
unzip -o kit_sprint5b_r10hazirlik_20260811.zip -d .
cat .gitignore.additions >> .gitignore
git add -A && git commit -m "sprint-5: round-9 repairs (141 tests)"
python -m pytest tests/ -q                        # 141 passed
python src/bootstrap_engine.py --selftest         # 5 satır birebir
make smoke                                        # calibrate bloğu YENİ (C25); MDE80=0.9 aynı
python tools/run_evidence.py environment.json     # pytest.log+selftest.log+env tek komut
python src/mde_sim.py --mode calibrate --sigma-delta <SS8-değeri> \
  --ncal 200 --B 9999 --out calibration_pinned.json   # ÜRETİM (uzun: ~1-1.5 sa)
python tools/build_audit_package.py --out round10_package_$(date +%Y%m%d).zip \
  --freeze-fields freeze_fields_r10.json \
  --log tests=pytest.log --log selftest=selftest.log \
  --env environment.json --calibration calibration_pinned.json \
  --ruling round2=<...> round3=<...> round4=<...> round7=<...> round8=<...> \
  --ruling round9=docs/ROUND9_THIRD_EYE_REVIEW.md --git-bundle
```
Not: calibrate commit SONRASI koşar → binding.git_commit == HEAD ==
ff.git_commit (packager bunu ZORLUYOR; evidence çıktıları .gitignore'lu
olduğundan ağaç temiz kalır). ff_r10.json Claude kabul denetimine gelir;
GO sonrası üçlü sevkiyat: v10 prompt + zip + ff_r10.
