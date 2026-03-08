#!/usr/bin/env python3
"""Discover fashion sellers from dolap.com homepage feed.

Strategy:
1. Visit homepage → extract /urun/ links via JS DOM query
2. Visit a few product pages → extract seller usernames + categories
3. Report sellers grouped by fashion categories
"""

import re
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def make_driver():
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--window-size=1280,900")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=opts)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"
    })
    return driver


def extract_urls_js(driver, pattern="/urun/"):
    return driver.execute_script(f"""
        var links = [];
        document.querySelectorAll('a').forEach(function(a) {{
            var href = a.href || '';
            if (href.includes('{pattern}')) links.push(href);
        }});
        return [...new Set(links)];
    """) or []


def extract_sellers_js(driver):
    return driver.execute_script("""
        var sellers = [];
        document.querySelectorAll('a').forEach(function(a) {
            var href = a.href || '';
            if (href.includes('/profil/')) {
                var parts = href.split('/profil/');
                if (parts.length === 2 && parts[1]) {
                    var username = parts[1].split('?')[0].split('#')[0].replace(/\\/+$/, '');
                    if (username) sellers.push(username);
                }
            }
        });
        return [...new Set(sellers)];
    """) or []


def get_page_text(driver):
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        return body.text
    except Exception:
        return ""


