"""
Web scraping modules for dolap.com.

Public API
----------
DolapScraper        — Selenium-powered scraper with Cloudflare bypass
load_scraping_config — Load scraping.yaml configuration
parse_product_detail — Parse raw HTML into structured dict
parse_listing_urls_from_page — Extract listing URLs from category HTML
extract_listing_id_from_url  — Pull numeric listing ID from URL slug
"""

from src.scraping.parsers import (
    extract_listing_id_from_url,
    parse_listing_urls_from_page,
    parse_product_detail,
)
from src.scraping.scraper import DolapScraper, load_scraping_config

__all__ = [
    "DolapScraper",
    "load_scraping_config",
    "parse_product_detail",
    "parse_listing_urls_from_page",
    "extract_listing_id_from_url",
]
