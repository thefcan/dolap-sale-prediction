"""
HTML parsers for Dolap.com listing pages.

Extracts structured data from product detail pages and category listing
pages using BeautifulSoup.  All parsers operate on *already-rendered* HTML
(i.e. the HTML returned after Selenium has executed all JS).

Design contract
---------------
* Each ``parse_*`` function receives a BeautifulSoup ``Tag`` or ``str``
  (raw HTML) and returns a plain ``dict`` with normalised field names.
* Every dict includes a ``_parse_errors`` list so callers can log problems
  without raising.
* ``None`` is used for missing / unparseable fields — never empty string.
"""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup, Tag


# ── Regex helpers ───────────────────────────────────────────────────────────

_PRICE_RE = re.compile(r"([\d.,]+)\s*TL", re.IGNORECASE)
_NUMERIC_RE = re.compile(r"(\d+)")
_ID_FROM_URL_RE = re.compile(r"-(\d{6,})$")  # trailing numeric id in slug


# ── Low-level helpers ───────────────────────────────────────────────────────


def _to_soup(html: str | Tag) -> BeautifulSoup:
    """Ensure we always work with a BeautifulSoup object."""
    if isinstance(html, BeautifulSoup):
        return html
    if isinstance(html, Tag):
        return BeautifulSoup(str(html), "html.parser")
    return BeautifulSoup(html, "html.parser")


def _first_int(text: str | None) -> int | None:
    """Extract first integer from *text*, or ``None``."""
    if not text:
        return None
    m = _NUMERIC_RE.search(text)
    return int(m.group(1)) if m else None


def _extract_price(text: str | None) -> float | None:
    """Parse ``'249 TL'`` or ``'1.299 TL'`` → ``float``."""
    if not text:
        return None
    m = _PRICE_RE.search(text)
    if not m:
        return None
    raw = m.group(1).replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _clean(text: str | None) -> str | None:
    """Strip and normalise whitespace; return ``None`` for empty."""
    if text is None:
        return None
    cleaned = " ".join(text.split()).strip()
    return cleaned or None


# ── Public parsers ──────────────────────────────────────────────────────────


def parse_listing_urls_from_page(html: str | Tag) -> list[str]:
    """Extract product detail URLs from a category / search / profile page.

    Looks for anchor tags whose ``href`` matches ``/urun/…`` pattern.
    Deduplicates and preserves order.

    Parameters
    ----------
    html : str | Tag
        Rendered HTML of a listing page.

    Returns
    -------
    list[str]
        Deduplicated listing URLs (relative paths starting with ``/urun/``).
    """
    soup = _to_soup(html)
    seen: set[str] = set()
    urls: list[str] = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/urun/" in href:
            # Normalise: strip domain if present
            if href.startswith("http"):
                # keep path only
                from urllib.parse import urlparse

                href = urlparse(href).path
            if href not in seen:
                seen.add(href)
                urls.append(href)
    return urls


def extract_listing_id_from_url(url: str) -> str | None:
    """Pull trailing numeric id from a product URL slug.

    ``/urun/apple-bej-telefon-kilifi-yeni-etiketli-iphonelcase-442885461``
    → ``'442885461'``
    """
    m = _ID_FROM_URL_RE.search(url.rstrip("/"))
    return m.group(1) if m else None


