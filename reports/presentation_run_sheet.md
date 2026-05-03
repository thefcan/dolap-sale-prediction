# Sunum Run-Sheet — 4 Mayıs 2026 (20 dk)

**Format**: 5 dk live demo + 10 dk model kararları (17 section) + 5 dk Q&A
**Ekip**: Furkan (F) · Halil Utku (HU) · Halil İbrahim (Hİ)
**Materyal**:
- Tab 1 → Tarayıcı `http://127.0.0.1:5000/` (live demo)
- Tab 2 → Tarayıcı `notebooks/dolap_classification_final.html` (kod-gizli HTML, 17 section)
- Tab 3 → Terminal (demo server logu, gözardı)

> **Konuşma metni**: [`notebook_presentation_script.md`](notebook_presentation_script.md). Bu run-sheet dakika dakika kim ne yapacak; metnin tamamı orada.

---

## T-30 dk · Sahne öncesi kontrol (3 paralel)

| Kim | Görev |
|---|---|
| F | `source .venv/bin/activate && jupyter nbconvert --to notebook --execute --inplace notebooks/dolap_classification_final.ipynb` — Run All hatasız |
| F | `jupyter nbconvert --to html --no-input notebooks/dolap_classification_final.ipynb` — HTML tazelendi |
| F | `grep -c '"id":' models/feature_schema.json` → **10** olmalı |
| F | `python demo/demo_server.py` → boot logu "Features : 60", "Test AUC : 0.8150" |
| F | Tarayıcı Tab 1 = `127.0.0.1:5000` (10 preset render), Tab 2 = HTML dosyası açık |
| F | "Hızlı satılan" preset → P=%96, τ slider 0.50 → 0.247 → marker hareket eder |
| HU | `reports/methodology_addendum.md` PDF kopya USB + bulut yedek |
| HU | Yedek: `demo/FALLBACK_PLAN.md` ekranda 3. tab olarak hazır |
| Hİ | `qa_cards.md` ve `notebook_presentation_script.md` printed/açık (cep notu) |
| Hİ | Projektör DPI test edildi, font okunuyor, klikleyici çalışıyor |

---

## 0:00 – 5:00 · LIVE DEMO (Furkan, Tab 1)

> Hedef: model çalışıyor olduğunu **göstermek**, sayıyı değil tepkiyi vurgulamak.

| Süre | Aksiyon | Söylenecek |
|---|---|---|
| 0:00–0:30 | Tarayıcıyı aç, başlık satırını oku | "60 özellikli XGBoost — test AUC 0.8150, %95 GA ±0.06. Şimdi modele 10 farklı senaryo göstereceğim." |
| 0:30–1:00 | **Tipik / medyan ilan** preset → Predict | "Medyan ilan ~%2. Platformun gerçek satış oranı %5.8 — yani ortalama ilan ortalamanın altında." |
| 1:00–1:30 | **Hızlı satılan** preset → Predict | "Aynı modelden %96. Aradaki 94 puanlık fark, modelin gerçekten ayırt ettiğini gösteriyor." |
| 1:30–2:15 | **Cold-start** preset → Predict | "like=0, comment=0 — engagement sinyali yok. Buna rağmen %91. §15'teki STATIC-only çalışmasının ana motivasyonu bu." |
| 2:15–2:45 | **Premium / lüks marka** preset | "brand_tier=4, is_known_brand=1 — H2 (marka kademesi) doğrulayıcı analizine doğrudan bağlanıyor." |
| 2:45–3:30 | **Hard-negative (model yanılıyor)** preset | "Bu satılmamış ama model %84 SOLD diyor. Kasıtlı gösteriyorum — modelin kör noktası şeffaf raporlanmalı." |
| 3:30–4:15 | τ slider'ı 0.50 → 0.247 | "F1-optimal eşik. Cold-start gauge'da işaretçi soluna kayıyor — etiket aynı modelle yeniden eğitim yapmadan değişiyor. B.2 reviewer yorumunun cevabı bu." |
| 4:15–4:50 | Filter "price" → 80 TL elle düşür → Predict | "Tek özellik değiştirildiğinde küçük kayma — çünkü price_log/pctile medyanda kalıyor. Preset yaklaşımının gerekçesi bu: 60 özellik tutarlı kalsın diye." |
| 4:50–5:00 | **Cmd+Tab → Tab 2 (HTML)** + geçiş cümlesi | "Modelin nasıl davrandığını gördünüz; şimdi bu sayıların nasıl üretildiğini Halil Utku'ya bırakıyorum. Notebook'a geçiyorum." |

