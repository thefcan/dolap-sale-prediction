# Furkan'ın Sunum Scripti — Detaylı

> **Toplam sahne süresi**: 5 dk demo + 15 sn §17 köprü + Q&A katılımı = ~6 dk + Q&A
> **Sorumluluk**: Live demo, §17 export köprüsü, demo/altyapı/threshold sorularına Q&A cevap
> **Cep notu**: [`script_demo_detailed.md`](script_demo_detailed.md) (preset-by-preset detay)

---

## 0:00 — 5:00 · LIVE DEMO

> Tam detay: [`script_demo_detailed.md`](script_demo_detailed.md). Bu dosya o blokun bir hızlı özetini içerir; sahnede o dosyayı okumalısın.

### Akış özeti (8 adım, 5 dk)

| Süre | Aksiyon | Beklenen P |
|---|---|---:|
| 0:00–0:30 | Açılış konuşması (60 feature, AUC 0.8150 vurgu) | — |
| 0:30–1:00 | Preset 1: Tipik / Medyan İlan | %2.3 |
| 1:00–1:30 | Preset 2: Hızlı satılan | %95.9 |
| 1:30–2:15 | Preset 3: Cold-start | %91.4 |
| 2:15–2:45 | Preset 4: Premium / Lüks Marka | %94.5 |
| 2:45–3:30 | Preset 5: Hard-Negative (model hatası) | %84 (yanlış!) |
| 3:30–4:15 | τ slider 0.50 → 0.247 | marker hareket |
| 4:15–4:50 | Manuel edit: price 150→80 | ~%15-20 |
| 4:50–5:00 | HU'ya devir | — |

### Açılış konuşması (kelime-kelime)

> "Merhaba. Halil Utku, Halil İbrahim ve ben — bu sunumda **Dolap.com için 7 günlük satış tahmin modelimizi** göstereceğiz. Hocamızın yönergesine göre EDA'yı tekrar anlatmıyoruz; doğrudan **canlı demoyla başlayacağım**, ardından Halil Utku model kararlarını, Halil İbrahim de reviewer feedback'ini ve limitleri açıklayacak.
>
> Burada gördüğünüz sayılar: **60 özellikli XGBoost modeli, test ROC-AUC 0.8150, %95 güven aralığı 0.76–0.87**. Şimdi modele 8 farklı senaryo göstereceğim."

### HU'ya devir cümlesi (kelime-kelime)

> "Modelin **nasıl** davrandığını gördünüz. Şimdi bu sayıların **neden** böyle çıktığını Halil Utku açıklayacak. Halil, sahne senin."

