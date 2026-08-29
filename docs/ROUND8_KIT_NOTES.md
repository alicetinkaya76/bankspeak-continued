# Round-8 hazırlık kiti — sprint-3 (round-7 onarımları)

| Round-7 bloker | Durum | Kanıt |
|---|---|---|
| s09a canlı katman yok; bayrak etkisiz | KAPALI — SPROLL sayfalı canlı yakalama + ham HTML + istek/sayfa logu; bayrak operasyonel | test_fetch_live_sproll_*, test_parse_sproll_* |
| s09b ham sayfa arşivlemiyor | KAPALI — s01 page_hook + sayfa-düzeyi ham JSON + request_log | test_page_hook_archives_every_raw_page |
| FSSA co-titled çelişkisi | METİN UZLAŞISI (C10) — dahil+bayrak+duyarlılık; standalone hariç; hükme sunuldu | test_fssa_* |
| Trinidad and Tobago | KAPALI — alias-önce çözüm + T&T-sınıfı seed'ler | test_tto_*, test_true_multi_* |
| G1 16/16 pass | KAPALI — tam-20 kuralı + draw reddi | test_g1_* |
| G3 yok | KAPALI — s14.g3_support (icra okuması C2'de ilan) | test_g3_support_reading |
| G1–G4 orkestrasyonu yok | KAPALI — s14_branch_decision, tek-yön, write-once | test_s14 (5 senaryo) |
| MDE dal-spesifik değil; P0 singleton yok | KAPALI — per-panel şablon/oran, docs×tpd, --family p0 (α=0.05) | test_mde_sim.py; smoke rakam-rakam aynı |
| Gerçek ≥0.80 token-desteği yok; sıfır-π sessiz | KAPALI — iki ayrı kapı + paylar + zero_coverage_post_cell | test_std_* |
| make_bins takvim/StopIteration | KAPALI — gözlenen-yıl birleşme + alt-medyan referans | test_make_bins_* |
| Event-study PASS-E makinesi eksik | KAPALI — passe_multi (ofset 600000), selftest bit-bit korunarak | test_event_study_*, test_passe_multi_* |
| allclose tamsayı | KAPALI — tam eşitlik | test_integer_contract_* |
| NB2 fallback fail-closed değil | KAPALI — her silme fit'i denetimli; jackknife_failed durumu | test_*_jackknife_* |
| Boş+p0_failed=False | KAPALI — geçersiz-durum raise | test_family_* |
| Kanıtlar zip içinden doğrulanamıyor | KAPALI — packager v3: evidence/ kopyaları, rulings haritası, git bundle, fail-closed, temiz-ağaç | test_packager v3 testleri |
| docty Stage-B mekanizması yok | KAPALI — --docty-verified zorunlu; config dokunulmaz | test_docty_verification_* |

Test: 50 → **93 passed** (ana stack + pinli venv çifti); selftest beş satır iki
stack'te bit-bit; smoke imzası değişmedi (satır sonuna `family=p1p2` etiketi
eklendi). Packager CLI DEĞİŞTİ: `--ruling` artık `NAME=PATH` ve tekrarlanabilir;
`--git-bundle`, `--allow-dirty` yeni; freeze alanları `zip_entry_count`/
`sha256sums_entries`/`manifest_rows`/`rulings`/`git_bundle_sha256`.
