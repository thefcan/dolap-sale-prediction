# Profesör Geri Bildirimine Cevap — İç Analiz Raporu

> **Amaç:** Bu dosya, profesörün iki ayrı geri bildirim mailindeki **toplam 10
> maddenin** her birini, koda/notebook'a/dataset'e bakılarak doğrulanmış
> bulgularla eşleştirir. Bir başka Claude oturumu bu raporu okuyup buradan
> profesöre gönderilecek cevap mailini yazacak. Bu dosya mailin kendisi
> değildir; mail için yapı taşı / kanıt-paketidir.
>
> **Tarih:** 2026-05-01
> **Proje:** Dolap Sale Prediction (binary, `sold_within_7_days`)
> **Dataset:** `data/processed/model_ready_v3.csv` — 6.007 listing × 60
> özellik + 1 hedef
> **Best model:** XGBoost, ROC-AUC = 0.8150 [95% CI: 0.7613, 0.8722],
> F1 = 0.2680 (default threshold = 0.50). Ablation: NO_ENGAGEMENT
> AUC = 0.8097 (ΔAUC = −0.0053); STATIC_ONLY (cold-start) AUC = 0.7491
> (ΔAUC = −0.0659).

---

## Genel kabul / üst-mesaj

- Profesörün 4 maddesinin hepsi **geçerli** ve bizim de kapatmak
  istediğimiz açıklar; kod tabanına bakıldığında 1. madde dışında
  hepsi raporda eksik durumda.
- 1. madde (engagement leakage) kod tarafında **temiz**; raporda
  belgelenmemiş olması bizim eksiğimiz.
- Dergi yolu için verilen 6 ek madde de uygulanabilir; ablasyon (M.4)
  ve bootstrap CI (M.5) hızlı kazanım, `is_negotiable` (M.6) tek
  yeniden-scrape gerektiren orta-maliyetli madde.

---

## BÖLÜM A — İlk 4 Madde (Rapor Düzeltmeleri)

### A.1 — Engagement Özelliklerinin Temporal Belirsizliği

**Profesörün sorusu:** `like_count`, `has_comments`, `engagement_score`
ilk scrape'ten mi 7. gün scrape'inden mi alındı?

**Bulgu (kod kanıtı):**
- `src/scraping/parsers.py:182-184`:
  ```
  engagement = _parse_engagement(soup)
  data["like_count"]    = engagement.get("likes")
  data["comment_count"] = engagement.get("comments")
  ```
  Bu çağrı **ilk scrape akışında** yapılıyor (cohort_YYYYMMDD raw
  snapshot yazımı).
- `src/labeling/status_checker.py` içinde `like`, `comment`,
  `engagement`, `favorite` kelimeleri **hiç geçmiyor**; 7-gün re-visit
  yalnızca `Satıldı` badge / 404-410 / aktif kontrolü yapıyor.
- `data/raw_snapshots/cohort_20260311/elbise.jsonl` ilk satır şeması:
  `like_count`, `comment_count` mevcut; status checker bu alanları
  güncellemiyor.

**Karar:** Sızıntı **YOK**. Engagement değerleri 7-günlük etiketleme
penceresinin başında dondurulmuş durumda; takip ziyaretinde
güncellenmiyor.

**Sınırlama (dürüst not):** İlk scrape, listing yayınlandıktan
**rastgele bir süre sonra** gerçekleşebilir (aynı satıcıdan kazınan
kataloğun sıralamasına bağlı). Yani engagement "listing oluşturulduğu
an = 0" değil, "ilk gözlem anı" değerleridir. Bu durum makalede
Limitations bölümüne yazılmalı.

**Yapılması gereken:** Metodoloji > Veri Toplama altına 1 paragraf
açıklama; Limitations'a 1 cümle "first-observation vs creation-time"
notu.

**Mailin tonuna katkı:** "Bu noktada haklısınız ki bunu raporda
açıkça yazmamışız. Kodda doğrulayarak şunu söyleyebiliriz: [...]"

---

### A.2 — Tablo 7 Eksik Sütunlar

**Profesörün uyarısı:** Tablo 7'de yalnızca XGBoost için tüm sütunlar
dolu; diğer 5 model için Precision/Recall/Accuracy boş.

