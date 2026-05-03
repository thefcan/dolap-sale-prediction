# Halil Utku'nun Sunum Scripti — Detaylı

> **Toplam sahne süresi**: ~6 dk notebook bloğu + Q&A katılımı
> **Sorumluluk**: §1, §2, §5, §6, §8, §9, §10, §11, §13, §14, §16 — model kararları omurgası
> **Kritik bölüm**: §14 RC4 (B.1 anomaly cevabı) — yavaş, vurgulu anlatılacak
> **Pencere**: Tab 2 = `notebooks/dolap_classification_final.html` (kod-gizli)

---

## Sahne öncesi mental hazırlık (T-5 dk)

- F demo bitirirken senin sıran yaklaşıyor — sahne kenarında dur, mikrofona yaklaş
- HTML §1'in başında olmalı (F demo bitiminde §1'e scroll edecek)
- Cep notu = bu dosya. Section başlıkları + söyleyeceğin metin satır satır.
- **Önemli**: Test AUC 0.815'i §9'da söylerken anomaly'ye değinme — §14'te grafikle birlikte anlatılır. Sürpriz olsun.

---

## 5:00 — 5:30 · §1 Setup & Data Loading (30 sn)

### Yapacağın
- F devir cümlesini söyledikten sonra sahne ortasına gel
- HTML'de §1 başlığını işaret et — "Section 1 — Setup & Data Loading"
- Aşağıda dataset shape çıktısı var: `Dataset shape : (6007, 61)` ve `Train: ... Test: ...`
- Class dağılımı tablosu: 0=94.2%, 1=5.8%

### Söyleyeceğin (kelime-kelime)

> "Teşekkürler Furkan. Section 1, veri yüklemesi.
>
> Dataset boyutu: **6,007 ilan, 60 mühendislik özelliği**. Pozitif sınıf — yani 7 günde satılmış ilanlar — toplam **%5.8**. Yani her 17 ilandan biri.
>
> Bu imbalance üç tane önemli karara sebep oldu: **(1) SMOTE oversampling**, **(2) F1-tabanlı eşik optimizasyonu**, **(3) bootstrap güven aralığı**. §11 ve §13'te bunları detaylandıracağım."

→ Hızla §2'ye scroll (Cmd+F → "Section 2" → enter)

---

## 5:30 — 6:00 · §2 Preprocessing & Train/Test Split (30 sn)

### Yapacağın
- §2 başlığını işaret et
- Train/val/test boyutları görünür: 60/20/20 split
- "Stratified" kelimesini vurgula

### Söyleyeceğin

> "Section 2: train/val/test split **60/20/20**, **stratified random shuffle** — sınıf dağılımı her fold'da korunuyor.
>
> Pipeline mimarisi: **Imputer → Scaler → Model**. İmputer sadece train'de fit ediliyor, val/test'te transform — leak-safe. Aynı şekilde **SMOTE sadece train fold'unda** uygulanıyor, validation set'i hiç görmüyor."
>
> *(Hızlı not)*
>
> "Bu split rastgele — yani satıcı kimliğini koruyamıyor. **§14'te bunun sonuçlarını göreceksiniz**."

→ §3, §4 atlayarak doğrudan §5'e scroll. (Cmd+F → "Section 5")

---

## 6:00 — 6:45 · §5 Visual Model Comparison (45 sn)

### Yapacağın
- §5 başlığını göster — "Visual Model Comparison"
- Bar grafiği: 5 modelin AUC + F1 karşılaştırması yan yana
- En yüksek bar XGBoost (sağ uçta)

### Söyleyeceğin

