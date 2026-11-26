# 4a4p.com — tanıtım sitesi

Bağımsız statik site. Sayfalar `tools/build.py` ile üretilir (`python3 tools/build.py`); iki dilin metni orada yan yana durur, çıktı HTML depoya girer. Ana swingod uygulamasına, 4A4P ölçüm motoruna ya da hasta verisine bağlı değildir.

- `index.html` Türkçe, `en/index.html` İngilizce — elle düzenlenmez, `tools/build.py` düzenlenip yeniden üretilir. Stil `assets/site.css`, etkileşim `assets/site.js`.
- Fontlar yerel (Manrope, Newsreader Italic; OFL lisansları `assets/fonts/`); ziyaretçi üçüncü tarafa bağlanmaz.
- İlk ziyaret `/` adresindeyse ve tarayıcı dili Türkçe değilse `/en/` açılır. Doğrudan açılan `/en/` her tarayıcıda İngilizce kalır. TR/EN bağlantıları temiz URL'leri kullanır ve dil tercihi `localStorage["4a4p-dil"]` anahtarında hatırlanır.
- Barındırma: GitHub Pages (ücretsiz). `CNAME` = `4a4p.com`. DNS Spaceship'te (ayrıntı swingod kökündeki `4a4p.md` §10).
- Arama motorlarına açık (2026-11-22): `robots.txt` Allow + `sitemap.xml`; sayfalarda canonical + hreflang (tr, en, x-default) + Open Graph. Arama motoru botları ve Google URL Denetleme Aracı, her dili kendi adresinden okur. `404.html` `noindex` kalır.
- Kural: araştırma doğrulanmadan sonuç, katsayı ya da risk puanı yayımlanmaz (`4a4p.md` §3).

Yerel önizleme: `python3 -m http.server 8790` (bu klasörde) → http://localhost:8790
