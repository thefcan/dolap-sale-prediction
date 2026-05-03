# Halil İbrahim'in Sunum Scripti — Detaylı

> **Toplam sahne süresi**: ~4 dk notebook bloğu + 1 dk kapanış + Q&A katılımı
> **Sorumluluk**: §7, §12, §15, kapanış (limitler + sonraki adım)
> **Pencere**: Tab 2 = `notebooks/dolap_classification_final.html`

---

## Sahne öncesi mental hazırlık (T-5 dk)

- HU §6 bitirince senin sıran. Sahne kenarında dur.
- Cep notu = bu dosya. Section başlıkları + söyleyeceğin metin + reviewer mapping tablo bilgisi.
- **Önemli**: §12 reviewer mapping, sunumun "akademik dürüstlük" mesajını taşır. Audience burada hocanın feedback'ine ne kadar saygılı yaklaştığımızı görmeli.

---

## 5:00 — 7:30 · §1, §2, §5, §6 (HU konuşur)

> Bu blokta sen sahnede değilsin. HU dataset/preprocess/model comparison/confusion matrix anlatıyor. Sahne kenarında bekle.

---

## 7:30 — 8:15 · §7 ROC & Precision-Recall Curves (45 sn)

### Yapacağın
- HU "Halil, ROC ve PR eğrileri" deyince sahne ortasına gel
- §7 başlığı — "ROC Curves & Precision-Recall Curves *(Beyond Template)*"
- İki grafik yan yana: solda ROC, sağda PR

### Söyleyeceğin (kelime-kelime)

> "Section 7: ROC ve Precision-Recall eğrileri.
>
> *(Sol grafiği işaret et)*
>
> ROC AUC için 5 model arasında **XGBoost ve LightGBM** ön planda — eğriler diagonal'den uzakta, sol-üst köşeye yakın.
>
> *(Sağ grafiğe geç)*
>
> Ama bizim problemde imbalance var, %5.8 pozitif sınıf. Bu durumda **ROC yanıltıcı olabilir** — true negative oranı zaten yüksek olduğundan AUC kolayca yüksek çıkar.
>
> *(Vurgu)*
>
> Asıl önemli olan **precision-recall eğrisi**. Rastgele tahminin baseline'ı %5.8 — yani PR-AUC'un anlam taşıması için bu seviyenin çok üstünde olması gerek. Modelimizin PR-AUC'u **bunu aşıyor**, XGBoost lider.
>
> Bu yüzden §11'de threshold optimization'ı **PR-eğrisi üzerinden** yaptık, F1-tabanlı. Halil Utku §11'de detaylandıracak."

→ HU'ya köprü.

> *(Köprü cümlesi)*
>
> "Tekrar Halil Utku'ya — best model deep dive."

→ HU §8'e scroll, konuşmaya başlar. Sen yan tarafa çekil.

---

## 8:15 — 11:45 · §8, §9, §10, §11 (HU konuşur)

> Bu blokta sen sahnede değilsin. HU sırayla §8 SHAP, §9 CV, §10 model selection, §11 hyperparameter + threshold anlatıyor (~3.5 dk). Sahne kenarında bekle.
>
> §11 sonunda HU senin için köprü cümlesi söyleyecek: "Reviewer feedback'inin tam haritasını Halil İbrahim çıkardı, §12'ye geçiyor." Sen sahne ortasına gel.

---

## 11:45 — 12:45 · §12 Reviewer Mapping (1 dk — KRİTİK akademik mesaj)

### Yapacağın
- HU §11 sonunda devir cümlesini söyleyince sahne ortasına gel
- §12 başlığı — "Key Takeaways"
- Aşağı scroll: **Reviewer Mapping tablosu** (1. tur 4 yorum + 2. tur 4 yorum, toplam 8 satır)
- Tablodaki "Reviewer Comment" sütunu ile "Notebook §" sütununu işaret et

### Söyleyeceğin (yavaş, akademik ton)

