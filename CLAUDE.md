# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project goal

Binary classifier for **Dolap.com** (Turkish second-hand fashion marketplace) listings: given listing features at scrape time, predict whether the item will sell within **7 days** (`sold_within_7_days`, target defined in [configs/features.yaml](configs/features.yaml)).

## Pipeline architecture (cohort lifecycle)

The codebase is organised as a 5-stage pipeline. Each stage is a runnable module under [src/pipelines/](src/pipelines/) and has a corresponding YAML config under [configs/](configs/). State flows through **cohorts** — a cohort is one scrape batch identified by `YYYYMMDD`.

```
SCRAPE ─7-day wait─► LABEL ─► BUILD_DATASET ─► TRAIN ─► EVALUATE
   │                    │           │             │          │
   ▼                    ▼           ▼             ▼          ▼
data/raw_snapshots/  data/labels/  data/interim/  artifacts/  artifacts/
 cohort_YYYYMMDD/                   data/processed/ models/    figures+metrics/
```

| Stage | Entry | Reads | Writes |
|---|---|---|---|
| 1. Scrape | `python -m src.pipelines.scrape --cohort-id YYYYMMDD` | [configs/scraping.yaml](configs/scraping.yaml) (seed sellers per category) | `data/raw_snapshots/cohort_{id}/{category}.jsonl` + `meta.yaml` |
| 2. Label | `python -m src.pipelines.label --cohort-id YYYYMMDD` | listing URLs from cohort | `data/labels/cohort_{id}.jsonl` + summary.yaml |
| 3. Build | `python -m src.pipelines.build_dataset --all` | raw + labels | `data/interim/merged_data.parquet`, `data/interim/cleaned_all.parquet` |
| 4. Train | `python -m src.pipelines.train --model xgboost` | processed parquet + [configs/model.yaml](configs/model.yaml) | `artifacts/experiments/exp_{ts}/` (model, metrics, config snapshot) |
| 5. Evaluate | `python -m src.pipelines.evaluate --best` | model artifact + test parquet | `artifacts/figures/`, `artifacts/metrics/` |

Data layer documentation: [data/README.md](data/README.md). `data/` is **git-ignored** except for whitelisted cohorts (`cohort_20250712`, `cohort_20260308`).

## Critical architectural concepts

These are non-obvious patterns that span multiple files — read these before changing pipeline code.

- **Cohort state machine** ([src/scraping/storage.py](src/scraping/storage.py)): a SQLite `CohortStateTracker` (default `data/dolap_state.db`) records each cohort's lifecycle: `scraped → labeled → merged`. Pipelines update this state; do not bypass it when adding new cohorts.
- **Append-only crash-safe writes**: `SnapshotWriter` writes each listing immediately to per-category JSONL with dedup-by-`listing_id`. Never refactor it to batch-write — the scraper will hit Cloudflare bans and partial writes must survive.
- **Selenium is required**: Dolap sits behind Cloudflare WAF that blocks `requests`/`httpx`. All scraping (incl. the 7-day re-check in [src/labeling/status_checker.py](src/labeling/status_checker.py)) goes through headless Chrome via Selenium. Adaptive ban detection: see `ban_detection` block in [configs/scraping.yaml](configs/scraping.yaml).
- **Sold-status detection**: the label is determined by re-visiting the listing URL after 7 days and looking for the Turkish `"Satıldı"` badge. 404/410 → removed (excluded from train), still active → `0`, `"Satıldı"` → `1`.
- **Two cohort parser generations**: legacy cohort `20250712` has `brand="Brand - Size"` (concatenated) and `category=None`; new cohorts (`20260308`+) have clean fields. The cleaner ([src/preprocessing/cleaner.py](src/preprocessing/cleaner.py)) handles both — be aware when touching schema logic.
- **Experiment tracking** ([src/utils/experiment.py](src/utils/experiment.py)): every `train` run creates a timestamped `artifacts/experiments/exp_{ts}_{name}/` directory and snapshots the YAML configs ([src/utils/config_snapshot.py](src/utils/config_snapshot.py)), git hash, dataset SHA-256 hash ([src/utils/data_version.py](src/utils/data_version.py)), and global seed ([src/utils/seed.py](src/utils/seed.py)). Reproducibility depends on this — don't write training scripts that skip it.
- **Temporal split, never random** ([src/utils/split.py](src/utils/split.py)): train/val/test are sliced **chronologically** by `listed_at` to prevent leakage. Do not introduce `train_test_split(shuffle=True)` for the sale-prediction target.
- **YAML-driven config**: scraping seed sellers, brand tier mapping, condition ordinal map, model hyperparameters, and pipeline paths all live in [configs/](configs/). Code reads these at runtime — change YAML, not hard-coded constants.

## Common commands

```bash
# Setup (Python 3.10+ required)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Tests (pytest with coverage configured in pyproject.toml)
pytest                              # full suite
pytest tests/test_foo.py::test_bar  # single test
pytest -k "labeler"                 # by keyword

# Lint / format
ruff check src/ tests/
black src/ tests/

# Pipeline dry-runs (safe; no scraping)
python -m src.pipelines.scrape --dry-run
python -m src.pipelines.scrape --categories kazak --max-pages 2 --no-headless  # debug visible

# Auto-detect cohorts ready for 7-day re-check
python -m src.pipelines.label --auto

# Ad-hoc analysis scripts (one-offs, in scripts/)
python scripts/check_label_status.py
python scripts/label_all_data.py    # bulk re-label unlabeled rows in merged_data.csv
python scripts/validate_cohort.py
```

## Branch strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, releasable |
| `develop` | Active integration branch |
| `feature/*` | Per-feature work (`feature/scraper`, `feature/eda`, …) |

Project status and roadmap are tracked in detail in [todo.md](todo.md) (M0–M6 milestones, phase-level checklist).

## Notebooks

[notebooks/](notebooks/) contains exploratory work — `Dolap_EDA_Feature_Engineering.ipynb` (EDA + FE) and `dolap_classification_final.ipynb` (training/eval). The intent is for production logic to migrate into `src/pipelines/` over time; treat notebooks as the source of truth only when the corresponding pipeline module is incomplete.
