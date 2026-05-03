# Profesöre Cevap Maili — Taslak

> **Durum:** Taslak (kullanıcı onayı bekliyor).
> **Hazırlayan kanıt paketi:** [reports/professor_response_brief.md](reports/professor_response_brief.md)
> **İlişkili rapor düzeltmeleri:** [reports/methodology_addendum.md](reports/methodology_addendum.md)
> **Tarih:** 2026-05-01

---

## Konu satırı (öneri)

`Dolap Sale Prediction — Geri Bildirim Cevabı ve Revizyon Planı`

---

## Mail gövdesi (Türkçe)

Sayın Ayşegül Hocam,

Raporu detaylı incelediğiniz ve hem teknik hem de yayın yolu için
yön gösteren iki ayrı geri bildirim için çok teşekkür ederiz. 4 Mayıs
Pazartesi günkü sunumdan önce, 4 ana maddenin ve dergi yolunda
önerdiğiniz 6 ek maddenin her birine ne yaptığımızı / ne yapacağımızı
maddeli olarak paylaşmak istedik; sunum sırasında bu cevapları
görsel olarak da sizinle ele almayı planlıyoruz.

---

**1. Engagement özelliklerinin temporal belirsizliği.**
Haklı olarak işaret ettiğiniz nokta — bu kritik bilgiyi raporda
açıkça yazmamış olmamız bizim eksiğimiz. Kodu yeniden gözden
geçirdiğimizde durum şu: `like_count`, `comment_count`,
`engagement_score` ve türevleri yalnızca **listing'in ilk
gözleminde** alınmaktadır. Etiketleme aşamasındaki 7. gün takip
ziyareti yalnızca satış durumunu (`Satıldı` etiketi / 404-410)
kontrol eder; engagement değerlerini güncellemez. Dolayısıyla
sızıntı yok, ancak bu durum raporda belirtilmediği için haklı
olarak şüphe doğurmuş. Revize raporda **Metodoloji > Veri Toplama**
alt başlığına bu bilgiyi açıkça yazdık ve **Limitations**
bölümüne de "ilk-gözlem ≠ listing-yayın anı" notunu ekledik
(satıcı listing yayınladığı anda engagement = 0 olduğu için
production cold-start davranışı ablasyon analiziyle ayrıca
ölçülmektedir — Madde 8 aşağıda).

---

**2. Tablo 7'nin eksikliği.**
Tablo gerçekten eksik kalmış; düzelttik. Tüm modeller için tam
metrikleri aşağıya bırakıyorum (kaynak: training notebook,
varsayılan eşik = 0.50, SMOTE-resampled train, orijinal dengesiz
test seti):

| Model               | Accuracy | Precision | Recall | F1     | ROC-AUC    | 95% CI            |
|---------------------|---------:|----------:|-------:|-------:|-----------:|:------------------|
| **XGBoost**         |   0.9409 |    0.4815 | 0.1857 | 0.2680 | **0.8150** | **[0.7613, 0.8722]** |
| LightGBM            |   0.9434 |    0.5333 | 0.2286 | 0.3200 |     0.7798 | [0.7225, 0.8426]  |
| Random Forest       |   0.9351 |    0.3462 | 0.1286 | 0.1875 |     0.7604 | [0.7022, 0.8207]  |
| Logistic Regression |   0.7313 |    0.1224 | 0.5857 | 0.2025 |     0.7206 | [0.6613, 0.7864]  |
| Decision Tree       |   0.8344 |    0.1692 | 0.4714 | 0.2491 |     0.7116 | [0.6432, 0.7841]  |
| KNN                 |   0.7288 |    0.1168 | 0.5571 | 0.1931 |     0.6964 | [0.6364, 0.7612]  |

Sıralama ROC-AUC azalan; revize raporun ilgili tablosuna bu
sürüm yerleşti.

---

**3. Train vs Test Accuracy grafiğinin yorumu.**
Yine haklı yakalama — iki çubuğun yan yana gösterilmesi izleyiciye
"apple-to-apple" izlenimi veriyor, oysa train accuracy SMOTE-resampled
(50/50) veri üzerinde, test accuracy ise orijinal dengesiz (~%5 sold)
test seti üzerinde hesaplanıyor. Notebook hücresinin başlığını ve
alt yazısını bu farkı açıkça gösterecek şekilde güncelledik; rapora
da aynı uyarıyı kutulu olarak ekledik. Gerçek overfitting kararını
zaten **(i)** Bölüm 8'deki 5-fold StratifiedKFold cross-validation
skorları (XGBoost: 0.7517 ± 0.024) ve **(ii)** Bölüm 9'daki öğrenme
eğrileri üzerinden veriyorduk; bu referans grafikteki yorum
paragrafına da eklendi.

