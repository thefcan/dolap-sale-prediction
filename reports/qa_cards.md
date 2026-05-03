# Q&A Kartları — Olası 15 Soru

> Sunumdan sonra 5 dk Q&A. Sorular hocanın 1. + 2. tur feedback'i, demo'da görülen davranış ve ML metodoloji standartları üzerinden seçildi. Her kart: **soru → kim cevap verir → çekirdek 30 sn cevap → ek detay (lazımsa) → ilgili artefakt**.

---

## Kart 1 — "Test AUC neden CV ortalamasından yüksek?" (B.1)

- **Cevap eden**: HU
- **30 sn**: "Random split satıcı kimliğini koruyamıyor; aynı satıcının train ve test ilanları olduğunda model satıcı imzasını ezberliyor. Group-aware split (49 satıcı, GroupKFold) AUC=0.683 verdi. CV ortalaması 0.752±0.024, group-aware bunun bandında. Yani 0.815 üst sınır — gerçek dağılım üzerindeki performans CV'ye yakın."
- **Detay**: §14 4-bar grafik, `artifacts/metrics/seller_leakage_robustness.json`, `methodology_addendum.md` Bölüm 8.W ve 8.Z.
- **Tuzak**: Soruyu "leak vardı, sonuçlar şişik" diye yanıtlamayın — "headliner üst sınır, group-aware floor; ikisini de raporlıyoruz" doğru framing.

---

## Kart 2 — "Cold-start ilan için modeliniz nasıl çalışıyor?" (B.2)

