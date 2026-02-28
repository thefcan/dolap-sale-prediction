# Dolap.com Site Haritası & Reverse Engineering Raporu

> **Tarih:** 2025-01  
> **Amaç:** Scraper geliştirmeden önce Dolap.com'un teknik altyapısını, URL yapısını, sayfa yapılarını ve anti-bot korumalarını haritalamak.

---

## 1. Genel Mimari

| Özellik | Detay |
|---------|-------|
| **Domain** | `dolap.com` |
| **Sahiplik** | Trendyol (Dolap, Trendyol'un ikinci el moda platformu) |
| **CDN / WAF** | Cloudflare (WAF + DDoS Protection) |
| **Görsel CDN** | `dolap.dsmcdn.com` (Trendyol DSM CDN), `cdn.dolap.com` |
| **Rendering** | SPA (Single Page Application) — Kategori ve arama sayfaları JS ile yükleniyor |
| **SSR/Hybrid** | Ürün detay sayfaları kısmi SSR (fetch_webpage ile erişilebilir) |
| **Mobil Uygulama** | iOS (Apple Store) + Android (Google Play) — `app.adjust.com` deep link'leri |

---

## 2. robots.txt Analizi

**URL:** `https://dolap.com/robots.txt`

```
User-agent: *
Disallow: /kullanici-sozlesmesi
Disallow: /cdn-cgi/
Sitemap: https://dolap.com/static/sitemap.xml
```

**Yorum:**
- Sadece kullanıcı sözleşmesi ve Cloudflare internal path'i yasak
- Ürün sayfaları, kategori sayfaları, profil sayfaları → **İZİN VERİLMİŞ**
- Rate limiting uygulanmıyorsa bile robots.txt'e saygı gösterilecek

---

## 3. Sitemap Analizi

**URL:** `https://dolap.com/static/sitemap.xml`

- **Format:** XML urlset
- **İçerik:** Marka landing page'leri (ör. `/barbie`, `/mango`, `/balenciaga`)
- **Priority:** 0.5 (tüm sayfalar eşit)
- **Not:** Bireysel ürün URL'leri sitemap'te **YOK** — sadece marka sayfaları

---

## 4. URL Yapıları

### 4.1 Ürün Detay Sayfası
```
https://dolap.com/urun/{marka-slug}-{renk}-{kategori-slug}-{durum-slug}-{kullanici-adi}-{numeric-id}
```

**Örnekler:**
- `dolap.com/urun/apple-bej-telefon-kilifi-yeni-etiketli-iphonelcase-442885461`
- `dolap.com/urun/apple-pembe-telefon-kilifi-yeni-etiketli-meefaksesuar1-391497444`
- `dolap.com/urun/diger-yesil-telefon-kilifi-yeni-etiketli-iphonelcase-442754384`

**Slug Yapısı:**
| Segment | Açıklama | Örnekler |
|---------|----------|----------|
| `marka-slug` | Marka adı küçük harf, tire ile | `apple`, `diger`, `zara` |
| `renk` | Renk adı Türkçe | `bej`, `pembe`, `siyah`, `seffaf`, `mavi` |
| `kategori-slug` | Ürün alt kategorisi | `telefon-kilifi`, `kazak`, `mont` |
| `durum-slug` | Ürün durumu | `yeni-etiketli`, `az-kullanilmis` |
| `kullanici-adi` | Satıcı username | `iphonelcase`, `meefaksesuar1` |
| `numeric-id` | Benzersiz ürün ID | `442885461` (9+ haneli) |

### 4.2 Satıcı Profil Sayfası
```
https://dolap.com/profil/{username}
```
**Örnek:** `dolap.com/profil/iphonelcase`

### 4.3 Kategori Sayfası
```
https://dolap.com/{kategori-slug}
```
**Örnekler:** `dolap.com/kazak`, `dolap.com/mont`, `dolap.com/elbise`

**⚠️ DİKKAT:** Kategori sayfaları **marka listesi** döndürüyor (A-Z brand directory), ürün listesi DEĞİL. Ürünler JavaScript ile dinamik yükleniyor.

### 4.4 Marka + Kategori Filtresi
```
https://dolap.com/{kategori}?marka={marka-slug}
```
**Örnekler:**
- `dolap.com/spor-ayakkabi?marka=nike`
- `dolap.com/elbise?marka=koton`
- `dolap.com/bot?marka=harley-davidson`

### 4.5 Arama Sayfası
```
https://dolap.com/ara?q={query}
```
**Örnekler:**
- `dolap.com/ara?q=kazak`
- `dolap.com/ara?q=%23tesett%C3%BCr` (hashtag tesettür)

**⚠️ DİKKAT:** Arama sayfası da marka listesi döndürüyor (SPA, JS ile yükleniyor)

### 4.6 Marka Sayfası
```
https://dolap.com/{marka-slug}
```
**Örnekler:** `dolap.com/zara`, `dolap.com/nike`, `dolap.com/mango`

### 4.7 Görsel CDN
```
https://dolap.dsmcdn.com/dlp_{tarih_kodu}/product/org/{ana-kategori}/{alt-kategori}/{marka}_{image-id}.jpg
```
**Örnek:**
```
dolap.dsmcdn.com/dlp_230601_1/product/org/elektronik/telefon-kilifi/apple_1787295601.jpg
```

---

## 5. Sayfa Yapıları (HTML Elemanları)

### 5.1 Ürün Detay Sayfası

Gerçek ürün sayfasından (`/urun/apple-bej-telefon-kilifi-yeni-etiketli-iphonelcase-442885461`) elde edilen veri alanları:

| Alan | Değer Örneği | Erişilebilirlik |
|------|-------------|-----------------|
| **Marka** | Apple | ✅ HTML'de mevcut |
| **Kategori (breadcrumb)** | Ana Sayfa > Elektronik > Telefon Aksesuarı > Telefon Kılıfı > Apple | ✅ |
| **Fiyat** | 249 TL | ✅ |
| **Durum (condition)** | Yeni ve Etiketli | ✅ |
| **Kargo** | Alıcı Öder / Alıcı Ödemeli Kargo | ✅ |
| **Beğeni sayısı** | 32 Beğeni | ✅ |
| **Yorum sayısı** | 0 Yorum (Yorumlar (0)) | ✅ |
| **Renk** | Bej (renk swatch'ı ile) | ✅ |
| **Açıklama** | İphone simli magsafeli kılıf... | ✅ |
| **Satıcı adı** | iphonelcase | ✅ |
| **Satıcı ilan sayısı** | (1221) | ✅ |
| **Satıcı profil linki** | /profil/iphonelcase | ✅ |
| **Ürün görselleri** | 7 adet (carousel) | ✅ |
| **Benzer ürünler** | BENZER ÜRÜNLER bölümü | ✅ |
| **Teklif Ver** butonu | TEKLİF VER | ✅ (aktifse satışta) |
| **Satın Al** butonu | SATIN AL | ✅ (aktifse satışta) |
| **Ödeme seçenekleri** | Kredi kartı, 9 taksit | ✅ |
| **İndirimli fiyat** | 299 TL → 249 TL (orijinal → indirimli) | ✅ (varsa) |
| **Beden** | 4XL / 48 (giyim ürünlerinde) | ✅ (varsa) |

### 5.2 Satıcı Profil Sayfası

`/profil/iphonelcase` sayfasından elde edilen veri:

| Alan | Değer Örneği |
|------|-------------|
| **Username** | @Iphonelcase |
| **Aktif ürün sayısı** | 249 Ürün |
| **Toplam ilan sayısı** | (1221) — parantez içinde, satılmışlar dahil |
| **Sıralama** | Akıllı Sıralama |
| **Pagination** | 1, 2, 3, 4, 5, ..., 14 (Next butonu) |
| **Ürün kartları** | Her ürün: marka, kategori, fiyat, beğeni, yorum, durum, görsel |

**Filtre Sidebar'ı (çok değerli!):**

| Filtre | Değerler |
|--------|---------|
| **KATEGORİ** | Ağaç yapısı: Elektronik (249) > Telefon Aksesuarı (247) > Telefon Kılıfı (247) |
| **MARKA** | Apple (177), Diğer (72) |
| **FİYAT** | 50-100 (8), 100-150 (28), 150-200 (12), 200-300 (181), 300-500 (20) |
| **RENK** | Şeffaf (55), Siyah (47), Gri (22), Beyaz (19), Mor (14), + 17 renk daha |
| **DURUM** | Yeni & Etiketli (245), Az Kullanılmış (4) |

### 5.3 Ürün Kartı Yapısı (Listing'lerde)

Ana sayfa, profil ve benzer ürünler bölümlerinde görünen ürün kartı:

```
[Satıcı adı (ilan sayısı)]  →  satıcı profili linki
[Ürün görseli]
[Durum badge]  →  "Yeni & Etiketli" / "Az Kullanılmış"
[Marka][Kategori]
[Fiyat] TL
[Beğeni sayısı] Beğeni
[Yorum sayısı] Yorum  →  ürün detay linki
[Beğen butonu] (like1.png / like2.png)
[Takip et butonu] (follow.png)
```

---

## 6. Anti-Bot Korumaları

### 6.1 Cloudflare WAF
- **Tüm curl/requests istekleri** → HTTP 403 (Blocked)
- Cloudflare "Attention Required" sayfası döner
- Browser fingerprinting aktif
- Cookie kontrolü aktif (`Please enable cookies` mesajı)

### 6.2 Etkileri
| Yöntem | Sonuç |
|--------|-------|
| `curl` ile doğrudan istek | ❌ 403 Forbidden |
| `requests` kütüphanesi | ❌ 403 Forbidden (beklenen) |
| `requests` + fake headers | ❌ 403 Forbidden |
| `/api/*` endpoint'leri | ❌ 403 Forbidden |
| Selenium (gerçek browser) | ✅ Beklenen çalışma yöntemi |
| fetch_webpage tool | ✅ Çalışıyor (browser-like erişim) |

### 6.3 Keşfedilen API Endpoint Patternleri
```
/api/product/{id}          → 403 (var ama korumalı)
/rest/product/{id}         → 403 (var ama korumalı)
public-mdc.dolap.com/*     → DNS çözümlenemedi
```

---

## 7. Scraping Stratejisi (Karar)

### 7.1 Zorunlu Araç: Selenium + BeautifulSoup

Cloudflare WAF nedeniyle **Selenium zorunlu**. `requests` kütüphanesi tek başına kullanılamaz.

### 7.2 Veri Toplama Akışı

```
┌─────────────────────────────────────────────────┐
│  1. Selenium ile kategori sayfası aç             │
│     dolap.com/{kategori}                         │
│     → JS render'ı bekle (WebDriverWait)          │
│     → Ürün kartlarından URL'leri çıkar           │
│     → Pagination ile sonraki sayfalara geç       │
├─────────────────────────────────────────────────┤
│  2. Selenium ile her ürün detay sayfasını aç     │
│     dolap.com/urun/{slug}-{id}                   │
│     → BS4 ile parse et                           │
│     → Tüm veri alanlarını çıkar                  │
│     → rate limit: 1.5-3.5s arası bekleme         │
├─────────────────────────────────────────────────┤
│  3. 7 gün sonra aynı ürünleri tekrar kontrol     │
│     → "Satıldı" durumu kontrol et                │
│     → sold_within_7_days label'ı oluştur         │
└─────────────────────────────────────────────────┘
```

### 7.3 Alternatif Veri Kaynağı: Satıcı Profil Sayfaları

Satıcı profil sayfaları SSR benzeri davranıyor ve zengin veri sağlıyor:
- Ürün listesi + pagination
- Kategori, marka, fiyat, renk, durum filtreleri (sayılarla birlikte)
- Ürün kartları (tüm temel bilgiler)

**Kullanım:** Belirli satıcıların tüm ürünlerini toplamak için kullanılabilir.

---

## 8. Hedef Kategoriler

`configs/scraping.yaml`'dan:

| # | Kategori | URL |
|---|----------|-----|
| 1 | Kazak | `dolap.com/kazak` |
| 2 | Elbise | `dolap.com/elbise` |
| 3 | Mont | `dolap.com/mont` |
| 4 | Çizme | `dolap.com/cizme` |
| 5 | Bot | `dolap.com/bot` |
| 6 | Kol Çantası | `dolap.com/kol-cantasi` |
| 7 | Spor Ayakkabı | `dolap.com/spor-ayakkabi` |
| 8 | Jean Pantolon | `dolap.com/jean-pantolon` |
| 9 | Gömlek | `dolap.com/gomlek` |
| 10 | Etek | `dolap.com/etek` |
| 11 | T-shirt | `dolap.com/tshirt` |
| 12 | Sweatshirt | `dolap.com/sweatshirt` |

---

## 9. Satıldı (Sold) Tespiti

### 9.1 Yaklaşım

"Satıldı" durumu tespit yöntemleri:

1. **Ürün sayfası erişilemezlik:** Satılan ürünler kaldırılabilir → 404/redirect
2. **"Satıldı" badge'i:** Ürün kartında veya detay sayfasında özel bir gösterge
3. **"SATIN AL" butonunun yokluğu:** Satılan ürünlerde buton deaktif olabilir
4. **Ana sayfa review bölümü:** Satılmış ürünlerin alıcı yorumları görünüyor

### 9.2 Labeling Stratejisi

```
T=0: Ürün URL'lerini topla ve detay bilgilerini kaydet
T=7 gün: Aynı ürün URL'lerini tekrar ziyaret et
  → Sayfa hâlâ aktif + SATIN AL butonu var → sold_within_7_days = 0
  → Sayfa 404 / redirect / "Satıldı" badge → sold_within_7_days = 1
```

---

## 10. Keşfedilen Önemli Sayfalar

| Sayfa | URL | Amaç |
|-------|-----|------|
| Markalar dizini | `dolap.com/markalar` | Tüm markaların listesi |
| Satıcı soruları | `dolap.com/satici-sorulari` | Platform kuralları |
| Alıcı soruları | `dolap.com/alici-sorulari` | Platform kuralları |
| Giriş yap | `dolap.com/giris` | Kimlik doğrulama |
| Hakkımızda | `dolap.com/hakkimizda` | İletişim bilgileri |
| Destek | `destek.dolap.com` | Yardım merkezi |

---

## 11. Bilinen Durum Değerleri (Condition)

HTML'den keşfedilen ürün durumları:
- **Yeni & Etiketli** (`yeni-etiketli`)
- **Az Kullanılmış** (`az-kullanilmis`)

Muhtemel ek değerler (configs/features.yaml'dan):
- Yeni (Etiketsiz) → `yeni`
- Çok Kullanılmış → `cok-kullanilmis`
- Defolu → `defolu`

---

## 12. Bilinen Renk Değerleri

Profil filtre sidebar'ından keşfedilen renkler (21 adet):
Şeffaf, Siyah, Gri, Beyaz, Mor, Taba, Turuncu, Pembe, Mavi, Gümüş, Bej, Kahverengi, Lacivert, Yeşil, Çok Renkli, Altın, Kiremit, Bakır, Lila, Antrasit, Pudra

---

## 13. Fiyat Aralıkları (Platform Tanımlı)

Filtre sidebar'ından:
- 50-100 TL
- 100-150 TL
- 150-200 TL
- 200-300 TL
- 300-500 TL

---

## 14. Sonraki Adımlar

1. **Phase 3:** Selenium tabanlı basic scraper prototipi
   - WebDriver setup (headless Chrome)
   - Cloudflare bypass doğrulama
   - Kategori sayfasından ürün URL çıkarma
   - Ürün detay sayfasından veri parsing
2. **Phase 4:** Rate limiting + error handling
3. **Phase 5:** Labeling pipeline (7 gün sonra re-check)
4. **Phase 6:** Full data collection (~3000+ ürün)
