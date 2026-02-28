# 📊 Dolap İkinci El Moda İlanı Satış Tahmini — Detaylı Proje Raporu

> **Araştırma Sorusu:** Bir Dolap ilanının özelliklerine bakarak 7 gün içinde satılıp satılmayacağını tahmin edebilir miyiz?

**Hazırlanma Tarihi:** 1 Mart 2026  
**Platform:** [dolap.com](https://dolap.com) (Trendyol bünyesinde)

---

## 1. 📌 Yönetici Özeti (Executive Summary)

Bu proje, Türkiye'nin önde gelen ikinci el moda platformu **Dolap.com** üzerinde yayınlanan ilanların **7 gün içinde satılıp satılmayacağını** makine öğrenmesi yöntemleriyle tahmin etmeyi amaçlamaktadır. Proje, hem akademik özgünlük hem de pratik değer açısından güçlü bir zemine sahiptir:

- **Literatürde Dolap.com üzerine herhangi bir ML çalışması bulunmamaktadır** (Google Scholar taraması ile teyit edilmiştir)
- İkinci el moda pazarı Türkiye'de hızla büyümekte olup, satıcıların fiyatlama ve ilan stratejilerini optimize etmelerine yardımcı olacak bir araç büyük değer taşımaktadır
- Hedef değişken (`sold_within_7_days`) doğal olarak platformdan elde edilebilir (ground truth)

---

## 2. 🔬 Literatür Taraması ve Özgünlük Analizi

### 2.1 Dolap.com Üzerine Mevcut Çalışmalar

Google Scholar üzerinde yapılan kapsamlı tarama sonuçları:

| Arama Sorgusu | Sonuç |
|---|---|
| `"dolap.com" machine learning` | ❌ Hiçbir ilgili makale bulunamadı |
| `dolap ikinci el moda makine öğrenmesi` | ❌ Dolap'a özgü ML çalışması yok |
| `dolap second hand fashion machine learning prediction` | ❌ Doğrudan ilgili sonuç yok |

> **✅ TEYİT:** Dolap.com platformu üzerine literatürde herhangi bir makine öğrenmesi çalışması **bulunmamaktadır**. Bu durum projeye güçlü bir özgünlük zemini sağlamaktadır.

### 2.2 Benzer Platformlar Üzerine Mevcut Çalışmalar

| Platform | Çalışma Türü | Referans |
|---|---|---|
| **Mercari** | Fiyat Tahmini (Price Prediction) | Fathalla et al. (2020) - "Deep end-to-end learning for price prediction of second-hand items" — *72 atıf* |
| **Mercari** | Fiyat Önerisi | Han et al. (2020, 2021) - "Price suggestion for online second-hand items" |
| **ZOZOUSED** (Japonya) | Mevsimsel Talep Tahmini | Saito et al. (2021) - "ML for Demand Prediction of Seasonal Second-hand Fashion Items" |
| **Genel** | İade Tahmini | Niederlaender et al. (2025) - "Garment Returns Prediction with Feature Importance" |
| **Genel** | CNN ile Sınıflandırma | Malmgård (2021) - "Second-hand goods classification with CNNs" |
| **Poshmark** | Satış Tahmini | ❌ `"poshmark" "sale prediction" machine learning` → **Hiçbir sonuç bulunamadı** |

### 2.3 Özgünlük Değerlendirmesi

| Boyut | Değerlendirme |
|---|---|
| **Platform Özgünlüğü** | 🟢 Dolap.com üzerine ilk ML çalışması |
| **Görev Özgünlüğü** | 🟢 Satış tahmini (binary classification) — Mevcut çalışmalar fiyat tahminine odaklı |
| **Coğrafi Özgünlük** | 🟢 Türkiye'ye özgü ikinci el moda pazarı (yerel dinamikler, marka tercihleri, fiyatlama davranışları) |
| **Metodolojik Katkı** | 🟡 Feature engineering (fiyat/medyan oranı vb.) yeni, model mimarileri bilinen |

---

## 3. 🏗️ Platform Analizi — Dolap.com

### 3.1 Platform Hakkında

- **Kuruluş:** Dolap.com, Türkiye'nin en büyük e-ticaret platformu **Trendyol** bünyesinde faaliyet göstermektedir
- **Kapsam:** İkinci el kıyafet, çanta, ayakkabı, aksesuar, bebek/çocuk ürünleri, elektronik aksesuar, kitap, ev eşyaları
- **Slogan:** "Elden ele moda"
- **Güvenlik:** Orijinallik kontrolü (Dolap Dedektifi), güvenli ödeme, 7/24 müşteri hizmetleri
- **Taksit:** Tüm kredi kartlarına 9 taksit imkanı

### 3.2 Ürün Sayfası Yapısı (Scraping İçin Kritik)

Bir Dolap ürün sayfasından elde edilebilecek veriler:

```
📦 ÜRÜN BİLGİLERİ
├── Marka (ör: Zara, Nike, Apple)
├── Ürün Kategorisi (breadcrumb: Ana Sayfa > Kadın > Üst Giyim > Kazak)
├── Alt Kategori (ör: Telefon Kılıfı, Elbise, Bot)
├── Fiyat (TL cinsinden)
├── Durum Etiketi (Yeni & Etiketli / Az Kullanılmış / Yeni)
├── Renk
├── Beden (varsa)
├── Ürün Açıklaması (serbest metin)
├── Fotoğraf Sayısı (1-6 arası fotoğraf)
├── Beğeni Sayısı
├── Yorum Sayısı
├── Kargo Bilgisi (Alıcı Öder / Satıcı Öder)

👤 SATICI BİLGİLERİ
├── Satıcı Kullanıcı Adı
├── Satıcı Toplam Satış/Değerlendirme Sayısı (parantez içinde gösteriliyor)
├── Satıcı Profil Linki

📍 DURUM BİLGİSİ
├── "Satıldı" etiketi (satılan ürünlerde)
├── URL yapısı: dolap.com/urun/{marka}-{renk}-{kategori}-{durum}-{satıcı}-{id}
```

### 3.3 URL Yapısı Analizi

```
https://dolap.com/urun/apple-seffaf-telefon-kilifi-yeni-etiketli-iphonelcase-443555655
                       │       │        │              │            │           │
                     marka   renk    kategori        durum       satıcı      ürün_id
```

Bu yapı, toplu veri toplama için programatik URL oluşturmayı kolaylaştıracaktır.

### 3.4 Popüler Markalar ve Kategoriler

**En Çok Aranan Markalar (dolap.com'dan):**
- **Fast Fashion:** Zara, Mango, H&M, Bershka, Stradivarius, Pull&Bear, Koton, LC Waikiki, Defacto
- **Spor:** Nike, Adidas, New Balance, Puma, Skechers, Converse, Under Armour, Hummel
- **Lüks:** Louis Vuitton, Gucci, Chanel, Prada, Burberry, Balenciaga, Michael Kors
- **Türk Markaları:** İpekyol, Yargıcı, Beymen, Derimod, Kemal Tanca

**Ana Kategoriler:**
- Kadın (Kol Çantası, Mont, Kazak, Çizme, Bot, Elbise)
- Bebek/Çocuk (Erkek Çocuk, Kız Çocuk)
- Hamile
- Tesettür
- Elektronik Aksesuar
- Kitap / Hobi

---

## 4. 🎯 Proje Tasarımı

### 4.1 Problem Tanımı

| Özellik | Değer |
|---|---|
| **Problem Tipi** | İkili Sınıflandırma (Binary Classification) |
| **Hedef Değişken** | `sold_within_7_days` → {0, 1} |
| **Gözlem Birimi** | Tek bir Dolap ilanı |
| **Zaman Penceresi** | İlan yayınlanma tarihi + 7 gün |
| **Ground Truth** | Platform üzerinde "Satıldı" etiketi |

### 4.2 Önerilen Özellik Seti (Feature Engineering)

#### A) İlan Özellikleri (Listing Features)

| # | Özellik | Tip | Açıklama | Kaynak |
|---|---|---|---|---|
| 1 | `price` | Continuous | İlan fiyatı (TL) | Ürün sayfası |
| 2 | `price_to_category_median_ratio` | Continuous | Fiyat / Kategori medyan fiyatı | Türetilmiş |
| 3 | `brand_tier` | Ordinal | Marka kademesi (1: Budget → 5: Luxury) | Türetilmiş |
| 4 | `photo_count` | Discrete | İlanda kaç fotoğraf var | Ürün sayfası |
| 5 | `description_length` | Discrete | Açıklama karakter/kelime sayısı | Ürün sayfası |
| 6 | `condition_label` | Categorical | Durum etiketi (Yeni & Etiketli / Az Kullanılmış / Yeni) | Ürün sayfası |
| 7 | `size` | Categorical | Beden bilgisi (XS, S, M, L, XL...) | Ürün sayfası |
| 8 | `color` | Categorical | Renk bilgisi | Ürün sayfası |
| 9 | `category` | Categorical | Ürün kategorisi | Ürün sayfası |
| 10 | `subcategory` | Categorical | Alt kategori | Ürün sayfası |
| 11 | `has_discount` | Binary | İndirimli mi? (üstü çizili fiyat var mı) | Ürün sayfası |
| 12 | `listing_hour` | Discrete | İlanın yayınlandığı saat (0-23) | Ürün sayfası/API |
| 13 | `listing_day_of_week` | Categorical | İlanın yayınlandığı gün | Ürün sayfası/API |
| 14 | `shipping_paid_by` | Binary | Kargo kimin tarafından ödeniyor | Ürün sayfası |

#### B) Satıcı Özellikleri (Seller Features)

| # | Özellik | Tip | Açıklama | Kaynak |
|---|---|---|---|---|
| 15 | `seller_rating_count` | Discrete | Satıcının toplam değerlendirme sayısı | Profil sayfası |
| 16 | `seller_total_listings` | Discrete | Satıcının aktif ilan sayısı | Profil sayfası |
| 17 | `seller_account_age` | Continuous | Hesap yaşı (gün) | Profil sayfası |
| 18 | `seller_is_verified` | Binary | Satıcı doğrulanmış mı? | Profil sayfası |

#### C) Etkileşim Özellikleri (Engagement Features — opsiyonel)

| # | Özellik | Tip | Açıklama | Kaynak |
|---|---|---|---|---|
| 19 | `like_count_at_scrape` | Discrete | Scrape anındaki beğeni sayısı | Ürün sayfası |
| 20 | `comment_count` | Discrete | Yorum sayısı | Ürün sayfası |

> ⚠️ **Dikkat:** Beğeni ve yorum sayısı gibi etkileşim özellikleri **data leakage** riski taşır, çünkü bunlar ilanın yayınlanmasından sonra artar. Bu özelliklerin modelde kullanılıp kullanılmayacağına dikkat edilmelidir. İlan yayınlanma anında bu bilgiler 0 olacağı için, **sadece scrape anında "erken dönem" etkileşimi ölçen bir alt-set** oluşturulabilir.

#### D) Türetilmiş Özellikler (Derived Features)

| # | Özellik | Formül / Mantık |
|---|---|---|
| 21 | `price_per_brand_avg` | `price / brand_avg_price` |
| 22 | `desc_has_keywords` | Açıklamada "indirim", "acil", "son fiyat" gibi anahtar kelimeler var mı |
| 23 | `title_quality_score` | Başlıktaki bilgi yoğunluğu (marka + beden + renk + durum) |
| 24 | `is_weekend_listing` | Hafta sonu mu yayınlandı? |
| 25 | `category_competition` | Aynı kategorideki aktif ilan sayısı (scrape anı) |

### 4.3 Marka Kademe Sistemi (Brand Tier)

```
Tier 1 (Budget)     : LC Waikiki, Defacto, Koton, Civil, Tozlu
Tier 2 (Mid-Range)  : Zara, Mango, H&M, Bershka, Stradivarius, Pull&Bear, Colin's
Tier 3 (Premium)    : İpekyol, Yargıcı, Beymen, Tommy Hilfiger, Lacoste
Tier 4 (Designer)   : Michael Kors, Coach, Kate Spade, Guess, Ray-Ban
Tier 5 (Luxury)     : Louis Vuitton, Gucci, Chanel, Prada, Burberry, Balenciaga, Valentino, Fendi
```

---

## 5. 🕸️ Veri Toplama Stratejisi

### 5.1 Web Scraping Mimarisi

```
                    ┌─────────────────────────────┐
                    │      PHASE 1: İlk Scrape    │
                    │      (Aktif İlanlar)         │
                    │                              │
                    │  • Kategori sayfalarını tara  │
                    │  • Ürün detay sayfalarını çek │
                    │  • Satıcı profil bilgilerini  │
                    │    topla                      │
                    │  • Timestamp kaydet           │
                    └──────────┬──────────────────┘
                               │
                               │ 7 gün bekle
                               ▼
                    ┌─────────────────────────────┐
                    │    PHASE 2: Durum Kontrolü   │
                    │    (7 Gün Sonra)             │
                    │                              │
                    │  • Aynı ürün URL'lerini      │
                    │    tekrar ziyaret et          │
                    │  • "Satıldı" etiketi var mı? │
                    │  • sold_within_7_days = 1/0  │
                    │    olarak etiketle            │
                    └──────────┬──────────────────┘
                               │
                               ▼
                    ┌─────────────────────────────┐
                    │    PHASE 3: Veri Temizleme   │
                    │    & Feature Engineering     │
                    │                              │
                    │  • Eksik veri kontrolü       │
                    │  • Kategorik encoding        │
                    │  • Özellik türetme           │
                    │  • Dengesizlik analizi       │
                    └─────────────────────────────┘
```

### 5.2 Teknik Detaylar

```python
# Önerilen Teknoloji Stack'i
scraping_stack = {
    "http_client": "requests / httpx (async)",
    "html_parser": "BeautifulSoup4 / lxml",
    "browser_automation": "Selenium / Playwright (JS-rendered içerik için)",
    "scheduler": "APScheduler / cron (7 günlük re-check için)",
    "storage": "SQLite / PostgreSQL + CSV export",
    "rate_limiting": "1-3 sn/istek arası bekleme",
    "proxy": "İsteğe bağlı rotating proxy",
}
```

### 5.3 Scraping Stratejisi

1. **Kategori Bazlı Tarama:**
   - Ana kategorileri sırayla tara (Kadın > Üst Giyim > Kazak, vb.)
   - Her kategori için pagination ile tüm aktif ilanları listele
   - Her ilan için detay sayfasını çek

2. **Rate Limiting & Etik Kurallar:**
   - İstekler arası minimum 1-3 saniye bekleme
   - `robots.txt` dosyasına uyum
   - User-Agent header'ı belirtme
   - Sunucuyu aşırı yüklememek için gece saatlerinde çalıştırma
   - Kişisel veri toplamama (satıcı adı yerine hash kullanma)

3. **Hedef Veri Büyüklüğü:**

| Metrik | Hedef |
|---|---|
| Minimum ilan sayısı | 5,000+ |
| İdeal ilan sayısı | 10,000 – 50,000 |
| Kategori çeşitliliği | En az 10 farklı ana kategori |
| Marka çeşitliliği | En az 50 farklı marka |
| Scrape periyodu | 2-4 hafta (haftalık cohort'lar halinde) |

### 5.4 Etiketleme (Labeling) Mekanizması

```
İlan durumu kontrol mantığı:
─────────────────────────────
1. İlan sayfasına git
2. EĞER sayfa 404 döner → muhtemelen satıldı/kaldırıldı → ayrı bayrak
3. EĞER "Satıldı" etiketi/badge'i varsa → sold_within_7_days = 1
4. EĞER ilan hâlâ aktifse → sold_within_7_days = 0
5. EĞER ilan silindiyse (satılmadan) → veri setinden çıkar veya ayrı sınıf
```

---

## 6. 🤖 Modelleme Stratejisi

### 6.1 Önerilen Modeller

| # | Model | Neden | Avantaj |
|---|---|---|---|
| 1 | **Logistic Regression** | Baseline model | Yorumlanabilirlik, hız |
| 2 | **Random Forest** | Ensemble, feature importance | Overfitting'e dayanıklı |
| 3 | **XGBoost / LightGBM** | State-of-the-art tabular | Yüksek performans, kategorik destek |
| 4 | **CatBoost** | Kategorik veri native desteği | Encoding gerektirmez |
| 5 | **Neural Network (MLP)** | Non-linear patterns | Metin embedding'leri ile birleştirilir |

### 6.2 Deneysel Tasarım

```
Pipeline:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Ham Veri → Temizleme → Feature Engineering → Train/Test Split
                                                    │
                              ┌──────────────────────┼──────────────────────┐
                              │                      │                      │
                         Baseline              Tree-Based            Deep Learning
                      (Logistic Reg)       (XGBoost/CatBoost)         (MLP/LSTM)
                              │                      │                      │
                              └──────────────────────┼──────────────────────┘
                                                    │
                                            Performans Karşılaştırması
                                                    │
                                         ┌──────────┴──────────┐
                                         │                     │
                                   En İyi Model         Ablation Study
                                   Seçimi               (Feature Importance)
                                         │
                                    Hyperparameter
                                    Tuning (Optuna)
                                         │
                                    Final Model
```

### 6.3 Değerlendirme Metrikleri

| Metrik | Neden Önemli |
|---|---|
| **AUC-ROC** | Sınıf dengesizliğinde güvenilir, ana metrik |
| **F1-Score** | Precision-Recall dengesi |
| **Precision** | "Satılacak" dediğimizde ne kadar haklıyız? |
| **Recall** | Gerçekten satılan ilanların yüzde kaçını yakalıyoruz? |
| **Accuracy** | Genel doğruluk (dengesiz veri varsa yanıltıcı olabilir) |
| **PR-AUC** | Dengesiz veri setlerinde ROC'tan daha bilgilendirici |

### 6.4 Sınıf Dengesizliği Stratejileri

Dolap'ta ilanların büyük çoğunluğu 7 gün içinde **satılmayabilir** → dengesiz veri bekleniyor.

| Strateji | Açıklama |
|---|---|
| **SMOTE** | Sentetik azınlık örnekleri üretme |
| **Class Weights** | Model eğitiminde sınıf ağırlıkları (XGBoost: `scale_pos_weight`) |
| **Undersampling** | Çoğunluk sınıfından örnekleme |
| **Threshold Tuning** | Karar eşiğini 0.5'ten farklı ayarlama |
| **Stratified K-Fold** | Cross-validation'da sınıf oranını koruma |

---

## 7. 📁 Proje Yapısı

```
dolap-sale-prediction/
│
├── docs/
│   ├── PROJE_RAPORU.md              ← Bu dosya
│   └── LITERATUR.md                 ← Detaylı literatür notları
│
├── src/
│   ├── scraping/
│   │   ├── __init__.py
│   │   ├── dolap_scraper.py         ← Ana scraper sınıfı
│   │   ├── product_parser.py        ← Ürün sayfası ayrıştırıcı
│   │   ├── seller_parser.py         ← Satıcı profil ayrıştırıcı
│   │   ├── category_crawler.py      ← Kategori gezgini
│   │   └── status_checker.py        ← 7 gün sonraki durum kontrolü
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── cleaning.py              ← Veri temizleme
│   │   ├── feature_engineering.py   ← Özellik türetme
│   │   ├── brand_tiers.py           ← Marka kademe tanımları
│   │   └── eda.py                   ← Keşifsel veri analizi
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── baseline.py              ← Logistic Regression baseline
│   │   ├── tree_models.py           ← XGBoost, CatBoost, RF
│   │   ├── neural_net.py            ← MLP modeli
│   │   ├── train.py                 ← Eğitim pipeline
│   │   ├── evaluate.py              ← Değerlendirme metrikleri
│   │   └── hyperparameter_tuning.py ← Optuna ile tuning
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py                ← Proje konfigürasyonu
│       ├── logger.py                ← Loglama
│       └── database.py              ← DB bağlantısı
│
├── notebooks/
│   ├── 01_eda.ipynb                 ← Keşifsel Veri Analizi
│   ├── 02_feature_analysis.ipynb    ← Özellik analizi
│   ├── 03_modeling.ipynb            ← Model eğitimi ve karşılaştırma
│   └── 04_results.ipynb             ← Sonuçlar ve görselleştirme
│
├── data/
│   ├── raw/                         ← Ham scrape verileri
│   ├── processed/                   ← Temizlenmiş veriler
│   └── models/                      ← Eğitilmiş model dosyaları
│
├── tests/
│   ├── test_scraper.py
│   ├── test_features.py
│   └── test_models.py
│
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
└── README.md
```

---

## 8. 📦 Teknoloji Stack'i

### 8.1 Python Paketleri

```
# Veri Toplama
requests>=2.31.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
selenium>=4.15.0          # JS-rendered içerik için
playwright>=1.40.0         # Alternatif browser automation
httpx>=0.25.0              # Async HTTP client

# Veri İşleme & Analiz
pandas>=2.1.0
numpy>=1.25.0
scipy>=1.11.0

# Görselleştirme
matplotlib>=3.8.0
seaborn>=0.13.0
plotly>=5.18.0

# Makine Öğrenmesi
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.1.0
catboost>=1.2.0
imbalanced-learn>=0.11.0  # SMOTE vb.
optuna>=3.4.0             # Hyperparameter tuning
shap>=0.43.0              # Model açıklanabilirliği

# Derin Öğrenme (opsiyonel)
torch>=2.1.0
transformers>=4.35.0      # Metin embedding'leri için

# Veritabanı
sqlalchemy>=2.0.0
sqlite3                   # Yerleşik

# Yardımcı
python-dotenv>=1.0.0
tqdm>=4.66.0
schedule>=1.2.0           # Zamanlayıcı
loguru>=0.7.0             # Gelişmiş loglama
```

---

## 9. ⏱️ Zaman Çizelgesi

```
Hafta 1-2:  🕸️ Scraper Geliştirme & İlk Veri Toplama
            ├── Scraper sınıflarını yaz
            ├── Dolap.com yapısını reverse-engineer et
            ├── İlk batch scrape (5,000+ ilan)
            └── Veritabanı şemasını oluştur

Hafta 2-3:  ⏳ Bekleme & İkinci Scrape
            ├── 7 gün bekle
            ├── Durum kontrolü scrape (Phase 2)
            ├── Etiketleme (sold_within_7_days)
            └── İkinci batch'i başlat

Hafta 3-4:  🧹 Veri Temizleme & EDA
            ├── Eksik veri analizi
            ├── Outlier tespiti
            ├── İstatistiksel özetler
            ├── Görselleştirmeler
            └── Feature Engineering

Hafta 4-5:  🤖 Modelleme
            ├── Baseline modeller
            ├── Gelişmiş modeller (XGBoost, CatBoost)
            ├── Hyperparameter tuning
            ├── Cross-validation
            └── Sınıf dengesizliği stratejileri

Hafta 5-6:  📊 Analiz & Raporlama
            ├── Model karşılaştırması
            ├── Feature importance analizi
            ├── SHAP değerleri
            ├── Ablation study
            └── Final rapor
```

---

## 10. ⚠️ Riskler ve Azaltma Stratejileri

| # | Risk | Olasılık | Etki | Azaltma Stratejisi |
|---|---|---|---|---|
| 1 | Dolap scraping'i engelleyebilir (anti-bot) | 🔴 Yüksek | 🔴 Kritik | Rate limiting, proxy rotation, browser fingerprint |
| 2 | Site yapısı değişebilir | 🟡 Orta | 🟡 Orta | Modüler parser yapısı, düzenli test |
| 3 | Sınıf dengesizliği çok yüksek olabilir | 🟡 Orta | 🟡 Orta | SMOTE, class weights, threshold tuning |
| 4 | "Satıldı" etiketi ile "Kaldırıldı" karışabilir | 🟡 Orta | 🔴 Yüksek | 404 vs "Satıldı" badge ayrımını net yapma |
| 5 | Veri toplama süresi uzayabilir (7 gün bekleme) | 🟢 Düşük | 🟡 Orta | Paralel cohort'lar, haftalık batch'ler |
| 6 | Yasal/etik sorunlar | 🟡 Orta | 🔴 Yüksek | Kişisel veri toplamama, akademik amaç belirtme, robots.txt'ye uyum |
| 7 | Feature leakage (beğeni, yorum sayıları) | 🟡 Orta | 🔴 Yüksek | Etkileşim features ayrı deney seti |

---

## 11. 📈 Beklenen Çıktılar ve Katkılar

### 11.1 Akademik Katkılar
1. **Dolap.com üzerine ilk ML çalışması** → Yeni bir veri alanının açılması
2. **İkinci el moda satış tahmini** için yeni bir framework (fiyat tahmini değil)
3. **Türkiye pazarına özgü tüketici davranışı** içgörüleri (marka tercihleri, fiyatlama)
4. **Feature engineering** tekniklerinin ikinci el moda bağlamında değerlendirilmesi

### 11.2 Pratik Katkılar
1. **Satıcılar için:** İlanlarını optimize etme rehberi (fiyat, fotoğraf sayısı, açıklama)
2. **Platform için:** Satış olasılığı skoru ile ilan öne çıkarma
3. **Alıcılar için:** Pazarlık potansiyeli tahmini

### 11.3 Beklenen Model Performansı

| Metrik | Beklenen Aralık | Referans |
|---|---|---|
| AUC-ROC | 0.70 – 0.85 | Mercari fiyat tahmini çalışmalarından analoji |
| F1-Score | 0.60 – 0.75 | Binary classification benchmark |
| Accuracy | 0.65 – 0.80 | Sınıf dağılımına bağlı |

---

## 12. 🔍 İlgili Akademik Referanslar

1. **Fathalla, A. et al. (2020)** — "Deep end-to-end learning for price prediction of second-hand items" — *Knowledge and Information Systems* — 72 atıf
2. **Han, L. et al. (2020)** — "Price suggestion for online second-hand items with texts and images" — *ACM Multimedia*
3. **Saito, F. et al. (2021)** — "Machine Learning for Demand Prediction of Seasonal Second-hand Fashion Items" — *IEEE ICDMW*
4. **Niederlaender, M. et al. (2025)** — "Garment Returns Prediction with Feature Importance" — *SN Computer Science*
5. **Malmgård, T. (2021)** — "Second-hand goods classification with CNNs" — *KTH Thesis*
6. **Öztürk, S. (2020)** — "Hızlı moda sektöründe makine öğrenmesi yöntemleri ile satış miktarlarının tahmin edilmesi" — *İTÜ Tezi*
7. **Wang, H. et al. (2025)** — "LLP: LLM-based Product Pricing in E-commerce" — *arXiv*
8. **Özkaya, B. & Kazançoğlu, İ. (2021)** — "Y Kuşağının İkinci El Tüketim Motivasyonları" — *Journal of Business in Digital Age*

---

## 13. ✅ Sonraki Adımlar

Rapor onaylandıktan sonra aşağıdaki sırayla geliştirmeye başlayacağız:

- [ ] **Adım 1:** Proje yapısını oluştur (klasörler, `requirements.txt`, `.gitignore`)
- [ ] **Adım 2:** Dolap scraper prototipi geliştir (tek bir ürün sayfası parse)
- [ ] **Adım 3:** Kategori crawler'ı yaz (toplu ürün URL'si toplama)
- [ ] **Adım 4:** Satıcı bilgisi parser'ı yaz
- [ ] **Adım 5:** Veritabanı şemasını oluştur
- [ ] **Adım 6:** 7-gün durum kontrol mekanizmasını kur
- [ ] **Adım 7:** Feature engineering pipeline
- [ ] **Adım 8:** EDA notebook'u
- [ ] **Adım 9:** Model eğitim pipeline'ı
- [ ] **Adım 10:** Değerlendirme ve raporlama

---

> 💡 **Not:** Bu rapor, projenin başlangıç aşaması için hazırlanmış olup, geliştirme sürecinde güncellenecektir. Her aşamada elde edilen bulgulara göre strateji revize edilebilir.
