# Dolap İkinci El Moda İlanı — Satış Tahmini

> Bir Dolap ilanının özelliklerine bakarak **7 gün içinde satılıp satılmayacağını** tahmin eden makine öğrenmesi projesi.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Proje Yapısı

```
dolap-sale-prediction/
├── configs/              # YAML / JSON konfigürasyon dosyaları
├── data/
│   ├── raw_snapshots/    # Ham scrape çıktıları (git-ignored)
│   ├── labels/           # 7-gün sonrası durum etiketleri (git-ignored)
│   └── processed/        # Temizlenmiş & feature-engineered veri (git-ignored)
├── docs/                 # Proje dokümanları & raporlar
├── models/               # Eğitilmiş model artifact'leri (git-ignored)
├── notebooks/            # Jupyter notebook'ları (EDA, modelleme)
├── reports/              # Üretilen figürler, metrikler (git-ignored)
├── src/
│   ├── scraping/         # Dolap.com web scraper modülleri
│   ├── labeling/         # 7-gün satış durumu etiketleyici
│   ├── dataset/          # Veri seti oluşturma & yönetimi
│   ├── preprocessing/    # Veri temizleme pipeline'ları
│   ├── features/         # Feature engineering
│   ├── models/           # Model tanımları & eğitim mantığı
│   ├── evaluation/       # Değerlendirme metrikleri
│   ├── pipelines/        # Uçtan uca pipeline orkestrasyon
│   └── utils/            # Ortak araçlar (config, logging, DB)
└── tests/                # Birim & entegrasyon testleri
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
