# Sunum Run-Sheet — 4 Mayıs 2026 (20 dk)

**Format**: 5 dk live demo + 10 dk model kararları + 5 dk Q&A
**Ekip**: Furkan (F) · Halil Utku (HU) · Halil İbrahim (Hİ)
**Materyal**: `notebooks/dolap_classification_final.ipynb` (Run-All temiz) + `python demo/demo_server.py`

---

## T-30 dk · Sahne öncesi kontrol (3 kişi paralel)

| Kim | Görev |
|---|---|
| F | Notebook Restart & Run All — kırmızı stripe yok, §14/§15/§16/§17 hücreleri çıktılı |
| F | `lsof -i :5000` → boş, `python demo/demo_server.py` → "Test AUC: 0.8150" yazıyor |
| F | Tarayıcı `http://127.0.0.1:5000/` → 10 senaryo butonu görünüyor, "Hızlı satılan" çalışıyor |
| HU | `reports/methodology_addendum.md` PDF olarak hazır, USB + bulut kopyası |
| HU | Yedek: `FALLBACK_PLAN.md` ekranda 2. tab olarak açık |
| Hİ | Sunum dosyası projektörde test edildi, font okunuyor, klikleyici çalışıyor |

---

## 0:00 – 5:00 · LIVE DEMO (Furkan)

> Hedef: model çalışıyor olduğunu **göstermek**, sayıyı değil tepkiyi vurgulamak.

| Süre | Aksiyon | Söylenecek |
|---|---|---|
| 0:00–0:30 | Tarayıcıyı aç, başlık satırını oku | "60 özellikli XGBoost — test AUC 0.8150, %95 GA ±0.06. Şimdi modele 10 farklı senaryo göstereceğim." |
| 0:30–1:00 | **Tipik / medyan ilan** preset → Predict | "Medyan ilan ~%2. Platformun gerçek satış oranı %5 — yani ortalama ilan ortalamanın altında." |
| 1:00–1:30 | **Hızlı satılan (yüksek olasılık)** preset → Predict | "Aynı modelden %96. Aradaki 94 puanlık fark, modelin gerçekten ayırt ettiğini gösteriyor." |
| 1:30–2:15 | **Cold-start** preset → Predict | "like=0, comment=0 — engagement sinyali yok. Buna rağmen %91. §15'teki STATIC-only çalışmasının ana motivasyonu bu." |
| 2:15–2:45 | **Premium / lüks marka** preset | "brand_tier=4, is_known_brand=1 — H2 (marka kademesi) doğrulayıcı analizine doğrudan bağlanıyor." |
| 2:45–3:30 | **Hard-negative (model yanılıyor)** preset | "Bu satılmamış ama model %84 SOLD diyor. Kasıtlı gösteriyorum — modelin kör noktası şeffaf raporlanmalı." |
| 3:30–4:15 | τ slider'ı 0.50 → 0.247 | "F1-optimal eşik. Cold-start gauge'da işaretçi soluna kayıyor — etiket aynı modelle yeniden eğitim yapmadan değişiyor. B.2 reviewer yorumunun cevabı bu." |
| 4:15–5:00 | Filter "price" → 80 TL elle düşür → Predict | "Tek özellik değiştirildiğinde küçük kayma — çünkü price_log/pctile medyanda kalıyor. Preset yaklaşımının gerekçesi bu: 60 özellik tutarlı kalsın diye." |

**Geçiş cümlesi → HU**: "Şimdi Halil Utku model kararlarını anlatacak."

---

## 5:00 – 10:00 · MODEL KARARLARI (Halil Utku)

> Hedef: `notebooks/.../§12 Sunum Yapısı` + reviewer feedback'ine 1-1 cevap.

