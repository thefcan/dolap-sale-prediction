"""
Web scraping modules for dolap.com.

Public API
----------
DolapScraper        — Selenium-powered scraper with Cloudflare bypass
load_scraping_config — Load scraping.yaml configuration
parse_product_detail — Parse raw HTML into structured dict
parse_listing_urls_from_page — Extract listing URLs from category HTML
extract_listing_id_from_url  — Pull numeric listing ID from URL slug
RateLimiter          — Adaptive delay management with back-pressure
BanDetector          — Consecutive failure tracking and ban alerting
BanDetectedError     — Exception raised when ban threshold is reached
SessionManager       — Cookie persistence and rotation
SnapshotWriter       — Append-only JSONL snapshot storage with dedup
CohortStateTracker   — SQLite-backed cohort lifecycle tracking
"""

from src.scraping.parsers import (
    extract_listing_id_from_url,
    parse_listing_urls_from_page,
    parse_product_detail,
)
from src.scraping.rate_limiter import (
    BanDetectedError,
    BanDetector,
    RateLimiter,
    SessionManager,
)
from src.scraping.scraper import DolapScraper, load_scraping_config
from src.scraping.storage import CohortStateTracker, SnapshotWriter

__all__ = [
    "DolapScraper",
    "load_scraping_config",
    "parse_product_detail",
    "parse_listing_urls_from_page",
    "extract_listing_id_from_url",
    "RateLimiter",
    "BanDetector",
    "BanDetectedError",
    "SessionManager",
    "SnapshotWriter",
    "CohortStateTracker",
]