def parse_product_detail(html: str | Tag, url: str = "") -> dict[str, Any]:
    """Parse a rendered product detail page into a flat dict.

    Parameters
    ----------
    html : str | Tag
        Full rendered HTML of a ``/urun/…`` page.
    url : str
        The page URL (used for id extraction and stored in output).

    Returns
    -------
    dict
        Keys are column names matching ``configs/features.yaml``.
    """
    soup = _to_soup(html)
    errors: list[str] = []
    data: dict[str, Any] = {
        "url": url or None,
        "listing_id": extract_listing_id_from_url(url) if url else None,
    }

    # ── Breadcrumb (category hierarchy) ──────────────────────────────────
    breadcrumbs = _parse_breadcrumbs(soup)
    data["category"] = breadcrumbs.get("category")
    data["subcategory"] = breadcrumbs.get("subcategory")

    # ── Brand ────────────────────────────────────────────────────────────
    data["brand"] = _parse_brand(soup, breadcrumbs)

    # ── Title ────────────────────────────────────────────────────────────
    data["title"] = _parse_title(soup)

    # ── Price ────────────────────────────────────────────────────────────
    prices = _parse_prices(soup)
    data["price"] = prices.get("current")
    data["original_price"] = prices.get("original")
    data["has_discount"] = prices.get("original") is not None and (
        prices.get("original", 0) > prices.get("current", 0)
    )

    # ── Condition ────────────────────────────────────────────────────────
    data["condition"] = _parse_condition(soup)

    # ── Color ────────────────────────────────────────────────────────────
    data["color"] = _parse_color(soup, url)

    # ── Size ─────────────────────────────────────────────────────────────
    data["size"] = _parse_size(soup)

    # ── Description ──────────────────────────────────────────────────────
    desc = _parse_description(soup)
    data["description_text"] = desc
    data["description_length"] = len(desc) if desc else 0
    data["description_word_count"] = len(desc.split()) if desc else 0

    # ── Photos ───────────────────────────────────────────────────────────
    data["photo_count"] = _parse_photo_count(soup)

    # ── Engagement ───────────────────────────────────────────────────────
    engagement = _parse_engagement(soup)
    data["like_count"] = engagement.get("likes")
    data["comment_count"] = engagement.get("comments")

    # ── Shipping ─────────────────────────────────────────────────────────
    data["shipping_info"] = _parse_shipping(soup)
    data["shipping_buyer_pays"] = _is_buyer_pays(data["shipping_info"])

    # ── Seller ───────────────────────────────────────────────────────────
    seller = _parse_seller(soup)
    data["seller_username"] = seller.get("username")
    data["seller_listing_count"] = seller.get("listing_count")

    # ── Sold status ──────────────────────────────────────────────────────
    data["is_sold"] = _detect_sold(soup)

    # ── Parse quality ────────────────────────────────────────────────────
    # Count how many key fields are None → quality signal
    key_fields = ["price", "brand", "condition", "seller_username"]
    missing = [f for f in key_fields if data.get(f) is None]
    if missing:
        errors.append(f"Missing key fields: {missing}")

    data["_parse_errors"] = errors
    return data


# ── Internal parsing helpers ────────────────────────────────────────────────


def _parse_breadcrumbs(soup: BeautifulSoup) -> dict[str, str | None]:
    """Extract category hierarchy from breadcrumb navigation."""
    result: dict[str, str | None] = {"category": None, "subcategory": None}

    # Breadcrumbs: "Ana Sayfa > Elektronik > Telefon Aksesuarı > Telefon Kılıfı > Apple"
    # We want the 2nd-to-last and 3rd-to-last levels
    # Try: look for breadcrumb-like link sequences or text
    bc_links = []
    for a in soup.find_all("a"):
        text = _clean(a.get_text())
        href = a.get("href", "")
        if text and href and text not in ("Ana Sayfa", "GİRİŞ YAP", "Markalar"):
            # breadcrumb links typically point to dolap.com/ category paths
            if href.startswith("https://dolap.com/") or (
                href.startswith("/") and "/urun/" not in href and "/profil/" not in href
            ):
                bc_links.append(text)

    # The page typically shows: Ana Sayfa > MainCat > SubCat > SubSubCat > Brand
    # We'll try to detect the breadcrumb by finding "KATEGORİLER" section
    # or by checking the page structure
    breadcrumb_text = soup.get_text()

    # Fallback: try to extract from URL slug
    # /urun/{brand}-{color}-{category-slug}-{condition}-{user}-{id}
    return result


def _parse_brand(soup: BeautifulSoup, breadcrumbs: dict) -> str | None:
    """Extract brand name.

    Strategy priority:
    1. <h1> or heading containing just the brand name
    2. Product title area near the price section
    3. Breadcrumb last element (often brand)
    """
    # Strategy 1: The brand name appears as a standalone heading / title
    # On Dolap product pages, the brand appears prominently
    # Look for the main product info section
    page_text = soup.get_text(separator="\n")

    # Look for pattern: Brand name near "Telefon Kılıfı" or category name
    # The product page shows: "Apple Telefon Kılıfı" or "Zara Kazak"
    for h in soup.find_all(["h1", "h2", "h3"]):
        text = _clean(h.get_text())
        if text and len(text) < 50:
            # This might be the brand name shown as heading
            # On Dolap, h1 often just shows the brand
            return text

    return None


