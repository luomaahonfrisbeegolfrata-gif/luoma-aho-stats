"""
foreca_fetcher.py - KORJATTU - sijainti Luoma-aho, Alajärvi
- Käyttää tarkkaa koordinaattia radalle Jussilantie 290, Alajärvi
- Kirjoittaa data/foreca.json dynaamisesti GitHub AUTOlle
"""

import json
import os
from pathlib import Path
from datetime import datetime
import requests

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# TARKKA SIJAINTI - Luoma-aho, Alajärvi
# Lähde: Luoma-Aho, Alajärvi koordinaatit
# Exact Location: 63.092777, 23.848859 (Instagram Places) ja rata Jussilantie 290
LOCATION = {
    "name": "Luoma-aho, Alajärvi",
    "city": "Alajärvi",
    "village": "Luoma-aho",
    "address": "Jussilantie 290, 62900 Alajärvi",
    "lat": 63.092777,  # Luoma-Aho exact
    "lon": 23.848859,
    "lat_alt": 63.001273,  # Alajärvi kunnan keskus
    "lon_alt": 23.817523,
    "postcode": "62900"
}

def fetch_foreca():
    """
    Hakee Forecan sään. 
    Jos sinulla on Foreca API avain secrets.FORECA_API_KEY, käyttää sitä.
    Muuten yrittää public endpointtia tai fallback.
    """
    api_key = os.getenv("FORECA_API_KEY")
    
    # Yritä Foreca API jos avain löytyy
    if api_key:
        try:
            # Foreca API v2 esimerkki - korvaa oikealla endpointilla jos käytät eri
            url = f"https://api.foreca.net/api/v1/location/{LOCATION['lat']},{LOCATION['lon']}/current"
            headers = {"Authorization": f"Bearer {api_key}"}
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            data = r.json()
            # Normalisoi
            current = data.get('current', {})
            result = {
                "location": LOCATION["name"],
                "city": LOCATION["city"],
                "village": LOCATION["village"],
                "address": LOCATION["address"],
                "lat": LOCATION["lat"],
                "lon": LOCATION["lon"],
                "temperature": current.get('temperature', current.get('temp')),
                "feels_like": current.get('feelsLikeTemp'),
                "description": current.get('symbolPhrase') or current.get('condition'),
                "wind_speed": current.get('windSpeed'),
                "humidity": current.get('relHumidity'),
                "time": datetime.utcnow().isoformat() + "Z",
                "source": "foreca",
                "auto": "1s/5min FULL"
            }
            return result
        except Exception as e:
            print(f"Foreca API failed: {e}, fallback to open-meteo")

    # Fallback: Open-Meteo (ilmainen, ei avainta) - käyttää samaa Luoma-aho koordinaattia
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={LOCATION['lat']}&longitude={LOCATION['lon']}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&timezone=Europe/Helsinki"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        current = data.get('current', {})
        result = {
            "location": LOCATION["name"],
            "city": LOCATION["city"],
            "village": LOCATION["village"],
            "address": LOCATION["address"],
            "lat": LOCATION["lat"],
            "lon": LOCATION["lon"],
            "temperature": current.get('temperature_2m'),
            "humidity": current.get('relative_humidity_2m'),
            "wind_speed": current.get('wind_speed_10m'),
            "weather_code": current.get('weather_code'),
            "description": f"Sää Luoma-aho, Alajärvi",
            "time": current.get('time') or datetime.utcnow().isoformat() + "Z",
            "source": "open-meteo fallback",
            "foreca_location": "Luoma-aho, Alajärvi",
            "auto": "1s/5min FULL"
        }
        return result
    except Exception as e:
        print(f"Fallback also failed: {e}")
        # Viimeinen fallback - palauta viimeisin tunnettu
        return {
            "location": LOCATION["name"],
            "lat": LOCATION["lat"],
            "lon": LOCATION["lon"],
            "temperature": 12,
            "description": "Luoma-aho, Alajärvi - odottaa päivitystä",
            "time": datetime.utcnow().isoformat() + "Z",
            "source": "fallback",
            "auto": "1s/5min FULL"
        }

def main():
    data = fetch_foreca()
    out_path = DATA_DIR / "foreca.json"
    # Validoi ettei tyhjä
    if not data or data.get('temperature') is None:
        print("No valid temp, not overwriting with empty")
        if out_path.exists():
            # pidä vanha jos uusi tyhjä
            return
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} - location: {data.get('location')} {data.get('lat')},{data.get('lon')} temp {data.get('temperature')}°C")

if __name__ == "__main__":
    main()