→ HTML'de **§1'in başına scroll** edip HU'ya devret.

---

## 5:00 – 15:00 · NOTEBOOK 17 SECTION (HU + Hİ, Tab 2 HTML)

> Konuşma metnini bu run-sheet tekrar etmiyor — [`notebook_presentation_script.md`](notebook_presentation_script.md)'te section bazlı okuma metinleri var. Bu tabloda dakika dakika "kim, hangi section, ne kadar süre" özetli.

| Süre | Section | Kim | Ne yapacak | Süre detay |
|---|---|---|---|---|
| 5:00–5:30 | §1 Setup & Data Loading | HU | Dataset shape + class dağılımı | 30 sn |
| 5:30–6:00 | §2 Preprocessing & Split | HU | 60/20/20 split, leak-safe pipeline, SMOTE-train-only | 30 sn |
| 6:00 | §3 Training (atla) | — | scroll geç | 0 |
| 6:00 | §4 Metrics Explained (atla) | — | scroll geç | 0 |
| 6:00–6:45 | §5 Visual Comparison | HU | 5-model AUC + F1 bar grafiği | 45 sn |
| 6:45–7:30 | §6 Confusion Matrices | HU | Default τ=0.50 FN-eğilimi → §11 motivasyon | 45 sn |
| 7:30–8:15 | §7 ROC & PR Curves | **Hİ** | Imbalance altında PR daha bilgilendirici | 45 sn |
| 8:15–9:15 | §8 Best Model Deep Dive | HU | XGBoost classification report + SHAP H1–H4 + **A reviewer post-hoc framing** | 1 dk |
| 9:15–9:45 | §9 Cross-Validation | HU | CV AUC 0.752±0.024, **§14'e işaret** | 30 sn |
| 9:45–10:45 | §10 Final Model Selection | HU | XGB vs LGBM 3 gerekçe (**B.3 cevabı**) | 1 dk |
| 10:45–11:45 | §11 Hyperparameter + Threshold | HU | RandomizedSearch + τ=0.247 F1 hikayesi | 1 dk |
| 11:45–12:45 | §12 Reviewer Mapping | **Hİ** | 1.+2. tur 8 yorum tablosu | 1 dk |
| 12:45–13:15 | §13 Bootstrap CI | HU | AUC 0.815 [0.7613, 0.8722] | 30 sn |
| 13:15–14:15 | §14 RC4 Robustness | HU | 4-bar grafik + group-aware AUC=0.683 (**B.1 cevabı, kritik bölüm yavaş anlat**) | 1 dk |
| 14:15–15:15 | §15 STATIC F1 Sweep | **Hİ** | Cold-start τ=0.18 F1=0.215 (**B.2 cevabı**) | 1 dk |
| 15:15–16:00 | §16 Ablation Summary | HU | FULL/NO_ENG/STATIC tablosu, engagement marjinal | 45 sn |
| 16:00–16:15 | §17 Export Köprü | **F** | "Demo'daki sayılar bu hücreden — tutarlı hikaye" | 15 sn |

> **Toplam notebook bloğu**: 11 dk 15 sn. 1 dk pay 16:15–17:15'te kapanış için.

---

## 16:15 – 17:15 · KAPANIŞ: Limitler + Sonraki Adım (Hİ, 1 dk)

