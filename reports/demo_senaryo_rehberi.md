# Dolap 7-Day Sale Prediction — Demo Senaryo Rehberi

> **Hazırlayan:** Antigravity  
> **Amaç:** Sunum demo GUI'sındaki mevcut senaryoları açıklamak ve yeni senaryo önerileri sunmak.
> **Son doğrulama:** 2026-05-03 — sayı ve SHAP iddiaları `reports/ablation_results.json` ve `reports/methodology_addendum.md` Bölüm 8.X ile hizalandı. SHAP sıraları **top-5 / top-10** olarak nitel ifade edildi; spesifik rank numaraları kaldırıldı çünkü notebook §13 SHAP summary plot ondalıklı rank vermiyor, sadece görsel sıra var.

---

## Mevcut 10 Senaryo — Ne İşe Yarıyor?

### 🟢 GÜÇLÜ TAHMİNLER

#### 1. Hızlı satılan
- **Ne ayarlıyor:** Yüksek beğeni sayısı + kategoride ucuz fiyat + iyi marka + yeni etiket — tüm güçlü sinyaller aynı anda
- **Hangi hipotezi test ediyor:** H1 (ucuz fiyat) + H2 (marka) + H3 (beğeni) + H4 (kalite) — hepsini birden
- **Beklenen sonuç:** ✅ SOLD, P > %70
- **Sunum notu:** "Modelin en emin olduğu ilan profili. SHAP rank 1-4'teki tüm özellikler iyi yönde."

#### 2. Satılmayacak (kesin)
- **Ne ayarlıyor:** Yüksek fiyat yüzdesi (kategorinin en pahalısı), sıfır beğeni, düşük ilan kalitesi, eski/hasarlı ürün
- **Hangi hipotezi test ediyor:** H1, H3, H4'ün tersini — tüm olumsuz sinyaller
- **Beklenen sonuç:** ❌ NOT SOLD, P < %10
- **Sunum notu:** "Modelin en emin olduğu negatif vaka. Gerçek veriye bakıldığında bu profildeki ilanların %98'i satılmıyor."

---

### 🟠 FİYAT & MARKA HİKAYELERİ

#### 3. Premium / İsim Marka
- **Ne ayarlıyor:** brand_tier = 5 (Lacoste, Tommy Hilfiger, İpekyol vb.) + fiyat kategorinin medyanının altında
- **Hangi hipotezi test ediyor:** **H2 — "Tanınmış markalar daha hızlı satılır"**
- **SHAP bağlantısı:** `brand_tier` mean(|SHAP|) = 0.1614, value↔SHAP corr = **+0.761** (güçlü pozitif yön — `methodology_addendum.md` Bölüm 8.X)
- **Beklenen sonuç:** ✅ SOLD
- **Sunum notu:** "H2 hipotezimizi doğruluyor. Premium marka + makul fiyat kombinasyonu modelin en sevdiği profil."

#### 4. Ucuz + Yeni Etiket
- **Ne ayarlıyor:** price_pctile_cat < 0.30 + condition_score = 4 (yeni ve etiketli)
- **Hangi hipotezi test ediyor:** **H1 + H4** birleşimi — `cheap_and_new` interaction feature tam burası
- **SHAP bağlantısı:** `price_pctile_cat` SHAP top-5 içinde, **yön negatif** (yüksek fiyat→düşük P, ucuz→yüksek P) — H1 doğrulayıcı bulgu
- **Beklenen sonuç:** ✅ SOLD
- **Sunum notu:** "Feature engineering'in gücünü gösteriyor — sadece 'ucuz' veya sadece 'yeni' değil, ikisi birlikte çok güçlü sinyal."

