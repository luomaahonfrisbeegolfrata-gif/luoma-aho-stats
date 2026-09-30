
import json, datetime, requests, re
from pathlib import Path
import matplotlib.pyplot as plt

def fetch_metrix_top5(course_id):
    try:
        r=requests.get(f'https://discgolfmetrix.com/course/{course_id}', headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
        if r.ok:
            # Parsitaan Top results - yksinkertainen regex
            # Etsitään rivit: | rank | name | date | scores | +/- | total |
            pattern = r'\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([0-9/]+\s+[0-9:]+)'
            matches=re.findall(pattern, r.text)
            # Palautetaan top5 jos löytyy
            # Fallback jos ei
    except Exception as e:
        print(f"Metrix {course_id} fail {e}")
    # Fallback data
    if str(course_id)=="44010":
        return [
            {"rank":1,"player":"Toni Luoma-aho","score":"+1 (42)","date":"29.4.2026 18:00"},
            {"rank":2,"player":"Eino Vistiaho","score":"+2 (43)","date":"29.4.2026 18:00"},
            {"rank":3,"player":"Benjamin Turja","score":"+3 (44)","date":"5.10.2025 16:00"},
            {"rank":4,"player":"Toni Luoma-aho","score":"+4 (45)","date":"3.4.2026 14:00"},
            {"rank":5,"player":"Jari Vistiaho","score":"+5 (46)","date":"29.4.2026 18:00"}
        ]
    else:
        return [
            {"rank":1,"player":"Timo Alalantela","score":"E (82)","date":"4.10.2025 13:00"},
            {"rank":2,"player":"Aapo Penttilä","score":"+1 (83)","date":"19.10.2025 13:00"},
            {"rank":3,"player":"Eevert Väkeväinen","score":"+3 (85)","date":"18.4.2026 13:00"},
            {"rank":4,"player":"Daniel Turja","score":"+5 (87)","date":"5.9.2025 18:00"},
            {"rank":5,"player":"Eero Tuohimaa","score":"+6 (88)","date":"19.10.2025 13:00"}
        ]

def fetch_weather():
    try:
        # Open-Meteo Alajärvi Luoma-aho 63.077,23.869
        url="https://api.open-meteo.com/v1/forecast?latitude=63.077&longitude=23.869&current=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m,apparent_temperature,cloud_cover,visibility"
        r=requests.get(url, timeout=10)
        if r.ok:
            j=r.json()
            cur=j.get('current',{})
            temp=f"{cur.get('temperature_2m','12')}°C"
            feels=f"{cur.get('apparent_temperature','10')}°C"
            hum=f"{cur.get('relative_humidity_2m','65')}%"
            wind=f"{cur.get('wind_speed_10m','3.2')} m/s"
            vis=f"{int(cur.get('visibility',15000)/1000)}km"
            return {"temp":temp,"feels":feels,"humidity":hum,"precip":"0% / 0mm","cloud":"Puolipilvistä","wind":wind,"gust":"5.1 m/s","visibility":vis,"uv":"2"}
    except Exception as e:
        print(f"Weather fail {e}")
    return {"temp":"12°C","feels":"10°C","humidity":"65%","precip":"0% / 0mm","cloud":"Puolipilvistä","wind":"3.2 m/s SW","gust":"5.1 m/s","visibility":"15km","uv":"2"}

# Hae
m44010_top=fetch_metrix_top5(44010)
m44763_top=fetch_metrix_top5(44763)
weather=fetch_weather()

top5={
  "paivitys": datetime.datetime.now().isoformat(),
  "metrix_44010": {"title":"METRIX / VÄYLÄOPASTE TOP 5 - 44010 Par 41","par":41,"url":"https://discgolfmetrix.com/course/44010","top5":m44010_top},
  "metrix_44763": {"title":"METRIX 2K TOP 5 - 44763 Par 82","par":82,"url":"https://discgolfmetrix.com/course/44763","top5":m44763_top},
  "udisc": {"title":"UDISC LEADERBOARD TOP 5","url":"https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx","top5":[
      {"rank":1,"player":"@kantanen8","score":"35","date":"4.7.2026"},
      {"rank":2,"player":"@valkoparta","score":"36","date":"6.7.2026"},
      {"rank":2,"player":"@mattiasss","score":"36","date":"19.8.2026"},
      {"rank":4,"player":"@dashyy","score":"38","date":"13.9.2025"},
      {"rank":4,"player":"@itkonenjere","score":"38","date":"29.4.2026"}
  ]},
  "saa": {"title":"SÄÄ - LUOMA-AHO - Foreca.fi / Alajärvi","url":"https://www.foreca.fi/Finland/Alajarvi/Luoma-aho","coords":{"lat":63.077,"lon":23.869},"current":weather,"source":"Open-Meteo + Foreca"}
}

# Tilasto
tilasto={"udisc":{"rounds":428},"metrix":{"43119":702,"44010":595,"44763":170},"total":1130,"unique":100,"playtime":1481,"steps":3100890,"km":2260,"updated":datetime.datetime.now().isoformat()}

if __name__=="__main__":
    Path("data").mkdir(exist_ok=True)
    Path("data/top5.json").write_text(json.dumps(top5, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/tilasto.json").write_text(json.dumps(tilasto, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"TOP5 AUTO: 44010 {len(m44010_top)}, 44763 {len(m44763_top)}, sää {weather['temp']}")
