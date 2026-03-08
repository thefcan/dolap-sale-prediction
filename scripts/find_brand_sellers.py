#!/usr/bin/env python3
"""Discover fashion sellers from Dolap brand pages.

Strategy: Visit fashion brand pages (dolap.com/zara, dolap.com/hm, etc.)
to find actual clothing product URLs and their sellers.
"""

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


# Fashion category keywords in URL slugs
FASHION_SLUGS = {
    "kazak": "Kazak",
    "elbise": "Elbise", 
    "mont": "Mont",
    "cizme": "Çizme",
    "bot": "Bot",
    "kol-cantasi": "Kol Çantası",
    "spor-ayakkabi": "Spor Ayakkabı",
    "jean-pantolon": "Jean Pantolon",
    "pantolon": "Pantolon",
    "gomlek": "Gömlek",
    "etek": "Etek",
    "tshirt": "T-Shirt",
    "sweatshirt": "Sweatshirt",
    "hirka": "Hırka",
    "ceket": "Ceket",
    "triko": "Triko",
    "bluz": "Bluz",
}


def classify_url(url: str) -> str | None:
    """Try to extract fashion category from product URL slug."""
    slug = url.rstrip("/").split("/")[-1].lower()
    for kw, cat in FASHION_SLUGS.items():
        if kw in slug:
            return cat
    return None


def main():
    driver = make_driver()
    
    # Fashion brand pages to try
    brand_pages = [
        "zara", "hm", "koton", "bershka", "pull-bear",
        "mango", "defacto", "lcw", "ipekyol", "adidas",
        "nike", "puma", "massimo-dutti", "gap", "mavi-jeans",
    ]
    
    all_sellers = {}  # username -> {categories, product_count}
    all_products = []  # (url, category, seller)
    
    try:
        # First visit homepage for cookies
        print("Visiting homepage for cookies...")
        driver.get("https://dolap.com/")
        time.sleep(4)
        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button#onetrust-accept-btn-handler"))
            )
            cookie_btn.click()
            time.sleep(1)
        except Exception:
            pass
        
        # Visit brand pages
        print("\n" + "=" * 60)
        print("VISITING BRAND PAGES")
        print("=" * 60)
        
        for brand in brand_pages:
            url = f"https://dolap.com/{brand}"
            print(f"\n📦 Brand: {brand} ({url})")
            
            try:
                driver.get(url)
                time.sleep(4)
                
                # Check final URL (might redirect)
                final_url = driver.current_url
                if "markalar" in final_url:
                    print(f"  ❌ Redirected to brands page")
                    continue
                
                # Scroll to load products
                for _ in range(3):
                    driver.execute_script("window.scrollBy(0, 800);")
                    time.sleep(1)
                
                # Extract product URLs
                product_urls = extract_urls_js(driver, "/urun/")
                print(f"  Found {len(product_urls)} product URLs")
                
                if product_urls:
                    # Classify products by category
                    cat_counts = {}
                    for pu in product_urls:
                        cat = classify_url(pu)
                        if cat:
                            cat_counts[cat] = cat_counts.get(cat, 0) + 1
                    print(f"  Fashion categories: {cat_counts}")
                    
                    # Extract seller from URL slug
                    # URL format: /urun/{brand}-{color}-{category}-{condition}-{seller}-{id}
                    for pu in product_urls:
                        cat = classify_url(pu)
                        if cat:
                            # Try to get seller from URL slug
                            slug = pu.rstrip("/").split("/")[-1]
                            parts = slug.rsplit("-", 1)
                            if len(parts) == 2:
                                slug_no_id = parts[0]
                                # Seller is usually between condition and id
                                # Pattern: brand-color-cat-condition-seller-id
                                all_products.append((pu, cat, brand))
                    
                    print(f"  Sample: {product_urls[0][:80]}")
                
            except Exception as e:
                print(f"  Error: {e}")
            
            time.sleep(2)
        
        # Now visit some product pages to extract actual sellers
        print("\n" + "=" * 60)
        print("VISITING PRODUCT PAGES TO EXTRACT SELLERS")
        print("=" * 60)
        
        # Collect unique fashion product URLs
        fashion_products = [(url, cat, brand) for url, cat, brand in all_products]
        # Deduplicate and take diverse sample
        seen_urls = set()
        unique_products = []
        for url, cat, brand in fashion_products:
            if url not in seen_urls:
                seen_urls.add(url)
                unique_products.append((url, cat, brand))
        
        print(f"\nTotal fashion product URLs: {len(unique_products)}")
        
        category_sellers = {}  # category -> set of sellers
        
        for i, (url, cat, brand) in enumerate(unique_products[:30]):
            print(f"\n[{i+1}] {cat} | {url.split('/')[-1][:50]}...")
            
            try:
                driver.get(url)
                time.sleep(3)
                
                sellers = extract_sellers_js(driver)
                if sellers:
                    seller = sellers[0]  # First profile link is usually the seller
                    
                    if cat not in category_sellers:
                        category_sellers[cat] = set()
                    category_sellers[cat].add(seller)
                    
                    if seller not in all_sellers:
                        all_sellers[seller] = {"categories": set(), "count": 0}
                    all_sellers[seller]["categories"].add(cat)
                    all_sellers[seller]["count"] += 1
                    
                    print(f"  Seller: @{seller} | Category: {cat}")
                else:
                    print(f"  No seller found")
                    
            except Exception as e:
                print(f"  Error: {e}")
            
            time.sleep(1)
        
        # Final report
        print("\n" + "=" * 60)
        print("FINAL REPORT")
        print("=" * 60)
        
        print(f"\nSellers by category:")
        for cat in sorted(category_sellers.keys()):
            sellers_list = sorted(category_sellers[cat])
            print(f"\n  {cat}:")
            for s in sellers_list:
                print(f"    @{s}")
        
        print(f"\n\nAll sellers ({len(all_sellers)}):")
        for seller in sorted(all_sellers.keys()):
            info = all_sellers[seller]
            cats = ", ".join(sorted(info["categories"]))
            print(f"  @{seller} — {cats}")
        
        # Generate config snippet
        print("\n" + "=" * 60)
        print("CONFIG SNIPPET (for scraping.yaml)")
        print("=" * 60)
        
        # Map sellers to our target categories
        target_cats = {
            "kazak": "Kazak", "elbise": "Elbise", "mont": "Mont",
            "cizme": "Çizme", "bot": "Bot", "kol-cantasi": "Kol Çantası",
            "spor-ayakkabi": "Spor Ayakkabı", "jean-pantolon": "Jean Pantolon",
            "gomlek": "Gömlek", "etek": "Etek", "tshirt": "T-Shirt",
            "sweatshirt": "Sweatshirt",
        }
        
        # Collect all unique sellers as a shared pool
        all_seller_list = sorted(all_sellers.keys())
        print(f"\n# Shared seed_sellers pool ({len(all_seller_list)} sellers):")
        print(f"# {all_seller_list}")
        
        for slug, name in target_cats.items():
            cat_sellers = list(category_sellers.get(name, set()))
            if cat_sellers:
                print(f"\n# {name}: {cat_sellers}")
                
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
