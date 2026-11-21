"""4a4p.com sayfalarını üretir: index.html (TR) ve en/index.html (EN).

Metin iki dilde aynı yerde durur; biri değişince öbürü de değişir. Çalıştır:
    python3 sites/4a4p/tools/build.py
Kural: araştırma doğrulanmadan sonuç, katsayı ya da risk puanı yazılmaz (swingod `4a4p.md` §3).
"""
from __future__ import annotations

import html
import math
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]

ALANLAR = [
    # kod, tür, kısa ad (tr, en), başlık, metin, çipler, bilinen hata
    dict(kod="A1", tur="a",
         ad=("Gövde kası", "Trunk muscle"),
         baslik=("Sternumdan koksikse tüm gövde kasları.", "All trunk muscle, from sternum to coccyx."),
         metin=("Bu aralıktaki tüm iskelet kaslarının hacmi ve ortalama yoğunluğu ölçülür. Düşük yoğunluk kas içi yağlanmayı gösterir. Pektoral, paraspinal, karın duvarı ve psoas kasları ayrıca değerlendirilir.",
                "Volume and mean density of all skeletal muscle in the range; density reflects fatty infiltration. Pectoral, paraspinal, abdominal wall and psoas groups are measured separately."),
         cip=(["BT", "mL", "HU"], ["CT", "mL", "HU"]),
         hata=("görüntünün bu aralığı tam kapsamaması, kol pozisyonu, kontrast fazı", "truncated coverage, arm position, contrast phase")),
    dict(kod="A2", tur="a",
         ad=("Karın yağı", "Abdominal fat"),
         baslik=("Deri altı ve viseral yağ, ayrı ayrı.", "Subcutaneous and visceral fat, separately."),
         metin=("Diyafram kubbesi ile iliak krest arasındaki deri altı (SAT) ve viseral (VAT) yağ hacmi ölçülür. Birincil değişken SAT'tır; az yağ dokusu kötü seyirle ilişkili olabilir.",
                "Subcutaneous (SAT) and visceral (VAT) fat volume between the diaphragm dome and the iliac crest. SAT is the primary variable: low fat may signal a poorer course."),
         cip=(["BT", "mL"], ["CT", "mL"]),
         hata=("asit, mezenterik kitle, görüntü alanı dışında kalan yağ dokusu", "ascites, mesenteric mass, fat outside the field of view")),
    dict(kod="A3", tur="a",
         ad=("L1–L4 vertebraları", "L1–L4 vertebrae"),
         baslik=("Vertebra yüksekliği ve kemik yoğunluğu.", "The spine: shape and density."),
         metin=("Her vertebra gövdesinin ön, orta ve arka yüksekliği ile L1 trabeküler yoğunluğu ölçülür. Kompresyonu radyolog doğrular. Miyelomda kırık hastalığın kendisine bağlı olabileceği için sonuç ayrı yorumlanır.",
                "Anterior, middle and posterior height of each vertebral body and L1 trabecular density. A radiologist confirms compression; in myeloma a fracture may be the disease itself, so it is interpreted separately."),
         cip=(["BT", "mm", "HU"], ["CT", "mm", "HU"]),
         hata=("eğik kesit, dejeneratif değişiklikler, patolojik çökme", "oblique reformat, degenerative shape, pathological collapse")),
    dict(kod="A4", tur="a",
         ad=("Beyaz cevher", "White matter"),
         baslik=("Beyaz cevher lezyon yükü.", "The silent burden in the brain."),
         metin=("Tüm MR'larda Fazekas derecesi, uygun çekimlerde beyaz cevher hiperintensitelerinin hacmi ölçülür. İki ölçüm birbiriyle karşılaştırılır.",
                "Fazekas grade on every MRI; quantitative white matter hyperintensity volume where the scan allows. The two are compared with each other."),
         cip=(["MR", "Fazekas 0–3", "mL"], ["MRI", "Fazekas 0–3", "mL"]),
         hata=("okuyucular arası uyum, MR'ın çekilme nedeni", "inter-reader agreement, reason the MRI was ordered")),
    dict(kod="P1", tur="p",
         ad=("Yürüme hızı", "Gait speed"),
         baslik=("Olağan hızda 4 metre yürüme.", "Four metres, usual pace."),
         metin=("Yaşlı hematoloji hastalarında kanıtı en güçlü yatak başı ölçümdür. Sürekli değişken olarak kullanılır.",
                "The bedside measure with the strongest evidence in older patients with haematological cancer. Used as a continuous variable."),
         cip=(["Yatak başı", "m/s"], ["Bedside", "m/s"]),
         hata=("başlangıç şekli, yürüme yardımcısı kullanımı", "start protocol, walking aid")),
    dict(kod="P2", tur="p",
         ad=("Kavrama gücü", "Grip strength"),
         baslik=("Dinamometreyle el kavrama gücü.", "Muscle strength, measured in the hand."),
         metin=("Denemelerin en iyisi alınır ve cinsiyete göre değerlendirilir. Görüntülemedeki kas ölçümünü işlev yönünden tamamlar.",
                "Best trial on a dynamometer, interpreted by sex. The functional counterpart of the muscle seen on imaging."),
         cip=(["Dinamometre", "kg"], ["Dynamometer", "kg"]),
         hata=("cihaz ve kalibrasyonu, ölçülen el", "device and calibration, choice of hand")),
    dict(kod="P3", tur="p",
         ad=("Denge", "Balance"),
         baslik=("Ayakta denge.", "Being able to stand."),
         metin=("Kısa Fiziksel Performans Bataryası'nın (SPPB) tamamı kaydedilir. Skora denge alt puanı girer; toplam puan keşif amaçlı analizlerde kullanılır.",
                "The full Short Physical Performance Battery is recorded; the balance subscore enters the score and the total is used for exploration."),
         cip=(["SPPB", "0–4 · 0–12"], ["SPPB", "0–4 · 0–12"]),
         hata=("tavan etkisi, süre ölçümü", "ceiling effect, timing")),
    dict(kod="P4", tur="p",
         ad=("Bilişsel durum", "Cognition"),
         baslik=("Mini Mental Test ve eğitim düzeyi.", "Cognitive performance, with education."),
         metin=("Standardize Mini Mental Test puanı, eğitim düzeyiyle birlikte değerlendirilir. Beyaz cevher bulgularıyla yan yana incelenir.",
                "Mini-Mental State Examination together with education level. The clinical counterpart of the white matter burden."),
         cip=(["SMMT", "0–30"], ["MMSE", "0–30"]),
         hata=("eğitim düzeyi, işitme ve görme kaybı, deliryum", "education, sensory loss, delirium")),
]

