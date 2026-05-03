---
type: "Türkçe Özet"
target_journal: "Veri Bilimi Dergisi"
word_target: "150–200 kelime"
keywords:
  - ikinci el e-ticaret
  - satış tahmini
  - SHAP
  - SMOTE
  - XGBoost
  - Dolap
---

> **Durum:** Taslak iskelet. Final yazımda bu dosyaya ~150-200
> kelimelik tek paragraflık özet yazılacak. Aşağıda yapı taşları
> verilmiştir; cümleler İngilizce abstract'tan **çeviri değil**,
> Türkçe akademik dilinde yeniden yazılacaktır (%20 benzerlik
> sınırı için bağımsız metin gerekli).

# Yapı taşları (final paragrafı bunlardan kuracağız)

1. **Bağlam ve motivasyon (1 cümle):** Dolap.com Türkiye'nin en büyük
   ikinci el moda platformudur; bir ilanın 7 gün içinde satılıp
   satılmayacağını tahmin eden bir model, satıcı tarafında fiyatlama
   aracı, platform tarafında sıralama sinyali sunabilir.

2. **Boşluk (1 cümle):** Bilgimiz dahilinde Dolap üzerinde herhangi
   bir kamuya açık ML çalışması bulunmamaktadır; mevcut literatür
   (Vinted, Depop, Mercari) farklı dil ve fiyat rejimlerine sahiptir.

3. **Veri (1-2 cümle):** Çalışmada Selenium tabanlı kohort scraping
   ile toplanmış ~6.000 ilan kullanılmıştır. Hedef değişken
   `sold_within_7_days`, ilanların 7 gün sonra yeniden ziyaret
   edilerek "Satıldı" rozetinin tespiti yoluyla doğal etiket olarak
   elde edilmiştir.

4. **Yöntem (1-2 cümle):** Fiyat-pozisyonu, marka kademesi,
   etkileşim, ilan kalitesi ve satıcı deneyimi bloklarından oluşan
   60 mühendislik özelliği üzerinde 6 sınıflandırıcı kıyaslanmış,
   sınıf dengesizliği için CV-içi SMOTE uygulanmış, yorumlanabilirlik
   için SHAP TreeExplainer kullanılmıştır.

5. **Sonuçlar (1-2 cümle):** XGBoost test seti üzerinde ROC-AUC =
   0.8150 [%95 GA: 0.7613, 0.8722] değerine ulaşmıştır. Engagement
   özelliklerinin çıkarıldığı ablasyon analizinde AUC düşüşü yalnızca
   0.0053 (NO_ENGAGEMENT: 0.8097), yalnızca listing-statik özelliklerle
   eğitilen cold-start sürümü ise AUC = 0.7491 vermektedir; bu, modelin
   sinyalinin büyük ölçüde fiyat pozisyonu, marka kademesi ve listing
   kalitesi gibi yapısal özelliklerden geldiğini göstermektedir.

6. **Katkı (1 cümle):** Çalışma, Dolap için ilk benchmark'ı,
   tekrarlanabilir veri toplama-etiketleme hattını ve SHAP-tabanlı
   hipotez testi çerçevesini sunmaktadır.

# Anahtar Kelimeler (final)

İkinci el e-ticaret; satış tahmini; XGBoost; SMOTE; SHAP;
yorumlanabilir makine öğrenmesi; Dolap.

# Yazım notları

- Cümleler **kısa ve teknik** olsun (Veri Bilimi Dergisi tarzı).
- "Bilgimiz dahilinde" ifadesini "novelty" sinyali olarak koruyalım.
- Sayısal sonuçlar (AUC, CI) ablation+CI notebook'u çalıştırıldıktan
  sonra final değerle güncellenecek.