> HTML §17 sonu / kaydır metodology_addendum referansı. Sözlü özet.

| Süre | İçerik |
|---|---|
| 16:15–16:35 | Üç limit: 49 satıcı, tek-platform, tek-seed |
| 16:35–16:55 | Sonraki adımlar: cohort genişletme, cross-platform, fairness audit |
| 16:55–17:15 | "Veri Bilimi Dergisi makale taslağı hazır, sunum sonrası finalize." → "Sorularınıza açığız." |

---

## 17:15 – 20:00 · Q&A (3 kişi panel)

> Q&A 2 dk 45 sn. 15 olası soru kart hazır → [`qa_cards.md`](qa_cards.md).

- **F** demo + altyapı + threshold/feature sorularını alır → Kart 2, 9, 13
- **HU** model/metrik/ablation sorularını alır → Kart 1, 3, 4, 5, 7, 8, 12
- **Hİ** literatür/etik/limitler/sonraki adım → Kart 6, 10, 11, 14, 15

**Soru gelmezse açılış formülü (HU)**: *"Sıkça merak edilen üç noktaya kendimiz değinelim."* → Kart 1 (B.1) → Kart 4 (post-hoc) → Kart 8 (engagement marjinal).

---

## Geçişler arası "köprü cümleleri" (ezberle)

- **F → HU** (5:00): *"Modelin nasıl davrandığını gördünüz; şimdi bu sayıların nasıl üretildiğini Halil Utku açıklayacak."*
- **HU → Hİ** (7:30, §6→§7): *"ROC ve PR yorumunu Halil İbrahim verecek."*
- **Hİ → HU** (8:15, §7→§8): *"Tekrar Halil Utku'ya — best model deep dive."*
- **HU → Hİ** (11:45, §11→§12): *"Reviewer feedback'ine nasıl cevap verdiğimizi tablolaştırdık, Halil İbrahim üzerinden geçecek."*
- **Hİ → HU** (12:45, §12→§13): *"Halil Utku bootstrap CI ve robustness check'ı detaylandıracak."*
- **HU → Hİ** (14:15, §14→§15): *"Cold-start çalışmasını ayrı bir başlık olarak Halil İbrahim anlatacak."*
- **Hİ → HU** (15:15, §15→§16): *"Halil Utku ablation özetini kapatıyor."*
- **HU → F** (16:00, §16→§17): *"Demo'nun arkasındaki export hücresine kısaca Furkan değinecek."*
- **F → Hİ** (16:15, kapanış): *"Limitler ve sonraki adımları Halil İbrahim özetleyecek."*

---

## Yedek planı (FALLBACK_PLAN.md çağırma)

Demo donarsa:
1. **F**: "1 saniye, notebook §17 hücresine geçiyorum" → ipynb (HTML değil) açıp `run_preset("sold_high_conf")` çalıştır.
2. **HU** sahneye devralır, §16 inline ablation çıktısı zaten ekranda — direkt o sayılara geç.
3. **Hİ** chronometre takip eder, 12:45 — §12 reviewer mapping'i başlat zorla.

HTML açılmazsa: notebook'un kendisi VSCode'da açık — Hide Code yok ama 17 section ve outputs orada. Audience çoğunlukla başlık + grafik takip eder; kod kayar geçer.

Demo + HTML ikisi de çökerse: `methodology_addendum.md` ve `qa_cards.md` printed kopyalar üzerinden sözel sunum (FALLBACK Tier-3).

---

## Geri bildirim toplama (sunum sonrası)

- Hocanın yorumları → 5 dk içinde Hİ not alır (`reports/professor_post_presentation_notes.md`)
- Demo sırasında ekran kaydı (QuickTime) → `artifacts/recordings/` (mahremiyet kontrolü ardından)
- Q&A'da yetersiz cevapladığımız soru → kart no'su işaretle, sonraki revizyonda `qa_cards.md` güncellenir
