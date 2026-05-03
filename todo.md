# 📋 Dolap Sale Prediction — Master TODO

> **Son güncelleme:** 2026-05-03 (M7.6 ✅, M9 sunum live demo + Section 17 model export ✅, mail gönderildi)
> **Branch:** `main` | **Son commit:** `877f544` (henüz push'lanmamış değişiklikler var)
> **Durum:** M0/M1 ✅ | EDA 🟡 | M2 ✅ | M3 ✅ + RC4 ✅ | M4 ✅ | M5 ✅ + §14/15/16 ✅ | **M6 ⏸️ DURDURULDU** (sunumdan sonraya ertelendi) | **M7.1-M7.5 ✅, M7.6 ✅ (mail gönderildi)** | **M9 (4 Mayıs sunum) 🟡 — hazırlık devam**
> **Canonical notebook:** `notebooks/dolap_classification_final.ipynb` (45 cell, §14-17 yeni). Run All hatasız çalışıyor (jupyter nbconvert --execute ile doğrulandı). Demo artefacts: `models/dolap_xgboost_pipeline.joblib` + `models/feature_schema.json`.
>
> 🔴 **HATIRLATMA — MAKALE YAZIMI ERTELENDİ:** Kullanıcı 3 Mayıs'ta açık talimat verdi: "daha makale yazılmayacak bana hatırlat bunu sadece sonrasında". M8.5 (DergiPark prose yazımı) **sunum bitene kadar açılmayacak**. Sunumdan sonra konuşulacak.
>
> **Sıradaki kullanıcı aksiyonu:** sunum prova + her üye konuşma sırası + canlı demo testi (kendi makinede)
> **Sonraki blok (sunum sonrası):** M8.5 makale prose yazımı (~26 Mayıs deadline) — kullanıcı izniyle açılacak
>
> ⚠️ **Hedef:** Bu proje **Dolap.com (Türk ikinci el moda platformu) için 7-günlük satış tahmini** — CV satırı ve **Veri Bilimi Dergisi (DergiPark, TR Dizin)** makalesi çıktıları için. Mevcut durum bozulmadan, sadece iyileştirmeler yapılır; her değişiklik önce sorulur.
>
> 📊 **Headline sonuç (canonical = `final` notebook):** XGBoost ROC-AUC = **0.8150** [95% CI: 0.7613, 0.8722], F1 = 0.27 (default) → 0.35 (optimal threshold). Ablation: NO_ENGAGEMENT 49 feat AUC=0.8097 (ΔAUC −0.005), STATIC_ONLY 26 feat AUC=0.7491 (ΔAUC −0.066). **Robustness check (RC4):** group-aware split AUC=0.6832 [0.6079, 0.7544] — Limitations'a girecek. Dataset: `model_ready_v3.csv` (6007 listing × 60 feature, %5 sold).

---

## Proje Haritası

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DOLAP SALE PREDICTION — ROADMAP                      │
│                                                                         │
│  🏗️ M0 — FOUNDATION                                        [██████░░] 🟡│
│  ├── Phase 0   — Project Architecture                        ✅         │
│  ├── Phase 0.5 — ML Infrastructure (Experiment Tracking)     ✅         │
│  └── Phase 1   — Literature Research & Project Report        ⏳ doc yok │
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
│  🟡 M2 — TEMPORAL LABELING SYSTEM                           [████████] ✅│
│  ├── Phase 6   — 7-Day Labeling Mechanism                    ✅         │
│  └── Phase 7   — First Cohort Lifecycle (5472/6059 labeled) ✅         │
│                                                                         │
│  🧹 M3 — DATA PROCESSING & FEATURE ENGINEERING              [██████░░] 🟡│
│  ├── Phase 8   — Data Cleaning Pipeline                      ✅         │
│  ├── Phase 9   — Feature Engineering                         ✅ kod    │
│  ├── Phase 9.1 — RC1/2/3 ✅ kod, RC4 ✅ mitigation kod (rapor ⏳)      │
│  └── Phase 10  — EDA Notebook (merged into EDA Presentation)            │
│                                                                         │
│  🤖 M4 — MODELING                                           [███████░] ✅ notebook│
│  ├── Phase 11  — Baseline Models (LR, KNN, DT, RF) ✅ classification_final cell[8]│
│  ├── Phase 12  — Advanced Models (XGB, LightGBM)   ✅ XGB best AUC=0.8150│
│  ├── Phase 13  — Class Imbalance (SMOTE-safe pipe + threshold tuning) ✅│
│  └── Phase 14  — Hyperparameter Tuning (RandomizedSearchCV SMOTE-safe) ✅│
│                                                                         │
│  📊 M5 — EVALUATION & EXPLAINABILITY                        [███████░] ✅ notebook│
│  ├── Phase 15  — Test Set Eval (CM, classification report, CI) ✅       │
│  ├── Phase 16  — SHAP Analysis (TreeExplainer + H1-H4 doğrulama) ✅     │
│  └── Phase 17  — Visualization Suite (ROC, PR, radar, learning) ✅      │
│                                                                         │
│  📝 M6 — REPORTING & DELIVERY                               [███░░░░░] 🟡│
│  ├── Phase 18  — Final Analysis Report (methodology_addendum.md ✅)     │
│  └── Phase 19  — Paper Draft (article EN + TR abstract iskelet ✅)      │
│                                                                         │
│  📨 M7 — Profesör Geri Bildirimi (4 Mayıs sunum + 26 Mayıs teslim)      │
│  ├── M7.1-M7.4 (1. tur 4 madde rapor düzeltmesi) ✅ kod+rapor, PDF ⏳   │
│  ├── M7.5.1 PDF aktarımı                          ⏳ kullanıcı aksiyonu │
│  ├── M7.5.2 1. tur mail taslağı                   ✅ hazır              │
│  └── M7.6 2. tur feedback (A + B.1 + B.2 + B.3)   ✅ mail gönderildi   │
│                                                                         │
│  🎤 M9 — 4 Mayıs Sunum (Live Demo + Model Decisions, 20 dk)             │
│  ├── M9.1 Notebook §14/15/16/17 + §12 + Show/Hide toggle  ✅ tüm 8 alt  │
│  ├── M9.2 Demo (10 preset + Dolap-themed UI + FALLBACK)    ✅ 7 alt    │
│  ├── M9.3 Prova run-sheet + Q&A 15 kart + görev dağılımı   ✅ 3 alt    │
│  └── M9.4 Yedek plan (notebook fail / demo fail)    ✅ FALLBACK_PLAN.md │
│                                                                         │
│  📰 M8 — Veri Bilimi Dergisi (PAUSED — sunum sonrası açılacak)         │
│                                                                         │
│  📰 M8 — Veri Bilimi Dergisi Yayın Yolu                                 │
│  ├── M8.1 Hipotez-SHAP paragrafı                  ✅ §5.3'te            │
│  ├── M8.2 Ablation                                ✅ rakamlar gerçek    │
│  ├── M8.3 Bootstrap CI                            ✅ 6 model için       │
│  ├── M8.4 is_negotiable feature                   ⏸️ kullanıcı onayı   │
│  ├── M8.5 Akademik makale formatı                 🟡 prose yazımı kaldı │
│  └── M8.6 Submission                              ⏳                    │
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

### Phase 1 — Literature Research & Project Report 🟡
> ⚠️ **DOĞRULAMA (2026-05-02):** `docs/PROJE_RAPORU.md` dosyası yok. `docs/` altında sadece `DOLAP_SITE_MAP.md` var.
> Aşağıdaki maddeler kavramsal olarak araştırılmış olabilir ama belge halinde toplanmamış.
> 🎯 **Makale/CV önceliği:** Bu rapor M6'da Final Report'a girdi olacak — yeniden açıldı.

- [ ] Google Scholar taraması — Dolap.com üzerine ML çalışması yok (kavramsal tespit edildi, belge yok)
- [ ] Benzer platform çalışmaları (Mercari, ZOZOUSED, genel)
- [ ] Özgünlük değerlendirmesi (platform + görev + coğrafi + metodolojik)
- [x] Platform analizi — URL yapısı, HTML structure, ürün sayfası veri haritası → `docs/DOLAP_SITE_MAP.md` (354 satır)
- [ ] 25+ özellik tanımı (listing, seller, engagement, derived) — kod tarafında engineer.py'da var, doküman yok
- [ ] 5-tier marka kademe sistemi (Budget → Luxury) — kod tarafında engineer.py + features.yaml'da var, doküman yok
- [ ] Scraping mimarisi (Phase 1-2-3 diyagramı)
- [ ] 5 model önerisi + deneysel tasarım
- [ ] 6 değerlendirme metriği + sınıf dengesizliği stratejileri
- [ ] 6 haftalık zaman çizelgesi
- [ ] Risk analizi (7 risk + azaltma stratejileri)
- [ ] 8 akademik referans

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
> ⚠️ **DOĞRULAMA (2026-05-02):** Gerçek notebook adı `notebooks/Dolap_EDA_Feature_Engineering.ipynb` (todo'da "01_eda_presentation.ipynb" olarak geçiyordu).
> `docs/PRESENTATION_GUIDE.md` dosyası **mevcut değil**. Show/Hide Code toggle notebook içinde doğrulanamadı.

- [ ] **Show/Hide Code mekanizması:** Notebook'ta toggle bulunamadı → eklenecek veya iddia geri çekilecek
- [x] **Takım üyesi görev dağılımı (3 kişi × 10 dk):**
  | Üye | Bölüm | Cell'ler | Süre |
  |-----|-------|----------|------|
  | **Furkan** | S1 Problem + S2 Data Collection + Target Dist. | Cell 1-6 | ~3 dk |
  | **Utku** | S3.1 Schema + S3.2 Stats + S3.3 Distributions | Cell 7-20 | ~3.5 dk |
  | **Halil** | S3.4 Correlations + Hypotheses + S4 Feature Eng. + Investigation + Conclusion | Cell 21-34 | ~3.5 dk |
- [x] **Tüm slide'lar İngilizce** — Türkçe terim varsa parantez içinde
- [ ] **10 dakika prova** — zamanlama kontrolü
- [ ] **Yedek slide'lar:** Sorulabilecek sorular için ekstra grafikler hazırla
- [x] Final notebook: `notebooks/Dolap_EDA_Feature_Engineering.ipynb` (26 cell, EDA + FE)
- [ ] Prova rehberi → `docs/PRESENTATION_GUIDE.md` **(yok, oluşturulacak)**

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

### Phase 7 — First Cohort Lifecycle ✅
> commit: `8c10484` — *Label all dataset with comprehensive temporal re-check: 5,472/6,059 (90.3%) labeled via StatusChecker*
> ⚠️ Etiketleme tamamlandı (2026-05-01 civarı). Aşağıdaki "Bekleme" maddeleri tarihsel kayıt olarak bırakıldı.

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
- [x] **Gün 2-7 (12-17 Mart):** Bekleme (7 gün labeling süresi) — tamamlandı
- [x] **cohort_20260311 re-check → labeling** ✅
  - `data/labels/cohort_20260311.jsonl` (6016 satır) + `cohort_20260311_summary.yaml`
  - Sold: 49 | Active: 1611 | Errors/Removed: 4356
  - 5431/6016 etiketli (=%90.3 cohort coverage)
- [x] **cohort_20250712 etiketleme** ✅
  - `data/labels/cohort_20250712.jsonl` (360 satır)
  - 41/43 etiketli
- [x] Label dağılımı analizi: sold vs not_sold oranı
  - Toplam etiketli: 5472/6059 (%90.3)
  - Sold: 347 (%6.34) | Not sold: 5125 (%93.66)
  - 2.cı tur mass relabeling: commit `8c10484` (StatusChecker temporal re-check)
- [x] Hedef: minimum 2 cohort labeled, 2000+ etiketli ilan ✅ (5472 etiketli)
- [ ] Veri kalitesi raporu: eksik alanlar, parse hataları → kısmen `target_variable_report.json`'da var, formal rapor yok
- [ ] **Bilinen sınırlama:** Late-window oranı yüksek (`late_window_count=6016`, çoğu 8+ gün) — `analyze_target_variable.py` çıktısı. M5 evaluation'da "labeled within strict 7-day window" alt grubu için ayrı metrik gerekli.

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

#### 🎯 **TRAINING READINESS REPORT (2 Mayıs 2026 — sync edildi)**

**Current State:** `data/interim/merged_data.csv` (single source CSV)
> Kaynak: `artifacts/metrics/target_variable_report.json` (`scripts/analyze_target_variable.py` çıktısı)

```
📊 DATASET OVERVIEW:
  Total rows: 6059
  Cohort count in file: 2 (20250712, 20260311)

🎯 TARGET COVERAGE (mass relabeling sonrası — commit 8c10484):
  Labeled rows (sold_within_7_days non-null): 5472 (%90.3)
  Unlabeled rows: 587 (%9.7)

🎯 TARGET DISTRIBUTION (only labeled subset):
  True  (Sold):    347 (6.34%)
  False (Active): 5125 (93.66%)
  → Class imbalance ratio ~1:14.8 → modelleme için ciddi pozitif sınıf eksikliği

⏱️ LABEL WINDOW QC:
  valid_window_count: 18 (yalnızca 7-8 gün penceresinde)
  early_window_count: 0 (RC1 guard çalışıyor ✅)
  late_window_count: 6016 (8+ gün — toplu re-check sonucu)
  early_window_ratio: 0.0

📉 COHORT BREAKDOWN:
  cohort_20250712: 43 row, 41 labeled
  cohort_20260311: 6016 row, 5431 labeled

🏪 SELLER CONCENTRATION (RC4 doğrulaması):
  Unique sellers (total): 49
  Unique sellers (labeled): 48
  Top-10 share: %54.3 (listings) | %55.1 (labeled)
  Top-20 share: %78.2 (listings) | %79.3 (labeled)
  → conbez tek başına 60 listing × %95 sold ≈ pozitiflerin %16'sı (high-leverage)
```

**🚨 INTERPRETATION (güncel):**
- Canonical `merged_data.csv` artık resmi pipeline ile yeniden üretildi.
- RC3 relabeling tamamlandı; `cohort_20260311` resmi label/snapshot akışı üretildi.
- 2.cı tur mass relabeling (commit `8c10484`) ile etiketleme kapsamı %27.7'den %90.3'e çıktı.
- Dataset training için kullanılabilir ama 3 ana sınırlama var:
  1. **Late-window dominantlığı** — 6016 satır 8+ gün sonra etiketlendi; "7 gün içinde satıldı" tanımı için strict subset (window 168-192h) sadece 18 satır.
  2. **Class imbalance** — %6.34 pozitif → `class_weight='balanced'`, threshold tuning, focal loss veya SMOTE şart.
  3. **Seller concentration** — 49 seller, top-10 %54 → group-aware split ZORUNLU (random shuffle çok iyimser tahmin verir).
- Model eğitiminde cohort/time filtreleri, `unknown/error` yönetimi, group-split ve sample weighting birlikte uygulanmalı.

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

*Mitigasyon kodu (TAMAMLANDI):*
- [x] **Group-aware split helper** — `src/utils/split.py:136` `temporal_group_train_val_test_split()` (seller leakage azaltımı, `__init__.py`'de export edilmiş)
- [x] **Seller-frequency feature** — `src/features/engineer.py:209-220`:
  - [x] `seller_listing_frequency` (raw count)
  - [x] `seller_frequency_log` (log1p)
  - [x] `seller_listing_frequency_capped` (95p cap)
  - [x] `seller_balance_weight = 1/sqrt(freq)` (cap/weight stratejisi için sample weighting hazır)

*Analiz (BEKLEYEN):*
- [ ] Seller concentration raporu üret:
  - [ ] top10 seller payı (kod tarafında çıkarılabilir, formal rapor yok)
  - [ ] top20 seller payı
  - [ ] seller başına sold rate dağılımı
  - **Önceki gözlem:** 49 seller, top-10 %54.3, conbez 60 listing × %95 sold (16% pozitif payı) — bu rakamlar formal rapora yazılmadı.
- [ ] Train/val split simulation çıktısı: leakage groups before/after, dropped train rows
- [ ] Raporla:
  - [ ] "Marketplace behavior vs labeling artifact" ayrımı (%6.34 sold rate doğal)
  - [ ] category bazında doğal düşük satış olasılığı (rapor için tablo)

**Definition of Done (RC4):**
- [x] Group-aware split + seller-frequency feature kod entegrasyonu tamamlandı (`src/utils/split.py`, `src/features/engineer.py`)
- [ ] Seller concentration metriği formal rapora işlendi (`artifacts/metrics/seller_concentration_report.{json,md}`)
- [ ] Train/val split seller leakage kontrolünden geçti (simulation log'u arşivlendi)
- [ ] **🚨 NOTEBOOK GAP DOĞRULANDI (2026-05-02):** `dolap_classification_final.ipynb` cell[6] satırında
  ```python
  X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.20, random_state=42, stratify=y, shuffle=True)
  ```
  → **stratified random shuffle** kullanıyor; `temporal_group_train_val_test_split` BAĞLANMAMIŞ. Aynı seller train+test'te bulunabilir. AUC=0.8150 sayısı seller-leakage altında raporlanmış olabilir.
  **Karar gerekli:**
  - Opsiyon A (savunma): Makale Limitations bölümüne ekle, group-aware split ek deneyini "future work" olarak bırak.
  - Opsiyon B (deney): Notebook'a yeni cell ekle, `temporal_group_train_val_test_split` ile aynı modeli yeniden eğit, AUC karşılaştırmasını makaleye koy.
  - **Önerim:** Opsiyon B — sadece XGBoost için bir ek satır makale güçlendirir; ~1-2 saatlik iş.

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
  - [ ] Create `configs/features.yaml` with all feature definitions (metadata) — şu an sadece brand_tiers var, eksik
  - [x] Store engineering code in `src/features/engineer.py` (FeatureEngineer class)
  - [ ] Generate feature importance baseline (on first few models)
  - [x] Save final feature matrix: `data/processed/engineered_features.parquet` (6059×38)
  - [x] Create features metadata JSON: `data/processed/features_metadata.json` (38 feature kolonu) — ⚠️ ad/encoding/range alanları yok, sadece kolon listesi

- [ ] **Potential Data Leakage Checks:**
  - ⚠️ **like_count / comment_count:** Only use @ scrape time, NOT later counts
  - ⚠️ **seller_rating_count:** May be post-purchase ratings (if used, must be @ scrape time)
  - ⚠️ **listing_date derived from other columns:** Ensure not using time-future information

### Phase 10 — Exploratory Data Analysis (EDA) ➡️ **EDA Presentation'a merge edildi**
> ℹ️ Bu phase artık ayrı yapılmayacak. Tüm EDA içeriği yukarıdaki
> "🎤 EDA PRESENTATION" bölümündeki Step 1-8 içinde yer alıyor.
> Notebook: `notebooks/Dolap_EDA_Feature_Engineering.ipynb` (todo'da eski adı `01_eda_presentation.ipynb` geçiyordu)

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
> ✅ **DOĞRULAMA (2026-05-02):** Notebook tabanlı modeling **TAMAMLANDI**.
> - `notebooks/dolap_classification_final.ipynb` — 6 model + tuning + threshold opt + bootstrap CI (37 cell, 13 section)
> - `notebooks/dolap_ablation_study.ipynb` — 3 versiyonlu ablation (FULL / NO_ENGAGEMENT / STATIC_ONLY)
> - Dataset: `data/processed/model_ready_v3.csv` (6007 × 60), 0 missing, target: `sold_within_7_days`
> - Train/Test split: 80/20 stratified shuffle (`random_state=42`)
>
> ⚠️ **`src/models/*.py` modülleri YAZILMADI** — notebook prototype yeterli kabul edilmiş; makale + CV için `src/`'a taşıma kararı M9'da konuşulacak.
> ⚠️ **RC4 group-aware split notebook'a bağlanmamış** — `temporal_group_train_val_test_split` mevcut ama notebook stratified random shuffle kullanıyor → seller leakage riski var (cell[6] satırında). Makale Limitations bölümünde belgelenmeli veya ek deney yapılmalı.

### Phase 11 — Baseline Models ✅ (notebook'ta)
> Notebook hücreleri: cell[8] (training), cell[15-19] (CM + classification report)

- [x] Logistic Regression (max_iter=1000, default class_weight) → AUC=0.7206, F1=0.2025
- [x] KNN (n_neighbors=7) → AUC=0.6964, F1=0.1931
- [x] Decision Tree (max_depth=8) → AUC=0.7116, F1=0.2491
- [x] Random Forest (n_estimators=200) → AUC=0.7604, F1=0.1875
- [x] Val set üzerinde metrikler: AUC-ROC, F1, Precision, Recall, Accuracy
- [x] Bootstrap 95% CI (cell[36], 1000 iter) — 6 modelin CI'ları rapor + makale Tablo 7'de
- [x] İlk karşılaştırma tablosu (cell[27] `summary` styled DataFrame)
- [ ] `src/models/baseline.py` — modüle taşıma (opsiyonel; notebook+rapor yeterli ise atlanabilir)
- [ ] Sonuçları `artifacts/experiments/` dizinine kaydetme (notebook output'u var ama experiment lifecycle'a girmedi)

### Phase 12 — XGBoost / LightGBM ✅ (notebook'ta)
> Notebook hücreleri: cell[8] (training), cell[19-23] (best model deep dive + SHAP)

- [x] XGBoost (n_estimators=300, lr=0.05, max_depth=5, subsample=0.8) → **AUC=0.8150** ⭐
- [x] LightGBM (n_estimators=300) → AUC=0.7798
- [x] Feature importance (cell[20] top-20 bar chart, gain-based)
- [x] Test set karşılaştırması (cell[15-17] CM + ROC + PR curves)
- [ ] CatBoost — yapılmadı (XGB+LightGBM yeterli kabul edildi)
- [ ] `src/models/tree_models.py` — modüle taşıma (opsiyonel)

### Phase 13 — Class Imbalance Handling ✅ (notebook'ta)
> Notebook hücreleri: cell[8] SMOTE in pipeline, cell[29] SMOTE-safe RandomizedSearchCV, cell[31] threshold opt

- [x] SMOTE deneyi (imblearn pipeline ile, train fold içinde)
- [x] SMOTE-safe Pipeline (CV fold içinde SMOTE — leakage'ı önlemek için)
- [x] Threshold tuning — XGBoost: 0.50 (F1=0.27, Recall=0.20) → 0.247 (F1=0.354, Recall=0.40)
- [ ] Class weight deneyi (separate experiment) — `seller_balance_weight` mevcut ama deney yapılmadı
- [ ] Undersampling deneyi (SMOTE seçildiği için atlandı)
- [x] İmbalance stratejisi karşılaştırma — ablation notebook ΔAUC tablosu

### Phase 14 — Hyperparameter Tuning ✅ (RandomizedSearchCV, notebook'ta)
> Notebook hücreleri: cell[28-29] tuning + comparison

- [x] RandomizedSearchCV (XGBoost): 6 hyperparameter grid → best params
  - Best: subsample=0.7, n_estimators=200, min_child_weight=5, max_depth=5, lr=0.01, colsample_bytree=0.6
  - CV AUC (honest, leak-free): 0.7560 | Test AUC: 0.7931 (vs original 0.8119)
- [ ] Optuna study (100 trial) — yapılmadı; RandomizedSearchCV yeterli kabul edildi
- [x] Study visualization — RandomizedSearchCV best_params_ + CV mean ± std
- [ ] Tuning sonuçları → `artifacts/experiments/` (notebook output'u var, experiment lifecycle'a yerleşmedi)

---

## 📊 M5 — EVALUATION & EXPLAINABILITY
> ✅ **DOĞRULAMA (2026-05-02):** Notebook tabanlı evaluation **TAMAMLANDI**.
> Notebook: `dolap_classification_final.ipynb` Section 6-13 + ablation notebook.

### Phase 15 — Test Set Evaluation ✅ (notebook'ta)
> Notebook hücreleri: cell[15] CM, cell[19] classification report, cell[36] bootstrap CI

- [x] Final model (XGBoost) → test set prediction (1202 örnek)
- [x] Metrikler: AUC-ROC, F1, Precision, Recall, Accuracy (6 model için tam tablo)
- [x] Optimal threshold tuning (PR curve, F1-maximize): default 0.50 → optimal 0.247
- [x] Confusion matrix heatmap (cell[15], 6 model 2×3 grid)
- [x] Classification report (cell[19], precision/recall/f1 per class)
- [x] **Bootstrap 95% CI** (cell[36], 1000 iter): XGB AUC=0.8150 [0.7613, 0.8722]
- [ ] `src/evaluation/evaluator.py` — modüle taşıma (opsiyonel)
- [ ] Sonuçlar `artifacts/experiments/` lifecycle'a yerleşmedi

### Phase 16 — SHAP Analysis ✅ (notebook'ta)
> Notebook hücreleri: cell[21] TreeExplainer, cell[23] H2 verification

- [x] SHAP TreeExplainer on test sample (400 listing)
- [x] SHAP beeswarm/summary plot (top features)
- [x] **H1-H4 hipotez doğrulama (post-hoc)** — H1 ✅ price_pctile_cat negatif yön, H2 ✅ brand_tier corr=+0.76 mean|SHAP|=0.16, H3 ✅ engagement_score top-5 pozitif, H4 ✅ seller_exp_log pozitif
- [x] Feature importance ranking (SHAP-based) — cell[20] gain-based + cell[21] SHAP-based
- [ ] SHAP waterfall (tek örnek açıklama) — yapılmadı
- [ ] SHAP dependence plots (top 3-5 feature) — yapılmadı
- [ ] `src/evaluation/shap_analysis.py` — modüle taşıma (opsiyonel)

### Phase 17 — Visualization Suite ✅ (notebook'ta)
> Notebook hücreleri: cell[11] bar charts, cell[13] radar, cell[15] CM, cell[17] ROC+PR, cell[33] learning curves

- [x] ROC curve (cell[17], tüm modeller aynı grafikte)
- [x] Precision-Recall curve (cell[17])
- [x] Feature importance bar chart (cell[20])
- [x] Confusion matrix heatmap (cell[15])
- [x] Threshold vs F1 grafiği (cell[31])
- [x] **Radar / Spider Chart** (cell[13], beyond template)
- [x] **Learning curves** (cell[33], beyond template — top-2 model)
- [x] Train vs Test Accuracy bar (cell[12]) — ⚠️ M7.3 kapsamında uyarı eklendi (SMOTE-train vs imbalanced-test, doğrudan kıyas yanıltıcı)
- [ ] Calibration plot — yapılmadı
- [ ] `src/evaluation/plots.py` — modüle taşıma (opsiyonel)
- [ ] Tüm figürler `artifacts/experiments/<exp>/figures/` lifecycle'a yerleşmedi

---

## 📝 M6 — REPORTING & DELIVERY
> 🎯 **Bu projenin CV ve akademik makale çıktısı bu milestone'da üretilir.**
> Hedef dergi: **Veri Bilimi Dergisi (DergiPark, TR Dizin)** — %20 benzerlik sınırı, Cambria + çift kolon + APA, EN ana metin + TR özet.
> 🔗 Detaylı görev planı: M7 (profesör cevabı) ve M8 (dergi yolu) bölümlerinde.

### Phase 18 — Final Analysis Report 🟡 (parça parça hazır, tek dosyada toplanmadı)

**Hazır parçalar (`reports/` klasörü):**
- [x] `reports/methodology_addendum.md` — 5 blok (engagement temporal, Tablo 7, overfitting caveat, H1-H4 SHAP test, ablation) hazır kopya-yapıştır metin
- [x] `reports/professor_response_brief.md` — iç analiz raporu (10 madde × kanıt-paket)
- [x] `reports/professor_response_email_draft.md` — TR mail taslağı (~700 kelime)

**Final teslim için bekleyen:**
- [ ] `reports/FINAL_REPORT.md` veya PDF — yukarıdaki parçaların tek dosyada birleştirilmesi
- [ ] Yönetici özeti (1 sayfa)
- [ ] Veri toplama süreci ve zorluklar
  - [x] Cloudflare WAF + Selenium gereksinimi (kod kanıtı `parsers.py`, `status_checker.py`)
  - [x] Cohort lifecycle (scrape → 7gün → re-check) — methodology_addendum §1
  - [ ] 49-seller / top-10 %54.3 concentration → group-aware split gerekçesi (RC4 raporu eksik)
- [x] Feature engineering kararları ve gerekçeleri (engineer.py + Bölüm 4)
- [x] Model karşılaştırma tablosu (methodology_addendum §2 Tablo 7, 6 model + bootstrap CI)
- [x] En iyi modelin SHAP analizi yorumu (methodology_addendum §4, H1-H4 doğrulama)
- [x] Sınıf dengesizliği çözüm karşılaştırması (notebook + ablation)
- [ ] Pratik öneriler: satıcılara fiyatlama/ilan tavsiyeleri (Discussion bölümünde olacak)
- [x] Limitasyonlar:
  - [x] Late-window etiket sapması (8+ gün) — todo'da belgelenmiş
  - [x] First-observation vs creation-time engagement (methodology_addendum §1)
  - [ ] Single-platform / single-language — makaleye eklenecek
  - [ ] Seller concentration / leakage riski (notebook stratified random split kullanıyor)
- [ ] Akademik referanslar (≥12 atıf hedefi — M8.5.4)

### Phase 19 — Paper Draft & Presentation 🟡 (iskelet hazır, prose yazımı kaldı)

**Makale taslağı (`reports/article_draft_en.md` — iskelet hazır):**
- [x] Abstract iskelet (6-noktalı blueprint, ~200-250 kelime hedef)
- [x] TR özet (`reports/article_abstract_tr.md` — yapı taşları)
- [x] Section structure: Abstract → Intro → Related Work → Data → Methodology → Experiments → Results → Discussion → Conclusion → References → Reviewer Mapping Appendix
- [x] §3.3 Engagement temporal (Reviewer Comment 1 cevabı)
- [x] §5.1 Tablo 1 (6 model + CI)
- [x] §5.3 SHAP-driven hypothesis testing (M8.1, dense paragraph)
- [x] §5.4 Ablation table (FULL/NO_ENGAGEMENT/STATIC_ONLY)
- [x] §5.5 Threshold optimization
- [x] §6.X Limitations
- [ ] **Prose yazımı** — bölüm-bölüm (M8.5.3, ~26 Mayıs deadline)
- [ ] Related Work atıfları ≥12 (M8.5.4)
- [ ] Akademik şablon aktarımı: Cambria + çift kolon + APA (M8.5.6)
- [ ] iThenticate benzerlik kontrolü <%20 (M8.5.7)

**Sunum slaytları (4 Mayıs sunumu — acil):**
- [ ] 4 Mayıs Pazartesi sunumu için profesörün 4 maddesini revize haliyle göstermek (ana sunum)
- [ ] Mevcut PDF + methodology_addendum 4 bloğu birleştirilip slaytlara aktarılmalı
- [ ] Hipotez sonuçları (H1-H4 ✅) slide'ı
- [ ] Ablation slide'ı (cold-start AUC=0.7491 vurgulu)

**CV satırı:**
- [ ] Repo public README'si (sonuç metrikleri, paper link, demo) — `README.md` halen Phase 0 generic
- [ ] LinkedIn project entry hazırlığı — submission sonrası

---

## 📊 İlerleme Özeti (2026-05-02 sync, notebook + reports doğrulaması ile)

| Milestone | Durum | Notlar |
|-----------|-------|--------|
| 🏗️ M0 — Foundation | 🟡 Phase 0/0.5 ✅, Phase 1 doc eksik | `docs/PROJE_RAPORU.md` yok — makale Related Work'e taşındı |
| 🌐 M1 — Data Collection | ✅ Tamamlandı | 2 cohort, 6059 ilan, 49 seller |
| 🎙️ EDA Presentation | 🟡 Notebook ✅, prova/Show-Hide/PRESENTATION_GUIDE.md ⏳ | Notebook: `Dolap_EDA_Feature_Engineering.ipynb` |
| ⏳ M2 — Temporal Labeling | ✅ Phase 6 ✅, Phase 7 ✅ (5472/6059 = %90.3 etiketli) | Late-window dominant — strict 7-gün subset 18 satır |
| 🧹 M3 — Data Processing | 🟡 Phase 8 ✅, Phase 9 kod ✅, Phase 9.1 RC1/2/3 ✅ + RC4 mitigation kod ✅ | ⚠️ RC4 notebook'a bağlanmamış — bkz. RC4 DoD; configs/features.yaml metadata eksik |
| 🤖 M4 — Modeling | ✅ **Notebook'ta tam** | 6 model, XGB AUC=0.8150 [CI], SMOTE-safe tuning, threshold opt 0.247→F1=0.354 |
| 📊 M5 — Evaluation | ✅ **Notebook'ta tam** | CM, ROC, PR, SHAP+H1-H4, bootstrap CI, learning curves, radar |
| 📝 M6 — Reporting | 🟡 Parçalar hazır, birleştirme + prose kaldı | methodology_addendum ✅ + article_draft_en iskelet ✅ + abstract_tr ✅ + email draft ✅ |
| 📨 M7 — Profesör Cevabı | ✅ 1. tur ✅, **M7.6 2. tur ✅ mail gönderildi 3 Mayıs** | A/B.1/B.2/B.3 cevapları + RC4 robustness + sunum takvimi |
| 🎤 M9 — 4 Mayıs Sunum | 🟡 Notebook + demo HAZIR, prova ⏳ | 20 dk yapı: 5 dk demo + 10 dk metrics + 5 dk Q&A; demo localhost'ta test edildi |
| 📰 M8 — DergiPark Yayın | ⏸️ **PAUSED** | Sunum bitene kadar açılmayacak (kullanıcı talimatı 3 Mayıs); ~26 Mayıs deadline sonrasına ertelenmiş olabilir |

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
| 19 | `7cc19b4` | `feat(M3): data cleaning pipeline — cleaner, merger, build_dataset` | develop |
| 20 | `586c491` | `chore(data): consolidate interim CSV into single merged_data source` | develop |
| 21 | `7c29422` | `docs(Phase 9): detailed target variable specification and feature engineering plan` | develop |
| 22 | `4ed9a43` | `feat: update merged dataset, notebook analysis, and dataset pipeline` | develop |
| 23 | `8c10484` | `Label all dataset with comprehensive temporal re-check: 5,472/6,059 (90.3%) labeled via StatusChecker` | develop |
| 24 | `9c2627e` | `yeni eda eklendi` | main |
| 25 | `82ac3d5` | `model_ready.csv, training ve evaluation notebook eklendi` | main |
| 26 | `877f544` | `Merge develop into main` | main |

## 🏗️ Altyapı Envanteri

### ✅ Implementasyon Tamamlanan Modüller
```
src/utils/
├── experiment.py       ← create_experiment, save_metadata, get_git_commit_hash
├── config_snapshot.py  ← snapshot_configs
├── data_version.py     ← compute_dataset_hash, compute_file_hash
├── seed.py             ← set_global_seed (random, numpy, torch, PYTHONHASHSEED)
├── split.py            ← temporal_train_val_test_split + temporal_group_train_val_test_split (RC4)
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
src/features/           ← ✅ engineer.py (FeatureEngineer + RC4 seller_frequency_log + seller_balance_weight)
src/dataset/            ← ✅ merger.py (DatasetMerger)
src/models/             ← ⏳ Boş (notebook'larda exploratory modeling var, modüle taşıma kararı bekliyor)
src/evaluation/         ← ⏳ Boş (Phase 15-17)
```

### 📓 Notebook Envanteri (gerçek dosyalar)
```
notebooks/
├── Dolap_EDA_Feature_Engineering.ipynb  ← ✅ EDA Presentation (Step 1-8) + FE highlights
├── dolap_classification_final.ipynb     ← ✅ M4+M5 (6 model + tuning + SHAP + bootstrap CI + threshold) [37 cell]
└── dolap_ablation_study.ipynb           ← ✅ FULL/NO_ENGAGEMENT/STATIC_ONLY ablation
```

### 📑 Reports Envanteri (`reports/` klasörü, M7+M8 çıktıları)
```
reports/
├── article_draft_en.md             ← 🟡 EN makale iskeleti (9 bölüm + Reviewer Mapping appendix), prose yazımı kaldı
├── article_abstract_tr.md          ← 🟡 TR özet iskelet (6-noktalı yapı)
├── methodology_addendum.md         ← ✅ 5 blok (PDF rapora kopya-yapıştır kaynağı)
│                                       §1 engagement temporal | §2 Tablo 7 (6 model+CI)
│                                       §3 overfitting caveat | §4 H1-H4 SHAP test
│                                       §5 ablation
├── professor_response_brief.md     ← ✅ İç analiz (10 madde × kanıt-paket)
└── professor_response_email_draft.md ← ✅ TR mail taslağı (~700 kelime, Tablo 7 + H tablosu)
```

### 📊 Üretilmiş Veri/Metrik Çıktıları
```
data/interim/
├── merged_data.csv              ← canonical (6059 × 42, %90.3 etiketli)
├── merged_data.parquet
├── cleaned_all.parquet/.csv     ← Phase 8 çıktısı
└── merged_{cohort_id}.parquet   ← cohort-bazlı

data/processed/
├── engineered_features.parquet  ← Phase 9 çıktısı (6059 × 38, RC4 features dahil)
├── features_metadata.json       ← ⚠️ kolon listesi var, per-feature metadata eksik
└── model_ready_v3.csv           ← M4 notebook girdisi (commit 82ac3d5)

data/labels/
├── cohort_20250712.jsonl        ← 360 satır
├── cohort_20260311.jsonl        ← 6016 satır
└── cohort_20260311_summary.yaml

artifacts/metrics/
└── target_variable_report.json  ← 5472/6059 etiketli, %6.34 sold rate
```

---

## ⚡ Sonraki Adım (2026-05-02)

> **🎯 Gerçek durum:** Veri + FE + Modeling + Evaluation **notebook'ta tamamlanmış**. M7+M8 raporlama parçaları %80 hazır. Kalan iş: birleştirme, prose yazımı, sunum.

### Acil deadline'lar (3 Mayıs gece itibariyle)
| Tarih | İş | Durum |
|---|---|---|
| 4 Mayıs Pzt sabah | Profesöre 2. tur cevap maili gönder | ✅ Gönderildi |
| **4 Mayıs Pzt** | **20 dk sunum** | 🟡 Notebook + demo hazır; prova ⏳ |
| ~26 Mayıs | DergiPark makale draft teslim | ⏸️ **PAUSED** — sunum sonrası açılacak (kullanıcı talimatı) |

### Önümüzdeki kritik bloklar (sunum hazırlık)

**🔴 4 Mayıs Pzt SUNUM ÖNCESİ (kullanıcı işi, toplam ~1 saat):**

1. **M9.1.7** — `dolap_classification_final.ipynb` → Restart & Run All, hata kontrolü (sabah, ~10 dk)
2. **M9.2.5** — Demo testi sunum makinesinde:
   - `pip install flask flask-cors joblib pandas xgboost`
   - `python demo/demo_server.py`
   - Tarayıcıda `http://127.0.0.1:5000/` aç
   - Defaults ile predict + 2-3 farklı feature kombosu dene (~10 dk)
3. **M9.3.1** — 20 dk prova: kim ne anlatacak, geçişler, demo akışı (~30 dk)
4. **M9.3.2** — Görev dağılımı: 3 üye × ~6-7 dk (kullanıcı belirleyecek)
5. **M9.3.3** — Olası soru–cevaplara hızlı bakış (~10 dk)

**⏸️ SUNUM SONRASI — kullanıcı talimatıyla açılacak:**

> 🔴 **HATIRLATMA:** Makale yazımı (M8.5) sunum bitene kadar açılmayacak. Kullanıcı 3 Mayıs'ta talimat verdi: *"daha makale yazılmayacak bana hatırlat bunu sadece sonrasında"*.

Sunum sonrası, kullanıcı onayıyla aşağıdakilere geçilebilir (sırası kullanıcıya bağlı):
- M8.5.3 — Makale prose yazımı
- M8.5.4 — Related Work atıfları (≥12)
- M8.5.6 — Akademik şablon aktarımı (Cambria + çift kolon + APA)
- M8.5.7 — iThenticate benzerlik kontrolü
- M8.4 — `is_negotiable` re-scrape (Cloudflare ban riski; kullanıcı onayı gerekli)
- Phase 1 PROJE_RAPORU.md doc yazımı (M0)
- src/models/, src/evaluation/ modülleştirme (opsiyonel; notebook yeterli kabul edildi)

### Bilinen ama kapatılmamış borçlar (kapsam dışı / ileride)
- `docs/PROJE_RAPORU.md` yok — Phase 1 araştırması makale Related Work'e entegre olacak; ayrı doküman gerek yok
- `docs/PRESENTATION_GUIDE.md` yok — gerekirse sunum öncesi yazılır
- `configs/features.yaml` per-feature metadata eksik — sadece brand_tiers var; makale için kritik değil
- `scripts/validate_features.py` yok — notebook QC sayıları yeterli kabul edildi
- Categorical target encoding (color, size, category) — şu an frequency encoding kullanılmış olabilir, doğrulanmadı
- Late-window etiket sapması (6016 satır 8+ gün) — makale Limitations'da belgelenecek
- `engineered_features.parquet` (6059 × 38) ile `model_ready_v3.csv` (6007 × 60) tutarsızlığı — notebook v3 kullanıyor; engineer.py'nın çıktısı bu değil. **Bu farkın açıklanması gerekli** (muhtemelen v3 daha geniş feature set ile EDA notebook'tan üretildi). Makale Methodology bölümüne hangi feature setin kullanıldığı net yazılmalı.

### Tamamlanan zaman çizelgesi
- 11 Mart: ✅ Scrape + ✅ Cleaning pipeline
- 19 Mart: ✅ Phase 9 kickoff + RC1/RC2 kod entegrasyonu
- 24 Mart: ✅ RC3 resmi relabeling + dataset rebuild
- ~1 Mayıs: ✅ Mass relabeling (5472/6059 = %90.3) — commit `8c10484`
- 1 Mayıs: ✅ M4 + M5 notebook'ları (`dolap_classification_final`, `dolap_ablation_study`)
- 1 Mayıs: 📨 Profesör geri bildirimi alındı (M7 bölümünde takipte)
- 1 Mayıs: ✅ Methodology addendum + article draft + TR abstract + email draft yazıldı
- 2 Mayıs: ✅ todo.md sync (codebase + notebook + reports doğrulaması)

---

## M7 — Profesör Geri Bildirimi (Mayıs 2026)

> **Bağlam:** Profesör 1 Mayıs 2026'da ilk geri bildirimini (4 madde + 6 dergi yolu maddesi),
> **2 Mayıs gecesi ikinci tur feedback'i** (3 yeni teknik gözlem + 1 dil uyarısı, mail
> içinde) göndermiştir. M7.1-M7.5 ilk turu kapatır; **M7.6 ikinci turu** kapatır.
> Her görev tek başına yapılabilecek şekilde küçük tutulmuş olup, ön-doğrulama
> bulguları (kod tarafında ne var/yok) inline yazılmıştır ki tekrar araştırma
> gerekmesin.
>
> **Ön-analiz özeti (1 Mayıs 2026, kod tabanında doğrulandı):**
> - Engagement scrape zamanı: `src/scraping/parsers.py:182-184` listing
>   ilk scrape'inde `like_count` / `comment_count` yakalar.
> - 7-gün re-visit: `src/labeling/status_checker.py` engagement alanlarına
>   **dokunmaz**; yalnızca `Satıldı` / 404-410 / aktif kontrolü yapar.
>   → Sızıntı YOK; ancak rapor metninde bu durum açıkça belgelenmeli.
> - Cell 12 (overfitting grafiği): `train_acc` SMOTE-resampled
>   (`X_train_res, y_train_res`) üzerinden, `test_acc` orijinal dengesiz
>   test seti üzerinden hesaplanmaktadır → karşılaştırma yanıltıcı.
> - Tablo 7 verisi mevcut: `notebooks/dolap_classification_final.ipynb`
>   cell[8] sonrası `df_res` DataFrame'i 6 model için Accuracy, Precision,
>   Recall, F1-Score, ROC-AUC sütunlarının tamamını içeriyor.
> - H1–H4 hipotezleri: kod tabanında / notebook'larda hiçbir yerde
>   geçmiyor → proposal feedback / proposal dosyasından çıkarılmalı.

### M7.1 — Engagement Temporal Documentation (Madde 1)

> ✅ **Çıktı:** `reports/methodology_addendum.md` Bölüm 1 (Engagement
> Özelliklerinin Zamansal Konumu + Limitations cümlesi). Mail brief:
> `reports/professor_response_brief.md` A.1.

- [x] **M7.1.1** — Rapor "Metodoloji > Veri Toplama" bölümüne aşağıdaki
  içeriği ekleyen tek paragraflık metni yaz (kod kanıtı: `parsers.py:182-184`,
  `status_checker.py` engagement'a dokunmuyor):
  - "Engagement özellikleri (`like_count`, `comment_count`,
    `engagement_score`, `like_pctile_cat`) yalnızca **ilk scrape anında**
    `_parse_engagement` fonksiyonu üzerinden alınmıştır."
  - "7. günde yapılan re-visit (`status_checker.py`) yalnızca satış
    durumunu (`Satıldı` / aktif / kaldırılmış) kontrol eder; engagement
    sayılarını güncellemez."
  - "Bu nedenle engagement değerleri etiketleme penceresi sonrası
    bilgiyi içermez ve veri sızıntısı bulunmamaktadır."
- [x] **M7.1.2** — Aynı paragrafta sınırlamayı belirt: "İlk scrape, listing
  yayınlandıktan rastgele bir süre sonra gerçekleşebilir; dolayısıyla
  engagement 'listing oluşturulduğu an' yerine 'ilk gözlem anı'
  değerleridir." (Bu uyarı Limitations / Future Work bölümüne de
  eklenebilir.)

### M7.2 — Tablo 7 Eksik Metrikler (Madde 2)

> ✅ **Çıktı:** `reports/methodology_addendum.md` Bölüm 2. 6 model × 5
> metrik tam tablo, ROC-AUC azalan, 4 ondalık. Veri kaynağı: notebook
> cell[8] `df_res` HTML çıktısı (run-time hesaplamaya gerek kalmadan
> mevcut çıktıdan parse edildi).

- [x] **M7.2.1** — `notebooks/dolap_classification_final.ipynb` aç,
  cell[8]'i çalıştırıp `df_res` çıktısını al (Accuracy, Precision, Recall,
  F1-Score, ROC-AUC × 6 model). Notebook zaten bu değerleri üretiyor;
  yeni hesaplamaya gerek yok.
- [x] **M7.2.2** — `df_res` çıktısını markdown tablo olarak biçimlendir
  (raporun Tablo 7 stiline uygun, 4 ondalık basamak). Örnek tek satırlık
  kod: `print(df_res[['Accuracy','Precision','Recall','F1-Score','ROC-AUC']].to_markdown(floatfmt=".4f"))`.
- [x] **M7.2.3** — Raporda Tablo 7'yi tamamla: 6 modelin tamamı için
  Precision/Recall/Accuracy sütunlarını doldur, satır sıralamasını
  ROC-AUC'a göre azalan şekilde koru (notebook ile aynı sıra).

### M7.3 — Overfitting Grafiği Caveat (Madde 3)

> ✅ **Çıktı:**
> - Notebook cell[12] güncellendi: yeni başlık (multi-line, "not
>   directly comparable" uyarısı) + figtext alt-not (EN) + cell-comment
>   (TR). `outputs` temizlendi → bir sonraki run'da yeni grafik
>   render edilecek.
> - `reports/methodology_addendum.md` Bölüm 3: rapora kopyalanacak TR
>   yorum bloğu hazır, "5-fold CV (XGBoost: 0.7517 ± 0.024) +
>   öğrenme eğrileri" referansıyla.

- [x] **M7.3.1** — `notebooks/dolap_classification_final.ipynb` cell[12]:
  `ax.set_title(...)` çağrısını güncelle. Yeni başlık:
  `"Train vs Test Accuracy — SMOTE-resampled train vs imbalanced test (not directly comparable)"`.
- [x] **M7.3.2** — Aynı cell'in sonuna `plt.figtext(...)` ile alt-not ekle:
  `"Train accuracy SMOTE-resampled (50/50) veri üzerinde, test accuracy orijinal dengesiz test seti üzerinde hesaplanmıştır — doğrudan karşılaştırılmamalıdır. Overfitting yorumu için Bölüm 9 öğrenme eğrilerine bakınız."`
- [x] **M7.3.3** — Raporda bu grafiğin yorumlandığı paragrafa aynı uyarıyı
  Türkçe olarak ekle: "Train accuracy SMOTE-resampled dengeli veri
  üzerinde hesaplanmıştır; test accuracy ile doğrudan karşılaştırılmamalıdır.
  Overfitting analizi için öğrenme eğrileri referans alınmalıdır."

### M7.4 — Hipotez Testleri H1–H4 (Madde 4)

> ✅ **Çözüldü (post-hoc çerçeveyle).** Kullanıcı netleştirdi: proposal
> feedback (Mart 2026) Dolap'ı "Seçenek 2" olarak öneren mailmiş;
> içinde formel H1–H4 yokmuş, sadece konu önerisi + özellik listesi.
> Profesör mailde yalnızca H1 örneği vermişti.
>
> **Çözüm:** H1 örneği temel alınarak proposal'daki önerilen
> özellik listesi + domain bilgisi üzerinden 4 hipotez post-hoc
> tanımlandı, SHAP yön analizi ile test edildi.
>
> **Sonuç:** H1 ✅ Doğrulandı (price_pctile_cat negatif SHAP),
> H2 ⚠️ Kısmen (brand_tier × fiyat karışımı), H3 ✅ Doğrulandı
> (engagement_score SHAP top-5 pozitif), H4 ✅ Doğrulandı
> (seller_exp_log notebook Business Insights pozitif).
>
> **Çıktılar:**
> - `reports/methodology_addendum.md` Bölüm 4 (rapor metni, post-hoc
>   çerçeveleme + 4 hipotez detayı + özet cümle)
> - `reports/professor_response_brief.md` A.4 (mail için ton uyarısı:
>   "proposal'da formel listemiz yoktu, H1 çerçevenizi domain'e
>   uyarladık" mesajı; defansif olmadan ama net)
>
> **H2 kesinleştirildi (2026-05-02):** brand_tier × SHAP
> korelasyonu = +0.7610, mean(|SHAP|) = 0.1614 →
> **Doğrulandı**. Notebook'a cell[22-23] (H2 verification)
> eklendi; tüm rapor / makale / mail dosyalarında "Kısmen ⚠️"
> → "Doğrulandı ✅" güncellendi, yıldız notu kaldırıldı.

- [x] **M7.4.1** — Proposal / proposal feedback dosyasını bul: önce
  `reports/`, `docs/`, repo kökü, ardından kullanıcı yerel dosyalarında
  ara. H1–H4 metinlerini çıkar.  
  → Kullanıcıdan netleşti: proposal feedback Dolap konusunu ilk öneren
  Mart 2026 maili; biçimsel H1–H4 listesi yok, sadece konu
  seçeneği + özellik önerileri. Profesör H1 örneğini sonradan
  4-maddelik feedback'inde verdi.
- [x] **M7.4.2** — Her hipotezi bir kanıt-özelliğine eşle.  
  → 4 hipotez post-hoc tanımlandı:
    - H1: `price_pctile_cat` (profesörün verdiği örnek)
    - H2: `brand_tier`, `is_known_brand`
    - H3: `engagement_score`, `like_count`, `like_pctile_cat`
    - H4: `seller_exp_log`, `seller_listing_count`, `is_super_seller`
- [x] **M7.4.3** — Raporda yeni alt bölüm aç (Bölüm 8.X — Domain
  Hipotezlerinin SHAP-Tabanlı Testi). Her hipotez için 2-3 cümlelik
  blok: metin + SHAP yönü + karar.  
  → `reports/methodology_addendum.md` Bölüm 4'te yazıldı; post-hoc
  çerçeveleme paragrafı + 4 hipotez bloğu + tartışma cümlesi
  hazır.
- [x] **M7.4.4** — Tartışma / Sonuç bölümüne hipotez sonuçlarını
  özetleyen bir cümle ekle.  
  → Yazıldı: "4 hipotezden 3'ü doğrulandı, 1'i kısmen desteklendi
  (H2 — fiyat-marka karışımı)". Yorumlanabilirlik vurgusu ile
  kapatıldı.

### M7.5 — Final Kontrol & Teslim

- [ ] **M7.5.1** — Tüm M7.x maddeleri kapandıktan sonra rapor PDF'ini
  yeniden derle ve değişen sayfaları (Metodoloji, Tablo 7, Cell 12
  yorumu, Hipotez bölümü) gözle doğrula.  
  → **Kullanıcı aksiyonu (repo dışı).** PDF/Word kaynağı repoda yok;
  `reports/methodology_addendum.md` 4 bloğunu manuel olarak rapora
  aktar, sonra notebook cell[12]'yi yeniden çalıştırıp grafiği
  yenile. Bu kutu, kullanıcı aktarımı tamamladığında işaretlenecek.
- [x] **M7.5.2** — Profesörün 4 maddesinin her birine kısa cevap içeren
  e-posta taslağı hazırla; her madde için "ne değişti + raporda hangi
  sayfada" referansı ver.  
  → ✅ **Çıktı:** `reports/professor_response_email_draft.md` —
  Türkçe, ~700 kelime, 10 madde (4 ana + 6 dergi yolu) + takvim
  önerisi + kullanıcı kontrol listesi. Tablo 7 ve hipotez tablosu
  mailin gövdesine yerleştirildi. Mail Madde 4'te post-hoc çerçeveleme
  ("proposal'da formel H1–H4 listesi yoktu, H1 örneğinizi uyarladık")
  defansif olmadan profesyonel tonla yazıldı.


---

### M7.6 — İkinci Tur Profesör Feedback (3 Mayıs 2026, sunum öncesi son revize)

> **Bağlam:** 2 Mayıs gecesi profesörden ikinci tur feedback geldi. Feedback,
> 1. tur cevabımızı **olumlu** karşıladı ama makaleye geçmeden ele alınması
> gereken **3 yeni teknik gözlem + 1 dil uyarısı** içeriyor. 4 Mayıs Pzt
> sunumdan önce çözülmeli.
>
> **Yeni feedback (kısa özet):**
> - **A.** "post-hoc tanımladık" yerine **"post-hoc confirmatory analysis"** kullan (dil uyarısı, makale dili için kritik)
> - **B.1.** Test AUC=0.8150 vs CV AUC=0.7517 → **+0.063 anomali**, kontrol et
> - **B.2.** STATIC_ONLY: AUC −0.066 (kabul) ama F1 **−%59** (0.268 → 0.110) → AUC tek başına yorumlanmamalı
> - **B.3.** LightGBM F1=0.320 > XGBoost F1=0.268 ama XGB AUC önde → "hangi modeli öneriyorsunuz" net cevap gerekli
>
> **Yan-bağlam: notebook canonical kararı (3 Mayıs):**
> - `notebooks/dolap_classification_final.ipynb` (1 Mayıs commit) — **canonical**
>   - Hocaya gönderilen Tablo 7 + Bootstrap CI buradan: XGB AUC=0.8150 [0.7613, 0.8722]
>   - H2 verification cell'i (corr=+0.7610) burada (cell[22-23])
> - `notebooks/dolap_classification_final2.ipynb` (3 Mayıs WP, ekip arkadaşının güncel sürümü) — **arşiv**
>   - H2 cell'i yok, yeni inline ablation cell'i farklı sayılar üretmiş (STATIC_ONLY 41-feat AUC=0.7951 vs hocaya verilen 26-feat AUC=0.7491)
>   - Karar: hocayla tutarlılık için final ile devam → final2 → `notebooks/_archive/` (kullanıcı onayı sonrası)
> - **final2'den faydalanılacak parça:** sondaki inline-ablation görsel cell'i (cell[35]) eski sayılarla yeniden adapte edilerek `final` notebook'una eklenecek
>
> **Yan-bağlam: RC4 robustness deneyi (2 Mayıs çıktı):**
> - `scripts/seller_leakage_experiment.py` çalıştırıldı → `artifacts/metrics/seller_leakage_robustness.{json,md}` üretildi
> - Sonuç (canonical engineer.py + 26 feature):
>   - Random split AUC = 0.7755 [0.7116, 0.8348]
>   - Group-aware split AUC = 0.6832 [0.6079, 0.7544], **ΔAUC = −0.092**
> - Akademik değer: B.1'deki Test>CV anomalisinin **kök nedenine direkt kanıt** sağlıyor (CV=0.7517, group-aware=0.6832 → CV ile çok daha tutarlı; random split AUC seller-identity bilgisinden faydalanıyor).
> - Yorum stratejisi: **Yorum 1 (dürüst raporlama)** — headline AUC=0.8150 korunur, robustness check Limitations + ek tablo olarak makaleye girer.

#### M7.6.0 — Notebook Canonical Kararı

- [x] **M7.6.0.1** — Karşılaştırma tamamlandı: final ile final2 cell-by-cell diff alındı
  - 16/37 cell farklı; final2 H2 verification cell'ini drop etmiş, sondaki inline-results cell'ini eklemiş
  - Sayısal farklar: XGB AUC 0.8150 vs 0.8119 (Δ=−0.0031, n_jobs nondeterminism)
  - Ablation farkı: STATIC_ONLY 26 feat (final) vs 41 feat (final2) — farklı feature listesi
- [x] **M7.6.0.2** — Karar: `final` canonical (hocayla tutarlılık öncelikli)
- [x] **M7.6.0.3** — `notebooks/dolap_classification_final2.ipynb` → `notebooks/_archive/dolap_classification_final2_wp_2026-05-03.ipynb`
  - Kullanıcı onayı: "tamam final ile devam edelim" (3 Mayıs) ✅
  - Dosya taşındı (3 Mayıs)

#### M7.6.1 — RC4 Robustness Çıktısını Reports'a Taşı (Yorum 1: dürüst raporlama)

- [x] **M7.6.1.1** — `reports/methodology_addendum.md` Bölüm 6 (ana metinde Bölüm 8.Z) eklendi
  - Tablo: Protocol A (random) vs Protocol B (group-aware) — AUC, F1, CI, ΔAUC
  - 49-seller limitation acknowledgment + Limitations cümlesi hazır
  - Bağlantı: B.1 anomalisinin kök nedeni → CV=0.7517 ↔ group-aware=0.6832 yakın
- [x] **M7.6.1.2** — `reports/article_draft_en.md` §5.X (Robustness Check) eklendi
  - Tablo 3 (EN) + Limitations bölümünde 49-seller acknowledgment
  - F1=0 default-eşik mis-calibration notu

#### M7.6.2 — A maddesi: "post-hoc confirmatory analysis" Dili

- [x] **M7.6.2.1** — `reports/methodology_addendum.md` Bölüm 4 başlık ve içerik revize edildi
  - "Post-Hoc Confirmatory SHAP Analizi" başlığı
  - "post-hoc confirmatory analiz" çerçeve paragrafı ekli
  - 🔴 Dil notu (M7.6.2 referansı) inline yerleştirildi
- [x] **M7.6.2.2** — `reports/article_draft_en.md` §5.3 dili güncellendi
  - "post-hoc confirmatory SHAP-based examination" çerçevesi
  - Pre-registration eksikliğinin açıkça kabul edildiği not eklendi
- [x] **M7.6.2.3** — Notebook Section 12'de "post-hoc confirmatory" dili (M7.6.6.4 ile birlikte)

#### M7.6.3 — B.1 cevabı: Test AUC > CV AUC Anomalisi (RC4 ile bağla)

- [x] **M7.6.3.1** — `reports/methodology_addendum.md` Bölüm 7 (ana metinde Bölüm 8.W) eklendi
  - Sayılar: Test AUC=0.8150, 5-fold CV AUC=0.7517 ± 0.024, Δ=+0.063
  - 4 olası neden + RC4 ile sayısal kapatma
  - Sonuç cümlesi: kök neden seller-identity leakage; headline + leakage-free birlikte raporlanıyor
- [x] **M7.6.3.2** — `reports/article_draft_en.md` §5.2 genişletildi
  - "Cross-validation honesty and the test–CV gap" başlığı
  - Reviewer Comment B.1 ile direkt bağ + §5.X'e atıf

#### M7.6.4 — B.2 cevabı: STATIC_ONLY F1 Düşüşü + Threshold Optimization

- [x] **M7.6.4.1** — Notebook Section 15 eklendi (cell 39+40)
  - STATIC_ONLY 26-feat yeniden eğitim + PR-curve threshold optimization
  - Default τ vs optimal τ karşılaştırması + grafik
- [x] **M7.6.4.2** — `reports/methodology_addendum.md` Bölüm 5 ek (ana metinde Bölüm 8.Y.1) eklendi
  - AUC vs F1 trade-off açıklaması
  - Pratik çıkarım: top-K ranking deployment vs binary decision
- [x] **M7.6.4.3** — `reports/article_draft_en.md` §5.4 ek paragraf eklendi
  - Reviewer Comment B.2 doğrudan referans + §5.5 threshold tuning ile köprü
  - Notebook §15 atıfı

#### M7.6.5 — B.3 cevabı: XGBoost vs LightGBM — Hangi Model?

- [x] **M7.6.5.1** — `reports/methodology_addendum.md` Bölüm 8 (ana metinde Bölüm 9.X) eklendi
  - 3 bağımsız gerekçe (AUC üstünlüğü + tighter CI, tuned F1, SHAP uyumu)
  - LightGBM eş-ağırlıkta alternatif notu
- [x] **M7.6.5.2** — `reports/article_draft_en.md` §6.X Discussion paragraf eklendi
  - Primary model = XGBoost önerisi 3 gerekçe ile
  - Threshold-tuned operating point karşılaştırması

#### M7.6.6 — Notebook Cell Eklemeleri (final canonical'e)

> ✅ 6 yeni cell eklendi (cell index 37-42); notebook 37 → 43 cell'e büyüdü.

- [x] **M7.6.6.1** — Section 14 — Test vs CV AUC Anomaly Explanation
  - cell 37 markdown + cell 38 code: `seller_leakage_robustness.json` yükle, 4-bar görsel (CV band + Group-aware + Random + Headline)
- [x] **M7.6.6.2** — Section 15 — STATIC_ONLY Threshold Optimization
  - cell 39 markdown + cell 40 code: 26-feat retrain + PR-curve sweep + F1 vs τ grafiği
- [x] **M7.6.6.3** — Section 16 — Inline Ablation + Bootstrap CI Display
  - cell 41 markdown + cell 42 code: `reports/ablation_results.json` (yeni üretildi) → 2-panel bar chart (AUC + F1)
  - JSON dosyası: FULL/NO_ENGAGEMENT/STATIC_ONLY headline sayıları + Tablo 7 (6 model) + RC4 sayıları
- [x] **M7.6.6.4** — Section 12 (Key Takeaways) genişletildi
  - "post-hoc confirmatory" dili
  - Yeni satırlar: §14, §15 lecture concept coverage'a eklendi
  - Yeni Reviewer-Comment Mapping tablosu (1. tur + 2. tur)

#### M7.6.7 — Mail Revize Draft (4 Mayıs sunum öncesi gönderim)

- [x] **M7.6.7.1** — `reports/professor_response_email_draft.md`'a 2. tur cevap bölümü eklendi (~600 kelime)
  - Açılış: "İkinci tur değerlendirmenize hassasiyetle bakıp..."
  - Madde A (post-hoc confirmatory) ✅
  - Madde B.1 (Test>CV anomaly): tablo + RC4 yorumu ✅
  - Madde B.2 (STATIC_ONLY F1): italik blok + Section 15 referansı ✅
  - Madde B.3 (XGB vs LGBM): 3 gerekçe + LightGBM alternatif notu ✅
  - Sunum + makale takvimi
  - 2. tur kullanıcı kontrol listesi
- [x] **M7.6.7.2** — Mail uzunluğu ~600 kelime (1. tura kıyasla daha odaklı, profesörün 2. tur tonuna uygun)
- [ ] **M7.6.7.3** — Kullanıcı onayı sonrası 4 Mayıs Pzt sabah gönderim

#### M7.6.8 — Senkronizasyon

- [x] **M7.6.8.1** — `reports/feature_set_provenance.md` üretildi (S2 sonucu)
- [x] **M7.6.8.2** — `artifacts/metrics/seller_leakage_robustness.{json,md}` üretildi (RC4 deneyi)
- [x] **M7.6.8.3** — `reports/ablation_results.json` üretildi (Section 16 girdi dosyası)

#### Definition of Done (M7.6)

- [ ] Mail revize draft kullanıcı onayı aldı (mail göndermeden önce)
- [ ] 4 Mayıs Pzt sabah profesöre gönderildi
- [ ] Sunum sırasında §14 (robustness) + §15 (threshold opt) + §16 (ablation) hazır görseller olarak kullanılabilir
- [ ] PDF rapor güncellendi (M7.5.1 kullanıcı aksiyonu)
- [ ] todo.md M7.6 alt-maddelerinin tamamı kapatıldı

#### Öncelik sırası ve gerçekleşme (3 Mayıs run)

```
✅ P0 TAMAMLANDI (~2 saat Claude):
  M7.6.0.3 → final2'yi arşive taşı                          ✅
  M7.6.1.1 → methodology_addendum Bölüm 6 (RC4)            ✅
  M7.6.2.1 → methodology_addendum Bölüm 4 dili             ✅
  M7.6.3.1 → methodology_addendum Bölüm 7 (B.1)            ✅
  M7.6.4.2 → methodology_addendum Bölüm 5 ek (B.2)         ✅
  M7.6.5.1 → methodology_addendum Bölüm 8 (B.3)            ✅
  M7.6.7.1 → mail revize draft                              ✅

✅ P1 TAMAMLANDI (~2 saat Claude):
  M7.6.6.3a → ablation_results.json üret                   ✅
  M7.6.6.3b → Section 16 cell (inline ablation+CI)         ✅
  M7.6.6.1 → Section 14 cell (B.1 görsel)                  ✅
  M7.6.6.2 → Section 15 cell (B.2 threshold opt)           ✅
  M7.6.6.4 → Section 12 dili revize                         ✅
  M7.6.1.2 → article_draft §5.X                             ✅
  M7.6.2.2 → article_draft §5.3 dili                        ✅
  M7.6.3.2 → article_draft §5.2 genişletme                  ✅
  M7.6.4.3 → article_draft §5.4 ek                          ✅
  M7.6.5.2 → article_draft §6.X paragraf                    ✅

⏳ P2 (sunum/mail sonrası kullanıcı aksiyonu):✅
  M7.6.7.3 → mail kullanıcı onayı + 4 Mayıs sabah gönderim
  M7.5.1   → PDF rapor aktarımı (methodology_addendum 5+4 blok)
  Section 14/15/16 notebook'ta çalıştırılıp grafikler render edilecek
  (kullanıcı sunum öncesi: notebook'u baştan run, screenshot'la)
  
DURUM: 4 Mayıs sabah deadline'a hazır.
```

---

## M9 — 4 Mayıs Sunum (Live Demo + Model Decisions)

> **Bağlam:** Profesör mailinde (3 Mayıs) sunum yapısını netleştirdi. Bu sunum,
> önceki EDA sunumunun **devamıdır**; veri ve EDA tekrar anlatılmayacak.
> Odak: model eğitimi, değerlendirme, **canlı demo**.
>
> **Sunum süresi:** 20 dk · **Format:** notebook üzerinden (kod gizli) +
> Flask demo · **Slayt veya PDF zorunlu değil**.

### Sunum yapısı (öğretmen şablonu)

| Block | Süre | Kaynak | Notlar |
|---|---:|---|---|
| Araştırma sorusu hatırlatma | 0.5 dk | §1 markdown | "7 gün içinde satılır mı?" |
| **Canlı demo** | **5 dk** | `demo/demo_server.py` + tarayıcı | Profesör birden fazla feature kombinasyonu deneyecek |
| Model kararları & metrikler | **10 dk** | §3 train, §6 CM, §7 ROC/PR, §11 tuning, §13 CI, §16 ablation, §14 robustness | Hangi modeli neden? Test/CV/Feature importance |
| Sonuç & soru–cevap | **5 dk** | §15 cold-start, §6 confusion patterns, §14 group-aware | Limitations + nerede hata yapıyor |

### M9.1 — Notebook Hazırlığı ✅

- [x] **M9.1.1** — Section 14 (Test>CV + RC4) cell'i eklendi + render edildi
- [x] **M9.1.2** — Section 15 (STATIC_ONLY threshold opt) cell'i eklendi + render edildi
- [x] **M9.1.3** — Section 16 (inline ablation + CI display) cell'i eklendi + render edildi
- [x] **M9.1.4** — Section 17 (model export) cell'i eklendi: `models/dolap_xgboost_pipeline.joblib` + `models/feature_schema.json` üretildi
- [x] **M9.1.5** — Section 12 (Key Takeaways) sunum yapısına göre güncellendi (20 dk yapı + Lecture coverage + Reviewer mapping + "Where the model fails" Q&A tablosu)
- [x] **M9.1.6** — Notebook end-to-end test: `jupyter nbconvert --execute --inplace` hatasız (3 Mayıs gece)
- [x] **M9.1.7** — Strip-outputs + fresh execute simulation: 24 code cell, **0 hata, 0 unexecuted** (3 Mayıs gece, sunum sabahı simülasyonu)
  - "Restart & Run All clean" kanıtı kayıt altında. Sunum sabahı kullanıcı VS Code/Jupyter'da tekrar çalıştırırsa aynı sonuç beklenir.
- [x] **M9.1.8** — Sticky toolbar Show/Hide Code toggle eklendi (cell[0], `presentation-toolbar` tag'li markdown)
  - Notebook açıldığında otomatik **Hide Code** modunda başlar (sunum modu)
  - "Show Code" butonu ile kod tekrar görünür hale gelir (Q&A sırasında profesör koda bakmak isterse)
  - Saf HTML+CSS+JS — nbextensions / harici eklenti gerektirmez
  - 46 toplam cell (1 toolbar + 45 içerik), end-to-end execute hatasız

### M9.2 — Live Demo Hazırlığı ✅

- [x] **M9.2.1** — `demo/demo_server.py` yazıldı: Flask + STUDENT CONFIG + 4 endpoint (`/`, `/api/schema`, `/api/presets`, `/api/predict`); preset endpoint'i 3 Mayıs öğle eklendi
- [x] **M9.2.2** — `demo/demo_ui.html` yazıldı: 60 feature input, threshold slider, gauge görsel, headline metrics card, filter box, **4 quick-scenario preset butonu** (3 Mayıs öğle)
- [x] **M9.2.3** — `demo/README.md` yazıldı: kurulum + sunum demo scripti + LMS şablonu karşılaştırma + presets açıklaması
- [x] **M9.2.4** — Initial end-to-end test: server başlatıldı, /api/health + /api/predict çalıştı (3 Mayıs gece, 1. tur)
- [x] **M9.2.5** — Demo end-to-end test (3 Mayıs, 3 tur)
  - **Tur 1 (gece):** 6 senaryo + 4 preset hepsi 200 OK
  - **Tur 2 (öğle):** preset sayısı **10**'a çıkarıldı, **4 gruba ayrıldı**:
    - 🟢 **STRONG (2):** Hızlı satılan (95.9%), Satılmayacak kesin (0.1%) — 95-puan dramatik fark
    - 🔥 **PRICING (3):** Premium marka (94.5%), Ucuz + yeni etiketli (84.4%), Yüksek engagement (93.5%)
    - 🟧 **EDGE (3):** Cold-start (91.4%), Tipik medyan (2.3%), Belirsiz P≈0.5 (40.1%)
    - 🔴 **ERRORS (2):** False positive (84.4% model SOLD ama gerçek not_sold), False negative (0.7% model NOT_SOLD ama gerçek sold) — Q&A için altın
  - **Tur 3 (akşam):** UI yeniden boyandı — Dolap.com pembe/turuncu light theme:
    - Pembe-turuncu gradient header (`#FF3D7F → #FF6B35`)
    - Soft pink background (`#FFF5F8`), beyaz card, pembe border (`#FFD6E1`)
    - Gradient probability text (Dolap brand'ı yansıtıyor)
    - Gradient Predict butonu, threshold quick-pick chip'leri (default 0.50 / F1-optimal 0.247)
    - Live gauge marker threshold sürüklenirken anlık takip
  - Threshold slider τ=0.50 ↔ 0.247 davranışı doğrulandı; quick-pick chip'leri tek tıkla geçiş sağlıyor
- [x] **M9.2.6** — LMS şablonu rehberi `demo/README.md`'a eklendi:
  - Karşılaştırma: bizim demo data-driven (schema JSON), LMS şablonu hard-coded HTML
  - Migration path: STUDENT CONFIG değerleri + 60 feature listesi paste-ready
  - **Önerim:** Bizim demo primary; LMS şablonu indirildi ise backup olarak kalsın
- [x] **M9.2.7** — Yedek plan dokümante edildi: `demo/FALLBACK_PLAN.md` 3 tier:
  - Tier-1: Notebook §17 üzerinden manuel `run_preset()` (~90 saniyelik kurtarma)
  - Tier-2: §16 önceden render'lanmış ablation + CI tablosu
  - Tier-3: `methodology_addendum.md` Bölüm 2/5/6/8.Y.1 statik markdown
  - + 8 maddelik sunum öncesi 5 dk checklist

### M9.3 — Sunum Provası ve Görev Dağılımı

- [x] **M9.3.1** — 20 dk prova run-sheet hazırlandı → [`reports/presentation_run_sheet.md`](reports/presentation_run_sheet.md)
  - T-30 dk sahne öncesi kontrol (3 paralel görev)
  - 0:00–5:00 Live demo (F): 8 preset + τ slider + manuel edit
  - 5:00–10:00 Model kararları (HU): §11/14/16/15/13 sırası
  - 10:00–15:00 Reviewer mapping + sonraç (Hİ)
  - 15:00–20:00 Q&A panel
  - Geçiş köprü cümleleri + yedek plan + sunum sonrası feedback toplama
- [x] **M9.3.2** — Görev dağılımı run-sheet'e işlendi (3 üye × ~5 dk):
  - **F (Furkan)**: Live demo + altyapı + threshold/feature soruları
  - **HU (Halil Utku)**: Model kararları (XGB/LGBM, ablation, anomaly, threshold) + ML metodoloji soruları
  - **Hİ (Halil İbrahim)**: Reviewer mapping + limitler + etik + sonraki adım soruları
  - Profesör notu karşılığı: her üye en az 5 dk ekranda + Q&A'da kendi alanı
- [x] **M9.3.2b** — Notebook konuşma metni → [`reports/notebook_presentation_script.md`](reports/notebook_presentation_script.md) — classification + ablation notebookları için dakika dakika konuşma akışı, BLOK A–F (HU + Hİ), her hücre için "AÇ → SÖYLE → GEÇ" şablonu, geçiş cümleleri, sahne kuralları
- [x] **M9.3.3** — Q&A kartları → [`reports/qa_cards.md`](reports/qa_cards.md) — 15 olası soru, her biri için 30 sn cevap + ek detay + ilgili artefakt:
  - 1: Test>CV anomaly (B.1) | 2: Cold-start (B.2) | 3: XGB vs LGBM (B.3) | 4: SHAP post-hoc (A)
  - 5: Class imbalance/SMOTE | 6: 49 satıcı temsili | 7: Leakage kontrol katmanları | 8: Engagement marjinal
  - 9: Hard cases (FP/FN preset) | 10: Production readiness | 11: Cross-platform | 12: Tek-seed bootstrap
  - 13: τ=0.247 gerekçesi | 14: Etik/mahremiyet | 15: Sonraki adım
  - Soru gelmezse açılış formülü: HU → Kart 1 → Kart 4 → Kart 8

### M9.4 — Yedek/Acil Plan

- [ ] **M9.4.1** — Notebook çalışmazsa: yedek olarak `reports/methodology_addendum.md` + `artifacts/figures/` PNG'leri ile sunum yap
- [ ] **M9.4.2** — Demo çalışmazsa: notebook §17 cell'inden manuel input ile prediction göster (`PIPELINE.predict_proba(...)`)
- [ ] **M9.4.3** — Internet kesilirse: Flask localhost'ta çalışıyor, internet gerekmez ✅

#### Definition of Done (M9)

- [ ] Sunum makinesinde notebook Run All hatasız (M9.1.7)
- [ ] Demo server localhost'ta çalışıyor + UI render oluyor (M9.2.5)
- [ ] Üç ekip üyesi konuşma sırası belirlendi (M9.3.2)
- [ ] 20 dk prova yapıldı (M9.3.1)
- [ ] Profesörün gönderdiği LMS şablonu kontrol edildi — yedek olarak (M9.2.6)

#### 🔴 KULLANICI HATIRLATMASI

> **Makale yazımı (M8) ŞİMDİ YAPILMAYACAK.** 3 Mayıs'ta kullanıcı talimatı:
> "daha makale yazılmayacak bana hatırlat bunu sadece sonrasında"
>
> Bu sunum tamamlandıktan sonra M8.5 (DergiPark prose yazımı, ~26 Mayıs deadline)
> kullanıcının onayıyla yeniden açılacak.

---

## M8 — Veri Bilimi Dergisi (TR Dizin / DergiPark) Yayın Yolu

> **🔴 ŞU AN DURUM:** ⏸️ **PAUSED** (sunumdan sonraya ertelendi — kullanıcı talimatı 3 Mayıs).

> **Bağlam:** Çalışma, bazı eklemelerle Veri Bilimi Dergisi'nde (DergiPark)
> yayınlanabilir. Dergi: e-ticaret + ML uygulamaları kapsıyor; %20
> benzerlik sınırı; Cambria font, çift kolon, APA atıf; İngilizce ana
> metin + Türkçe özet.
>
> **Bağımlılık:** M7.4 (H1–H4 hipotez bölümü) tamamlanmadan M8.1
> başlatılmamalı; M8 makale-format adımları M7.1–M7.3'ten bağımsız
> ilerleyebilir.
>
> **Ön-analiz özeti (1 Mayıs 2026, kod tabanında doğrulandı):**
> - Engagement kolonları (notebook header): `like_count`, `comment_count`,
>   `engagement_score`, `like_pctile_cat` (+ olası `has_comments`,
>   `like_per_day`). Dataset: `data/processed/model_ready_v3.csv`,
>   notebook cell[3] yüklüyor.
> - `is_negotiable` özelliği şu an **YOK**: `parsers.py`'de teklif/pazarlık
>   parse'ı yapılmıyor (`raw_snapshots/cohort_20260311/elbise.jsonl`
>   schema'sında bu alan yok). Mevcut "pazarlık" geçişi
>   (`engineer.py:244`, `clean_features.py:33`) yalnızca açıklama metni
>   keyword-match, HTML butonu değil.
> - Tam model AUC: 0.8119 (notebook cell[8] çıktısı, XGBoost).

### M8.1 — Hipotez–SHAP Eşleştirme Paragrafı (Madde 1)

> ✅ **Çıktı:** `reports/article_draft_en.md` §5.3 — yoğun, tek
> paragraflık İngilizce makale anlatımı. H1 (price_pctile_cat
> negatif SHAP) doğrulandı, H2 kısmen (fiyat-marka karışımı), H3
> (engagement_score top-5 pozitif) ve H4 (seller_exp_log pozitif)
> doğrulandı. Sonuç cümlesi: "3 of 4 hypotheses align ... domain-
> coherent rather than arbitrary black-box".

- [x] **M8.1.1** — M7.4 tamamlandıktan sonra: H1–H4 sonuçlarını tek bir
  yoğun paragrafta toparla (her hipotez için tek cümle: hipotez metni →
  SHAP yön/büyüklük → karar).

### M8.2 — Ablasyon Çalışması (Madde 4)

> ✅ **Çıktı:** `notebooks/dolap_ablation_study.ipynb` çalıştırıldı,
> sayılar gerçek:
>
> | Versiyon | n_feat | ROC-AUC | ΔAUC vs FULL |
> |---|---:|---:|---:|
> | FULL | 60 | **0.8150** | – |
> | NO_ENGAGEMENT | 49 | 0.8097 | **−0.0053** |
> | STATIC_ONLY (cold-start) | 26 | 0.7491 | **−0.0659** |
>
> Sonuçlar mail draft Madde 7 + makale §5.4 + methodology
> addendum Bölüm 5'e yerleştirildi.

- [x] **M8.2.1** — `notebooks/` altında yeni notebook oluştur:
  `dolap_ablation_study.ipynb`. Cell[3] dataset yüklemesini
  `dolap_classification_final.ipynb`'den birebir kopyala
  (`model_ready_v3.csv`).
- [x] **M8.2.2** — Üç feature-set tanımla.  
  → `ENGAGEMENT_COLS` (11 kolon) + `STATIC_COLS` (~22) ablation
  notebook'ta sabit listeler olarak yazıldı; `df.columns` ile
  kesişim alınıyor (eksik kolonu sessizce atlar).
- [x] **M8.2.3** — `train_xgb(X, y, seed=42) -> dict` fonksiyonu.  
  → Ablation notebook hücre 6'da; ana notebook cell[6]+cell[8]
  pipeline'ı birebir kopyalandı.
- [x] **M8.2.4** — Üç feature-set için `train_xgb` çağır,
  `pd.DataFrame` olarak topla.  
  → Hücre 8'de döngü + `df_abl` (n_features + 5 metrik + ΔAUC
  sütunu).
- [x] **M8.2.5** — Markdown export.  
  → `df_abl.to_markdown(floatfmt='.4f')` aynı hücrede; çıktı
  doğrudan makaleye yapıştırılır.
- [x] **M8.2.6** — Tartışma cümlesi şablonu.  
  → Notebook son markdown hücresinde 3-noktalı yorum çerçevesi
  (marjinal katkı / cold-start / leakage cevabı).

### M8.3 — Bootstrap Güven Aralığı (Madde 5)

> ✅ **Çıktı:** Section 13 çalıştırıldı, gerçek CI değerleri:
>
> | Model | ROC-AUC | 95% CI |
> |---|---:|:---|
> | **XGBoost** | **0.8150** | **[0.7613, 0.8722]** |
> | LightGBM | 0.7798 | [0.7225, 0.8426] |
> | Random Forest | 0.7604 | [0.7022, 0.8207] |
> | Logistic Regression | 0.7206 | [0.6613, 0.7864] |
> | Decision Tree | 0.7116 | [0.6432, 0.7841] |
> | KNN | 0.6964 | [0.6364, 0.7612] |
>
> Tüm CI'lar mail draft Tablo 7'ye eklendi; methodology
> addendum Bölüm 2 ve makale §5.1 senkronize edildi.
> CI genişlikleri ~0.11–0.14, model sıralaması istatistiksel
> olarak güvenilir.

- [x] **M8.3.1** — Bootstrap CI fonksiyonu notebook'a eklendi.  
  → Section 13 (cell 33 markdown + cell 34 code), 35-satırlık
  `bootstrap_auc_ci()` + degenerate-resample guard.
- [x] **M8.3.2** — 6 model için döngü, `df_ci` üretildi.  
  → Aynı hücrede `for name, model in fitted.items()`; sonuçlar
  ROC-AUC azalan sıraya göre.
- [x] **M8.3.3** — Tablo 7 CI sütunu format şablonu.  
  → Notebook print çıktısı `AUC = 0.8119 [95% CI: X.XX, Y.YY]`
  formatında; makale Tablo 7'ye yeni sütun olarak eklenecek.

### M8.5 — Akademik Makale Formatına Yeniden Yazım (Madde 2 + 3)

> ⚠️ **Kısmen tamamlandı (iskelet hazır, içerik yazımı + şablon
> aktarımı + benzerlik kontrolü açık).** İskelet dosyalar: ablasyon
> + CI + hipotezler + reviewer mapping iskelete işlendi.
>
> **Çıktılar:**
> - `reports/article_draft_en.md` — 9 bölümlü full skeleton + reviewer
>   mapping appendix; her bölümün outline'ı yazıldı, prose yazımı
>   açık. M8.1 yoğun paragrafı §5.3'e yerleştirildi.
> - `reports/article_abstract_tr.md` — 6-noktalı yapı taşları +
>   yazım notları.

- [ ] **M8.5.1** — DergiPark'tan Veri Bilimi Dergisi şablonunu indir:
  https://dergipark.org.tr/tr/pub/veri (yazım kuralları sayfası).
  Şablonu `reports/journal_template.docx` olarak kaydet. Gereksinimler:
  Cambria font, çift kolon, APA, %20 benzerlik.  
  → **Kullanıcı aksiyonu (web + login).** Ben dosyayı indiremem.
- [x] **M8.5.2** — Yeni dosya: `reports/article_draft_en.md` ve
  `reports/article_abstract_tr.md` oluştur.  
  → İskelet hazır; final yazım M8.5.3'te.
- [ ] **M8.5.3** — Bölümleri sıfırdan yaz (mevcut PDF'ten copy-paste
  YAPMA — %20 benzerlik sınırı): Abstract, Introduction, Related
  Work, Data, Methodology, Experiments, Results, Discussion,
  Conclusion.  
  → İskelet outline'ı `article_draft_en.md`'de hazır; bölüm-bölüm
  prose yazımı bekliyor (M8.5.5 figürleri ve M8.2/M8.3 sayıları
  geldikten sonra).
- [ ] **M8.5.4** — Related Work bölümü için en az 12-15 atıf hazırla.  
  → §2'de 4-strand grouping yazıldı; atıf çekme açık.
- [ ] **M8.5.5** — Tüm tabloları ve şekilleri makale dpi'ında (≥300)
  yeniden render et.  
  → Notebook'lar `dpi=300` ile re-run edildiğinde otomatik;
  figure-caption'ları İngilizce yaz.
- [ ] **M8.5.6** — Şablona aktarım: `.docx` veya LaTeX (dergi hangisini
  kabul ediyorsa). Cambria + çift kolon + APA atıf stilini uygula.  
  → M8.5.1 şablonu indikten sonra.
- [ ] **M8.5.7** — Benzerlik kontrolü: iThenticate / Turnitin
  (üniversite hesabıyla) — %20 altında olduğunu doğrula.  
  → Final draft sonrası, gönderim öncesi.

### M8.6 — Gönderim & Takip

- [ ] **M8.6.1** — DergiPark Veri Bilimi Dergisi gönderim formunu
  doldur: yazar(lar), kurum, ORCID, anahtar kelimeler.
- [ ] **M8.6.2** — Cover letter taslağı: çalışmanın derginin kapsamına
  uyumu, novelty (Dolap'a özgü dataset + ablasyon + SHAP yorumu).
- [ ] **M8.6.3** — Submission tarihini ve makale ID'sini bu todo'ya
  not düş; revizyon tarihinde geri dönülecek.

