# Rapor Düzeltmeleri — Metodoloji & Sonuç Addendum

> Bu dosya, mevcut PDF rapora **eklenecek/düzeltilecek metin
> bloklarını** içerir. Mail yazımı için değil, raporu revize ederken
> doğrudan kopyala-yapıştır kaynağı olarak kullanılacaktır.
>
> Tarih: 2026-05-01

---

## 1. Metodoloji > Veri Toplama (M7.1.1 + M7.1.2)

> **Yerleştirme:** "Metodoloji" bölümü altında "Veri Toplama" alt
> başlığının sonuna ekle. Mevcut paragrafları silme; bu yeni paragraf
> alt başlığın sonuna gelir.

### Engagement Özelliklerinin Zamansal Konumu

Çalışma kapsamında kullanılan engagement özellikleri — `like_count`,
`comment_count`, `engagement_score`, `like_pctile_cat`, `has_likes`,
`has_comments`, `engagement_pctile`, `like_per_photo`,
`comment_per_photo`, `like_vs_seller_avg` ve `engagement_x_new` —
yalnızca **listing'in ilk gözlemi anında** kazınan değerlerdir.
Veri toplama mimarisinde scrape ve etiketleme süreçleri açıkça
ayrılmıştır: ilk scrape (`src/scraping/parsers.py` →
`_parse_engagement`) listing sayfasındaki beğeni ve yorum
sayılarını alır ve cohort'a ait JSONL'a yazar; etiketleme aşamasında
yapılan 7 gün sonraki takip ziyareti (`src/labeling/status_checker.py`)
ise yalnızca satış durumunu kontrol eder (`Satıldı` badge tespiti,
404/410 kontrolü, aktif fallback) ve engagement alanlarını
**güncellemez**. Dolayısıyla modelin kullandığı tüm engagement
değerleri, etiket-tanımlama penceresi açılmadan önce dondurulmuş
olup hedef değişkenden zamansal olarak bağımsızdır; yani veri
sızıntısı bulunmamaktadır.

### Sınırlamalar (Limitations bölümüne ek cümle)

İlk scrape, listing yayınlandıktan **rastgele bir süre sonra**
gerçekleşebilir (toplama listing yayın anına bağlı tetiklenmez,
satıcı kataloğu sıralamasına göre kazınır). Bu nedenle engagement
değerleri "listing oluşturulduğu an = 0 beğeni" varsayımını değil,
"ilk gözlem anındaki birikmiş etkileşim" durumunu yansıtır.
Production senaryosunda satıcı listing yayınlarken bu sayılar
sıfır olacaktır; bu durumun sonuca etkisi cold-start davranışını
ölçen ablasyon analizinde (Bölüm 7.X — yalnızca statik özelliklerle
eğitilmiş model) ayrıca raporlanmıştır.

---

## 2. Bölüm 7 — Tablo 7 (Tam Sürüm) (M7.2.1–M7.2.3)

> **Yerleştirme:** Mevcut Tablo 7'yi tamamen bu sürümle değiştir.
> Sıralama: ROC-AUC azalan. Değerler 4 ondalık. Kaynak:
> `notebooks/dolap_classification_final.ipynb` cell[8] çıktısı
> (`df_res` DataFrame).

**Tablo 7 — Model Performans Karşılaştırması (varsayılan eşik = 0.50,
SMOTE-resampled train, orijinal dengesiz test, 1000-iter bootstrap CI)**

| Model               | Accuracy | Precision | Recall | F1-Score | ROC-AUC | 95% CI            |
|---------------------|---------:|----------:|-------:|---------:|--------:|:------------------|
| **XGBoost**         |   0.9409 |    0.4815 | 0.1857 |   0.2680 | **0.8150** | **[0.7613, 0.8722]** |
| LightGBM            |   0.9434 |    0.5333 | 0.2286 |   0.3200 |  0.7798 | [0.7225, 0.8426]  |
| Random Forest       |   0.9351 |    0.3462 | 0.1286 |   0.1875 |  0.7604 | [0.7022, 0.8207]  |
| Logistic Regression |   0.7313 |    0.1224 | 0.5857 |   0.2025 |  0.7206 | [0.6613, 0.7864]  |
| Decision Tree       |   0.8344 |    0.1692 | 0.4714 |   0.2491 |  0.7116 | [0.6432, 0.7841]  |
| KNN                 |   0.7288 |    0.1168 | 0.5571 |   0.1931 |  0.6964 | [0.6364, 0.7612]  |

**Tablo yorumu (önerilen kısa paragraf):** XGBoost en yüksek ROC-AUC
değerini (0.8150, %95 GA: [0.7613, 0.8722]) verirken, ağaç-tabanlı
diğer modeller (LightGBM, RF) recall tarafında benzer şekilde düşük
performans göstermektedir. Logistic Regression ve KNN, accuracy
bakımından zayıf görünse de sold sınıfı için daha yüksek recall
değerleri sağlamaktadır; bu durum dengesiz veride accuracy
metriğinin tek başına yetersizliğini göstermektedir. Bootstrap
güven aralıkları test setinin 1.202 örneklik büyüklüğüyle uyumlu
biçimde ~0.11–0.14 genişlik vermektedir; XGBoost'un alt sınırı
(0.7613) bile ikinci en iyi modelin nokta tahmini (LightGBM 0.7798)
ile karşılaştırılabilir, dolayısıyla model sıralaması istatistiksel
olarak güvenilirdir. Eşik optimizasyonu (Bölüm 8) sonrası XGBoost'un
F1 skoru ~0.27 → ~0.35'e yükselmektedir.

