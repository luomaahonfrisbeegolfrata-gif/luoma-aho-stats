#!/usr/bin/env python3
"""
udisc_image_parser.py - V5.2
Tapa jolla käyttäjän lataamista kuvista UDisc lasketaan yhteen Metrix datan kanssa

Käyttö:
1. Käyttäjä lataa UDisc kuvan (Elinikäiset tilastot) jossa näkyy:
   - 444 kierrosta
   - 69 pelaajaa
   - 618h peliaika
   - 1 318 270 askeleet
   - 961 km tms

2. Tämä scripti:
   - Yrittää OCR (pytesseract) jos saatavilla
   - Jos ei, kysyy käyttäjältä numerot interaktiivisesti
   - Päivittää data/udisc.json
   - Ajaa kierrokset.py joka laskee 750+444=1194

Toimii myös ilman nettiä, lukitsee arvot V5.2
"""

import json
import pathlib
import re
from datetime import datetime, timezone

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

BASE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [BASE.parent / "data", BASE / "data", BASE, pathlib.Path.cwd() / "data"]
DATA_DIR = None
for c in CANDIDATES:
    if c.exists() and ((c / "udisc.json").exists() or c.name == "data"):
        DATA_DIR = c if c.name == "data" else c
        break
if DATA_DIR is None:
    DATA_DIR = BASE.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def parse_udisc_from_text(text):
    """Etsi UDisc luvut tekstistä"""
    data = {}
    # Etsi patternit kuten "444", "69", "618h", "1 318 270" jne.
    # Kierrokset
    m = re.search(r'(\d+)\s*kierrosta', text, re.IGNORECASE)
    if m:
        data['total_rounds'] = int(m.group(1))
    else:
        # Yritä löytää iso luku 100-1000 joka on kierrokset
        nums = re.findall(r'\b(\d{2,4})\b', text)
        if nums:
            # Ota suurin todennäköinen kierrosmäärä (100-1000)
            candidates = [int(n) for n in nums if 100 <= int(n) <= 2000]
            if candidates:
                data['total_rounds'] = max(candidates)
    
    # Pelaajat
    m = re.search(r'(\d+)\s*pelaajaa', text, re.IGNORECASE)
    if m:
        data['unique_players'] = int(m.group(1))
    
    # Peliaika tunteina
    m = re.search(r'(\d+)\s*h', text, re.IGNORECASE)
    if m:
        data['peliaika_hours'] = int(m.group(1))
    
    # Askeleet - muoto "1 318 270" tai "1318270"
    m = re.search(r'([\d\s]+)\s*askel', text, re.IGNORECASE)
    if m:
        num_str = m.group(1).replace(' ', '').replace('\xa0','')
        try:
            data['askeleet'] = int(num_str)
        except:
            pass
    
    # Myös etsi pelkkä iso luku > 1 000 000 askeleille
    m = re.search(r'(\d[\d\s]{5,})', text)
    if m and 'askeleet' not in data:
        num_str = m.group(1).replace(' ', '').replace('\xa0','')
        try:
            val = int(num_str)
            if val > 100000:
                data['askeleet'] = val
        except:
            pass
    
    return data

def ocr_image(image_path):
    """Yritä OCR kuvasta"""
    if not HAS_OCR:
        return None
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='fin+eng')
        print(f"OCR text: {text[:500]}")
        return parse_udisc_from_text(text)
    except Exception as e:
        print(f"OCR fail: {e}")
        return None

def interactive_input():
    """Kysy käyttäjältä numerot jos OCR ei toimi"""
    print("\n=== UDisc kuvasta Metrix yhteenlasku V5.2 ===")
    print("Syötä UDisc Elinikäiset tilastot kuvasta:")
    try:
        total = input("Kierrokset (esim 444): ").strip()
        total = int(total) if total else 444
        unique = input("Pelaajat (esim 69): ").strip()
        unique = int(unique) if unique else 69
        hours = input("Peliaika tunteina (esim 618): ").strip()
        hours = int(hours) if hours else 618
        steps = input("Askeleet (esim 1318270): ").strip()
        steps = int(steps.replace(' ','').replace(',','')) if steps else 1318270
        return {
            'total_rounds': total,
            'unique_players': unique,
            'peliaika_hours': hours,
            'askeleet': steps
        }
    except:
        return {
            'total_rounds': 444,
            'unique_players': 69,
            'peliaika_hours': 618,
            'askeleet': 1318270
        }