> *(Cmd+Tab → Tab 2 = HTML, §1'in başına scroll)*

---

## 5:00 — 16:00 · NOTEBOOK BLOĞU (sen sahnede DEĞİLSİN)

> HU + Hİ konuşur. Sen sahnenin bir tarafına çekilir, mikrofon range'inde kalırsın. Köprü cümlelerinde devreye girersin (sadece §17 köprüsü senin).
>
> **Bu süreçte yapacaklarınla:**
> 1. Demo Tab 1'i açık tut — donmasın
> 2. Audience'a bakma — HU/Hİ'yi destekleyici göz teması
> 3. Q&A'da çıkacak demo sorularını mental hazırlık (kart 2, 9, 13)

---

## 16:00 — 16:15 · §17 KÖPRÜ (sen tekrar sahneye, 15 sn)

> §16 sonu HU bitirdiğinde sen 15 sn'lik bir geçiş söyleyeceksin.

### Yapacağın

1. HU §16 sonunda dur cümlesi söyleyince ("Halil, devral" cümlesi yok — ekibe önceden söylendi: §16 bittiğinde HU "Demo'nun arkasındaki export hücresine kısaca Furkan değinecek" diyecek, sen sahneye gel)
2. HTML'de **§17 hücresinin print output**'a scroll et
3. Şu satırları parmakla işaret et:
   ```
   [ok] pipeline saved : models/dolap_xgboost_pipeline.joblib
   [ok] schema saved   : models/feature_schema.json
   features        : 60
   presets         : 10
   [self-test] sample probability(sold) = 0.xxxx
   ```

### Söyleyeceğin (kelime-kelime)

> "Bir saniye — buraya kısaca değineyim. **§17, demo'nun arkasındaki export hücresi**. Az önce gördüğünüz `dolap_xgboost_pipeline.joblib` ve `feature_schema.json` dosyaları burada üretiliyor.
>
> *(Self-test satırını işaret et)*
>
> Hücrenin sonunda bir **self-test** var: kaydettiğimiz modeli geri yükleyip ilk test satırı için tahmin yaparak sayı tutarsızlığı olmadığını doğruluyor. Yani **demo'da gördüğünüz canlı tahminler ile §16'daki ablation sayıları aynı pipeline'dan** — tutarlı hikaye.
>
> *(El hareketiyle Hİ'yi davet et)*
>
> Halil İbrahim limitler ve sonraki adımları özetleyecek."

→ Sahneden çekil. Hİ devralır.

---

## 16:15 — 17:15 · KAPANIŞ (sen sahnede DEĞİLSİN)

> Hİ konuşuyor. Sen Q&A'ya zihinsel hazırlık yap.

---

## 17:15 — 20:00 · Q&A

> 3 üye panel olarak. Sorular kime gelirse F/HU/Hİ'den uygun olan cevaplar. Senin alanın: **demo + altyapı + threshold + feature edit + hard cases**.

### Sana gelebilecek 3 ana soru (kart referansı)

#### Soru 1 — "Cold-start ilanlar için modeliniz nasıl çalışıyor?"

**Kart 2 referansı**. 30 sn cevap:

> "Cold-start preset'inde gördüğünüz gibi like=0, comment=0 — engagement sinyali yok. Ablasyon analizinde STATIC_ONLY (sadece 26 statik özellik) AUC=0.749 verdi. Default τ=0.50'de F1=0.110, F1-optimal τ=0.18'de F1=0.215'e çıkıyor. Yani engagement yokken bile statik özellikler — fiyat, marka, fotoğraf, açıklama — pozitif sınıfı tespit edecek bilgiyi taşıyor."

**Demo eşliği (eğer izin verirse)**: "İsterseniz demo'da gösterebilirim — cold-start preset, τ slider 0.18 — bu tam B.2 reviewer cevabı."

#### Soru 2 — "Modeliniz hangi örneklerde hata yapıyor?"

**Kart 9 referansı**. 30 sn cevap:

> "Demo'da iki preset'i kasıtlı gösterdik: **hard-negative FP** — premium görünümlü ama satılmamış stale ilan, model %84 SOLD diyor. **hard-positive FN** — cold-start anomali, gerçekte satılmış ama model %0.7 NOT SOLD diyor. İlk hata precision'ı düşürüyor (0.48), ikinci hata recall'u (0.19). Threshold optimization recall'u 0.32'ye taşıyor — yani daha az ilan kaçırıyoruz."

**Demo eşliği**: "Hard cases preset'lerini tekrar açabilirim — bunlar dataset'ten gerçek satırlar."

#### Soru 3 — "Threshold τ neden 0.247? Default 0.50 neden değil?"

**Kart 13 referansı**. 30 sn cevap:

> "PR-eğrisi sweep'inde F1 maksimum yapan eşik 0.247. Default 0.50 precision-favorlu — recall'u kaçırıyor. Bu marketplace'de pozitif sınıf nadir (%5.8), recall önemli. 0.247'de F1 0.268'den 0.354'e çıkıyor, %32 iyileşme. §11'de PR-eğrisi grafiği var, F1 vs τ sweep'i orada."

### Soru gelmezse (HU sinyal verirse devreye gir)

> HU "Sıkça merak edilen üç noktaya kendimiz değinelim" deyip Kart 1'i (B.1 anomaly) açarsa, sen sırada Kart 2 (cold-start) veya Kart 13 (threshold) için "Demo tarafından da bunu eklemek isterim" diye söze gir. Panel canlılığı için iyi.

---

## Sahne kuralları — F için

1. **Demo Tab 1'i sahne süresince kapatma** — "donar mı?" diye refresh tıklama, sayfa state'ini koru
2. **Sayıları gauge'dan oku** — ekran üstünde net görünüyor; ezberden sayı söyleme
3. **Tıklarken parmağı projeksiyon yönüne çevir** — audience hangi butona bastığını görsün
4. **Hata olur durumda "fallback" deme** — "1 saniye, başka bir vakaya bakalım" de, profesyonel ton
5. **Threshold slider takılırsa quick-pick chip** kullan ("F1-optimal" butonu)
6. **HU/Hİ konuşurken sahne ortasına geçme** — yan tarafta dur, mikrofona uzak değilsin

---

## Pre-prova kontrolü (T-1 saatte)

```bash
cd /Users/furkankarafil/dolap-sale-prediction
source .venv/bin/activate
python demo/demo_server.py &
sleep 3
curl -s http://127.0.0.1:5000/api/presets | python -c "import json,sys; print('preset count:', len(json.load(sys.stdin)))"
# Çıktı: preset count: 10  → OK
```

Tarayıcı:
- Cmd+R ile yenile, 10 buton görüyorum ✓
- "Hızlı satılan" tıkla → P %95-96 dönüyor mu? ✓
- τ slider 0.50→0.247 hareket ediyor mu? ✓
- Filter "price" yazınca filtreleme oluyor mu? ✓

HTML:
- `open notebooks/dolap_classification_final.html` → 17 section görünür ✓
- §1 başına scroll, §17 sonuna scroll → her ikisi de yükleniyor ✓
- Anchor'lar çalışıyor mu? → Cmd+F "Section 14" → direkt o bölüm açılıyor ✓

Bu 7 kontrol geçtiyse demo hazır.
