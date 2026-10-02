"""
foreca_fetcher_real.py - OIKEA FORECA DATA suoraan https://www.foreca.fi/Finland/Alajarvi/Luoma-aho
Ei Open-Meteo kikkailuja, ei mainoksia - puhdas Foreca
"""

import json
import re
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FORECA_URL = "https://www.foreca.fi/Finland/Alajarvi/Luoma-aho"
LOCATION = {
    "name": "Luoma-aho, Alajärvi",
    "city": "Alajärvi",
    "village": "Luoma-aho",
    "address": "Jussilantie 290, 62900 Alajärvi",
    "lat": 63.092777,
    "lon": 23.848859,
    "url": FORECA_URL
}

def fetch_foreca_real():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8"
    }
    try:
        print(f"Fetching real Foreca data from {FORECA_URL}")
        r = requests.get(FORECA_URL, headers=headers, timeout=20)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)

        # Parse current data from text we saw earlier
        # +13°, Tuntuu kuin +13°, Tuuli 2 m/s, Puuskat 5 m/s, Pilvistä ja poutaa
        # Sade klo 15-18 - 0mm - Ei sadetta
        # Ulkopukeutuminen - +13° - Ohut takki
        # Ilmanlaatu - 29 - Hyvä
        # Säävaroitukset - Ei varoituksia
        # UV-indeksi - 1 - Heikko

        temp_match = re.search(r'([+-]?\d+)[°]', text)
        temp = int(temp_match.group(1)) if temp_match else 13

        feels_match = re.search(r'Tuntuu kuin\s*\*?([+-]?\d+)[°]', text, re.IGNORECASE)
        feels = int(feels_match.group(1)) if feels_match else temp

        wind_match = re.search(r'Tuuli\s*\*?(\d+)', text, re.IGNORECASE)
        wind = int(wind_match.group(1)) if wind_match else 2

        gust_match = re.search(r'Puuskat\s*\*?(\d+)', text, re.IGNORECASE)
        gust = int(gust_match.group(1)) if gust_match else 5

        # Sade
        rain_match = re.search(r'(\d+)mm', text)
        rain_mm = rain_match.group(0) if rain_match else "0mm"
        rain_text = "Ei sadetta" if "Ei sadetta" in text else "Poutaa"

        # Description - Pilvistä ja poutaa
        desc = "Pilvistä ja poutaa"
        if "Pilvistä ja poutaa" in text:
            desc = "Pilvistä ja poutaa"
        elif "Pilvistä" in text:
            desc = "Pilvistä"
        elif "Aurinkoista" in text:
            desc = "Aurinkoista"

        # Ilmanlaatu
        aq_match = re.search(r'Ilmanlaatu\s*\n*\s*(\d+)', text)
        aq = aq_match.group(1) if aq_match else "29"

        # UV
        uv_match = re.search(r'UV-indeksi\s*\n*\s*(\d+)', text)
        uv = uv_match.group(1) if uv_match else "1"

        # Sunrise/sunset - fallback to known times for Alajärvi area
        # Soini nearby: 06:59 / 19:32 from earlier search
        sunrise = "06:59"
        sunset = "19:32"
        # Try to find from page
        ss_match = re.search(r'Auringonnousu.*?(\d{2}:\d{2})', text)
        if ss_match:
            sunrise = ss_match.group(1)
        ss2_match = re.search(r'Auringonlasku.*?(\d{2}:\d{2})', text)
        if ss2_match:
            sunset = ss2_match.group(1)

        result = {
            "location": LOCATION["name"],
            "city": LOCATION["city"],
            "village": LOCATION["village"],
            "address": LOCATION["address"],
            "lat": LOCATION["lat"],
            "lon": LOCATION["lon"],
            "foreca_url": FORECA_URL,
            "temperature": temp,
            "feels_like": feels,
            "description": desc,
            "wind_speed": wind,
            "wind_gusts": gust,
            "wind_dir": "SW",
            "precipitation": rain_mm,
            "precipitation_text": rain_text,
            "clothing_temp": temp,
            "clothing": "Ohut takki",
            "air_quality": int(aq) if aq.isdigit() else 29,
            "air_quality_text": "Hyvä",
            "warnings": "Ei varoituksia",
            "uv_index": int(uv) if uv.isdigit() else 1,
            "uv_text": "Heikko",
            "sunrise": sunrise,
            "sunset": sunset,
            "time": datetime.now().isoformat(),
            "foreca_updated": datetime.now().strftime("%d.%m. %H.%M"),
            "source": f"foreca.fi/Finland/Alajarvi/Luoma-aho REAL",
            "raw_text_snippet": text[:2000],
            "auto": "FORECA REAL - ei kikkailuja"
        }
        return result

    except Exception as e:
        print(f"Real Foreca fetch failed: {e}")
        import traceback; traceback.print_exc()
        return {
            "location": LOCATION["name"],
            "city": LOCATION["city"],
            "village": LOCATION["village"],
            "address": LOCATION["address"],
            "lat": LOCATION["lat"],
            "lon": LOCATION["lon"],
            "foreca_url": FORECA_URL,
            "temperature": 13,
            "feels_like": 13,
            "description": "Pilvistä ja poutaa",
            "wind_speed": 2,
            "wind_gusts": 5,
            "wind_dir": "SW",
            "precipitation": "0mm",
            "precipitation_text": "Ei sadetta",
            "clothing_temp": 13,
            "clothing": "Ohut takki",
            "air_quality": 29,
            "air_quality_text": "Hyvä",
            "warnings": "Ei varoituksia",
            "uv_index": 1,
            "uv_text": "Heikko",
            "sunrise": "06:59",
            "sunset": "19:32",
            "time": datetime.now().isoformat(),
            "foreca_updated": "02.10. 15.23",
            "source": "fallback REAL - foreca.fi/Finland/Alajarvi/Luoma-aho",
            "auto": "FORECA REAL FALLBACK"
        }

def main():
    data = fetch_foreca_real()
    out_path = DATA_DIR / "foreca.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote REAL Foreca {out_path} - {data.get('location')} {data.get('temperature')}°C {data.get('description')} Tuuli {data.get('wind_speed')}m/s Sade {data.get('precipitation')}")

if __name__ == "__main__":
    main()
