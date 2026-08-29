# Round-13 Third-Eye Review

**Project:** *Bankspeak, Continued*  
**Package:** `round13_package_20260813.zip`  
**Freeze fields:** `freeze_fields_r13.json`  
**Review prompt:** `THIRD_EYE_REVIEW_PROMPT_v13.md`  
**Reviewed commit:** `d9ddef5bd48252c30be9f4c3b81ee975e4a43d37`  
**Review date:** 14 Ağustos 2026  
**Mandate:** Adversarial recomputation and a binary Stage-A ruling.

# Binary ruling

## **REJECT WITH REQUIRED CHANGES**

V13 talimatı yalnız iki hükme izin veriyor ve bütün sonuçların yeniden hesaplanmasını istiyor.

Round-12’deki iki maddi yöntem blokeri kapanmıştır:

- **C33:** Haricî kalibrasyon provenans kapısı artık `calibration_ok` değerlendirilmeden önce çalışıyor.
- **C34:** `1`/`"1"` ve `"1"`/`" 1 "` kimlik karşı-örnekleri fail-closed reddediliyor.
- Mevcut test koleksiyonu tam geçiyor.
- Selftest ve smoke imzaları korunuyor.

Bununla birlikte paket Stage-A zaman damgasına hazır değildir. Üç bağımsız ve yeniden üretilebilir bloker vardır:

1. **C32’nin “pakette yalnız bir freeze-record template var” beyanı yanlış.** İki ayrı template gönderilmiş ve singleton testi bunlardan birini göremiyor. V3.3 ayrıca güncel `PREREG_v0.11_AMENDMENTS.md` dosyasını frozen prereg zincirine açıkça almıyor.
2. **C35 test sınıflandırması yanlış.** Güncel Round-11 test dosyasının `10266ba` üzerindeki sonucu 12/4 değil, **13 failed / 3 passed**. “Geçen kollar docstring ile işaretlidir” beyanı da doğru değil.
3. **Paketlenmiş `docs/reproduce_round12_blockers.sh` çalışamaz durumda.** Onarılmış C33 davranışının ürettiği ilk beklenen nonzero çıkışta `set -e` nedeniyle kesiliyor; hiçbir `NOT REPRODUCED` veya `REJECTED` sonucu basmıyor.

Bu kusurlar kozmetik değildir. İrreversible timestamp’e girecek nesnenin kimliğini, test kanıtlarının doğru sınıflandırılmasını ve paketin arşivlenmiş adversarial yeniden üretim kanıtını doğrudan etkiler.

---

# 1. Integrity gate

Dış freeze kaydı ZIP için `501d893e…e1c8c9e`, `10,607,383` bayt, 175 ZIP girdisi, 174 checksum girdisi ve 173 manifest satırı beyan ediyor.

| Kontrol | Sonuç | Yeniden hesaplanan değer |
|---|---:|---|
| ZIP SHA-256 | **PASS** | `501d893e2179ff3f4347946bed330f20fd2fdb9c1de93fe15f1e15532e1c8c9e` |
| ZIP boyutu | **PASS** | `10,607,383` bayt |
| ZIP giriş sayısı | **PASS** | `175` |
| Yinelenen ZIP yolu | **PASS** | Yok |
| CRC testi | **PASS** | Bozuk üye yok |
| Sembolik bağ | **PASS** | Yok |
| Mutlak/yukarı taşan yol | **PASS** | Yok |
| `SHA256SUMS` | **PASS** | 174/174 doğrulandı |
| `MANIFEST.tsv` | **PASS** | 173/173 yol, bayt ve SHA doğru |
| Git bundle | **PASS** | Tam geçmiş; `HEAD/main = d9ddef5…` |
| Paket–Git bayt eşliği | **PASS** | Pakete giren izlenen dosyalarda fark yok |
| V13 talimat eşliği | **PASS** | Dış ve paket içi prompt bayt-birebir aynı |
| Ruling zinciri | **PASS** | Round 2, 3, 4, 7, 8, 9, 10, 11 ve 12 mevcut |
| Environment SHA-256 | **PASS** | `f936c765…5accfba3d` |
| Calibration SHA-256 | **PASS** | `518e0d59…89d1dc3` |

