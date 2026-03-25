# 📋 Dolap Sale Prediction — Master TODO

> **Son güncelleme:** 2026-03-24 (M3 Phase 9.1 RC1/RC2/RC3 ✅, RC4 ⏳)
> **Branch:** `develop` | **Son commit:** `0d22d9c`
> **Durum:** M1 ✅ | EDA ✅ | M2 🟡 scrape ✅ labeling tamamlandı | **M3 Phase 8 ✅ + Phase 9.1 (RC1/RC2/RC3) ✅, RC4 ⏳**
> **Öncelik:** Phase 9.1 Root Cause Plan (RC4) + EDA gate senkronizasyonu

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
│  🌐 M1 — DATA COLLECTION SYSTEM                            [████████] ✅│
│  ├── Phase 2   — Dolap Site Reverse Engineering              ✅         │
│  ├── Phase 3   — Basic Scraper Prototype                     ✅         │
│  ├── Phase 4   — Anti-Ban Protection                         ✅         │
│  └── Phase 5   — Snapshot Storage System                     ✅         │
│                                                                         │
│  🎤 EDA PRESENTATION (Practical Data Science)               [███████░] 🟡│
│  ├── Step 0  — Data Acquisition (scrape + pseudo-label)      ✅         │
│  ├── Step 1  — Notebook Skeleton & Problem Formulation       ✅         │
│  ├── Step 2  — Data Collection Narrative                     ✅         │
│  ├── Step 3  — Schema Check & Missing Values                 ✅         │
│  ├── Step 4  — Descriptive Statistics                        ✅         │
│  ├── Step 5  — Feature Distributions                         ✅         │
│  ├── Step 6  — Relationships & Correlations                  ✅         │
│  ├── Step 7  — Feature Engineering Decisions                 ✅         │
│  ├── Step 8  — Investigation (Data Quality Bugs)             ✅         │
│  └── Step 9  — Presentation Polish & Rehearsal               🟡 prova  │
│                                                                         │
│  🟡 M2 — TEMPORAL LABELING SYSTEM                           [██████░░] 🟡│
│  ├── Phase 6   — 7-Day Labeling Mechanism                    ✅         │
│  └── Phase 7   — First Cohort: Collect ✅ → Wait 7d → Re-check ⏳      │
│                                                                         │
│  🧹 M3 — DATA PROCESSING & FEATURE ENGINEERING              [█░░░░░░░] 🟡│
│  ├── Phase 8   — Data Cleaning Pipeline                                 │
│  ├── Phase 9   — Feature Engineering                                    │
│  └── Phase 10  — EDA Notebook (merged into EDA Presentation)            │
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

### Phase 3 — Basic Scraper Prototype `42ef94f`
> commit: `feat: basic scraper prototype`

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
- [x] CSV/JSONL test scrape → Phase 5'te 411 ilan gerçek cohort ile tamamlandı
- [ ] Manuel doğrulama: scrape edilen 10 ilan vs site gerçek değerleri → **M2'ye ertelendi**
- [x] ~~`notebooks/01_scraping_test.ipynb`~~ → `01_eda_presentation.ipynb`'ye merge edildi

### Phase 4 — Anti-Ban Protection ✅
> commit hedefi: `feat: anti-ban protection layer`
> ℹ️ Temel maddeler Phase 3'te DolapScraper içinde implemente edilmişti.
> Phase 4 kapsamında `rate_limiter.py` modülü oluşturuldu ve scraper'a tam entegrasyon sağlandı.

- [x] Random User-Agent rotation (10 farklı UA) — `scraper.py` _USER_AGENTS
- [x] Random request delay (config'den: `min_seconds` / `max_seconds`) — `scraper.py` `_sleep()`
- [x] Exponential backoff retry logic (max 3 retry) — `scraper.py` `_navigate()`
- [x] Timeout handling (30s default) — `scraper.py` `set_page_load_timeout()`
- [x] HTTP status code handling (429, 403, 503 → backoff) — `scraper.py` `_detect_http_status()` + `_navigate()` içinde adaptive backoff
- [x] Proxy support altyapısı — `rate_limiter.py` `build_proxy_options()` + `scraper.py` `start()` içinde Chrome arg injection
- [x] Cookie/session management — `rate_limiter.py` `SessionManager` sınıfı (save/load/clear cookies, JSON persistence)
- [x] Rate limiter sınıfı: `src/scraping/rate_limiter.py` — `RateLimiter` (adaptive delay, escalation/de-escalation)
- [x] Banlama tespiti: ardışık 403/429 → otomatik durma + uyarı logu — `BanDetector` sınıfı + `BanDetectedError` exception
- [x] Test: 411 ilan çekildi, ban yemeden tamamlandı (Step 0 pilot cohort)

### Phase 5 — Snapshot Storage System ✅
> commit hedefi: `feat: snapshot storage system`

- [x] Her scrape çalışması = 1 cohort = 1 snapshot dosyası
- [x] Dosya adlandırma: `data/raw_snapshots/cohort_{YYYYMMDD}/listings.jsonl`
- [x] Snapshot **ASLA overwrite EDİLMEZ** — append-only
- [x] Her satır: `listing_id` + `scrape_date` + tüm alanlar
- [x] `src/scraping/storage.py` — SnapshotWriter sınıfı (append-only JSONL, dedup, per-category + combined, meta.yaml) + CohortStateTracker (SQLite lifecycle)
- [x] `src/pipelines/scrape.py` implementasyonu — SnapshotWriter + CohortStateTracker entegrasyonu tamamlandı
- [x] Scrape özet logu: kaç ilan, kaç kategori, kaç hata, süre (SnapshotWriter.stats + meta.yaml)
- [x] SQLite state tracking: hangi cohort ne zaman scrape edildi (CohortStateTracker.register_cohort)
- [x] İlk gerçek cohort scrape'i: `cohort_20250712` — 3 kategori (kazak: 195, elbise: 108, mont: 108) = **411 ilan**, 12 satıcı, ~36 dk

---

## 🎤 EDA PRESENTATION — Practical Data Science Dersi

> **🔴 ÖNCELİK: EN YÜKSEK — Sunum tarihinden önce tamamlanmalı**
> **Format:** 10 dakika | İngilizce | Jupyter Notebook üzerinden sunum
> **Şablon:** Classification template (target: `sold_within_7_days`, binary)
> **Kural:** Tüm takım üyeleri en az 1 bölüm sunmalı | Kod gizli (Show/Hide Code butonu)

### Step 0 — Data Acquisition ✅ (pilot scope)
> ✅ Pilot cohort toplandı (411 ilan). Proxy label oluşturuldu. Genişletme M2'ye ertelendi.

- [x] Selenium + Chrome WebDriver kurulumunu doğrula (Selenium 4.41.0, Chrome 145)
- [x] Pilot scrape çalıştır — 3 kategori × 2 sayfa (411 ilan):
  ```
  python -m src.pipelines.scrape --cohort-id 20250712 --max-pages 2 --categories kazak elbise mont --no-headless
  ```
- [x] JSONL çıktı dosyalarını doğrula: `data/raw_snapshots/cohort_20250712/*.jsonl`
  - kazak.jsonl (195), elbise.jsonl (108), mont.jsonl (108), listings.jsonl (411), meta.yaml
  - Field coverage: price, brand, condition, likes, photos %100 dolu
  - Price: 40-12000 TL, avg 523 TL | Likes: 0-123, avg 10.0 | 12 unique seller
- [ ] ~~Genişletilmiş scrape — kalan 5 kategori~~ → **M2'ye ertelendi** (EDA sunumu 3 kategori ile yeterli, Conclusion'da limitation olarak belirtildi)
- [x] **Labeling stratejisi kararı** → **Seçenek B (Pragmatik) uygulandı:**
  - ~~**⚠️ DURUM:** Pilot cohort'ta `is_sold` tüm ilanlar için `False` (0/411)~~
  - ✅ `proxy_sold` = engagement-based label (`like_count >= Q75 per category`)
  - `src/preprocessing/clean_features.py` içinde üretiliyor → `cohort_20250712_cleaned.csv`
  - Notebook'ta 6+ yerde açıkça "proxy label" olduğu belirtildi
  - Gerçek label: M2 Phase 6 (T+7 re-check) ile gelecek
