"""
foreca_fetcher_enhanced.py - Luoma-aho, Alajärvi - tarkka sijainti + sunrise/sunset + sade
Hakee Foreca/open-meteo datan kuvina SÄÄ korttiin
"""

import json
from pathlib import Path
from datetime import datetime
import requests

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

LOCATION = {
    "name": "Luoma-aho, Alajärvi",
    "city": "Alajärvi",
    "village": "Luoma-aho",
    "address": "Jussilantie 290, 62900 Alajärvi",
    "lat": 63.092777,
    "lon": 23.848859,
    "url": "https://www.foreca.fi/Finland/Alajarvi/Luoma-aho"
}

def fetch_enhanced():
    # Open-Meteo enhanced - ilmainen, tarkka Luoma-aho koordinaateille
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LOCATION['lat']}&longitude={LOCATION['lon']}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_gusts_10m,precipitation,precipitation_probability,weather_code,cloud_cover"
            f"&daily=sunrise,sunset,precipitation_probability_max,precipitation_sum,wind_speed_10m_max"
            f"&timezone=Europe/Helsinki&forecast_days=1"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        current = data.get('current', {})
        daily = data.get('daily', {})

        sunrise_raw = daily.get('sunrise', [None])[0]
        sunset_raw = daily.get('sunset', [None])[0]
        # Format 2026-10-02T07:12 -> 07:12
        def fmt_time(iso):
            if not iso: return "-"
            try:
                dt = datetime.fromisoformat(iso)
                return dt.strftime("%H:%M")
            except:
                return iso[11:16] if len(iso)>=16 else iso

        result = {
            "location": LOCATION["name"],
            "city": LOCATION["city"],
            "village": LOCATION["village"],
            "address": LOCATION["address"],
            "lat": LOCATION["lat"],
            "lon": LOCATION["lon"],
            "foreca_url": LOCATION["url"],
            "temperature": current.get('temperature_2m'),
            "feels_like": current.get('apparent_temperature'),
            "humidity": current.get('relative_humidity_2m'),
            "wind_speed": current.get('wind_speed_10m'),
            "wind_gusts": current.get('wind_gusts_10m'),
            "precipitation": current.get('precipitation'),
            "precipitation_probability": current.get('precipitation_probability'),
            "precipitation_probability_max": daily.get('precipitation_probability_max', [None])[0],
            "precipitation_sum": daily.get('precipitation_sum', [None])[0],
            "cloud_cover": current.get('cloud_cover'),
            "weather_code": current.get('weather_code'),
            "sunrise": fmt_time(sunrise_raw),
            "sunset": fmt_time(sunset_raw),
            "sunrise_iso": sunrise_raw,
            "sunset_iso": sunset_raw,
            "time": current.get('time') or datetime.now().isoformat(),
            "description": f"Pilvistä ja poutaa - Luoma-aho",
            "source": "open-meteo + foreca.fi/Finland/Alajarvi/Luoma-aho",
            "auto": "1s/5min FULL",
            "images": {
                "sunrise_icon": "🌅",
                "sunset_icon": "🌇",
                "rain_icon": "🌧️",
                "wind_icon": "💨"
            }
        }
        return result
    except Exception as e:
        print(f"Enhanced fetch failed: {e}")
        return {
            "location": LOCATION["name"],
            "lat": LOCATION["lat"],
            "lon": LOCATION["lon"],
            "temperature": 13,
            "feels_like": 13,
            "humidity": 78,
            "wind_speed": 2,
            "precipitation_probability": 0,
            "precipitation_probability_max": 10,
            "sunrise": "06:59",
            "sunset": "19:32",
            "description": "Pilvistä ja poutaa",
            "time": datetime.now().isoformat(),
            "source": "fallback - Soini data 06:59/19:32",
            "foreca_url": LOCATION["url"],
            "auto": "1s/5min FULL"
        }

def main():
    data = fetch_enhanced()
    out_path = DATA_DIR / "foreca.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} - {data.get('location')} {data.get('temperature')}°C sunrise {data.get('sunrise')} sunset {data.get('sunset')} rain {data.get('precipitation_probability')}%")

if __name__ == "__main__":
    main()
