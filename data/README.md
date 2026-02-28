# data/ — Veri Katmanları

Bu klasör **git-ignored** olarak saklanır. Yapıyı anlamak için bu doküman bırakılmıştır.

## Dizin Yapısı

```
data/
├── raw_snapshots/              # Phase 1: Ham scrape çıktıları
│   ├── cohort_20260301/        #   Her cohort = bir scrape batch'i
│   │   ├── listings.jsonl      #   İlan verileri (JSON Lines)
│   │   ├── sellers.jsonl       #   Satıcı profil verileri
│   │   └── meta.yaml           #   Cohort meta: tarih, adet, filtre
│   ├── cohort_20260308/
│   └── ...
│
├── labels/                     # Phase 2: 7-gün sonrası durum etiketleri
│   ├── cohort_20260301.jsonl   #   listing_id → sold_within_7_days (0/1)
│   └── ...
│
├── interim/                    # Phase 3: Birleştirme ara çıktıları
│   ├── merged_20260301.parquet #   raw + labels join
│   └── ...
│
└── processed/                  # Phase 4: Train-ready dataset
    ├── train.parquet
    ├── val.parquet
    ├── test.parquet
    └── feature_schema.yaml     #   Kolon adları, tipleri, açıklamaları
```

## Cohort Akışı

```
    Gün 0                    Gün 7                    Gün 7+
 ┌──────────┐          ┌──────────────┐         ┌────────────────┐
 │ SCRAPE   │          │ LABEL CHECK  │         │ MERGE & BUILD  │
 │          │  7 gün   │              │         │                │
 │ listings │ ──────►  │ sold? 0 / 1  │ ──────► │ interim/       │
 │ sellers  │  bekle   │              │         │ processed/     │
 └──────────┘          └──────────────┘         └────────────────┘
  raw_snapshots/         labels/                  interim/ + processed/
```

## Adlandırma Kuralı

- **Cohort ID** = scrape başlangıç tarihi: `YYYYMMDD`
- Ham dosyalar: `data/raw_snapshots/cohort_{id}/listings.jsonl`
- Etiketler: `data/labels/cohort_{id}.jsonl`
- Ara çıktılar: `data/interim/merged_{id}.parquet`