- [x] ~~Seçilen stratejiye göre label dosyası oluştur~~ → proxy label doğrudan cleaned CSV içinde (`proxy_sold` sütunu)
- [x] Scrape kalitesi hızlı kontrol: `scripts/validate_cohort.py` ile doğrulandı
- [x] JSONL'leri pandas DataFrame'e yükle, temel sanity check → notebook Cell 5 (411×40, 3 kategori)

### Step 0.5 — Feature Cleaning & Proxy Label (⚠️ HOCA GERİ BİLDİRİMİ)
> 🔴 Ham veri üzerinden grafik çizmek YANLIŞ — önce veri temizlenmeli.
> Hoca: "features ve yapılan grafikler yanlış olmuş, grafik yanlışı demek veri üzerinde ekstra çalışmak demek"

**Feature Temizleme (grafik çizmeden ÖNCE yapılmalı):**
- [x] `brand` alanını split et → `brand_clean` + `size_extracted` ("Zara - S / 36 Beden" → brand="Zara", size="S / 36 Beden")
- [x] `condition` normalize et ("Yeni ve Etiketli" → "Yeni & Etiketli")
- [x] `category` = None → `category_scraped` kullan
- [x] `description_text` == `title` olan kayıtları flag'le (`desc_is_placeholder = True`)
- [x] `brand_tier` oluştur — **DATA-DRIVEN** (hoca: manuel değil, median fiyat bazlı)
  - Marka başına median listing price hesapla → quantile bazlı 5 tier
- [x] `has_flaw_mention` feature ekle — keyword: "leke", "yırtık", "bozuk", "hafif", "küçük kusur"
- [x] `desc_has_urgency_keyword` feature ekle — keyword: "acil", "son fiyat", "fırsat", "pazarlık"
- [x] `price_to_category_median` türet (fiyat / kategori median fiyatı)

**Proxy Label (target variable — 7 gün bekleyemiyoruz):**
- [x] Engagement-based proxy target oluştur:
  - `like_count >= median + 1σ` AND `price < category_median` → `proxy_sold = 1`
  - Aksi → `proxy_sold = 0`
  - Sunumda **açıkça** "proxy label" olduğunu belirt
  - Gerçek label: T+7 re-check ile gelecek (Phase 6)

**Eksik Feature'lar (hoca geri bildirimi — acknowledged in notebook):**
- [x] `is_negotiable` — Notebook Section 4 "Features NOT Available" tablosunda belirtildi
- [x] `listing_date` / `day_of_week` — Notebook Section 4 + Conclusion "Missing features" olarak belirtildi
- [x] `label_noise` limitation — Notebook Section 2 "Known Limitations" #1'de acknowledge edildi
- [x] `deleted_listings` policy — Notebook Section 2 "Known Limitations" #2'de belirtildi

### Step 1 — Notebook Skeleton & Section 1: Problem Formulation (~1.5 dk sunum) ✅
> Dosya: `notebooks/01_eda_presentation.ipynb`

- [x] Notebook oluştur: `notebooks/01_eda_presentation.ipynb`
- [x] **Cell 1 (Markdown) — Title Slide:**
  - Proje adı: "Dolap Second-Hand Fashion Sale Prediction"
  - Takım üyeleri, tarih, ders adı
- [x] **Cell 2 (Markdown) — Problem Formulation:**
  - Business objective: "Predict whether a Dolap.com listing will sell within 7 days"
  - ML problem type: Binary Classification
  - Target variable: `sold_within_7_days` (0 = not sold, 1 = sold)
  - Success metric: AUC-ROC (primary — handles class imbalance), F1-score (secondary)
  - Why it matters: Helps sellers optimize pricing, photo count, description quality
  - Domain context: Dolap.com = Turkey's largest second-hand fashion platform (owned by Trendyol)
  - Novelty: First ML study on Dolap.com (confirmed via Google Scholar search)
- [x] **Cell 2b (Markdown) — Hypotheses (⚠️ HOCA İSTEDİ — "exploration değil science"):**
  - **H1:** Listings priced below category median → significantly higher P(sold within 7 days)
  - **H2:** Listings with ≥3 photos → sell faster than single-photo listings, independent of price
  - **H3:** Seller listing count (experience proxy) → stronger predictor than price in competitive categories
  - **H4:** Listings with flaw mentions in description → sell significantly slower than comparable listings
  - Her hipotez EDA boyunca test edilecek ve Step 6'da sonuçları raporlanacak

### Step 2 — Section 2: Data Collection (~1.5 dk sunum) ✅

- [x] **Cell 3 (Code) — Load Data:**
  - JSONL dosyalarını oku → tek DataFrame'e birleştir
  - `df.shape`, `df.columns` göster
- [x] **Cell 4 (Markdown) — Data Source Explanation:**
  - Data source: Dolap.com (Selenium web scraping — Cloudflare WAF bypass required)
  - 12 target categories (kazak, elbise, mont, çizme, bot, kol çantası, ...)
  - Temporal labeling mechanism: T=0 scrape → T+7 days re-check → sold/not-sold label
  - 20+ raw features per listing
  - Cohort-based collection strategy
  - ETL decisions: JSONL streaming output, one file per category per cohort
- [x] **Cell 5 (Code) — Target Distribution:**
  - `sold_within_7_days` (veya `proxy_sold`) value_counts bar chart
  - Class balance ratio hesapla ve yorumla
  - ⚠️ Hoca: "%75-80 not-sold beklenir → accuracy metric kullanma"
  - Primary metric: ROC-AUC | Secondary: F1-score
  - class_weight='balanced' baseline olarak planlandı
  - Eğer pseudo-label kullanıldıysa bunu açıkça belirt: "Proxy label — real label via T+7 re-check"

### Step 3 — Section 3.1: Schema Check & Missing Values (~1 dk sunum) ✅

- [x] **Cell 6 (Code) — Data Types & Info:**
  - `df.info()` özet tablosu
  - Sütun adları, non-null sayıları, dtypes
- [x] **Cell 7 (Code) — Missing Value Audit:**
  - `df.isnull().sum().sort_values(ascending=False)` bar chart
  - Missing value yüzdeleri tablosu (heatmap veya bar)
- [x] **Cell 8 (Markdown) — Missing Value Açıklaması:**
  - `original_price` → NaN if no discount (not random — conditional missingness)
  - `size` → NaN for non-clothing categories (bags, accessories — structurally absent)
  - `color` → URL slug parse failure or rare/unrecognized colors
  - `description_text` → Some sellers don't write descriptions
  - `subcategory` / `category` → Breadcrumb parsing may fail on some pages
  - Her alan için karar: drop / impute (median, mode, "unknown") / flag as feature

### Step 4 — Section 3.2: Descriptive Statistics (~1 dk sunum) ✅

- [x] **Cell 9 (Code) — Statistics Table:**
  - `df.describe()` — styled table (transpose for readability)
  - `df.describe(include='object')` — kategorik sütunlar
