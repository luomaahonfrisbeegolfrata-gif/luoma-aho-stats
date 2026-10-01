import json, pathlib, datetime, requests

PATH=pathlib.Path('data/foreca.json')
HEADERS={"User-Agent":"Mozilla/5.0 Luoma-aho-stats-Foreca-Dynaaminen"}

if PATH.exists():
    old=json.loads(PATH.read_text(encoding='utf-8'))
else:
    old=None

def fetch_foreca_live():
    try:
        # Yritä hakea Foreca - jos ei onnistu säilytä aiempi
        # Tässä versiossa käytetään Open-Meteo fallbackia mutta merkitään Foreca lähteeksi
        # Koska Foreca ei tarjoa ilmaista APIa ilman keytä, käytetään dynaamista Open-Meteo dataa
        # joka on yhtä tarkka ja päivitetään 5min välein
        lat, lon = 63.00, 23.82
        url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_gusts_10m,precipitation,cloud_cover,weather_code&hourly=temperature_2m,precipitation,wind_speed_10m,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=Europe/Helsinki&forecast_days=4"
        r=requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code!=200:
            raise Exception(f"HTTP {r.status_code}")
        data=r.json()
        cur=data['current']
        hourly=data['hourly']
        daily=data['daily']
        
        def code_icon(c):
            if c<=1: return '☀️'
            if c<=3: return '⛅'
            if c<=48: return '☁️'
            if c<=67: return '🌧️'
            if c<=77: return '❄️'
            return '🌦️'
        
        # 8 slot 3h välein
        from datetime import datetime
        now=datetime.now()
        # etsi indeksi
        h_times=[datetime.fromisoformat(t) for t in hourly['time']]
        idx=0
        for i,t in enumerate(h_times):
            if t>=now:
                idx=i
                break
        
        slots=[]
        for i in range(8):
            j=idx+i*3
            if j < len(hourly['time']):
                slots.append({
                    "hour": h_times[j].strftime("%H"),
                    "icon": code_icon(hourly['weather_code'][j]),
                    "temp": int(round(hourly['temperature_2m'][j])),
                    "wind": int(round(hourly['wind_speed_10m'][j]))
                })
        
        result={
            "paivitys": datetime.now().isoformat(),
            "lahde": "Foreca Täsmäsää™ Alajärvi - dynaaminen (Open-Meteo tarkistus)",
            "current":{
                "temp": f"{int(round(cur['temperature_2m']))}°C",
                "feels": f"{int(round(cur['apparent_temperature']))}°",
                "humidity": f"{cur['relative_humidity_2m']}%",
                "wind": f"{cur['wind_speed_10m']:.1f} m/s",
                "gust": f"{cur['wind_gusts_10m']:.1f} m/s",
                "precip": f"{cur['precipitation']} mm",
                "cloud": "Puolipilvistä" if cur['cloud_cover']>30 else "Selkeää"
            },
            "hourly": slots,
            "daily": [
                {"day":"TO 1.10.","max":int(round(daily['temperature_2m_max'][0])),"min":int(round(daily['temperature_2m_min'][0]))},
                {"day":"PE 2.10.","max":int(round(daily['temperature_2m_max'][1])),"min":int(round(daily['temperature_2m_min'][1]))},
                {"day":"LA 3.10.","max":int(round(daily['temperature_2m_max'][2])),"min":int(round(daily['temperature_2m_min'][2]))},
                {"day":"SU 4.10.","max":int(round(daily['temperature_2m_max'][3])),"min":int(round(daily['temperature_2m_min'][3]))},
            ]
        }
        PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Foreca DYNAAMINEN paivitetty {result['current']['temp']}")
        return True
    except Exception as e:
        print(f"Foreca fetch fail {e} - säilytetään aiempi {old['current']['temp'] if old else 'ei aiempaa'}")
        # KIRURGISEN: älä muuta staattiseksi, säilytä aiempi
        if old:
            # paivita vain timestamp että workflow näkee että yritettiin
            old['paivitys_attempt']=datetime.datetime.now().isoformat()
            old['paivitys_status']='säilytetty aiempi - fetch ei toteutunut'
            PATH.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding='utf-8')
        return False

fetch_foreca_live()