> "Section 12: **Key Takeaways ve Reviewer Mapping**.
>
> *(Tabloyu işaret et)*
>
> Bu tablo, hocamızın **iki tur** halinde verdiği toplam **8 yorum**u tek tek hangi notebook section'unda nasıl ele aldığımızı gösteriyor.
>
> *(Tablonun üst yarısını parmakla işaret et)*
>
> **Birinci tur**: dört yorum vardı.
>
> *(Sırayla hızlıca say)*
>
> Bootstrap güven aralığı eksikti — §13'te eklendi. Threshold optimization yoktu — §11'de yapıldı. Robustness check istendi — §14'te 4-bar grafiği ile yapıldı. Hipotezlerin SHAP ile doğrulanması istendi — §3'te hipotezler önceden kayıtlı, §8'de post-hoc confirmatory analiz yapıldı.
>
> *(Tablonun alt yarısını işaret et)*
>
> **İkinci tur**: dört yorum daha geldi. **A** — SHAP framework post-hoc framing — §3 hipotez kaydı + §8 dipnot. **B.1** — test AUC neden CV'den yüksek — §14'te az önce gördük. **B.2** — STATIC_ONLY F1 eksikti — §15'te birazdan göreceğiz. **B.3** — XGB vs LightGBM — §10'da Halil Utku üç gerekçe verdi.
>
> *(Sonuç tonu)*
>
> Toplam 8 yorum, 8 satır, hepsinin notebook karşılığı var. Detayı `methodology_addendum.md` Bölüm 8.A–8.D, 8.W, 8.Y.1, 8.Z, 9.X'te uzun formda yazılı — hocamızın mailine ek olarak gönderildi."

→ HU'ya köprü.

> *(Köprü cümlesi)*
>
> "Halil Utku bootstrap CI ve robustness check'ı detaylandıracak."

→ HU §13'e scroll, konuşmaya başlar. Sen yan tarafa çekil.

---

## 12:45 — 14:15 · §13, §14 (HU konuşur)

> Bu blokta sen sahnede değilsin. HU bootstrap CI ve **§14 RC4 anomaly açıklaması** (kritik bölüm) anlatıyor. Sahne kenarında bekle.
>
> §14 sonunda HU senin için köprü cümlesi söyleyecek: "Cold-start senaryosunu Halil İbrahim §15'te anlatacak." Sen sahne ortasına gel.

---

## 14:15 — 15:15 · §15 STATIC_ONLY F1 Sweep (1 dk — B.2 cevabı)

### Yapacağın
- HU §14 sonunda devir cümlesini söyleyince sahne ortasına gel
- §15 başlığı — "STATIC_ONLY Cold-Start: Threshold Optimisation"
- İki grafik: sol PR-eğrisi, sağ F1 vs τ sweep

### Söyleyeceğin (kelime-kelime)

