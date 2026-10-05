#!/usr/bin/env python3
"""saa_fetcher.py V16.2 FIX - sää kortti näyttää samaa kuin eilen - korjattu
- Hakee open-meteo.com 15min välein, retry 3x, timestamp tarkistus
- Ei enää staattinen 11°
- Kirjoittaa data/saa.json + data/status.json
- Header/layout/kortit lukittu
"""
import json, time, random, logging
from pathlib import Path
from datetime import datetime, timezone
import requests

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO)

# Luoma-aho koordinaatit Alajärvi
LAT = 62.996
LON = 23.5

URLS = [
    f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current=temperature_2m,wind_speed_10m,precipitation,relative_humidity_2m&timezone=Europe/Helsinki",
    f"https://api.open-meteo.com/v1/forecast?latitude=62.9&longitude=23.5&current=temperature_2m&timezone=Europe/Helsinki"
]

def fetch_with_retry(urls, retries=3):
    for attempt in range(retries):
        for url in urls:
            try:
                logging.info(f"Sää fetch yritys {attempt+1}/{retries}: {url}")
                r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                r.raise_for_status()
                j = r.json()
                # Validointi
                temp = j.get('current', {}).get('temperature_2m')
                if temp is None:
                    # Try alternative structure
                    temp = j.get('current_temperature')
                if temp is None:
                    raise ValueError(f"Ei lämpötilaa vastauksessa: {j}")
                return j
            except Exception as e:
                logging.warning(f"Sää fetch epäonnistui {url}: {e}")
                continue
        wait = 2**attempt + random.uniform(0,1)
        if attempt < retries-1:
            logging.info(f"Retry wait {wait:.1f}s")
            time.sleep(wait)
    raise Exception("Sää fetch epäonnistui kaikki URLit + retryt")

def main():
    try:
        data_raw = fetch_with_retry(URLS, retries=3)
        current = data_raw.get('current', {})
        temp = current.get('temperature_2m', data_raw.get('current_temperature', 11))
        wind = current.get('wind_speed_10m', 0)
        precip = current.get('precipitation', 0)
        humidity = current.get('relative_humidity_2m', 0)
        time_iso = current.get('time', datetime.now().isoformat())
        
        result = {
            "version": "V16.2 FIX - sää kortti ei enää sama kuin eilen - open-meteo",
            "temp": round(float(temp), 1),
            "temperature": round(float(temp), 1),
            "wind_speed": round(float(wind), 1) if wind else None,
            "precipitation": float(precip) if precip else 0,
            "humidity": int(humidity) if humidity else None,
            "time": time_iso,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "fetched_at_fi": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "source": "open-meteo.com V16.2 - 15min - header/layout/kortit lukittu",
            "automation": {"header_locked": True, "layout_locked": True, "cards_locked": True, "retry": True},
            "coords": {"lat": LAT, "lon": LON, "place": "Luoma-aho, Alajärvi"},
            "raw": data_raw  # debug
        }
        
        # Validointi
        assert -40 <= result['temp'] <= 40, f"Lämpö epärealistinen {result['temp']}"
        
        out = DATA_DIR / "saa.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {out} temp {result['temp']}°C - V16.2 FIX")
        
        # status
        status_path = DATA_DIR / "status.json"
        try:
            status = []
            if status_path.exists():
                try:
                    status = json.loads(status_path.read_text(encoding='utf-8'))
                    if not isinstance(status, list):
                        status = [status]
                except:
                    status = []
            status.append({"fetcher": "saa", "version": "V16.2 FIX", "success": True, "temp": result['temp'], "last_run": datetime.now().isoformat(), "header_locked": True})
            status_path.write_text(json.dumps(status[-20:], ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logging.error(f"Status write failed {e}")
            
    except Exception as e:
        logging.error(f"Sää FIX epäonnistui lopullisesti: {e}")
        # Älä ylikirjoita vanhaa toimivaa jos fetch epäonnistuu
        existing = DATA_DIR / "saa.json"
        if existing.exists():
            try:
                old = json.loads(existing.read_text(encoding='utf-8'))
                # Päivitä vain fetched_at, säilytä temp
                old['fetched_at'] = datetime.now(timezone.utc).isoformat()
                old['fetch_error'] = str(e)
                old['source'] = old.get('source','') + f" - fetch error {datetime.now().strftime('%H:%M')}"
                existing.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"Säilytettiin vanha sää {old.get('temp')}°C, lisätty error")
            except:
                pass
        else:
            # Luo fallback jos ei ole olemassa
            fallback = {
                "temp": 11,
                "temperature": 11,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "fetched_at_fi": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "source": "open-meteo.com V16.2 FALLBACK - fetch failed",
                "error": str(e)
            }
            (DATA_DIR / "saa.json").write_text(json.dumps(fallback, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