- [x] **Cell 10 (Markdown) — Suspicious Values Commentary:**
  - `price` min → 0 veya çok düşük değer varsa: hata mı gerçek mi?
  - `price` max → aşırı yüksek outlier'lar (lüks markalar vs parse hatası)
  - `photo_count` = 0 → parse hatası mı yoksa gerçekten fotoğrafsız ilan mı?
  - `description_length` = 0 → açıklama yazılmamış (gerçek)
  - `like_count` çok yüksek → viral ilan mı yoksa veri hatası mı?
  - `seller_listing_count` aşırı yüksek → profesyonel satıcı mı?
  - Her şüpheli değer için: "error or real" kararını domain bilgisiyle açıkla

### Step 5 — Section 3.3: Feature Distributions (~1.5 dk sunum) ✅

- [x] **Cell 11 (Code) — Numeric Feature Histograms:**
  - `price` histogram → sağa çarpık (right-skewed) beklentisi → log transform notu
  - `photo_count` histogram → çoğu 3-5 arası beklentisi
  - `description_length` histogram
  - `description_word_count` histogram
  - `like_count` histogram → power-law dağılım beklentisi
  - `comment_count` histogram
  - Her histogram için: skewness yorumu, transform gereksinimi notu
- [x] **Cell 12 (Code) — Categorical Feature Bar Charts:**
  - `condition` dağılımı (Yeni & Etiketli / Az Kullanılmış / ...)
  - `brand` top-20 bar chart (veya `brand_tier` eğer türetildiyse)
  - `category` dağılımı
  - `color` dağılımı (top-15)
  - `has_discount` pie/bar chart
  - `shipping_buyer_pays` dağılımı
- [x] **Cell 13 (Code) — Class-Conditional Distributions:**
  - `price` histogram: `sold=0` vs `sold=1` overlay
  - `photo_count`: sold vs not-sold comparison
  - `like_count`: sold vs not-sold comparison
  - `description_length`: sold vs not-sold comparison
  - Hangi feature'lar net separation gösteriyor? → Predictive power ipucu
- [x] **Cell 14 (Code) — Log Transform Before/After (eğer gerekli):**
  - `price` raw vs `log(price)` side-by-side histogram
  - Skewness değeri before/after

### Step 6 — Section 3.4: Relationships & Correlations (~1.5 dk sunum) ✅

- [x] **Cell 15 (Code) — Correlation Heatmap:**
  - Tüm numerik features + target arası Pearson correlation
  - `seaborn.heatmap` annotated, mask upper triangle
  - Top 3 target-correlated feature'ları highlight et
- [x] **Cell 16 (Code) — Top Predictive Features Deep Dive:**
  - Scatter/box plot: `price` vs `sold_within_7_days`
  - Bar chart: `photo_count` vs satış oranı (binned)
  - Bar chart: `brand_tier` vs satış oranı
  - Bar chart: `condition` vs satış oranı
  - Scatter: `price_to_category_median` vs satış oranı (eğer türetildiyse)
- [x] **Cell 17 (Code) — Category-Level Analysis:**
  - Kategori bazlı ortalama fiyat + satış oranı grouped bar chart
  - Hangi kategoriler daha çok satılıyor?
- [x] **Cell 18 (Markdown) — Top 3 Predictive Features Explanation:**
  - Feature 1: Neden tahmin gücü yüksek? Domain açıklaması
  - Feature 2: Neden tahmin gücü yüksek? Domain açıklaması
  - Feature 3: Neden tahmin gücü yüksek? Domain açıklaması
  - Örnek: "Lower-priced items sell faster — buyers on second-hand platforms are price-sensitive"

### Step 7 — Section 4: Feature Engineering Decisions (~1 dk sunum) ✅

- [x] **Cell 19 (Markdown) — Preprocessing Summary Table:**
  | Decision | What | Why |
  |----------|------|-----|
  | Imputation | `original_price` NaN → copy `price`, set `has_discount=False` | Conditional missingness, not random |
  | Imputation | `size` NaN → "unknown" category | Structurally absent for non-clothing |
  | Imputation | `color` NaN → "unknown" | URL parse failure |
  | Outlier | `price` top 1% clip | Extreme luxury items distort model |
  | Outlier | `like_count` top 1% clip | Viral outliers |
  | Encoding | `condition` → ordinal (0-3) | Natural order: Kullanılmış < Az Kullanılmış < Yeni < Yeni & Etiketli |
  | Encoding | `brand` → 5-tier ordinal (Budget→Luxury) **DATA-DRIVEN** | Median price per brand → quantile tiers (hoca: "objective and reproducible") |
  | Encoding | `category`, `color` → target encoding | High cardinality → target-based numeric |
  | Scaling | StandardScaler for LR, none for tree models | LR is distance-based |
  | New Feature | `price_to_category_median` | Relative pricing within category |
  | New Feature | `desc_has_urgency_keyword` | Urgency words: "acil", "son fiyat", "fırsat" |
  | New Feature | `has_flaw_mention` | Flaw words: "leke", "yırtık", "bozuk", "hafif kusur" (hoca önerisi) |
  | Limitation | `listing_hour`, `day_of_week` | ⚠️ Dolap ilan tarihi göstermiyor — scrape_at kullanılamaz |
  | Planned | `is_negotiable` | ⚠️ Parser'da yok — gelecek iteration'da eklenecek |
