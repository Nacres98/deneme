# NexaGlobe Wedding Planner Spreadsheet: araştırma ve ürün planı

Durum: araştırma tamam, tasarım/yapım sırada. Tarih: 2026-11-25.
Açıklamalar Türkçe; ürün, sekme ve listing metinleri İngilizce (ABD alıcısı).

---

## 1. Pazar araştırması (bulgular)

### Rekabet: beklediğimden sert
| Rakip (Etsy) | Yorum | Fiyat | Not |
|---|---|---|---|
| "Professional Wedding Planner Spreadsheet" (Sheets + Excel; budget, guest list, seating, vendor) | ~13.4k | $4.85 (indirimli) | Lider. Yorum duvarı + ucuz fiyat |
| "Ultimate Wedding Planner": 24 sekme, dashboard, venue comparison, finance tracker | 10k+ | ? | "Çok sekme, otomasyon" vaadi zaten var |
| Budget tracker tek başına | ~6.3k | $3.50 | Bütçe tek başına ucuzlamış |
| Orta segment all-in-one (budget, checklist, guest, seating, itinerary, gift, vendor) | – | $6.99–9.99 | Standart özellik seti bu |
| Üst segment bundle | – | $25–50 | Az sayıda, yorumu az |

**Sonuç:** "Hepsi bir arada" artık bir farklılık değil, standart. Sıfır yorumla $25'a satamayız. Fiyat
çıpası $5–10. Farkı **rakiplerde zayıf olan işlevlerle** ve **alt-niş listinglerle** yaratmalıyız.

> Düzeltme: önceki mesajda "rakiplerin çoğu tek sekmelik basit bütçe" demiştim. Araştırma bunu doğrulamadı:
> liderler çok sekmeli ve otomatik. Strateji buna göre güncellendi.

### Talep ve zamanlama
- ABD ortalama düğün maliyeti **$34,200** (The Knot 2026 Real Weddings Study, 10,474 çift, 2025 düğünleri),
  ortalama 117 davetli, kişi başı $292. Zola 2026: $36,000. → Alıcının bütçesi büyük, $10–15'lık bir araç küçük kalem.
- Davetli sayısına göre: 1–50 kişi ~$17,100 · 51–100 ~$27,200 · 100+ ~$43,300 (The Knot).
- **Aralık = nişan sezonu**, planlama 12–18 ay önceden başlar → **Ocak en güçlü ay**. Hedef: **20 Aralık'tan önce yayında**.

### Rakiplerin açık bıraktığı yerler (farklılaşma)
- Excel sürüm sorunları: bazı satıcılar "Excel 2016'da #NAME? hatası verir" diye uyarıyor; bazıları
  "Sheets→Excel formül aktarımı garanti değil" diyor. → **Bizim kuralımız: Excel 2016+ ve Google Sheets'te
  birebir çalışır, tek dosya** (envanter ürününde test ettiğimiz uyumluluk kuralı).
- Bütçeyi **kim ödüyor** (çift / gelinin ailesi / damadın ailesi) ayrımı: liderlerin açıklamalarında görmedim.
- **Ödeme takvimi / nakit akışı**: kapora ve kalan ödemelerin vadeleri, "önümüzdeki 30 günde ödenecek".
- **Bahşiş (tip) hesaplayıcı** + düğün günü zarf listesi (ayrı arama kelimesi: "wedding tip calculator").
- Checklist'in **düğün tarihinden geriye otomatik tarihlenmesi**.

