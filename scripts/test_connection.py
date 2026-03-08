"""Quick connection test for Dolap.com via Selenium."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

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

print("[1] Navigating to dolap.com ...")
d.get("https://dolap.com")
time.sleep(5)

title = d.title
page_len = len(d.page_source)
cf_blocked = "Attention Required" in d.page_source or "cf-error" in d.page_source

print(f"[2] Title: {title}")
print(f"[3] Page length: {page_len}")
print(f"[4] Cloudflare blocked: {cf_blocked}")

if not cf_blocked:
    # Try a category page
    print("[5] Testing category page: kazak ...")
    d.get("https://dolap.com/kategori/kazak")
    time.sleep(5)
    print(f"[6] Category title: {d.title}")
    print(f"[7] Category page length: {len(d.page_source)}")
    has_listings = "product" in d.page_source.lower() or "listing" in d.page_source.lower()
    print(f"[8] Has listing content: {has_listings}")

d.quit()
print("[DONE] Connection test finished.")