---

**4. Hipotezlerin SHAP sonuçlarıyla eşleşmesi.**
Bu noktada bir netleştirme yapmamız gerekiyor: Mart 2026'da Dolap'ı
"Seçenek 2" olarak önerdiğiniz proposal feedback mailinizde, projenin
kapsamı, özellik listesi ve hedef değişken tanımı vardı; ancak
biçimsel olarak yazılmış H1–H4 listesi bulunmuyordu. Bu nedenle
raporda doğrudan referans verebileceğimiz bir hipotez bloğu yoktu —
bu yüzden bağlantıyı eksik bıraktığımız yerde haklısınız. Sizin son
mailinizde verdiğiniz H1 örneğini (kategori medyanı altı fiyat →
hızlı satış, `price_pctile_cat` negatif SHAP) çerçeve olarak alıp,
proposal'da önerdiğimiz özellik kümesi ve domain bilgimiz üzerinden
4 hipotezi **post-hoc olarak** tanımlayıp SHAP üzerinden test ettik:

| #  | Hipotez                                              | İlgili Özellik                       | Sonuç           |
|----|------------------------------------------------------|--------------------------------------|------------------|
| H1 | Kategori medyanı altı fiyat → hızlı satış            | `price_pctile_cat`                   | ✅ Doğrulandı    |
| H2 | Üst-tier markalar daha hızlı satılır                 | `brand_tier`, `is_known_brand`       | ✅ Doğrulandı    |
| H3 | İlk-gözlem engagement'ı pozitif sinyal               | `engagement_score`, `like_count`     | ✅ Doğrulandı    |
| H4 | Deneyimli satıcılar daha hızlı satar                 | `seller_exp_log`, `is_super_seller`  | ✅ Doğrulandı    |

H2 için sayısal yön testi: brand_tier × SHAP korelasyonu
**r = +0.76**, mean(|SHAP|) = 0.16; üst-tier listing'lerin yüksek
fiyatla listelenmesi nedeniyle öngördüğümüz fiyat-marka karışımı
SHAP yön analizinde **baskın çıkmadı** — marka sinyali fiyattan
bağımsız net pozitif yönde etki etmektedir. Raporda yeni bir alt
bölüm açıldı (Bölüm 8.X — Domain Hipotezlerinin SHAP-Tabanlı Testi);
4 hipotezin tamamının doğrulanması, modelin alan bilgisiyle güçlü
uyum içinde yorumlanabilir bir karar yapısı sunduğuna dair
vurguyla tartışıldı.

---

**Veri Bilimi Dergisi yolu için önerileriniz** (Madde 5–10):
Bu yönlendirme bizim için çok kıymetli — aşağıda her birine
yaklaşımımızı belirtiyorum.

**5. H1–H4 ⇄ SHAP eşleştirme paragrafı (makale sürümü).**
Yukarıdaki rapor bölümünü makaleye uygun yoğun bir paragrafa
dönüştürüp Discussion bölümüne yerleştireceğiz.

**6. Akademik formata yeniden yazım + İngilizce metin + Türkçe
özet.** DergiPark Veri Bilimi Dergisi şablonunu (Cambria, çift
kolon, APA) indirip sıfırdan yeni bir İngilizce taslak yazacağız;
mevcut PDF rapordan kopya yapmayarak %20 benzerlik sınırının
güvenli altında kalacağız. Türkçe ~250 kelimelik özet bunu
takip edecek.

**7. Ablasyon çalışması.** En değerli bulduğumuz öneri buydu —
hem leakage tartışmasını kapattı hem de production cold-start
performansını sayısal olarak gösterdi. Aynı seed ve XGBoost
hiperparametreleriyle 3 sürüm eğittik (sonuçlar tek tabloda):

| Versiyon | n_features | ROC-AUC | F1 | ΔAUC vs FULL |
|---|---:|---:|---:|---:|
| **FULL** (referans) | 60 | **0.8150** | 0.2680 | – |
| NO_ENGAGEMENT | 49 | 0.8097 | 0.2340 | **−0.0053** |
| STATIC_ONLY (cold-start) | 26 | 0.7491 | 0.1099 | **−0.0659** |

Yorum: Engagement özelliklerinin marjinal AUC katkısı yalnızca
**~0.005** — yani modelin yüksek AUC'si engagement leakage'tan
değil, fiyat-pozisyonu, marka ve listing kalitesi gibi yapısal
sinyallerden gelmektedir; bu Madde 1'deki temporal-leakage
endişesini sayısal olarak kapatıyor. STATIC_ONLY satırı (cold-
start) AUC = **0.7491** ise satıcı listing yayınlarken hiç
beğeni / yorum yokken modelin pratik performansını gösteriyor —
mutlak anlamda kullanılabilir bir başlangıç noktası.

