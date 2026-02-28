# End-to-end pipeline orchestration
#
# Entrypoints:
#   python -m src.pipelines.scrape          → Crawl & scrape listings
#   python -m src.pipelines.label           → 7-day sold-status re-check
#   python -m src.pipelines.build_dataset   → Merge, clean, feature-eng, split
#   python -m src.pipelines.train           → Train classification models
#   python -m src.pipelines.evaluate        → Evaluate on test set + SHAP