(Not: Etsy/eRank'a buradan erişemiyorum; yorum sayıları arama sonuçlarındaki listing özetlerinden.
Yayından önce eRank'ta kelimeleri kontrol edelim.)

---

## 2. Ürün: sekme yapısı (13 sekme)

| # | Sekme | Ne yapar | Fark mı? |
|---|---|---|---|
| 1 | **Start Here** | Çift isimleri, düğün tarihi, toplam bütçe, davetli hedefi, para birimi, katkı verenler | |
| 2 | **Dashboard** | Geri sayım, harcanan/kalan bütçe, RSVP durumu, 30 gün içindeki ödemeler, sıradaki 5 görev, grafikler | |
| 3 | **Budget Builder** | Toplam bütçe + davetli sayısı → kategori bazlı önerilen dağılım (düzenlenebilir %), kişi başı maliyet | ✓ |
| 4 | **Budget & Expenses** | Kategori, kalem, tahmini/gerçek, ödeyen kişi, ödenen/kalan | |
| 5 | **Who's Paying** | Katkı verenlere göre söz verilen / ödenen / kalan | ✓✓ |
| 6 | **Payment Schedule** | Her tedarikçinin kapora ve kalan ödemesi, vade, durum (Paid / Due soon / Overdue), aylık nakit akışı | ✓✓ |
| 7 | **Vendors** | Tedarikçi rehberi + 3 teklif yan yana karşılaştırma (Vendor Compare) | |
| 8 | **Guest List** | Taraf, grup, +1, adres, RSVP, yemek seçimi, masa, hediye, teşekkür kartı gönderildi mi | |
| 9 | **Seating Plan** | Masa kapasitesi ve dolu koltuk, fazla atama uyarısı | |
| 10 | **Checklist** | ~90 görev, "X ay önce" → düğün tarihinden otomatik son tarih, gecikme vurgusu | ✓ |
| 11 | **Tips & Envelopes** | Tedarikçi bazlı bahşiş önerisi (% / sabit), kimin vereceği, zarf hazır mı | ✓✓ |
| 12 | **Day-Of Timeline** | Saat saat akış, sorumlu kişi, tedarikçi geliş saatleri | |
| 13 | **Gifts & Thank-Yous** | Hediye kaydı ↔ Guest List, teşekkür kartı takibi | |

Teslim paketi (envanter ürünüyle aynı mantık): `SAMPLE_DATA.xlsx` (örnek çift: "Maya & Jordan",
kurgusal) + `BLANK.xlsx` + kısa PDF kılavuz + Google Sheets kopya linki.

Tasarım: yumuşak, düğün estetiği (ivory / sage / dusty rose / altın vurgular, Georgia başlıklar).
Giriş hücreleri tek renk, formüller kilitli; dropdown'lar her yerde.

Teknik kural: yalnızca SUMIFS / COUNTIFS / SUMPRODUCT / INDEX-MATCH / IFERROR / DATE / EDATE / TODAY.
XLOOKUP, FILTER, LET, IFS, dinamik dizi yok. LibreOffice ile tam yeniden hesap + çapraz kontrol denetimi.

---

## 3. Fiyat ve listing stratejisi

- **Ana ürün:** liste fiyatı **$14.99**, açılışta %40 indirim → **~$8.99** (çıpa $5–10 bandında ama
  "premium" görünür). 15–20 yorumdan sonra $16.99–19.99'a çık.
- **Alt-niş "giriş" listingleri** (aynı dosyadan tek sekmelik sürümler, $3–5): her biri ana ürüne yönlendirir.
  1. Wedding Tip Calculator & Envelope Checklist
  2. Wedding Payment Schedule / Vendor Payment Tracker
  3. Wedding Budget by Guest Count
  4. Wedding Guest List & RSVP Tracker
- **Bundle:** Wedding Planner + (ileride) Honeymoon Budget / Bachelorette Planner.
- Hediye açısı: başlık/etiketlerde "engagement gift", "newly engaged" (Aralık aramaları).

---

## 4. Yol haritası
- [x] Pazar ve rakip araştırması
- [ ] Workbook builder (`build_workbook.py sample|blank`) + örnek veri
- [ ] Denetim (LibreOffice recalc, çapraz kontroller, Excel/Sheets uyumluluğu)
- [ ] Listing kiti (başlık, 13 etiket, açıklama), 10 görsel + video
- [ ] Alt-niş listing dosyaları
- [ ] 20 Aralık öncesi yayın

## Kaynaklar
- Etsy rakip listingleri: https://www.etsy.com/market/wedding_planning_spreadsheet ·
  https://www.etsy.com/listing/1326502722/ultimate-wedding-planning-spreadsheet ·
  https://www.etsy.com/listing/934242338/wedding-planning-google-sheets ·
  https://www.etsy.com/listing/4610267109 · https://www.etsy.com/listing/1192908350/wedding-vendor-payment-tracker-wedding
- The Knot, average wedding cost: https://www.theknot.com/content/average-wedding-cost
- Maliyet derlemeleri: https://www.bespoke-bride.com/2026/05/03/average-wedding-cost-2026/ ·
  https://www.meetneptune.com/blog/average-wedding-cost-2026