# Kadranda açı (derece; SVG'de +x'ten saat yönünde, y aşağı). Üst yarı 4A, alt yarı 4P; soldan sağa okunur.
ACI = {"A1": 180, "A2": 225, "A3": 270, "A4": 315, "P4": 0, "P3": 45, "P2": 90, "P1": 135}

T = {
    "tr": dict(
        lang="tr", kok="/", title="4A4P — Geriatrik Anatomi ve Performans Skoru",
        desc="Yaşlı hematoloji hastalarında tedavi öncesi rutin görüntüleme ve dört kısa yatak başı testiyle 90 gün içindeki ölüm ya da bağımlılık gelişimini öngörmeyi amaçlayan araştırma programı.",
        nav=[("yaklasim", "Yaklaşım"), ("alanlar", "Sekiz alan"), ("soru", "Soru"), ("ilkeler", "İlkeler"), ("yol", "Yol haritası")],
        eyebrow="Geriatrik hemato-onkoloji için yeni bir ölçüm yaklaşımı",
        h1=("Rezervi ölçmek.", "Tedaviden önce."),
        lead="Tedavi öncesinde zaten çekilmiş görüntülerle ve yatak başında yapılan dört kısa testle, yaşlı hastanın tedaviyi ne ölçüde kaldırabileceğini öngörmeyi amaçlayan bir araştırma programı.",
        btn="4A4P'yi keşfedin", link="Araştırma sorusu",
        dial_title="Sekiz alanlı profil kadranı (şematik)",
        dial_sub="sekiz alan", dial_name="tek profil",
        ax_a="4A · ANATOMİ", ax_p="4P · PERFORMANS",
        dial_note=("Üzerine gelin ya da bir alan seçin", "Şematik · hasta verisi içermez"),
        bar="Hekim bakışıyla kurulan bir araştırma.", feats=["Rutin görüntüleme", "Yatak başı testler", "Yerelde işleme"], down="Aşağı kaydırın",
        s1=("Yaklaşım", ("Görüntüler zaten çekiliyor.", "İçlerindeki bilgi okunmuyor.")),
        s1p=("Hematolojik kanserlerde kemoterapiden ya da kök hücre naklinden önce hemen her hastaya BT ya da PET/BT, çoğuna da beyin MR'ı çekilir. Bu görüntülerde kas, yağ dokusu, omurga ve beyaz cevher görülür. Ancak evrelemeden sonra bu bilgilere çoğu zaman yeniden bakılmaz.",
             "Takvim yaşı, hastanın tedaviye ne kadar dayanabileceği konusunda yalnızca kaba bir fikir verir. Kapsamlı geriatrik değerlendirme bu farkı daha iyi gösterir ama zaman alır. 4A4P, ek çekim yapmadan ve ek radyasyon vermeden bu açığın kapatılıp kapatılamayacağını araştırıyor."),
        s2=("Sekiz alan", ("Dört anatomik ölçüm.", "Dört performans testi.")),
        s2side="Ölçümlerin dördü görüntülemeden, dördü doğrudan hastadan alınır. Her ölçümün tanımı, sınırları ve olası hata kaynakları veri toplanmadan önce yazılır.",
        grup_a="4A · Görüntüleme", grup_p="4P · Yatak başı", atlas="4A4P / Alan atlası", tanim="Tanım",
        tur_a="Anatomi · görüntüleme", tur_p="Performans · yatak başı", hata="Olası hata kaynakları", onceden="Tanım önceden kayıtlı",
        s3=("Soru", ("Üç model.", "Tek soru.")),
        s3p="<b>Hasta grubu:</b> kemoterapi ya da kök hücre nakli planlanan, 60 yaş ve üzeri hematolojik kanser hastaları.<br><br><b>Sonlanım:</b> ilk tedavi dozundan sonraki 90 gün içinde ölüm ya da en az bir temel günlük yaşam aktivitesinde yeni gelişen bağımlılık.",
        durum="Araştırma aşamasında · henüz sonuç yok",
        modeller=[("Klinik model", "M1", "Yaş, cinsiyet, ECOG, eşlik eden hastalık yükü ve hastalığa özgü prognostik indeks."),
                  ("+ Performans", "M2", "Dört yatak başı testi eklenir. <em>Tahmine katkı sağlıyor mu?</em>"),
                  ("+ Anatomi", "M3", "Dört görüntüleme ölçümü eklenir. <em>Asıl soru: görüntüleme tahmini iyileştiriyor mu?</em>")],
        mnot="Tek bir model kurulur. Tanı grubu ve tedavi türü modelde değişken olarak yer alır; kalibrasyon her alt grup için ayrı raporlanır.",
        s4=("İlkeler", ("Önce kural.", "Sonra sonuç.")),
        ilkeler=[("Önce arşiv verisi.", "Etik kurul onayının ardından çalışma arşiv kayıtlarıyla başlar. Geliştirilen model daha sonra ileriye dönük bir hasta grubunda yeniden test edilir."),
                 ("Plan önceden kaydedilir.", "Ölçüm tanımları ve analiz planı, verilere bakılmadan önce tarihli olarak kayda geçirilir."),
                 ("Görüntüler kurumda kalır.", "Segmentasyon yerel bilgisayarda yapılır. Görüntüler buluta gönderilmez, hasta kimlik bilgisi tutulmaz."),
                 ("Uydurma veri yok.", "Ölçülemeyen değer boş bırakılır ve nedeni kaydedilir. Model doğrulanmadan katsayı ya da risk puanı yayımlanmaz.")],
        s5=("Yol haritası", ("Bugün tasarım.", "Yarın kanıt.")),
        s5side="Bu sayfada çalışmanın tasarımı anlatılıyor. Henüz hasta verisi işlenmedi.",
        yol=[("ok", "Tamamlandı", "Ölçüm tanımları ve literatür", "Sekiz ölçümün tanımı yazıldı; temel kaynaklar özgün yayınlarından incelendi."),
             ("on", "Devam ediyor", "Protokol ve ön kayıt", "Örneklem, veri sözlüğü ve analiz planı."),
             ("on", "Devam ediyor", "Görüntü analiz altyapısı", "Açık lisanslı BT verileriyle kuruldu. Aynı görüntü iki kez işlendiğinde birebir aynı sonuç alınıyor."),
             ("", "Planlandı", "Etik kurul başvurusu", "Geriye dönük arşiv çalışması için."),
             ("", "Planlandı", "Arşiv çalışması", "Uygulanabilirlik ve tekrarlanabilirlik; M1 → M2 → M3 karşılaştırması."),
             ("", "Planlandı", "Doğrulama", "İleriye dönük hasta grubunda ve bağımsız bir örneklemde.")],
        s6=("Kaynaklar", ("Temel", "kaynaklar.")),
        s6side="Bu çalışmaların çoğu farklı hasta gruplarında yapıldı. 4A4P, bulguların hematolojik kanserlerde de geçerli olup olmadığını araştırıyor.",
        kaynak=[("Ying ve ark. 2024", "Osteoporos Sarcopenia 10:78–83", "Sternum–koksiks arasındaki tüm gövde kaslarının ölçümü.", "10.1016/j.afos.2024.04.001"),
                ("Ullrich ve ark. 2026 · PETAL", "Blood Adv 10:5995–6006", "DLBCL'de BT ile saptanan sarkopeni; relaps dışı mortalite ve hematolojik toksisite.", "10.1182/bloodadvances.2026020504"),
                ("Liu ve ark. 2019", "Blood", "Yaşlı hematoloji hastalarında yürüme hızı ve sağkalım.", "10.1182/blood.2019000758"),
                ("Armenian ve ark. 2019", "J Natl Cancer Inst", "Allojenik nakil öncesinde BT ile saptanan sarkopeni.", "10.1093/jnci/djy231"),
                ("Merli ve ark. 2021", "J Clin Oncol", "Yaşlı DLBCL hastalarında Elderly Prognostic Index (EPI).", "10.1200/JCO.20.02465"),
                ("Cobbing ve ark. 2025", "J Geriatr Oncol 16:102201", "Yaşlı kanser hastalarında fiziksel performans testleri.", "10.1016/j.jgo.2025.102201"),
                ("Inzitari ve ark. 2009 · LADIS", "BMJ 339:b2477", "Beyaz cevher değişiklikleri ve yeti yitimi.", "10.1136/bmj.b2477")],
        f1="Yaşlı hastanın tedaviye dayanıklılığını anlamaya yönelik bir araştırma.", yukari="Yukarı",
        f2="4A4P bir araştırma projesidir; klinik kararlarda kullanılmak üzere tasarlanmamıştır.",
        sec_tr='<span>TR</span>', sec_en='<a href="/en/" data-dil="en">EN</a>',
    ),
    "en": dict(
        lang="en", kok="/en/", title="4A4P — Geriatric Anatomy and Performance Score",
        desc="A research programme on predicting 90-day loss of independence in older patients with haematological cancer from routine pre-treatment imaging and four short bedside tests.",
        nav=[("yaklasim", "Approach"), ("alanlar", "Eight domains"), ("soru", "Question"), ("ilkeler", "Principles"), ("yol", "Roadmap")],
        eyebrow="A new measure in geriatric haemato-oncology",
        h1=("Measuring reserve.", "Before treatment."),
        lead="A research programme that aims to read how an older patient will tolerate treatment from imaging already taken before therapy and four short bedside tests.",
        btn="Explore 4A4P", link="The research question",
        dial_title="Eight-domain profile dial (schematic)",
        dial_sub="eight domains", dial_name="one profile",
        ax_a="4A · ANATOMY", ax_p="4P · PERFORMANCE",
        dial_note=("Hover · select a domain", "Schematic · no patient data"),
        bar="Research built from a clinician's perspective.", feats=["Routine imaging", "Bedside tests", "Local processing"], down="Scroll to explore",
        s1=("Approach", ("The scans are already there.", "The reserve is not yet read.")),
        s1p=("Before chemotherapy or stem cell transplantation for a haematological cancer, almost every patient has a CT or PET/CT and most have a brain MRI. These scans show muscle, fat, spine and white matter, yet after staging they are rarely read again.",
             "Chronological age separates resilience only roughly. Geriatric assessment captures the difference but takes time. 4A4P tests whether this gap can be closed without an extra scan or extra radiation."),
        s2=("Eight domains", ("Four of anatomy.", "Four of performance.")),
        s2side="Four measures from imaging, four from the patient. Every definition, boundary and known error is written down before data collection.",
        grup_a="4A · Imaging", grup_p="4P · Bedside", atlas="4A4P / Domain atlas", tanim="Definition",
        tur_a="Anatomy · from imaging", tur_p="Performance · at the bedside", hata="Known measurement error", onceden="Definition written in advance",
        s3=("Question", ("Three models.", "One question.")),
        s3p="<b>Population:</b> aged 60 or older, haematological cancer, before chemotherapy or stem cell transplantation.<br><br><b>Outcome:</b> death within 90 days of the first treatment dose, or a new need for help in at least one basic activity of daily living.",
        durum="In research · no results yet",
        modeller=[("Clinical model", "M1", "Age, sex, ECOG, comorbidity burden and a disease-specific index."),
                  ("+ Performance", "M2", "The four bedside tests are added. <em>Do they add value?</em>"),
                  ("+ Anatomy", "M3", "The four imaging domains are added. <em>The main question: does imaging add anything?</em>")],
        mnot="One model is fitted; diagnosis group and treatment type enter as covariates, and calibration is reported separately in each subgroup.",
        s4=("Principles", ("Rules first.", "Results after.")),
        ilkeler=[("Archive first.", "After ethics approval the work starts with retrospective records; the model is then tested again in a prospective cohort."),
                 ("Rules in advance.", "Measurement definitions and the analysis plan are registered, with dates, before the data are examined."),
                 ("Images stay in-house.", "Segmentation runs on a local computer; images are not sent to the cloud and no identities are stored."),
                 ("No invented numbers.", "A value that cannot be measured stays empty with its reason. No coefficient or risk score is published before validation.")],
        s5=("Roadmap", ("Design today.", "Evidence tomorrow.")),
        s5side="This page describes the study design. No patient data have been processed yet.",
        yol=[("ok", "Done", "Eight domains and sources", "Definitions written; key sources read in the primary publications."),
             ("on", "Ongoing", "Protocol and preregistration", "Sample, data dictionary and analysis plan."),
             ("on", "Ongoing", "Imaging pipeline", "Built on openly licensed CT data; two runs on the same scan give identical results."),
             ("", "Next", "Ethics approval", "Application for the retrospective archive arm."),
             ("", "Next", "Archive arm", "Feasibility, reproducibility, M1 → M2 → M3."),
             ("", "Next", "Validation", "Prospective cohort and an independent sample.")],
        s6=("Sources", ("The studies", "it builds on.")),
        s6side="Most were done in other patient groups. 4A4P tests whether their findings hold in haematology.",
        kaynak=[("Ying et al. 2024", "Osteoporos Sarcopenia 10:78–83", "All trunk muscle from sternum to coccyx.", "10.1016/j.afos.2024.04.001"),
                ("Ullrich et al. 2026 · PETAL", "Blood Adv 10:5995–6006", "CT sarcopenia, non-relapse mortality and haematotoxicity in DLBCL.", "10.1182/bloodadvances.2026020504"),
                ("Liu et al. 2019", "Blood", "Gait speed and survival in older patients with haematological cancer.", "10.1182/blood.2019000758"),
                ("Armenian et al. 2019", "J Natl Cancer Inst", "CT sarcopenia before allogeneic transplantation.", "10.1093/jnci/djy231"),
                ("Merli et al. 2021", "J Clin Oncol", "The Elderly Prognostic Index in older patients with DLBCL.", "10.1200/JCO.20.02465"),
                ("Cobbing et al. 2025", "J Geriatr Oncol 16:102201", "Performance tests in older patients with cancer.", "10.1016/j.jgo.2025.102201"),
                ("Inzitari et al. 2009 · LADIS", "BMJ 339:b2477", "White matter changes and disability.", "10.1136/bmj.b2477")],
        f1="Research dedicated to the reserve of older patients.", yukari="Top",
        f2="4A4P is a research project, not a clinical decision tool.",
        sec_tr='<a href="/" data-dil="tr">TR</a>', sec_en='<span>EN</span>',
    ),
}