Freeze kaydındaki Python sürümü, test/selftest/smoke log hashleri ve Git commit alanları paketle eşleşiyor. Dokuz ruling, bundle, environment ve calibration hashleri de doğrulandı.

## 1.1 Git bundle

Bundle eksiksizdir:

```text
d9ddef5bd48252c30be9f4c3b81ee975e4a43d37 refs/heads/main
d9ddef5bd48252c30be9f4c3b81ee975e4a43d37 HEAD
```

Pakette bulunan 142 izlenen dosyanın hiçbirinde Git nesnesine göre bayt farkı yoktur. Sekiz repository-only dosyanın paket dışında bırakılması mevcut paketleme sözleşmesiyle uyumludur.

## 1.2 Evidence provenance

Staged calibration:

```text
sha256          = 518e0d59ed385ae19ae113dc9534dc960adc6f7dc267905202477c49289d1dc3
ncal            = 200
B               = 9999
calibration_ok  = false
years           = 1994–2025, 32 yıl
binding.commit  = d9ddef5bd48252c30be9f4c3b81ee975e4a43d37
schema errors   = []
```

Environment kaydı dört sıralı zero-exit koşu içeriyor:

1. pytest
2. selftest
3. smoke
4. production calibration

Paketlenmiş pytest, selftest ve smoke loglarının hashleri ilgili zero-exit koşularla birebir eşleşiyor. Calibration artefaktının hash’i de calibration koşusunun `artifact_sha256` alanına bağlıdır. V13’ün evidence provenansı için istediği staged calibration şeması, paket commit bağlaması ve Stage-B hash sözleşmesi bu bölümde doğrulanmıştır.

---

# 2. Independent execution

V13, pinli ortamda 182 test, beş satırlık bit-identical selftest ve değişmemiş smoke sayı/şekli bekliyor.

## 2.1 Test suite

Paketlenmiş pinli kanıt:

```text
Python 3.11.9
182 passed, 1 warning in 45.42s
```

Bağımsız ortamda Python 3.13.5 kullanıldı. Tek prosesli tam-suite çağrısı bu konteynerde güvenilir biçimde sonlanmadığı için testler izole modül gruplarında çalıştırıldı:

| Grup | Sonuç |
|---|---:|
| Temel test modülleri | 52 passed |
| Round-7/8/9 modülleri | 73 passed, 1 warning |
| Round-10 + s14/sampler/standardize/WB frame | 32 passed |
| Round-11 | 16 passed |
| Round-12 | 9 passed |
| **Toplam** | **182 passed, 0 failed** |

Dolayısıyla bütün test fonksiyonlarının mevcut commit üzerinde geçtiği bağımsız olarak doğrulanmıştır. Ancak pinli Python 3.11.9 tek-komut sonucu, bağımsız ortam tekrarı değil, paket içindeki hash-bound kanıttır.

## 2.2 Selftest

Bağımsız selftest çıktısı paket kaydıyla **604 bayt boyunca birebir aynıdır**:

```text
[selftest null-large] beta=-0.137 p=0.117 ci=[-0.3, 0.011] beta_in_ci=True floored=0.0000 alpha=0.000 governing=ci_percentile
[selftest effect-large] beta=+0.765 p=0.003 ci=[0.623, 0.898] beta_in_ci=True floored=0.0000 alpha=0.000 governing=ci_percentile
[selftest null-small] beta=+1.104 p=0.193 ci=[0.157, 2.02] beta_in_ci=True floored=0.0316 alpha=0.000 governing=ci_percentile
[selftest nb2-overdispersed] beta=-0.310 p=0.257 ci=[-0.922, 0.259] beta_in_ci=True floored=0.0000 alpha=0.035 governing=ci_percentile
[selftest duplicate-rejection] OK (duplicate institution-year cells: [('WB', 1994)]...)
```

## 2.3 Smoke

| Ölçüm | Paket | Bağımsız |
|---|---:|---:|
| `crit_abs_z` | `5.820810382338911` | `5.820810382338811` |
| Mutlak fark |  | `9.9476 × 10⁻14` |
| Bağıl fark |  | `1.70897 × 10⁻14` |
| Motor | `full_nested_pass_p` | `full_nested_pass_p` |
| Theta satırları | `0.0`, `0.9` | Aynı |
| Güç sütunları | p1, p2, family | Aynı |
| `MDE80` | `0.9` | `0.9` |

