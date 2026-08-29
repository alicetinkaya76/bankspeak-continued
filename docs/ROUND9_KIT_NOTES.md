# Round-9 hazırlık kiti — sprint-4 (round-8 onarımları)

| Round-8 bloker | Durum | Kanıt |
|---|---|---|
| SPROLL 500/CAPTCHA/bakım = "son sayfa" | KAPALI — non-200/boş-ilk-sayfa/anchor'lı-sıfır-satır/max-pages hepsi RAISE | test_sproll_* (5) |
| WB "ham sayfa" verbatim değil | KAPALI — hook ham gövdeyi alır; yeniden serileştirme yasak; ham gövdesiz transport ABORT | verbatim assert, test_page_hook |
| total=N, eksik kayıt sessiz | KAPALI — tamlık sözleşmesi iki noktada RAISE | test_fetch_* |
| docty {} kabul | KAPALI — tam şema + probe_sha256 bağı | test_docty_schema_* |
| p1p2 MDE'de IMF girdisi etkisiz | KAPALI — tokens_imf/rate_imf simülasyona bağlı; defaults = eski çekilişler | test_imf_* (3) |
| crit_abs_z kararı yönetmiyor | KAPALI — kalibre singleton + kalibre Holm step-down; half yoksa REFUSE | test_calibrated_wald_crit_governs |
| Eksik şablon yılı sessiz dolgu | KAPALI — katı kapsama, RAISE | test_template_missing_year_raises |
| İç boş bin sahte katsayı | KAPALI — ileri-birleşme fixpoint + all-zero/rank guard'ları | test_make_bins_*, test_passe_multi_*_guard |
| Std tanıları eksik/maskeleme | KAPALI — evrensel tanı seti + failures[] + donmuş öncelik sırası | test_std_* (2) |
| Ortam kaydı yok | KAPALI — capture_env.py + packager doğrulaması + evidence/environment.json ZORUNLU | test_env_validation |
| Calibration kanıtı yok | KAPALI — evidence/calibration.json ZORUNLU + sanity | test_calibration_staged_* |
| git hatası = temiz | KAPALI — ABORT | test_git_status_failure_aborts |
| freeze+allow-dirty | KAPALI — karşılıklı dışlayıcı | (main guard) |
| null zorunlu alan = uyarı | KAPALI — ABORT (lock tek opsiyonel) | test_freeze_completeness_enforced |
| Freeze record nesne tanımı | KAPALI — v3: nesne = v0.5+v0.6+v0.7 amendments + onaylı zip | STAGE_A_FREEZE_RECORD_v3.md |
| Ruling zinciri | MEKANİZMA HAZIR — r2/r3/r4/r7/r8 pakete; r6 Ali export bekliyor | C19 |

Testler 93 → **116 passed** (ana + pinli çift koşu); selftest beş satır bit-bit;
smoke imzası korunmuş (calibrate çıktısına crit_abs_z_half alanı EKLENDİ —
karar yolu değişmedi, ncal=10'da half==full aynı order-statistic kuralıyla).
Packager CLI: --env ZORUNLU-with-freeze, --calibration ZORUNLU-with-freeze;
--freeze-fields artık --allow-dirty ile birlikte kullanılamaz.
