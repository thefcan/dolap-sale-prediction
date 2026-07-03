"""Unit tests for :mod:`src.preprocessing.clean_features` (pre-EDA cleaning)."""

from __future__ import annotations

import pandas as pd

from src.preprocessing import clean_features as cf

# ── clean_brand_size ─────────────────────────────────────────────────────────


def test_clean_brand_size_splits_and_recovers_size():
    df = pd.DataFrame(
        {
            "brand": ["Zara - S / 36 Beden", "Mango", None, ""],
            "size": [None, "M", "L", None],
        }
    )
    out = cf.clean_brand_size(df)

    assert out.loc[0, "brand_clean"] == "Zara"
    assert out.loc[0, "size_extracted"] == "S / 36 Beden"
    assert out.loc[1, "brand_clean"] == "Mango"
    assert pd.isna(out.loc[1, "size_extracted"])
    # Missing / empty brand collapses to the "unknown" sentinel.
    assert out.loc[2, "brand_clean"] == "Bilinmiyor"
    assert out.loc[3, "brand_clean"] == "Bilinmiyor"
    # size_final backfills from the brand-embedded size only when size is null.
    assert out.loc[0, "size_final"] == "S / 36 Beden"
    assert out.loc[1, "size_final"] == "M"


# ── normalize_condition ──────────────────────────────────────────────────────


def test_normalize_condition_maps_labels_and_ordinals():
    df = pd.DataFrame({"condition": ["Yeni ve Etiketli", "Kullanılmış", "Foo", None]})
    out = cf.normalize_condition(df)

    assert out.loc[0, "condition_clean"] == "Yeni & Etiketli"
    assert out.loc[0, "condition_ordinal"] == 3
    assert out.loc[1, "condition_ordinal"] == 0
    # Unknown / missing -> sentinel label and -1 ordinal.
    assert out.loc[2, "condition_clean"] == "Bilinmiyor"
    assert out.loc[2, "condition_ordinal"] == -1
    assert out.loc[3, "condition_clean"] == "Bilinmiyor"


# ── fix_category ─────────────────────────────────────────────────────────────


def test_fix_category_copies_scraped_column():
    df = pd.DataFrame({"category_scraped": ["Elbise", "Ayakkabı"]})
    out = cf.fix_category(df)
    assert list(out["category"]) == ["Elbise", "Ayakkabı"]


# ── detect_placeholder_descriptions ──────────────────────────────────────────


def test_detect_placeholder_descriptions():
    df = pd.DataFrame(
        {
            "title": ["Kırmızı elbise", "Ayakkabı", "Çanta"],
            "description_text": ["Kırmızı elbise", "Az giyildi", None],
        }
    )
    out = cf.detect_placeholder_descriptions(df)
    assert bool(out.loc[0, "desc_is_placeholder"]) is True  # equals the title
    assert bool(out.loc[1, "desc_is_placeholder"]) is False
    assert bool(out.loc[2, "desc_is_placeholder"]) is True  # missing description


# ── add_keyword_features ─────────────────────────────────────────────────────


def test_add_keyword_features_respects_placeholder_gate():
    df = pd.DataFrame(
        {
            "description_text": [
                "ufak leke var",
                "acil satılık",
                "temiz ürün",
                "leke var ama",
            ],
            "desc_is_placeholder": [False, False, False, True],
        }
    )
    out = cf.add_keyword_features(df)
    assert bool(out.loc[0, "has_flaw_mention"]) is True  # "leke"
    assert bool(out.loc[1, "desc_has_urgency"]) is True  # "acil"
    assert bool(out.loc[2, "has_flaw_mention"]) is False
    # Keyword present but the row is a placeholder -> feature is suppressed.
    assert bool(out.loc[3, "has_flaw_mention"]) is False


# ── add_price_features ───────────────────────────────────────────────────────


def test_add_price_features_ratio_and_discount():
    df = pd.DataFrame(
        {
            "category": ["A", "A", "A"],
            "price": [50, 100, 150],
            "original_price": [100, None, 300],
        }
    )
    out = cf.add_price_features(df)
    # Category median price is 100.
    assert out.loc[0, "price_to_cat_median"] == 0.5
    assert out.loc[1, "price_to_cat_median"] == 1.0
    assert out.loc[2, "price_to_cat_median"] == 1.5
    # discount_pct is 0 when original_price is missing.
    assert out.loc[0, "discount_pct"] == 50.0
    assert out.loc[1, "discount_pct"] == 0.0
    assert out.loc[2, "discount_pct"] == 50.0


# ── add_brand_tier ───────────────────────────────────────────────────────────


def test_add_brand_tier_orders_cheapest_to_priciest():
    df = pd.DataFrame(
        {
            "brand_clean": ["b0", "b1", "b2", "b3", "b4"],
            "price": [10, 20, 30, 40, 50],
        }
    )
    out = cf.add_brand_tier(df)
    tier = dict(zip(out["brand_clean"], out["brand_tier"], strict=True))
    name = dict(zip(out["brand_clean"], out["brand_tier_name"], strict=True))

    assert tier["b0"] < tier["b4"]
    assert name["b0"] == "Budget"
    assert name["b4"] == "Luxury"
    assert set(out["brand_tier"]).issubset({0, 1, 2, 3, 4})


# ── add_proxy_label ──────────────────────────────────────────────────────────


def test_add_proxy_label_flags_high_engagement():
    df = pd.DataFrame(
        {
            "category": ["A", "A", "A", "A"],
            "like_count": [0, 1, 2, 100],
            "price": [10, 20, 30, 40],
        }
    )
    out = cf.add_proxy_label(df)
    # Only the top-engagement listing crosses the category q75 threshold.
    assert out.loc[3, "proxy_sold"] == 1
    assert out.loc[0, "proxy_sold"] == 0
    assert set(out["proxy_sold"].unique()).issubset({0, 1})
    # sale_score = high_engagement (0/1) + competitive_price (0/1).
    assert out["sale_score"].between(0, 2).all()
