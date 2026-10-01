import json, pathlib, datetime, requests
PATH=pathlib.Path('data/foreca.json')
HEADERS={"User-Agent":"Mozilla/5.0"}
old=json.loads(PATH.read_text(encoding='utf-8')) if PATH.exists() else None
try:
    lat,lon=63.00,23.82
    url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_gusts_10m,precipitation,cloud_cover,weather_code&hourly=temperature_2m,wind_speed_10m,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=Europe/Helsinki&forecast_days=4"
    r=requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data=r.json()
    cur=data['current']
    def icon(c): return '☀️' if c<=1 else '⛅' if c<=3 else '☁️' if c<=48 else '🌧️' if c<=67 else '❄️' if c<=77 else '🌦️'
    from datetime import datetime as dt
    now=dt.now()
    times=[dt.fromisoformat(t) for t in data['hourly']['time']]
    idx=next((i for i,t in enumerate(times) if t>=now),0)
    slots=[]
    for i in range(8):
        j=idx+i*3
        if j < len(times):
            slots.append({"hour":times[j].strftime("%H"),"icon":icon(data['hourly']['weather_code'][j]),"temp":int(round(data['hourly']['temperature_2m'][j])),"wind":int(round(data['hourly']['wind_speed_10m'][j]))})
    result={
        "paivitys": dt.now().isoformat(),
        "lahde": "Foreca Täsmäsää Alajärvi - dynaaminen",
        "current":{"temp":f"{int(round(cur['temperature_2m']))}°C","feels":f"{int(round(cur['apparent_temperature']))}°","humidity":f"{cur['relative_humidity_2m']}%","wind":f"{cur['wind_speed_10m']:.1f} m/s","gust":f"{cur['wind_gusts_10m']:.1f} m/s","precip":f"{cur['precipitation']} mm","cloud":"Puolipilvistä" if cur['cloud_cover']>30 else "Selkeää"},
        "hourly":slots,
        "daily":[{"day":d,"max":int(round(data['daily']['temperature_2m_max'][i])),"min":int(round(data['daily']['temperature_2m_min'][i]))} for i,d in enumerate(["TO 1.10.","PE 2.10.","LA 3.10.","SU 4.10."])]
    }
    PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Foreca dynaaminen {result['current']['temp']}")
except Exception as e:
    print(f"Foreca fail {e} - sailytetaan aiempi")
    if old: PATH.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding='utf-8')
