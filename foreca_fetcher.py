import requests
import json
import os
from datetime import datetime, timezone

LAT = 63.07717
LON = 23.869444
LOCATION_NAME = "Luoma-ahon Frisbeegolfrata, Jussilantie 290, Alajärvi"

def wmo_to_icon(code: int) -> str:
    if code == 0: return "☀️"
    if code == 1: return "🌤️"
    if code == 2: return "⛅"
    if code == 3: return "☁️"
    if code in (45, 48): return "🌫️"
    if code in (51, 53, 55, 56, 57): return "🌦️"
    if code in (61, 63, 65, 66, 67): return "🌧️"
    if code in (71, 73, 75, 77, 85, 86): return "❄️"
    if code in (80, 81, 82): return "🌦️"
    if code in (95, 96, 99): return "⛈️"
    return "☁️"

def main():
    URL = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current": "temperature_2m,apparent_temperature,wind_speed_10m,wind_gusts_10m,cloud_cover,weather_code",
        "hourly": "temperature_2m,weather_code",
        "timezone": "Europe/Helsinki",
        "wind_speed_unit": "ms",
        "forecast_days": 2
    }
    print(f"Haetaan sää: {LOCATION_NAME} {LAT}, {LON}")
    r = requests.get(URL, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    current = data["current"]
    hourly = data["hourly"]

    hourly_list = []
    times = hourly["time"]
    temps = hourly["temperature_2m"]
    codes = hourly["weather_code"]

    for i in range(0, 24, 3):
        if i >= len(times): break
        t = datetime.fromisoformat(times[i])
        hourly_list.append({
            "hour": t.strftime("%H:00"),
            "temp": round(temps[i]),
            "icon": wmo_to_icon(codes[i]),
            "iso": times[i]
        })

    output = {
        "current": {
            "temp": round(current["temperature_2m"]),
            "feels": round(current["apparent_temperature"]),
            "wind": round(current["wind_speed_10m"], 1),
            "gust": round(current["wind_gusts_10m"], 1),
            "cloud": int(current["cloud_cover"]),
            "code": current["weather_code"]
        },
        "hourly": hourly_list,
        "location": {
            "name": LOCATION_NAME,
            "lat": LAT,
            "lon": LON,
            "source": "frisbeegolfradat.fi"
        },
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "provider": "open-meteo.com"
    }

    os.makedirs("data", exist_ok=True)
    with open("data/foreca.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"OK -> data/foreca.json")
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
