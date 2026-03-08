"""Discover seed sellers for each target category on Dolap.com.

Strategy: Visit the homepage/feed, find product cards, click through to
product detail pages, extract seller usernames and their categories.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re

opts = Options()
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--window-size=1920,1080")
opts.add_argument(
    "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option("useAutomationExtension", False)

d = webdriver.Chrome(options=opts)
d.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
)

# Visit homepage first
print("[1] Setting up cookies via homepage...")
d.get("https://dolap.com")
time.sleep(8)
try:
    accept_btn = d.find_element(By.ID, "onetrust-accept-btn-handler")
    accept_btn.click()
    time.sleep(2)
except Exception:
    pass

# Strategy: Visit a known seller, get a product URL, then from that product
# page discover more sellers via "BENZER ÜRÜNLER"
known_seller = "iphonelcase"

# First: find different category sellers by visiting profiles of large sellers
# We can get sellers from the homepage feed too
print("\n[2] Collecting sellers from a known profile...")
d.get(f"https://dolap.com/profil/{known_seller}")
time.sleep(8)

# Get product URLs from this profile
product_urls = d.execute_script("""
    var links = [];
    document.querySelectorAll('a').forEach(function(a) {
        var href = a.href || '';
        if (href.includes('/urun/')) links.push(href);
    });
    return [...new Set(links)];
""") or []
print(f"  Product URLs from {known_seller}: {len(product_urls)}")

# Visit first product to discover more sellers via BENZER ÜRÜNLER
if product_urls:
    print(f"\n[3] Visiting product to find sellers: {product_urls[0][:80]}")
    d.get(product_urls[0])
    time.sleep(8)

    # Scroll down to see similar products
    d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    # Get all profile links
    profil_urls = d.execute_script("""
        var links = [];
        document.querySelectorAll('a').forEach(function(a) {
            var href = a.href || '';
            if (href.includes('/profil/')) links.push(href);
        });
        return [...new Set(links)];
    """) or []

    sellers = set()
    for pu in profil_urls:
        parts = pu.rstrip("/").split("/profil/")
        if len(parts) == 2:
            username = parts[1].split("?")[0].split("#")[0]
            if username:
                sellers.add(username)

    print(f"  Discovered sellers: {sellers}")

# Now try to find sellers for specific categories by searching
# Visit the category pages that the nav bar links to
print("\n[4] Trying to find category-specific sellers...")
categories_to_check = ["kazak", "elbise", "mont", "bot", "cizme", "kol-cantasi", "spor-ayakkabi"]

# Method: Use the Dolap brand pages for each category
# For example dolap.com/kazak might show some sellers
# Or try dolap.com/zara?kategori=kazak

# Actually, the best approach: use the fact that product URLs contain
# category-slug in the URL pattern:
# /urun/{marka}-{renk}-{kategori-slug}-{durum}-{username}-{id}
# So from any product URL we can infer the category and seller

# Let's visit a few large sellers known to sell clothing
clothing_sellers = ["solo", "busradalgcc", "lomelux", "nalburcuamca", "melidakids", "aeaccessories"]
category_sellers = {}

for seller in clothing_sellers:
    print(f"\n  Checking seller: {seller}")
    d.get(f"https://dolap.com/profil/{seller}")
    time.sleep(6)

    # Get product URLs
    urls = d.execute_script("""
        var links = [];
        document.querySelectorAll('a').forEach(function(a) {
            var href = a.href || '';
            if (href.includes('/urun/')) links.push(href);
        });
        return [...new Set(links)];
    """) or []
    print(f"    Products: {len(urls)}")

    # Get the category info from sidebar
    body_text = d.find_element(By.TAG_NAME, "body").text
    if "KATEGORİ" in body_text:
        cat_idx = body_text.find("KATEGORİ")
        cat_section = body_text[cat_idx:cat_idx+300]
        print(f"    Categories: {cat_section[:200]}")

    # Extract category from URLs
    for url in urls[:3]:
        print(f"    URL: {url[:100]}")

print("\n[5] Looking for fashion sellers specifically...")
# Visit a fashion product URL and discover sellers from BENZER ÜRÜNLER
fashion_search_urls = [
    "https://dolap.com/profil/busradalgcc",  # had phone cases
]

# Try some common Turkish fashion seller names
test_sellers = [
    "modabutik", "fashionstore", "gardrop", "gardrobum",
    "ikinciel", "modaevi", "stilgardrob", "tarzim",
]

for seller in test_sellers:
    d.get(f"https://dolap.com/profil/{seller}")
    time.sleep(4)
    if d.current_url.endswith(f"/profil/{seller}"):
        urls = d.execute_script("""
            var links = [];
            document.querySelectorAll('a').forEach(function(a) {
                var href = a.href || '';
                if (href.includes('/urun/')) links.push(href);
            });
            return [...new Set(links)];
        """) or []
        if urls:
            body = d.find_element(By.TAG_NAME, "body").text
            product_count_match = re.search(r'(\d+)\s*Ürün', body)
            product_count = product_count_match.group(1) if product_count_match else "?"
            print(f"  ✅ {seller}: {len(urls)} URLs on page, {product_count} total products")
            # Check first URL for category
            if urls:
                print(f"     Sample: {urls[0][:100]}")

d.quit()
print("\n[DONE]")
