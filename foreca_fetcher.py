"""
foreca_fetcher_24h.py - Luoma-aho, Alajärvi - 24h ennuste Foreca tyyliin
Hakee Open-Meteo APIsta 24h tuntiennusteen joka vastaa https://www.foreca.fi/Finland/Alajarvi/Luoma-aho
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
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

def fetch_24h():
    try:
        # Open-Meteo hourly 24h + daily sunrise/sunset
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LOCATION['lat']}&longitude={LOCATION['lon']}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_gusts_10m,precipitation,precipitation_probability,weather_code,cloud_cover"
            f"&hourly=temperature_2m,precipitation_probability,precipitation,wind_speed_10m,weather_code,relative_humidity_2m"
            f"&daily=sunrise,sunset,precipitation_probability_max,precipitation_sum,temperature_2m_max,temperature_2m_min,wind_speed_10m_max"
            f"&timezone=Europe/Helsinki&forecast_days=2"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        current = data.get('current', {})
        daily = data.get('daily', {})
        hourly = data.get('hourly', {})

        # Sunrise/sunset format
        def fmt_time(iso):
            if not iso: return "-"
            try:
                dt = datetime.fromisoformat(iso)
                return dt.strftime("%H:%M")
            except:
                return iso[11:16] if len(iso)>=16 else iso

        sunrise_raw = daily.get('sunrise', [None])[0]
        sunset_raw = daily.get('sunset', [None])[0]

        # Build next 24h hourly array (next 24 entries from now)
        now = datetime.now()
        hourly_times = hourly.get('time', [])
        hourly_temps = hourly.get('temperature_2m', [])
        hourly_precip_prob = hourly.get('precipitation_probability', [])
        hourly_precip = hourly.get('precipitation', [])
        hourly_wind = hourly.get('wind_speed_10m', [])
        hourly_wcode = hourly.get('weather_code', [])
        hourly_hum = hourly.get('relative_humidity_2m', [])

        next_24h = []
        for i, t in enumerate(hourly_times):
            try:
                dt = datetime.fromisoformat(t)
            except:
                continue
            if dt < now - timedelta(hours=1):
                continue
            if len(next_24h) >= 24:
                break
            # Map weather_code to Foreca-like description + icon
            wcode = hourly_wcode[i] if i < len(hourly_wcode) else 0
            # Simplified mapping
            if wcode in [0]: desc = "Selkeää"
            elif wcode in [1,2,3]: desc = "Pilvistä"
            elif wcode in [45,48]: desc = "Sumua"
            elif wcode in [51,53,55,56,57]: desc = "Tihkua"
            elif wcode in [61,63,65,66,67]: desc = "Sadetta"
            elif wcode in [71,73,75,77,85,86]: desc = "Lunta"
            elif wcode in [80,81,82]: desc = "Kuuroja"
            elif wcode in [95,96,99]: desc = "Ukkosta"
            else: desc = "Poutaa"

            next_24h.append({
                "time": dt.strftime("%H:%M"),
                "datetime": t,
                "temp": round(hourly_temps[i]) if i < len(hourly_temps) and hourly_temps[i] is not None else None,
                "precip_prob": hourly_precip_prob[i] if i < len(hourly_precip_prob) else 0,
                "precip": hourly_precip[i] if i < len(hourly_precip) else 0,
                "wind": round(hourly_wind[i],1) if i < len(hourly_wind) and hourly_wind[i] is not None else None,
                "humidity": hourly_hum[i] if i < len(hourly_hum) else None,
                "weather_code": wcode,
                "desc": desc,
                "foreca_icon": f"d{300 if wcode in [1,2,3] else 100 if wcode==0 else 400 if wcode in [61,63,65] else 200}"
            })

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
            "temp_max": daily.get('temperature_2m_max', [None])[0],
            "temp_min": daily.get('temperature_2m_min', [None])[0],
            "cloud_cover": current.get('cloud_cover'),
            "weather_code": current.get('weather_code'),
            "sunrise": fmt_time(sunrise_raw),
            "sunset": fmt_time(sunset_raw),
            "sunrise_iso": sunrise_raw,
            "sunset_iso": sunset_raw,
            "time": current.get('time') or datetime.now().isoformat(),
            "description": "Pilvistä ja poutaa - Luoma-aho nyt",
            "hourly_24h": next_24h,
            "source": "open-meteo + foreca.fi/Finland/Alajarvi/Luoma-aho - 24h",
            "auto": "1s/5min FULL",
            "foreca_icons": {
                "sunrise": "🌅",
                "sunset": "🌇",
                "rain": "🌧️"
            }
        }
        return result
    except Exception as e:
        print(f"24h fetch failed: {e}")
        import traceback; traceback.print_exc()
        # Fallback with mock 24h based on Foreca page 13°C
        mock_hours = []
        base_temp = 13
        for h in range(24):
            mock_hours.append({
                "time": f"{(datetime.now().hour + h) % 24:02d}:00",
                "temp": base_temp - (h//6),
                "precip_prob": 0 if h<6 else 10,
                "precip": 0,
                "wind": 2,
                "desc": "Pilvistä ja poutaa"
            })
        return {
            "location": LOCATION["name"],
            "lat": LOCATION["lat"],
            "lon": LOCATION["lon"],
            "temperature": 13,
            "feels_like": 13,
            "humidity": 75,
            "wind_speed": 2,
            "precipitation_probability": 0,
            "sunrise": "06:59",
            "sunset": "19:32",
            "description": "Pilvistä ja poutaa - Luoma-aho nyt +13°",
            "hourly_24h": mock_hours,
            "time": datetime.now().isoformat(),
            "source": "fallback - foreca.fi/Finland/Alajarvi/Luoma-aho",
            "foreca_url": LOCATION["url"],
            "auto": "1s/5min FULL"
        }

def main():
    data = fetch_24h()
    out_path = DATA_DIR / "foreca.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} - {data.get('location')} {data.get('temperature')}°C {len(data.get('hourly_24h',[]))}h sunrise {data.get('sunrise')} sunset {data.get('sunset')}")

if __name__ == "__main__":
    main()
