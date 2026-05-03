# Demo Detaylı Script — F (Furkan), 5 dakika

> **Kim okuyacak**: Furkan, sahnede projektör önünde.
> **Süre**: 5 dk (0:00–5:00) + 15 sn §17 köprü (16:00–16:15)
> **Tab durumu**: Tab 1 = `http://127.0.0.1:5000/`, Tab 2 = HTML hazır arkada.
> **Bu metin sahnede okunabilir formatta yazıldı** — kelime kelime ezber gerekmez, ama her preset için "ne tıklayacağım, ne söyleyeceğim, ne bekliyorum" sıralı şekilde yazılı.

---

## Sahne öncesi son kontrol (T-2 dk, F)

1. Tab 1'de `127.0.0.1:5000` açık → 4 grupta 10 buton render oluyor
2. Sayfayı **bir kez yenile** (Cmd+R) → cache temiz
3. Threshold slider 0.50'de mi kontrol et — değilse "Reset" tıkla
4. Filter kutusunu **boş bırak** — başlangıçta tüm featurelar görünür
5. Sayfa zoom %100 (Cmd+0) — projektör DPI bozar zoom seviyesi farklıysa
6. Demo server logu Tab 3'te görünür kalsın (debug için)

---

## 0:00 — 0:30 · Açılış (30 sn)

**Yapacağın**: Sahneye çık, projektör Tab 1'i göstersin. Header satırını parmakla işaret et.