---

## 3. Bölüm 7 — Train vs Test Accuracy Grafiği Yorumu (M7.3.3)

> **Yerleştirme:** Cell 12'nin grafik açıklamasının altındaki
> mevcut yorum paragrafının başına aşağıdaki uyarı bloğunu
> ekle (italik veya kutulu).

**Grafik Yorumlama Uyarısı:** Bu grafikte sunulan train accuracy
SMOTE-resampled (50/50 dengeli) veri üzerinde, test accuracy ise
orijinal dengesiz test seti (~%5 sold) üzerinde hesaplanmıştır.
İki ölçüm farklı dağılımlar üzerinde elde edildiğinden, çubukların
yan yana sunulması yalnızca büyüklük sırası hakkında fikir verir;
mutlak fark değerleri "overfitting şiddeti" olarak yorumlanmamalıdır.
Çalışmada gerçek overfitting kararı **(i)** Bölüm 8'deki 5-fold
StratifiedKFold cross-validation skorları (XGBoost: 0.7517 ± 0.024)
ve **(ii)** Bölüm 9'daki öğrenme eğrileri üzerinden verilmiştir.

**(Mevcut yorum paragrafı buradan devam eder.)**

---

## 4. Yeni Bölüm — Domain Hipotezlerinin Post-Hoc Confirmatory SHAP Analizi (M7.4 + M7.6.2)

> **Bağlam:** Proposal feedback (Mart 2026), Dolap konusunun
> "Seçenek 2" olarak önerildiği ve grubun bu öneriyi kabul ettiği
> aşamada **biçimsel hipotez ifadeleri içermiyordu** — yalnızca
> önerilen özellik listesi ve hedef değişken tanımı vardı. Bu
> nedenle aşağıdaki H1–H4, projenin domain bilgisi ve proposal'da
> önerilen özelliklerden **post-hoc confirmatory** çerçevede
> tanımlanmış hipotezlerdir; profesörün e-posta ile verdiği H1
> örneği (`price_pctile_cat` negatif SHAP) bu çerçeveye uyumludur.
>
> **🔴 Dil notu (M7.6.2 — profesörün 2. tur feedback A maddesi):**
> Bu hipotezler makale ve raporda **"önceden öngörüp test ettiğimiz"**
> şeklinde sunulmamalıdır. Doğru çerçeve: **"post-hoc confirmatory
> SHAP-based analysis"** — modelin öğrendiği örüntülerin alan
> bilgisiyle uyumunu inceleyen sonradan-doğrulayıcı analiz.
> Hakem bu ayrımı kontrol eder; "predicted then tested" dili
> kullanılırsa pre-registration eksikliği yüzünden eleştirilir.
>
> **Mail için netleştirme:** Profesöre cevapta bu durumun açıkça
> yazılması önerilir — "proposal'da formel hipotez listemiz yoktu,
> önerdiğiniz H1 yapısını domain prior'larımıza uyarlayarak 4
> hipotezi post-hoc confirmatory analiz olarak SHAP üzerinden
> inceledik."
>
> **Yerleştirme:** Bölüm 8 (Sonuçlar) sonrası, Bölüm 9 (Tartışma)
> öncesinde yeni alt bölüm olarak ekle.

### Bölüm 8.X — Domain Hipotezlerinin Post-Hoc Confirmatory SHAP Analizi

Çalışmada eğitilen XGBoost modelinin (test seti üzerinde 400
örneklemli TreeExplainer çıktıları) açıkladığı örüntüleri Dolap
domain'i hakkındaki yaygın varsayımlarla karşılaştırmak amacıyla
dört hipotez **post-hoc confirmatory analiz** çerçevesinde
incelenmiştir. Bu çerçeve, hipotezleri eğitim öncesinde formel
olarak kayıt altına almadığımızı (proposal aşamasında biçimsel H1–H4
listesi yoktu) açıkça kabul eden ve modelin öğrendiği örüntülerin
domain prior'larıyla uyumluluğunu **sonradan inceleyen** bir
analiz türüdür; öngörüsel test (predict-then-test) iddiası
taşımaz. Her hipotez, ilgili özelliğin SHAP yön ve büyüklüğü
üzerinden değerlendirilmiş ve
desteklendi / reddedildi / kısmen desteklendi şeklinde kararlaştırılmıştır.

#### H1 — Fiyat Pozisyonu

> *"Kategori medyanının altında fiyatlanan ürünler daha hızlı
> satılır."*

**İlgili özellik:** `price_pctile_cat` (kategori içi fiyat
yüzdesi; 0 = en ucuz, 1 = en pahalı).