Bağıl fark, izin verilen `1e-12` bandının çok altındadır.

---

# 3. Round-12 blokerlerinin flip doğrulaması

V13, gerçek `calibration_ok=false` artefaktının hashsiz çalışmada abort etmesini, doğru hash ile verified-hash satırı taşıyarak nested çalışmasını; şeması bozuk artefaktın abort etmesini ve iki kimlik fikstürünün reddedilmesini istiyor.

Paket bundle checkout’u ve `evidence/calibration.json` üzerinde, beklenen nonzero çıkışları yakalayan bağımsız reviewer betiği şu sonucu verdi:

```text
A1 no_hash_rc=1 correct_hash_rc=0
A1 no_hash_stderr=[mde] ABORT -- an EXTERNAL calibration requires
                  --calib-expected-sha256 ...
A1 correct_hash_verified_lines=1
A1 correct_hash_nested_lines=1
A1 NOT REPRODUCED

A2 broken_rc=1
A2 verified_lines=0
A2 NOT REPRODUCED

B int-vs-string REJECTED RuntimeError:
[s01] document id must be a string, got int — schema failure

B trim-variant REJECTED RuntimeError:
[s01] document id is empty or carries surrounding whitespace
```

## 3.1 C33 — PASS

Haricî kalibrasyon yolu artık şu sırayı uygular:

1. Artefakt baytlarını bir kez okur.
2. `--calib-expected-sha256` alanını zorunlu tutar.
3. Hash’i parse işleminden önce karşılaştırır.
4. Aynı baytları strict JSON olarak parse eder.
5. Ortak recursive schema, üretim boyutları ve full binding’i denetler.
6. Her kapı hatasında `SystemExit` ile abort eder.
7. Bütün kapılar geçtikten sonra verified-hash satırını basar.
8. Ancak bundan sonra `calibration_ok` üzerinden motor seçer.

Gerçek frozen `calibration_ok=false` artefaktı:

- Hashsiz: exit 1 ve açık refusal.
- Doğru hash ile: verified-hash satırı + `full_nested_pass_p`.
- Yanlış hash ile: exit 1.
- Şeması bozuk ama kendi doğru hashine sahip sürüm: exit 1, verified satırı yok.

**C29/C31 → C33 disposition: PASS.**

## 3.2 C34 — PASS

`src/s01_fetch_metadata.py` artık ID için:

```python
isinstance(rid_raw, str)
rid_raw.strip() == rid_raw
bool(rid_raw)
```

şartlarını uyguluyor. Uniqueness ve completeness aynı kanonik string üzerinden yürütülüyor.

Sonuç:

```text
1 ve "1"       → REJECTED
"1" ve " 1 "   → REJECTED
"1" ve "2"     → ACCEPTED
```

**C30 → C34 disposition: PASS.**

## 3.3 SPROLL gerçek bayt davranışı — PASS

- Arşiv kaynağı `response.content`.
- `response.text` içindeki sahte içerik dikkate alınmıyor.
- Strict UTF-8 parse arşivlemeden sonra yapılıyor.
- Logdaki `bytes` sütunu `len(raw_bytes)` kullanıyor.
- Multibyte fixture byte/character farkını gerçek anlamda ayırt ediyor.

Bu uygulama onarımı geçerlidir.

---

# 4. BLOCKER 1 — C32 tek freeze-record sözleşmesini sağlamıyor

V13 talimatı açıkça v3.3’ün paketteki **tek record template** olduğunu ve superseded template’lerin çıkarıldığını söylüyor.

Gerçek paket:

```text
docs/STAGE_A_FREEZE_RECORD.md
docs/STAGE_A_FREEZE_RECORD_v3.3.md
```

Sürümsüz dosyanın ilk satırı:

```text
# Stage-A freeze record
(TEMPLATE — completed and externally timestamped on APPROVE)
```

Bu dosya:

- `PREREG_DRAFT_v0.4.md`yi frozen prereg olarak gösteriyor;
- yalnız Round-6 ruling placeholder’ı taşıyor;
- mevcut v0.5–v0.11 normatif zincirinden eski;
- adı ve içeriğiyle açıkça aktif bir template görünümünde.

Dolayısıyla “pakette yalnız bir template var” beyanı olgusal olarak yanlıştır.

## 4.1 Singleton testi karşı-örneği göremiyor

Mevcut test:

```python
recs = sorted(
    (ROOT / "docs").glob("STAGE_A_FREEZE_RECORD_v*.md")
)
assert len(recs) == 1
```

Bu glob yalnız `_v*.md` dosyalarını görür. Sürümsüz:

```text
STAGE_A_FREEZE_RECORD.md
```

testin kapsamı dışındadır.

Test docstring’i:

```text
EXACTLY ONE STAGE_A_FREEZE_RECORD_v*.md ships
...
a superseded template can never satisfy it again
```

diyor. Gönderilen paket, bu iddianın doğrudan karşı-örneğidir: test geçerken iki template sevk edilmiştir.

## 4.2 V3.3 güncel normatif amendment’ı açıkça içermiyor

`STAGE_A_FREEZE_RECORD_v3.3.md` frozen object’i şöyle tanımlıyor:

```text
PREREG_DRAFT_v0.5.md
+ PREREG_v0.6_AMENDMENTS
+ PREREG_v0.7_AMENDMENTS
+ PREREG_v0.8_AMENDMENTS
+ PREREG_v0.9_AMENDMENTS
+ PREREG_v0.10_AMENDMENTS
+ the APPROVED audit package zip
```

Ancak bu turun bağlayıcı onarımları:

```text
PREREG_v0.11_AMENDMENTS.md
C33–C35
```

açık frozen prereg zincirinde yer almıyor.

Dosyanın audit ZIP içinde bulunması, onu normatif prereg amendment olarak açıkça tanımlamakla aynı şey değildir. Özellikle önceki bütün amendment’ların tek tek sayıldığı bir tanımda v0.11’in dışarıda bırakılması, gelecekte C33–C35’in statüsü konusunda maddi belirsizlik üretir.

### Hüküm

## **C32 — FAIL / BLOCKER**

Timestamp edilecek nesne tekil ve eksiksiz biçimde tanımlanmamıştır.

---

# 5. BLOCKER 2 — C35 test sınıflandırması doğru değil

V13 beyanı:

```text
16 tests
old commit 10266ba:
12 failed / 4 passed

passing arms:
behavior-preservation / layer-attribution
docstring-marked
```

şeklindedir.

Güncel `tests/test_round11_repairs.py`, `10266ba` commit’ine taşındı. Eski commit’te bulunmayan isimler, repaired davranış taşınmadan, yalnız eski inline davranışları isimlendiren audit-only compatibility shim’leriyle görünür kılındı.

Yeniden hesaplanan sonuç:

```text
13 failed, 3 passed
```

Geçen üç test:

```text
test_attribute_only_anchor_variants
test_sproll_archives_verbatim_transport_bytes
test_schema_accepts_real_calibrate_output
```

## 5.1 12/4 neden artık mümkün değil?

Round-12 ruling’inde dördüncü eski-commit pass şuydu:

```text
test_packager_rejects_nonstandard_json_constants
```

Eski fixture eksik alanlarla dolu olduğu için eski packager zaten başka gerekçelerle exit ediyor ve test vacuous biçimde geçiyordu.

Round-13’te fixture doğru biçimde güçlendirildi:

- bütün diğer alanları geçerli;
- tek kusuru `NaN`;
- beklenen hata nedeni `strict JSON`.

Bu nedenle eski commit artık:

```text
crit_abs_z missing or non-numeric
```

gerekçesiyle test beklentisini karşılamıyor ve test **FAIL** oluyor.

Yani fixture’ın güçlendirilmesi, eski matrisin zorunlu olarak:

```text
12/4 → 13/3
```

değişmesine yol açmıştır. Teknik onarım doğru; frozen açıklama güncellenmemiştir.

## 5.2 “Docstring-marked” beyanı yanlış

Round-11 dosyasında function docstring taşıyan yalnız iki test vardır:

```text
test_packager_rejects_nonstandard_json_constants
test_freeze_record_covers_current_schema
```

