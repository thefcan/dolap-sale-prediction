"""
Rate limiting, ban detection and session management for Dolap.com scraper.

Provides three cooperating components:

1. **RateLimiter** — adaptive delay management with token-bucket–style
   back-pressure.  Automatically increases delays when the server signals
   stress (429 / 503) and slowly recovers when things calm down.

2. **BanDetector** — tracks consecutive failures and raises
   ``BanDetectedError`` when the scraper should stop to avoid a
   permanent IP ban.

3. **SessionManager** — cookie persistence and rotation helpers so that
   the Selenium session survives across restarts and can be refreshed on
   demand.

Usage::

    from src.scraping.rate_limiter import RateLimiter, BanDetector

    rl = RateLimiter()
    bd = BanDetector()

    rl.wait()            # sleep before each request
    bd.record_success()  # after a successful page load
    bd.record_failure(403)  # after a blocked response
    rl.adapt(status_code=429)  # increase delays
"""

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.logger import get_logger


# ── Exceptions ──────────────────────────────────────────────────────────────


class BanDetectedError(Exception):
    """Raised when consecutive failures exceed the threshold."""


# ── Rate Limiter ────────────────────────────────────────────────────────────


@dataclass
class RateLimiter:
    """Adaptive rate limiter with automatic back-pressure.

    Starts with ``base_min`` / ``base_max`` delays.  When the server
    returns a throttling status code (429, 503) the current window is
    multiplied by ``escalation_factor``.  After ``recovery_requests``
    consecutive successes the window shrinks back toward the base.

    Parameters
    ----------
    base_min : float
        Minimum sleep seconds under normal conditions.
    base_max : float
        Maximum sleep seconds under normal conditions.
    escalation_factor : float
        Multiplier applied to the delay window on each throttle event.
    max_delay : float
        Hard upper bound for the delay (prevents runaway escalation).
    recovery_requests : int
        Number of consecutive successes before the delay window is
        decreased by one step.
    """

    base_min: float = 1.5
    base_max: float = 3.5
    escalation_factor: float = 2.0
    max_delay: float = 60.0
    recovery_requests: int = 5

    # ── internal state ───────────────────────────────────────────────────
    _current_min: float = field(init=False, default=0.0)
    _current_max: float = field(init=False, default=0.0)
    _consecutive_ok: int = field(init=False, default=0)
    _total_waits: int = field(init=False, default=0)
    _total_escalations: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self._current_min = self.base_min
        self._current_max = self.base_max
        self._logger = get_logger("rate_limiter")

    # ── public API ───────────────────────────────────────────────────────

    def wait(self) -> float:
        """Sleep for a random duration within the current window.

        Returns the actual number of seconds slept.
        """
        delay = random.uniform(self._current_min, self._current_max)
        time.sleep(delay)
        self._total_waits += 1
        return delay

    def adapt(self, *, status_code: int | None = None, success: bool = True) -> None:
        """Update the delay window based on the server's response.

        Call after every request.  ``success=False`` with a throttling
        status code will escalate; repeated successes will de-escalate.
        """
        if not success and status_code in (429, 403, 503):
            self._escalate(status_code)
        elif success:
            self._consecutive_ok += 1
            if self._consecutive_ok >= self.recovery_requests:
                self._deescalate()
                self._consecutive_ok = 0

    # ── private ──────────────────────────────────────────────────────────

    def _escalate(self, status_code: int | None) -> None:
        """Increase the delay window."""
        old_min, old_max = self._current_min, self._current_max
        self._current_min = min(self._current_min * self.escalation_factor, self.max_delay)
        self._current_max = min(self._current_max * self.escalation_factor, self.max_delay)
        self._consecutive_ok = 0
        self._total_escalations += 1
        self._logger.warning(
            "Rate limiter escalated",
            status_code=status_code,
            old_range=f"{old_min:.1f}-{old_max:.1f}s",
            new_range=f"{self._current_min:.1f}-{self._current_max:.1f}s",
            total_escalations=self._total_escalations,
        )

    def _deescalate(self) -> None:
        """Shrink the delay window back toward the base (one step)."""
        if self._current_min <= self.base_min:
            return
        self._current_min = max(self._current_min / self.escalation_factor, self.base_min)
        self._current_max = max(self._current_max / self.escalation_factor, self.base_max)
        self._logger.info(
            "Rate limiter de-escalated",
            new_range=f"{self._current_min:.1f}-{self._current_max:.1f}s",
        )

    @property
    def current_range(self) -> tuple[float, float]:
        """Current (min, max) delay window."""
        return (self._current_min, self._current_max)

    @property
    def stats(self) -> dict[str, Any]:
        """Return rate limiter statistics."""
        return {
            "total_waits": self._total_waits,
            "total_escalations": self._total_escalations,
            "current_min": round(self._current_min, 2),
            "current_max": round(self._current_max, 2),
        }


# ── Ban Detector ────────────────────────────────────────────────────────────