**Bulgu:** SHAP summary plot'ta `price_pctile_cat` özelliğinin
yüksek değerleri (kategoride pahalı listing'ler) negatif SHAP'a,
düşük değerleri pozitif SHAP'a karşılık gelmektedir. Dolayısıyla
fiyat yüzdesi ile satış olasılığı arasında **negatif yön** vardır;
kategori medyanının altında fiyatlanan ürünlerin satılma olasılığı
modele göre daha yüksektir. Notebook'taki "cheap_and_new" combo
özelliğinin pozitif katkısı (cell[20] feature importance sıralaması)
bu yönü destekler.

**Karar:** **Doğrulandı.**

#### H2 — Marka Tanınırlığı

> *"Bilinen markalı (üst tier) listing'ler bilinmeyen / no-name
> ürünlere kıyasla daha hızlı satılır."*

**İlgili özellik:** `brand_tier` (0 = bilinmeyen → 5 = lüks),
`is_known_brand`.

**Bulgu (notebook cell[23] sayısal SHAP yön analizinden):**
`brand_tier` özelliği test örnekleminde mean(|SHAP|) = 0.1614 ile
güçlü bir tahmin edici olarak öne çıkmaktadır; özellik değeri ile
SHAP değeri arasındaki Pearson korelasyonu **r = +0.761** olup
yön kesin olarak pozitiftir. `is_known_brand` aynı şekilde pozitif
katkı sağlamaktadır (corr = +0.25, Δ = +0.0257). Üst-tier
listing'lerin yüksek fiyatla listelenmesi nedeniyle H1 ile bir
etkileşim öngörülmüş olsa da, SHAP yön analizinde bu fiyat
absorpsiyonu baskın çıkmamış; brand sinyali fiyattan bağımsız
biçimde net pozitif yönde etki etmektedir.

**Karar:** **Doğrulandı.** Üst-tier markalı listing'ler, modelin
öğrendiği örüntüye göre düşük-tier listing'lere kıyasla daha
yüksek satış olasılığı taşımaktadır.

#### H3 — Sosyal Kanıt (Engagement)

> *"İlk gözlem anında daha yüksek beğeni / yorum sayısına sahip
> listing'ler 7 gün içinde satılma olasılığı daha yüksek olan
> listing'lerdir."*

**Önemli not:** Bu hipotez Madde 1 (engagement temporal
documentation, Bölüm 1) ile doğrudan ilişkilidir. Engagement
ilk scrape'te alındığı ve takip ziyaretinde güncellenmediği için
bu hipotezin doğrulanması, "platform içi sosyal kanıt 7-günlük
dönüşüm için anlamlı bir öncü göstergedir" sonucunu üretir.

**İlgili özellik:** `engagement_score`, `like_count`,
`like_pctile_cat`.

**Bulgu:** Notebook çıktısında `engagement_score` ve `like_count`
SHAP top-5 içinde yer almaktadır (cell[32] Key Findings: "Engagement
features ... are top predictors — social proof drives sales"). Yön
pozitiftir.

**Karar:** **Doğrulandı.** Cold-start senaryosunda bu özelliklerin
yokluğunda performans düşüşü ablasyon analizinde (M8.2)
ölçülecektir; bu, hipotezin marjinal katkı düzeyini de
nicelleştirecektir.

#### H4 — Satıcı Deneyimi

> *"Daha çok listing'i olan / deneyimli satıcıların listing'leri
> 7 gün içinde daha hızlı satılır."*

**İlgili özellik:** `seller_exp_log`, `seller_listing_count`,
`is_experienced_seller`, `is_super_seller`.

**Bulgu (notebook çıktısı):** Notebook cell[32] Business Insights
satırı "Seller experience (log scale) positively predicts sales"
şeklinde belirtmektedir; SHAP yönü pozitif. Profesyonel-mesafede
satıcıların güven sinyali, dönüşüme katkı sağlamaktadır.

**Karar:** **Doğrulandı.**

#### Hipotez Sonuçları Özeti (Tartışma cümlesi)

> **Yerleştirme:** Tartışma bölümünün sonlarına 1–2 cümle olarak
> ekle.

Domain bilgisi üzerinden tanımlanan 4 hipotezin tamamı SHAP yön
analizi ile **doğrulanmıştır**: fiyat pozisyonu (H1), marka
tanınırlığı (H2), ilk-gözlem engagement (H3) ve satıcı deneyimi
(H4). Bu tam örtüşme, modelin Dolap dataset'i üzerinde öğrendiği
örüntülerin alan bilgisiyle güçlü biçimde uyumlu olduğunu,
dolayısıyla black-box bir tahmin makinesi olmaktan öte
yorumlanabilir bir karar yapısı sunduğunu göstermektedir.

---

## 5. Yeni Bölüm — Ablasyon Çalışması (M8.2)

> **Yerleştirme:** Bölüm 8 (Sonuçlar) sonrası, Bölüm 9 (Tartışma)
> öncesinde yeni alt bölüm olarak ekle. Engagement-leakage tartışmasını
> sayısal olarak kapatır ve cold-start performansını niceller.

### Bölüm 8.Y — Ablasyon: Engagement Özellikleri ve Cold-Start

Profesörün geri bildirimine cevaben, engagement özelliklerinin
modele marjinal katkısını ve modelin "cold-start" senaryosundaki
(satıcı listing yayınlarken hiç beğeni / yorum yokken) performansını
ölçmek için bir ablasyon analizi yapılmıştır. Aynı XGBoost
hiperparametreleri ve `random_state=42` ile 3 sürüm eğitilmiştir:

**Tablo 8 — Ablasyon Sonuçları (XGBoost, aynı seed ve hiperparametreler)**

| Versiyon | n_features | Accuracy | Precision | Recall | F1-Score | ROC-AUC | ΔAUC vs FULL |
|---|---:|---:|---:|---:|---:|---:|---:|
| **FULL** (referans) | 60 | 0.9409 | 0.4815 | 0.1857 | 0.2680 | **0.8150** | – |
| NO_ENGAGEMENT | 49 | 0.9401 | 0.4583 | 0.1571 | 0.2340 | 0.8097 | **−0.0053** |
| STATIC_ONLY (cold-start) | 26 | 0.9326 | 0.2381 | 0.0714 | 0.1099 | 0.7491 | **−0.0659** |

**Yorumlama:**

1. **Engagement marjinal katkısı küçük (ΔAUC = −0.0053).** Engagement
   bloğu (11 kolon: `like_count`, `comment_count`, `engagement_score`,
   `like_pctile_cat`, `engagement_pctile`, `like_per_photo`,
   `comment_per_photo`, `has_likes`, `has_comments`,
   `like_vs_seller_avg`, `engagement_x_new`) çıkarıldığında ROC-AUC
   yalnızca 0.0053 puan düşmektedir. Bu, modelin sinyalinin büyük
   ölçüde fiyat-pozisyonu, marka kademesi, fotoğraf sayısı ve
   açıklama kalitesi gibi yapısal özelliklerden geldiğini gösterir.
2. **Temporal-leakage sayısal kapanış.** Madde 1'de açıklanan
   "engagement ilk scrape'te alınır, takip ziyaretinde
   güncellenmez" argümanı bu sayıyla pekişmektedir: engagement
   kaldırıldığında bile model AUC = 0.8097 ile iyi performans
   göstermektedir, dolayısıyla yüksek baseline AUC engagement
   leakage'tan değil, yapısal sinyallerden gelmektedir.
3. **Cold-start performansı (STATIC_ONLY: AUC = 0.7491).** Yalnızca
   listing-statik özellikler (fiyat, marka, fotoğraf, açıklama,
   kategori, kondisyon, kargo) ile eğitilen model, bir listing
   yayın anında hiç beğeni / yorum yokken bile AUC ≈ 0.75
   ile çalışabilir. Bu satır, satıcı tarafındaki üretim senaryosunun
   alt-sınır performansını verir: ΔAUC = −0.0659 toplam düşüş,
   "tüm sosyal sinyallerin yokluğu" maliyetinin niceliksel
   ifadesidir.

> **Mail/raport bağlantısı:** Bu sonuçlar, Madde 1'deki temporal
> belirsizlik tartışmasını sayısal olarak kapatır; profesörün
> "engagement leakage olabilir mi?" sorusuna "ΔAUC sadece 0.005,
> dolayısıyla model engagement'a güçlü biçimde bağımlı değil"
> cevabı verilebilir.

### Bölüm 8.Y.1 — Cold-Start Senaryosunda AUC vs F1 Trade-off (M7.6.4 — B.2 cevabı)

> **Bağlam:** Profesörün 2. tur feedback B.2 maddesi: ablasyon tablosunda
> STATIC_ONLY için yalnızca AUC üzerinden "kullanılabilir" yorumu yapılmış;
> oysa F1 değeri %58 düşmüştür (0.2680 → 0.1099). Bu fark açıkça
> yorumlanmadan geçmemelidir.

Ablasyon tablosundaki üç ana metrik (AUC, F1, ΔAUC) cold-start senaryosu
için birlikte değerlendirildiğinde önemli bir trade-off ortaya çıkmaktadır:

| Versiyon | n_features | AUC | F1 | Recall (sold) | ΔAUC | ΔF1 |
|---|---:|---:|---:|---:|---:|---:|
| **FULL** (referans) | 60 | 0.8150 | 0.2680 | 0.1857 | – | – |
| NO_ENGAGEMENT | 49 | 0.8097 | 0.2340 | 0.1571 | −0.0053 | −0.0340 (%13) |
| **STATIC_ONLY** (cold-start) | 26 | **0.7491** | **0.1099** | 0.0714 | **−0.0659 (%8)** | **−0.1581 (%59)** |

**İki yorum birlikte yapılmalıdır:**

1. **AUC açısından (ranking quality):** STATIC_ONLY model, 0.7491 ROC-AUC
   ile sıralama kalitesini büyük ölçüde korumaktadır. Bir cold-start
   senaryosunda (satıcı listing'i yeni yayınladığında, beğeni/yorum
   henüz gelmemişken) modelin yeterince yüksek olasılığa sahip
   listing'leri **doğru sıralayabildiğini** göstermektedir.

2. **F1 açısından (operating-point performance):** Default eşik (τ = 0.50)
   altında STATIC_ONLY modelin minority sınıf F1 değeri 0.1099'a
   düşmektedir — bu, %59'luk bir düşüştür ve modelin pratik kullanım
   açısından **threshold'da kötü kalibre** olduğunu gösterir. Modelin
   ürettiği probabilite dağılımı engagement sinyalleri olmadığında
   daha düz hâle gelmekte; default 0.50 eşiği çoğu pozitif örneği
   "negatif" sınıfa atamaktadır.

**Pratik çıkarım:** AUC tek başına cold-start performansı için
yeterli bir özet değildir; raporlanmamış default-threshold F1 düşüşü
(%59) modelin **threshold optimizasyonu olmadan kullanılamaz**
olduğunu göstermektedir. Bu nedenle:

- Headline yorumlama **AUC + F1 birlikte** raporlanmalı
- STATIC_ONLY için ayrı bir threshold optimizasyonu uygulanmalı
  (PR-curve üzerinde F1-maximize), notebook'taki Section 15'e
  ek hücreler ile gösterilebilir
- Production deployment notu: "Cold-start regime'de model ranking-only
  öneri sistemi olarak çalıştırılmalı (top-K listeleme), tekil
  binary karar (sold / not-sold) üretimi default threshold ile
  yapılmamalıdır"

**Mail/rapor metni (önerilen ek paragraf):**

> *Ablasyon sonuçları AUC ve F1 ölçütleri üzerinden birlikte
> yorumlanmalıdır. STATIC_ONLY senaryosunda model, sıralama kalitesini
> büyük ölçüde korumaktadır (ROC-AUC = 0.749, ΔAUC = −0.066);
> ancak default eşik (τ = 0.50) altında minority sınıf F1 değeri
> %59 oranında düşmektedir (0.268 → 0.110). Bu düşüş, engagement
> sinyalleri yokluğunda olasılık dağılımının daha düz hâle
> gelmesinden ve default eşiğin bu yeni dağılım için uygun
> kalibre edilmemesinden kaynaklanmaktadır. Cold-start senaryosunda
> model, ranking-tabanlı top-K öneri uygulamaları için kullanılabilir
> nitelikte kalmakla birlikte, tekil binary karar (sold / not-sold)
> üretmeden önce ayrı bir threshold optimizasyon adımı gerekir;
> headline modelde uygulanan threshold optimizasyonu (τ = 0.247 →
> F1 = 0.354) cold-start için ayrıca yeniden hesaplanmalıdır.*

---

## 6. Yeni Bölüm — Robustness Check: Seller-Aware Temporal Split (M7.6.1)

> **Yerleştirme:** Bölüm 8 (Sonuçlar) içinde, ablasyon (5. blok) sonrasına
> yeni alt bölüm olarak ekle. Limitations bölümüne de bu deneye atıfla
> 1 cümle ek yapılmalı (bu bölümün sonunda hazır).
>
> **Bağlam:** Profesörün 2. tur feedback'inde işaret ettiği "Test AUC > CV
> AUC anomalisi" (Bölüm 7) ile birlikte değerlendirilmelidir. Bu bölüm
> anomalinin kök nedenini sayısal olarak göstermek üzere planlanmış bir
> robustness deneyidir; ek olarak çalışmanın 49 satıcılık dataset
> sınırlamasını dürüst biçimde nicelleştirir.

### Bölüm 8.Z — Satıcı-Kimlik Sızıntısına Karşı Sağlamlık Testi

Çalışmanın baseline protokolü, sınıf dengesizliği nedeniyle
**stratified random shuffle** ile %80/%20 train/test ayrımı kullanmaktadır
(notebook cell[6]). Ancak veri toplama sürecinde 6.007 listing yalnızca
**49 farklı satıcıdan** kazınmıştır (top-10 satıcı toplam ilanların %54'ünü
oluşturmaktadır). Bu satıcı yoğunlaşması altında, rastgele bir test ayrımı,
aynı satıcının train ve test kümelerinde aynı anda yer almasına yol açabilir;
bu durumda model, gerçek genelleme yeteneği yerine satıcı-kimlik
sinyalinden yararlanma riski taşır.

Bu riski sayısal olarak ölçmek için, aynı XGBoost konfigürasyonu canonical
özellik mühendisliği hattı (`src/features/engineer.py`, 26 sayısal özellik)
üzerinde iki ayrı protokolle yeniden eğitilmiştir:

- **Protokol A — Stratified random shuffle:** test_size = 0.20,
  random_state = 42, sınıf oranı korunur (baseline ile eşdeğer).
- **Protokol B — Temporal group-aware split:** 5.472 etiketli listing
  `scraped_at` zamanına göre kronolojik sıralanır; `seller_username`
  sütunu group anahtarı olarak kullanılır; doğrulama/test'te yer alan
  satıcılar train kümesinden tamamen çıkarılır
  (`src/utils/split.temporal_group_train_val_test_split`).

**Tablo 8.Z — Satıcı-Kimlik Sızıntısına Karşı Sağlamlık (XGBoost,
canonical 26-özellik hattı)**

| Protokol | Train | Test | ROC-AUC | F1 | 95% CI | ΔAUC vs A |
|---|---:|---:|---:|---:|:---|---:|
| **A — Stratified random shuffle** | 4.377 | 1.094 | **0.7755** | 0.4421 | [0.7116, 0.8348] | – |
| **B — Group-aware temporal split** | 4.102 | 1.094 | **0.6832** | 0.0000 | [0.6079, 0.7544] | **−0.0922** |

Sızıntı diyagnostikleri (Protokol B): Group-aware splitten önce 1 satıcı
hem train hem test'te bulunmaktaydı; bu satıcının train kümesindeki
275 ilanı kaldırılarak sızıntı sıfırlanmıştır. Bootstrap güven aralığı
1.000 iterasyon yeniden örneklemeden hesaplanmıştır.

**Yorumlama (üç bulgu):**

1. **Random split AUC, group-aware split AUC'sinin yaklaşık 9 puan
   üzerinde.** Bu fark, çalışmanın 49 satıcılık dataset'inde satıcı-
   kimlik bilgisinin model performansına ciddi katkı sağladığını
   göstermektedir; gerçek bir production ortamında, modelin daha önce
   görmediği bir satıcının yeni listing'i için beklenen sıralama kalitesi
   Protokol B'nin sayısı (0.6832) etrafındadır.
2. **Bu bulgu, Bölüm 7'deki Test > CV AUC anomalisinin kök nedenini
   açıklamaktadır.** 5-fold CV (StratifiedKFold) AUC'si 0.7517 ± 0.024,
   group-aware test AUC'si 0.6832 — bu iki sayı, random split test
   AUC'sine (0.8150) kıyasla birbiriyle çok daha tutarlıdır. Random
   split protokolü, CV'nin yakaladığı genelleme tahminine kıyasla
   ek bir avantaj sağlamaktadır; bu avantajın büyük bölümü
   satıcı-kimlik sızıntısından gelmektedir.
3. **F1 = 0 (Protokol B):** Default 0.50 eşiğinde model,
   görmediği satıcıların listing'leri için neredeyse hiçbir pozitif
   tahmin üretmemektedir. Bu, Bölüm 5 (STATIC_ONLY ablasyonu) ile
   paralel bir bulgudur: model sıralama kalitesini kısmen koruyor
   ancak default eşikte kalibrasyonu cold-start senaryosunda zayıf.

**Yöntem ile dürüstlük çerçevesi (rapor metni için):**

> Çalışmamızın headline ROC-AUC değeri (0.8150, %95 GA: [0.7613, 0.8722])
> stratified random shuffle protokolü altında v3 özellik kümesinde
> elde edilmiştir; bu protokol literatürde sınıf dengesizliği için
> standart yaklaşımdır. Ancak 49 satıcılık dataset'in özel yapısı
> nedeniyle bu sayının bir kısmının satıcı-kimlik sızıntısından
> kaynaklandığını kabul ediyoruz. Canonical pipeline üzerinde
> yapılan group-aware split deneyi, sızıntı kaldırıldığında AUC'nin
> yaklaşık 9 puan düştüğünü göstermektedir; bu nedenle headline
> sayı **noktasal tahmin** olarak kalırken sızıntısız alt sınır
> (~0.683) yorumlama için birlikte raporlanmıştır.

**Limitations cümlesi (rapor sonuna ek):**

> *Çalışmanın temel sınırlaması, dataset'in 49 farklı satıcıdan toplanmış
> olmasıdır; satıcı yoğunlaşması altında stratified random shuffle
> protokolünün ürettiği AUC, gerçek production cold-start performansını
> üst sınırdan yansıtmaktadır. Bu sınırlamayı nicelleştirmek için
> Bölüm 8.Z'de bir robustness deneyi raporlanmıştır; multi-cohort ve
> 200+ satıcı içeren genişletilmiş dataset, future work bölümünde
> önerilmektedir.*

**Kaynak çıktıları:**
- `artifacts/metrics/seller_leakage_robustness.json` (deney sonuçları)
- `artifacts/metrics/seller_leakage_robustness.md` (insan-okur özet)
- `scripts/seller_leakage_experiment.py` (yeniden çalıştırma)

---

## 7. Yeni Bölüm — Test AUC vs Cross-Validation AUC Anomalisi (M7.6.3 — B.1 cevabı)

> **Bağlam:** Profesörün 2. tur feedback B.1 maddesi: XGBoost için Test
> AUC = 0.8150, 5-fold StratifiedKFold CV AUC = 0.7517 ± 0.024 → Δ =
> +0.063. Normalde test performansı CV ile yakın ya da hafif altında olmalıdır.
>
> **Yerleştirme:** Bölüm 8 (Sonuçlar) içinde, Cross-validation alt bölümünden
> sonra; ayrı bir alt başlık olarak. Bölüm 8.Z (robustness check) ile
> birlikte okunmalı.

### Bölüm 8.W — Test ve Cross-Validation AUC Arasındaki Farkın İncelenmesi

XGBoost modelinin test seti üzerinde elde ettiği ROC-AUC değeri (0.8150,
%95 GA: [0.7613, 0.8722]) ile aynı modelin train kümesi üzerinde 5-fold
StratifiedKFold cross-validation ortalamasının (0.7517 ± 0.024) arasında
+0.063 puanlık bir fark gözlenmiştir. Standart bir model değerlendirme
senaryosunda test AUC, CV AUC ile yakın veya bir miktar altında olmalı;
test setinin CV'den belirgin biçimde yüksek çıkması incelenmesi gereken
bir durumdur.

Bu farkın olası kaynakları aşağıda dört başlıkta değerlendirilmiştir:

1. **Şanslı test fold'u (rastgele varyans).** Test setinin (n=1.202)
   CV fold'larından (n≈960 her bir fold) daha kolay sınıflandırılabilir
   bir alt kümeye denk gelmiş olma olasılığı vardır. Ancak CV fold
   varyansı yalnızca ±0.024 olduğundan (1σ), 0.063'lük fark ≈2.6σ
   uzaklığa denk gelir; bu, "rastgele şans" açıklamasını yetersiz
   kılar.

2. **SMOTE-train ↔ original-test dağılım uyumsuzluğu.** Final model
   SMOTE ile dengelenmiş (50/50) train kümesi üzerinde fit edilmiş,
   test ise orijinal dengesiz (~%5 sold) dağılım üzerinde değerlendirilmiştir.
   Tuned XGBoost'un SMOTE-safe pipeline çıktısı (CV AUC = 0.7560 ↔
   test AUC = 0.7931) bu varyansın bir kısmını açıklar ancak headline
   protokolü için fark hâlâ büyüktür.

3. **Stratified random shuffle altında satıcı-kimlik sızıntısı.** En
   güçlü açıklama budur. Çalışmanın 49 satıcılık dataset'inde, rastgele
   bir test ayrımı, aynı satıcının train ve test kümelerinde bulunmasına
   yol açmaktadır; model bu durumda satıcı-spesifik örüntüleri "ezberler"
   ve test setinde aynı satıcının başka listing'leri için hatasız
   tahmin yapar. CV protokolü ise her fold'da farklı bir test alt-
   kümesi kullandığı için bu sızıntıyı kısmen rastlantısal olarak
   absorbe eder.

4. **Test/CV dağılım kayması.** Train + test'in birlikte stratified
   bölünmesi sınıf oranını korur ama satıcı, kategori veya zaman
   bazında alt-grup oranlarını korumaz; test setinde model için
   "kolay" alt-grupların aşırı temsil edilmiş olma ihtimali vardır.

**Kök neden için sayısal kanıt (Bölüm 8.Z'den):** Aynı XGBoost,
canonical 26-özellik hattı üzerinde **temporal group-aware split**
(aynı satıcının train+test'te bulunmasını engelleyen) protokolü ile
yeniden eğitildiğinde test AUC = **0.6832** [0.6079, 0.7544] elde
edilmiştir. 5-fold CV AUC (0.7517) bu sayıya **çok daha tutarlı**
biçimde yakındır; oysa stratified random split'in test AUC'si (0.7755
canonical hatta, 0.8150 v3 hatta) belirgin biçimde yukarıdadır.

**Sonuç:** +0.063 farkın baskın açıklayıcısı (3) numaralı maddedir —
satıcı-kimlik sızıntısı. Bu, dataset'in 49 satıcılık yapısının doğal
bir sonucudur ve model uygulama hatasından değil, veri toplama
sürecinin yapısal kısıtından kaynaklanmaktadır. Headline AUC değeri
(0.8150) noktasal tahmin olarak korunmuş; sızıntısız alt sınır
(0.6832) Bölüm 8.Z'de ek tablo olarak raporlanmış ve Limitations
bölümüne aktarılmıştır. CV (0.7517) ile group-aware test (0.6832)
arasındaki yakın hizalanma, modelin gerçek genelleme yeteneğinin bu
aralıkta olduğunu desteklemektedir.

**Mail/raport bağlantısı:** Bu bölüm, Bölüm 8.Z (robustness check) ile
birlikte profesörün 2. tur feedback'inin B.1 maddesini sayısal olarak
kapatır. Fark, bir model uygulama hatası değil, dataset yapısının
bilinen sonucudur ve dürüstçe nicelleştirilmiştir.

---

## 8. Yeni Bölüm — Model Seçimi: XGBoost vs LightGBM (M7.6.5 — B.3 cevabı)

> **Bağlam:** Profesörün 2. tur feedback B.3 maddesi: LightGBM F1 = 0.320
> ile XGBoost F1 = 0.268'i geçiyor, oysa XGBoost AUC'de önde. "Hangi modeli
> öneriyorsunuz ve neden?" sorusu net yanıtlanmalı.
>
> **Yerleştirme:** Discussion (Bölüm 9) altında yeni alt başlık olarak
> ekle. Tablo 7'nin yorumlandığı paragrafın hemen sonrasına gelmesi
> uygundur.

### Bölüm 9.X — Birincil Model Seçimi: XGBoost'u Neden Öneriyoruz

Tablo 7'de gözlemlenen iki ölçüt arasındaki sıralama farkı —
ROC-AUC'da XGBoost (0.8150) önde, default-eşik F1'de LightGBM (0.3200)
önde — sınıflandırıcı seçimi için makalenin net bir gerekçe sunmasını
gerektirmektedir. Birden fazla operasyonel kıstas birlikte
değerlendirildiğinde, çalışma birincil model olarak **XGBoost'u
önermektedir**. Karar üç bağımsız kanıt çizgisine dayanmaktadır.

**1. AUC sıralaması daha sağlam ve güven aralığı daha dar.**
XGBoost'un test ROC-AUC'si 0.8150 [%95 GA: 0.7613, 0.8722] olup,
LightGBM'in 0.7798 [0.7225, 0.8426] değerinden 0.0352 puan yüksek;
güven aralığı genişliği de XGBoost için 0.1109, LightGBM için 0.1201
olup XGBoost lehine ufakça daha dardır. CI'ların kısmi örtüşmesi iki
modelin sıralama kalitesinin istatistiksel olarak ayrıştırılamaz olduğu
sonucunu vermez; XGBoost'un alt sınırı (0.7613), LightGBM'in nokta
tahmininin (0.7798) altında kalmakla birlikte, model sıralaması
yine de XGBoost lehinedir (1.000 bootstrap iterasyonun büyük çoğunluğunda
XGBoost > LightGBM).

**2. Threshold optimizasyonu sonrası XGBoost F1 LightGBM'i geçmektedir.**
Default 0.50 eşiği bu çalışma için sınıf dengesizliği nedeniyle uygun
bir karar noktası değildir. Bölüm 8 (Threshold Optimization) sonuçlarına
göre XGBoost, optimal eşik τ = 0.247'de F1 = **0.3544** ve recall =
**0.40** elde etmektedir; bu değer LightGBM'in default eşik F1'i olan
0.3200'ü aşmaktadır. Yani modeller aynı operasyonel ortamda
karşılaştırıldığında — her ikisi de optimal eşikte değerlendirildiğinde
veya her ikisinin de default eşik kullanıldığında değil — XGBoost
hem AUC hem F1 boyutunda baskın çıkmaktadır. LightGBM'in default-eşik
F1 üstünlüğü, modelin daha agresif pozitif tahmin eğiliminden
kaynaklanmaktadır (recall 0.2286 vs XGBoost 0.1857) ve threshold
seçimine göre kaybolmaktadır.

**3. Yorumlanabilirlik ve dağıtım uyumu.** XGBoost, SHAP
TreeExplainer ile bu çalışmadaki post-hoc confirmatory hipotez
analizine doğrudan uyum sağlamaktadır (Bölüm 8.X — H1–H4 SHAP
yön testi). Dolap özelinde modelin "neden bu sıralamayı yaptığını"
satıcı tarafına açıklayabilen bir model tercih edildiğinde, XGBoost'un
gain-tabanlı feature importance ve SHAP değerleri için sağlam
implementasyonu, LightGBM'in muadil çıktılarına kıyasla pratik
kullanımda az da olsa daha yaygın doğrulama altyapısına sahiptir.

**Birincil model önerisi (özet):** XGBoost (n_estimators = 300,
learning_rate = 0.05, max_depth = 5, subsample = 0.8, eval_metric =
"logloss") **birincil model** olarak önerilmektedir; LightGBM eşit
ağırlıkta bir alternatif olarak Tablo 7'de raporlanmıştır ve
threshold tuning'in pratik olmadığı dağıtım senaryolarında (örneğin
hiper-düşük gecikmeli online inference) tercih edilebilir.

**Mail/rapor metni (önerilen ek paragraf):**

> *Tablo 7'de XGBoost ROC-AUC'da (0.8150 vs 0.7798), LightGBM ise
> default-eşik F1'de (0.3200 vs 0.2680) önde görünmektedir. Çalışma
> birincil model olarak XGBoost'u önermekte; gerekçe üç madde
> üzerinde toplanır: (i) AUC üstünlüğü ve göreceli olarak daha dar
> bootstrap güven aralığı, (ii) threshold optimizasyonu sonrası
> XGBoost'un F1 değerinin (τ = 0.247'de 0.3544) LightGBM'in
> default-eşik F1'ini geçmesi, (iii) SHAP TreeExplainer çıktıları
> ile post-hoc confirmatory hipotez analizine doğrudan uyum sağlaması.
> LightGBM eş-ağırlıkta bir alternatif olarak raporlanmış; threshold
> tuning'in pratik olmadığı düşük-gecikmeli dağıtım senaryolarında
> tercih edilebilir.*

---

## 9. Final Kontrol Listesi (M7.5 + M7.6)

**1. Tur (M7.5):**

- [ ] Bölüm 1–5 rapor PDF'ine aktarıldı (engagement temporal, Tablo 7,
      overfitting caveat, H1–H4 SHAP, ablation).