Bunların ikisi de `10266ba` üzerinde fail olur.

Eski commit’te geçen üç testin hiçbirinde function docstring yoktur.

Ayrıca modül başlığı:

```text
every reviewer probe ... must stay dead
Flip tests FAIL on commit 10266ba
```

diyor. Dosyada eski commit’te kasıtlı olarak geçen üç preservation/layer-attribution kolu bulunduğu için bu başlık da kategorik olarak doğru değildir.

## 5.3 Round-12 test dosyasında da eksik sınıflandırma var

Güncel dokuz Round-12 testi, doğrudan önceki `1b71b4f` commit’i üzerinde:

```text
7 failed, 2 passed
```

veriyor.

Geçenler:

```text
test_canonical_string_ids_still_pass
test_sproll_archive_ignores_forged_text
```

İlk test preservation docstring’i taşıyor. İkincisi taşımıyor.

İkinci test daha eski text-based archive davranışına göre gerçek bir flip olsa da, incelenen doğrudan önceki `1b71b4f` commit’ine göre preservation pass’tir. “Hangi commit’e göre flip?” sorusu dosyada ve C35 açıklamasında açıkça cevaplanmalıdır.

### Hüküm

## **C35 — FAIL / BLOCKER**

NaN fixture, transport-forgery ve byte-count uygulamaları teknik olarak doğrudur. Ancak testlerin neyi kanıtladığına ilişkin frozen karar kaydı sayısal ve yapısal olarak yanlıştır.

---

# 6. BLOCKER 3 — Paketlenmiş reproducer beklenen ilk ABORT’ta kesiliyor

Paket içindeki:

```text
docs/reproduce_round12_blockers.sh
```

şununla başlıyor:

```bash
set -euo pipefail
```

İlk komut:

```bash
"$PY" "${COMMON[@]}" > "$TMP/no_hash.log"
```

C33 onarımından sonra bu komutun **exit≠0** vermesi gerekir. Komut `if`, `!` veya açık status-capture yapısı içinde olmadığı için `set -e` betiği burada sonlandırır.

Gerçek paket betiği sonucu:

```text
exit code: 1
stdout: 0 bytes

stderr:
[mde] ABORT -- an EXTERNAL calibration requires
--calib-expected-sha256 ...
```

Betiğin ulaşamadığı bölümler:

- doğru-hash A1 kolu;
- A1 `NOT REPRODUCED` kararı;
- schema-broken A2;
- A2 `NOT REPRODUCED` kararı;
- `int-vs-string` fikstürü;
- `trim-variant` fikstürü.

A2’de de aynı `set -e` sorunu vardır. Ayrıca refusal stderr’e yazılırken sonraki kontrol yalnız stdout dosyasında grep yapacak şekilde yazılmıştır.

Buradaki ayrım önemlidir:

- **C33/C34 uygulaması doğru.**
- **Reviewer-side düzeltilmiş reproducer beklenen dört hükmü veriyor.**
- **Paketin arşivlediği reproducer, doğru onarım karşısında çalışmıyor.**

### Hüküm

## **Archived reproducer — FAIL / BLOCKER**

Paketin özellikle referans verdiği adversarial kanıt betiği, göstermesi gereken sonucu üretemiyor.

---

# 7. Amendment disposition

V13 raporu C10, C30→C34, C27, C22, C16, C29/C31→C33, C32, C19, C25 ve C35 için açık disposition istiyor.

