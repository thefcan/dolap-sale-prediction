"""
Status checker for Dolap.com listings — 7-day sold detection.

Re-visits a previously scraped listing URL and determines its current
status:

- **sold**       — "Satıldı" badge detected on the page
- **active**     — listing is still live (no sold indicator)
- **removed**    — HTTP 404/410 or "Sayfa bulunamadı" (item removed, not sold)
- **error**      — navigation / parse failure (transient issue)

Usage::

    from src.labeling.status_checker import StatusChecker

    with StatusChecker() as checker:
        result = checker.check(url)
        # {'listing_id': '442885461', 'url': '...', 'status': 'sold',
        #  'sold_within_7_days': 1, 'checked_at': '2026-03-17T...'}
"""

from __future__ import annotations

import time
import random
from datetime import datetime
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)

from src.scraping.parsers import extract_listing_id_from_url
from src.scraping.rate_limiter import (
    BanDetectedError,
    BanDetector,
    RateLimiter,
    build_proxy_options,
)
from src.scraping.scraper import _USER_AGENTS, load_scraping_config
from src.utils.logger import get_logger

# ── Constants ───────────────────────────────────────────────────────────────

_BASE_URL = "https://dolap.com"
_DEFAULT_CONFIG = "configs/scraping.yaml"

# Indicators that the listing was sold
_SOLD_INDICATORS = [
    "Satıldı",
    "Bu ürün satılmıştır",
    "SATILDI",
]

# Indicators that the page doesn't exist anymore
_REMOVED_INDICATORS = [
    "Sayfa bulunamadı",
    "Page not found",
    "Bu sayfa mevcut değil",
    "İlan kaldırılmıştır",
]


