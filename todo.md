# 📋 Dolap Sale Prediction — Master TODO

> **Son güncelleme:** 2026-03-02
> **Branch:** `develop`
> **Durum:** Phase 3 tamamlandı → M1 Data Collection devam ediyor

---

## Proje Haritası

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DOLAP SALE PREDICTION — ROADMAP                      │
│                                                                         │
│  🏗️ M0 — FOUNDATION                                        [████████] ✅│
│  ├── Phase 0   — Project Architecture                                   │
│  ├── Phase 0.5 — ML Infrastructure (Experiment Tracking)                │
│  └── Phase 1   — Literature Research & Project Report                   │
│                                                                         │
│  🌐 M1 — DATA COLLECTION SYSTEM                            [████░░░░] 🔄│
│  ├── Phase 2   — Dolap Site Reverse Engineering                         │
│  ├── Phase 3   — Basic Scraper Prototype                                │
│  ├── Phase 4   — Anti-Ban Protection                                    │
│  └── Phase 5   — Snapshot Storage System                                │
│                                                                         │
│  ⏳ M2 — TEMPORAL LABELING SYSTEM                           [░░░░░░░░] ⏳│
│  ├── Phase 6   — 7-Day Labeling Mechanism                               │
│  └── Phase 7   — First Cohort: Collect → Wait 7d → Re-check            │
│                                                                         │
│  🧹 M3 — DATA PROCESSING & FEATURE ENGINEERING              [░░░░░░░░] ⏳│
│  ├── Phase 8   — Data Cleaning Pipeline                                 │
│  ├── Phase 9   — Feature Engineering                                    │
│  └── Phase 10  — EDA Notebook                                           │
│                                                                         │
│  🤖 M4 — MODELING                                           [░░░░░░░░] ⏳│
│  ├── Phase 11  — Baseline Models                                        │
│  ├── Phase 12  — Advanced Models (XGB / LGBM / CatBoost)               │
│  ├── Phase 13  — Class Imbalance Handling                               │
│  └── Phase 14  — Hyperparameter Tuning (Optuna)                        │
│                                                                         │
│  📊 M5 — EVALUATION & EXPLAINABILITY                        [░░░░░░░░] ⏳│
│  ├── Phase 15  — Test Set Evaluation                                    │
│  ├── Phase 16  — SHAP Analysis                                          │
│  └── Phase 17  — Visualization Suite                                    │
│                                                                         │
│  📝 M6 — REPORTING & DELIVERY                               [░░░░░░░░] ⏳│
│  ├── Phase 18  — Final Analysis Report                                  │
│  └── Phase 19  — Presentation / Paper Draft                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ M0 — FOUNDATION

### Phase 0 — Project Architecture `fa1b082`
> commit: `chore: initialize project architecture`

- [x] Klasör yapısı oluştur (`src/`, `data/`, `artifacts/`, `configs/`, `docs/`, `tests/`, `notebooks/`, `reports/`)
- [x] Alt paketler (`src/scraping/`, `src/labeling/`, `src/features/`, `src/models/`, `src/evaluation/`, `src/utils/`, `src/pipelines/`, `src/preprocessing/`, `src/dataset/`)
- [x] Senior-grade `.gitignore` (data, artifacts, .env, __pycache__, notebooks checkpoints, IDE)
- [x] `requirements.txt` (scraping + data + ML + viz + test + quality)
- [x] `pyproject.toml` (black, ruff, pytest konfigürasyonu)
- [x] `.env.example`
- [x] `README.md`
- [x] Branch stratejisi: `main` (stable) / `develop` (active) / `feature/*`
- [x] GitHub repo: `thefcan/dolap-sale-prediction`

### Phase 0 — Restructuring `2c5e63a`
> commit: `chore: restructure artifacts, data snapshots, configs & pipeline entrypoints`

