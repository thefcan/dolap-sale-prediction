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
    """Extract category hierarchy from breadcrumb navigation.

    Strategy priority:
    1. JSON-LD ``BreadcrumbList`` (most reliable, structured data)
    2. ``<ul class="breadcrumb">`` HTML element
    3. Fallback: empty result
    """
    import json as _json

    result: dict[str, str | None] = {"category": None, "subcategory": None}

    # Strategy 1: JSON-LD BreadcrumbList
    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or ""
        if "BreadcrumbList" not in raw:
            continue
        try:
            ld = _json.loads(raw)
            items = ld.get("itemListElement", [])
            # items: [{position, item: {name, ...}}, ...]
            # Typical: ANASAYFA > Giyim > Üst Giyim > T-Shirt > "Koton T-Shirt"
            # The LAST item is brand+category (e.g. "Koton T-Shirt") → skip it
            # The second-to-last is the actual category (e.g. "T-Shirt")
            names = [it.get("item", {}).get("name", "") for it in items]
            names = [n for n in names if n and n.upper() != "ANASAYFA"]
            if len(names) >= 2:
                # Skip last (brand+category), use second-to-last
                result["category"] = names[-2]  # T-Shirt
                if len(names) >= 3:
                    result["subcategory"] = names[-3]  # Üst Giyim
            elif len(names) == 1:
                result["category"] = names[0]
            return result
        except (_json.JSONDecodeError, AttributeError):
            pass

    # Strategy 2: <ul class="breadcrumb"> HTML
    bc_ul = soup.find("ul", class_=re.compile(r"breadcrumb", re.I))
    if bc_ul:
        links = []
        for a in bc_ul.find_all("a"):
            text = _clean(a.get_text())
            if text and text not in ("Ana Sayfa",):
                links.append(text)
        if links:
            result["category"] = links[-1]  # deepest
            if len(links) >= 2:
                result["subcategory"] = links[-2]

    return result


def _parse_brand(soup: BeautifulSoup, breadcrumbs: dict) -> str | None:
    """Extract brand name.

    Strategy priority:
    1. ``<h1>`` in ``title-holder`` → ``"Koton - M / 38 Beden"`` → brand = ``"Koton"``
    2. Last item of BreadcrumbList JSON-LD (brand+category) → first word
    3. ``<title>`` tag fallback
    """
    # Strategy 1: <h1> in title-holder → "Koton - M / 38 Beden" → split by " - "
    title_holder = soup.find("div", class_="title-holder")
    if title_holder:
        h1 = title_holder.find("h1")
        if h1:
            text = _clean(h1.get_text())
            if text:
                # "Koton - M / 38 Beden" → brand = "Koton"
                # "Zara" (no size) → brand = "Zara"
                parts = text.split(" - ", 1)
                brand = parts[0].strip()
                if brand:
                    return brand

    # Strategy 2: <title> tag → "Koton T-Shirt | Dolap.com"
    title_tag = soup.find("title")
    if title_tag:
        text = _clean(title_tag.get_text())
        if text:
            for suffix in [" - Dolap.com", " | Dolap", " - dolap.com"]:
                if text.endswith(suffix):
                    text = text[: -len(suffix)].strip()
            return text or None

    return None


def _parse_title(soup: BeautifulSoup) -> str | None:
    """Extract the listing title.

    Strategy:
    1. ``<h1>`` inside ``title-holder`` → ``"Koton - M / 38 Beden"``
    2. ``<title>`` tag → ``"Koton T-Shirt Yeni & Etiketli…"``
    3. ``og:title`` meta tag
    """
    # Strategy 1: <h1> in title-holder (product heading)
    title_holder = soup.find("div", class_="title-holder")
    if title_holder:
        h1 = title_holder.find("h1")
        if h1:
            text = _clean(h1.get_text())
            if text:
                return text

    # Strategy 2: <title> tag
    title_tag = soup.find("title")
    if title_tag:
        text = _clean(title_tag.get_text())
        if text:
            for suffix in [" - Dolap.com", " | Dolap", " - dolap.com"]:
                if text.endswith(suffix):
                    text = text[: -len(suffix)].strip()
            return text

    # Strategy 3: og:title
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return _clean(og_title["content"])

    return None