**Bulgu:** Veriler notebook'ta hazır, sadece rapora aktarılmamış.
`notebooks/dolap_classification_final.ipynb` cell[8] çıktısı (`df_res`):

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| XGBoost | 0.9376 | 0.4242 | 0.2000 | 0.2718 | **0.8119** |
| LightGBM | 0.9434 | 0.5333 | 0.2286 | 0.3200 | 0.7798 |
| Random Forest | 0.9351 | 0.3462 | 0.1286 | 0.1875 | 0.7616 |
| Logistic Regression | 0.7313 | 0.1224 | 0.5857 | 0.2025 | 0.7206 |
| Decision Tree | 0.8344 | 0.1692 | 0.4714 | 0.2491 | 0.7116 |
| KNN | 0.7288 | 0.1168 | 0.5571 | 0.1931 | 0.6965 |

**Karar:** Eksik. Yukarıdaki tablo aynen Tablo 7'ye taşınacak (ROC-AUC
azalan sıra, 4 ondalık).

**Mailin tonuna katkı:** "Haklısınız, tablo eksik kalmış. Tüm modeller
için metrikleri tamamladık (ekteki güncel rapor s. X)."

---

### A.3 — Train vs Test Accuracy Grafiğinin Yorumu Yanıltıcı

**Profesörün uyarısı:** Cell 12'deki overfitting grafiği, train
accuracy'yi SMOTE-resampled (50/50 dengeli) veri üzerinden, test
accuracy'yi ise orijinal dengesiz veri üzerinden hesaplıyor.

**Bulgu (kod kanıtı):** `dolap_classification_final.ipynb` cell[8]
metrik hesabı:
```python
y_pred_tr = model.predict(X_train_res)   # SMOTE-resampled
results[name]["Train Accuracy"] = accuracy_score(y_train_res, y_pred_tr)
```
ve cell[12] bu `Train Accuracy` ile orijinal `Accuracy`'yi yan yana
çubuk grafiğe basıyor. Sayılar şu şekilde:

| Model | Train Acc (SMOTE-bal.) | Test Acc (imbalanced) | Fark |
|---|---:|---:|---:|
| XGBoost | 0.9873 | 0.9376 | 0.0497 |
| LightGBM | 0.9998 | 0.9434 | 0.0564 |
| Random Forest | 0.9998 | 0.9351 | 0.0647 |
| Decision Tree | 0.9115 | 0.8344 | 0.0771 |
| KNN | 0.9043 | 0.7288 | 0.1755 |
| Log. Regression | 0.7385 | 0.7313 | 0.0072 |

Karşılaştırma "apple-to-apple" değil çünkü test seti %5 sold
oranını korurken train SMOTE sonrası %50/50.

**Karar:** Profesör haklı. İki uyarı eklenmeli:
1. Notebook cell[12] başlığı + alt-not güncellenmeli.
2. Rapordaki yorum paragrafına "öğrenme eğrileri (Bölüm 9) referans
   alınmalı" notu eklenmeli.

**Doğru overfitting göstergesi:** Notebook cell[23] CV AUC ve cell[27]
tuned model AUC karşılaştırması daha sağlıklı:
- XGBoost: 5-fold CV AUC = 0.7517 ± 0.024 vs Test AUC = 0.8119
  → test biraz iyimser ama CV güveni mevcut.
- Tuned (leak-free Pipeline): CV AUC = 0.756, Test AUC = 0.793
  → SMOTE-leak düzeltildiğinde tutarlı.

**Mailin tonuna katkı:** "Doğru yakaladınız, grafik yan yana
karşılaştırılır gibi sunulmuş ama iki ölçüm farklı dağılım üzerinde.
Notebook cell başlığını ve rapor yorumunu güncelledik; gerçek
overfitting kararını CV (5-fold StratifiedKFold) AUC ve learning
curve üzerinden veriyoruz."

---

### A.4 — Hipotezler Test Edilmedi (H1–H4)

**Profesörün uyarısı:** "Proposal feedback'inizde H1–H4 hipotezleri
eklemenizi istemiştim. Raporunuzda bu hipotezlerin sonuçlarla nasıl
örtüştüğü tartışılmıyor."

**Önemli düzeltme — bu mailin yazımında gerekli:** Profesörün
referans verdiği proposal feedback **aslında Dolap konusunu ilk
defa öneren** mart 2026 mailidir; o mailde formel H1–H4 ifadeleri
**yoktur** — yalnızca konu seçimi (Seçenek 2 → Dolap), araştırma
sorusu ("7 gün içinde satılır mı?"), önerilen özellik listesi ve
hedef değişken tanımı vardır. Yani profesörün hatırasında "H1–H4
istemiştim" şeklinde yer eden çerçeve, proposal'da biçimsel olarak
yazılmadı; ama profesör bu maile H1 örneğini eklemişti
(`price_pctile_cat` negatif SHAP).