- [x] `models/` → `artifacts/models/` migration + `artifacts/figures/` + `artifacts/metrics/`
- [x] Cohort-bazlı data yapısı: `data/raw_snapshots/`, `data/labels/`, `data/interim/`, `data/processed/`
- [x] `data/README.md` — veri akışı dokümantasyonu
- [x] Config YAML'ları: `scraping.yaml`, `features.yaml`, `model.yaml`, `pipeline.yaml`
- [x] Pipeline entrypoint iskeletleri: `scrape.py`, `label.py`, `build_dataset.py`, `train.py`, `evaluate.py`

### Phase 0.5 Part 1 — Experiment Tracking Foundation `11f2683`
> commit: `feat: experiment tracking foundation`

- [x] `src/utils/experiment.py` — `create_experiment()`, `save_metadata()`, `get_git_commit_hash()`
- [x] `src/utils/config_snapshot.py` — `snapshot_configs()` (YAML freeze per experiment)
- [x] `src/utils/data_version.py` — `compute_dataset_hash()` SHA-256 fingerprint
- [x] `src/utils/seed.py` — `set_global_seed()` (random, numpy, torch, PYTHONHASHSEED)
- [x] `artifacts/experiments/` dizini + `.gitignore` kuralı
- [x] `configs/pipeline.yaml` güncelleme (`artifacts_experiments` path)

### Phase 0.5 Part 2 — Reproducible Training Pipeline `3cc0f6b`
> commit: `feat: reproducible training pipeline integration`

- [x] `src/utils/split.py` — `temporal_train_val_test_split()` (kesinlikle zaman bazlı, shuffle YOK)
- [x] `src/utils/metrics.py` — `compute_classification_metrics()` + `save_metrics()` (JSON)
- [x] `src/utils/logger.py` — loguru structured logging + `experiment_id` injection
- [x] `src/pipelines/train.py` — tam experiment lifecycle (10 adım)
- [x] `src/utils/__init__.py` — tüm public API'leri re-export

### Phase 1 — Literature Research & Project Report ✅
> Dosya: `docs/PROJE_RAPORU.md` (575 satır)

- [x] Google Scholar taraması — Dolap.com üzerine ML çalışması **YOK** (teyit edildi)
- [x] Benzer platform çalışmaları (Mercari, ZOZOUSED, genel)
- [x] Özgünlük değerlendirmesi (platform + görev + coğrafi + metodolojik)
- [x] Platform analizi — URL yapısı, HTML structure, ürün sayfası veri haritası
- [x] 25+ özellik tanımı (listing, seller, engagement, derived)
- [x] 5-tier marka kademe sistemi (Budget → Luxury)
- [x] Scraping mimarisi (Phase 1-2-3 diyagramı)
- [x] 5 model önerisi + deneysel tasarım
- [x] 6 değerlendirme metriği + sınıf dengesizliği stratejileri
- [x] 6 haftalık zaman çizelgesi
- [x] Risk analizi (7 risk + azaltma stratejileri)
- [x] 8 akademik referans

---

## 🌐 M1 — DATA COLLECTION SYSTEM

### Phase 2 — Dolap Site Reverse Engineering `8bacbfc`
> commit: `feat: dolap site reverse engineering`

- [x] Dolap.com `robots.txt` analizi ve uyumluluk notu
- [x] Listing URL pattern tespiti ve doğrulama
  - Örnek: `dolap.com/urun/{marka}-{renk}-{kategori}-{durum}-{satici}-{id}`
- [x] Kategori sayfası pagination yapısı
  - Sayfa numaralama: query param (`?sayfa=N`) + SPA rendering
  - Bir sayfada ~20 ilan
- [x] Ürün detay sayfası HTML structure mapping
  - Fiyat selector
  - Marka selector
  - Durum etiketi selector
  - Fotoğraf sayısı selector
  - Açıklama selector
  - Beden / renk selector
  - Kargo bilgisi selector
- [x] Satıcı profil sayfası yapısı
  - Rating/değerlendirme sayısı
  - Toplam satış
  - Hesap yaşı (mümkünse → elde edilemiyor)
