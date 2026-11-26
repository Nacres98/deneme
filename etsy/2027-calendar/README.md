# 2027 Printable Calendar: Etsy ürün seti

4 listing, hepsi yüklemeye hazır. Her klasörde `files/` (Etsy'ye yüklenecek dijital dosyalar), `images/` (listing görselleri,
2700×2025, 01 = kapak/thumbnail) ve `LISTING.md` (başlık, 13 etiket, açıklama, fiyat; kopyala-yapıştır) var.

| # | Klasör | Konsept | İçerik | Önerilen fiyat |
|---|---|---|---|---|
| 1 | `upload/01-minimal-monochrome` | Siyah-beyaz minimal, mürekkep dostu | 8 PDF: A4 + Letter × dikey + yatay × Pazar + Pazartesi başlangıç, 14'er sayfa | $4.50 |
| 2 | `upload/02-neutral-holidays` | 4 nötr renk (Sand, Sage, Terracotta, Dusty Blue) + ABD tatilleri + not sütunu | 16 PDF, 14'er sayfa | $5.90 |
| 3 | `upload/03-hyperlinked-digital` | iPad/GoodNotes için tıklanabilir sekmeli + yazdırılabilir | 4 PDF, 26 sayfa (ay + aylık plan sayfası) | $6.90 |
| 4 | `upload/04-year-at-a-glance` | Tek sayfa yıllık takvim (trafik çeken ucuz ürün) | 8 tek sayfalık PDF | $1.99 |

## Neden bunlar tercih edilir (rekabet avantajı)
- **Tek alımda tüm varyantlar.** Rakiplerin çoğu tek boyut ya da tek başlangıç günü satıyor. Biz A4 + Letter ve Pazar + Pazartesi
  başlangıcı aynı pakette veriyoruz. Bunu görsellerde ve başlıkta öne çıkardık.
- **ABD tatilleri hazır basılı.** 2027 tarihleri kurala göre hesaplandı (Easter 28 Mart, Thanksgiving 25 Kasım, Memorial Day 31 Mayıs vb.).
  21 tarih var, federal tatiller vurgulu.
- **Hepsi vektör PDF.** Her boyutta keskin basılıyor, gömülü fontlar açık lisanslı (OFL).
- **Ürünler birbirine yönlendiriyor.** #4 ucuz giriş ürünü; açıklamaları diğer listinglere atıf yapıyor.
- **Aramalar farklı nişlere dağılıyor:** "minimalist", "with holidays / sage / boho", "goodnotes / digital", "year at a glance".
  Böylece mağaza kendi ürünleriyle yarışmıyor.

## Yükleme adımları (her listing için)
1. Shop Manager → Listings → Add a listing → **Digital files**.
2. Fotoğraflar: `images/01.png` … sırayla (01 thumbnail). Thumbnail kırpmasında başlık ortada kalacak şekilde tasarlandı.
3. Başlık, açıklama ve 13 etiketi `LISTING.md` dosyasından kopyala. Materials: `Digital PDF`.
4. Kategori: Paper & Party Supplies → Paper → Calendars & Planners (Etsy'nin önerdiği alt kategoriyi seç).
5. Dosyalar: `files/` içindekilerin hepsi (Etsy sınırı: en fazla 5 dosya, 20 MB; hepsi bu sınırın altında).
6. Kim yaptı: I did · Ne zaman yapıldı: listedeki en yeni yıl aralığı · Tür: Digital.
7. Etsy'nin yaratıcılık standartları AI yardımıyla yapılan tasarımların belirtilmesini istiyor. Listing'deki ilgili alanı
   (veya açıklamayı) buna göre doldur.

## Satış önerileri
- **Zamanlama:** 2027 takvimi aramaları şu an (Kasım–Ocak) zirvede. Hemen yükle.
- **Açılış indirimi:** İlk 2 hafta %30–40 indirim. Rakamın üstü çizili görünür, ilk satış ve yorumları hızlandırır.
- **Etsy Ads:** Her listing için günlük $1–2 ile başla. 7 gün sonra tıklanmayan etiketi daha spesifik bir long-tail ile değiştir.
- **Bundle (5. listing):** 1 + 2 + 4 birlikte ~$8.90 olarak ayrı listing (dosyalar hazır, sadece aynı ZIP'leri yükle).
- **Pinterest:** `images/01-02` dikey kırpılıp pinlenebilir. Takvim/planner nişinde Pinterest trafiği çok güçlü.
- Etsy son dönemde daha kısa, okunur başlıkları öneriyor. 2–3 hafta sonra tıklama oranı düşükse başlığın ilk ~60 karakterini koruyup kısalt.

## Yeniden üretme
```
python3 etsy/2027-calendar/build.py        # PDF'ler + ZIP'ler (upload/*/files)
python3 etsy/2027-calendar/mockups.py      # listing görselleri (upload/*/images)
python3 etsy/2027-calendar/listing_md.py   # LISTING.md (listings.json'dan)
```
Ara dosyalar `build/` altında (git'e girmez). Fontlar: Inter, Fraunces, Cormorant Garamond (SIL OFL 1.1, `fonts/`).