| Süre | Slayt / Notebook | Anahtar mesaj |
|---|---|---|
| 5:00–5:45 | §1 problem + §2 dataset | "6,059 satır × 60 özellik, 7-gün satış oranı %5.8, temporal split (train/val/test=60/20/20)." |
| 5:45–7:00 | §11 model selection — XGBoost vs LGBM tablo | "AUC: 0.8150 vs 0.8120, F1@τ*: 0.354 vs 0.301, SHAP fit: monotonic constraints çalışıyor. Üç gerekçeyle XGB ana model. **B.3 cevabı**." |
| 7:00–7:45 | §14 robustness 4-bar grafik | "Random split AUC=0.815, group-aware (49 unique seller) AUC=0.683 — ΔAUC=−0.092. Headliner sayıya not düşüldü; CV bandı (0.752±0.024) ile group-aware uyumlu, **B.1 anomaly açıklandı**." |
| 7:45–8:30 | §16 ablation table + CI bar | "FULL=0.815, NO_ENGAGEMENT=0.810 (Δ=−0.005), STATIC_ONLY=0.749 (Δ=−0.066). Engagement marjinal, statik özellikler kemik." |
| 8:30–9:15 | §15 STATIC_ONLY threshold sweep | "Statik-only F1 default 0.110, optimal 0.215 (τ*=0.18). Cold-start için F1 maksimum üreten eşik var, **B.2 cevabı**." |
| 9:15–10:00 | §3-§13 SHAP ekranı + post-hoc dipnot | "H1 (fiyat) ve H2 (marka kademesi) önceden kayıtlı, SHAP onları **doğrulayıcı** olarak desteklemek için. Tüm diğer SHAP yorumları **post-hoc keşifsel** olarak işaretli — **A cevabı**." |

**Geçiş cümlesi → Hİ**: "Reviewer mapping ve sonraki adımları Halil İbrahim özetleyecek."

---

## 10:00 – 15:00 · YORUM HARİTASI + SONRAÇ (Halil İbrahim)

| Süre | İçerik |
|---|---|
| 10:00–11:00 | **§12 Reviewer mapping tablosu** ekranda — 1. tur (4 yorum) ve 2. tur (4 yorum), her satırda hangi notebook §'sinde nereden çözüldüğü |
| 11:00–12:00 | `methodology_addendum.md` özeti: Bölüm 8.Z (RC4), 8.W (anomaly), 8.Y.1 (STATIC F1), 9.X (XGB) |
| 12:00–13:00 | Limitler: 49 unique seller (group-aware n düşük), tek-platform veri, ablation tek-seed, derin DL denenmedi |
| 13:00–14:00 | Sonraki adımlar: çoklu-seed bootstrap, Dolap dışı validasyon (Vinted/Depop), seller-cluster fairness audit |
| 14:00–15:00 | "Veri Bilimi Dergisi" makale taslağı: `article_draft_en.md` mevcut, sunum sonrası finalize |

**Bitiriş**: "Sorulara açığız."

---

## 15:00 – 20:00 · Q&A (3 kişi panel)

- F demo + altyapı + threshold/feature sorularını alır
- HU model/metrik/ablation sorularını alır
- Hİ literatür/etik/limitler/sonraki adım sorularını alır
- Bir soru gelmezse → "Sıkça sorulan birkaç noktaya kendimiz değinelim" → Q&A kartlarından 2-3 tanesini sırayla F→HU→Hİ söyler (kart 3, kart 7, kart 12 önerilir).

---

## Geçişler arası "köprü cümleleri" (ezberle)

- F→HU: *"Modelin nasıl davrandığını gördünüz, şimdi neden böyle davrandığını Halil Utku açıklayacak."*
- HU→Hİ: *"Reviewer feedback'ine nasıl cevap verdiğimizi tablolaştırdık, Halil İbrahim üzerinden geçecek."*
- Q&A açılış: *"Üçümüz farklı bloklara baktık, soruyu en uygun olanımız alacak."*

---

## Yedek planı (FALLBACK_PLAN.md çağırma)

Demo donarsa:
1. F: "1 saniye, notebook'taki §17 hücresine geçiyorum" → notebook'tan `run_preset("sold_high_conf")` çalıştır.
2. HU sahneye devralır, §16 inline ablation çıktısı zaten ekranda — direkt o sayılara geç.
3. Hİ chronometre takip eder, 12. dakikada toplamayı zorla.

---

## Geri bildirim toplama (sunum sonrası)

- Hocanın yorumları → 5 dk içinde Hİ not alır (`reports/professor_post_presentation_notes.md`)
- Demo sırasında ekran kaydı (QuickTime) → `artifacts/recordings/` (mahremiyet kontrolü ardından)