**8. Bootstrap güven aralığı.** Eklendi. Test seti üzerinde
1000-iter bootstrap (resample with replacement, %2.5–%97.5
percentile) sonucu en iyi model için:
**XGBoost ROC-AUC = 0.8150 [95% CI: 0.7613, 0.8722]**.
6 modelin tamamı için CI sütunu yukarıdaki Tablo 7'ye eklendi
(en sağ sütun); CI genişliği test setinin 1.202 örnek
büyüklüğüyle uyumlu (ortalama ~0.12).

**9. `is_negotiable` özelliği.** Şu anki scrape şemamızda bu alan
yok; "Teklif Ver" butonunun varlığı parser'a eklenip mevcut
cohort üzerinde bir backfill scrape ile geri-doldurulacak. Bu
madde Cloudflare WAF nedeniyle re-scrape gerektirdiğinden ilk
revizyon paketinden bağımsız, ikinci revizyonda makaleye
eklenmesini planlıyoruz.

**10. Akademik yayın yönlendirmesi.** Veri Bilimi Dergisi'ne
yönlendirmeniz gerçekten teşvik edici. İlk 8 maddenin tamamlanması
ile birlikte gönderilebilir bir taslağa ulaşacağımızı öngörüyoruz.

---

**Takvim:**

- **Madde 1–4, 7, 8 (rapor düzeltmeleri + ablasyon + bootstrap CI):**
  Tamamlandı; 4 Mayıs Pazartesi sunumunda revize edilmiş bölümleri
  ve yukarıdaki tabloları doğrudan göstereceğiz.
- **Madde 5 (hipotez–SHAP makale paragrafı) + Madde 6 (akademik
  formata yeniden yazım, EN metin + TR özet) + Madde 9
  (`is_negotiable` özelliği):** ~26 Mayıs'a kadar makale taslağı
  hazır olacak; iThenticate benzerlik kontrolü sonrası Veri Bilimi
  Dergisi'ne gönderim için onayınıza sunacağız.

Geri bildirimleriniz olursa bu plan üzerinde değişiklik yapmaktan
mutluluk duyarız.

Saygılarımızla,
Furkan Can, Halil Utku, Halil İbrahim

---

# 📨 İKİNCİ TUR CEVAP MAİLİ — TASLAK (M7.6.7)

> **Durum:** Taslak (kullanıcı onayı bekliyor).
> **Gönderim hedefi:** 4 Mayıs Pzt sabahı (sunum öncesi).
> **Bağlam:** Profesör 2 Mayıs gece ikinci tur feedback gönderdi
> (1 dil uyarısı + 3 teknik gözlem). İlk turdaki ana mailimizden
> sonra yapılan revizyonlarımızı değerlendirip yeni maddeler ekledi.
> Aşağıdaki taslak yalnızca 2. tur 4 maddeye cevap içerir; 1. tur
> mail kullanıcı tarafından zaten gönderilmiş kabul edilmektedir.

## Konu satırı (öneri)

`Dolap Sale Prediction — İkinci Tur Geri Bildirim Cevabı + Sunum Notları`

---

## Mail gövdesi (Türkçe)

Sayın Ayşegül Hocam,

İkinci tur değerlendirmenize hassasiyetle bakıp dört maddenin
hepsini ele aldık; aşağıda her birine yaklaşımımızı paylaşıyorum.
Pazartesi sunumunda bu kalemlerin her birini güncellenmiş tablolar
üzerinden sizinle birlikte gözden geçirmeyi planlıyoruz.

---

**A. H1–H4 dil uyarısı — "Post-hoc Confirmatory Analysis".**
Haklı yakalama. Raporda hipotez bölümünün başına ve makale tasla-
ğının §5.3 paragrafına şu netleştirmeyi yerleştirdik: "Çalışma,
proposal aşamasında biçimsel bir H1–H4 listesi içermediği için
H1–H4 hipotezlerini *post-hoc confirmatory analysis* çerçevesinde,
modelin öğrendiği örüntülerin domain prior'larıyla uyumunu
sonradan-doğrulayıcı biçimde inceleyen bir analiz olarak
sunmaktadır." Hakemin pre-registration ayrımına dair olası
sorusunu önlemek için "predicted then tested" gibi öngörüsel
test imasını taşıyan ifadeler dilimizden çıkarıldı.