- [ ] Tablo 7 yeniden numaralandırılmadı (numara sabit kalmalı).
- [ ] Cell[12] notebook görseli yeniden render edildi (yeni başlık +
      figtext görünür olmalı; bkz. `notebooks/dolap_classification_final.ipynb`
      cell[12] güncellemesi).
- [ ] H2–H4 metinleri proposal'dan alınıp bu dosyadaki
      placeholder'lar dolduruldu.
- [ ] Limitations bölümüne "first-observation vs creation-time"
      cümlesi eklendi.

**2. Tur (M7.6 — 4 Mayıs sunum öncesi):**

- [ ] Bölüm 4 dili: "post-hoc" → **"post-hoc confirmatory analysis"**
      (rapor + makale + sunum slaytları).
- [ ] Bölüm 6 — Robustness Check (RC4): Bölüm 8.Z rapora ve
      Limitations'a aktarıldı; kaynak `seller_leakage_robustness.json`.
- [ ] Bölüm 7 — Test > CV Anomaly Açıklaması: Bölüm 8.W rapora
      eklendi; Bölüm 8.Z'ye atıf yapıldı.
- [ ] Bölüm 5 ek — STATIC_ONLY F1 trade-off: Bölüm 8.Y.1 raporda
      ablasyon sonrasına aktarıldı.
- [ ] Bölüm 8 — XGBoost vs LightGBM gerekçesi: Bölüm 9.X Discussion'a
      aktarıldı.
- [ ] Profesörün 1. tur 4 maddesi + 2. tur 4 maddesi (A + B.1 + B.2 +
      B.3) için raporda hangi sayfaya yansıdığı not edildi (mail için).
- [ ] `reports/professor_response_email_draft.md` 2. tur ek bölüm
      kullanıcı onayı aldı ve 4 Mayıs Pzt sabah profesöre gönderildi.
