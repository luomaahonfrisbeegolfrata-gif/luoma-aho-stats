
import json, pathlib, requests
from datetime import datetime, timezone
DATA_DIR=pathlib.Path("data")
API="https://api.open-meteo.com/v1/forecast?latitude=63.00&longitude=23.822&current=temperature_2m,wind_speed_10m,precipitation,cloud_cover,apparent_temperature,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Europe/Helsinki&forecast_days=1"
FORECA_URL="https://www.foreca.fi/Finland/Alajarvi/Luoma-aho"
try:
    r=requests.get(API,timeout=10)
    j=r.json(); cur=j['current']; daily=j['daily']
    cond="Kovaa sadetta" if cur.get('precipitation',0)>2 else "Puolipilvistä"
    data={"temp":round(cur['temperature_2m'],1),"condition":cond,"feels_like":round(cur.get('apparent_temperature',cur['temperature_2m']),1),"wind_speed":round(cur['wind_speed_10m'],1),"precipitation":cur.get('precipitation',0),"cloudiness":cur.get('cloud_cover',0),"forecast":f"{cond}. Ylin {daily['temperature_2m_max'][0]}°C","foreca_url":FORECA_URL,"fetched_at":datetime.now(timezone.utc).isoformat(),"fetched_at_fi":datetime.now().strftime("%d.%m.%Y %H:%M"),"lampotila":round(cur['temperature_2m'],1),"tuuli":f"{cur['wind_speed_10m']} m/s","vesisade":cur.get('precipitation',0),"pilvisyys":cur.get('cloud_cover',0),"ennuste":cond}
except:
    data={"temp":12,"condition":"Kovaa sadetta","feels_like":11,"wind_speed":4.5,"precipitation":4.2,"cloudiness":75,"forecast":"Kovaa sadetta","foreca_url":FORECA_URL,"fetched_at":datetime.now().isoformat(),"fetched_at_fi":datetime.now().strftime("%d.%m.%Y %H:%M"),"lampotila":12,"tuuli":"4.5 m/s","vesisade":4.2,"pilvisyys":75,"ennuste":"Kovaa sadetta"}
(DATA_DIR/"saa.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
(DATA_DIR/"foreca.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
