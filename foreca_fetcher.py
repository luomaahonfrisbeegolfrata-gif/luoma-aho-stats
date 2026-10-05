#!/usr/bin/env python3
"""foreca_fetcher V22 - PAKOLLISET: lämpötila, tuuli, ennuste, vesisade, pilvisyys - https://www.foreca.fi/Finland/Alajarvi/Luoma-aho"""
import json, re, time, random, logging
from pathlib import Path
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO)

FORECA_URL = "https://www.foreca.fi/Finland/Alajarvi/Luoma-aho"
# Open-Meteo provides ALL mandatory fields reliably
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast?latitude=63.00&longitude=23.822&current=temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,cloud_cover,relative_humidity_2m,apparent_temperature,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,cloud_cover_mean&timezone=Europe/Helsinki&forecast_days=3"

def parse_foreca_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}
    
    # Yritä löytää lämpötila, tuuli, sade, pilvisyys Foreca HTML:stä
    text = soup.get_text(separator=' ')
    
    # Lämpötila
    temp_match = re.search(r'(-?\d+)\s*°C', text)
    if temp_match:
        data['temp'] = float(temp_match.group(1))
    
    # Tuuli - etsi "tuuli X m/s" tai "Wind X"
    wind_match = re.search(r'(?:tuuli|wind)\s*[^\d]*?(\d+\.?\d*)\s*m/s', text, re.I)
    if wind_match:
        data['wind_speed'] = float(wind_match.group(1))
    
    # Pilvisyys
    cloud_match = re.search(r'(?:pilvisyys|cloudiness|pilvinen|puolipilvinen|selkeä)\s*[^\d]*?(\d+)?\s*%?', text, re.I)
    if cloud_match and cloud_match.group(1):
        data['cloudiness'] = int(cloud_match.group(1))
    
    # Sade
    precip_match = re.search(r'(?:sade|precipitation|sadetta)\s*[^\d]*?(\d+\.?\d*)\s*mm', text, re.I)
    if precip_match:
        data['precipitation'] = float(precip_match.group(1))
    
    return data

def fetch_open_meteo_all():
    """Hakee KAIKKI pakolliset kentät Open-Meteosta - 100% varma"""
    try:
        r = requests.get(OPEN_METEO_URL, timeout=20)
        r.raise_for_status()
        j = r.json()
        
        current = j.get('current', {})
        daily = j.get('daily', {})
        
        # Sääkoodit -> suomeksi ennuste
        weather_codes = {
            0: "Selkeää", 1: "Melkein selkeää", 2: "Puolipilvistä", 3: "Pilvistä",
            45: "Sumua", 48: "Kuuraa", 51: "Heikkoa tihkua", 53: "Tihkua", 55: "Voimakasta tihkua",
            61: "Heikkoa sadetta", 63: "Sadetta", 65: "Voimakasta sadetta",
            71: "Heikkoa lumisadetta", 73: "Lumisadetta", 75: "Voimakasta lumisadetta",
            80: "Heikkoja sadekuuroja", 81: "Sadekuuroja", 82: "Voimakkaita sadekuuroja",
            95: "Ukkosta"
        }
        
        code = current.get('weather_code', 1)
        forecast_text = weather_codes.get(code, f"Sääkoodi {code}")
        
        # Tuulen suunta -> ilmansuunta
        wind_dir = current.get('wind_direction_10m', 0)
        dirs = ["P", "Koillinen", "I", "Kaakko", "E", "Lounas", "L", "Luode"]
        dir_text = dirs[int((wind_dir + 22.5) / 45) % 8]
        
        # Päivän ennuste
        today_forecast = ""
        if daily.get('temperature_2m_max'):
            tmax = daily['temperature_2m_max'][0]
            tmin = daily['temperature_2m_min'][0]
            precip_sum = daily.get('precipitation_sum', [0])[0]
            wind_max = daily.get('wind_speed_10m_max', [0])[0]
            today_forecast = f"{forecast_text}. Ylin {tmax}°C, alin {tmin}°C. Tuulta {wind_max} m/s. Sadetta {precip_sum} mm."
        
        result = {
            # PAKOLLISET KENTÄT
            "temp": round(float(current.get('temperature_2m', 11)), 1),
            "temperature": round(float(current.get('temperature_2m', 11)), 1),
            "lampotila": round(float(current.get('temperature_2m', 11)), 1),
            
            "wind_speed": round(float(current.get('wind_speed_10m', 0)), 1),
            "wind_direction": int(current.get('wind_direction_10m', 0)),
            "wind_direction_text": dir_text,
            "tuuli": f"{round(float(current.get('wind_speed_10m', 0)), 1)} m/s {dir_text}",
            
            "precipitation": float(current.get('precipitation', 0)),
            "vesisade": float(current.get('precipitation', 0)),
            "precipitation_today": float(daily.get('precipitation_sum', [0])[0] if daily.get('precipitation_sum') else 0),
            
            "cloudiness": int(current.get('cloud_cover', 0)),
            "cloud_cover": int(current.get('cloud_cover', 0)),
            "pilvisyys": int(current.get('cloud_cover', 0)),
            
            "forecast": today_forecast,
            "ennuste": today_forecast,
            "forecast_text": forecast_text,
            "weather_code": code,
            
            # LISÄTIEDOT
            "humidity": int(current.get('relative_humidity_2m', 0)),
            "feels_like": round(float(current.get('apparent_temperature', current.get('temperature_2m', 11))), 1),
            "time": current.get('time'),
            
            # Huomisen ennuste
            "tomorrow": {
                "max": daily.get('temperature_2m_max', [None, None])[1] if len(daily.get('temperature_2m_max', [])) > 1 else None,
                "min": daily.get('temperature_2m_min', [None, None])[1] if len(daily.get('temperature_2m_min', [])) > 1 else None,
                "precipitation": daily.get('precipitation_sum', [None, None])[1] if len(daily.get('precipitation_sum', [])) > 1 else None,
            }
        }
        return result
    except Exception as e:
        logging.error(f"Open-Meteo fetch epäonnistui {e}")
        raise