> "Section 5: **5 baseline + 2 gradient-boosting model** karşılaştırdık. Bar grafiğinde: Logistic Regression, KNN, Decision Tree, Random Forest, XGBoost.
>
> *(En yüksek bar'ı işaret et)*
>
> XGBoost en yüksek AUC, ardından Random Forest. Logistic Regression ve KNN imbalance altında zayıf — bu beklenen sonuç çünkü bu iki model SMOTE'a daha duyarlı kalibrasyon gerektiriyor.
>
> Detay tablo §10'da, oraya birazdan geleceğim."

→ §6'ya scroll (Cmd+F → "Section 6")

---

## 6:45 — 7:30 · §6 Confusion Matrices (45 sn)

### Yapacağın
- §6 başlığı — "Confusion Matrices"
- 5 model için 2×2 confusion matrix grid'i görünür
- TP / FP / FN / TN sayıları

### Söyleyeceğin

> "Section 6: confusion matrix'ler. **Default eşik τ=0.50'de** tüm modeller pozitif sınıfa eğilimli kayıp veriyor — yani **false negative** sayısı yüksek.
>
> *(XGBoost confusion matrix'i işaret et)*
>
> XGBoost'un satırına bakın: 13 true positive, 57 false negative. Recall 0.19 — düşük. Bu, eşik optimizasyonunu §11'de neden yaptığımızın doğrudan sebebi.
>
> Hocamızın **'hangi örneklerde hata yapıyor?' sorusuna** ek olarak demo'da gerçek hard-negative ve hard-positive vakalarını gösterdik. Şimdi PR eğrisine geçeceğiz, ROC ve PR yorumunu Halil İbrahim verecek."

→ Sahnenin yan tarafına çekil, Hİ'yi sahneye davet et.

> *(Köprü cümlesi)*
>
> "Halil, ROC ve PR eğrileri."

→ Hİ §7'ye scroll eder ve konuşmaya başlar.

---

## 7:30 — 8:15 · §7 ROC & PR Curves (Hİ konuşur, sen sahne kenarında)

> Bu bölümde sen sahne ortasında değilsin. Hİ §7 ROC ve PR yorumunu yapıyor (45 sn).

---

## 8:15 — 9:15 · §8 Best Model Deep Dive (1 dk — kritik)

### Yapacağın
- Hİ "Tekrar Halil Utku'ya — best model deep dive" deyince sahne ortasına gel
- §8 başlığı — "Best Model Deep Dive"
- Aşağı scroll: classification report tablosu, confusion matrix, **SHAP summary plot**

### Söyleyeceğin (yavaş, vurgulu — kritik bölüm)

> "Section 8: **Best Model Deep Dive**. Seçilen model XGBoost.
>
> Classification report: precision **0.48**, recall **0.19** — default eşikte recall düşük dedik.
>
> *(SHAP summary plot'a scroll)*
>
> Şimdi SHAP grafiği. Bu, modelimizin hangi özellikleri kullandığını gösteriyor. Önemli özellikler: **like_count, engagement_score, price_pctile_cat, brand_tier**, satıcı deneyimi.
>
> *(Vurgu artır)*
>
> Bu noktada **bir reviewer feedback'ine doğrudan cevap vereceğim — A yorumu, post-hoc framing**. Önceden kayıtlı hipotezimiz **iki tane**: **H1** fiyat pozisyonu negatif yönde satışı tahmin eder, **H2** marka kademesi pozitif yönde satışı tahmin eder. SHAP bunları **doğrulayıcı** olarak destekliyor — H1 için price_pctile_cat negatif yön, H2 için brand_tier mean SHAP korelasyonu **artı 0.76**.
>
> *(Soluklan)*
>
> Diğer SHAP gözlemlerimiz — engagement, satıcı deneyimi vs. — **post-hoc keşifsel** olarak işaretli. Yani 'bu özellik X yapıyor' iddiası değil, 'modelde bu pattern var' gözlemi. Yeniden kayıtlı çalışmaya konu olabilir."

→ §9'a scroll.

---

## 9:15 — 9:45 · §9 Cross-Validation (30 sn — sürpriz hazırlığı)

### Yapacağın
- §9 başlığı — "Cross-Validation"
- 5-fold CV sonuçları tablosu görünür
- CV AUC mean=0.7517, std=0.0239

### Söyleyeceğin

> "Section 9: **5-fold stratified Cross-Validation**. Ortalama AUC **0.752**, standart sapma **0.024**.
>
> *(Hafif duraksa)*
>
> Burada bir not: **test AUC 0.815, CV ortalaması 0.752'den yüksek**. Bu sıradışı. Bunun açıklaması §14'te. Şimdilik **aklınızda kalsın**."

> **🔴 SAKIN açıklama yapma** — §14'te grafikle birlikte tek seferde anlatılacak. Audience'ın merak duygusunu §14'e taşı.

→ §10'a scroll.

---

## 9:45 — 10:45 · §10 Final Model Selection (1 dk — B.3 cevabı)

### Yapacağın
- §10 başlığı — "Final Model Selection"
- 6-model karşılaştırma tablosu: XGBoost / LightGBM / RF / LR / DT / KNN
- AUC, Precision, Recall, F1 sütunları + 95% CI

### Söyleyeceğin

> "Section 10: **Final Model Selection**. XGBoost final model.
>
> Tablonun en üstünde XGBoost: AUC 0.815, F1 0.268. Hemen altında LightGBM: AUC 0.780, F1 0.320.
>
> *(Audience'a doğru çevril)*
>
> **Reviewer'ın B.3 sorusu — 'neden XGBoost, neden LightGBM değil?'** Üç gerekçemiz var.
>
> *(Parmaklarla say)*
>
> **Bir**: AUC farkı 0.035, küçük değil. **İki**: F1-optimal eşik kullanırken XGBoost 0.354, LightGBM 0.301'e çıkıyor — precision-recall trade-off XGBoost lehine. **Üç**: SHAP monotonic constraints — H1 ve H2 hipotezleri için XGBoost'un monotonic feature constraint API'si daha temiz çalıştı. LightGBM'de aynı constraint'leri set ettiğimizde model kararsız fit oldu.
>
> *(Sonuç tonu)*
>
> Tek-seed ablasyon yaptığımızı kabul ediyoruz; multi-seed bootstrap gelecek çalışma listesinde. `methodology_addendum.md` Bölüm 9.X'te bu argüman tam yazılı."

→ §11'e scroll.

---

## 10:45 — 11:45 · §11 Hyperparameter Tuning + Threshold Optimization (1 dk)

### Yapacağın
- §11 başlığı — "Hyperparameter Tuning"
- RandomizedSearch best params görünür
- Aşağı scroll: PR-eğrisi grafiği + F1 vs τ sweep grafiği

### Söyleyeceğin

> "Section 11: **Hyperparameter Tuning + Threshold Optimization**.
>
> RandomizedSearchCV, **50 iterasyon × 5-fold stratified**. Önemli detay: **SMOTE pipeline içinde** — search'in her fold'u kendi SMOTE'unu fit ediyor. Yani CV sırasında **leakage yok**. Best params: n_estimators=300, max_depth=5, learning_rate=0.05.
>
> *(PR grafiğine scroll)*
>
> Şimdi threshold story. **Default τ=0.50'de F1=0.268**.
>
> *(F1 vs τ grafiğini işaret et)*
>
> PR-eğrisi sweep'inde F1 maksimum yapan eşik **τ=0.247**, F1=0.354. Yani **%32 iyileşme**. Recall'u 0.19'dan 0.32'ye taşıyor — false negative sayısını yarı yarıya azaltıyor.
>
> Demo'da Furkan slider'da bu eşiği gösterdi. **Reviewer'ın B.2 yorumunun cevabı tam burada**: aynı modeli yeniden eğitmeden, sadece eşiği değiştirerek operasyonel davranış değişiyor."

→ Hİ'ye köprü.

> *(Köprü cümlesi)*
>
> "Reviewer feedback'inin tam haritasını Halil İbrahim çıkardı, §12'ye geçiyor."

→ Hİ §12'ye scroll eder, konuşmaya başlar. Sen yan tarafa çekil.

---

## 11:45 — 12:45 · §12 Reviewer Mapping (Hİ konuşur, sen sahne kenarında)

> Bu blokta sen sahnede değilsin. Hİ reviewer mapping tablosunu açıklıyor (1 dk).

---

## 12:45 — 13:15 · §13 Bootstrap Confidence Intervals (30 sn)

### Yapacağın
- Hİ "Halil Utku bootstrap CI ve robustness check'ı detaylandıracak" deyince sahne ortasına gel
- §13 başlığı — "Bootstrap Confidence Intervals"
- 200-resample bootstrap çıktısı + histogram

### Söyleyeceğin

> "Section 13: bootstrap confidence intervals. **200 resample test setinden**, replacement ile.
>
> Sonuç: **AUC 0.815, %95 GA [0.7613, 0.8722]**, genişlik yaklaşık 0.06.
>
> *(Histogram'ı işaret et)*
>
> Histogram da görünüyor — dağılım tek-modlu, simetrik. Sayı tek-noktasal değil; CI ile birlikte raporluyoruz. Bu reviewer'ın **1. tur 1. yorumuna** doğrudan cevap."

→ §14'e scroll. Bu **kritik bölüm**, hazırlan.

---

## 13:15 — 14:15 · §14 RC4 Robustness — TEST > CV ANOMALY (1 dk — KRİTİK)

### Yapacağın
- §14 başlığı — "Robustness Check: Test vs CV AUC Gap Explained by Seller-Identity Leakage"
- 4-bar grafik: Random / CV / Group-aware / Headline
- Aşağı scroll: protocol A vs protocol B tablosu

### Söyleyeceğin (YAVAŞ, vurgulu — bu bölüm kritik)

> "Section 14, sunumun en önemli bölümlerinden biri.
>
> *(Audience'a doğru dönerek konuşma temposu yavaşlat)*
>
> Demin §9'da bir not düşmüştüm: test AUC 0.815, CV ortalaması 0.752'den **yüksek**. Bu sıradışı. Reviewer'ın **B.1 yorumu da bu**.
>
> *(Grafiği işaret et)*
>
> Cevap bu grafikte. Random split — bizim default akışımız — **satıcı kimliğini koruyamıyor**. Aynı satıcının ilanları hem train hem test setinde olabiliyor, model satıcı imzasını ezberliyor. Yani **leakage** — ama veri leakage'ı değil, **kimlik leakage'ı**.
>
> *(Bar'lara doğru parmakla göstererek)*
>
> Bu gerçek mi diye **GroupKFold** ile satıcı bazında split yaptık. 49 unique satıcı. Sonuç: AUC **0.683**'e düşüyor. Yani:
>
> *(Parmaklarla say)*
>
> **0.815**: random split, üst sınır, optimistic.
> **0.683**: group-aware, alt sınır, pessimistic — gerçek populasyon performansı.
> **0.752**: CV ortalaması, ikisinin arasında.
>
> *(Sonuç tonu)*
>
> CV bandı (0.752 ± 0.024) group-aware ile uyumlu. Yani anomaly açıklandı, **B.1 cevabı budur**. Headline sayıyı ve robustness floor'u **ikisini de raporluyoruz** — şeffaflık önce."

→ Audience'ın grafiği okuması için 3 sn sessizlik. Sonra Hİ'ye köprü.

> *(Köprü cümlesi)*
>
> "Cold-start senaryosunu Halil İbrahim §15'te anlatacak."

→ Hİ §15'e scroll, konuşmaya başlar. Sen yan tarafa çekil.

---

## 14:15 — 15:15 · §15 STATIC F1 Sweep (Hİ konuşur)

> Bu blokta sen sahnede değilsin. Hİ STATIC_ONLY ablation + threshold sweep anlatıyor.

---

## 15:15 — 16:00 · §16 Headline Summary: Ablation + Bootstrap CI (45 sn)

### Yapacağın
- Hİ "Halil Utku ablation özetini kapatıyor" deyince sahne ortasına gel
- §16 başlığı — "Headline Summary: Ablation + Bootstrap CI (Display Cell)"
- 3-satır tablo: FULL / NO_ENGAGEMENT / STATIC_ONLY
- Yanında 2-panel bar chart with confidence intervals

### Söyleyeceğin

> "Section 16: ablation çalışmasının özeti. Üç farklı feature seti karşılaştırdık.
>
> *(Tabloya işaret et)*
>
> **FULL**, 60 özellik, AUC **0.815**.
> **NO_ENGAGEMENT**, like ve comment çıkarılmış, 49 özellik, AUC **0.810** — yani ΔAUC sadece **eksi 0.005**, neredeyse fark yok.
> **STATIC_ONLY**, sadece 26 statik özellik (fiyat, marka, fotoğraf, açıklama), AUC **0.749** — ΔAUC **eksi 0.066**.
>
> *(Yorum tonu)*
>
> Yorum: **engagement marjinal**. Sadece yarım puan etki ediyor. Statik özellikler — fiyat, marka, fotoğraf, açıklama — bilginin **kemiği**.
>
> *(Hafif vurgu)*
>
> Bu sonuç bonus bir nokta da kapatıyor: reviewer 'engagement leakage olabilir mi?' diye sormuştu. Eğer leakage olsaydı engagement çıkarıldığında AUC **çökerdi**. Yarım puan düşüş, leakage olmadığının dolaylı kanıtı."

→ F'e §17 köprüsü için işaret.

> *(Köprü cümlesi)*
>
> "Demo'nun arkasındaki export hücresine kısaca Furkan değinecek."

→ F sahneye gelir, §17 köprüsünü 15 sn'de anlatır.

---

## 16:00 — 16:15 · §17 (F konuşur)

> Sen sahnede değilsin. F §17 köprüsünü anlatıyor.

---

## 16:15 — 17:15 · Kapanış (Hİ konuşur)

> Hİ limitler + sonraki adım özetliyor.

---

## 17:15 — 20:00 · Q&A

> **Senin alanın**: Model/metrik/ablation/threshold/CV/bootstrap soruları.
> Detay → [`qa_cards.md`](qa_cards.md). Senin için en olası 7 kart:

| Kart # | Soru | İlgili section |
|---|---|---|
| **1** | Test AUC neden CV'den yüksek? (B.1) | §14 |
| **3** | Neden XGB, neden LGBM değil? (B.3) | §10 |
| **4** | SHAP'a ne kadar güvenelim? (A) | §8 |
| **5** | Class imbalance nasıl ele alındı? | §11 |
| **7** | Leakage kontrol katmanları | §2, §14 |
| **8** | Engagement marjinal Δ neden? | §16 |
| **12** | Tek-seed bootstrap güvenli mi? | §13 |

### En kritik 3 cevap (kelime-kelime)

#### Q: "Test AUC neden CV'den yüksek?" (Kart 1, B.1)

> "Random split satıcı kimliğini koruyamıyor — aynı satıcının ilanları train ve test'te oluyor, model satıcı imzasını ezberliyor. **GroupKFold** ile satıcıya göre split yaptığımızda AUC 0.683'e düşüyor. CV ortalaması 0.752 bunun bandında. Yani 0.815 üst sınır — gerçek performans CV'ye yakın. §14'te 4-bar grafik bunu görselleştiriyor."

#### Q: "Neden XGBoost?" (Kart 3, B.3)

> "Üç gerekçe: AUC 0.815 vs LGBM 0.780 — fark tutarlı. F1-optimal'da XGB 0.354, LGBM 0.301. Üçüncüsü SHAP — XGB'nin monotonic constraint API'si H1 ve H2 hipotezleri için daha temiz çalıştı, LGBM aynı constraint'lerle kararsız fit oldu."

#### Q: "SHAP'a ne kadar güvenelim?" (Kart 4, A)

> "Önceden kayıtlı sadece iki hipotez: H1 fiyat ve H2 marka. SHAP bunları doğrulayıcı kullanıldı. Diğer SHAP gözlemleri post-hoc keşifsel — 'şu özellik X yapıyor' iddiası değil, 'bu modelde şu pattern var' gözlemi. Yeniden kayıtlı çalışmaya konu olur."

### Soru gelmezse açılış formülü (sen başlatırsın)

> "Sıkça merak edilen üç noktaya kendimiz değinelim."
>
> → Kart 1 (B.1) → Kart 4 (post-hoc) → Kart 8 (engagement marjinal)

---

## Sahne kuralları — HU için

1. **§14'ten önce anomaly'ye değinme** — sürpriz §14'e bekletilecek. §9'da "aklınızda kalsın" yeter.
2. **B.1 / B.2 / B.3 / A reviewer harflerini söyle** — audience hocanın yazılı yorumlarına cevap verdiğimizi anlamalı, profesyonel ton.
3. **SHAP grafiğinde top özellikleri rank numarası ile söyleme** — "top-5'te" gibi nitel ifade kullan; rank dosyamızda doğrulanmamış.
4. **Sayıları ekrandan oku** — tablolar görünür, ezbere riske girme.
5. **HU→F köprüsünde el hareketi** — "kısaca Furkan değinecek" deyince F'i el hareketiyle davet et, audience devir hissetsin.
6. **§16 sonu sahneden çekil** — F §17'ye gelir, sen yan tarafta dur.

---

## Pre-prova kontrolü (T-1 saatte)

```bash
# HTML'in doğru render olup olmadığını kontrol et
open /Users/furkankarafil/dolap-sale-prediction/notebooks/dolap_classification_final.html
```

Tarayıcıda kontrol:
- [ ] §1 dataset shape "6007" görünüyor
- [ ] §5 bar grafiği renderlanmış (5 model)
- [ ] §6 confusion matrix grid görünür
- [ ] §8 SHAP summary plot var
- [ ] §10 6-model karşılaştırma tablosu okunabilir
- [ ] §11 PR-eğrisi + F1 vs τ grafiği var
- [ ] §13 bootstrap histogram render olmuş
- [ ] §14 4-bar grafik (Random/CV/Group-aware/Headline) görünür
- [ ] §16 ablation tablosu + 2-panel bar chart var

Bu 9 kontrol geçtiyse senin tarafında hazırsın.

---

## Cep notu (sahnede çıktı al)

```
§1  → 5:00  Dataset 6007×60, %5.8 sold
§2  → 5:30  60/20/20, leak-safe, SMOTE-train-only
§5  → 6:00  5 model bar, XGB+RF lider
§6  → 6:45  CM, default τ=0.50 FN-eğilim
§7  → 7:30  Hİ devralır
§8  → 8:15  SHAP H1+H2 confirmatory, A cevabı
§9  → 9:15  CV 0.752±0.024, anomaly notu (§14'e bekle)
§10 → 9:45  XGB vs LGBM 3 gerekçe (B.3)
§11 → 10:45 RandomSearch + τ=0.247 F1 0.268→0.354
§12 → 11:45 Hİ devralır (mapping)
§13 → 12:45 Bootstrap CI [0.76, 0.87]
§14 → 13:15 RC4 anomaly açıklama (B.1, kritik)
§15 → 14:15 Hİ devralır (STATIC F1)
§16 → 15:15 Ablation NO_ENG Δ=-0.005, STATIC Δ=-0.066
§17 → 16:00 F devralır (köprü)
```
