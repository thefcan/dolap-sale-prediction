"""
Selenium-based scraper for Dolap.com.

Dolap.com sits behind Cloudflare WAF which blocks plain HTTP clients
(``requests``, ``curl``, ``httpx``).  We therefore drive a real browser
via Selenium so that Cloudflare challenges are handled automatically.

Architecture
------------
``DolapScraper`` manages the full lifecycle:

1. **init** — spin up headless Chrome via ``selenium.webdriver``
2. **crawl_category** — navigate to a category page, scroll / paginate,
   collect product URLs
3. **scrape_listing** — navigate to a product detail page, wait for
   render, return parsed dict
4. **close** — tear down the browser

Rate limiting, random delays and retry logic are built in.

Usage::

    from src.scraping.scraper import DolapScraper

    with DolapScraper() as scraper:
        urls = scraper.crawl_category("kazak", max_pages=3)
        for url in urls:
            data = scraper.scrape_listing(url)
            print(data)
"""

from __future__ import annotations

import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)

from src.scraping.parsers import (
    extract_listing_id_from_url,
    parse_listing_urls_from_page,
    parse_product_detail,
)
from src.utils.logger import get_logger


# ── Constants ───────────────────────────────────────────────────────────────

_BASE_URL = "https://dolap.com"
_DEFAULT_CONFIG = "configs/scraping.yaml"

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]


# ── Config loader ───────────────────────────────────────────────────────────


def load_scraping_config(path: str | Path = _DEFAULT_CONFIG) -> dict:
    """Load and return the scraping section of the YAML config."""
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    return cfg.get("scraping", cfg)


# ── Main scraper class ──────────────────────────────────────────────────────