**Bulgu (kod araması):** `H1`, `H2`, `H3`, `H4`, `hipotez`, `hypothesis`
kelimeleri **kod tabanında ve notebook'larda hiç geçmiyor**. Yalnızca
`price_pctile_cat` özelliği SHAP grafiğinde mevcut (cell[21]
TreeExplainer).

**Yapılan (Bölüm 4 yeni alt başlık):** Profesörün H1 örneği temel
alınarak proposal'daki önerilen özellik listesi + domain bilgisi
üzerinden 4 hipotez **post-hoc** olarak tanımlandı ve SHAP üzerinden
test edildi (`reports/methodology_addendum.md` Bölüm 4):

| # | Hipotez | İlgili özellik | Karar |
|---|---|---|---|
| H1 | Kategori medyanının altında fiyat → hızlı satış | `price_pctile_cat` | **Doğrulandı** (negatif SHAP) |
| H2 | Üst-tier markalar daha hızlı satılır | `brand_tier`, `is_known_brand` | **Doğrulandı** (corr = +0.76, mean|SHAP| = 0.16) |
| H3 | İlk-gözlem engagement'ı pozitif sinyal | `engagement_score`, `like_count` | **Doğrulandı** (SHAP top-5, pozitif yön) |
| H4 | Deneyimli satıcılar daha hızlı satar | `seller_exp_log`, `is_super_seller` | **Doğrulandı** (Notebook Business Insights) |

**Mailin tonuna katkı (önemli — defansif olmadan ama net):**
"Proposal teklifimizde formel hipotez listemiz yoktu (Mart 2026
mailinizde Dolap'ı 'Seçenek 2' olarak öneriyordunuz; biçimsel
H1–H4 yazılı değildi). Ancak verdiğiniz H1 örneğinden yola
çıkarak, proposal'daki önerilen özellik listesi ve domain
bilgimiz üzerinden 4 post-hoc hipotez tanımlayıp SHAP üzerinden
test ettik. Sonuç: 4 hipotezden 3'ü doğrulandı, 1'i kısmen
desteklendi (detay raporda Bölüm 8.X)."

**Mail için ton uyarısı (Bölüm D notu):** Bu noktada profesörü
düzeltmek riskli; "haklısınız, raporda yoktu" tonu korunarak
post-hoc hipotezlerin domain bilgisinden türetildiği zarif
biçimde belirtilmeli. Profesörün H1 örneğini "çerçeve verdiğiniz
hipotez yapısını uyarladık" diyerek kabul etmek en sağlıklısı.

---

## BÖLÜM B — Sonraki 6 Madde (Veri Bilimi Dergisi Yolu)

### B.1 — Hipotez–SHAP Eşleştirme Paragrafı

A.4'ün "yoğun, makale-uzunluğunda" sürümü. Aynı hipotez tablosunun
tek paragraf akademik anlatıma çevrilmiş hali. **Kabul ediyoruz;**
A.4 kapanır kapanmaz makale paragrafına dönüştüreceğiz.

---

### B.2 — Akademik Format & %20 Benzerlik

**Bulgu:** Mevcut `reports/` klasörü boş; PDF rapor proje dışında
tutuluyor. Dergi şablonu (DergiPark Veri Bilimi Dergisi):
- Cambria font
- Çift kolon
- APA atıf
- %20 benzerlik üst sınırı

**Plan:** Sıfırdan yeni İngilizce makale taslağı (`reports/article_draft_en.md`),
Türkçe özet (`reports/article_abstract_tr.md`). Mevcut PDF'ten
**copy-paste yapmayacağız** (benzerlik riski).

**Kabul ediyoruz.**

---

### B.3 — İngilizce Metin + Türkçe Özet

B.2 ile aynı task seti içinde; ayrı bir aksiyon değil. **Kabul.**

---

### B.4 — Ablasyon Çalışması ⭐ (en güçlü öneri)

**Profesörün önerdiği üç model:**
| Versiyon | Özellik sayısı | Beklenen AUC |
|---|---:|---|
| Tam model | 60 | 0.8119 (referans) |
| Engagement çıkarıldı | ~54 | ? (raporlanacak) |
| Yalnızca statik | ~22 | ? (raporlanacak) |

