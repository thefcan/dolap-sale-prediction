# Notebook Sunum Metni — Classification + Ablation

> **Hedef notebooks**: `notebooks/dolap_classification_final.ipynb` ve `notebooks/dolap_ablation_study.ipynb`. EDA notebook'u (`Dolap_EDA_Feature_Engineering.ipynb`) önceki sunumda anlatıldı, bu blokta sadece referans verilecek (tekrar açılmayacak).
>
> Bu metin **run-sheet'in 5:00–10:00 "Model Kararları" bloğunu** detaylandırır. Dakika dakika kim ne diyecek, hangi hücrede ne gösterilecek, geçişler nasıl olacak.
>
> **Kural**: Her hücre için "AÇ → SÖYLE → GEÇ" — kod hücresinin çıktısı görünür, kod gizli (toolbar'daki "Hide Code" aktif).

---

## Görev dağılımı (3 üye × ~5 dk konuşma + Q&A payı)

| Üye | Sahne süresi | Sorumluluk | Notebook bölümleri |
|---|---|---|---|
| **Furkan (F)** | 5 dk demo + 1 dk notebook geçişi | Live demo, §17 export hücresi (demo'ya köprü), τ slider hikayesi | classification §17 + demo |
| **Halil Utku (HU)** | ~6 dk model kararları | Veri/preprocess/train/CV/threshold/ablation/SHAP — modelleme omurgası | classification §1–2, §10–11, §13, §14, §16, ablation tüm | 
| **Halil İbrahim (Hİ)** | ~4 dk yorum & limitler | Reviewer mapping, robustness yorumu, STATIC_ONLY cold-start, post-hoc framing, sonraki adım | classification §12, §15, methodology_addendum.md |

> **Profesör notu**: "Her grup üyesinin katkısı sunumda görünür olmalıdır." Üçü de hem teknik bir blok hem Q&A'da kendi alanını alıyor — minimum 4 dk per üye + 5 dk Q&A.

---

## Notebook açılış (T-0, F yapar — 30 sn)

> Notebook ilk açıldığında üst çubukta toolbar görünür: **"Hide Code" aktif**. Audience kod görmüyor, sadece markdown başlıkları + grafik çıktıları + tablolar.

**F (söylenecek)**:
> "Notebook'u sunum modunda açıyorum — kod gizli, çıktılar açık. 17 bölüm var, bugün modelin nasıl seçildiğine ve reviewer feedback'ine nasıl cevap verdiğimize odaklanacağız."

→ Furkan demo bittiğinde sayfayı **§17'ye scroll** ederek HU'ya devreder ("İşte demo'da kullandığımız `joblib` artefaktının üretildiği hücre — buradan başlayalım").

---

## BLOK A — Veri ve Preprocessing (HU, ~60 sn)

### §1 — Setup & Data Loading

**Göster**: §1 sonu, `df.shape` ve `df['sold_within_7_days'].value_counts()` çıktısı.

**HU söyleyecek**:
> "6,007 ilan, 60 mühendislik özelliği. Pozitif sınıf %5.8 — yani her 17 ilandan biri 7 günde satıyor. Bu seviyedeki imbalance modelleme kararlarımızı şekillendiriyor: SMOTE, F1-tabanlı eşik, bootstrap CI."

### §2 — Preprocessing & Train/Test Split

**Göster**: train/val/test boyutları + class dağılımı tablosu.

**HU söyleyecek**:
> "Stratified random split 60/20/20. Imputer + scaler **leak-safe pipeline** içinde — train fit ediliyor, val/test sadece transform. SMOTE de sadece train fold'unda. Headliner sayımız bu split üzerinden — §14'te group-aware versiyonunu da göreceğiz."

**Geçiş cümlesi**: *"Şimdi 5 model arasında neyi seçtiğimize bakalım."*

---

## BLOK B — Model Seçimi (HU, ~90 sn)

### §10 — Final Model Selection

**Göster**: 5 modelin AUC/F1 karşılaştırma tablosu (LR / KNN / DT / RF / XGB / LGBM).

**HU söyleyecek**:
> "Beş aday model + iki gradient boosting. Test AUC sıralaması: XGBoost 0.815, LightGBM 0.812, RandomForest 0.79. XGB'yi seçtik — fark küçük ama üç gerekçe var, B.3 reviewer sorusuna birazdan döneceğiz."

### §11 — Hyperparameter Tuning

**Göster**: best params + RandomizedSearchCV CV AUC (0.752 ± 0.024).

**HU söyleyecek**:
> "RandomizedSearchCV 50 iterasyon, 5-fold stratified. SMOTE pipeline içinde — search'in her fold'u kendi SMOTE'unu fit ediyor, leakage yok. CV AUC 0.752 ± 0.024."

> **🔴 Tuzak uyarısı (HU içeriden bilmeli)**: Audience hemen "Test 0.815 nasıl CV 0.752'den yüksek?" diye düşünebilir. HU önden bahsetmiyor, §14'te **kanıtlı** açıklayacak.

### §11 sonu — Threshold optimization

**Göster**: PR-eğrisi + F1 vs τ grafiği.

**HU söyleyecek**:
> "Default τ=0.50'de F1=0.268, F1-maksimum eşik τ=0.247'de 0.354. %32 iyileşme — recall'u korurken precision'ı düşürüyor. Live demo'da bu eşiği slider olarak gördünüz."

**Geçiş cümlesi**: *"Bu sayıların ne kadar sağlam olduğuna bakalım."*

---

## BLOK C — Robustness ve Anomaly (HU, ~90 sn)

### §13 — Bootstrap Confidence Intervals

**Göster**: 200-resample bootstrap çıktısı (AUC 0.815 [0.7613, 0.8722]).

**HU söyleyecek**:
> "200 resample ile %95 GA: 0.761–0.872, genişlik ~0.06. Sayı tek-noktasal değil."

### §14 — Robustness Check: Seller-Identity Leakage (RC4)

**Göster**: 4-bar grafik (Random / CV / Group-aware / Headline) + tablo.

**HU söyleyecek (B.1 cevabı)**:
> "Reviewer'ın 'Test AUC neden CV AUC'dan yüksek' sorusunun cevabı bu grafikte. Random split satıcı kimliğini koruyamıyor — aynı satıcı hem train hem test'te oluyor, model satıcı imzasını ezberliyor. **GroupKFold satıcıya göre** çalıştırdığımızda AUC 0.683'e düşüyor. CV bandı (0.752 ± 0.024) ile group-aware uyumlu. Yani 0.815 üst sınır, 0.683 alt sınır — ikisini de raporluyoruz."

**Burada bekle**: Audience grafiği okuyana kadar 3-4 sn sessizlik. Sonra **geç**.

**Geçiş cümlesi**: *"Şimdi 60 özelliği parçalara ayıralım — hangisi gerçekten iş yapıyor?"*

---

## BLOK D — Ablation Study (HU, ~90 sn)

> **Notebook değişikliği**: Burada `dolap_classification_final.ipynb` §16'yı göster, ana sayıları orada zaten render ediyor (`reports/ablation_results.json` üzerinden okur). Detayı sorulursa `dolap_ablation_study.ipynb`'e geç.

### §16 — Headline Summary: Ablation + Bootstrap CI

**Göster**: 3-satır tablo (FULL / NO_ENGAGEMENT / STATIC_ONLY) + 2-panel bar chart (CI'lı).

**HU söyleyecek**:
> "Üç set: tüm 60 özellik, engagement çıkarılmış (49 özellik), sadece statik (26 özellik). FULL AUC=0.815, NO_ENGAGEMENT 0.810 — ΔAUC sadece −0.005. Yani engagement marjinal; statik özellikler (fiyat, marka, fotoğraf, açıklama) bilginin omurgası. STATIC_ONLY'de AUC 0.749'a düşüyor — ΔAUC −0.066, modelin gerçekten kullandığı katma değer."

### Eğer ablation detay sorulursa → `dolap_ablation_study.ipynb`

**Göster**: ablation notebook'unda `train_xgb` fonksiyonu + tam tablo.

**HU söyleyecek (sadece sorulursa)**:
> "Ablation notebook bağımsız bir runner — aynı XGB hiperparametreleriyle üç set ardışık eğitiyor, markdown tablosunu makaleye yapıştırılabilir formatta basıyor. Sonuçlar `reports/ablation_results.json`'a yazılıyor, classification notebook §16 oradan okuyor — yani iki notebook arasındaki sayılar her zaman senkron."

**Geçiş cümlesi**: *"Engagement-zayıf cold-start ilanlar için ne yapıyoruz, Halil İbrahim anlatacak."*

---

## BLOK E — Cold-Start ve Yorum (Hİ, ~120 sn)

### §15 — STATIC_ONLY Cold-Start: Threshold Optimisation

**Göster**: STATIC_ONLY PR-eğrisi + F1 vs τ sweep.

**Hİ söyleyecek (B.2 cevabı)**:
> "Reviewer'ın STATIC_ONLY F1 sorusu: cold-start ilanlarda engagement yok, ama yine de doğru kararlar gerekli. Statik-only sette F1 default τ=0.50'de 0.110 — düşük. Ama PR-eğrisi sweep'inde τ=0.18'de F1 0.215'e çıkıyor, **iki katı**. Yani cold-start için **ayrı eşik** kullanmak makul; B.2'nin cevabı bu."

### §12 — Key Takeaways + Reviewer Mapping

**Göster**: §12 reviewer mapping tablosu (1. tur 4 yorum + 2. tur 4 yorum).

**Hİ söyleyecek**:
> "Reviewer feedback'i iki turda toplam 8 yorum. Tablonun her satırında hangi yorumun hangi notebook §'sinde nasıl ele alındığı listeli. A — SHAP post-hoc framing §3 hipotez kaydı + §13 başlığında işaretli. B.1 — §14 RC4 grafiği. B.2 — §15 sweep. B.3 — §10 model seçim tablosu + §6 (manuscript) 3 gerekçe. 1. turun 4 maddesi `methodology_addendum.md` bölüm 8.A–8.D'de uzun formda."

**Geçiş cümlesi**: *"Limitler ve sonraki adımları özetleyelim."*

---

## BLOK F — Limitler ve Sonraki Adım (Hİ, ~60 sn)

> **Notebook değil, slayt veya sözlü**. `methodology_addendum.md` özet sayfası kullanılabilir.

**Hİ söyleyecek**:
> "Üç limit: (1) 49 unique satıcı — group-aware analizler için minimum yeterli, populasyon-üstü iddialar için değil. (2) Tek platform — Vinted/Depop validasyonu yok. (3) Ablasyon tek-seed; multi-seed bootstrap planlı. Sonraki adımlar: cohort genişletme, cross-platform, fairness audit. Veri Bilimi Dergisi makale taslağı (`article_draft_en.md`) reviewer mapping ekiyle hazır, sunum sonrası finalize."

**Bitiriş**: *"Soruları üçümüz panel olarak alacağız."* → Q&A.

---

## §17 — F'in demo'ya köprü hücresi (sadece referans, sahnede 5 sn)

> Aslında F en başta demo'yu burayla açtı. HU'ya devirken "Demo arkasındaki bu hücre, modeli `models/dolap_xgboost_pipeline.joblib` olarak kaydediyor — Halil Utku'nun anlatacağı tüm sayılar buradan akıyor" demesi yeterli. Tekrar açılmıyor.

---

## Sahne kuralları (üçü için)

1. **Hide Code aktif kalsın** — kod hücresine geçilirse kararlı kalmıyor; HU bir hücreyi merak ettirirse "isterseniz Q&A'da kodu açarız" der.
2. **Sayı söylerken not gösteriyor** — eski/güncel karışmasın diye HU her sayıyı **ekrandaki çıktıdan** okur, hafızadan değil.
3. **B.1 anomaly tek seferde söylenir, §14'te** — daha öncesinde "Test 0.815'i" söylerken anomaly'ye değinmeyin, audience kafası karışır. §14'te grafikle birlikte anlatılır.
4. **Geçişlerde adı geçeni el hareketiyle göster** ("Halil Utku şimdi …") — projektörden bakarken kim sıradaki belli olsun.
5. **Hücre yüklenmiyorsa** — `Run All` ile gelmiş çıktılar kayıtlı, kernel donsa bile çıktılar görünür kalır. Restart **YAPMAYIN**.

---

## Run-sheet'e bağlanma noktası

Bu metin run-sheet'in **5:00–10:00 (HU)** + **10:00–15:00 (Hİ)** bloklarını dakika dakika açıklar. Demo bloğu (0:00–5:00) için → [presentation_run_sheet.md](presentation_run_sheet.md). Q&A için → [qa_cards.md](qa_cards.md).

---

## Pre-prova kontrol (her üye T-1 saatte yapsın)

| Kim | Kontrol |
|---|---|
| F | Demo lokal makinede çalışıyor (`python demo/demo_server.py` → tarayıcı 5000) |
| HU | Notebook §1, §10, §11, §13, §14, §16 hücreleri çıktılı, "Hide Code" mode aktifken sayılar görünür |
| HU | Ablation notebook ayrı tab'da hazır, sadece §16'dan detay sorulursa açılacak |
| Hİ | §12 reviewer mapping tablosu okunabilir font'ta, §15 PR-curve grafiği bozuk değil |
| Hİ | `methodology_addendum.md` PDF kopya laptop'ta, sözlü sunumda ekrana geçilebilir |