def _parse_title(soup: BeautifulSoup) -> str | None:
    """Extract the listing title (Brand + Category combo)."""
    # On Dolap, title is typically "Apple Telefon Kılıfı" pattern
    # Shown in <title> or og:title meta
    title_tag = soup.find("title")
    if title_tag:
        text = _clean(title_tag.get_text())
        if text:
            # Remove site name suffix if present
            for suffix in [" - Dolap.com", " | Dolap", " - dolap.com"]:
                if text.endswith(suffix):
                    text = text[: -len(suffix)].strip()
            return text

    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return _clean(og_title["content"])

    return None


def _parse_prices(soup: BeautifulSoup) -> dict[str, float | None]:
    """Extract current and (optional) original price."""
    result = {"current": None, "original": None}

    # Find all price-like text in the page
    page_text = soup.get_text(separator="\n")
    price_matches = _PRICE_RE.findall(page_text)

    if price_matches:
        # Parse all found prices
        prices = []
        for raw in price_matches:
            p = raw.replace(".", "").replace(",", ".")
            try:
                prices.append(float(p))
            except ValueError:
                continue

        if len(prices) >= 2 and prices[0] > prices[1]:
            # First price is original (strikethrough), second is current
            result["original"] = prices[0]
            result["current"] = prices[1]
        elif len(prices) >= 1:
            result["current"] = prices[0]

    return result


def _parse_condition(soup: BeautifulSoup) -> str | None:
    """Detect condition badge text."""
    conditions = [
        "Yeni ve Etiketli",
        "Yeni & Etiketli",
        "Yeni",
        "Az Kullanılmış",
        "Çok Kullanılmış",
        "Kullanılmış",
        "Defolu",
    ]
    page_text = soup.get_text()
    for cond in conditions:
        if cond in page_text:
            return cond
    return None


def _parse_color(soup: BeautifulSoup, url: str = "") -> str | None:
    """Extract colour from colour swatch or URL slug."""
    # Strategy 1: Look for colour label text (e.g. "Bej" next to swatch img)
    for img in soup.find_all("img"):
        alt = img.get("alt", "")
        src = img.get("src", "")
        if "colour" in src or "color" in src:
            if alt:
                return _clean(alt)

    # Strategy 2: Parse from URL slug
    # URL pattern: /urun/{brand}-{color}-{category}-{condition}-{user}-{id}
    if url:
        parts = url.rstrip("/").split("/")
        if parts:
            slug = parts[-1]
            # Split by the last numeric id
            slug_parts = slug.rsplit("-", 1)
            if len(slug_parts) == 2 and slug_parts[1].isdigit():
                # Remove the user part
                remaining = slug_parts[0]
                # The color is typically the 2nd segment
                segments = remaining.split("-")
                if len(segments) >= 3:
                    # brand-color-cat...-condition-user
                    # Color is segments[1] (after brand)
                    return segments[1].capitalize()

    return None


def _parse_size(soup: BeautifulSoup) -> str | None:
    """Extract size from product details area."""
    # Size appears in product detail area for clothing items
    # Common patterns: "S", "M", "L", "36", "38", "4XL / 48"
    page_text = soup.get_text()
    size_patterns = [
        r"Beden[:\s]+([A-Z0-9/\s]+)",
        r"(\d{1,2}XL\s*/\s*\d{2})",
        r"Beden\s*:\s*(\S+)",
    ]
    for pattern in size_patterns:
        m = re.search(pattern, page_text, re.IGNORECASE)
        if m:
            return _clean(m.group(1))
    return None