def main():
    driver = make_driver()
    
    try:
        # Step 1: Visit homepage
        print("=" * 60)
        print("STEP 1: Homepage visit")
        print("=" * 60)
        driver.get("https://dolap.com/")
        time.sleep(5)
        
        # Accept cookies
        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#onetrust-accept-btn-handler"))
            )
            cookie_btn.click()
            print("✅ Cookie consent accepted")
            time.sleep(1)
        except Exception:
            print("ℹ️  No cookie banner")
        
        # Extract product URLs from homepage
        homepage_urls = extract_urls_js(driver, "/urun/")
        print(f"Homepage /urun/ URLs found: {len(homepage_urls)}")
        
        # If no URLs on homepage, try scrolling
        if len(homepage_urls) < 5:
            print("Scrolling to load more products...")
            for i in range(5):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1.5)
            homepage_urls = extract_urls_js(driver, "/urun/")
            print(f"After scroll: {len(homepage_urls)} URLs")
        
        if homepage_urls:
            print(f"\nSample URLs:")
            for u in homepage_urls[:5]:
                print(f"  {u}")
        
        # Step 2: Visit product pages and extract seller info
        print("\n" + "=" * 60)
        print("STEP 2: Visiting product pages to find sellers")
        print("=" * 60)
        
        sellers = {}  # username -> {products: [url], categories: set}
        
        # Visit up to 15 product pages
        for i, url in enumerate(homepage_urls[:15]):
            print(f"\n[{i+1}/15] Visiting: {url[:70]}...")
            try:
                driver.get(url)
                time.sleep(3)
                
                # Wait for content
                try:
                    WebDriverWait(driver, 8).until(
                        lambda d: "TL" in d.page_source
                    )
                except Exception:
                    pass
                
                text = get_page_text(driver)
                
                # Extract seller from page
                seller_usernames = extract_sellers_js(driver)
                
                # Parse category from URL slug
                # URL pattern: /urun/brand-description-category-condition-seller-id
                url_parts = url.rstrip("/").split("/")
                slug = url_parts[-1] if url_parts else ""
                
                # Try to find category in page text
                fashion_cats = [
                    "Kazak", "Elbise", "Mont", "Çizme", "Bot", 
                    "Kol Çantası", "Spor Ayakkabı", "Jean", "Pantolon",
                    "Gömlek", "Etek", "T-Shirt", "Sweatshirt",
                    "Hırka", "Ceket", "Triko", "Bluz", "Giyim",
                    "Ayakkabı", "Çanta", "Elbise"
                ]
                
                found_cats = []
                for cat in fashion_cats:
                    if cat.lower() in text.lower():
                        found_cats.append(cat)
                
                # Check if this is a fashion item
                is_fashion = any(cat in found_cats for cat in [
                    "Kazak", "Elbise", "Mont", "Bot", "Çizme",
                    "Spor Ayakkabı", "Jean", "Pantolon", "Gömlek",
                    "Etek", "T-Shirt", "Sweatshirt", "Hırka", "Ceket",
                    "Triko", "Bluz", "Giyim", "Ayakkabı", "Çanta"
                ])
                
                # Also check URL slug for fashion keywords
                fashion_slugs = [
                    "kazak", "elbise", "mont", "cizme", "bot",
                    "ayakkabi", "pantolon", "gomlek", "etek", "tshirt",
                    "sweatshirt", "hirka", "ceket", "triko", "bluz",
                    "cantasi", "canta"
                ]
                slug_fashion = any(fs in slug.lower() for fs in fashion_slugs)
                
                if seller_usernames:
                    seller = seller_usernames[0]
                    if seller not in sellers:
                        sellers[seller] = {"products": [], "categories": set(), "is_fashion": False}
                    sellers[seller]["products"].append(url)
                    sellers[seller]["categories"].update(found_cats)
                    if is_fashion or slug_fashion:
                        sellers[seller]["is_fashion"] = True
                    
                    cat_str = ", ".join(found_cats[:3]) if found_cats else "unknown"
                    print(f"  Seller: {seller} | Fashion: {is_fashion or slug_fashion} | Cats: {cat_str}")
                else:
                    print(f"  No seller found")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  Error: {e}")
                continue
        
        # Step 3: Report results
        print("\n" + "=" * 60)
        print("STEP 3: Results")
        print("=" * 60)
        
        fashion_sellers = {k: v for k, v in sellers.items() if v["is_fashion"]}
        other_sellers = {k: v for k, v in sellers.items() if not v["is_fashion"]}
        
        print(f"\n✅ FASHION SELLERS ({len(fashion_sellers)}):")
        for username, info in sorted(fashion_sellers.items()):
            cats = ", ".join(info["categories"]) if info["categories"] else "?"
            print(f"  @{username} — {len(info['products'])} products — {cats}")
        
        print(f"\n❌ NON-FASHION SELLERS ({len(other_sellers)}):")
        for username, info in sorted(other_sellers.items()):
            cats = ", ".join(info["categories"]) if info["categories"] else "?"
            print(f"  @{username} — {len(info['products'])} products — {cats}")
        
        # Step 4: Chain discover from fashion sellers' product pages
        if fashion_sellers:
            print("\n" + "=" * 60)
            print("STEP 4: Chain discovery from fashion products")
            print("=" * 60)
            
            # Visit 'BENZER ÜRÜNLER' section of fashion products to find more sellers
            chain_sellers = set()
            for username, info in list(fashion_sellers.items())[:3]:
                product_url = info["products"][0]
                print(f"\nVisiting {product_url[:60]}... to find similar sellers")
                try:
                    driver.get(product_url)
                    time.sleep(4)
                    
                    # Extract all seller profiles from page
                    more_sellers = extract_sellers_js(driver)
                    for s in more_sellers:
                        if s != username and s not in sellers:
                            chain_sellers.add(s)
                    
                    print(f"  Found {len(more_sellers)} profile links, {len(chain_sellers)} new sellers")
                except Exception as e:
                    print(f"  Error: {e}")
            
            if chain_sellers:
                print(f"\n🔗 CHAIN-DISCOVERED SELLERS ({len(chain_sellers)}):")
                for s in sorted(chain_sellers):
                    print(f"  @{s}")
        
        # Final summary for config
        all_fashion_usernames = list(fashion_sellers.keys())
        print("\n" + "=" * 60)
        print("SEED SELLERS FOR CONFIG:")
        print("=" * 60)
        print(f"seed_sellers: {all_fashion_usernames}")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
