# Notebook Sunum Konuşma Metni — 17 Section, Sahnede Okunacak (MASTER)

> **Bu dosya = unified overview**. 3 üye için ayrı detaylı script'ler:
>
> - **F (Furkan)** → [`script_furkan.md`](script_furkan.md) + [`script_demo_detailed.md`](script_demo_detailed.md)
> - **HU (Halil Utku)** → [`script_halil_utku.md`](script_halil_utku.md)
> - **Hİ (Halil İbrahim)** → [`script_halil_ibrahim.md`](script_halil_ibrahim.md)
>
> Her üye **kendi script'inden** sahneye çıksın — bu master dosya prova ve genel akış için.

> **Hedef**: `notebooks/dolap_classification_final.html` (kod-gizli HTML export). Sunum gün açılacak dosya bu, notebook'un kendisi değil. Demo `127.0.0.1:5000` ayrı tab'da açık.
>
> **Format**: Her section için → **(1)** Ne göstereceğin (HTML'de ne scroll etmen lazım), **(2)** Söyleyeceğin metin (sahnede ad-lib edilebilir, ezbere gerek yok), **(3)** Kim konuşur, **(4)** Süre. EDA tarafı (Section 1–7) hocanın yönergesine göre **hızlı geçilecek** ("EDA'yı tekrar anlatmayın"); model kararları (Section 8–17) detay anlatılacak.
>
> **Toplam süre hedefi**: 5 dk Demo + 10 dk Notebook (§1–§17) + 5 dk Q&A = 20 dk

---

## Görev Dağılımı

| Üye | Sahne süresi | Anlatacağı section'lar |
|---|:---:|---|
| **F (Furkan)** | 5 dk demo + 1 dk §17 köprü | Demo (Tab 1) → §17 köprü cümlesi |
| **HU (Halil Utku)** | ~6 dk | §1–§2 (veri/preprocess) → §5–§6 (model karşılaştırma) → §8–§11 (deep dive + tuning) → §13–§14 (CI + robustness) → §16 (ablation özet) |
| **Hİ (Halil İbrahim)** | ~4 dk | §7 (ROC/PR yorumu) → §12 (reviewer mapping) → §15 (STATIC F1) → limitler/sonuç |

> Her üye en az 4 dk sahnede + Q&A'da kendi alanı → hocanın "Her grup üyesinin katkısı görünür olmalıdır" şartı karşılanır.

---

# 0:00 — 5:00 · LIVE DEMO (F, Tab 1 = Tarayıcı http://127.0.0.1:5000)

> Demo bloğu için ayrıntı: [`presentation_run_sheet.md`](presentation_run_sheet.md). Özetle: 8 preset + τ slider + 1 manuel edit. Bittiğinde:
>
> **F geçiş cümlesi**: *"Modelin nasıl davrandığını gördünüz; şimdi bu sayıların nasıl üretildiğini Halil Utku'ya bırakıyorum. Ben tarayıcıdan notebook'a geçiyorum — section 17'ye, demo'nun arkasındaki export hücresine."*

→ F **Cmd+Tab** ile Tab 2'ye geçer (HTML), **§17'ye scroll** eder, sahneyi HU'ya devreder.

---

# 5:00 — 15:00 · NOTEBOOK BLOĞU (HTML üzerinden, Tab 2)

## Section 1 — Setup & Data Loading [HU, 30 sn]

**Göster**: §1 sonu, dataset shape çıktısı (6,007 satır × 60 feature) + class dağılımı (94.2% / 5.8%).

**Söyle**:
> "Veri seti **6,007 ilan**, 60 mühendislik özelliği. Pozitif sınıf %5.8 — yani her 17 ilandan biri 7 günde satıyor. Bu imbalance modelleme kararlarımızı şekillendiriyor: SMOTE, F1-tabanlı eşik, bootstrap CI."

→ Hızla §2'ye scroll.

---

## Section 2 — Preprocessing & Train/Test Split [HU, 30 sn]

**Göster**: train/val/test boyutları + class dağılımı tablosu.

**Söyle**:
> "Stratified random split 60/20/20. Imputer + scaler **leak-safe pipeline** içinde — train fit ediliyor, val/test sadece transform. SMOTE de sadece train fold'unda. Headline'ımız bu split üzerinden — §14'te group-aware versiyonunu da göreceğiz."

→ §3, §4'ü atla, **§5'e scroll**.

---

## Section 3 — Model Training [SES VERME, scroll geç]

> Sahnede zaman kaybı. Modeller §5'teki tabloda zaten görünüyor.

---

## Section 4 — Evaluation Metrics Explained [SES VERME, scroll geç]

> Pedagojik içerik (Accuracy/Precision/Recall/F1/AUC tanımları). Hocanın yönergesi "metric tanımı tekrarı" istemiyor.

---

## Section 5 — Visual Model Comparison [HU, 45 sn]

**Göster**: 5 modelin (LR / KNN / DT / RF / XGB) AUC + F1 bar grafiği.

**Söyle**:
> "5 baseline + 2 gradient-boosting karşılaştırdık. Görsel sıralama: XGBoost en yüksek AUC, ardından RandomForest. Logistic Regression ve KNN imbalance altında zayıf — bu beklenen sonuç. Detay tablo §10'da."

→ §6'ya scroll.

---

## Section 6 — Confusion Matrices [HU, 45 sn]

**Göster**: 5 modelin confusion matrix grid'i.

**Söyle**:
> "Default τ=0.50'de tüm modeller pozitif sınıfa eğilimli kayıp veriyor — false negative oranı yüksek. Bu, eşik optimizasyonunu §11'de niye yaptığımızın doğrudan sebebi. **Hocanın 'hangi örneklerde hata yapıyor' sorusuna** ek olarak demo'da `hard_negative_FP` ve `hard_positive_FN` preset'leri ile somut iki vakayı zaten gösterdik."

→ §7'ye scroll.

---

## Section 7 — ROC & Precision-Recall Curves [Hİ, 45 sn]

**Göster**: ROC eğrileri + PR eğrileri yan yana.

**Söyle (Hİ)**:
> "ROC AUC için 5 model arasında XGBoost ve LightGBM ön planda. Ama imbalance altında **precision-recall eğrisi daha bilgilendirici**: rastgele tahminin baseline'ı %5.8, modelimiz bunu çok aşıyor. PR-AUC üzerinden de XGBoost lider."

→ §8'e scroll.

---

## Section 8 — Best Model Deep Dive [HU, 1 dk]

**Göster**: XGBoost classification report + confusion matrix + SHAP summary plot.

**Söyle**:
> "Seçilen model XGBoost. Classification report: precision 0.48, recall 0.19 — default eşikte recall düşük. SHAP grafiği H1, H2, H3, H4 hipotezlerini **post-hoc confirmatory** olarak destekliyor: fiyat pozisyonu (H1) negatif yön, marka kademesi (H2) pozitif yön, engagement (H3) pozitif, satıcı deneyimi (H4) pozitif."

> "**Bu önemli not**: hipotezler önceden kayıtlı **iki tane** — H1 ve H2. Diğer SHAP gözlemleri post-hoc keşifsel; **A reviewer yorumuna cevap budur**."

→ §9'a scroll.

---

## Section 9 — Cross-Validation [HU, 30 sn]

**Göster**: 5-fold CV AUC sonuçları (mean=0.7517 ± 0.0239).

**Söyle**:
> "5-fold stratified CV. Ortalama AUC 0.752, standart sapma 0.024. **Burada bir not**: test AUC 0.815, CV ortalaması 0.752'den yüksek. Bunun açıklaması §14'te — şimdilik aklınızda kalsın."

→ §10'a scroll.

---

## Section 10 — Final Model Selection [HU, 1 dk]

**Göster**: 6-model karşılaştırma tablosu (XGBoost + LightGBM + 4 baseline).

**Söyle**:
> "XGBoost final model. **B.3 reviewer sorusu — neden LightGBM değil**: üç gerekçe. (1) Test AUC: XGBoost 0.815, LightGBM 0.780 — fark 0.035, küçük değil. (2) Bootstrap CI %95'leri ayrık değil ama mean farkı tutarlı. (3) SHAP monotonic constraints API'si XGBoost'ta H1/H2 hipotezleri için daha temiz çalıştı. Ablasyon tek-seed olduğundan multi-seed bootstrap'a gelecek çalışma listesinde — methodology_addendum.md Bölüm 9.X'te bu argüman tam yazılı."

→ §11'e scroll.

---

## Section 11 — Hyperparameter Tuning + Threshold Optimization [HU, 1 dk]

**Göster**: RandomizedSearchCV best params + PR-eğrisi + F1 vs τ grafiği.

**Söyle**:
> "RandomizedSearchCV 50 iter × 5-fold, **SMOTE pipeline içinde** — her fold kendi SMOTE'unu fit ediyor, leakage yok. Best params: n_estimators=300, max_depth=5, learning_rate=0.05."

> "**Threshold story**: Default τ=0.50'de F1=0.268. PR-eğrisi sweep'inde F1 maksimum yapan τ=**0.247**, F1=0.354. **%32 iyileşme** — recall'u 0.19'dan 0.32'ye çıkardı. Demo'da slider'da bu eşiği gösterdim."

→ §12'ye scroll.

---

## Section 12 — Key Takeaways + Reviewer Mapping [Hİ, 1 dk]

**Göster**: §12'deki reviewer mapping tablosu (1. tur 4 + 2. tur 4 yorum).

**Söyle (Hİ)**:
> "Bu tablo hocanın iki tur feedback'ini tek tek hangi notebook §'sinde nasıl ele aldığımızı gösteriyor. **1. tur**: bootstrap CI (§13), threshold optimization (§11), Reviewer Comment 4 robustness check, post-hoc SHAP framing (§3 hipotez kaydı + §8 confirmatory analiz). **2. tur**: A — post-hoc framing (§3, §8 dipnot), B.1 — test>CV anomaly (§14), B.2 — STATIC_ONLY F1 (§15), B.3 — XGB vs LGBM (§10). 8 yorum, 8 satır, hepsinin notebook karşılığı var."

> "Detayı `methodology_addendum.md` Bölüm 8.A–8.D, 8.W, 8.Y.1, 8.Z, 9.X'te uzun formda yazılı, hocanın mailine ek olarak gönderildi."

→ §13'e scroll.

---

## Section 13 — Bootstrap Confidence Intervals [HU, 30 sn]

**Göster**: 200-resample bootstrap çıktısı + histogram.

**Söyle**:
> "200 resample ile %95 GA: AUC = 0.815 [0.7613, 0.8722], genişlik ~0.06. Sayı tek-noktasal değil; CI'lı raporluyoruz."

→ §14'e scroll.

---

## Section 14 — Robustness Check (RC4): Test > CV Anomaly [HU, 1 dk]

**Göster**: 4-bar grafik (Random / CV / Group-aware / Headline) + RC4 protokol tablosu.

**Söyle (kritik bölüm — yavaş anlat)**:
> "Reviewer'ın **'Test AUC neden CV'den yüksek?'** sorusunun cevabı bu grafikte. Random split satıcı kimliğini koruyamıyor — aynı satıcının ilanları hem train hem test'te oluyor, model satıcı imzasını ezberliyor. **GroupKFold**'u satıcı bazında çalıştırdığımızda AUC **0.683**'e düşüyor."

> "Yorum: 0.815 **üst sınır** (random split, optimistic), 0.683 **alt sınır** (group-aware, pessimistic), CV ortalaması 0.752 ikisinin arasında. **B.1 cevabı budur** — anomaly açıklandı, ikisini de raporluyoruz."

→ Audience grafiği okuyana kadar 3 sn sessizlik. Sonra §15'e scroll.

---

## Section 15 — STATIC_ONLY Cold-Start: Threshold Optimization [Hİ, 1 dk]

**Göster**: STATIC_ONLY PR-eğrisi + F1 vs τ sweep.

**Söyle (Hİ)**:
> "Reviewer'ın **B.2** sorusu STATIC_ONLY F1 üzerine. Cold-start ilanlarda engagement yok — like, comment sıfır. Bu durumda 26 statik özellik kalıyor."

> "Sonuç: AUC **0.749**, default τ=0.50'de F1=0.110 — düşük. Ama **PR-eğrisi sweep'inde τ=0.18'de F1 0.215'e çıkıyor — iki katı**. Yani cold-start için **ayrı eşik** kullanmak makul. Demo'da bu eşiği slider ile gösterdik."

→ §16'ya scroll.

---

## Section 16 — Headline Summary: Ablation + Bootstrap CI [HU, 1 dk]

**Göster**: 3-satır tablo (FULL / NO_ENGAGEMENT / STATIC_ONLY) + 2-panel bar chart with CI.

**Söyle**:
> "Üç feature seti karşılaştırıldı: **FULL** 60 özellik AUC=0.815, **NO_ENGAGEMENT** 49 özellik AUC=0.810 (ΔAUC sadece **−0.005**), **STATIC_ONLY** 26 özellik AUC=0.749 (ΔAUC=**−0.066**)."

> "Yorum: engagement marjinal — sadece 0.5 puan düşürüyor. Statik özellikler (fiyat, marka, fotoğraf, açıklama) bilginin kemiği. Bu reviewer'ın 'engagement leakage olabilir mi?' endişesini dolaylı olarak da kapatıyor — leakage olsaydı engagement çıkarılınca AUC çökerdi."

→ §17'ye scroll.

---

## Section 17 — Export Trained Model for Live Demo [F köprü cümlesi, 15 sn]

**Göster**: §17 hücresinin son satırları — `[ok] schema saved`, `presets : 10`, `[self-test] sample probability(sold) = 0.xxx`.

**Söyle (F bu kısımda kısaca girer)**:
> "Bu hücre demo'da kullandığımız `models/dolap_xgboost_pipeline.joblib` ve `feature_schema.json` dosyalarını üretiyor. Yani **demo'daki canlı tahminler ile §16'daki ablation sayıları aynı modelden** — tutarlı hikaye."

→ Hİ devralır → kapanış bloğuna geç.

---

# 15:00 — 17:00 · KAPANIŞ: Limitler + Sonraki Adım [Hİ, 2 dk]

> Notebook scroll'u bittiğinde HTML'in sonunda kalın. `methodology_addendum.md`'i ayrı bir tab'da açabilirsin — ama gerek yok, sözlü özet yeterli.

**Söyle (Hİ)**:
> "Üç limit kabul ediyoruz. **Birinci**: 49 unique satıcı — group-aware analizler için yeterli ama populasyon-üstü iddialar için değil. **İkinci**: tek platform — Vinted/Depop validasyonu yok. **Üçüncü**: ablasyon tek-seed; multi-seed bootstrap planlı."

> "Sonraki adımlar: cohort genişletme (200+ satıcı), cross-platform validasyon, fairness audit. Veri Bilimi Dergisi makale taslağı (`reports/article_draft_en.md`) reviewer mapping ekiyle hazır, sunum sonrası finalize."

> "Sorulara açığız."

→ Q&A başlar (15:00–20:00). Sorular kime gelirse 3'ümüzden uygun olan cevaplar (`reports/qa_cards.md` 15 kart hazır).

---

# Sahne kuralları (3 üye için)

1. **HTML kullan, notebook'un kendisi değil** — JS sorunu olmaz, kod tamamen gizli, render hızlı.
2. **Sayıları ekrandan oku** — hafızadan değil. Tablolar HTML'de, görünür.
3. **§14'ten önce "Test 0.815'i" söylerken anomaly'ye değinme** — §14'te grafikle birlikte tek seferde anlatılır.
4. **Geçişlerde köprü cümlesi**: F→HU "modelin neden böyle davrandığını HU açıklayacak", HU→Hİ "reviewer mapping ve limitleri Hİ özetleyecek".
5. **Donma anında**: HTML statik, render kayıtlı — refresh yapma. Demo donarsa F notebook §17'den `run_preset("sold_high_conf")` çalıştırır (FALLBACK_PLAN.md Tier-1).

---

# Pre-prova kontrol (her üye T-1 saatte)

| Kim | Kontrol |
|---|---|
| F | Demo lokal makinede çalışıyor → `127.0.0.1:5000` → 10 preset render |
| F | HTML açılıyor → `open notebooks/dolap_classification_final.html` → 17 section görünüyor |
| HU | §1, §5, §10, §11, §13, §14, §16 hücreleri çıktılı; tablolar okunabilir font |
| Hİ | §7, §12, §15 grafikleri görünür, reviewer mapping tablosu satır-satır oku |
| Hİ | `methodology_addendum.md` PDF kopyası USB'de + bulut yedek |

---

## Run-sheet'e bağlanma

Bu metin notebook bloğunu (5:00–15:00) kapsar. Demo bloğu (0:00–5:00) ve Q&A bloğu (15:00–20:00) için → [`presentation_run_sheet.md`](presentation_run_sheet.md). Q&A için → [`qa_cards.md`](qa_cards.md).