**Söyle**:
> "Merhaba. Halil Utku, Halil İbrahim ve ben — bu sunumda **Dolap.com için 7 günlük satış tahmin modelimizi** göstereceğiz."
>
> *(1 sn duraksa)*
>
> "Hocamızın yönergesine göre EDA'yı tekrar anlatmıyoruz; doğrudan **canlı demoyla başlayacağım**, ardından Halil Utku model kararlarını, Halil İbrahim de reviewer feedback'ini ve limitleri açıklayacak."
>
> *(Header'daki sayıları parmakla işaret et)*
>
> "Burada gördüğünüz sayılar: **60 özellikli XGBoost modeli, test ROC-AUC 0.8150, %95 güven aralığı 0.76–0.87**. Şimdi modele 8 farklı senaryo göstereceğim."

---

## 0:30 — 1:00 · Preset 1: Tipik / Medyan İlan (30 sn)

**Yapacağın**:
1. Sayfada **"🟧 EDGE CASES"** grubuna scroll et
2. **"Tipik / medyan ilan"** butonuna tıkla → tüm 60 feature defaults'a doluyor
3. **"Predict"** butonuna bas
4. Probability gauge ~%2 dolacak (renk soluk)

**Beklenen sonuç**: P ≈ 0.023 (%2.3) → "NOT SOLD within 7 days"

**Söyle**:
> "İlk senaryo: dataset'in **tam medyanı**. 60 özelliğin hepsi medyan değerinde — ortalama bir Dolap ilanı."
>
> *(Predict bas, sonucu bekle)*
>
> "Sonuç: **%2.3** — yani modelimiz NOT SOLD diyor. Burada önemli bir nokta: **Dolap'ın gerçek satış oranı %5.8**. Yani ortalama bir ilan, ortalamanın altında satış olasılığına sahip. Bu başlı başına bir bulgu — platformun büyük kısmı yavaş satıyor."

→ Kısa duraksa, sayfayı yukarı scroll et (preset gruplarını göster).

---

## 1:00 — 1:30 · Preset 2: Hızlı satılan (30 sn)

**Yapacağın**:
1. **"🟢 STRONG"** grubuna scroll
2. **"Hızlı satılan (yüksek olasılık)"** butonuna tıkla
3. Predict bas → gauge dolacak (renk parlak yeşil/pembe)

**Beklenen sonuç**: P ≈ 0.959 (%95.9) → "SOLD within 7 days"

**Söyle**:
> "Şimdi tam tersini göstereyim — **gerçek bir satılmış ilan**, eğitim setinden alınmış."
>
> *(Predict bas)*
>
> "Sonuç: **%95.9 SOLD**. Aradaki fark **94 puan** — model gerçekten ayırt ediyor, rastgele tahmin etmiyor. Yüksek beğeni, kategori-altı fiyat, iyi marka, yeni etiket — hepsi pozitif sinyal aynı anda."

→ Sayfayı kaydır, Cold-start senaryosuna git.

---

## 1:30 — 2:15 · Preset 3: Cold-start (45 sn — kritik bölüm)

**Yapacağın**:
1. **"🟧 EDGE CASES"** grubuna git
2. **"Cold-start (henüz beğeni/yorum yok)"** butonuna tıkla
3. Predict bas

**Beklenen sonuç**: P ≈ 0.914 (%91.4) → "SOLD"

**Söyle**:
> "Üçüncü senaryo daha ilginç. **Cold-start ilan** — yeni yayınlanmış, henüz hiç beğeni almamış, yorum yok. Engagement sinyali sıfır."
>
> *(Predict bas, sonucu göster)*
>
> "Yine **%91 SOLD**. Bu çok önemli bir sonuç — çünkü **gerçek dünyada her yeni ilan başlangıçta cold-start'tır**. Modelimiz engagement bilgisi olmadan da tahmin yapabiliyor."
>
> *(Hafif vurguyla)*
>
> "Bu bulguyu reviewer feedback'inde de derinleştirdik. Halil Utku §15'te bu cold-start çalışmasını ablasyon analiziyle gösterecek — engagement çıkarıldığında bile model statik özelliklerle (fiyat, marka, fotoğraf, açıklama) çalışıyor."

→ Premium senaryosuna geç.

---

## 2:15 — 2:45 · Preset 4: Premium / Lüks Marka (30 sn)

**Yapacağın**:
1. **"🔥 PRICING"** grubunda **"Premium / lüks marka"** butonuna tıkla
2. Predict bas

**Beklenen sonuç**: P ≈ 0.945 (%94.5) → "SOLD"

**Söyle**:
> "Dördüncü senaryo — **premium marka**. brand_tier=4, is_known_brand=1, makul fiyat."
>
> *(Predict bas)*
>
> "Sonuç **%94.5**. Bu **H2 hipotezimizi** doğruluyor: önceden kayıtlı 'tanınmış markalar daha hızlı satılır' iddiası. Halil Utku §8'de SHAP analiziyle bunu nicelleştirecek — brand_tier mean SHAP korelasyonu **+0.76**, çok güçlü pozitif yön."

→ Hard-negative senaryosuna geç (model hatası).

---

## 2:45 — 3:30 · Preset 5: Hard-Negative (Model Yanılıyor) (45 sn — şeffaflık göstergesi)

**Yapacağın**:
1. **"🔴 ERRORS"** grubuna scroll
2. **"Model hatası: False Positive"** butonuna tıkla
3. Predict bas

**Beklenen sonuç**: P ≈ 0.84 (%84) → "SOLD" — **ama gerçekte satılmamış**

**Söyle (yavaş, vurgulu)**:
> "Beşinci senaryo özellikle önemli. Bu ilan **gerçekte satılmamış** — eğitim setinde NOT SOLD etiketi var."
>
> *(Predict bas, sonucu göster)*
>
> "Ama model **%84 SOLD** diyor. **Bu bir hata**. Modelin kör noktası — premium görünümlü, kalite skorları yüksek, ama bir nedenle satılmamış stale bir ilan."
>
> *(Sahnede mikrofona yaklaş, ağırbaşlı ton)*
>
> "Bu hatayı saklamak yerine **size kasıtlı gösteriyorum**. Çünkü modelin sınırlarını şeffaf raporlamak akademik dürüstlük gerektiriyor. Default eşikte precision **0.48**, yani 100 SOLD tahminden 48'i doğru — bu vakalar precision'ı düşüren tipik FP'lerden biri."
>
> "Halil Utku §11'de bu sayının nasıl iyileştirildiğini — F1-optimal eşik üzerinden — anlatacak."

→ Threshold slider'a geç.

---

## 3:30 — 4:15 · τ Slider Hikayesi (45 sn — interaktif)

**Yapacağın**:
1. Aynı **Hard-negative** preset hâlâ ekranda
2. Threshold slider'a git (default 0.50'de)
3. Slider'ı **yavaşça sola sürükle** → 0.247'ye getir
4. Quick-pick chip'lerden **"F1-optimal (0.247)"** tıkla (eğer slider zorlu ise)
5. Gauge'da **threshold marker** (kesik çizgi) sola hareket etmeli