- **Cevap eden**: F (demo'dan canlı gösterebilir)
- **30 sn**: "Cold-start preset'inde like=0, comment=0. STATIC_ONLY ablation (49 → 26 özellik) AUC 0.749, F1 default 0.110. F1-optimal eşik τ=0.18'de F1 0.215'e çıkıyor. Yani engagement sinyali yokken bile statik özelliklerle pozitif sınıfı çift kat tespit eden bir eşik var."
- **Detay**: §15 PR sweep grafiği, `methodology_addendum.md` Bölüm 8.Y.1.
- **Demo eşliği**: cold-start preset → τ slider 0.247 → 0.18'e indir → marker pozisyonu değişiyor.

---

## Kart 3 — "Neden XGBoost? LightGBM denediniz mi?" (B.3)

- **Cevap eden**: HU
- **30 sn**: "Üç gerekçe: (1) Test AUC 0.815 vs 0.812 — istatistiki olarak yakın ama XGB tutarlı. (2) F1-optimal eşikte XGB 0.354, LGBM 0.301; precision-recall trade-off XGB lehine. (3) SHAP monotonic constraints — H1 (fiyat) ve H2 (marka) hipotezleri için XGB'nin monotonic feature constraint API'si daha temiz çalıştı."
- **Detay**: `methodology_addendum.md` Bölüm 9.X, `article_draft_en.md` §6.X.

---

## Kart 4 — "SHAP açıklamalarını ne kadar ciddiye alalım?" (A — post-hoc framing)

- **Cevap eden**: HU
- **30 sn**: "Önceden kayıtlı sadece iki hipotez var: H1 (fiyat→satış) ve H2 (marka kademesi→satış). SHAP bunları onaylama amacıyla doğrulayıcı kullanıldı. Diğer tüm SHAP gözlemleri post-hoc keşifsel olarak işaretli — yani 'şu özellik X yapıyor' iddiası değil, 'bu modelde şu pattern var' gözlemi. Yeniden kayıtlı çalışmaya konu."
- **Detay**: §3 hipotez kayıt cümlesi, §13 SHAP slayt başlığında '(post-hoc, exploratory)', `article_draft_en.md` §5.3.
- **Tuzak**: 'SHAP yanlıştır' demeyin — 'kullanım çerçevesi farklı' deyin.

---

## Kart 5 — "Class imbalance ile nasıl başa çıktınız?"

- **Cevap eden**: HU
- **30 sn**: "Pozitif sınıf %5.8. SMOTE oversampling sadece training fold'unda, validation/test asla touch edilmedi. Eşik optimizasyonu PR-eğrisi üzerinden F1 maksimum: τ*=0.247. Default τ=0.50 ile F1=0.268, optimal τ ile 0.354 — %32 iyileşme."
- **Detay**: §10 SMOTE kullanımı, §11 threshold optimization.

---

## Kart 6 — "49 unique seller — bu sayı yeterince temsili mi?"

- **Cevap eden**: Hİ
- **30 sn**: "Hayır, bu bir limit. Ablasyon ve robustness analizleri için yeterli ama populasyon-genel iddialar için değil. Sınırlamalar bölümünde açıkça belirttik. Sonraki adımda farklı kategori-satıcı çiftleriyle daha geniş cohort planı var."
- **Detay**: `methodology_addendum.md` Section 6 limitations, `article_draft_en.md` §7.2.

---

## Kart 7 — "Veri sızıntısı (leakage) için başka ne kontrol ettiniz?"

- **Cevap eden**: HU
- **30 sn**: "Üç katman: (1) Temporal split — chronological train/val/test, gelecek bilgi geçmişe sızmıyor. (2) Group-aware split — satıcı kimliği. (3) Feature inspection — 7 günden sonra hesaplanabilen hiçbir özellik girmedi (örn. 'final_price' yok). RC4 robustness check ΔAUC=−0.092 verdi, raporlandı."
- **Detay**: `src/utils/split.py`, `methodology_addendum.md` Bölüm 8.Z.

---

## Kart 8 — "Engagement özellikleri kaldırıldığında AUC neden çok düşmüyor?"

- **Cevap eden**: HU
- **30 sn**: "FULL→NO_ENGAGEMENT ΔAUC=−0.005. Çünkü engagement (like, comment) ile statik özellikler (price, brand_tier, photo_count) yüksek korelasyon. Bilgi engagement'a özgü değil. STATIC_ONLY ile düşüş ΔAUC=−0.066 — yani 26 statik feature, problemin kemik bilgisini taşıyor."
- **Detay**: §16 ablation table.

---

## Kart 9 — "Modelin yanıldığı durumlar ne?" (hard cases)

- **Cevap eden**: F (demo'dan)
- **30 sn**: "İki preset gösterdik: 'hard-negative' — model %84 SOLD diyor ama satılmamış (premium görünümlü ama stale ilan). 'hard-positive' — model %0.7 NOT SOLD diyor ama satılmış (cold-start anomalisi, yüksek fiyatlı ama hızlı çıkmış). Hard cases preset'leri dataset'ten gerçek satırlar."
- **Detay**: `models/feature_schema.json` presets group='errors'.

---

## Kart 10 — "Bu modeli production'a alır mısınız?"

- **Cevap eden**: Hİ
- **30 sn**: "Mevcut haliyle hayır. Üç engel: (1) 49 satıcı temsili değil. (2) Group-aware AUC 0.683 — random-split AUC ile arasında ciddi gap, robust populasyon-üstü performans için yetersiz. (3) Concept drift monitoring kurulu değil. Production öncesi A/B test ve fairness audit gerek."
- **Detay**: `article_draft_en.md` §8 future work.

---

## Kart 11 — "Veri seti tek platform — Dolap dışında nasıl çalışır?"

- **Cevap eden**: Hİ
- **30 sn**: "Bilmiyoruz, doğrulanmadı. Vinted/Depop için aynı feature schema'yı çıkarmak mümkün — kategori taksonomileri farklı ama brand_tier, price_pctile, photo_count evrensel. Cross-platform validation sonraki adımlar listemizde."
- **Detay**: §1 problem definition limit.

---

## Kart 12 — "Tek seed ile ablasyon — istikrarlı mı?"

- **Cevap eden**: HU
- **30 sn**: "Bootstrap CI 200 resample ile hesaplandı: AUC 0.815 [0.7613, 0.8722]. Yani sayı tek-noktasal değil, %95 GA dar (~0.06). Ama farklı seed'lerle multi-fold bootstrap (örn. 5 seed × 200 resample) henüz yapılmadı, sınırlamalar listemizde."
- **Detay**: §16 bootstrap CI, `reports/ablation_results.json`.

---

## Kart 13 — "Threshold τ neden 0.247?"

- **Cevap eden**: F
- **30 sn**: "PR-eğrisi üzerinde F1 maksimum yapan τ. Default 0.50 (%50 olasılık → SOLD) precision-favorlu, recall'u kaçırıyor. Bu marketplace'de pozitif sınıf nadir, recall önemli — 0.247 F1'i %32 artırıyor (0.268 → 0.354)."
- **Detay**: §11 threshold optimization, demo τ chip 'F1-optimal'.

---

## Kart 14 — "Etik / mahremiyet ne durumda?"

- **Cevap eden**: Hİ
- **30 sn**: "Veri public listing sayfalarından çekildi, kişisel bilgi (telefon, adres) hariç. seller_username sadece group-aware split için kullanıldı, modele girmedi. Cohort takip SQLite'ta, repo dışında. IRB-eşdeğeri onay üniversitemiz veri politikası altında."
- **Detay**: `data/README.md`, `.env.example` ban_detection settings.

---

## Kart 15 — "Sonraki adım?"

- **Cevap eden**: Hİ
- **30 sn**: "Üç paralel: (1) Cohort genişletme — 49 → 200+ satıcı için yeni scrape. (2) Multi-seed bootstrap + cross-platform validation. (3) Veri Bilimi Dergisi makale finalize. Bugünkü reviewer mapping ile draft güncel, sunum sonrası göndermeyi hedefliyoruz."
- **Detay**: `todo.md` M9.4 + M8.5 (paused), `article_draft_en.md`.

---

## Hızlı bakış (panele yapışkan kart)

| # | Konu | Kim |
|---|---|---|
| 1 | Test>CV anomaly | HU |
| 2 | Cold-start | F |
| 3 | XGB vs LGBM | HU |
| 4 | SHAP post-hoc | HU |
| 5 | Class imbalance | HU |
| 6 | 49 satıcı temsili mi | Hİ |
| 7 | Leakage kontrolleri | HU |
| 8 | Engagement marjinal Δ | HU |
| 9 | Hard cases | F |
| 10 | Production hazır mı | Hİ |
| 11 | Cross-platform | Hİ |
| 12 | Tek-seed bootstrap | HU |
| 13 | τ=0.247 | F |
| 14 | Etik/mahremiyet | Hİ |
| 15 | Sonraki adım | Hİ |

**Soru gelmezse açılış formülü (HU)**: *"Sıkça merak edilen üç noktaya kendimiz değinelim."* → Kart 1 → Kart 4 → Kart 8 sırasıyla.