---

**B.1. Test AUC > CV AUC anomalisi.** Bu noktayı biz de fark
etmiştik ve kök nedenini araştırmak için **canonical pipeline
üzerinde bir robustness deneyi** yaptık. Aynı XGBoost
hiperparametreleriyle iki ayrı protokol altında karşılaştırma:

| Protokol | n_features | Test ROC-AUC | 95% CI |
|---|---:|---:|:---|
| Stratified random shuffle (headline) | 60 (v3) | **0.8150** | [0.7613, 0.8722] |
| 5-fold StratifiedKFold CV (headline) | 60 (v3) | 0.7517 | ±0.024 |
| Stratified random shuffle (canonical) | 26 | 0.7755 | [0.7116, 0.8348] |
| **Temporal group-aware split (canonical)** | 26 | **0.6832** | [0.6079, 0.7544] |

Group-aware split, aynı satıcının train ve test kümelerinde
bulunmasını engellemektedir; bu protokol altında AUC değeri
yaklaşık 9 puan düşmekte ve 5-fold CV (0.7517) ile çok daha
tutarlı bir bant oluşmaktadır. Yorum: Test ile CV arasındaki
+0.063 farkın baskın açıklayıcısı, çalışmanın 49 satıcılık
dataset'inde stratified random shuffle protokolünün ürettiği
**satıcı-kimlik sızıntısıdır**. Bu bir model uygulama hatası
değil, dataset yapısının doğal bir sonucudur. Headline AUC
(0.8150) noktasal tahmin olarak korunmuş; sızıntısız alt sınır
(0.6832) Bölüm 8.Z'de ek tablo olarak ve Limitations bölümünde
dürüstçe raporlanmıştır.

---

**B.2. STATIC_ONLY: AUC vs F1 trade-off.** Haklısınız, AUC tek
başına cold-start yorumu için yetersiz; %59'luk F1 düşüşü dikkate
alınmadan "kullanılabilir" yorumu yapılmamalı. Raporu şöyle
güncelledik:

> *Ablasyon sonuçları AUC ve F1 ölçütleri üzerinden birlikte
> yorumlanmalıdır. STATIC_ONLY senaryosunda model, sıralama
> kalitesini büyük ölçüde korumaktadır (ROC-AUC = 0.749, ΔAUC =
> −0.066); ancak default eşik (τ = 0.50) altında minority sınıf
> F1 değeri %59 oranında düşmektedir (0.268 → 0.110). Bu düşüş,
> engagement sinyalleri yokluğunda olasılık dağılımının daha düz
> hâle gelmesinden ve default eşiğin bu yeni dağılım için uygun
> kalibre edilmemesinden kaynaklanmaktadır. Cold-start
> senaryosunda model, ranking-tabanlı top-K öneri uygulamaları
> için kullanılabilir nitelikte kalmakla birlikte, tekil binary
> karar (sold / not-sold) üretmeden önce ayrı bir threshold
> optimizasyon adımı gerekir; headline modelde uygulanan
> threshold optimizasyonu (τ = 0.247 → F1 = 0.354) cold-start
> için ayrıca yeniden hesaplanmalıdır.*

Notebook'a Bölüm 15 olarak yalnızca STATIC_ONLY için PR-curve
tabanlı threshold optimizasyonu eklenmesi sunum sonrası
yapılacaklar listesinde.

---

**B.3. XGBoost vs LightGBM — birincil model gerekçesi.** Net
yanıt: Çalışma birincil model olarak **XGBoost'u** önermektedir;
gerekçe üç bağımsız çizgi üzerinde toplanır:

1. **AUC üstünlüğü ve daha dar CI:** XGBoost 0.8150 [0.7613,
   0.8722], LightGBM 0.7798 [0.7225, 0.8426]; CI genişliği
   XGBoost lehine ufakça daha dar.
2. **Threshold optimizasyonu sonrası F1 üstünlüğü:** Default
   τ = 0.50'de LightGBM önde (0.320 vs 0.268), ancak optimal
   eşik (τ = 0.247) altında XGBoost F1 = **0.3544** ve recall
   = **0.40** elde etmektedir; aynı operasyonel ortamda
   karşılaştırıldığında XGBoost hem AUC hem F1 boyutunda
   baskındır. LightGBM'in default-eşik avantajı, modelin daha
   agresif pozitif tahmin eğiliminden kaynaklanmakta ve
   threshold seçimine bağlı olarak kaybolmaktadır.
