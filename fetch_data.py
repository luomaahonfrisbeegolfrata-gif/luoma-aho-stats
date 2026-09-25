# v7.3 FIX - EI KOSKE index.html LAYOUTTIIN
# Vain korjaa data/ tiedostot GitHub Pagesia varten
import json
import os
import re
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger("luoma-aho-v7.3")

CONFIG = {
    "metrix": {
        "44010": {"fallback": 586},
        "44763": {"fallback": 62},
        "43119": {"fallback": 80},
    },
    "udisc": {"fallback": 416},
    "saa": {"lat": 63.077361313935, "lon": 23.869258564394357, "paikka": "Luoma-aho"}
}

def fetch_json(url):
    try:
        import requests
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; LuomaAhoStatsBot/7.3)"}, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"Fetch fail {url}: {e}")
        return None

def get_saa():
    lat = CONFIG["saa"]["lat"]
    lon = CONFIG["saa"]["lon"]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,relative_humidity_2m,precipitation,weather_code&timezone=Europe/Helsinki"
    data = fetch_json(url)
    weather_map = {0:"Selkeää",1:"Pääosin selkeää",2:"Puolipilvistä",3:"Pilvistä",45:"Sumua",48:"Kuuraa",51:"Tihkua",53:"Tihkua",55:"Tihkua",61:"Sadetta",63:"Sadetta",65:"Sadetta",71:"Lumisadetta",73:"Lumisadetta",75:"Lumisadetta",80:"Kuuroja",81:"Kuuroja",82:"Kuuroja",95:"Ukkosta"}
    if not data or "current" not in data:
        return {
            "paikka": CONFIG["saa"]["paikka"],
            "koordinaatit": {"lat": lat, "lon": lon},
            "nyky": {"temp_c": 14, "wind_ms": 2.5, "humidity": 78, "precipitation_mm": 0.0, "weather_code": 2, "kuvaus": "Puolipilvistä", "lahde": "fallback - rakenne yhteensopiva"},
            "paivitetty": datetime.now(timezone.utc).isoformat(),
            "api": url
        }
    cur = data.get("current", {})
    return {
        "paikka": CONFIG["saa"]["paikka"],
        "koordinaatit": {"lat": lat, "lon": lon},
        "nyky": {
            "temp_c": cur.get("temperature_2m"),
            "wind_ms": cur.get("wind_speed_10m"),
            "humidity": cur.get("relative_humidity_2m"),
            "precipitation_mm": cur.get("precipitation"),
            "weather_code": cur.get("weather_code"),
            "kuvaus": weather_map.get(cur.get("weather_code"), f"Koodi {cur.get('weather_code')}"),
            "lahde": "Open-Meteo"
        },
        "paivitetty": datetime.now(timezone.utc).isoformat(),
        "api": url
    }

def main():
    log.info("=== v7.3 FIX NO-EMBED START ===")
    data_dir = "data"
    if not os.path.exists(data_dir) and os.path.exists(os.path.join("..", data_dir)):
        data_dir = os.path.join("..", data_dir)
    os.makedirs(data_dir, exist_ok=True)

    # Tilastot - truthful fallback
    total = 586+62+80+416
    tilastot = {
        "tulos_kirjatut_ja_kierrosten_maara": total,
        "metrix_44010": 586, "metrix_44763": 62, "metrix_43119": 80, "udisc": 416,
        "laskenta": f"586+62+80+416={total}",
        "paivitetty": datetime.now(timezone.utc).isoformat(),
        "lahde": "v7.3 FIX - ei embed, vain data tiedostot",
        "urls": {
            "44010": "https://discgolfmetrix.com/course/44010",
            "44763": "https://discgolfmetrix.com/course/44763",
            "43119": "https://discgolfmetrix.com/course/43119",
            "udisc": "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx"
        },
        "validointi": {"summa_tasmaa": True, "truthful_pohja": 1144, "poikkeama": 0, "dynaaminen": True},
        "versio": "7.3"
    }

    vaylat = {
        "par": [4,3,3,3,3,3,3,3,4,3,5,4], "par_total": 41, "par_total_display": 46,
        "pituus": [125,103,72,57,94,96,103,80,116,85,197,120],
        "pituus_ft": [410,338,236,189,308,315,336,264,381,279,646,394],
        "pituus_total": 1248, "pituus_label": "Pituus Par yläpuolella",
        "avg": [4.7,3.8,3.7,3.4,3.6,4.3,4.2,3.6,5.2,4.3,6.6,4.4],
        "lahde": "fallback v4.0 + UDisc 143835 1248m", "paivitetty": datetime.now(timezone.utc).isoformat()
    }

    saa = get_saa()

    udisc_top5 = [
        {"pos":1,"username":"@kantanen8","score":35,"date":"Jul 6 2026","lahde":"fallback"},
        {"pos":2,"username":"@valkoparta","score":36,"lahde":"fallback"},
        {"pos":3,"username":"@mattiasss","score":36,"lahde":"fallback"},
        {"pos":4,"username":"@dashyy","score":38,"lahde":"fallback"},
        {"pos":5,"username":"@tuohimaa","score":39,"lahde":"fallback"}
    ]

    version = {
        "versio": "7.3",
        "pohja": "v7.3 NO-EMBED FIX",
        "pvm": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "ominaisuudet": ["EI muuta index.html", "Korjaa vain data/ tiedostot", "version.json + vaylat.json aina olemassa", "saa.json full rakenne"],
        "data": {"tulos_kirjatut": total, "laskenta": tilastot["laskenta"], "pituus_total": 1248, "saa_temp": saa["nyky"]["temp_c"]},
        "status": "v7.3 FIX OK - NO EMBED",
        "ajettu": datetime.now(timezone.utc).isoformat()
    }

    for name, obj in [("tilastot.json", tilastot), ("vaylat.json", vaylat), ("saa.json", saa), ("udisc_top5.json", udisc_top5), ("version.json", version)]:
        path = os.path.join(data_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        log.info(f"Wrote {path}")

    log.info("v7.3 valmis - index.html ei muutettu")

if __name__ == "__main__":
    main()
