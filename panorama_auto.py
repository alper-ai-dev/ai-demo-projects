"""
Panorama News — Otomatik Haber Sistemi
Sabah 08:00 - Akşam 22:00 arası, 20 dakikada bir çalışır.
"""

import feedparser
import requests
import openai
import schedule
import time
import json
import os
import base64
import hashlib
import logging
from datetime import datetime

# ─── AYARLAR — BURAYA GİR ──────────────────────────────────────
OPENROUTER_API_KEY = "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"
WP_URL             = "https://panorama-news.de"
WP_USER            = "editor-panorama"
WP_PASS = "QWQx ZaWd 0kAn pfiE XWkB 8XSO"

PEXELS_KEY         = ""   # opsiyonel

BASLANGIC_SAATI    = 8
BITIS_SAATI        = 22
ARALIK_DAKIKA      = 20

# ─── KATEGORİ SLUG EŞLEŞTİRMESİ ───────────────────────────────
# AI şu isimleri kullanır → kod bu slug'ları WP'de arar
KATEGORI_SLUGLAR = {
    "GÜNDEM":        "gundem",
    "DÜNYA":         "dunya",
    "EKONOMİ":       "ekonomi",
    "SPOR":          "spor",
    "MAGAZİN":       "magazin-2",
    "YAŞAM":         "yasam",
    "AVRUPA":        "avrupa",
    "TEKNOLOJİ":     "teknoloji",
    "KÜLTÜR-SANAT":  "kultur-sanat",
    "TOPLUM-SAĞLIK": "toplum-saglik",
}

# ─── RSS KAYNAKLARI ────────────────────────────────────────────
RSS_KAYNAKLARI = {
    "BBC Türkçe":        "https://feeds.bbci.co.uk/turkish/rss.xml",
    "Deutsche Welle TR": "https://rss.dw.com/rdf/rss-tur-all",
    "Euronews TR":       "https://tr.euronews.com/rss",
    "T24 Dünya":         "https://t24.com.tr/rss/haber/dunya",
    "Sözcü Dünya":       "https://www.sozcu.com.tr/feeds-rss-category-dunya",
    "Google Almanya":    "https://news.google.com/rss/search?q=Almanya&hl=tr&gl=TR&ceid=TR:tr",
    "Google Gurbetci":   "https://news.google.com/rss/search?q=Almanya+Turk+gurbetci&hl=tr&gl=TR&ceid=TR:tr",
    "Google Bundesliga": "https://news.google.com/rss/search?q=Bundesliga&hl=tr&gl=TR&ceid=TR:tr",
    "Google TR Unlu":    "https://news.google.com/rss/search?q=Turkiye+unlu+olay&hl=tr&gl=TR&ceid=TR:tr",
    "Google Dunya":      "https://news.google.com/rss/search?q=dunya+gundem+olay&hl=tr&gl=TR&ceid=TR:tr",
}