def _parse_description(soup: BeautifulSoup) -> str | None:
    """Extract seller description text."""
    # The description is the free-text area written by the seller
    # On Dolap it appears below the product details
    # We look for longer text blocks that aren't navigation / boilerplate
    page_text = soup.get_text(separator="\n")
    lines = [_clean(line) for line in page_text.split("\n") if _clean(line)]

    # Heuristic: find text blocks that are descriptive (20+ chars)
    # and not navigation elements
    skip_patterns = [
        "KATEGORİLER", "BENZER ÜRÜNLER", "Popüler Aramalar",
        "Dolap Hakkında", "Kol Çantası", "Kategoriler",
        "Tanımlama bilgilerini", "Ödeme Seçenekleri",
        "Yorum Yayınlanma", "PAYLAŞ", "Dolap Avantajları",
    ]
    for line in lines:
        if not line or len(line) < 20:
            continue
        if any(skip in line for skip in skip_patterns):
            continue
        # Description is typically a sentence about the product
        if any(kw in line.lower() for kw in [
            "kılıf", "elbise", "kazak", "mont", "pantolon", "ayakkabı",
            "çanta", "gömlek", "etek", "tshirt", "bot", "çizme",
            "kullanılmamış", "sıfır", "orjinal", "modelleri", "mevcut",
            "renk", "beden", "kargo", "yeni", "tertemiz",
        ]):
            return line

    return None


def _parse_photo_count(soup: BeautifulSoup) -> int:
    """Count product images (carousel slides or thumbnails)."""
    # Product images are typically in img tags with "product" in src
    count = 0
    seen_srcs: set[str] = set()
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "product" in src or "dlp_" in src or "dsmcdn" in src:
            if src not in seen_srcs:
                seen_srcs.add(src)
                count += 1
    # Fallback: alt text pattern "Brand Kategori" repeated = carousel
    if count == 0:
        alt_pattern_count = 0
        for img in soup.find_all("img"):
            alt = img.get("alt", "")
            if alt and ("Telefon" in alt or "Kazak" in alt or "Elbise" in alt):
                alt_pattern_count += 1
        count = alt_pattern_count
    return count


def _parse_engagement(soup: BeautifulSoup) -> dict[str, int | None]:
    """Extract like and comment counts."""
    result = {"likes": None, "comments": None}
    page_text = soup.get_text()

    # Like pattern: "32 Beğeni"
    like_match = re.search(r"(\d+)\s*Beğeni", page_text)
    if like_match:
        result["likes"] = int(like_match.group(1))

    # Comment pattern: "Yorumlar (0)" or "0 Yorum"
    comment_match = re.search(r"Yorumlar?\s*\((\d+)\)", page_text)
    if comment_match:
        result["comments"] = int(comment_match.group(1))
    else:
        comment_match2 = re.search(r"(\d+)\s*Yorum", page_text)
        if comment_match2:
            result["comments"] = int(comment_match2.group(1))

    return result


def _parse_shipping(soup: BeautifulSoup) -> str | None:
    """Extract shipping info text."""
    page_text = soup.get_text()
    shipping_patterns = [
        "Alıcı Ödemeli Kargo",
        "Alıcı Öder",
        "Ücretsiz Kargo",
        "Satıcı Öder",
        "Kargo Dahil",
    ]
    for pattern in shipping_patterns:
        if pattern in page_text:
            return pattern
    return None


def _is_buyer_pays(shipping_info: str | None) -> bool:
    """Return True if the buyer pays for shipping."""
    if not shipping_info:
        return False  # default: unknown
    buyer_keywords = ["Alıcı Ödemeli", "Alıcı Öder"]
    return any(kw in shipping_info for kw in buyer_keywords)


def _parse_seller(soup: BeautifulSoup) -> dict[str, Any]:
    """Extract seller username and listing count from product page."""
    result: dict[str, Any] = {"username": None, "listing_count": None}

    # Seller appears as a link to /profil/{username} with (count)
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "/profil/" in href:
            # Extract username from /profil/{username}
            parts = href.rstrip("/").split("/profil/")
            if len(parts) == 2 and parts[1]:
                username = parts[1]
                result["username"] = username

                # Look for listing count in nearby text: "iphonelcase (1221)"
                parent_text = a.parent.get_text() if a.parent else ""
                count_match = re.search(r"\((\d+)\)", parent_text)
                if count_match:
                    result["listing_count"] = int(count_match.group(1))
                break  # first seller link is the product seller

    return result


def _detect_sold(soup: BeautifulSoup) -> bool:
    """Return True if the listing is marked as sold."""
    page_text = soup.get_text()
    sold_indicators = [
        "Satıldı",
        "Bu ürün satılmıştır",
        "SATILDI",
        "sold",
    ]
    return any(indicator in page_text for indicator in sold_indicators)
