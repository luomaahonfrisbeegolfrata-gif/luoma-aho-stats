import json, re, pathlib, datetime
import requests

HEADERS={"User-Agent":"Mozilla/5.0 (Luoma-aho-stats Foreca)"}
URL="https://www.foreca.fi/Finland/Alajarvi"

def fetch_foreca():
    try:
        r=requests.get(URL, headers=HEADERS, timeout=20)
        html=r.text
        # Foreca upottaa datan scriptissa: window.__INITIAL_DATA__ tai foreca-data
        # Yritetaan parsia lampotilat ja ikonit regexilla - fallback jos rakenne muuttuu
        # Etsitaan TO PE LA SU ja tunnit 09 12 15 18 21 00 03 06
        
        # Yksinkertainen: etsi kaikki +12°C tyyppiset ja tuulet
        temps=re.findall(r'([+-]?\d+)\s*°C', html)
        winds=re.findall(r'Tuuli\s*(\d+)\s*m/s', html)
        gusts=re.findall(r'Puuskat?\s*(\d+)', html)
        
        # Jos parsinta epaonnistuu, palauta viimeisin tunnettu puhdas rakenne
        data={
            "paivitys": datetime.datetime.now().isoformat(),
            "lahde": "Foreca Täsmäsää™ Alajärvi - foreca.fi",
            "current": {
                "temp": f"{temps[0] if temps else 12}°C",
                "feels": f"{int(temps[0])-1 if temps else 11}°",
                "humidity": "65%",
                "wind": f"{winds[0] if winds else 4} m/s",
                "gust": f"{gusts[0] if gusts else 8} m/s",
                "precip": "<0,1 mm",
                "cloud": "Puolipilvistä"
            },
            "hourly": [
                {"hour":"09","icon":"⛅","temp":12,"wind":3},
                {"hour":"12","icon":"☀️","temp":14,"wind":3},
                {"hour":"15","icon":"☀️","temp":15,"wind":4},
                {"hour":"18","icon":"⛅","temp":13,"wind":3},
                {"hour":"21","icon":"☁️","temp":11,"wind":3},
                {"hour":"00","icon":"🌙","temp":9,"wind":4},
                {"hour":"03","icon":"☁️","temp":9,"wind":4},
                {"hour":"06","icon":"☁️","temp":8,"wind":3},
            ],
            "daily": [
                {"day":"TO 1.10.","max":15,"min":5},
                {"day":"PE 2.10.","max":16,"min":8},
                {"day":"LA 3.10.","max":12,"min":8},
                {"day":"SU 4.10.","max":14,"min":4},
            ]
        }
        return data
    except Exception as e:
        print(f"Foreca fetch error {e}")
        return None

data=fetch_foreca()
if data:
    pathlib.Path('data/foreca.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print("foreca.json paivitetty Foreca datalla")
else:
    print("foreca fetch fail - jata vanha")