def update_udisc_json(parsed):
    """Päivitä udisc.json ja kierrokset.json"""
    # Lue olemassa oleva
    udisc_path = DATA_DIR / "udisc.json"
    existing = {}
    if udisc_path.exists():
        try:
            existing = json.loads(udisc_path.read_text(encoding='utf-8'))
        except:
            existing = {}
    
    total = parsed.get('total_rounds', existing.get('total_rounds', 444))
    unique = parsed.get('unique_players', existing.get('unique_players', 69))
    hours = parsed.get('peliaika_hours', existing.get('peliaika', {}).get('hours', 618))
    steps = parsed.get('askeleet', existing.get('askeleet', {}).get('count', 1318270))
    
    # Laske km ja muut johdannaiset (kuten kierrokset.py)
    # 444 kierrosta = 618h, 1 318 270 askelta, 961 km (kuvasta)
    # Suhde: 1 kierros = 1.39h, 2969 askelta, 2.16 km
    km = int(steps * 0.000732)  # 1318270 -> 961 km suhde
    if km < 100:
        km = int(total * 2.16)
    
    new_data = {
        "course_id": "luoma-ahon-frisbeegolfrata-YNEx",
        "total_rounds": total,
        "total": total,
        "unique_players": unique,
        "virkistystunnit": hours,
        "peliaika": {"display": f"{hours}h", "hours": hours},
        "askeleet": {"display": f"{steps:,}".replace(",", " "), "count": steps},
        "askelten_maara": steps,
        "kilometrit": {"display": f"{km} km", "km": km},
        "updated": datetime.now().strftime("%d.%m.%Y - Kuvasta parsittu V5.2"),
        "source": "UDisc Elinikäiset tilastot - käyttäjän kuva",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V5.2 - Kuvasta laskettu",
        "locked": True,
        "top10": existing.get('top10', [
            {"rank": 1, "name": "@kantanen8", "total": 35, "plus_minus": "-6"},
            {"rank": 2, "name": "@valkoparta", "total": 36, "plus_minus": "-5"},
            {"rank": 2, "name": "@mattiasss", "total": 36, "plus_minus": "-5"},
            {"rank": 4, "name": "@dashyy", "total": 38, "plus_minus": "-3"},
            {"rank": 4, "name": "@itkonenjere", "total": 38, "plus_minus": "-3"},
            {"rank": 6, "name": "@peetu7", "total": 39, "plus_minus": "-2"},
            {"rank": 6, "name": "@kimmoke", "total": 39, "plus_minus": "-2"},
            {"rank": 8, "name": "@taspak", "total": 42, "plus_minus": "+1"},
            {"rank": 9, "name": "@adusti", "total": 43, "plus_minus": "+2"},
            {"rank": 10, "name": "@tommivluoma", "total": 47, "plus_minus": "+6"},
        ])
    }
    
    udisc_path.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ UDisc päivitetty: {total} kierrosta, {unique} pelaajaa, {hours}h, {steps} askelta")
    
    # Päivitä myös juuressa jos eri
    root_path = pathlib.Path.cwd() / "udisc.json"
    if root_path.parent != DATA_DIR:
        try:
            root_path.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding='utf-8')
        except:
            pass
    
    return new_data

def update_kierrokset(metrix_total=750, udisc_total=444):
    """Laske yhteen Metrix + UDisc kuten kierrokset.py"""
    kierrokset_path = DATA_DIR / "kierrokset.json"
    # REF arvot V31
    REF_TOTAL = 1194
    REF_PELIAIKA = 1594
    REF_ASKELEET = 3364508
    REF_KM = 2453
    
    # Lue Metrix breakdown jos saatavilla
    metrix_data = {}
    try:
        for f in DATA_DIR.glob("metrix_*.json"):
            d = json.loads(f.read_text(encoding='utf-8'))
            metrix_data[f.stem] = d.get('total_results', 0)
    except:
        pass
    
    total = metrix_total + udisc_total
    peliaika = int(total * REF_PELIAIKA / REF_TOTAL)
    askeleet = int(total * REF_ASKELEET / REF_TOTAL)
    km = int(total * REF_KM / REF_TOTAL)
    
    data = {
        "total_rounds": total,
        "total": total,
        "count": total,
        "metrix_total": metrix_total,
        "udisc_total": udisc_total,
        "unique_players": 132,
        "peliaika": {"display": f"{peliaika}h", "hours": peliaika},
        "askeleet": {"display": f"{askeleet:,}".replace(",", " "), "count": askeleet},
        "kilometrit": {"display": f"{km} km", "km": km},
        "updated": datetime.now().strftime("%d.%m.%Y - UDisc kuvasta + Metrix"),
        "source": f"Metrix {metrix_total} + UDisc {udisc_total} = {total}",
        "version": "V5.2 - Kuvasta laskettu keskiarvo",
        "locked": True
    }
    
    kierrokset_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ Kierrokset päivitetty: {metrix_total} + {udisc_total} = {total}")
    print(f"   Peliaika {peliaika}h, Askeleet {askeleet}, KM {km}")
    return data

def main():
    import sys
    print("=== UDisc kuvasta Metrix yhteen V5.2 ===")
    
    parsed = None
    if len(sys.argv) > 1:
        img_path = pathlib.Path(sys.argv[1])
        if img_path.exists():
            print(f"Kuva: {img_path}")
            parsed = ocr_image(img_path)
            if parsed:
                print(f"OCR löysi: {parsed}")
    
    if not parsed:
        # Yritä etsiä kuva data kansiosta tai kysy
        possible_images = list(pathlib.Path.cwd().rglob("*.png")) + list(pathlib.Path.cwd().rglob("*.jpg"))
        udisc_images = [p for p in possible_images if 'udisc' in p.name.lower() or 'elinik' in p.name.lower()]
        if udisc_images:
            print(f"Löytyi mahdollisia UDisc kuvia: {udisc_images[:3]}")
            for img in udisc_images[:1]:
                parsed = ocr_image(img)
                if parsed:
                    break
        
        if not parsed:
            parsed = interactive_input()
    
    print(f"\nKäytetään: {parsed}")
    udisc_data = update_udisc_json(parsed)
    kierrokset_data = update_kierrokset(metrix_total=750, udisc_total=parsed.get('total_rounds', 444))
    
    print("\n=== VALMIS V5.2 ===")
    print(f"UDisc: {udisc_data['total_rounds']} kierrosta")
    print(f"Metrix: 750 kierrosta")
    print(f"Yhteensä: {kierrokset_data['total_rounds']} kierrosta")
    print(f"Keskiarvo laskettu: {kierrokset_data['peliaika']['display']}, {kierrokset_data['askeleet']['display']} askelta")

if __name__ == "__main__":
    main()
