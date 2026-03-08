# 📋 Dolap Sale Prediction — Master TODO

> **Son güncelleme:** 2026-03-08 (EDA notebook tamamlandı)
> **Branch:** `develop` | **Son commit:** `e750147`
> **Durum:** M1 ✅ | EDA Notebook ✅ | 🎤 **Prova + görev dağılımı kaldı**
> **Öncelik:** Step 9 — Presentation Polish & Rehearsal (10 dk prova, takım üyesi dağılımı)

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
│  ⏳ M2 — TEMPORAL LABELING SYSTEM                           [░░░░░░░░] ⏳│
│  ├── Phase 6   — 7-Day Labeling Mechanism                               │
│  └── Phase 7   — First Cohort: Collect → Wait 7d → Re-check            │
│                                                                         │
│  🧹 M3 — DATA PROCESSING & FEATURE ENGINEERING              [░░░░░░░░] ⏳│
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
- [ ] **Takım üyesi görev dağılımı:**
  | Üye | Bölüm | Süre |
  |-----|-------|------|
  | Üye 1 | Section 1 (Problem) + Section 2 (Data Collection) | ~3 dk |
  | Üye 2 | Section 3.1-3.2 (Schema + Statistics) | ~2 dk |
  | Üye 3 | Section 3.3-3.4 (Distributions + Relationships) | ~2.5 dk |
  | Üye 4 | Section 4 (Feature Eng.) + Investigation (Bugs) | ~2.5 dk |
- [x] **Tüm slide'lar İngilizce** — Türkçe terim varsa parantez içinde
- [ ] **10 dakika prova** — zamanlama kontrolü
- [ ] **Yedek slide'lar:** Sorulabilecek sorular için ekstra grafikler hazırla
  - Model seçim gerekçesi (LR / RF / XGBoost)
  - 7-gün labeling mekanizması detay diyagramı
  - Cloudflare bypass teknik detayları
- [x] Final notebook commit: `feat: EDA presentation notebook`

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
| 🎤 **EDA Presentation** | 🟡 **AKTİF — PROVA KALDI** | Step 0-8 ✅, Step 9 prova + görev dağılımı |
| ⏳ M2 — Temporal Labeling | ⏳ Bekliyor | — |
| 🧹 M3 — Data Processing | ⏳ Bekliyor (Phase 10 → EDA Pres.) | — |
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
├── scrape.py           ← ✅ TAM İMPLEMENTASYON (Phase 5 — SnapshotWriter + CohortStateTracker entegrasyonlu)
├── label.py            ← ⏳ İskelet (Phase 6'da implement edilecek)
├── build_dataset.py    ← ⏳ İskelet (Phase 8-9'da implement edilecek)
└── evaluate.py         ← ⏳ İskelet (Phase 15-17'de implement edilecek)

src/labeling/           ← ⏳ Boş (Phase 6-7)
src/preprocessing/      ← ✅ clean_features.py (feature temizleme + proxy label)
src/features/           ← ⏳ Boş (Phase 9)
src/dataset/            ← ⏳ Boş (Phase 8)
src/models/             ← ⏳ Boş (Phase 11-14)
src/evaluation/         ← ⏳ Boş (Phase 15-17)
```

---

## ⚡ Sonraki Adım

> **🎤 EDA PRESENTATION — Notebook tamamlandı, prova ve görev dağılımı kaldı**
>
> ✅ Step 0-8 tamamlandı. Notebook 34 cell, tüm hücreler çalıştırıldı (exec 1-20).
>
> 1. **ŞİMDİ:** Takım üyesi görev dağılımı (Step 9)
> 2. **ŞİMDİ:** 10 dakika prova — zamanlama kontrolü
> 3. **SONRA (M2):** Genişletilmiş scrape (5 ek kategori) + temporal labeling (7 gün re-check)
>
> ✅ M0 Foundation + M1 Data Collection tamamlandı.
> 📊 Pilot veri: 411 ilan | 3 kategori | 12 satıcı | proxy_sold %26.5 positive