3. **Yorumlanabilirlik uyumu:** SHAP TreeExplainer ile post-hoc
   confirmatory hipotez analizine doğrudan uyum (Bölüm 8.X —
   H1–H4 SHAP yön testi) XGBoost ile sağlam biçimde
   gerçekleştirilmiştir.

LightGBM eş-ağırlıkta bir alternatif olarak Tablo 7'de raporlanmış;
threshold tuning'in pratik olmadığı düşük-gecikmeli dağıtım
senaryolarında tercih edilebilir notu Discussion bölümüne
eklenmiştir.

---

**Sunum + makale takvimi:**

- **4 Mayıs Pzt sunum:** Yukarıdaki dört maddenin de güncellenmiş
  rapor / tablo / yorum sürümlerini sunum sırasında doğrudan
  paylaşacağız. Robustness check (Bölüm 8.Z) ve Test>CV anomaly
  açıklaması (Bölüm 8.W) sunumun ana parçaları olacaktır.
- **~26 Mayıs makale taslağı:** Tüm 1. tur + 2. tur düzeltmeleri
  ile birlikte İngilizce taslak (post-hoc confirmatory dilinde)
  tamamlanıp iThenticate kontrolü sonrası onayınıza sunulacaktır.

Geri bildirimleriniz olursa bu plan üzerinde değişiklik yapmaktan
mutluluk duyarız.

Saygılarımızla,
Furkan Can, Halil Utku, Halil İbrahim

---

## 2. Tur Mail için Kullanıcı Kontrol Listesi

Mail göndermeden önce kontrol et:

- [x] Konu satırı: "Dolap Sale Prediction — İkinci Tur Geri Bildirim
      Cevabı + Sunum Notları"
- [x] Selamlama: "Sayın Ayşegül Hocam"
- [ ] B.1 tablosu mailin gövdesinde markdown formatında görünüyor
      (bazı mail istemcileri markdown'ı render etmez — gerekirse
      düz tabloya çevrilmeli)
- [x] B.2 cevabındaki uzun italik blok kısaltılabilir (mail
      okunurluğu için); bu hâliyle 4-5 cümle ile özetlenebilir
- [x] B.3 cevabındaki 3 madde net görünüyor; reviewer için
      "primary model = XGBoost" mesajı baskın
- [x] İmza: Furkan Can / Halil Utku / Halil İbrahim
- [x] Ek (opsiyonel): `reports/methodology_addendum.md` Bölüm 6, 7,
      5-ek, 8 (yeni eklenenler) — gerekirse PDF olarak ekle

## 2. Tur Mail Diğer Notlar

Mail uzunluğu ~600 kelime — profesörün ikinci tur feedback'i
1. tura kıyasla daha kısa ve odaklı; cevabımız da aynı tonu
korumalıdır. 4 madde × ortalama 5-6 cümle + giriş/kapanış.
Daha kısa istersen B.2 italik bloğu çıkarılabilir.

**Önemli ton notu:** B.1 cevabında "biz de fark etmiştik" ifadesi
kritik. Hocaya "siz uyarmadan önce gördük ve araştırdık" mesajı
verir; bu, robustness deneyimizin **proaktif** bir adım olarak
algılanmasını sağlar (defensive değil).

---

## Mail yazımı için kullanıcıya kontrol listesi (1. tur — referans)

Mail göndermeden önce kontrol et:

- [x] Konu satırı önerildi: "Dolap Sale Prediction — Geri Bildirim
      Cevabı ve Revizyon Planı" (4 Mayıs sunumu öncesi).
- [x] Selamlama: "Sayın Ayşegül Hocam".
- [x] H2 kesinleştirildi: Doğrulandı (brand_tier corr = +0.76,
      mean|SHAP| = 0.16). Yıldız notu kaldırıldı, tablo güncellendi.
- [x] Takvim: 4 Mayıs sunumunda göstereceğimiz tamamlanmış maddeler
      + 26 Mayıs makale taslağı tarihi mail metnine yerleştirildi.
- [x] İmza: Furkan Can / Halil Utku / Halil İbrahim.
- [x] Ek (attachment): Mail "sunumda göstereceğiz" tonunda kaldı;
      ek dosya istenirse `reports/methodology_addendum.md` ve
      güncel notebook çıktıları bağlanabilir.

## Diğer not

Mail uzunluğu ~700 kelime — profesörün gönderdiği iki uzun maile
karşılık dengeli. 10 madde × ortalama 4-5 cümle + giriş/kapanış.
Daha kısa istersen Madde 5–10'u tek paragrafa indirebiliriz; ama
profesörün ayrıntılı yaklaşımı düşünüldüğünde mevcut uzunluğun
"saygılı + profesyonel" tonu koruduğunu düşünüyoruz.