OK = '<svg class="arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M2 8h12M9 3l5 5-5 5"/></svg>'
CAPRAZ = '<svg class="arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M4 12 12 4M5 4h7v7"/></svg>'
ASAGI = '<svg class="arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M8 2v12M3 9l5 5 5-5"/></svg>'
YUKARI = '<svg class="arrow" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M8 14V2M3 7l5-5 5 5"/></svg>'
LOGO = ('<svg viewBox="0 0 30 30" aria-hidden="true">'
        + "".join(f'<rect x="{3 + (i % 4) * 6.5}" y="{8 + (i // 4) * 8}" width="4.5" height="5" rx="1" fill="{c}"/>'
                  for i, c in enumerate(["var(--gold)"] * 4 + ["var(--sage)"] * 4))
        + "</svg>")
IKON = [  # ilkeler: arşiv, kalem, kilit, ölçü
    '<svg viewBox="0 0 26 26"><rect x="3" y="5" width="20" height="5" rx="1"/><path d="M5 10v11h16V10M10 14h6"/></svg>',
    '<svg viewBox="0 0 26 26"><path d="M5 21l2-6L18 4l4 4-11 11-6 2zM15 7l4 4"/></svg>',
    '<svg viewBox="0 0 26 26"><rect x="5" y="11" width="16" height="11" rx="1.5"/><path d="M9 11V8a4 4 0 0 1 8 0v3M13 15v3"/></svg>',
    '<svg viewBox="0 0 26 26"><path d="M3 20h20M6 20v-4M10 20v-7M14 20v-5M18 20v-9"/><circle cx="20" cy="5" r="2"/></svg>',
]