class StatusChecker:
    """Re-visit Dolap.com listing URLs and detect sold/active/removed status.

    Uses the same Selenium + anti-ban infrastructure as the scraper, but
    with a lighter page-load strategy (we only need to check for badges,
    not parse full product details).

    Parameters
    ----------
    config_path : str
        Path to ``scraping.yaml``.
    headless : bool
        Run Chrome without a visible window.
    """

    def __init__(
        self,
        config_path: str = _DEFAULT_CONFIG,
        headless: bool = True,
    ) -> None:
        self.cfg = load_scraping_config(config_path)
        self.headless = headless
        self.logger = get_logger("status_checker")
        self.driver: webdriver.Chrome | None = None

        # Rate limiting
        delay_cfg = self.cfg.get("delay", {})
        ban_cfg = self.cfg.get("ban_detection", {})

        self._rate_limiter = RateLimiter(
            base_min=delay_cfg.get("min_seconds", 1.5),
            base_max=delay_cfg.get("max_seconds", 3.5),
            escalation_factor=self.cfg.get("retry_backoff_factor", 2.0),
            max_delay=ban_cfg.get("max_delay", 60.0),
            recovery_requests=ban_cfg.get("recovery_requests", 5),
        )
        self._ban_detector = BanDetector(
            max_consecutive_failures=ban_cfg.get("max_consecutive_failures", 5),
            cooldown_seconds=ban_cfg.get("cooldown_seconds", 30.0),
            warning_threshold=ban_cfg.get("warning_threshold", 3),
        )

        self._max_retries: int = self.cfg.get("max_retries", 3)
        self._backoff_factor: float = self.cfg.get("retry_backoff_factor", 2.0)
        self._timeout: int = self.cfg.get("timeout_seconds", 30)
        self._proxy_cfg: dict = self.cfg.get("proxy", {})

        # Stats
        self._stats: dict[str, int] = {
            "checked": 0,
            "sold": 0,
            "active": 0,
            "removed": 0,
            "error": 0,
        }

    # ── Lifecycle ───────────────────────────────────────────────────────

    def __enter__(self) -> "StatusChecker":
        self.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def start(self) -> None:
        """Initialize the Selenium Chrome WebDriver."""
        if self.driver is not None:
            return

        self.logger.info("Starting StatusChecker WebDriver", headless=self.headless)
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")

        ua = random.choice(_USER_AGENTS)
        options.add_argument(f"--user-agent={ua}")

        # Proxy
        proxy_args = build_proxy_options(self._proxy_cfg)
        for arg, val in proxy_args.items():
            options.add_argument(f"{arg}={val}")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
        )
        self.driver.set_page_load_timeout(self._timeout)
        self.logger.info("StatusChecker WebDriver ready")

    def close(self) -> None:
        """Shut down the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logger.info("StatusChecker closed", stats=self._stats)

    # ── Core: single URL check ──────────────────────────────────────────

    def check(self, url: str) -> dict[str, Any]:
        """Re-visit a listing URL and determine its current status.

        Parameters
        ----------
        url : str
            Full or relative URL of the listing.

        Returns
        -------
        dict
            Keys: listing_id, url, status, sold_within_7_days, checked_at,
                  page_title (for debugging).
        """
        assert self.driver is not None, "Call .start() first"

        listing_id = extract_listing_id_from_url(url) or ""
        full_url = url if url.startswith("http") else f"{_BASE_URL}{url}"
        result: dict[str, Any] = {
            "listing_id": listing_id,
            "url": full_url,
            "status": "error",
            "sold_within_7_days": None,
            "checked_at": datetime.utcnow().isoformat(),
            "page_title": None,
        }

        # Adaptive delay
        self._rate_limiter.wait()

        try:
            page_source = self._navigate_with_retry(full_url)
        except BanDetectedError:
            result["status"] = "error"
            result["error_detail"] = "ban_detected"
            self._stats["error"] += 1
            self._stats["checked"] += 1
            return result
        except (TimeoutException, WebDriverException) as exc:
            result["status"] = "error"
            result["error_detail"] = str(exc)[:200]
            self._stats["error"] += 1
            self._stats["checked"] += 1
            return result

        # Grab page title for debugging
        try:
            result["page_title"] = self.driver.title
        except Exception:
            pass

        # Determine status from page content
        status = self._classify_page(page_source)
        result["status"] = status

        if status == "sold":
            result["sold_within_7_days"] = 1
            self._stats["sold"] += 1
        elif status == "active":
            result["sold_within_7_days"] = 0
            self._stats["active"] += 1
        elif status == "removed":
            # Removed but not sold — exclude from training or treat as not-sold
            result["sold_within_7_days"] = None  # ambiguous
            self._stats["removed"] += 1
        else:
            self._stats["error"] += 1

        self._stats["checked"] += 1
        return result

    def check_batch(self, urls: list[str]) -> list[dict[str, Any]]:
        """Check multiple listing URLs in sequence.

        Parameters
        ----------
        urls : list[str]
            List of listing URLs to re-check.

        Returns
        -------
        list[dict]
            One result dict per URL.
        """
        results: list[dict[str, Any]] = []
        total = len(urls)

        self.logger.info("Starting batch status check", total=total)

        for idx, url in enumerate(urls, 1):
            self.logger.info(f"[{idx}/{total}] Checking", url=url[:80])
            result = self.check(url)
            results.append(result)

            # Abort on ban
            if result.get("error_detail") == "ban_detected":
                self.logger.error(
                    "Ban detected — aborting batch",
                    checked=len(results),
                    remaining=total - idx,
                )
                break

            # Progress every 25 listings
            if idx % 25 == 0:
                self.logger.info(
                    "Batch progress",
                    done=idx,
                    total=total,
                    stats=dict(self._stats),
                )

        self.logger.info("Batch check complete", total=total, stats=self._stats)
        return results

    # ── Internal helpers ────────────────────────────────────────────────

    def _navigate_with_retry(self, url: str) -> str:
        """Navigate to URL with retry + ban detection. Returns page source."""
        assert self.driver is not None

        for attempt in range(1, self._max_retries + 1):
            try:
                self.driver.get(url)
                WebDriverWait(self.driver, self._timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                page_source = self.driver.page_source

                # Detect Cloudflare / rate-limit blocks
                http_status = self._detect_http_status(page_source)
                if http_status in (403, 429, 503):
                    self.logger.warning(
                        "Server block detected",
                        url=url[:80],
                        status=http_status,
                        attempt=attempt,
                    )
                    self._rate_limiter.adapt(status_code=http_status, success=False)
                    self._ban_detector.record_failure(http_status)

                    if attempt < self._max_retries:
                        backoff = self._backoff_factor ** attempt + random.uniform(2, 5)
                        time.sleep(backoff)
                        continue
                    raise WebDriverException(f"Server returned {http_status}")

                # Success
                self._rate_limiter.adapt(status_code=200, success=True)
                self._ban_detector.record_success()
                return page_source

            except BanDetectedError:
                raise
            except (TimeoutException, WebDriverException) as exc:
                self.logger.warning(
                    "Navigation failed", url=url[:80], attempt=attempt, error=str(exc)[:120]
                )
                if attempt < self._max_retries:
                    time.sleep(self._backoff_factor ** attempt)
                else:
                    raise

        raise RuntimeError("Unreachable")  # pragma: no cover

    def _detect_http_status(self, page_source: str) -> int | None:
        """Infer HTTP status from rendered page content."""
        if not page_source:
            return 503
        if "Attention Required" in page_source or "cf-error" in page_source:
            return 403
        if "Rate limited" in page_source or "Too many requests" in page_source:
            return 429
        if "503 Service" in page_source or "temporarily unavailable" in page_source:
            return 503
        return None

    def _classify_page(self, page_source: str) -> str:
        """Classify a listing page as sold / active / removed / error.

        Parameters
        ----------
        page_source : str
            Rendered HTML of the listing page.

        Returns
        -------
        str
            One of: ``'sold'``, ``'active'``, ``'removed'``, ``'error'``.
        """
        if not page_source:
            return "error"

        # Check for 404 / removed
        if any(indicator in page_source for indicator in _REMOVED_INDICATORS):
            return "removed"

        # Check for "Satıldı" badge
        if any(indicator in page_source for indicator in _SOLD_INDICATORS):
            return "sold"

        # Check for price (indicates active listing)
        if "TL" in page_source and ("Beğeni" in page_source or "Sepete Ekle" in page_source):
            return "active"

        # Fallback: if page has meaningful content, assume active
        if len(page_source) > 5000 and "dolap.com" in page_source.lower():
            return "active"

        return "error"

    @property
    def stats(self) -> dict[str, int]:
        """Return check statistics."""
        return dict(self._stats)