# ─── LOG ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%d.%m %H:%M",
    handlers=[
        logging.FileHandler("panorama_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger()

GECMIS_DOSYA = "yayinlananlar.json"

def gecmisi_yukle():
    if os.path.exists(GECMIS_DOSYA):
        with open(GECMIS_DOSYA, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def gecmise_ekle(hid):
    gecmis = gecmisi_yukle()
    gecmis.add(hid)
    gecmis = set(list(gecmis)[-500:])
    with open(GECMIS_DOSYA, "w", encoding="utf-8") as f:
        json.dump(list(gecmis), f)

def haber_id(baslik, link):
    return hashlib.md5((baslik + link).encode()).hexdigest()[:12]

def ai_client():
    return openai.OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

# ─── KATEGORİ ID BULTCU ────────────────────────────────────────
_kategori_cache = {}

def kategori_id_bul(ai_kategori):
    """AI'ın verdiği kategori adından WP kategori ID'sini bul."""
    if ai_kategori in _kategori_cache:
        return _kategori_cache[ai_kategori]
    slug = KATEGORI_SLUGLAR.get(ai_kategori, "gundem")
    try:
        endpoint = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/categories"
        r = requests.get(endpoint, params={"slug": slug}, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data:
                _kategori_cache[ai_kategori] = data[0]["id"]
                return data[0]["id"]
    except Exception as e:
        log.warning(f"Kategori ID bulunamadı ({slug}): {e}")
    return None  # WP varsayılan kullanır

# ─── FİLTRE PROMPT ─────────────────────────────────────────────
FILTRE_PROMPT = """Sen Almanya'daki Türklere yönelik 'Panorama News' haber sitesinin editörüsün.

## KABUL ET:
- Almanya haberleri (kaza, suç, sosyal olay, ekonomi, gündem, siyaset)
- Almanya-Türkiye ilişkileri, gurbetçi/diaspora haberleri
- Avrupa / AB haberleri
- Almanya'da futbol (Bundesliga, Alman kulüpler)
- Türkiye'den: ünlü isimlerin karıştığı olaylar, büyük kaza/patlama/afet, şaşırtıcı/ilginç olaylar
- Dünyadan: büyük olaylar, ünlü isimlerin haberleri, kaza/patlama/afet
- Ekonomi, teknoloji, sağlık, kültür-sanat, yaşam

## REDDET:
- Türkiye iç siyaseti (AKP, CHP, MHP, meclis, parti, seçim)
- ABD iç siyaseti (Trump iç politika, Kongre, ABD seçimleri)
- Türkiye'den sıradan yerel haberler (mahalle, belediye, trafik)
- Türkiye sporu (Süper Lig, Türk kulüpler)
- Seks / müstehcen içerik
- Reklam / etkinlik duyurusu

## KATEGORİ SEÇ:
GÜNDEM → Almanya/Avrupa güncel
DÜNYA → uluslararası olaylar
EKONOMİ → ekonomi, finans
SPOR → futbol, spor
MAGAZİN → ünlüler, magazin
YAŞAM → sağlık, yaşam
AVRUPA → AB, Avrupa haberleri
TEKNOLOJİ → teknoloji, bilim
KÜLTÜR-SANAT → kültür, sanat
TOPLUM-SAĞLIK → toplum, sağlık

Sadece şu formatta yanıt ver:
KARAR: KABUL veya REDDET
KATEGORİ: (kategori adı)
PUAN: (1-5)"""

def haberi_filtrele(baslik, ozet):
    try:
        client = ai_client()
        resp = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            max_tokens=60,
            messages=[
                {"role": "system", "content": FILTRE_PROMPT},
                {"role": "user", "content": f"Başlık: {baslik}\nÖzet: {ozet[:300]}"}
            ]
        )
        yanit = resp.choices[0].message.content.strip()
        karar = "KABUL" if "KABUL" in yanit else "REDDET"

        kategori = "GÜNDEM"
        for k in KATEGORI_SLUGLAR:
            if k in yanit:
                kategori = k
                break

        puan = 3
        for satir in yanit.split("\n"):
            if "PUAN:" in satir:
                try:
                    puan = int(satir.split(":")[1].strip())
                except:
                    pass

        return karar, kategori, puan
    except Exception as e:
        log.warning(f"Filtre hatası: {e}")
        return "KABUL", "GÜNDEM", 3

# ─── YAZIM PROMPT ──────────────────────────────────────────────
YAZIM_PROMPT = """Sen Panorama News Almanya için Türkçe haber yazan editörsün.
Hedef kitle: Almanya'daki Türkler.

YAZIM KURALLARI:
- Profesyonel Türkçe gazetecilik dili
- İlk cümle BOLD olmayacak
- Özne-yüklem sırası
- Her paragraf maksimum 275 karakter
- "yarattı", "bugün", "resmen", "mucize" kelimelerini KULLANMA
- Polisiye/suç haberinde "iddia" ifadesi kullan
- 3-4 paragraf yaz
- Gurbetçiyi ilgilendiriyorsa öne çıkar

ÇIKTI FORMATI (sadece bu, başka hiçbir şey yazma):
BAŞLIK: (maksimum 60 karakter)
SPOT: (tam 140 karakter)
METİN:
(paragraflar)
ETİKETLER: (5 etiket virgülle)"""

def haberi_yeniden_yaz(baslik, ozet):
    try:
        client = ai_client()
        resp = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            max_tokens=1200,
            messages=[
                {"role": "system", "content": YAZIM_PROMPT},
                {"role": "user", "content": f"Başlık: {baslik}\nİçerik: {ozet[:800]}"}
            ]
        )
        return resp.choices[0].message.content
    except Exception as e:
        log.error(f"Yazım hatası: {e}")
        return None

def ai_ciktisini_ayristir(metin):
    if not metin:
        return None
    satirlar = metin.strip().split("\n")
    sonuc = {"baslik": "", "spot": "", "icerik": "", "etiketler": []}
    mod = None
    icerik_satirlari = []

    for satir in satirlar:
        if satir.startswith("BAŞLIK:"):
            sonuc["baslik"] = satir.replace("BAŞLIK:", "").strip()[:60]
        elif satir.startswith("SPOT:"):
            sonuc["spot"] = satir.replace("SPOT:", "").strip()[:140]
        elif satir.startswith("METİN:"):
            mod = "icerik"
            kalan = satir.replace("METİN:", "").strip()
            if kalan:
                icerik_satirlari.append(kalan)
        elif satir.startswith("ETİKETLER:"):
            mod = "etiket"
            ham = satir.replace("ETİKETLER:", "").strip()
            sonuc["etiketler"] = [e.strip() for e in ham.split(",") if e.strip()][:5]
        elif mod == "icerik" and not satir.startswith("ETİKETLER:"):
            icerik_satirlari.append(satir)

    sonuc["icerik"] = "\n".join(icerik_satirlari).strip()
    return sonuc

# ─── PEXELS ────────────────────────────────────────────────────
def pexels_fotograf(arama):
    if not PEXELS_KEY:
        return None
    try:
        headers = {"Authorization": PEXELS_KEY}
        r = requests.get(
            f"https://api.pexels.com/v1/search?query={arama}&per_page=1",
            headers=headers, timeout=8
        )
        if r.status_code == 200:
            photos = r.json().get("photos", [])
            if photos:
                return photos[0]["src"]["large2x"]
    except:
        pass
    return None

def wp_fotograf_yukle(img_url):
    try:
        img_data = requests.get(img_url, timeout=10).content
        endpoint = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/media"
        auth = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Disposition": 'attachment; filename="haber.jpg"',
            "Content-Type": "image/jpeg",
        }
        r = requests.post(endpoint, headers=headers, data=img_data, timeout=20)
        if r.status_code in (200, 201):
            return r.json().get("id")
    except Exception as e:
        log.warning(f"Fotoğraf hatası: {e}")
    return None

# ─── ETİKET ────────────────────────────────────────────────────
def etiket_id_al(etiket_adi, auth_header):
    endpoint = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/tags"
    headers = {"Authorization": auth_header, "Content-Type": "application/json"}
    r = requests.get(endpoint, params={"search": etiket_adi}, headers=headers, timeout=8)
    if r.status_code == 200:
        sonuclar = r.json()
        eslesen = [t for t in sonuclar if t.get("name","").lower() == etiket_adi.lower()]
        if eslesen:
            return eslesen[0]["id"]
    rc = requests.post(endpoint, headers=headers, json={"name": etiket_adi}, timeout=8)
    if rc.status_code in (200, 201):
        return rc.json()["id"]
    return None

# ─── WORDPRESS YAYINLA ─────────────────────────────────────────
def wordpress_yayinla(ayristirilmis, kategori_id, fotograf_id=None):
    endpoint = f"{WP_URL.rstrip('/')}/wp-json/wp/v2/posts"
    auth = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    auth_header = f"Basic {auth}"
    headers = {"Authorization": auth_header, "Content-Type": "application/json"}

    icerik_html = "".join(
        f"<p>{p.strip()}</p>"
        for p in ayristirilmis["icerik"].split("\n")
        if p.strip()
    )

    etiket_idleri = []
    for et in ayristirilmis["etiketler"]:
        eid = etiket_id_al(et, auth_header)
        if eid:
            etiket_idleri.append(eid)

    payload = {
        "title":      ayristirilmis["baslik"],
        "content":    icerik_html,
        "excerpt":    ayristirilmis["spot"],
        "status":     "draft",
        "tags":       etiket_idleri,
    }
    if kategori_id:
        payload["categories"] = [kategori_id]
    if fotograf_id:
        payload["featured_media"] = fotograf_id

    r = requests.post(endpoint, headers=headers, json=payload, timeout=25)
    if r.status_code in (200, 201):
        return r.json().get("link", "")
    else:
        raise Exception(f"WP {r.status_code}: {r.text[:150]}")

# ─── ANA DÖNGÜ ─────────────────────────────────────────────────
def haberleri_isle():
    saat = datetime.now().hour
    if saat < BASLANGIC_SAATI or saat >= BITIS_SAATI:
        log.info(f"Mesai dışı ({saat}:00), bekleniyor...")
        return

    log.info("=" * 55)
    log.info(f"Tarama: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    gecmis = gecmisi_yukle()

    # RSS çek
    haberler = []
    for kaynak, url in RSS_KAYNAKLARI.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                baslik = entry.get("title", "").strip()
                ozet   = entry.get("summary", entry.get("description", "")).strip()
                link   = entry.get("link", "")
                if baslik and link:
                    haberler.append({
                        "kaynak": kaynak,
                        "baslik": baslik,
                        "ozet":   ozet,
                        "link":   link,
                        "id":     haber_id(baslik, link)
                    })
        except Exception as e:
            log.warning(f"{kaynak} hatası: {e}")

    yeni = [h for h in haberler if h["id"] not in gecmis]
    log.info(f"Toplam {len(haberler)} haber | {len(yeni)} yeni")

    if not yeni:
        log.info("Yeni haber yok.")
        return

    # Filtrele ve puanla
    adaylar = []
    for haber in yeni[:25]:
        karar, kategori, puan = haberi_filtrele(haber["baslik"], haber["ozet"])
        if karar == "KABUL":
            haber["kategori"] = kategori
            haber["puan"]     = puan
            adaylar.append(haber)
            log.info(f"  ✅ [{kategori}] P:{puan} — {haber['baslik'][:50]}")
        else:
            log.info(f"  ❌ — {haber['baslik'][:50]}")
        time.sleep(1)

    if not adaylar:
        log.info("Uygun haber yok.")
        return

    # En yüksek puanlıyı seç
    adaylar.sort(key=lambda x: x["puan"], reverse=True)
    secilen = adaylar[0]
    log.info(f"Seçilen: [{secilen['kategori']}] {secilen['baslik']}")

    # Yeniden yaz
    ai_metin = haberi_yeniden_yaz(secilen["baslik"], secilen["ozet"])
    parsed   = ai_ciktisini_ayristir(ai_metin)

    if not parsed or not parsed["baslik"]:
        parsed = {
            "baslik":    secilen["baslik"][:60],
            "spot":      secilen["ozet"][:140],
            "icerik":    secilen["ozet"],
            "etiketler": []
        }

    # Fotoğraf
    fotograf_id = None
    if PEXELS_KEY:
        img_url = pexels_fotograf(parsed["baslik"].split()[0])
        if img_url:
            fotograf_id = wp_fotograf_yukle(img_url)

    # Kategori ID bul
    kat_id = kategori_id_bul(secilen["kategori"])

    # Yayınla
    try:
        link = wordpress_yayinla(parsed, kat_id, fotograf_id)
        gecmise_ekle(secilen["id"])
        log.info(f"🟢 YAYINLANDI → {link}")
    except Exception as e:
        log.error(f"🔴 Yayın hatası: {e}")

# ─── BAŞLAT ────────────────────────────────────────────────────
def basla():
    log.info("=" * 55)
    log.info("  Panorama News — Otomatik Sistem BAŞLADI")
    log.info(f"  Çalışma: {BASLANGIC_SAATI}:00 - {BITIS_SAATI}:00 | Her {ARALIK_DAKIKA} dk")
    log.info("=" * 55)

    haberleri_isle()

    schedule.every(ARALIK_DAKIKA).minutes.do(haberleri_isle)

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    basla()
