# Dolap İkinci El Moda İlanı — Satış Tahmini

> Bir Dolap ilanının özelliklerine bakarak **7 gün içinde satılıp satılmayacağını** tahmin eden makine öğrenmesi projesi.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Proje Yapısı

```
dolap-sale-prediction/
├── configs/                # YAML konfigürasyon dosyaları
│   ├── scraping.yaml       #   Scraper parametreleri
│   ├── features.yaml       #   Feature engineering tanımları
│   ├── model.yaml          #   Model hiperparametreleri
│   └── pipeline.yaml       #   Pipeline orkestrasyon ayarları
├── data/
│   ├── raw_snapshots/      # Cohort bazlı ham scrape çıktıları (git-ignored)
│   │   └── cohort_YYYYMMDD/
│   ├── labels/             # 7-gün sonrası satış etiketleri (git-ignored)
│   ├── interim/            # Ara çıktılar – merge / join sonuçları (git-ignored)
│   └── processed/          # Final train-ready dataset (git-ignored)
├── artifacts/
│   ├── models/             # Eğitilmiş model dosyaları (git-ignored)
│   ├── figures/            # Üretilen grafikler (git-ignored)
│   └── metrics/            # JSON/CSV metrik dökümantları (git-ignored)
├── docs/                   # Proje dokümanları
├── notebooks/              # Jupyter notebook'ları (EDA, modelleme)
├── reports/                # Final raporlar (git-ignored)
├── src/
│   ├── scraping/           # Dolap.com web scraper modülleri
│   ├── labeling/           # 7-gün satış durumu etiketleyici
│   ├── dataset/            # Veri seti oluşturma & yönetimi
│   ├── preprocessing/      # Veri temizleme pipeline'ları
│   ├── features/           # Feature engineering
│   ├── models/             # Model tanımları & eğitim mantığı
│   ├── evaluation/         # Değerlendirme metrikleri & raporlama
│   ├── pipelines/          # Uçtan uca pipeline entrypoint'leri
│   └── utils/              # Ortak araçlar (config, logging, DB)
└── tests/                  # Birim & entegrasyon testleri
```

## Branch Stratejisi

| Branch | Amaç |
|---|---|
| `main` | Kararlı, yayınlanabilir sürüm |
| `develop` | Aktif geliştirme entegrasyon dalı |
| `feature/*` | Her özellik için ayrı dal (`feature/scraper`, `feature/eda` …) |

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Ortam değişkenlerini düzenle
```

## Lisans

MIT