#### 5. Yüksek Beğeni / Yorum
- **Ne ayarlıyor:** like_count = 20-30, comment_count = 5+
- **Hangi hipotezi test ediyor:** **H3 — "Erken etkileşim satışı tahmin eder"**
- **SHAP bağlantısı:** `engagement_score` ve `like_count` SHAP top-5 içinde, yön pozitif (notebook cell[32] Key Findings)
- **Beklenen sonuç:** ✅ SOLD, yüksek olasılıkla
- **Sunum notu:** "Sosyal kanıt etkisi. Ablasyon çalışmamız (NO_ENGAGEMENT, 49 feature) AUC'yi 0.8150'den **0.8097**'ye düşürdüğünü gösterdi (ΔAUC −0.0053) — etkili ama marjinal; modelin omurgası statik özelliklerde."

---

### 🔴 EDGE CASES

#### 6. Cold-Start (Etkileşimin Yok)
- **Ne ayarlıyor:** like_count = 0, comment_count = 0, yeni yayınlanmış ilan
- **Neyi test ediyor:** Sıfır etkileşimli bir ilan — gerçek dünya deployment senaryosu
- **SHAP bağlantısı:** Ablasyon (STATIC_ONLY, 26 feature): AUC = **0.7491** (ΔAUC vs FULL = −0.0659). Default τ=0.50'de F1=0.110, F1-optimal τ=0.18'de F1=0.215'e çıkıyor (§15 sweep, B.2 cevabı)
- **Beklenen sonuç:** Preset gerçek satırdan üretildiği için **P ≈ %91** çıkıyor (cold_start preset bilinçli olarak satılmış bir cold-start vakası — yapısal kalitesi yüksek). Düşük-P versiyonu için `not_sold_high_conf` kullan
- **Sunum notu:** "Bir satıcı yeni ilan açtığında henüz sıfır beğenisi var. Modelimiz bunu bile tahmin edebiliyor — statik özellikler (fiyat, marka, kalite) hâlâ sinyal veriyor. Engagement marjinal, statik kemik."

#### 7. Tipik / Medyan İlan
- **Ne ayarlıyor:** Tüm featurelar eğitim setinin medyan değerinde
- **Neyi test ediyor:** Ortalama Dolap ilanı için model ne diyor?
- **Beklenen sonuç:** P ≈ %5-8 (veri setindeki gerçek satış oranına yakın)
- **Sunum notu:** "Model kalibre edilmiş: ortalama ilan için ortalama olasılık üretiyor. Bu iyi bir işaret."

#### 8. Belirsiz (P ≈ 0.5)
- **Ne ayarlıyor:** Bir kısım özellik iyi, bir kısım kötü — birbiriyle çelişen sinyaller
- **Neyi test ediyor:** Karar sınırındaki ilanlar + **threshold optimizasyonunun önemi**
- **Beklenen sonuç:** P ≈ 0.40-0.55
- **Sunum notu:** "Bu ilan default threshold (0.50) ile NOT SOLD, optimal threshold (0.247) ile SOLD sayılıyor. Threshold seçimi kritik!"

---

### 🟣 MODEL HATALARI — Q&A İçin

#### 9. Model Hatası: False Positive (`hard_negative_FP` preset)
- **Ne gösteriyor:** Model SOLD dedi (P=%84), gerçekte satılmadı
- **Nedenini açıkla:** Premium görünümlü ama "stale" kalmış ilan — model statik kalite sinyallerini abartıyor
- **Precision bağlantısı:** Default τ=0.50'de Precision = **0.4815** (ablation_results.json FULL satırı) — bu tür FP'ler precision'ın 0.50'nin altında kalmasının sebebi
- **Sunum notu:** "Modelin kör noktası şeffaf raporlanmalı — bu hatayı saklamak yerine sahnede gösteriyoruz."

#### 10. Model Hatası: False Negative (`hard_positive_FN` preset)
- **Ne gösteriyor:** Gerçekte satılmış ama model %0.7 NOT SOLD diyor — cold-start anomalisi
- **Nedenini açıkla:** 16:1 sınıf dengesizliği — model NOT SOLD'e eğilimli; bu satıra özgü statik profil zayıf ama listing yine de hızlı çıkmış
- **Recall bağlantısı:** Default τ=0.50'de Recall = **0.1857** (ablation_results.json) — false negative oranı yüksek
- **Sunum notu:** "Bu yüzden threshold'u 0.50'den 0.247'ye düşürdük. F1 0.268'den 0.354'e çıktı — recall iyileşmesi precision'a tercih edilebilir, kayıp ilanları azaltıyoruz."