@dataclass
class BanDetector:
    """Detect potential IP bans from consecutive HTTP error patterns.

    Tracks consecutive failures (403 / 429 / 503) and raises
    ``BanDetectedError`` when the threshold is exceeded.

    Parameters
    ----------
    max_consecutive_failures : int
        Number of consecutive failures before declaring a ban.
    ban_status_codes : tuple[int, ...]
        HTTP status codes considered as ban/throttle indicators.
    cooldown_seconds : float
        Mandatory pause when approaching the failure threshold
        (at ``warning_threshold`` failures).
    warning_threshold : int
        Issue a warning and perform a cooldown at this many failures
        (must be < ``max_consecutive_failures``).
    """

    max_consecutive_failures: int = 5
    ban_status_codes: tuple[int, ...] = (403, 429, 503)
    cooldown_seconds: float = 30.0
    warning_threshold: int = 3

    # ── internal state ───────────────────────────────────────────────────
    _consecutive_failures: int = field(init=False, default=0)
    _total_failures: int = field(init=False, default=0)
    _total_successes: int = field(init=False, default=0)
    _last_failure_code: int | None = field(init=False, default=None)
    _last_failure_time: str | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._logger = get_logger("ban_detector")

    # ── public API ───────────────────────────────────────────────────────

    def record_success(self) -> None:
        """Record a successful request — resets the failure counter."""
        self._consecutive_failures = 0
        self._total_successes += 1

    def record_failure(self, status_code: int | None = None) -> None:
        """Record a failed request and check for ban conditions.

        Parameters
        ----------
        status_code : int | None
            The HTTP status code (or ``None`` for generic failures).

        Raises
        ------
        BanDetectedError
            If consecutive failures exceed ``max_consecutive_failures``.
        """
        self._consecutive_failures += 1
        self._total_failures += 1
        self._last_failure_code = status_code
        self._last_failure_time = datetime.utcnow().isoformat()

        self._logger.warning(
            "Request failure recorded",
            status_code=status_code,
            consecutive=self._consecutive_failures,
            max_allowed=self.max_consecutive_failures,
        )

        # Warning threshold — cooldown pause
        if self._consecutive_failures == self.warning_threshold:
            self._logger.warning(
                "Approaching ban threshold — entering cooldown",
                cooldown_seconds=self.cooldown_seconds,
                consecutive=self._consecutive_failures,
            )
            time.sleep(self.cooldown_seconds)

        # Ban threshold — abort
        if self._consecutive_failures >= self.max_consecutive_failures:
            msg = (
                f"Ban detected: {self._consecutive_failures} consecutive failures "
                f"(last status: {status_code}). Stopping scraper to protect IP."
            )
            self._logger.error(msg)
            raise BanDetectedError(msg)

    def is_healthy(self) -> bool:
        """Return ``True`` if no consecutive failures are accumulated."""
        return self._consecutive_failures == 0

    @property
    def stats(self) -> dict[str, Any]:
        """Return ban detector statistics."""
        return {
            "consecutive_failures": self._consecutive_failures,
            "total_failures": self._total_failures,
            "total_successes": self._total_successes,
            "last_failure_code": self._last_failure_code,
            "last_failure_time": self._last_failure_time,
            "is_healthy": self.is_healthy(),
        }


# ── Session Manager ─────────────────────────────────────────────────────────


class SessionManager:
    """Cookie persistence and rotation for Selenium sessions.

    Saves / loads browser cookies to a JSON file so that a session can
    survive across scraper restarts (e.g. when recovering from a ban
    cooldown).

    Parameters
    ----------
    cookie_file : str | Path
        Path to the JSON file where cookies are persisted.
    """

    def __init__(self, cookie_file: str | Path = "data/.cookies.json") -> None:
        self._cookie_file = Path(cookie_file)
        self._logger = get_logger("session_manager")

    def save_cookies(self, driver: Any) -> None:
        """Persist current browser cookies to disk."""
        if driver is None:
            return
        cookies = driver.get_cookies()
        self._cookie_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._cookie_file, "w", encoding="utf-8") as fh:
            json.dump(cookies, fh, ensure_ascii=False, indent=2)
        self._logger.info(
            "Cookies saved",
            count=len(cookies),
            path=str(self._cookie_file),
        )

    def load_cookies(self, driver: Any, domain: str = "dolap.com") -> int:
        """Load persisted cookies back into the browser.

        The driver should have already navigated to a page on the target
        domain before calling this method (Selenium requires domain
        match for cookie injection).

        Returns the number of cookies loaded.
        """
        if not self._cookie_file.exists():
            self._logger.debug("No cookie file found, skipping load")
            return 0

        with open(self._cookie_file, "r", encoding="utf-8") as fh:
            cookies = json.load(fh)

        loaded = 0
        for cookie in cookies:
            # Only inject cookies for the target domain
            cookie_domain = cookie.get("domain", "")
            if domain in cookie_domain:
                try:
                    driver.add_cookie(cookie)
                    loaded += 1
                except Exception:
                    pass  # skip incompatible cookies silently

        self._logger.info("Cookies loaded", loaded=loaded, total=len(cookies))
        return loaded

    def clear_cookies(self, driver: Any | None = None) -> None:
        """Delete persisted cookies and optionally clear browser cookies."""
        if self._cookie_file.exists():
            self._cookie_file.unlink()
            self._logger.info("Cookie file deleted")
        if driver is not None:
            try:
                driver.delete_all_cookies()
                self._logger.info("Browser cookies cleared")
            except Exception:
                pass

    @property
    def has_saved_cookies(self) -> bool:
        """Check whether a persisted cookie file exists."""
        return self._cookie_file.exists()


# ── Proxy Helper ────────────────────────────────────────────────────────────


def build_proxy_options(proxy_cfg: dict) -> dict[str, str]:
    """Convert proxy config section into Selenium Chrome arguments.

    Parameters
    ----------
    proxy_cfg : dict
        The ``proxy`` section from ``scraping.yaml``, e.g.::

            {"enabled": true, "url": "http://user:pass@host:port"}

    Returns
    -------
    dict
        Chrome argument(s) to inject, e.g.
        ``{"--proxy-server": "http://host:port"}``.
        Empty dict when proxy is disabled.
    """
    if not proxy_cfg.get("enabled", False):
        return {}

    url = proxy_cfg.get("url", "")
    if not url:
        return {}

    return {"--proxy-server": url}