class DolapScraper:
    """Selenium-powered Dolap.com scraper with anti-ban protections.

    Parameters
    ----------
    config_path : str | Path
        Path to ``scraping.yaml``.
    headless : bool
        Run Chrome without a visible window.
    """

    # -- lifecycle --------------------------------------------------------

    def __init__(
        self,
        config_path: str | Path = _DEFAULT_CONFIG,
        headless: bool = True,
    ) -> None:
        self.cfg = load_scraping_config(config_path)
        self.headless = headless
        self.logger = get_logger("scraper")
        self.driver: webdriver.Chrome | None = None

        # Rate limiting params
        self._delay_min: float = self.cfg.get("delay", {}).get("min_seconds", 1.5)
        self._delay_max: float = self.cfg.get("delay", {}).get("max_seconds", 3.5)
        self._max_retries: int = self.cfg.get("max_retries", 3)
        self._backoff_factor: float = self.cfg.get("retry_backoff_factor", 2.0)
        self._timeout: int = self.cfg.get("timeout_seconds", 30)

        # Stats
        self._stats: dict[str, int] = {
            "pages_loaded": 0,
            "listings_scraped": 0,
            "errors": 0,
        }

    def __enter__(self) -> "DolapScraper":
        self.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def start(self) -> None:
        """Initialise the Selenium Chrome WebDriver."""
        if self.driver is not None:
            return

        self.logger.info("Starting Selenium Chrome WebDriver", headless=self.headless)
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument(f"--window-size=1920,1080")

        # Random User-Agent
        ua = random.choice(_USER_AGENTS)
        options.add_argument(f"--user-agent={ua}")

        # Suppress automation flags
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)

        # Remove webdriver flag from navigator
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )

        self.driver.set_page_load_timeout(self._timeout)
        self.logger.info("WebDriver initialised", user_agent=ua[:60] + "…")

    def close(self) -> None:
        """Shut down the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("WebDriver closed", stats=self._stats)

    # -- rate limiting ----------------------------------------------------

    def _sleep(self) -> None:
        """Random sleep between requests."""
        delay = random.uniform(self._delay_min, self._delay_max)
        time.sleep(delay)

    def _navigate(self, url: str, *, retries: int | None = None) -> str:
        """Navigate to *url* with retry logic.  Returns page source HTML."""
        assert self.driver is not None, "Call .start() first"
        max_tries = retries or self._max_retries
        full_url = url if url.startswith("http") else f"{_BASE_URL}{url}"

        for attempt in range(1, max_tries + 1):
            try:
                self.driver.get(full_url)
                # Wait for body to be present (Cloudflare may take a moment)
                WebDriverWait(self.driver, self._timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                self._stats["pages_loaded"] += 1

                # Check for Cloudflare challenge page
                page_source = self.driver.page_source
                if "Attention Required" in page_source or "cf-error" in page_source:
                    self.logger.warning(
                        "Cloudflare challenge detected, waiting…",
                        url=full_url,
                        attempt=attempt,
                    )
                    time.sleep(5 + attempt * 2)  # extra wait for CF
                    page_source = self.driver.page_source
                    if "Attention Required" in page_source:
                        raise WebDriverException("Cloudflare block persists")

                return page_source

            except (TimeoutException, WebDriverException) as exc:
                self.logger.warning(
                    "Navigation failed",
                    url=full_url,
                    attempt=attempt,
                    error=str(exc)[:120],
                )
                if attempt < max_tries:
                    backoff = self._backoff_factor ** attempt
                    time.sleep(backoff)
                else:
                    self._stats["errors"] += 1
                    raise

        raise RuntimeError("Unreachable")  # pragma: no cover

    # -- category crawling ------------------------------------------------

    def crawl_category(
        self,
        category_slug: str,
        max_pages: int | None = None,
    ) -> list[str]:
        """Crawl a category and return a list of product URLs.

        Dolap.com category pages are SPA-rendered.  We scroll/wait for
        product cards to appear, then extract ``/urun/…`` links.

        Parameters
        ----------
        category_slug : str
            E.g. ``"kazak"``, ``"elbise"``, ``"mont"``.
        max_pages : int, optional
            Override ``max_pages_per_category`` from config.

        Returns
        -------
        list[str]
            Deduplicated product detail URLs (relative paths).
        """
        limit = max_pages or self.cfg.get("max_pages_per_category", 50)
        all_urls: list[str] = []
        seen: set[str] = set()

        self.logger.info(
            "Crawling category",
            category=category_slug,
            max_pages=limit,
        )

        for page_num in range(1, limit + 1):
            url = f"{_BASE_URL}/{category_slug}?sayfa={page_num}"
            self.logger.debug("Loading category page", url=url, page=page_num)

            try:
                html = self._navigate(url)
            except (TimeoutException, WebDriverException):
                self.logger.error("Failed to load category page, stopping", page=page_num)
                break

            # Wait for product cards to render (JS)
            self._wait_for_products()

            # Re-fetch page source after JS rendering
            html = self.driver.page_source

            # Extract product URLs
            urls = parse_listing_urls_from_page(html)

            new_urls = [u for u in urls if u not in seen]
            if not new_urls:
                self.logger.info(
                    "No new listings found, stopping pagination",
                    page=page_num,
                    total=len(all_urls),
                )
                break

            for u in new_urls:
                seen.add(u)
                all_urls.append(u)

            self.logger.info(
                "Category page scraped",
                page=page_num,
                new_urls=len(new_urls),
                total=len(all_urls),
            )
            self._sleep()

        self.logger.info(
            "Category crawl complete",
            category=category_slug,
            total_urls=len(all_urls),
        )
        return all_urls

    def _wait_for_products(self, timeout: int = 10) -> None:
        """Wait for product cards to appear in the DOM after JS render."""
        assert self.driver is not None
        try:
            # Product cards contain links to /urun/...
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, 'a[href*="/urun/"]')) > 0
            )
        except TimeoutException:
            # Products may not have loaded (empty page or end of results)
            self.logger.debug("No product links found within timeout")

        # Extra scroll to trigger lazy-loading
        try:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(1.5)
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight / 2);"
            )
            time.sleep(1.0)
        except WebDriverException:
            pass

    # -- listing scraping -------------------------------------------------

    def scrape_listing(self, url: str) -> dict[str, Any]:
        """Scrape a single product detail page.

        Parameters
        ----------
        url : str
            Relative or absolute URL of the product (``/urun/…``).

        Returns
        -------
        dict
            Parsed listing data.  See ``parsers.parse_product_detail``.
        """
        self.logger.debug("Scraping listing", url=url)
        self._sleep()

        try:
            html = self._navigate(url)
        except (TimeoutException, WebDriverException) as exc:
            self.logger.error("Failed to load listing", url=url, error=str(exc)[:120])
            return {
                "url": url,
                "listing_id": extract_listing_id_from_url(url),
                "_parse_errors": [f"Navigation failed: {exc}"],
            }

        # Wait for price or brand text to appear (product content loaded)
        self._wait_for_product_detail()

        # Re-fetch HTML after full render
        html = self.driver.page_source

        data = parse_product_detail(html, url)
        data["scraped_at"] = datetime.utcnow().isoformat()
        self._stats["listings_scraped"] += 1

        if data.get("_parse_errors"):
            self.logger.warning(
                "Parse issues",
                url=url,
                errors=data["_parse_errors"],
            )

        return data

    def _wait_for_product_detail(self, timeout: int = 10) -> None:
        """Wait for product detail content to render."""
        assert self.driver is not None
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: "TL" in d.page_source and "Beğeni" in d.page_source
            )
        except TimeoutException:
            self.logger.debug("Product detail content may not have loaded fully")

    # -- batch operations -------------------------------------------------

    def scrape_listings_batch(
        self,
        urls: list[str],
        output_path: str | Path | None = None,
    ) -> list[dict[str, Any]]:
        """Scrape multiple listings and optionally save as JSONL.

        Parameters
        ----------
        urls : list[str]
            Product detail URLs.
        output_path : str | Path, optional
            If provided, results are appended line-by-line to this JSONL file.

        Returns
        -------
        list[dict]
            All scraped listing dicts.
        """
        results: list[dict[str, Any]] = []
        total = len(urls)

        if output_path:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
        else:
            out = None

        self.logger.info("Starting batch scrape", total=total)

        for idx, url in enumerate(urls, 1):
            self.logger.info(f"[{idx}/{total}] Scraping", url=url[:80])
            data = self.scrape_listing(url)
            results.append(data)

            # Stream to JSONL
            if out:
                with open(out, "a", encoding="utf-8") as fh:
                    # Remove _parse_errors from persisted data (keep it clean)
                    record = {k: v for k, v in data.items() if k != "_parse_errors"}
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")

            # Progress log every 10 listings
            if idx % 10 == 0:
                self.logger.info(
                    "Batch progress",
                    done=idx,
                    total=total,
                    errors=self._stats["errors"],
                )

        self.logger.info(
            "Batch scrape complete",
            total=total,
            scraped=len(results),
            errors=self._stats["errors"],
        )
        return results

    # -- full category pipeline -------------------------------------------

    def scrape_category(
        self,
        category_slug: str,
        max_pages: int | None = None,
        output_path: str | Path | None = None,
    ) -> list[dict[str, Any]]:
        """End-to-end: crawl category → scrape all listings → save.

        Convenience method combining ``crawl_category`` +
        ``scrape_listings_batch``.
        """
        urls = self.crawl_category(category_slug, max_pages=max_pages)
        if not urls:
            self.logger.warning("No URLs found for category", category=category_slug)
            return []
        return self.scrape_listings_batch(urls, output_path=output_path)

    @property
    def stats(self) -> dict[str, int]:
        """Return scraping statistics."""
        return dict(self._stats)