**Beklenen sonuç**: Probability aynı kalır (%84), ama threshold marker pozisyonu değişir; bazı borderline preset'lerde label'ı flip edebilir.

**Söyle**:
> "Şimdi **threshold slider**'ı kullanacağım. Default değer 0.50 — yani %50'nin üstündeki olasılıklara SOLD diyoruz."
>
> *(Slider'ı sola sürükle, marker'ı işaret et)*
>
> "Bunu **0.247**'ye düşürdüğümde —"
>
> *(Slider stop)*
>
> "— işte gauge'daki kesik çizgi sola kaydı. Bu **F1-optimal eşik**, §11'de PR-eğrisi sweep'i ile bulduk."
>
> *(Hızlıca cold-start preset'ini tekrar aç)*

**Hızlı geçiş**: Cold-start preset'ini tekrar tıkla → P ≈ %91 görünür → marker hâlâ 0.247'de.

> "**Cold-start preset'ine geri döndüm**. Default eşikte de SOLD, optimal eşikte de SOLD. Ama daha önemli — **F1 metriği 0.268'den 0.354'e çıkıyor, %32 iyileşme**. Recall'u 0.19'dan 0.32'ye taşıyor."
>
> "**B.2 reviewer yorumunun cevabı tam burada**: aynı modeli yeniden eğitmeden, sadece eşiği oynayarak operasyonel davranış değişiyor. Halil Utku §11'de detayını gösterecek."

---

## 4:15 — 4:50 · Manuel Edit: Price Düşürme (35 sn — feature editing)

**Yapacağın**:
1. Filter kutusuna **"price"** yaz
2. price field'ı görünecek; mevcut değer ~150 TL
3. Field'ı temizle, **80** yaz
4. Predict bas

**Beklenen sonuç**: Probability hafif değişir (örn %15-20 → %25), büyük değil

**Söyle**:
> "Son olarak **manuel bir edit**: filter'a 'price' yazıyorum, field'ı buluyorum, mevcut 150 TL'yi **80 TL**'ye düşürüyorum."
>
> *(Predict bas)*
>
> "Olasılık az miktarda yükseldi. Neden büyük bir sıçrama yok? Çünkü **`price_log`, `price_pctile_cat`, `price_vs_brand_median`** gibi türetilmiş özellikler hâlâ medyan değerinde. Tek özellik değiştiğinde tüm türev özellikler tutarlı kalmıyor."
>
> *(Açıklama tonu)*
>
> "Bu yüzden **preset yaklaşımını tercih ettik**: gerçek bir eğitim satırından alınmış 60 özellik aynı anda set ediliyor, ilişkiler bozulmuyor. Demo'daki dramatik %2 ↔ %96 farkları o yüzden tutarlı."

---

## 4:50 — 5:00 · Geçiş: HU'ya devret (10 sn)

**Yapacağın**:
1. Sahne ortasına gel
2. Halil Utku'yu el hareketiyle işaret et
3. **Cmd+Tab** ile Tab 2'ye (HTML) geç
4. HTML açıldığında §1'in başında olmalı (kontrol et: önceden T-2 dk'da §1'e scroll edildi)

**Söyle**:
> "Modelin **nasıl** davrandığını gördünüz. Şimdi bu sayıların **neden** böyle çıktığını Halil Utku açıklayacak."
>
> *(El hareketiyle HU'yu sahneye davet et)*
>
> "Halil, sahne senin."

→ HU başlar, sen sahneden bir adım geri çekil ama mikrofon range'inde kal (köprü cümleleri için).

---

## 16:00 — 16:15 · §17 Köprü (15 sn — sen tekrar sahneye)

> §16 (HU) bittiğinde, F yine 15 sn için sahneye girer. HTML §17'de olmalı.

**Yapacağın**:
1. HTML §17 hücresinin **en altındaki print outputs**'una scroll et:
   ```
   [ok] pipeline saved : models/dolap_xgboost_pipeline.joblib
   [ok] schema saved   : models/feature_schema.json
   features        : 60
   headline AUC    : 0.815
   presets         : 10
   [self-test] sample probability(sold) = 0.xxxx
   ```
2. Bu satırları parmakla göster

**Söyle (kısa, hızlı)**:
> "Bir saniye — buraya kısaca değineyim. **§17, demo'nun arkasındaki export hücresi**. Az önce gördüğünüz `dolap_xgboost_pipeline.joblib` ve `feature_schema.json` dosyaları burada üretiliyor."
>
> *(Self-test satırını işaret et)*
>
> "Hücrenin sonunda bir **self-test** var: kaydettiğimiz modeli geri yükleyip ilk test satırı için tahmin yaparak sayı tutarsızlığı olmadığını doğruluyor. Yani **demo'da gördüğünüz canlı tahminler ile §16'daki ablation sayıları aynı pipeline'dan**."
>
> *(El hareketiyle Hİ'yi davet et)*
>
> "Halil İbrahim limitler ve sonraki adımları özetleyecek."

→ Sahneden çekil, Hİ devralır.

---

## Q&A bloğunda senin üzerine düşenler (17:15 — 20:00)

> Demo + altyapı + threshold/feature soruları F'in. Detay için → [`qa_cards.md`](qa_cards.md)

| Soru tipi | İlgili kart | 30 sn cevap çekirdeği |
|---|---|---|
| Cold-start nasıl çalışıyor? | Kart 2 | "STATIC_ONLY ablation, AUC 0.749, F1 default 0.110, optimal τ=0.18'de 0.215" |
| Hard cases ne? | Kart 9 | "Demo'da hard_negative_FP ve hard_positive_FN preset'lerini gösterdik" |
| τ neden 0.247? | Kart 13 | "PR-eğrisi sweep'inde F1 maksimum yapan değer; %32 iyileşme" |

---

## Yedek planı (sen başlatırsan)

| Sorun | F'nin yapacağı |
|---|---|
| Demo server bağlanmıyor | Tab 3 terminal'i göster, log oku, hızlı debug. Bağlanmıyorsa: "Bir saniye, fallback'e geçiyorum" → Tab 4 = notebook .ipynb dosyası, §17'den `run_preset("sold_high_conf")` çalıştır |
| Preset butonları görünmüyor | `grep -c '"id":' models/feature_schema.json` (Tab 3'te) → 10 değilse `git checkout HEAD -- models/feature_schema.json` → server restart |
| Probability hep aynı | Notebook §17 self-test satırını sahnede oku — "model bu satıra şu cevabı veriyor" diye |
| Tüm demo çöker | "Notebook'a geçiyorum" → HTML'de §16 ablation tablosunu sözlü oku, sayıları audience okusun, FALLBACK Tier-2 |

---

## Cep notu (sahnede ele alacaksan)

8 preset isim sırası, beklenen P:

```
1. Tipik / medyan ilan         %2.3   NOT SOLD
2. Hızlı satılan               %95.9  SOLD
3. Cold-start                  %91.4  SOLD
4. Premium / lüks marka        %94.5  SOLD
5. Hard-negative (FP hata)     %84    SOLD (yanlış!)
6. Threshold slider hikayesi   τ: 0.50→0.247
7. Manuel price edit           ~%15-20
8. HU'ya devret
```

Bu 8 adımı ezberlemen şart değil — sayfa scroll'u sırayla yapacak. Önemli olan **hangi preset'in beklenen sonucunu doğru bilmek** ki sahnede yanılınca ad-lib edebilirsin.
