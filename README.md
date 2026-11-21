# 4a4p.com — tanıtım sitesi

Bağımsız statik site. Sayfalar `tools/build.py` ile üretilir (`python3 tools/build.py`); iki dilin metni orada yan yana durur, çıktı HTML depoya girer. Ana swingod uygulamasına, 4A4P ölçüm motoruna ya da hasta verisine bağlı değildir.

- `index.html` Türkçe, `en/index.html` İngilizce — elle düzenlenmez, `tools/build.py` düzenlenip yeniden üretilir. Stil `assets/site.css`, etkileşim `assets/site.js`.
- Fontlar yerel (Manrope, Newsreader Italic; OFL lisansları `assets/fonts/`); ziyaretçi üçüncü tarafa bağlanmaz.
- İlk ziyarette Türkçe olmayan tarayıcı `/en/`'e gider; TR/EN tıklaması `localStorage["4a4p-dil"]` ile hatırlanır.
- Barındırma: GitHub Pages (ücretsiz). `CNAME` = `4a4p.com`. DNS Spaceship'te (ayrıntı swingod kökündeki `4a4p.md` §10).
- Arama motoru kapalı: `robots.txt` `Disallow: /` ve sayfalarda `noindex`. Açmak ayrı karardır.
- Kural: araştırma doğrulanmadan sonuç, katsayı ya da risk puanı yayımlanmaz (`4a4p.md` §3).

Yerel önizleme: `python3 -m http.server 8790` (bu klasörde) → http://localhost:8790
