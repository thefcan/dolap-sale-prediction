"""Unit tests for :mod:`src.scraping.rate_limiter` (back-pressure + ban detection)."""

from __future__ import annotations

import pytest

import src.scraping.rate_limiter as rlmod
from src.scraping.rate_limiter import (
    BanDetectedError,
    BanDetector,
    RateLimiter,
    SessionManager,
    build_proxy_options,
)

# ── RateLimiter ──────────────────────────────────────────────────────────────


def test_ratelimiter_starts_at_base_window():
    rl = RateLimiter()
    assert rl.current_range == (1.5, 3.5)


def test_ratelimiter_escalates_on_throttle_status():
    rl = RateLimiter()
    rl.adapt(success=False, status_code=429)
    assert rl.current_range == (3.0, 7.0)
    assert rl.stats["total_escalations"] == 1


def test_ratelimiter_caps_at_max_delay():
    rl = RateLimiter(base_min=40.0, base_max=50.0, max_delay=60.0, escalation_factor=2.0)
    rl.adapt(success=False, status_code=503)
    assert rl.current_range == (60.0, 60.0)


def test_ratelimiter_deescalates_after_recovery():
    rl = RateLimiter(recovery_requests=5)
    rl.adapt(success=False, status_code=429)  # -> (3.0, 7.0)
    for _ in range(5):
        rl.adapt(success=True)
    assert rl.current_range == (1.5, 3.5)


def test_ratelimiter_ignores_non_throttle_failure():
    rl = RateLimiter()
    rl.adapt(success=False, status_code=404)
    assert rl.current_range == (1.5, 3.5)
    assert rl.stats["total_escalations"] == 0


def test_ratelimiter_wait_stays_within_window(monkeypatch):
    monkeypatch.setattr(rlmod.time, "sleep", lambda _seconds: None)
    rl = RateLimiter()
    slept = rl.wait()
    low, high = rl.current_range
    assert low <= slept <= high
    assert rl.stats["total_waits"] == 1


# ── BanDetector ──────────────────────────────────────────────────────────────


def test_bandetector_success_resets_failures():
    bd = BanDetector(cooldown_seconds=0.0)
    bd.record_failure(403)
    assert bd.is_healthy() is False
    bd.record_success()
    assert bd.is_healthy() is True
    assert bd.stats["total_successes"] == 1


def test_bandetector_raises_after_threshold():
    bd = BanDetector(max_consecutive_failures=3, warning_threshold=2, cooldown_seconds=0.0)
    bd.record_failure(429)
    bd.record_failure(429)  # hits warning threshold -> cooldown (0s here)
    with pytest.raises(BanDetectedError):
        bd.record_failure(429)  # third consecutive failure -> ban


def test_bandetector_cooldown_triggered_at_warning(monkeypatch):
    calls = []
    monkeypatch.setattr(rlmod.time, "sleep", lambda seconds: calls.append(seconds))
    bd = BanDetector(max_consecutive_failures=5, warning_threshold=2, cooldown_seconds=3.0)
    bd.record_failure(403)  # 1 -> no cooldown
    bd.record_failure(403)  # 2 == warning threshold -> cooldown
    assert calls == [3.0]


# ── build_proxy_options ──────────────────────────────────────────────────────


def test_build_proxy_options():
    assert build_proxy_options({"enabled": False}) == {}
    assert build_proxy_options({"enabled": True}) == {}  # no url
    assert build_proxy_options({"enabled": True, "url": "http://h:1"}) == {
        "--proxy-server": "http://h:1"
    }


# ── SessionManager ───────────────────────────────────────────────────────────


class _FakeDriver:
    """Minimal Selenium-driver stand-in for cookie persistence tests."""

    def __init__(self, cookies=None):
        self._cookies = cookies or []
        self.added = []

    def get_cookies(self):
        return self._cookies

    def add_cookie(self, cookie):
        self.added.append(cookie)


def test_session_manager_cookie_roundtrip(tmp_path):
    cookie_file = tmp_path / "cookies.json"
    sm = SessionManager(cookie_file=cookie_file)
    assert sm.has_saved_cookies is False

    sm.save_cookies(_FakeDriver([{"name": "a", "value": "1", "domain": "dolap.com"}]))
    assert sm.has_saved_cookies is True

    loader = _FakeDriver()
    loaded = sm.load_cookies(loader, domain="dolap.com")
    assert loaded == 1
    assert loader.added[0]["name"] == "a"

    sm.clear_cookies()
    assert sm.has_saved_cookies is False


def test_session_manager_skips_foreign_domain_cookies(tmp_path):
    cookie_file = tmp_path / "cookies.json"
    sm = SessionManager(cookie_file=cookie_file)
    sm.save_cookies(_FakeDriver([{"name": "x", "value": "1", "domain": "example.com"}]))
    loader = _FakeDriver()
    # Cookie domain does not match the target domain -> not injected.
    assert sm.load_cookies(loader, domain="dolap.com") == 0