def _parse_prices(soup: BeautifulSoup) -> dict[str, float | None]:
    """Extract current and (optional) original price.

    Strategy priority:
    1. ``<div class="price-block">`` → primary price area
    2. ``<div class="price-detail">`` → clean price text
    3. Fallback: regex scan of full page text
    """
    result = {"current": None, "original": None}

    # Strategy 1: price-block div (contains current + optional original)
    price_block = soup.find("div", class_="price-block")
    if price_block:
        # Look for strikethrough (original) price
        strike = price_block.find(["del", "s", "strike"])
        if strike:
            result["original"] = _extract_price(strike.get_text())

        # The first price-detail in price-block is the current price
        price_detail = price_block.find("div", class_="price-detail")
        if price_detail:
            result["current"] = _extract_price(price_detail.get_text())
        else:
            # Fallback: first TL price in price-block
            result["current"] = _extract_price(price_block.get_text())

        if result["current"] is not None:
            return result

    # Strategy 2: standalone price-detail divs
    price_details = soup.find_all("div", class_="price-detail")
    if price_details:
        result["current"] = _extract_price(price_details[0].get_text())
        return result

    # Strategy 3: regex fallback
    page_text = soup.get_text(separator="\n")
    price_matches = _PRICE_RE.findall(page_text)
    if price_matches:
        prices = []
        for raw in price_matches:
            p = raw.replace(".", "").replace(",", ".")
            try:
                prices.append(float(p))
            except ValueError:
                continue
        if len(prices) >= 2 and prices[0] > prices[1]:
            result["original"] = prices[0]
            result["current"] = prices[1]
        elif len(prices) >= 1:
            result["current"] = prices[0]

    return result


def _parse_condition(soup: BeautifulSoup) -> str | None:
    """Detect condition badge text.

    Strategy priority:
    1. ``<span class="subtitle">`` in title-block (most reliable)
    2. Full-text keyword search (fallback)
    """
    conditions = [
        "Yeni ve Etiketli",
        "Yeni & Etiketli",
        "Yeni",
        "Az Kullanılmış",
        "Çok Kullanılmış",
        "Kullanılmış",
        "Defolu",
    ]

    # Strategy 1: <span class="subtitle"> in title-block
    title_block = soup.find("div", class_="title-block")
    if title_block:
        for span in title_block.find_all("span", class_="subtitle"):
            text = _clean(span.get_text())
            if text and text in conditions:
                return text

    # Strategy 2: any <span class="subtitle"> matching conditions
    for span in soup.find_all("span", class_="subtitle"):
        text = _clean(span.get_text())
        if text and text in conditions:
            return text

    # Strategy 3: full-text fallback
    page_text = soup.get_text()
    for cond in conditions:
        if cond in page_text:
            return cond
    return None


def _parse_color(soup: BeautifulSoup, url: str = "") -> str | None:
    """Extract colour from page elements or URL slug.

    Strategy priority:
    1. ``<title>`` tag often contains color ("Koton Desenli T-Shirt")
    2. URL slug second segment (brand-color-category-...)
    """
    # Known Dolap colour values
    _COLORS = {
        "siyah", "beyaz", "kirmizi", "kırmızı", "mavi", "lacivert",
        "yesil", "yeşil", "sari", "sarı", "turuncu", "mor", "pembe",
        "gri", "kahverengi", "bej", "krem", "bordo", "haki", "ekru",
        "fuşya", "lila", "turkuaz", "pudra", "antrasit", "camel",
        "altın", "gümüş", "mercan", "kiremit", "hardal",
        "desenli", "çizgili", "karışık", "renkli", "çok renkli",
    }

    # Strategy 1: Parse from <title> tag ("Koton Desenli T-Shirt Yeni...")
    title_tag = soup.find("title")
    if title_tag:
        title_text = (title_tag.get_text() or "").lower()
        for color in _COLORS:
            if color in title_text:
                return color.capitalize()

    # Strategy 2: Parse from URL slug
    if url:
        slug_parts = url.rstrip("/").split("/")[-1].split("-")
        for part in slug_parts:
            if part.lower() in _COLORS:
                return part.capitalize()

    return None


def _parse_size(soup: BeautifulSoup) -> str | None:
    """Extract size from product details area.

    Strategy:
    1. ``<h1>`` in ``title-holder`` → ``"Koton - M / 38 Beden"`` → ``"M / 38 Beden"``
    2. Regex fallback on page text
    """
    # Strategy 1: <h1> in title-holder → split by " - " → second part is size
    title_holder = soup.find("div", class_="title-holder")
    if title_holder:
        h1 = title_holder.find("h1")
        if h1:
            text = _clean(h1.get_text())
            if text and " - " in text:
                parts = text.split(" - ", 1)
                size_part = parts[1].strip()
                # Remove "Beden" suffix for cleaner output
                if size_part:
                    return size_part

    # Strategy 2: regex fallback
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
    """Extract seller description text.

    Strategy priority:
    1. ``<div class="profile-block">`` seller description area
    2. og:description meta tag
    3. Heuristic text search (fallback)
    """
    # Strategy 1: <p> inside profile-block > remarks-block
    profile_block = soup.find("div", class_="profile-block")
    if profile_block:
        # Description is in <div class="remarks-block"> > <p>
        remarks = profile_block.find("div", class_="remarks-block")
        if remarks:
            p_tag = remarks.find("p")
            if p_tag:
                text = _clean(p_tag.get_text())
                if text and len(text) > 5:
                    return text
        # Fallback: any <p> in profile-block
        for p_tag in profile_block.find_all("p"):
            text = _clean(p_tag.get_text())
            if text and len(text) > 10:
                return text

    # Strategy 2: og:description meta tag
    og_desc = soup.find("meta", property="og:description")
    if og_desc and og_desc.get("content"):
        desc = _clean(og_desc["content"])
        if desc and len(desc) > 10:
            return desc

    # Strategy 3: heuristic fallback
    page_text = soup.get_text(separator="\n")
    lines = [_clean(line) for line in page_text.split("\n") if _clean(line)]
    skip_patterns = [
        "KATEGORİLER", "BENZER ÜRÜNLER", "Popüler Aramalar",
        "Dolap Hakkında", "Kategoriler", "Tanımlama bilgilerini",
        "Ödeme Seçenekleri", "Yorum Yayınlanma", "PAYLAŞ",
        "Dolap Avantajları", "Teklif Nasıl",
    ]
    for line in lines:
        if not line or len(line) < 20:
            continue
        if any(skip in line for skip in skip_patterns):
            continue
        if any(kw in line.lower() for kw in [
            "kılıf", "elbise", "kazak", "mont", "pantolon", "ayakkabı",
            "çanta", "gömlek", "etek", "tshirt", "bot", "çizme",
            "kullanılmamış", "sıfır", "orjinal", "mevcut",
            "renk", "beden", "kargo", "yeni", "tertemiz",
        ]):
            return line

    return None