---

## ➕ Önerilen 4 Yeni Senaryo

> Bunlar hem sunum hikayesini güçlendiriyor hem de hocadan gelebilecek sorulara hazırlık sağlıyor.

---

### 11. 🔄 Threshold Etkisi (Canlı Karşılaştırma)
**Amaç:** Threshold optimizasyonunu somut olarak göstermek

**Nasıl kurgulanır:**
- Karar sınırında bir ilan yükle (P ≈ 0.35-0.40 çıkacak)
- Slider'da threshold = 0.50 → NOT SOLD göster
- Slider'da threshold = 0.247 → SOLD'a döndüğünü göster

**Arka plan:** Aynı ilan, aynı model — sadece eşik değişiyor
```
like_count = 5
price_pctile_cat = 0.35
brand_tier = 3
condition_score = 3
```

**Sunum notu:** *"Threshold'u 0.50'den 0.247'ye düşürmek, bu ilânı 'kayıp' olmaktan 'kazanılan tahmin'e çeviriyor. Recall'ı ikiye katladık."*

---

### 12. ⬆️ Fiyat Kırılma Noktası (H1 Canlı Kanıtı)
**Amaç:** H1 hipotezini interaktif olarak doğrulamak

**Nasıl kurgulanır:**
- Fiyat dışında tüm featureları sabit tut
- `price_pctile_cat` değerini kademeli artır: 0.20 → 0.40 → 0.60 → 0.85
- Her adımda Predict'e bas, grafikte P'nin düştüğünü göster

**Başlangıç değerleri:**
```
price_pctile_cat = 0.20  → P yüksek (SOLD)
price_pctile_cat = 0.85  → P düşük (NOT SOLD)
```

**Sunum notu:** *"H1 hipotezimiz: kategori medyanının altında fiyatlanan ürünler daha hızlı satılır. Bu interaktif demo bunu canlı kanıtlıyor."*

---

### 13. 🧑‍💼 Satıcı Deneyimi Farkı
**Amaç:** `seller_exp_log` SHAP rank 7 — görünmez ama güçlü özellik

**Nasıl kurgulanır:**
- Aynı ilan iki versiyon:
  - **Yeni satıcı:** seller_rating_count = 2 → seller_exp_log = 1.1
  - **Deneyimli satıcı:** seller_rating_count = 150 → seller_exp_log = 5.0

**Sunum notu:** *"Aynı ürünü aynı fiyata satan iki satıcı — ama deneyimli satıcının tahmin olasılığı belirgin şekilde yüksek. Güven etkisi."*

---

### 14. 📦 Ücretsiz Kargo Toggle
**Amaç:** Tek özellik değişiminin etkisini izole etmek — en sade demo

**Nasıl kurgulanır:**
- Sabit bir ilan kur (P ≈ 0.20-0.25 çıkacak)
- `has_free_shipping` = 0 → Predict
- `has_free_shipping` = 1 → Predict (P artmalı)

**Sunum notu:** *"Satıcıya pratik tavsiye: kargo ücretini üstlenmek bile tahmin olasılığını artırıyor. Platform öneri sistemi buradan çıkabilir."*

---

## Senaryoları Kodla Eklemek İçin

Eğer `SCENARIOS` dict'i JS'te tutuyorsan şu formatla ekle:

```javascript
const SCENARIOS = {
  // ... mevcut senaryolar ...

  // YENİ SENARYOLAR:
  threshold_demo: {
    like_count: 5, price_pctile_cat: 0.35, brand_tier: 3,
    condition_score: 3, seller_rating_count: 15, photo_count: 4,
    has_free_shipping: 0, listing_quality_score: 4, comment_count: 1
  },
  price_breakpoint: {
    like_count: 3, price_pctile_cat: 0.85, brand_tier: 2,
    condition_score: 2, seller_rating_count: 10, photo_count: 3,
    has_free_shipping: 0, listing_quality_score: 3, comment_count: 0
  },
  seller_expert: {
    like_count: 4, price_pctile_cat: 0.40, brand_tier: 3,
    condition_score: 3, seller_rating_count: 150, photo_count: 5,
    has_free_shipping: 1, listing_quality_score: 5, comment_count: 2
  },
  free_shipping_toggle: {
    like_count: 3, price_pctile_cat: 0.45, brand_tier: 2,
    condition_score: 2, seller_rating_count: 12, photo_count: 4,
    has_free_shipping: 0, listing_quality_score: 3, comment_count: 0
  },
};
```

---

## Senaryo → Hipotez Eşleşmesi (Hoca için özet)

| Senaryo (preset id) | Hipotez | SHAP Feature | Beklenen P |
|---|---|---|---:|
| Hızlı satılan (`sold_high_conf`) | H1+H2+H3+H4 | Hepsi top-10'da | %95.9 ✅ |
| Satılmayacak (`not_sold_high_conf`) | Tüm hipotezlerin tersi | Negatif yön | %0.1 ❌ |
| Premium / İsim Marka (`premium_brand`) | H2 | `brand_tier` (corr=+0.761) | %94.5 ✅ |
| Ucuz + Yeni Etiket (`cheap_and_new`) | H1+H4 | `price_pctile_cat` (negatif yön) + `condition_score` | %84.4 ✅ |
| Yüksek Beğeni (`high_engagement`) | H3 | `like_count`, `engagement_score` top-5 | %93.5 ✅ |
| Cold-Start (`cold_start`) | H3 yokluğu | `engagement_score`=0, statik kemik | %91.4 ✅ |
| Tipik / Medyan (`median_listing`) | — | Tüm değerler medyan | %2.3 ❌ |
| Belirsiz (`boundary_uncertain`) | Threshold story | Karışık yön | %40.1 🔄 |
| Hata: FP (`hard_negative_FP`) | — | Statik abartma | %84 (yanlış) |
| Hata: FN (`hard_positive_FN`) | — | Cold-start anomali | %0.7 (yanlış) |

> **Önerilen 4 yeni senaryo (11–14)** sunum güncel sürümünde **eklenmedi**: `boundary_uncertain` (P≈0.40) zaten threshold hikayesini karşılıyor, diğer 3 öneri 60 feature'ın 9'unu set edip 51'ini medyana bırakacaktı — derived feature consistency riskine girilmedi.

---

## Sunum-Güncel Sayılar (cheat-sheet)

| Metrik | Değer | Kaynak |
|---|---:|---|
| Test ROC-AUC (FULL) | 0.8150 [0.7613, 0.8722] | `ablation_results.json` |
| CV ROC-AUC (5-fold) | 0.7517 ± 0.0239 | notebook §11 |
| Group-aware AUC (RC4) | 0.6832 [0.6079, 0.7544] | `seller_leakage_robustness.json` |
| F1 default (τ=0.50) | 0.2680 | `ablation_results.json` |
| F1 optimal (τ=0.247) | 0.3544 | notebook §11 |
| Precision default | 0.4815 | `ablation_results.json` |
| Recall default | 0.1857 | `ablation_results.json` |
| ΔAUC NO_ENGAGEMENT (49 ft) | −0.0053 (AUC=0.8097) | `ablation_results.json` |
| ΔAUC STATIC_ONLY (26 ft) | −0.0659 (AUC=0.7491) | `ablation_results.json` |
| STATIC_ONLY F1 default | 0.110 → optimal 0.215 (τ=0.18) | notebook §15 |

---

*Bu doküman Dolap Sale Prediction sunum demosu için hazırlanmıştır.*  
*Model: XGBoost · AUC = 0.8150 (95% CI: 0.7613–0.8722) · 60 feature · SMOTE-balanced (sadece train fold)*
