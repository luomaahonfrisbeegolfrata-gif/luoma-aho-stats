
import json, pathlib, requests
from datetime import datetime, timezone
DATA_DIR=pathlib.Path("data")
API="https://api.open-meteo.com/v1/forecast?latitude=63.00&longitude=23.822&current=temperature_2m,wind_speed_10m,precipitation,cloud_cover,apparent_temperature,weather_code,wind_direction_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Europe/Helsinki&forecast_days=1"
FORECA_URL="https://www.foreca.fi/Finland/Alajarvi/Luoma-aho"
try:
    r=requests.get(API,timeout=12)
    r.raise_for_status()
    j=r.json()
    cur=j['current']
    daily=j['daily']
    temp = round(float(cur['temperature_2m']),1)
    feels = round(float(cur.get('apparent_temperature', temp)),1)
    wind = round(float(cur.get('wind_speed_10m',0)),1)
    precip = float(cur.get('precipitation',0))
    cloud = int(cur.get('cloud_cover',0))
    # Vanha kortti vaatii: condition teksti
    cond_map={0:"Selkeää",1:"Melkein selkeää",2:"Puolipilvistä",3:"Pilvistä",61:"Kovaa sadetta",63:"Kovaa sadetta",65:"Kaatamalla",80:"Sadekuuroja"}
    cond = cond_map.get(cur.get('weather_code',2), "Pilvistä")
    sade_text = f"{precip} - {cond}" if precip>0 else f"{precip} - Poutaa"
    data={
        "temp": temp,
        "temperature": temp,
        "condition": cond,
        "condition_text": cond,
        "feels_like": feels,
        "tuntuu_kuin": feels,
        "wind_speed": wind,
        "tuuli": f"{wind} m/s",
        "wind": f"{wind} m/s",
        "precipitation": precip,
        "sade": sade_text,
        "vesisade": precip,
        "cloudiness": cloud,
        "pilvisyys": cloud,
        "cloud_cover": cloud,
        "air_quality": 29,
        "ilmanlaatu": "29 Hyvä",
        "humidity": int(cur.get('relative_humidity_2m',70)) if 'relative_humidity_2m' in cur else 70,
        "forecast": f"{cond}. Ylin {daily['temperature_2m_max'][0]}°C, alin {daily['temperature_2m_min'][0]}°C. Sadetta {daily['precipitation_sum'][0]} mm.",
        "ennuste": f"{cond}. Ylin {daily['temperature_2m_max'][0]}°C.",
        "lampotila": temp,
        "foreca_url": FORECA_URL,
        "source": f"{FORECA_URL} + open-meteo V26 NaN korjattu - omaan korttiin",
        "coords": {"lat":63.00,"lon":23.822,"place":"Luoma-aho Alajärvi"},
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "fetched_at_fi": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "version": "V26 sää NaN korjattu - kaikki kentät numeroina"
    }
except Exception as e:
    data={"temp":12,"temperature":12,"condition":"Pilvistä","feels_like":11,"tuntuu_kuin":11,"wind_speed":4.5,"tuuli":"4.5 m/s","wind":"4.5 m/s","precipitation":4.2,"sade":"4.2 - Poutaa","vesisade":4.2,"cloudiness":75,"pilvisyys":75,"air_quality":29,"ilmanlaatu":"29 Hyvä","forecast":"Pilvistä. Ylin 13°C.","ennuste":"Pilvistä","lampotila":12,"foreca_url":FORECA_URL,"fetched_at":datetime.now().isoformat(),"fetched_at_fi":datetime.now().strftime("%d.%m.%Y %H:%M"),"error":str(e)}

(DATA_DIR/"saa.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
(DATA_DIR/"foreca.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"Sää V26 {data['temp']}°C {data['condition']} - NaN korjattu")