def e(s: str) -> str:
    return html.escape(s, quote=True)


def halka(cx, cy, r1, r2, a0, a1):
    """Halka dilimi yolu (derece)."""
    def p(r, a):
        t = math.radians(a)
        return f"{cx + r * math.cos(t):.2f} {cy + r * math.sin(t):.2f}"
    return (f"M{p(r2, a0)} A{r2} {r2} 0 0 1 {p(r2, a1)} L{p(r1, a1)} "
            f"A{r1} {r1} 0 0 0 {p(r1, a0)} Z")


def kadran(d: dict, i: int) -> str:
    c, r1, r2, bos = 240, 150, 196, 1.6
    parca = []
    for a in ALANLAR:
        a0 = ACI[a["kod"]] + bos
        a1 = ACI[a["kod"]] + 45 - bos
        orta = math.radians(ACI[a["kod"]] + 22.5)
        lx, ly = c + 173 * math.cos(orta), c + 173 * math.sin(orta)
        parca.append(
            f'<g class="sector {a["tur"]}" data-kod="{a["kod"]}" data-ad="{e(a["ad"][i])}" tabindex="0" role="button" aria-label="{a["kod"]} {e(a["ad"][i])}">'
            f'<path d="{halka(c, c, r1, r2, a0, a1)}" stroke-width="1"/>'
            f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle">{a["kod"]}</text></g>')
    tikler = []
    for k in range(120):
        a = math.radians(k * 3)
        uz = 14 if k % 15 == 0 else 6
        r0 = 210
        tikler.append(f'<line x1="{c + r0 * math.cos(a):.1f}" y1="{c + r0 * math.sin(a):.1f}" '
                      f'x2="{c + (r0 + uz) * math.cos(a):.1f}" y2="{c + (r0 + uz) * math.sin(a):.1f}"/>')
    return f'''<svg viewBox="0 0 480 480" role="img" aria-label="{e(d["dial_title"])}">
  <circle cx="240" cy="240" r="236" fill="none" stroke="var(--night-line)" stroke-dasharray="2 6"/>
  <g class="ticks" stroke="var(--on-night-2)" stroke-opacity="0.45" stroke-width="1">{"".join(tikler)}</g>
  <circle cx="240" cy="240" r="140" fill="none" stroke="var(--night-line)"/>
  <line x1="104" y1="240" x2="376" y2="240" stroke="var(--night-line)"/>
  {"".join(parca)}
  <text class="axis" x="240" y="128" text-anchor="middle">{e(d["ax_a"])}</text>
  <text class="axis" x="240" y="362" text-anchor="middle">{e(d["ax_p"])}</text>
  <text class="core-sub" id="core-sub" x="240" y="196" text-anchor="middle">{e(d["dial_sub"])}</text>
  <text class="core-code" id="core-code" x="240" y="256" text-anchor="middle">4A4P</text>
  <text class="core-name" id="core-name" x="240" y="292" text-anchor="middle">{e(d["dial_name"])}</text>
</svg>'''


def mini(kod: str) -> str:
    c, r1, r2 = 100, 72, 92
    parca = []
    for a in ALANLAR:
        on = a["kod"] == kod
        renk = "var(--bronze)" if a["tur"] == "a" else "var(--sage-d)"
        parca.append(f'<path d="{halka(c, c, r1, r2, ACI[a["kod"]] + 2, ACI[a["kod"]] + 43)}" fill="{renk}" '
                     f'fill-opacity="{0.85 if on else 0.08}" stroke="{renk}" stroke-opacity="{1 if on else 0.35}"/>')
    return (f'<svg viewBox="0 0 200 200" aria-hidden="true"><circle cx="100" cy="100" r="64" fill="none" stroke="var(--line)"/>'
            f'{"".join(parca)}<text class="big" x="100" y="122" text-anchor="middle">{kod}</text></svg>')


def sayfa(dil: str) -> str:
    d, i = T[dil], (0 if dil == "tr" else 1)
    nav = "".join(f'<a href="#{k}">{e(v)}</a>' for k, v in d["nav"])

    def sekme(a, ilk):
        return (f'<li><button class="tab" role="tab" id="tab-{a["kod"]}" aria-controls="pan-{a["kod"]}" '
                f'aria-selected="{"true" if ilk else "false"}" data-kod="{a["kod"]}"><span class="c">{a["kod"]}</span>'
                f'<span>{e(a["ad"][i])}</span>{OK}</button></li>')
    tabs_a = "".join(sekme(a, a["kod"] == "A1") for a in ALANLAR if a["tur"] == "a")
    tabs_p = "".join(sekme(a, False) for a in ALANLAR if a["tur"] == "p")
    paneller = "".join(f'''<article class="panel" role="tabpanel" id="pan-{a["kod"]}" aria-labelledby="tab-{a["kod"]}" data-kod="{a["kod"]}">
        <div class="panel-top"><span class="label">{e(d["atlas"])}</span><span class="kind {a["tur"]}">{e(d["tur_a"] if a["tur"] == "a" else d["tur_p"])}</span></div>
        <div class="panel-main"><div class="glyph">{mini(a["kod"])}</div><div>
          <h4>{e(a["baslik"][i])}</h4><p>{e(a["metin"][i])}</p>
          <div class="chips">{"".join(f"<span>{e(c)}</span>" for c in a["cip"][i])}</div></div></div>
        <div class="panel-foot"><span><b>{e(d["hata"])}</b>{e(a["hata"][i])}</span><span class="label">{e(d["onceden"])}</span></div>
      </article>''' for a in ALANLAR)
    modeller = "".join(f'<li class="reveal" style="--d:{k * 90}ms"><span class="n">0{k + 1}</span><h3>{e(m[0])}</h3><span class="tag">{m[1]}</span><p>{m[2]}</p></li>'
                       for k, m in enumerate(d["modeller"]))
    ilkeler = "".join(f'<li class="reveal" style="--d:{k * 90}ms">{IKON[k]}<h3>{e(r[0])}</h3><p>{e(r[1])}</p></li>' for k, r in enumerate(d["ilkeler"]))
    yol = "".join(f'<li class="{s} reveal" style="--d:{k * 70}ms"><span class="dot"></span><span class="st">{e(st)}</span><h3>{e(b)}</h3><p>{e(m)}</p></li>'
                  for k, (s, st, b, m) in enumerate(d["yol"]))
    kaynak = "".join(f'<li><div><b>{e(a)}</b> · {e(j)}<br>{e(n)}<br><a href="https://doi.org/{doi}" rel="noopener">doi:{doi}</a></div></li>'
                     for a, j, n, doi in d["kaynak"])
    yonlendir = ('if (!t && !/^tr/i.test(navigator.language || "")) location.replace("/en/");' if dil == "tr"
                 else 'if (!t && /^tr/i.test(navigator.language || "")) location.replace("/");')
    return f'''<!doctype html>
<html lang="{d["lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(d["title"])}</title>
<meta name="description" content="{e(d["desc"])}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0b1214">
<link rel="alternate" hreflang="tr" href="https://4a4p.com/">
<link rel="alternate" hreflang="en" href="https://4a4p.com/en/">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/manrope-variable.woff" as="font" type="font/woff" crossorigin>
<link rel="stylesheet" href="/assets/site.css">
<script>
  document.documentElement.classList.add("js");
  try {{ var t = localStorage.getItem("4a4p-dil"); {yonlendir} }} catch (e) {{}}
</script>
</head>
<body>
<div class="progress" id="progress"></div>
<header class="top">
  <div class="wrap">
    <a class="brand" href="{d["kok"]}" aria-label="4A4P">{LOGO}<span>4A<b>4</b>P</span></a>
    <nav>{nav}</nav>
    <div class="lang">{d["sec_tr"]}{d["sec_en"]}</div>
  </div>
</header>

<section class="hero dark">
  <div class="wrap hero-grid">
    <div>
      <p class="label eyebrow reveal">{e(d["eyebrow"])}</p>
      <h1 class="display reveal" style="--d:120ms">{e(d["h1"][0])}<em>{e(d["h1"][1])}</em></h1>
      <p class="lead reveal" style="--d:260ms">{e(d["lead"])}</p>
      <div class="cta reveal" style="--d:380ms">
        <a class="btn" href="#alanlar">{e(d["btn"])}{OK}</a>
        <a class="link" href="#soru">{e(d["link"])}{CAPRAZ}</a>
      </div>
    </div>
    <figure class="dial reveal" style="--d:200ms">
      {kadran(d, i)}
      <figcaption class="dial-note"><span><i></i>{e(d["dial_note"][0])}</span><span>{e(d["dial_note"][1])}</span></figcaption>
    </figure>
  </div>
  <div class="hero-bar"><div class="wrap">
    <span>{e(d["bar"])}</span>
    <div class="feats">{"".join(f"<span>{e(f)}</span>" for f in d["feats"])}</div>
    <a class="down" href="#yaklasim">{e(d["down"])}{ASAGI}</a>
  </div></div>
</section>

<section class="sec light" id="yaklasim">
  <div class="wrap intro">
    <p class="label reveal"><span class="n">01 /</span>{e(d["s1"][0])}</p>
    <div>
      <h2 class="display reveal">{e(d["s1"][1][0])}<em>{e(d["s1"][1][1])}</em></h2>
      <div class="body"><p class="reveal" style="--d:100ms">{e(d["s1p"][0])}</p><p class="reveal" style="--d:200ms">{e(d["s1p"][1])}</p></div>
    </div>
  </div>
</section>

<section class="sec light alt" id="alanlar">
  <div class="wrap">
    <p class="label reveal"><span class="n">02 /</span>{e(d["s2"][0])}</p>
    <div class="head-row">
      <h2 class="display reveal">{e(d["s2"][1][0])}<em>{e(d["s2"][1][1])}</em></h2>
      <p class="side reveal" style="--d:120ms">{e(d["s2side"])}</p>
    </div>
    <div class="atlas reveal">
      <div class="tabs" role="tablist" aria-orientation="vertical">
        <h3>{e(d["grup_a"])}</h3><ul>{tabs_a}</ul>
        <h3>{e(d["grup_p"])}</h3><ul>{tabs_p}</ul>
      </div>
      <div class="panels">{paneller}</div>
    </div>
  </div>
</section>

<section class="sec dark" id="soru">
  <div class="wrap">
    <p class="label reveal"><span class="n">03 /</span>{e(d["s3"][0])}</p>
    <div class="question" style="margin-top:34px">
      <div>
        <h2 class="display reveal">{e(d["s3"][1][0])}<em>{e(d["s3"][1][1])}</em></h2>
        <p class="lead reveal" style="--d:120ms">{d["s3p"]}</p>
        <span class="status reveal" style="--d:200ms">{e(d["durum"])}</span>
      </div>
      <div>
        <ol class="models">{modeller}</ol>
        <p class="models-note reveal">{e(d["mnot"])}</p>
      </div>
    </div>
  </div>
</section>

<section class="sec light" id="ilkeler">
  <div class="wrap">
    <p class="label reveal"><span class="n">04 /</span>{e(d["s4"][0])}</p>
    <h2 class="display reveal" style="margin-top:34px">{e(d["s4"][1][0])}<em>{e(d["s4"][1][1])}</em></h2>
    <ul class="rules">{ilkeler}</ul>
  </div>
</section>

<section class="sec dark" id="yol">
  <div class="wrap">
    <p class="label reveal"><span class="n">05 /</span>{e(d["s5"][0])}</p>
    <div class="head-row">
      <h2 class="display reveal">{e(d["s5"][1][0])}<em>{e(d["s5"][1][1])}</em></h2>
      <p class="side reveal" style="--d:120ms">{e(d["s5side"])}</p>
    </div>
    <ol class="road">{yol}</ol>
  </div>
</section>

<section class="sec light" id="kaynaklar">
  <div class="wrap">
    <p class="label reveal"><span class="n">06 /</span>{e(d["s6"][0])}</p>
    <div class="head-row" style="margin-bottom:0">
      <h2 class="display reveal">{e(d["s6"][1][0])}<em>{e(d["s6"][1][1])}</em></h2>
      <p class="side reveal" style="--d:120ms">{e(d["s6side"])}</p>
    </div>
    <ol class="refs reveal">{kaynak}</ol>
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="row1">
      <a class="brand" href="{d["kok"]}" aria-label="4A4P">{LOGO}<span>4A<b>4</b>P</span></a>
      <p>{e(d["f1"])}</p>
      <a class="up" href="#">{e(d["yukari"])}{YUKARI}</a>
    </div>
    <div class="row2">
      <span>{e(d["f2"])}</span>
      <span class="sp"><a href="https://entorina.com" rel="noopener">entorina.com ↗</a><a href="https://geriatri.net" rel="noopener">geriatri.net ↗</a><span>© 2026 4A4P</span></span>
    </div>
  </div>
</footer>
<script src="/assets/site.js" defer></script>
</body>
</html>
'''


def main():
    (KOK / "index.html").write_text(sayfa("tr"), encoding="utf-8")
    (KOK / "en").mkdir(exist_ok=True)
    (KOK / "en" / "index.html").write_text(sayfa("en"), encoding="utf-8")
    print("yazıldı: index.html, en/index.html")


if __name__ == "__main__":
    main()
