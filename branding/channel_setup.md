# YouTube kanal kurulumu

Tüm görseller kodla çizildi (`tools/branding.py`), Rockstar logosu veya başka birinin görseli yok.
İsim değişirse tek komutla yeniden üretilir:
`python3 tools/branding.py --name "YENI ISIM" --tagline "..." --badge 5 --out branding`

## 1. Kanal adı ve kullanıcı adı (handle)

| # | Kanal adı | Handle | Neden |
|---|---|---|---|
| ⭐ 1 | **Five Star Facts** | `@FiveStarFacts` | Formatımız "5 şey" listeleri + GTA'nın 5 yıldızlı aranma seviyesi. "Facts" kelimesi doğrulanmış bilgi vaadimizi taşıyor. GTA dışındaki oyunlara da genişleyebilir. **Önerim** |
| 2 | Wanted Level | `@WantedLevelHQ` | Kısa, akılda kalıcı, gaming terimi |
| 3 | Leonida Intel | `@LeonidaIntel` | Tamamen GTA 6'ya odaklı; ama oyun dışına çıkmak zorlaşır |
| 4 | Vice Files | `@ViceFiles` | Gizem / "dosya" havası, detay videolarına uygun |

- Kanal adında **"GTA"** kullanmamanı öneririm: marka (Rockstar/Take-Two) riski var ve kanalı tek oyuna kilitler.
  "GTA 6" kelimesi video başlıklarında ve açıklamada zaten geçiyor; arama için yeterli.
- Handle müsait mi bilmiyorum (YouTube bu ortamda engelli). Studio → Özelleştirme → Temel bilgiler → Herkese açık kullanıcı adı'nda kontrol et.
  Doluysa sırayla `@FiveStarFactsHQ`, `@FiveStarFactsTV`, `@5StarFacts` dene.

## 2. Görseller
| Dosya | Nereye | Not |
|---|---|---|
| `avatar_800.jpg` | Profil resmi | 800×800, YouTube daire şeklinde keser. `avatar_preview_98px.png` küçük boyutta nasıl göründüğünü gösteriyor |
| `banner_2560x1440.jpg` | Banner görseli | Yazılar 1235×338'lik güvenli alanın içinde, telefonda kesilmez. "NEW SHORTS DAILY" etiketi sadece masaüstü/TV'de görünür |
| `avatar_800.jpg` | Video filigranı (opsiyonel) | Studio → Özelleştirme → Marka → Video filigranı. "Videonun sonunda" seç |

## 3. Kanal açıklaması (Studio → Özelleştirme → Temel bilgiler → Açıklama)
```
GTA 6 news, hidden details and secrets: verified, never faked. ⭐⭐⭐⭐⭐

Every claim in our videos is checked against official Rockstar sources. If something is a rumor or a leak, we say so on screen. No fake gameplay, no clickbait lies.

What you'll find here:
🎮 Hidden details you missed in GTA 6
🚔 GTA 6 vs GTA 5 comparisons
📰 Fast, verified GTA news
🔥 Tips before you play

New Shorts every day. Subscribe so you never miss a detail.

Business inquiries: [e-posta adresin]

Not affiliated with or endorsed by Rockstar Games or Take-Two Interactive. Game footage © Rockstar Games.
```
`[e-posta adresin]` kısmını kanal için açacağın ayrı bir iş e-postasıyla değiştir; kişisel adresini yazma.

## 4. Diğer ayarlar (Studio → Ayarlar)
| Ayar | Değer |
|---|---|
| Kanal → Temel bilgiler → **Ülke** | **Gerçekten yaşadığın ülke (Türkiye).** Para kazanma, vergi ve ödeme bu ayara bağlı; ABD seçmek yanlış beyan olur ve ileride sorun çıkarır. İzleyici kitlesini etkilemez |
| Kanal → Anahtar kelimeler | `GTA 6, GTA VI, Grand Theft Auto 6, GTA 6 news, GTA 6 details, GTA 6 secrets, GTA 6 vs GTA 5, Vice City, Leonida, gaming facts` |
| Kanal → Gelişmiş → Kitle | **Hayır, çocuklara özel değil** |
| Yükleme varsayılanları → Kategori | Gaming |
| Yükleme varsayılanları → Video dili / başlık dili | English (United States) |
| Yükleme varsayılanları → Açıklama | Her videoya eklenecek son satır: `Not affiliated with Rockstar Games. Footage © Rockstar Games.` |
| Yükleme varsayılanları → Lisans / yorumlar | Standart YouTube Lisansı / Tümü |
| Özelleştirme → Düzen → Kanal fragmanı | İlk videon (Video 01) |
| Özelleştirme → Temel bilgiler → Bağlantılar | Varsa TikTok / Instagram / X hesapları. Aynı isimle açman önerilir |

## 5. Diğer platformlar (önerim)
Aynı Shorts'u **TikTok** ve **Instagram Reels**'e de yükleyebilirsin; ekstra üretim maliyeti sıfır.
Kullanıcı adını üç platformda da aynı tut (`fivestarfacts`).