- [x] **"Satıldı" badge detection** — HTML'de nasıl görünüyor?
  - CSS class? Text? Overlay?
  - 404 vs "Satıldı" vs "Kaldırıldı" ayrımı
- [x] JavaScript-rendered content var mı? (SSR vs CSR tespiti)
  - **Cloudflare WAF** tüm HTTP client'ları blokluyor (403)
  - **Selenium zorunlu** — real browser gerekiyor
  - Kategori sayfaları: SPA (JS render)
  - Ürün detay sayfaları: SSR benzeri (HTML'de mevcut)
- [x] Dolap API endpoint keşfi (network tab analizi)
  - `/api/product/{id}` ve `/rest/product/{id}` → 403 bloklu
  - `public-mdc.dolap.com` → DNS çözünemiyor
- [x] `docs/DOLAP_SITE_MAP.md` — tüm bulguları dokümante et (354 satır, 14 bölüm)
- [x] Test: 3-5 farklı kategoriden elle 1'er ilan parse et

### Phase 3 — Basic Scraper Prototype `(commit pending)`
> commit hedefi: `feat: basic scraper prototype`

- [x] `src/scraping/scraper.py` — Selenium-based DolapScraper sınıfı
  - WebDriver lifecycle (headless Chrome, anti-detection flags)
  - Cloudflare bypass (real browser rendering)
  - `crawl_category()` → kategori sayfalarından ilan URL'leri
  - `scrape_listing()` → tekil ilan detay parse
  - `scrape_listings_batch()` → toplu scrape + JSONL streaming
  - `scrape_category()` → end-to-end kategori pipeline
  - Random delay, retry logic, exponential backoff
- [x] `src/scraping/parsers.py` — 17 HTML parser fonksiyonu (~400 satır)
  - `parse_product_detail()` → ana parser (20+ alan)
  - `parse_listing_urls_from_page()` → kategori sayfası URL extraction
  - `extract_listing_id_from_url()` → URL'den listing ID
  - Graceful error handling, `_parse_errors` tracking
- [x] Çekilecek alanlar:
  - `listing_id`, `url`, `title`, `price`, `original_price`
  - `brand`, `category`, `subcategory`
  - `size`, `color`, `condition`
  - `photo_count`, `description_length`, `description_text`, `description_word_count`
  - `seller_username`, `seller_listing_count`
  - `has_discount`, `shipping_info`, `shipping_buyer_pays`
  - `like_count`, `comment_count`
  - `is_sold`, `scraped_at`
- [x] Kategori crawler: verilen kategori slug → ilan URL listesi
- [x] `src/scraping/__init__.py` — Public API re-exports
- [x] `src/pipelines/scrape.py` — Full implementation (skeleton → gerçek)
  - `--cohort-id`, `--categories`, `--max-pages`, `--dry-run`, `--no-headless`
  - Cohort dizini oluşturma, JSONL output, `meta.yaml` üretimi
- [ ] CSV/JSONL test scrape (~50 ilan) → Phase 5'te gerçek cohort ile
- [ ] Manuel doğrulama: scrape edilen 10 ilan vs site gerçek değerleri
- [ ] `notebooks/01_scraping_test.ipynb` — scrape sonuçları inceleme

### Phase 4 — Anti-Ban Protection
> commit hedefi: `feat: anti-ban protection layer`
> ℹ️ Bazı maddeler Phase 3'te DolapScraper içinde temel düzeyde implemente edildi.

- [x] Random User-Agent rotation (10 farklı UA) — `scraper.py` _USER_AGENTS
- [x] Random request delay (config'den: `min_seconds` / `max_seconds`) — `scraper.py` `_sleep()`
- [x] Exponential backoff retry logic (max 3 retry) — `scraper.py` `_navigate()`
- [x] Timeout handling (30s default) — `scraper.py` `set_page_load_timeout()`
- [ ] HTTP status code handling (429, 403, 503 → backoff)
- [ ] Optional: proxy support altyapısı (config'de var, implementasyon)
- [ ] Optional: cookie/session management
- [ ] Rate limiter sınıfı: `src/scraping/rate_limiter.py`
- [ ] Banlama tespiti: ardışık 403/429 → otomatik durma + uyarı logu
- [ ] Test: 200 ilan çek, ban yemeden tamamla

### Phase 5 — Snapshot Storage System ⭐
> commit hedefi: `feat: snapshot storage system`

- [ ] Her scrape çalışması = 1 cohort = 1 snapshot dosyası
- [ ] Dosya adlandırma: `data/raw_snapshots/cohort_{YYYYMMDD}/listings.jsonl`
- [ ] Snapshot **ASLA overwrite EDİLMEZ** — append-only
- [ ] Her satır: `listing_id` + `scrape_date` + tüm alanlar
- [ ] `src/scraping/storage.py` — snapshot writer sınıfı
- [ ] `src/pipelines/scrape.py` implementasyonu (skeleton → gerçek)
- [ ] Scrape özet logu: kaç ilan, kaç kategori, kaç hata, süre
- [ ] SQLite state tracking: hangi cohort ne zaman scrape edildi
- [ ] İlk gerçek cohort scrape'i: `cohort_20260301` (~1000+ ilan)

---

## ⏳ M2 — TEMPORAL LABELING SYSTEM

> **⚠️ PROJENİN ALTIN NOKTASI**
> Ground truth doğal olarak Dolap'tan elde ediliyor — ama bu 7 günlük
> bekleme süresini disiplinli yönetmeyi gerektiriyor.

### Phase 6 — 7-Day Labeling Mechanism
> commit hedefi: `feat: temporal labeling mechanism`

- [ ] `src/labeling/status_checker.py` — ilan durum kontrol sınıfı
  - URL'yi ziyaret et
  - HTTP 404/410 → `removed`
  - "Satıldı" badge → `sold_within_7_days = 1`
  - Hâlâ aktif → `sold_within_7_days = 0`
  - Sayfa parse hatası → `error` (ayrı kaydet)
- [ ] `src/labeling/labeler.py` — batch labeling orchestrator
  - Bir cohort'taki tüm ilanları sırayla kontrol et
  - Anti-ban kurallarına uy (Phase 4'ten miras)
- [ ] Label output: `data/labels/cohort_{YYYYMMDD}.jsonl`
  - Her satır: `{listing_id, url, status, sold_within_7_days, checked_at}`
- [ ] `src/pipelines/label.py` implementasyonu (skeleton → gerçek)
- [ ] Edge case'ler:
  - İlan silindi ama satılmadı → `removed_unsold` (veri setinden çıkar veya ayrı sınıf)
  - İlan fiyatı değişti → logla (fiyat değişimi feature olabilir)
  - İlan hâlâ aktif ama 404 → retry logic
- [ ] Labeling süreci logu: `X satıldı / Y aktif / Z hata`

### Phase 7 — First Cohort Lifecycle
> commit hedefi: `feat: first cohort labeled`

- [ ] **Gün 1:** Cohort_01 scrape (~1000+ ilan)
- [ ] **Gün 2-7:** Bekleme (isteğe bağlı: Cohort_02 scrape başlat)
- [ ] **Gün 8:** Cohort_01 re-check → labeling
- [ ] Label dağılımı analizi: sold vs not_sold oranı
- [ ] Veri kalitesi raporu: eksik alanlar, parse hataları
- [ ] **Gün 8+:** Cohort_02, Cohort_03... paralel devam
- [ ] Hedef: minimum 3 cohort, 3000+ etiketli ilan

---

## 🧹 M3 — DATA PROCESSING & FEATURE ENGINEERING

### Phase 8 — Data Cleaning Pipeline
> commit hedefi: `feat: data cleaning pipeline`

- [ ] `src/preprocessing/cleaner.py`
  - Duplicate detection & removal (aynı `listing_id`)
  - Missing value analizi + imputation stratejisi
  - Outlier detection (fiyat, description_length)
  - Data type validation (price → float, date → datetime)
  - Tutarsız kayıtları logla ve filtrele
- [ ] `src/dataset/merger.py`
  - Raw snapshots + labels → merged interim file
  - Cohort-bazlı merge: `data/interim/merged_{cohort_id}.parquet`
  - Tüm cohort'ları birleştir: `data/interim/merged_all.parquet`
- [ ] `src/pipelines/build_dataset.py` implementasyonu — cleaning step

### Phase 9 — Feature Engineering
> commit hedefi: `feat: feature engineering pipeline`

- [ ] `src/features/engineer.py` — ana feature engineering sınıfı
- [ ] **İlan özellikleri:**
  - `price` (ham)
  - `price_to_category_median` (fiyat / kategori medyan fiyatı)
  - `photo_count`
  - `description_length` (char count)
  - `description_word_count`
  - `listing_hour` (0-23)
  - `is_weekend_listing`
  - `has_discount`
  - `shipping_buyer_pays`
- [ ] **Marka kademesi:**
  - `brand_tier` (1-5, `configs/features.yaml`'dan)
  - Bilinmeyen marka → tier 0 veya median tier
- [ ] **Durum etiketi:**
  - `condition` ordinal encoding (Yeni & Etiketli=3, Yeni=2, Az Kullanılmış=1, Kullanılmış=0)
- [ ] **Kategorik encoding:**
  - `category` → target encoding
  - `color` → target encoding
  - `size` → ordinal/target encoding
- [ ] **Satıcı özellikleri:**
  - `seller_rating_count`
  - `seller_sales_count` (mümkünse)
- [ ] **Metin özellikleri:**
  - `desc_has_urgency_keyword` (acil, son fiyat, indirim, fırsat, pazarlık)
- [ ] Oluşturulan feature'ların `configs/features.yaml` ile tutarlılık kontrolü
- [ ] Final output: `data/processed/dataset.parquet`
- [ ] Feature listesi metadata'ya kaydet

### Phase 10 — Exploratory Data Analysis (EDA)
> commit hedefi: `feat: EDA notebook`

- [ ] `notebooks/01_eda.ipynb`
- [ ] Temel istatistikler: satır sayısı, sütun tipleri, missing ratio
- [ ] Target dağılımı: `sold_within_7_days` → class balance
- [ ] Fiyat dağılımı (histogram, boxplot, kategori bazlı)
- [ ] Marka tier dağılımı
- [ ] Durum etiketi dağılımı
- [ ] Fotoğraf sayısı vs satış oranı
- [ ] Fiyat/medyan oranı vs satış oranı
- [ ] Satıcı deneyimi vs satış oranı
- [ ] Korelasyon matrisi (numerik features)
- [ ] Kategori bazlı satış oranları
- [ ] Zaman bazlı trendler (ilan saati, gün)
- [ ] Sınıf dengesizliği analizi ve strateji önerisi

---

## 🤖 M4 — MODELING

### Phase 11 — Baseline Models
> commit hedefi: `feat: baseline models`

- [ ] `src/models/baseline.py` — Logistic Regression
- [ ] Logistic Regression eğitimi (class_weight="balanced")
- [ ] Random Forest eğitimi
- [ ] Dummy classifier (stratified) — alt sınır belirleme
- [ ] Val set üzerinde metrikler: AUC-ROC, F1, Precision, Recall
- [ ] Baseline sonuçları → experiment dizinine kaydet
- [ ] İlk karşılaştırma tablosu

### Phase 12 — XGBoost Deep Dive
> commit hedefi: `feat: xgboost training`

- [ ] `src/models/tree_models.py` — XGBoost wrapper
- [ ] XGBoost eğitimi (early stopping on val)
- [ ] Feature importance (gain, weight, cover)
- [ ] Val set karşılaştırması (vs baseline)
- [ ] Tüm sonuçlar experiment dizinine

### Phase 13 — Class Imbalance Handling
> commit hedefi: `feat: class imbalance strategies`

- [ ] SMOTE deneyi (imbalanced-learn)
- [ ] Class weight deneyi (her model için)
- [ ] Threshold tuning (F1-maximize / Youden's J)
- [ ] Undersampling deneyi
- [ ] İmbalance stratejisi karşılaştırma tablosu
- [ ] En iyi stratejiyi seç → metadata'ya kaydet

### Phase 14 — Hyperparameter Tuning
> commit hedefi: `feat: optuna hyperparameter tuning`

- [ ] `src/models/tuner.py` — Optuna objective fonksiyonları
- [ ] XGBoost Optuna study (100 trial)
- [ ] Study visualization (parallel coordinate, importance)
- [ ] Tuned XGBoost → final val score
- [ ] Tuning sonuçları → experiment dizinine

---

## 📊 M5 — EVALUATION & EXPLAINABILITY

### Phase 15 — Test Set Evaluation
> commit hedefi: `feat: test set evaluation`

- [ ] Final model → test set prediction
- [ ] `src/evaluation/evaluator.py`
- [ ] Metrikler: AUC-ROC, F1, Precision, Recall, PR-AUC, Accuracy
- [ ] Optimal threshold on val → apply on test
- [ ] Confusion matrix
- [ ] Classification report
- [ ] Sonuçları experiment dizinine kaydet

### Phase 16 — SHAP Analysis
> commit hedefi: `feat: SHAP explainability`

- [ ] `src/evaluation/shap_analysis.py`
- [ ] SHAP beeswarm plot (top 20 features)
- [ ] SHAP waterfall (tek örnek açıklama)
- [ ] SHAP dependence plots (top 3-5 feature)
- [ ] Feature importance ranking (SHAP-based vs model-based karşılaştırma)
- [ ] Figures → `artifacts/experiments/<exp>/figures/`

### Phase 17 — Visualization Suite
> commit hedefi: `feat: evaluation visualization suite`

- [ ] `src/evaluation/plots.py`
- [ ] ROC curve (tüm modeller aynı grafikte)
- [ ] Precision-Recall curve
- [ ] Calibration plot
- [ ] Feature importance bar chart
- [ ] Confusion matrix heatmap
- [ ] Threshold vs F1 grafiği
- [ ] Tüm figürler → experiment dizinine

---

## 📝 M6 — REPORTING & DELIVERY

### Phase 18 — Final Analysis Report
> commit hedefi: `feat: final analysis report`

- [ ] `reports/FINAL_REPORT.md` veya `.pdf`
- [ ] Yönetici özeti
- [ ] Veri toplama süreci ve zorluklar
- [ ] Feature engineering kararları ve gerekçeleri
- [ ] Model karşılaştırma tablosu
- [ ] En iyi modelin SHAP analizi yorumu
- [ ] Sınıf dengesizliği çözüm karşılaştırması
- [ ] Pratik öneriler: satıcılara fiyatlama/ilan tavsiyeleri
- [ ] Limitasyonlar ve gelecek çalışmalar
- [ ] Akademik referanslar

### Phase 19 — Presentation / Paper Draft
> commit hedefi: `feat: presentation`

- [ ] Sunum slaytları (10-15 slayt)
  - Problem tanımı
  - Veri toplama yaklaşımı (temporal labeling)
  - Feature engineering
  - Model sonuçları
  - SHAP açıklanabilirlik
  - Sonuç ve öneriler
- [ ] (Opsiyonel) Kısa makale taslağı

---

## 📊 İlerleme Özeti

| Milestone | Durum | Tamamlanan Phase |
|-----------|-------|------------------|
| 🏗️ M0 — Foundation | ✅ Tamamlandı | Phase 0, 0.5, 1 |
| 🌐 M1 — Data Collection | 🔄 Devam Ediyor | Phase 2, 3 |
| ⏳ M2 — Temporal Labeling | ⏳ Bekliyor | — |
| 🧹 M3 — Data Processing | ⏳ Bekliyor | — |
| 🤖 M4 — Modeling | ⏳ Bekliyor | — |
| 📊 M5 — Evaluation | ⏳ Bekliyor | — |
| 📝 M6 — Reporting | ⏳ Bekliyor | — |

## 📌 Commit Geçmişi

| # | Hash | Mesaj | Branch |
|---|------|-------|--------|
| 1 | `fa1b082` | `chore: initialize project architecture` | develop |
| 2 | `2c5e63a` | `chore: restructure artifacts, data snapshots, configs & pipeline entrypoints` | develop |
| 3 | `11f2683` | `feat: experiment tracking foundation` | develop |
| 4 | `3cc0f6b` | `feat: reproducible training pipeline integration` | develop |
| 5 | `c2f4805` | `merge: sync develop into main (Phase 0 + 0.5)` | main |
| 6 | `556c8a7` | `merge: sync develop into main (Phase 0.5 Part 2)` | main |
| 7 | `8bacbfc` | `feat: dolap site reverse engineering` | develop |
| 8 | `(pending)` | `feat: basic scraper prototype` | develop |

## 🏗️ Altyapı Envanteri

### ✅ Implementasyon Tamamlanan Modüller
```
src/utils/
├── experiment.py       ← create_experiment, save_metadata, get_git_commit_hash
├── config_snapshot.py  ← snapshot_configs
├── data_version.py     ← compute_dataset_hash, compute_file_hash
├── seed.py             ← set_global_seed (random, numpy, torch, PYTHONHASHSEED)
├── split.py            ← temporal_train_val_test_split (zaman bazlı, shuffle YOK)
├── metrics.py          ← compute_classification_metrics, save_metrics
├── logger.py           ← setup_logging, get_logger (loguru + experiment_id)
└── __init__.py         ← tüm public API re-export
```

### ✅ Konfigürasyon Dosyaları
```
configs/
├── scraping.yaml       ← 12 kategori, rate limiting, labeling kuralları
├── features.yaml       ← brand tiers, condition mapping, feature tanımları
└── model.yaml          ← 3 model config (LR, RF, XGB), seed, split oranları, Optuna, evaluation
└── pipeline.yaml       ← paths, logging, database URL, step enable/disable
```

### ✅ Scraping Modülü (Phase 2-3)
```
src/scraping/
├── __init__.py         ← Public API re-exports (DolapScraper, parsers)
├── parsers.py          ← 17 HTML parse fonksiyonu (~400 satır)
└── scraper.py          ← Selenium-based DolapScraper sınıfı (~330 satır)
```

### ⏳ İskelet (Skeleton) — İmplementasyon Bekliyor
```
src/pipelines/
├── train.py            ← ✅ TAM İMPLEMENTASYON (experiment lifecycle)
├── scrape.py           ← ✅ TAM İMPLEMENTASYON (Phase 3)
├── label.py            ← ⏳ İskelet (Phase 6'da implement edilecek)
├── build_dataset.py    ← ⏳ İskelet (Phase 8-9'da implement edilecek)
└── evaluate.py         ← ⏳ İskelet (Phase 15-17'de implement edilecek)

src/labeling/           ← ⏳ Boş (Phase 6-7)
src/preprocessing/      ← ⏳ Boş (Phase 8)
src/features/           ← ⏳ Boş (Phase 9)
src/dataset/            ← ⏳ Boş (Phase 8)
src/models/             ← ⏳ Boş (Phase 11-14)
src/evaluation/         ← ⏳ Boş (Phase 15-17)
```

---

## ⚡ Sonraki Adım

> **Phase 4 — Anti-Ban Protection**
>
> Mevcut scraper'ın rate limiting ve retry mekanizmalarını
> güçlendir. Proxy desteği, ban tespiti, session yönetimi ekle.
> Ardından Phase 5 (Snapshot Storage) ile ilk gerçek cohort
> scrape'ini gerçekleştir.