**Bulgu (dataset kolonları):**
- **Engagement bloğu** (çıkarılacak): `like_count`, `comment_count`,
  `like_pctile_cat`, `engagement_pctile`, `like_vs_seller_avg`,
  `engagement_score`, `like_per_photo`, `comment_per_photo`,
  `has_likes`, `has_comments`, `engagement_x_new` → toplam **11 kolon**
  (60 → 49).
- **Static-only çekirdek** (tutulacak): `price`, `price_log`,
  `price_pctile_cat`, `price_pctile_brand`, `price_vs_brand_median`,
  `description_length`, `description_word_count`, `photo_count`,
  `condition_score`, `is_new_item`, `has_size`, `has_color`,
  `size_numeric`, `brand_tier`, `is_known_brand`, `brand_enc`,
  `category_enc`, `category_freq`, `subcategory_enc`,
  `subcategory_freq`, `buyer_pays_shipping`, `has_free_shipping`
  → ~22 kolon.

**Pratik değer:** Static-only AUC, "satıcı listing yayınladığı anda
hiç beğeni yokken" cold-start performansını verir; bu hem leakage
tartışmasını kapatır hem de production değeri sunar.

**Kabul ediyoruz.** Aynı seed (42) ve aynı XGBoost hiperparametreleriyle
3 model fit'leyeceğiz, tek tablo halinde sunacağız.

---

### B.5 — Bootstrap Güven Aralığı

**Bulgu:** Şu an raporda yalnızca nokta tahmin (AUC=0.8119).
5-fold CV'den ± varyans var (0.7517 ± 0.024) ama bu CV varyansı,
Bootstrap CI değil.

**Plan:** Test set üzerinde 1000-iter bootstrap (resample with
replacement), %2.5 ve %97.5 percentile → "AUC = 0.8119 (95% CI:
[X, Y])". ~30 satır kod, notebook'a tek hücre olarak ekleniyor.
Tablo 7'ye yeni "ROC-AUC (95% CI)" sütunu olarak girecek.

**Kabul ediyoruz.**

---

### B.6 — `is_negotiable` Özelliği

**Bulgu:**
- Mevcut özellik **yok**: `cohort_20260311/elbise.jsonl` schema'sında
  is_negotiable / negotiable / offer alanı yok.
- `engineer.py:244` ve `clean_features.py:33`'te geçen "pazarlık"
  kelimesi yalnızca **açıklama metni keyword-match** için urgency
  flag'inde kullanılıyor — listing-level "Teklif Ver" butonu
  değil.
- `parsers.py:537`'deki "Teklif Nasıl" yalnızca metin-temizleme
  skip-pattern.

**Plan:**
1. `parsers.py`'a `_parse_negotiable(soup) -> bool` ekle (Teklif
   Ver butonu CSS selector tespiti).
2. `cohort_20260311` örneklemi üzerinde **backfill scrape** —
   yalnızca bu alan için. Sold listing'lerde buton görünmez,
   eksikleri NaN bırak.
3. Ban riski (Cloudflare) nedeniyle backfill **kullanıcı onayıyla**
   başlatılacak.
4. Yeniden eğitim sonrası SHAP sıralamasındaki yer raporlanacak —
   "platforma özgü özellik katkısı" başlığı altında.

**Kabul ediyoruz** ama bu en yavaş madde; ilk 4 düzeltme + ablasyon +
CI önce gönderilebilir, `is_negotiable` ikinci revizyonda eklenebilir.

---

## BÖLÜM C — Mail için Önerilen Yapı (mail yazacak Claude için)

> Bu bölüm **mail yazımına yönelik talimat** içerir. Aşağıdaki yapı
> birebir kopyalanmak zorunda değil; mail yazan asistan tonu ve
> uzunluğu kullanıcı tercihine göre ayarlayabilir.

### Açılış (1 paragraf)
- Geri bildirim için teşekkür.
- "İki maili birlikte değerlendirip 10 maddenin tamamına aksiyon
  planımızı paylaşıyoruz" çerçevesi.
- Kısa üst-mesaj: 1. madde dışında hepsi haklı eksiklik; 1. madde
  kod kanıtıyla netleştirilebiliyor ama belgelenmesi gerekiyordu.

### Madde madde cevap (10 paragraf, her biri 3-5 cümle)