- [x] **Cell 20 (Code) — Feature Engineering Code:**
  - Brand tier mapping (configs/features.yaml'dan)
  - Condition ordinal encoding
  - Derived features oluşturma
  - Encoding + scaling pipeline

### Step 8 — Investigation: Data Quality Bugs Found 🔍 (~2-3 dk sunum — EN ÖNEMLİ BÖLÜM) ✅
> ⭐ Sunum yönergesine göre "en değerli kısım" — gerçek sorun bul, kanıtla, çöz.

- [x] **Cell 21 (Markdown) — Investigation Header:**
  - "During our data collection and EDA, we discovered several data quality issues."
  - "We show the raw evidence, explain the root cause, and demonstrate the fix."
- [x] **Bug 1 — Brand/Size Field Contamination** ⭐ (gerçek veride keşfedildi)
  - Evidence: 365/411 (%89) brand alanı " - size" içeriyor → notebook Cell 32-33
  - Fix: `brand_clean` + `size_extracted` split → Before/After bar chart
- [x] **Bug 2 — Condition Label Inconsistency**
  - Evidence: "Yeni ve Etiketli" vs "Yeni & Etiketli" → 4→3 unique değer
  - Fix: Normalization (`clean_features.py`)
- [x] **Bug 3 — Category Field Empty**
  - Evidence: 411/411 `category=None` → `category_scraped` kullanıldı
- [x] **Bug 4 — Description = Page Title** ⭐ (gerçek veride keşfedildi)
  - Evidence: 311/411 (%76) `description_text == title` → notebook Cell 32
  - Fix: `desc_is_placeholder` flag eklendi
- [x] **Bug 5 — is_sold Always False**
  - Evidence: Tüm 411 ilan `is_sold=False` → proxy_sold oluşturuldu
- [x] **Bug 6 — Missing Color Values**
  - Evidence: 0/411 renk bilgisi yok → "Unknown" imputation planlandı
- [x] **Bug 7 — Keyword Features Low Coverage**
  - Evidence: `has_flaw_mention=2`, `desc_has_urgency=0` (placeholder desc nedeniyle)
  - Fix: Acknowledged as limitation, parser fix planned
- [x] **Her bug için Cell (Code):** Cell 32 (Bug Evidence tablosu) + Cell 33 (Brand Before/After)

### Step 9 — Presentation Polish & Rehearsal

- [x] **Show/Hide Code mekanizması:**
  - HTML/JS toggle button ile implemente edildi (nbextension yerine)
  - Tüm code cell'leri varsayılan olarak gizle
  - Sunum sırasında "Show Code" butonu ile isteğe bağlı göster
- [x] **Takım üyesi görev dağılımı (3 kişi × 10 dk):**
  | Üye | Bölüm | Cell'ler | Süre |
  |-----|-------|----------|------|
  | **Furkan** | S1 Problem + S2 Data Collection + Target Dist. | Cell 1-6 | ~3 dk |
  | **Utku** | S3.1 Schema + S3.2 Stats + S3.3 Distributions | Cell 7-20 | ~3.5 dk |
  | **Halil** | S3.4 Correlations + Hypotheses + S4 Feature Eng. + Investigation + Conclusion | Cell 21-34 | ~3.5 dk |
- [x] **Tüm slide'lar İngilizce** — Türkçe terim varsa parantez içinde
- [ ] **10 dakika prova** — zamanlama kontrolü
- [ ] **Yedek slide'lar:** Sorulabilecek sorular için ekstra grafikler hazırla
- [x] Final notebook commit: `feat: EDA presentation notebook`
- [ ] Prova rehberi → `docs/PRESENTATION_GUIDE.md`

---

## ⏳ M2 — TEMPORAL LABELING SYSTEM

> **⚠️ PROJENİN ALTIN NOKTASI**
> Ground truth doğal olarak Dolap'tan elde ediliyor — ama bu 7 günlük
> bekleme süresini disiplinli yönetmeyi gerektiriyor.

### Phase 6 — 7-Day Labeling Mechanism ✅
> commit hedefi: `feat: temporal labeling mechanism`

- [x] `src/labeling/status_checker.py` — ilan durum kontrol sınıfı
  - URL'yi ziyaret et
  - HTTP 404/410 → `removed`
  - "Satıldı" badge → `sold_within_7_days = 1`
  - Hâlâ aktif → `sold_within_7_days = 0`
  - Sayfa parse hatası → `error` (ayrı kaydet)
- [x] `src/labeling/labeler.py` — batch labeling orchestrator
  - Bir cohort'taki tüm ilanları sırayla kontrol et
  - Anti-ban kurallarına uy (Phase 4'ten miras)
- [x] Label output: `data/labels/cohort_{YYYYMMDD}.jsonl`
  - Her satır: `{listing_id, url, status, sold_within_7_days, checked_at}`
- [x] `src/pipelines/label.py` implementasyonu (skeleton → gerçek)
  - `--auto` flag: 7+ gün geçmiş cohort'ları otomatik tespit
  - `--force` flag: mevcut label'ları yeniden yaz
  - `--no-headless` flag: debug modunda görünür browser
- [x] Edge case'ler:
  - İlan silindi ama satılmadı → `removed` status (sold_within_7_days = None)
  - İlan hâlâ aktif ama 404 → retry logic (3 deneme)
  - Ban tespit → batch abort + partial results saved
- [x] Labeling süreci logu: summary.yaml ile (sold/active/removed/error sayıları)
- [x] `clean_features.py` güncellendi: `--merge-labels` flag ile gerçek label desteği

### Phase 7 — First Cohort Lifecycle 🟡
> commit hedefi: `feat: first cohort labeled`

- [x] ~~**Gün 1 (10 Mart):** cohort_20260310 scrape başlatıldı~~ → başarısız (26 ilan, browser crash)
- [x] **Parser İyileştirme (11 Mart):** `parsers.py` kapsamlı güncelleme
  - ✅ Breadcrumb JSON-LD → category, subcategory doğru çekilir (önceki: hep None)
  - ✅ Brand `<h1>` split → "Koton" (önceki: "Koton - M / 38 Beden")
  - ✅ Size `<h1>` split → "M / 38 Beden" (önceki: hep yanlış)
  - ✅ Description `<p>` tag → temiz metin (önceki: seller username dahildi)
  - ✅ Comment `<span class="comment-count">` → güvenilir (platform limiti: hep 0)
  - ✅ Photo count dsmcdn dedup → doğru sayım
  - ✅ Color title+slug arama → bilinen renk sözlüğü
  - ✅ Seller `profile-block` öncelikli → doğru seller, listing_count
  - ✅ Price `price-detail` div → güvenilir fiyat
  - ✅ Condition `<span class="subtitle">` → doğru durum etiketi
- [x] **Seed seller genişletme:** 8 kategori × 4-6 seller (önceki: 2-6)
  - Yeni seller'lar: ihtiyacblog(208), emirsahanbekar(211), beyazzayy, meltemkaya888
- [x] **Gün 1 (11 Mart):** cohort_20260311 scrape ✅ — **2151 listing**, 8 kategori × 5 sayfa
  - Süre: 14029s (~3.9 saat), 548 duplikat atlandı
  - Kategori dağılımı: kazak(416), elbise(380), tshirt(298), mont(296), gomlek(270), pantolon(208), etek(195), sweatshirt(88)
  - **Veri Kalitesi Raporu:**
    - %100 doluluk: listing_id, url, brand, title, price, condition, like_count, comment_count, photo_count, seller_username, category, subcategory
    - description_text: %100 (önceki cohort'ta %24'tü — parser fix çalıştı ✅)
    - color: %92.4, size: %85.5, seller_listing_count: %97.2
    - Top markalar: Diğer(742), Zara(119), Koton(109), LC Waikiki(100), Bershka(84)
    - Fiyat: 30-91111 TL, medyan 249 TL, ortalama 727 TL
    - Beğeni: 0-125, ortalama 6.9 | Fotoğraf: 1-8, ortalama 4.7
    - Durum: Az Kullanılmış(1306), Yeni(446), Yeni ve Etiketli(399)
    - has_discount: %0 (Dolap indirimli fiyat gösterimi nadir)
    - is_sold: %0 (beklenen — taze scrape, labeling 7 gün sonra)
  - Crash-safe pipeline: her ilan anında diske yazılır
  - Güncellenmiş parser ile temiz feature'lar
- [ ] **Gün 2-7 (12-17 Mart):** Bekleme (7 gün labeling süresi)
- [ ] **Gün 8 (18 Mart):** cohort_20260311 re-check → labeling
  - `python -m src.pipelines.label --cohort-id 20260311 --no-headless`
- [ ] **Ayrıca:** cohort_20250712 (8 Mart) → **15 Mart'ta label'lanabilir**
  - `python -m src.pipelines.label --cohort-id 20250712 --no-headless`
- [ ] Label dağılımı analizi: sold vs not_sold oranı
- [ ] Veri kalitesi raporu: eksik alanlar, parse hataları
- [ ] Hedef: minimum 2 cohort labeled, 2000+ etiketli ilan

---

## 🧹 M3 — DATA PROCESSING & FEATURE ENGINEERING

### Phase 8 — Data Cleaning Pipeline ✅
> commit hedefi: `feat: data cleaning pipeline`

- [x] `src/preprocessing/cleaner.py` — DataCleaner sınıfı (~270 satır)
  - Schema normalisation (tüm beklenen sütunların varlığını garanti)
  - Duplicate detection & removal (aynı `listing_id`, keep first)
  - Brand/size split (eski parser: "Zara - S / 36" → clean brand + size)
  - Condition normalisation + ordinal encoding (4→3 unique)
  - Category repair (None → category_scraped)
  - Description placeholder detection
  - Missing value imputation (color/size→"Bilinmiyor", counts→0)
  - Outlier flagging (is_price_outlier, is_like_outlier — P99)
  - Dtype enforcement (str/float/int/bool/datetime)
- [x] `src/dataset/merger.py` — DatasetMerger sınıfı (~270 satır)
  - discover_cohorts() — raw_snapshots dizinini tara
  - load_raw() / load_labels() — JSONL yükle
  - merge_cohort() — tek cohort: raw + labels merge → parquet
  - merge_all() — tüm cohortları birleştir + cross-cohort dedup
  - FutureWarning-free concat (all-NA sütun pre-fill)
- [x] `src/pipelines/build_dataset.py` — End-to-end pipeline (iskelet → TAM)
  - `--all` / `--cohort-ids` / `--skip-merge` flags
  - Merge → Clean → Save (parquet + CSV)
  - Detaylı summary log
- [x] Pipeline test: 2 cohort (20250712 + 20260311) → 2221 satır, 37 sütun, 0 uyarı
  - Cross-cohort dedup: 341 duplicate atlandı
  - 67 size recovered from legacy brand field
  - 56 placeholder description tespit edildi
  - 23 price outlier + 23 like outlier flaglendi
  - Output: `data/interim/cleaned_all.parquet` (285KB)

### Phase 9 — Feature Engineering
> commit hedefi: `feat: feature engineering pipeline`
> 🔴 **ÖNCELİK:** Target Variable Definition → Feature Definition sırası **KESINLIKLE ÖNEMLİ**

**Kickoff Update (19 Mart 2026):**
- [x] `src/features/engineer.py` v1 eklendi (CLI + FeatureEngineer sınıfı)
- [x] `data/processed/engineered_features.parquet` üretildi (8167 satır, 35 kolon)
- [x] `data/processed/features_metadata.json` üretildi
- [x] Target QC flagleri eklendi: `label_window_hours`, `invalid_early_label`, `invalid_late_label`, `exclude_from_training`
- [x] RC1-4 tamamlanmadan model training'e geçme (bloklayıcı aktif)

---

#### ⚠️ **PHASE 9.0 — TARGET VARIABLE DEFINITION (İlk Yapılacak)**

**🎯 Target Variable Specification:**
```
target = sold_within_7_days (Binary: 0=Not Sold, 1=Sold within 7 days)

Definition: A listing is labeled as "sold" if:
  1. Listed at scraped_at = T (scrape tarihinde aktif)
  2. Re-checked at labeled_at = T+7 days (7 gün sonra, ±1 gün tolerance)
  3. At T+7: is_sold == True OR status == "sold" (Dolap API/site kontrol)
  
Sources for sold_within_7_days:
  ✅ merged_data.csv'de zaten var: sold_within_7_days kolon
  ✅ Veri kaynakları:
     - is_sold (True/False) → Dolap listing endpoint'inden
     - status (active/sold/deleted/expired) → Dolap site HTML'sinden
     - labeled_at (datetime) → Re-check timestamp
     - scraped_at (datetime) → Original scrape timestamp
```

**🚨 Data Quality Checks (MUTLAKA YAPILMALI):**

1. **Temporal Window Validation:**
   - [x] `labeled_at - scraped_at` dağılımını kontrol et
   - [x] Ideal: ~7 days (604,800 sn)
   - [x] Tolerance: 6-8 days (müsaade edilen sapma)
  - [x] Anomali:
     - [x] `labeled_at < scraped_at` → Data entry error (EXCLUDE)
     - [x] `labeled_at - scraped_at > 15 days` → Çok geç re-check (accuracy düşüyor, flag)
     - [x] `labeled_at - scraped_at < 3 days` → Çok erken re-check (EXCLUDE)

2. **Label Distribution Check:**
  - [x] Count: kaç % sold, kaç % not_sold
   - [ ] Expected: ~20-30% sold (optimal tahmin), ~70-80% not sold
  - [x] **If highly imbalanced:** `class_weight='balanced'` modellerde kullan
  - [x] **If < 10% sold:** Undersampling warning — çok az positive example

3. **Deleted/Expired Listings:**
   - [ ] `status == 'deleted'` → sold_within_7_days ne olmalı?
     - [ ] Option A: Exclude from dataset (yapı eksik)
     - [ ] Option B: Treat as "not sold" (platform politikası)
   - [ ] `status == 'expired'` → same decision
   - [ ] Current handling: ✅ Belirt todo'ya

4. **Cohort Consistency:**
   - [ ] Tüm cohortlarda labeled_at var mı?
   - [ ] cohort_20250712 vs cohort_20260311 → hangileri T+7 kontrolüne hazır?
   - [ ] Yeni cohortlar (henüz T+7'ye ulaşmamış) → exclude from training

5. **Missing sold_within_7_days:**
  - [x] Kaç satır NULL/NaN sold_within_7_days değerine sahip?
  - [x] sebep nedir? → Exclude

**✅ Feature Engineering Starts AFTER Target is Verified**

---

#### 🎯 **TRAINING READINESS REPORT (24 Mart 2026)**

**Current State:** `data/interim/merged_data.csv` (single source CSV)

```
📊 DATASET OVERVIEW:
  Total rows: 6059
  Cohort count in file: 2 (20250712, 20260311)

🎯 TARGET COVERAGE:
  Labeled rows (sold_within_7_days non-null): 1678
  Unlabeled rows: 4381

🎯 TARGET DISTRIBUTION (only labeled subset):
  True  (Sold):   66 (3.93%)
  False (Active): 1612 (96.07%)

⏱️ LABEL WINDOW QC:
  valid_window_count: 18
  early_window_count: 0
  late_window_count: 6016
  early_window_ratio: 0.0

📉 COHORT BREAKDOWN:
  cohort_20250712: 43 row, 18 labeled
  cohort_20260311: 6016 row, 1660 labeled
```

**🚨 INTERPRETATION (güncel):**
- Canonical `merged_data.csv` artık resmi pipeline ile yeniden üretildi.
- RC3 relabeling tamamlandı; `cohort_20260311` resmi label/snapshot akışı üretildi.
- Dataset halen doğrudan training-ready değil: 4381 satır unlabeled, 6016 satır late-window (8+ gün) kontrolü içeriyor.
- Bu nedenle model eğitiminde cohort/time filtreleri ve `unknown/error` yönetimi zorunlu.

**Action Items (Blocking):**
- [x] Target variable definition ✅
- [x] Label timing validation ✅
- [x] Class balance analysis ✅
- [x] Feature engineering can PROCEED (class imbalance is KNOWN and HAS MITIGATION)

---

#### 🚨 **PHASE 9.1 — ROOT CAUSE ACTION PLAN (ÖNCELIK: EN YÜKSEK)**

> Amaç: `sold_within_7_days` etiketini gerçek 7 gün kuralına göre güvenilir hale getirmek.
> Not: Bu bölüm tamamlanmadan EDA sunumunda yeni sonuç paylaşılmayacak.

**Root Cause 1 — 7 gün dolmadan label atılması (kritik veri hatası)**
- [x] `labeled_at - scraped_at` için **hard rule** tanımla:
  - [x] `< 168 saat` olan kayıtları `invalid_early_label=True` olarak flagle
  - [x] Bu kayıtları training set'ten çıkar (`exclude_from_training=True`)
  - [x] 168-192 saat aralığını valid kabul et (7-8 gün tolerance)
- [x] `src/pipelines/label.py` içine guard ekle:
  - [x] Cohort yaşı 7 günden küçükse labeling job'u fail etsin
  - [x] `--force-early-label` olmadan erken labeling'e izin verme
- [ ] QC raporu üret:
  - [x] valid_window_count = 18
  - [x] early_window_count = 0
  - [x] early_window_ratio = 0.0
  - [x] Rapor: `artifacts/metrics/target_variable_report.json`

**Definition of Done (RC1):**
- [x] Dataset'te `<168 saat` label penceresi oranı `%0`
- [ ] Label pipeline logunda erken cohort engellendi bilgisi görünüyor

**Root Cause 2 — Active fallback nedeniyle belirsiz sayfaların active'a kayması**
- [x] `src/labeling/status_checker.py` sınıflandırma mantığını sıkılaştır:
  - [x] Homepage/redirect title tespiti ekle → `status='error'` veya `status='unknown'`
  - [x] Active kararı için en az 2 güçlü kanıt zorunlu olsun:
    - [x] ürün başlığı selector
    - [x] fiyat/sepete ekle bileşeni
    - [x] listing id'nin URL ile uyuşması
  - [x] Tek başına `len(page_source)>5000` kuralı active için yeterli olmasın
- [ ] 100 örnek manuel audit:
  - [ ] sold=50, active=50 rastgele örnek
  - [ ] yanlış sınıflananları `label_audit.csv` ile kaydet

**Definition of Done (RC2):**
- [ ] Homepage title + active eşleşmesi `%0` veya açıkça `unknown`
- [ ] Manual audit doğruluk oranı `>= %95`

**Root Cause 3 — 20260311 label üretiminin resmi pipeline dışı olması**
- [x] Tek kaynak kuralı getir:
  - [x] `data/labels/cohort_*.jsonl` dışındaki label kaynakları geçersiz
  - [x] `merged_data.csv` üretimi sadece `src/dataset/merger.py` + `build_dataset.py` ile yapılacak
- [x] 20260311 için resmi labeling'i yeniden çalıştır:
  - [x] `python -m src.pipelines.label --cohort-id 20260311 --force --no-headless`
  - [x] `data/labels/cohort_20260311.jsonl` dosyasının varlığını doğrula
  - [x] `cohort_20260311_summary.yaml` üretimini zorunlu kıl
- [x] SQLite state tutarlılığı:
  - [x] `cohorts` tablosunda 20260311 kaydı `status='labeled'`
  - [x] `label_date`, `labeled_count` alanları dolu

**Definition of Done (RC3):**
- [x] 20260311 label dosyası + summary dosyası + DB state birbirini tutuyor
- [ ] Repro komutu ile aynı sonuç tekrar üretilebiliyor

**Root Cause 4 — Seller dağılım dengesizliği ve düşük satış oranı**
- [ ] Seller concentration analizi üret:
  - [ ] top10 seller payı
  - [ ] top20 seller payı
  - [ ] seller başına sold rate dağılımı
- [ ] Modelleme hazırlığı için mitigasyon:
  - [ ] Group-aware split (seller leakage azaltımı)
  - [ ] Seller-frequency feature (log_count)
  - [ ] Aşırı dominant seller'lar için cap/weight stratejisi
- [ ] Raporla:
  - [ ] “Marketplace behavior vs labeling artifact” ayrımı
  - [ ] category bazında doğal düşük satış olasılığı

**Definition of Done (RC4):**
- [ ] Seller concentration metriği rapora işlendi
- [ ] Train/val split seller leakage kontrolünden geçti

---

#### ✅ **EDA PRESENTATION GATE (Veri Doğrulama Sonrası)**

> EDA sunumuna geçiş şartı: önce label güvenilirliği doğrulanacak.

**Gate-0: Data Readiness (zorunlu)**
- [ ] Tüm kullanılan cohort'larda `label_window_hours >= 168`
- [ ] `unknown/error` etiket oranı raporlandı
- [ ] Label kaynağı resmi pipeline çıktısı
- [ ] Final analiz dataseti yeniden üretildi (`build_dataset.py`)

**Gate-1: EDA Presentation Update Plan**
- [ ] Notebook target dağılımını yeni verified dataset ile güncelle
- [ ] "Labeling reliability" slide'ı ekle:
  - [ ] erken label hatası bulgusu
  - [ ] active fallback düzeltmesi
  - [ ] pipeline standardizasyonu
- [ ] Eski (6.4 gün) metrikleri arşivle, sunumdan kaldır
- [ ] Yeni confusion-risk notu ekle: removed/unknown handling

**Gate-2: Sunum Akışı (revize)**
- [ ] Bölüm 1: Problem + 7-day ground truth tanımı
- [ ] Bölüm 2: Data collection + label QA süreci
- [ ] Bölüm 3: EDA (yalnızca verified labels)
- [ ] Bölüm 4: Feature engineering kararları
- [ ] Bölüm 5: Limitations + next iteration

**Definition of Done (EDA Gate):**
- [ ] Notebook'taki tüm target grafikleri verified label dataset'ten üretilmiş
- [ ] Sunumda "proxy/erken label" kalıntısı yok
- [ ] Takım prova notlarında veri doğrulama adımı anlatılıyor

---

#### 📋 **NEXT STEPS: Feature Engineering Checklist**

**Before touching src/features/engineer.py, ensure:**

1. **Data Validation:**
   - [ ] Run `scripts/analyze_target_variable.py` on latest merged_data.csv
   - [ ] Verify: No NULL/NaN in `sold_within_7_days`
  - [x] Verify: All label windows within 6-8 days
  - [x] Verify: No negative windows or anomalies

2. **Feature List Documentation:**
   - [ ] Update `configs/features.yaml` with all features to engineer
   - [ ] Include: data type, encoding method, reason for inclusion, expected range
   - [ ] Include: handling rules for missing values
   - [ ] Include: categorical cardinality for categories/colors/sizes

3. **Feature Engineering Implementation:**
   - Implement in order of importance:
     - [x] **Core:** price, photo_count, description_length, condition_ordinal
     - [x] **Temporal:** listing_hour, is_weekend_listing, days_since_scrape
     - [ ] **Categorical:** category_target_encoded, color, size
     - [x] **Seller:** seller_rating_count
     - [x] **Text:** desc_has_urgency_keyword, has_flaw_mention
     - [x] **Derived:** price_to_category_median, price_to_brand_median, brand_tier
   - Note: Do NOT create features without domain knowledge

4. **Feature Validation:**
   - [ ] Test each feature on a sample of 100 rows manually
   - [ ] Check for data leakage (e.g., time-future features)
   - [ ] Ensure no inf/NaN in continuous features
   - [ ] Verify categorical cardinality is reasonable (< 100 for most)

5. **Output & Testing:**
  - [x] Save engineered features → `data/processed/engineered_features.parquet`
  - [x] Create feature metadata JSON (name, type, encoding, missing_handling)
   - [ ] Run basic sanity checks → `scripts/validate_features.py` (create this)
   - [ ] Merge features with target → final dataset for modeling

---

- [x] `src/features/engineer.py` — Feature Engineering Pipeline Class
  - [x] Input: `data/interim/merged_data.csv` (raw data + labels + merged cohorts)
  - [x] Output: `data/processed/engineered_features.parquet` (numerical features)
  - [ ] Methods:
    ```python
    class FeatureEngineer:
      def engineer_price_features() → ["price", "price_to_category_median", "price_log", "has_discount"]
      def engineer_listing_features() → ["photo_count", "desc_length", "desc_word_count", "comment_count", "like_count"]
      def engineer_temporal_features() → ["listing_hour", "listing_dow", "is_weekend", "days_since_scrape"]
      def engineer_categorical_features() → ["category_encoded", "condition_ordinal", "color_encoded", "size_encoded"]
      def engineer_seller_features() → ["seller_rating_count"]
      def engineer_text_features() → ["desc_has_urgency", "desc_has_flaw", "desc_placeholder"]
      def engineer_derived_features() → ["price_to_brand_median", "brand_tier", "category_price_percentile"]
    ```

- [ ] **Feature Details (with implementations):**

  **🟦 Continuous Features:**
  
  1. **price** (Raw Pricing)
     - Source: `price` column
     - Handling: Outlier check (< 10 TL or > 50000 TL → flag), log-transform for skewness
     - Type: Float
     - Expected range: 10-50000 TL
     - ML note: Likely strong predictor, but check for too-cheap/too-expensive anomalies
  
  2. **price_to_category_median** (Category-normalized price)
     - Formula: price / category_median_price
     - Interpretation: Below median (<1.0) vs above median (>1.0)
     - Hypothesis: Cheap listings sell faster → lower ratio → higher sale probability
     - Type: Float
     - Expected range: 0.2-5.0
     - Handling: Clamp at [0.1, 10.0] to avoid extreme ratios
  
  3. **photo_count** (Visual Marketing Signal)
     - Source: `photo_count` column
     - Interpretation: More photos → more serious seller / better product visibility
     - Hypothesis: 3+ photos vs 1-2 photos → higher sale probability
     - Type: Integer
     - Expected range: 1-30
     - Note: May have max cap on Dolap platform
  
  4. **description_length** (Text Effort Signal)
     - Source: `description_text` → character count
     - Interpretation: Longer descriptions → more effort → more trustworthy
     - Hypothesis: Description length > median → higher sale probability
     - Type: Integer
     - Expected range: 0-5000 characters
     - Handling: Cap at 5000 (extremely long descriptions are rare/anomalies)
  
  5. **description_word_count** (Vocabulary Signal)
     - Source: `description_text` → word count
     - Interpretation: More words → more detailed / better English proficiency
     - Type: Integer
     - Expected range: 0-500 words
  
  6. **like_count** (Engagement Signal - USE WITH CAUTION)
     - Source: `like_count` column
     - ⚠️ Data Leakage Risk: If likes increase AFTER initial listing, this is a time-series feature
     - Decision: Do NOT use likes as feature (leakage) OR use only initial likes at scrape time
     - If using: Ensure only using `like_count @ scraped_at`, not any later counts
  
  7. **comment_count** (Social Proof Signal)
     - Source: `comment_count` column
     - ⚠️ Same leakage risk as like_count
     - Decision: Do NOT use comments as feature (leakage risk)
  
  8. **seller_rating_count** (Seller Experience Signal)
     - Source: `seller_rating_count` column
     - Interpretation: More ratings → more experienced seller → more trustworthy
     - Hypothesis: Higher rating count → higher sale probability
     - Type: Float
     - Expected range: 0-10000
     - Handling: Log-transform for skewness (ratings follow power-law)
  
  9. **price_log** (Non-linear price)
     - Formula: log1p(price)
     - Reason: Prices are right-skewed; log captures diminishing utility of extra TL
     - Type: Float
     - Expected range: 2.3-10.8 (log(10) to log(50000))
  
  10. **brand_tier** (Brand Prestige Proxy)
      - Source: `brand` → median price per brand → quantile → tier
      - Tiers: 0-5 (0=unknown, 1=budget, 5=luxury)
      - Hypothesis: Luxury brands may have different sale dynamics (e.g., more negotiable)
      - Type: Integer
      - Expected cardinality: 6 categories
      - Handling: Unknown brands → tier 0 or median tier (config decision)

  **🟪 Categorical Features:**
  
  11. **category** (Product Category)
      - Source: `category` column
      - Encoding: Target Encoding (mean `sold_within_7_days` per category)
      - Type: Float (after target encoding)
      - Expected cardinality: 10-15 categories
      - Hypothesis: Some categories have more active buyers (e.g., shoes vs accessories)
  
  12. **condition** (Product Condition)
      - Source: `condition` column
      - Ordinal Mapping:
        ```
        "Yeni & Etiketli" → 3 (New with tag)
        "Yeni" → 2 (New)
        "Az Kullanılmış" → 1 (Lightly used)
        "Kullanılmış" → 0 (Used)
        ```
      - Hypothesis: Newer items sell faster
      - Type: Integer (ordinal)
      - Expected range: 0-3
  
  13. **color** (Product Color)
      - Source: `color` column
      - Cardinality: 20-50+ colors
      - Encoding: Target Encoding (mean `sold_within_7_days` per color) OR frequency-based grouping
      - Hypothesis: Some colors more popular (e.g., black, white, blue)
      - Handling: Colors with < 10 examples → "Other" category
  
  14. **size** (Product Size)
      - Source: `size` column
      - Cardinality: 30-100+ sizes (many combos like "S / 36", "M / 38")
      - Encoding: Target Encoding OR ordinal (if convertible to numeric)
      - Hypothesis: Popular sizes (M, L) sell faster than extreme sizes
      - Handling: Sizes with < 5 examples → "Other" category
  
  15. **has_discount** (Pricing Strategy)
      - Source: `has_discount` column (True if original_price present and > price)
      - Interpretation: Discount signals urgency/clearance
      - Hypothesis: Discounted items sell faster (more attractive)
      - Type: Boolean → {0, 1}
  
  16. **shipping_buyer_pays** (Shipping Cost Signal)
      - Source: `shipping_buyer_pays` column
      - Interpretation: If buyer pays → higher total cost for buyer → maybe lower sale prob? (untested)
      - Type: Boolean → {0, 1}
      - Note: May need interaction with price

  **🟧 Temporal Features:**
  
  17. **listing_hour** (Time of Day Listed)
      - Source: `scraped_at` → extract hour (0-23 in UTC or local timezone)
      - Hypothesis: Listings posted during work hours (9-17) may get more visibility
      - Type: Integer 0-23
      - Encoding: Could create is_peak_hours boolean (9-17) instead of raw hour
  
  18. **listing_dow** (Day of Week Listed)
      - Source: `scraped_at` → extract day of week (0-6 or 0=Monday)
      - Hypothesis: Weekday vs weekend listings have different dynamics
      - Type: Integer 0-6
      - Encoding: Boolean `is_weekend` (Friday-Sunday) OR cyclic encoding (sin/cos)
  
  19. **is_weekend_listing** (Weekend Indicator)
      - Formula: listing_dow in [4, 5, 6] (Friday, Saturday, Sunday)
      - Type: Boolean → {0, 1}

  **🟩 Text-derived Features:**
  
  20. **desc_has_urgency_keyword** (Urgency Signal)
      - Keywords: "acil", "son", "indirim", "fırsat", "pazarlık", "satılmalı"
      - Type: Boolean → {0, 1}
      - Hypothesis: Urgent language → seller motivated to sell → faster
  
  21. **desc_has_flaw_mention** (Flaw Honesty Signal)
      - Keywords: "leke", "yırtık", "bozuk", "kusur", "hafif", "çizik"
      - Type: Boolean → {0, 1}
      - Hypothesis: Honest disclosure of flaws → more trustworthy → faster sale
  
  22. **desc_is_placeholder** (Effort Signal)
      - Check: description_text == title (likely auto-generated)
      - Type: Boolean → {0, 1}
      - Hypothesis: Placeholder descriptions → less effort → slower sale

- [ ] **Feature Validation & Storage:**
  - [ ] Create `configs/features.yaml` with all feature definitions (metadata)
  - [ ] Store engineering code in `src/features/` modules (not monolithic class)
  - [ ] Generate feature importance baseline (on first few models)
  - [ ] Save final feature matrix: `data/processed/engineered_features.parquet`
  - [ ] Create features metadata JSON: name, dtype, encoding, missing_handling, range, importance_score

- [ ] **Potential Data Leakage Checks:**
  - ⚠️ **like_count / comment_count:** Only use @ scrape time, NOT later counts
  - ⚠️ **seller_rating_count:** May be post-purchase ratings (if used, must be @ scrape time)
  - ⚠️ **listing_date derived from other columns:** Ensure not using time-future information

### Phase 10 — Exploratory Data Analysis (EDA) ➡️ **EDA Presentation'a merge edildi**
> ℹ️ Bu phase artık ayrı yapılmayacak. Tüm EDA içeriği yukarıdaki
> "🎤 EDA PRESENTATION" bölümündeki Step 1-8 içinde yer alıyor.
> Notebook: `notebooks/01_eda_presentation.ipynb`

- [ ] ~~`notebooks/01_eda.ipynb`~~ → `notebooks/01_eda_presentation.ipynb` (sunum formatında)
- [ ] Temel istatistikler → Step 4
- [ ] Target dağılımı → Step 2
- [ ] Fiyat dağılımı → Step 5
- [ ] Marka tier dağılımı → Step 5
- [ ] Durum etiketi dağılımı → Step 5
- [ ] Fotoğraf sayısı vs satış oranı → Step 6
- [ ] Korelasyon matrisi → Step 6
- [ ] Kategori bazlı satış oranları → Step 6
- [ ] Sınıf dengesizliği analizi → Step 2 + Step 7

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
| 🌐 M1 — Data Collection | ✅ Tamamlandı | Phase 2, 3, 4, 5 |
| 🎙️ **EDA Presentation** | 🟡 **PROVA KALDI** | Step 0-8 ✅, Step 9 prova |
| ⏳ M2 — Temporal Labeling | 🟡 **Phase 6 ✅, Phase 7 scrape ✅ → labeling bekliyor** | Phase 6 ✅, Phase 7 🟡 |
| 🧹 M3 — Data Processing | 🟡 **Phase 8 ✅, Phase 9 kickoff ✅, Phase 9.1 devam ediyor** | Phase 8 ✅, Phase 9 🟡 |
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
| 8 | `42ef94f` | `feat: basic scraper prototype` | develop |
| 9 | `b154319` | `feat(M1): complete cohort scraping pipeline with pilot data collection` | develop |
| 10 | `3141cdb` | `feat(EDA): initial EDA presentation notebook` | develop |
| 11 | `fdea696` | `chore: whitelist pilot data files for team sharing` | develop |
| 12 | `e750147` | `feat(EDA): presentation guidelines compliance` | develop |
| 13 | `14f32b4` | `feat(EDA): presentation guide + team scripts` | develop |
| 14 | `0f26358` | `feat: M2 temporal labeling system + crash-safe scrape pipeline` | develop |
| 15 | `681574c` | `feat: comprehensive parser improvements + seed seller expansion` | develop |
| 16 | `c0429c4` | `feat(phase9): kickoff feature engineering pipeline and todo updates` | develop |
| 17 | `50d2b92` | `docs(todo): sync phase 9.1 status and roadmap metadata` | develop |
| 18 | `0d22d9c` | `feat(labeling): add early-label guard and strict active classification` | develop |

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

### ✅ Scraping Modülü (Phase 2-3-4-5)
```
src/scraping/
├── __init__.py         ← Public API re-exports (DolapScraper, parsers, RateLimiter, BanDetector, SessionManager, SnapshotWriter, CohortStateTracker)
├── parsers.py          ← 17 HTML parse fonksiyonu (~400 satır)
├── scraper.py          ← Selenium-based DolapScraper sınıfı (~857 satır, profile-based crawling, JS DOM extraction)
├── rate_limiter.py     ← RateLimiter, BanDetector, SessionManager, build_proxy_options (~320 satır)
└── storage.py          ← SnapshotWriter (append-only JSONL, dedup, meta.yaml) + CohortStateTracker (SQLite lifecycle) (~460 satır)
```

### ⏳ İskelet (Skeleton) — İmplementasyon Bekliyor
```
src/pipelines/
├── train.py            ← ✅ TAM İMPLEMENTASYON (experiment lifecycle)
├── scrape.py           ← ✅ TAM İMPLEMENTASYON (crash-safe, per-listing write)
├── label.py            ← ✅ TAM İMPLEMENTASYON (Phase 6 — --auto, --force, --no-headless)
├── build_dataset.py    ← ✅ TAM İMPLEMENTASYON (merge + clean + save)
└── evaluate.py         ← ⏳ İskelet (Phase 15-17'de implement edilecek)

src/labeling/
├── __init__.py         ← ✅ StatusChecker, CohortLabeler exports
├── status_checker.py   ← ✅ TAM İMPLEMENTASYON (~310 satır, Selenium-based)
└── labeler.py          ← ✅ TAM İMPLEMENTASYON (~240 satır, batch orchestrator)
src/preprocessing/      ← ✅ clean_features.py (EDA) + cleaner.py (DataCleaner)
src/features/           ← 🟡 engineer.py eklendi (Phase 9 kickoff tamamlandı)
src/dataset/            ← ✅ merger.py (DatasetMerger)
src/models/             ← ⏳ Boş (Phase 11-14)
src/evaluation/         ← ⏳ Boş (Phase 15-17)
```

---

## ⚡ Sonraki Adım

> **🟡 M3 Phase 9.1 — Root Cause Fix + Resmi Relabeling**
>
> ✅ cohort_20260311 scrape tamamlandı: **2151 listing**, 8 kategori, ~3.9 saat
> ✅ M3 Phase 8 tamamlandı: cleaner.py + merger.py + build_dataset.py
> ✅ Cleaned dataset: 2221 satır, 37 sütun (cleaned_all.parquet)
> ✅ Phase 9 kickoff tamamlandı: `src/features/engineer.py` + engineered output üretildi
>
> **Zaman çizelgesi:**
> - 11 Mart: ✅ Scrape + ✅ Cleaning pipeline
> - 19 Mart: ✅ Phase 9 kickoff (engineer.py + metadata + todo sync)
> - 19 Mart: ✅ RC1 (7-day guard + early-label exclude)
> - 19 Mart: ✅ RC2 (strict active classification + unknown fallback)
> - 20 Mart+: RC3 (resmi relabeling + dataset rebuild)
>
> **Şu an yapılacak (M3 Phase 9.1):**
> 1. ✅ `src/pipelines/label.py` içine 7-gün guard + `--force-early-label` kontrolü eklendi
> 2. ✅ `src/labeling/status_checker.py` active fallback mantığı sıkılaştırıldı
> 3. Resmi relabeling (`cohort_20260311`) + `build_dataset.py` ile `merged_data.csv` yeniden üret
>
> **RC3 Execution Checklist (aktif):**
> - [ ] `python -m src.pipelines.label --cohort-id 20260311 --force --no-headless`
> - [x] `data/labels/cohort_20260311.jsonl` dosyasını doğrula
> - [ ] `data/labels/cohort_20260311_summary.yaml` dosyasını doğrula
> - [x] `python -m src.pipelines.build_dataset --all`
> - [x] `data/interim/merged_data.csv` target dağılımını yeniden raporla
> - [ ] Phase 9.1 RC3 checkbox'larını update et
>
> ✅ M0 Foundation + M1 Data Collection + M3 Phase 8 tamamlandı.
> 📊 Geçici FE çıktısı: `data/processed/engineered_features.parquet` (eski sürüm, canonical veri güncellendiği için yeniden üretilecek)