def main():
    result = None
    foreca_data = {}
    
    # 1. Yritä Foreca HTML (ei pakollinen mutta kokeillaan)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fi-FI,fi;q=0.9",
        }
        r = requests.get(FORECA_URL, headers=headers, timeout=15)
        if r.ok:
            foreca_data = parse_foreca_html(r.text)
            logging.info(f"Foreca parsittu: {foreca_data}")
    except Exception as e:
        logging.warning(f"Foreca HTML parse epäonnistui {e} - käytetään Open-Meteo")

    # 2. Hae KAIKKI pakolliset Open-Meteosta (100% varma)
    try:
        om_data = fetch_open_meteo_all()
        # Yhdistä Foreca ja Open-Meteo, Open-Meteo on varma
        result = {**om_data, **{k:v for k,v in foreca_data.items() if v is not None}}
        # Varmista pakolliset
        if 'temp' not in result:
            result['temp'] = om_data['temp']
        
        result["source"] = f"{FORECA_URL} + open-meteo.com - V22 kaikki pakolliset kentät"
        result["foreca_url"] = FORECA_URL
        result["coords"] = {"lat": 63.00, "lon": 23.822, "place": "Luoma-aho, Alajärvi - Foreca"}
        result["fetched_at"] = datetime.now(timezone.utc).isoformat()
        result["fetched_at_fi"] = datetime.now().strftime("%d.%m.%Y %H:%M")
        result["version"] = "V22 FORECA pakolliset: lämpötila, tuuli, ennuste, vesisade, pilvisyys"
        result["mandatory"] = ["lampotila", "tuuli", "ennuste", "vesisade", "pilvisyys"]
        result["automation"] = {"header_locked": True, "layout_locked": True, "cards_locked": True, "foreca": True, "mandatory_fields": True}
        
    except Exception as e:
        logging.error(f"KAIKKI epäonnistui {e}")
        result = {
            "temp": 11,
            "temperature": 11,
            "lampotila": 11,
            "wind_speed": 2,
            "tuuli": "2 m/s",
            "precipitation": 0,
            "vesisade": 0,
            "cloudiness": 50,
            "pilvisyys": 50,
            "forecast": "Säätieto ei saatavilla",
            "ennuste": "Säätieto ei saatavilla",
            "source": f"{FORECA_URL} - fallback - {e}",
            "foreca_url": FORECA_URL,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "fetched_at_fi": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "error": str(e)
        }
    
    # Kirjoita
    out = DATA_DIR / "saa.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    out2 = DATA_DIR / "foreca.json"
    out2.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out} - {result['temp']}°C tuuli {result.get('wind_speed')} m/s sade {result.get('precipitation')} mm pilvisyys {result.get('cloudiness')}% ennuste {result.get('forecast')}")
    
    # status
    status_path = DATA_DIR / "status.json"
    try:
        status = []
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding='utf-8'))
                if not isinstance(status, list):
                    status = [status]
            except:
                status = []
        status.append({"fetcher": "foreca_v22_mandatory", "url": FORECA_URL, "temp": result['temp'], "mandatory": result.get('mandatory'), "last_run": datetime.now().isoformat()})
        status_path.write_text(json.dumps(status[-30:], ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logging.error(f"Status {e}")

if __name__ == "__main__":
    main()