> "Section 15: **cold-start senaryosu için threshold optimization**.
>
> *(Audience'a açıklayıcı ton)*
>
> Reviewer'ın **B.2 yorumu** STATIC_ONLY ablation üzerine. Cold-start ilanlar — yeni yayınlanmış, henüz beğeni almamış — engagement sinyali olmayan ilanlar. Furkan demoda bu durumu gösterdi.
>
> *(Sayıları söyle)*
>
> Engagement çıkarıldığında 26 statik özellik kalıyor. AUC **0.749** — düşmüş ama hâlâ rastgeleden çok daha iyi. Default τ=0.50'de **F1=0.110** — düşük.
>
> *(Sağ grafiğe işaret et)*
>
> Ama F1 vs τ sweep'inde, **τ=0.18'de F1 0.215'e çıkıyor — neredeyse iki katı**.
>
> *(Vurgu)*
>
> Yani cold-start için **ayrı eşik** kullanmak makul. Demo'da Furkan slider ile bu fikri canlı gösterdi. Production'da uygulanırsa, cold-start ilanlar için τ=0.18, normal ilanlar için τ=0.247 — bu **operasyonel öneri** olarak `methodology_addendum.md` Bölüm 8.Y.1'de yazılı.
>
> Bu hocamızın B.2 yorumuna cevap."

→ HU'ya köprü.

> *(Köprü cümlesi)*
>
> "Halil Utku ablation özetini kapatıyor."

→ HU §16'ya scroll, konuşmaya başlar. Sen yan tarafa çekil.

---

## 15:15 — 16:15 · §16, §17 (HU + F konuşur)

> Bu blokta sen sahnede değilsin. HU §16 ablation özeti, F §17 köprü.
>
> F §17 köprüsünü bitirince ("Halil İbrahim limitler ve sonraki adımları özetleyecek") sen sahne ortasına gel.

---

## 16:15 — 17:15 · KAPANIŞ: Limitler + Sonraki Adım (1 dk — kritik kapanış)

### Yapacağın
- F'in devir cümlesinden sonra sahne ortasına gel
- HTML §17'nin sonunda kal — başka bir şey scroll etme
- **Bu blok sözel** — slayt veya grafik kullanma, audience'la göz teması kur

### Söyleyeceğin (kelime-kelime, ağırbaşlı ton)

> "Teşekkürler Furkan.
>
> Sunumu **üç limit** kabul ederek kapatıyorum.
>
> *(Parmaklarla say)*
>
> **Birinci**: bu çalışma **49 unique satıcı** üzerinden yapıldı. Group-aware analizler için yeterli ama populasyon-üstü iddialar için değil. §14'te bunu gösterdik — group-aware AUC headline'dan ciddi düşüyor.
>
> **İkinci**: tek platform veri. Vinted, Depop gibi cross-platform validasyonu yok. Modelimizin Dolap dışında nasıl çalışacağını **bilmiyoruz**.
>
> **Üçüncü**: ablasyon ve robustness analizleri **tek-seed**. Multi-seed bootstrap, çoklu run varyansını ölçmek için planlı.
>
> *(Sonuç tonu — ileriye dönük)*
>
> Sonraki adımlar üç paralel iz. Cohort genişletme — 200+ satıcıya çıkmak için yeni scrape. Cross-platform validasyon. Fairness audit — modelin satıcı-cluster bazında bias yapıp yapmadığı.
>
> *(Bitiş)*
>
> Veri Bilimi Dergisi makale taslağımız `reports/article_draft_en.md`'da hazır. Reviewer mapping eki ile birlikte sunum sonrası finalize edip göndermeyi hedefliyoruz.
>
> Sunumu burada kapatıyorum.
>
> *(Hafif duraksa, audience'a doğru çevril)*
>
> Sorularınıza açığız."

→ Q&A başlar. F + HU + Hİ panel olarak.

---

## 17:15 — 20:00 · Q&A

> **Senin alanın**: Limitler / etik / sonraki adım / cross-platform / 49 satıcı temsilliliği gibi soruları al.
> Detay → [`qa_cards.md`](qa_cards.md). Senin için en olası 5 kart:

| Kart # | Soru | Çekirdek cevap |
|---|---|---|
| **6** | 49 satıcı temsili mi? | "Bir limit. Ablation/robustness için yeterli, populasyon-üstü iddia için değil. Cohort genişletme planlı." |
| **10** | Production'a alır mısınız? | "Bu haliyle hayır. 49 satıcı, group-aware AUC 0.683, concept drift monitoring yok. A/B test + fairness audit gerek." |
| **11** | Cross-platform çalışır mı? | "Doğrulanmadı. Vinted/Depop için aynı schema çıkarılabilir, brand_tier/price_pctile evrensel ama kategori taksonomileri farklı." |
| **14** | Etik / mahremiyet | "Public listing data, kişisel bilgi yok. seller_username sadece group-aware split için, modele girmedi. SQLite cohort takip repo dışında." |
| **15** | Sonraki adım | "Cohort genişletme + multi-seed + cross-platform + Veri Bilimi Dergisi makale finalize." |

### En kritik 3 cevap (kelime-kelime)

#### Q: "49 satıcı temsili mi?" (Kart 6)

> "Hayır, bu bir limit. Bu sayı ablasyon ve robustness analizleri için yeterli ama populasyon-üstü iddialar için değil. Sınırlamalar bölümünde açıkça belirttik. Sonraki adımda 200+ satıcı için yeni cohort planı var, kategori-satıcı çiftlerini çeşitlendirerek."

#### Q: "Modeli production'a alır mısınız?" (Kart 10)

> "Mevcut haliyle hayır. Üç engel: 49 satıcı temsili değil. Group-aware AUC 0.683 — random-split AUC ile arasında ciddi gap, robust populasyon-üstü performans için yetersiz. Concept drift monitoring kurulu değil. Production öncesi A/B test ve fairness audit gerek."

#### Q: "Cross-platform çalışır mı?" (Kart 11)

> "Bilmiyoruz, doğrulanmadı. Vinted, Depop için aynı feature schema'yı çıkarmak teorik olarak mümkün — kategori taksonomileri farklı ama brand_tier, price_pctile, photo_count evrensel kavramlar. Cross-platform validation sonraki adımlar listemizde."

### Soru gelmezse — HU'nun açılış formülünü destekle

> HU "Sıkça merak edilen üç noktaya kendimiz değinelim" deyip Kart 1'i (B.1) açtığında, sonraki sırada sen Kart 6'yı (49 satıcı) veya Kart 11'i (cross-platform) ekle: "Bir nokta da limitler tarafından eklemek isterim..."

---

## Sahne kuralları — Hİ için

1. **Reviewer mapping §12'de tabloya bak, satır satır oku** — audience hocanın feedback'ine cevap verdiğimizi görmeli, akademik dürüstlük mesajı net olsun
2. **B.1 / B.2 / B.3 / A reviewer harflerini söyle** — hocanın kullandığı etiketler bunlar, profesyonel ton
3. **Kapanışta ağırbaşlı ton** — limitler hızlı geçilmez, sayıları (49 satıcı, 0.683 group-aware AUC) net söyle
4. **"Sonraki adımlar" listede 3 madde** — fazlasını söyleme, audience kafası karışır. Cohort genişletme + cross-platform + fairness audit yeterli
5. **Veri Bilimi Dergisi'ni anlat** — projenin akademik çıktısı bu, hoca için önemli sinyal
6. **"Sorularınıza açığız" cümlesini söyledikten sonra hafif duraksa** — audience'a soru hazırlama zamanı tanı, hemen Q&A'ya atlama

---

## Pre-prova kontrolü (T-1 saatte)

Tarayıcıda:
- [ ] §7 ROC + PR grafikleri yan yana renderlanmış
- [ ] §12 Reviewer Mapping tablosu okunabilir font, 8 satır görünür (1.tur 4 + 2.tur 4)
- [ ] §15 PR-eğrisi + F1 vs τ grafikleri görünür
- [ ] `methodology_addendum.md` PDF kopyası USB'de + bulut yedek

Bu 4 kontrol geçtiyse senin tarafında hazırsın.

---

## Cep notu (sahnede çıktı al)

```
§7  → 7:30  ROC vs PR, imbalance altında PR daha bilgilendirici
§12 → 11:45 Reviewer mapping 8 satır (1.tur 4 + 2.tur 4)
              A → §3+§8 post-hoc, B.1 → §14, B.2 → §15, B.3 → §10
§15 → 14:15 STATIC AUC=0.749, F1 0.110→0.215 @ τ=0.18 (B.2)
KAPN → 16:15 3 limit: 49 satıcı, tek-platform, tek-seed
              3 next: cohort genişletme, cross-platform, fairness audit
              Veri Bilimi Dergisi makale finalize
```

### Reviewer mapping cep notu (§12'de hızlı bakman için)

```
1. tur — 4 yorum
  ① Bootstrap CI eksik    → §13
  ② Threshold opt yok     → §11
  ③ Robustness istendi    → §14
  ④ Hipotezler SHAP'la    → §3 (kayıt) + §8 (confirmatory)

2. tur — 4 yorum
  A   SHAP post-hoc       → §3 + §8 dipnot
  B.1 Test>CV anomaly     → §14
  B.2 STATIC F1           → §15
  B.3 XGB vs LGBM         → §10
```

Bu blok kafanda net olsun — §12 sahnede sürpriz olmasın.