| Amendment | Hüküm | Denetim sonucu |
|---|---|---|
| **C10 — FSSA rule** | **PASS** | İlgili regresyonlar geçti; yeni karşı-örnek bulunmadı. |
| **C30 → C34 — canonical document identity** | **PASS** | ID yalnız nonempty ve trim-stable JSON string olabilir; iki collision reddedildi. |
| **C27 — template/year binding** | **PASS** | Tam 1994–2025 vektörü ile template/rate/binding alanları korunuyor. |
| **C22 — event-study failure propagation** | **PASS** | İlgili regresyonlar geçti. |
| **C16 — universal diagnostics** | **PASS** | İlgili regresyonlar geçti; failure masking görülmedi. |
| **C29/C31 → C33 — calibration provenance/schema** | **PASS** | Gate pre-`calibration_ok`; mandatory hash, strict parse, schema, size ve binding kontrolleri fail-closed. |
| **C32 — freeze record v3.3** | **FAIL / BLOCKER** | İki template sevk edilmiş; singleton testi sürümsüz template’i göremiyor; v0.11 açık frozen zincirde yok. |
| **C19 — ruling-chain completeness** | **PASS** | Dokuz gerekli ruling mevcut ve hash-valid; Round 6 declared pending. |
| **C25 — smoke signature** | **PASS** | Kritik değer tolerans içinde; shape, nested engine ve MDE80 aynı. |
| **C35 — test honesty / byte count** | **FAIL / BLOCKER** | Byte-count uygulaması doğru; 12/4 ve docstring beyanları yanlış. |
| **Archived Round-12 reproducer** | **FAIL / BLOCKER** | İlk beklenen abort `set -e` ile betiği sonlandırıyor. |

---

# 8. Zorunlu değişiklikler

1. **Sürümsüz eski template’i kaldırın:**

   ```text
   docs/STAGE_A_FREEZE_RECORD.md
   ```

   Tarihçe amacıyla tutulacaksa aktif freeze-record template olarak yorumlanamayacak bir ad ve konuma taşınmalıdır.

2. **Freeze record’u ilerletin ve v0.11’i açıkça normatif yapın:**

   ```text
   + PREREG_v0.11_AMENDMENTS (C33–C35)
   ```

3. **Singleton testini gerçek sözleşmeyi ölçecek biçimde değiştirin.**

   Test bütün:

   ```text
   STAGE_A_FREEZE_RECORD*.md
   ```

   adaylarını kapsamalı; yalnız tam güncel dosyanın bulunduğunu doğrulamalıdır.

   Ayrıca en az şunları aramalıdır:

   ```text
   PREREG_v0.11_AMENDMENTS
   C33
   C34
   C35
   rulings.round12
   ```

4. **C35’in bütün 12/4 beyanlarını 13/3 olarak düzeltin.**

   Düzeltilmesi gereken yerler:

   - `THIRD_EYE_REVIEW_PROMPT_v13.md`
   - `PREREG_v0.11_AMENDMENTS.md`
   - `ROUND13_KIT_NOTES.md`
   - `tests/test_round11_repairs.py` modül açıklaması

5. **Üç eski-commit pass’i gerçekten işaretleyin:**

   ```text
   test_attribute_only_anchor_variants
   test_sproll_archives_verbatim_transport_bytes
   test_schema_accepts_real_calibrate_output
   ```

6. **Round-12 test sınıflandırmasının baseline’ını açıkça yazın.**

   `1b71b4f` için doğru matris:

   ```text
   7 failed / 2 passed
   ```

   `test_sproll_archive_ignores_forged_text` için hangi eski commit’e göre flip sayıldığı açıklanmalı veya preservation olarak işaretlenmelidir.

7. **Paketlenmiş reproducer’ı onarın.**

   Beklenen nonzero komutlar için:

   - `set +e`/status capture veya `if command; then ... fi`;
   - stdout ve stderr ayrı kayıt;
   - exit kodu assert’i;
   - mesaj assert’i;
   - sonraki proba devam;
   - A1/A2 `NOT REPRODUCED`;
   - iki ID için `REJECTED`.

   Betiğin kendisini çalıştırıp bu dört sonuç satırını doğrulayan bir regresyon eklenmelidir.

8. **C33 ve C34 çekirdek koduna geri dönüş yapmayın.**

   Bu iki yöntem blokeri mevcut hâliyle kapanmıştır.

9. Bu Round-13 ruling’ini ruling zincirine ekleyin, final commit üzerinde dört-run evidence’i yeniden üretin, yeni freeze record/paket/freeze JSON oluşturun ve yeni binary inceleme turuna gönderin.

# Final instruction

## **Bu Round-13 nesnesi OSF’ye timestamp edilmemelidir.**

Çekirdek yöntem onarımları hazırdır; ancak frozen object tanımı, C35 test sınıflandırması ve arşivlenmiş yeniden üretim betiği mevcut hâliyle doğru ve tekil değildir.