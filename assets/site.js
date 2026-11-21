// 4A4P — küçük etkileşim katmanı. JS yoksa sayfa yine eksiksiz okunur (bütün paneller görünür).
(function () {
  var dil = document.documentElement.lang;
  try {
    if (!localStorage.getItem("4a4p-dil")) localStorage.setItem("4a4p-dil", dil);
  } catch (e) {}
  document.querySelectorAll("[data-dil]").forEach(function (a) {
    a.addEventListener("click", function () {
      try { localStorage.setItem("4a4p-dil", a.dataset.dil); } catch (e) {}
    });
  });

  // Görünür olunca beliren öğeler
  var ogeler = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (girdiler) {
      girdiler.forEach(function (g) {
        if (g.isIntersecting) { g.target.classList.add("in"); io.unobserve(g.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    ogeler.forEach(function (o) { io.observe(o); });
  } else {
    ogeler.forEach(function (o) { o.classList.add("in"); });
  }

  // Okuma çizgisi
  var cizgi = document.getElementById("progress");
  function ilerleme() {
    var h = document.documentElement.scrollHeight - innerHeight;
    cizgi.style.transform = "scaleX(" + (h > 0 ? Math.min(scrollY / h, 1) : 0) + ")";
  }
  addEventListener("scroll", ilerleme, { passive: true });
  ilerleme();

  // Alan atlası sekmeleri
  var sekmeler = Array.prototype.slice.call(document.querySelectorAll(".tab"));
  var paneller = document.querySelectorAll(".panel");
  function sec(kod, odakla) {
    sekmeler.forEach(function (s) {
      var on = s.dataset.kod === kod;
      s.setAttribute("aria-selected", on ? "true" : "false");
      s.tabIndex = on ? 0 : -1;
      if (on && odakla) s.focus();
    });
    paneller.forEach(function (p) { p.hidden = p.dataset.kod !== kod; });
    document.querySelectorAll(".sector").forEach(function (s) { s.classList.toggle("on", s.dataset.kod === kod); });
  }
  sekmeler.forEach(function (s, i) {
    s.addEventListener("click", function () { sec(s.dataset.kod); });
    s.addEventListener("keydown", function (ev) {
      var y = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[ev.key];
      if (!y) return;
      ev.preventDefault();
      sec(sekmeler[(i + y + sekmeler.length) % sekmeler.length].dataset.kod, true);
    });
  });
  if (sekmeler.length) sec("A1");

  // Kadran: üzerine gelince ortada alan adı; tıklayınca atlasta o alan
  var kod = document.getElementById("core-code");
  var ad = document.getElementById("core-name");
  var alt = document.getElementById("core-sub");
  if (kod) {
    var ilk = { kod: kod.textContent, ad: ad.textContent, alt: alt.textContent };
    var goster = function (s) {
      kod.textContent = s ? s.dataset.kod : ilk.kod;
      ad.textContent = s ? s.dataset.ad : ilk.ad;
      alt.textContent = s ? (s.classList.contains("a") ? "4A" : "4P") : ilk.alt;
    };
    document.querySelectorAll(".sector").forEach(function (s) {
      s.addEventListener("mouseenter", function () { goster(s); });
      s.addEventListener("focus", function () { goster(s); });
      s.addEventListener("mouseleave", function () { goster(null); });
      s.addEventListener("blur", function () { goster(null); });
      var git = function () {
        sec(s.dataset.kod);
        document.getElementById("alanlar").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
      };
      s.addEventListener("click", git);
      s.addEventListener("keydown", function (ev) { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); git(); } });
    });
  }
})();
