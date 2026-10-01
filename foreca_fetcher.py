import requests
import json
import os
from datetime import datetime, timezone

# OIKEA SIJAINTI - Luoma-ahon Frisbeegolfrata
LAT = 63.07717
LON = 23.869444
LOCATION_NAME = "Luoma-ahon Frisbeegolfrata, Jussilantie 290, Alajärvi"

# Open-Meteo - ilmainen, ei API-avainta, tarkat tuulet
# Foreca scraping hajoaa, tämä on stabiili
URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": LAT,
    "longitude": LON,
    "current": "temperature_2m,apparent_temperature,wind_speed_10m,wind_gusts_10m,cloud_cover,weather_code",
    "hourly": "temperature_2m,weather_code",
    "timezone": "Europe/Helsinki",
    "wind_speed_unit": "ms",  # m/s kuten Forecassa
    "forecast_days": 2
}

print(f"Haetaan sää: {LOCATION_NAME} {LAT}, {LON}")
r = requests.get(URL, params=params, timeout=15)
r.raise_for_status()
data = r.json()

current = data["current"]
hourly = data["hourly"]

# WMO koodi -> Foreca-tyylinen ikoni
def wmo_to_icon(code):
    if code == 0: return "01d"  # selkeää
    if code in [1,2]: return "02d"
    if code == 3: return "04d"
    if code in [45,48]: return "50d"
    if code in [51,53,55,61,63,65]: return "09d"
    if code in [71,73,75,77,85,86]: return "13d"
    if code in [80,81,82]: return "09d"
    if code in [95,96,99]: return "11d"
    return "02d"

# 24h ennuste 3h välein
hourly_list = []
times = hourly["time"]
temps = hourly["temperature_2m"]
codes = hourly["weather_code"]

# Etsi nyt-hetki
now_hour = datetime.now(timezone.utc).replace(tzinfo=None)
# Otetaan seuraavat 8 pistettä 3h välein
for i in range(0, 24, 3):
    idx = i
    if idx >= len(times): break
    t = datetime.fromisoformat(times[idx])
    hourly_list.append({
        "hour": t.strftime("%H:00"),
        "temp": round(temps[idx]),
        "icon": wmo_to_icon(codes[idx]),
        "iso": times[idx]
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