def _parse_photo_count(soup: BeautifulSoup) -> int:
    """Count product images (carousel slides or thumbnails).

    Strategy:
    1. Images from ``dsmcdn.com`` with ``/product/`` path (actual product photos)
    2. OG image as minimum-1 fallback
    """
    seen_srcs: set[str] = set()

    for img in soup.find_all("img"):
        src = img.get("src", "") or img.get("data-src", "")
        # Product images are hosted on dsmcdn.com under /product/ path
        if "dsmcdn" in src and "/product/" in src:
            # Normalise: strip resize params to dedup same image at diff sizes
            base = src.split("?")[0]
            # Remove mnresize prefix variations
            base = re.sub(r"/mnresize/\d+/\d+/", "/", base)
            if base not in seen_srcs:
                seen_srcs.add(base)

    count = len(seen_srcs)

    # Fallback: if nothing found, check og:image exists
    if count == 0:
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            count = 1

    return count


def _parse_engagement(soup: BeautifulSoup) -> dict[str, int | None]:
    """Extract like and comment counts.

    Strategy priority:
    - Likes:  ``<a class="product-likes">`` in ``likes-block`` (hidden-xs)
    - Comments: ``<span class="comment-count">`` in ``<h2>Yorumlar (N)</h2>``
    - Fallback: regex on page text
    """
    result = {"likes": None, "comments": None}

    # ── Likes ────────────────────────────────────────────────────────
    # Strategy 1: likes-block (hidden-xs) → "N\n Beğeni"
    likes_block = soup.find("div", class_="likes-block")
    if likes_block:
        like_link = likes_block.find("a", class_="product-likes")
        if like_link:
            nums = _NUMERIC_RE.findall(like_link.get_text())
            if nums:
                result["likes"] = int(nums[0])

    # Strategy 2: regex fallback for likes
    if result["likes"] is None:
        page_text = soup.get_text()
        like_match = re.search(r"(\d+)\s*Beğeni", page_text)
        if like_match:
            result["likes"] = int(like_match.group(1))

    # ── Comments ─────────────────────────────────────────────────────
    # Strategy 1: <span class="comment-count"> in <h2>Yorumlar (N)</h2>
    cc_span = soup.find("span", class_="comment-count")
    if cc_span:
        cc_text = cc_span.get_text().strip()
        if cc_text.isdigit():
            result["comments"] = int(cc_text)

    # Strategy 2: regex fallback
    if result["comments"] is None:
        page_text = page_text if "page_text" in dir() else soup.get_text()
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
    """Extract seller username and listing count from product page.

    The seller appears in ``<div class="profile-block">`` as a link
    to ``/profil/{username}`` with listing count in parentheses.
    """
    result: dict[str, Any] = {"username": None, "listing_count": None}

    # Strategy 1: profile-block div (primary seller, not similar products)
    profile_block = soup.find("div", class_="profile-block")
    if profile_block:
        for a in profile_block.find_all("a", href=True):
            href = a.get("href", "")
            if "/profil/" in href:
                parts = href.rstrip("/").split("/profil/")
                if len(parts) == 2 and parts[1]:
                    username = parts[1].split("?")[0].split("#")[0]
                    result["username"] = username
                    # Listing count: parent text contains "(N)"
                    parent_text = a.parent.get_text() if a.parent else ""
                    count_match = re.search(r"\((\d+)\)", parent_text)
                    if count_match:
                        result["listing_count"] = int(count_match.group(1))
                    return result

    # Strategy 2: first /profil/ link on page (fallback)
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if "/profil/" in href:
            parts = href.rstrip("/").split("/profil/")
            if len(parts) == 2 and parts[1]:
                username = parts[1].split("?")[0].split("#")[0]
                result["username"] = username
                parent_text = a.parent.get_text() if a.parent else ""
                count_match = re.search(r"\((\d+)\)", parent_text)
                if count_match:
                    result["listing_count"] = int(count_match.group(1))
                break

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