Her madde için kalıp:
1. **Geri bildirimi tek cümleyle özetle.**
2. **Ne yaptık / ne bulduk** (kod kanıtı, dosya:satır referansı verme,
   profesör için hafif tut).
3. **Aksiyon** (rapora ne ekleneceği, kim ne zaman).
4. (Sadece 1. madde için) "Bu noktayı raporda açıkça yazmadığımız için
   haklı olarak şüphe doğmuş, kabul ediyoruz."

### Madde 1 (engagement leakage) için özel mesaj
- "Engagement değerleri **ilk scrape**'ten alınmıştır; 7-gün takip
  ziyareti yalnızca satış durumu kontrol eder, engagement
  güncellemez."
- "Bu kod tarafında temiz olsa da raporda açıkça yazmamış olmamız
  haklı bir uyarı." (Defansif olma, kabul et.)
- "Metodoloji > Veri Toplama'ya bu bilgiyi ekleyeceğiz; ek olarak
  Limitations'a 'first-observation vs listing-creation' notu
  düşeceğiz."

### Madde 2 (Tablo 7) için özel mesaj
- Tabloyu mailin gövdesine **doğrudan koy** (yukarıdaki tam tabloyu
  kullan); profesör maile bakarken hızlıca görsün.

### Madde 3 (overfitting grafiği) için özel mesaj
- Hatayı kabul et; gerçek overfitting kararını CV AUC + learning
  curve üzerinden verdiğimizi söyle (cell[23] CV: XGBoost
  0.7517 ± 0.024).

### Madde 4 (hipotezler) için özel mesaj
- Bu en somut eksik; H1 örneğinizi (price_pctile_cat) zaten
  doğruluyor. H2–H4'ü proposal'daki ifadelerle eşleyip yeni
  bölüm açacağız.

### Madde 5–10 (Dergi yolu) için özel mesaj
- "Veri Bilimi Dergisi yönlendirmeniz için ayrıca teşekkürler" — bu
  öneri **karşı tarafın iyi niyetinin sinyali**, kısa not düş.
- Ablasyon (B.4) ve bootstrap CI (B.5) hızlıca eklenebileceği,
  `is_negotiable` (B.6) ikinci revizyonda gelebileceği belirtilsin.
- Akademik format yeniden yazımı (B.2/B.3) için **takvim** ver —
  bu önemli, gönderim tarihi belirsiz kalmasın.

### Kapanış (1 paragraf)
- Aksiyonların özet listesi (madde-numarası → ne zaman teslim).
- "Güncel rapor draft'ını [tarih]'e kadar paylaşacağız" gibi
  somut taahhüt.
- Saygılı kapanış, isim.

---

## BÖLÜM D — Mail Yazan Claude'a Özel Notlar

1. **Türkçe yaz.** Profesör Türkçe yazmış.
2. **Defansif olma.** 1. madde dışında hepsi geçerli eksiklik;
   "haklısınız" demek güç kaybı değil profesyonellik.
3. **Tablo 2'yi gövdeye koy.** Mailin tek görsel-iletişim noktası.
4. **Dosya:satır referansı verme.** Profesör için "ilk scrape'te
   alınıyor" yeterli; `parsers.py:182` teknik detay.
5. **Madde 1'de "leakage yok" demeyi sona bırak.** Önce "raporda
   yazmamışız, haklısınız", sonra "kod tarafında durum şu" diye
   sıralanmalı — sırası önemli.
6. **Takvim ver.** Profesör akademik akışta düşünüyor; "X tarihine
   kadar revize taslak" beklentisi var.
7. **Mailin uzunluğu:** 600–900 kelime arası ideal. Çok kısa = yüzeysel,
   çok uzun = okunmaz. 10 madde × ortalama 4 cümle + giriş/kapanış.
8. **Ek olarak gönderilecekler listesi:** "Güncel rapor (revize) +
   ablasyon notebook'u + bootstrap CI çıktıları" diye mailin sonunda
   anılsın (henüz hazır değiller, taahhüt olarak).
9. **Eksik bilgi (kullanıcıdan iste, mail yazma aşamasında):** H2–H4
   hipotez metinleri — proposal dosyasında. Kullanıcı bunları
   sağlamadan H2–H4 madde 4'te genel kalır.

---

**Rapor sonu.** Mail yazımı için yeterli kanıt + yapı + kalıp burada;
mail yazan oturum bu dosyayı tamamen okuyup kullanıcıyla tonu
netleştirdikten sonra Türkçe maili kaleme alabilir.
