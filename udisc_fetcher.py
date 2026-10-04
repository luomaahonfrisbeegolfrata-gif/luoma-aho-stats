#!/usr/bin/env python3
"""
udisc_fetcher.py - Hakee Top 10 UDISC - V8 MANUAALINEN 10 NIMELLÄ SÄILYTYS
https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835
Automaattinen dynaaminen haku - SÄILYTTÄÄ MANUAALISEN 10 NIMEN PÄIVITYKSEN
"""
import json
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

URL = "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/leaderboard?layoutId=143835&dateRange=all&limit=100"
COURSE_URL = "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/leaderboard?layoutId=143835&dateRange=all&limit=100"
LAYOUT_URL = "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835"

def fetch_udisc_top10():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8"
    }
    top_results = []
    
    # TARKISTA ONKO MANUAALINEN 10 NIMEN PÄIVITYS - SÄILYTÄ SE
    try:
        existing_path = DATA_DIR / "udisc.json"
        if existing_path.exists():
            existing = json.loads(existing_path.read_text(encoding='utf-8'))
            if existing.get('manual_update') and len(existing.get('top10', [])) >= 10:
                print(f"Säilytetään manuaalinen 10 nimen päivitys - {existing.get('manual_update_fi')} - EI ylikirjoiteta 4 nimellä")
                # Päivitä vain timestamp, älä ylikirjoita nimiä
                existing['fetched_at'] = datetime.now().isoformat()
                existing['fetched_at_fi'] = datetime.now().strftime("%d.%m.%Y %H:%M")
                existing['source'] = "MANUAALINEN 10 NIMELLÄ SÄILYTETTY - auto fetcher ei ylikirjoittanut - V8"
                return existing
    except Exception as e:
        print(f"Manual check failed: {e} - jatketaan fetch")
    
    # HAE OIKEA UDISC LEADERBOARD - layoutId 143835 = 12 väylää Par 41
    try:
        print(f"Fetching UDisc leaderboard {COURSE_URL}")
        r = requests.get(COURSE_URL, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        import re
        pattern = r'@(\w+)[^0-9]*?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^0-9]*?(\d{4})[^\d]*(\d{1,2})\b'
        matches = re.findall(pattern, text)
        print(f"Found {len(matches)} potential entries in leaderboard text")
        if matches:
            for i, (user, year, score) in enumerate(matches[:10]):
                score_int = int(score)
                if 25 <= score_int <= 60:
                    top_results.append({
                        "rank": i+1,
                        "name": f"@{user}",
                        "total": score_int,
                        "plus_minus": f"{score_int-41:+d}" if score_int != 41 else "0",
                        "date": year,
                        "source": "udisc.com leaderboard - REAL"
                    })
        print(f"UDisc leaderboard parsed: {len(top_results)} entries from real data")
    except Exception as e:
        print(f"UDisc fetch failed: {e}")
    
    # Jos ei saatu tarpeeksi oikeaa dataa, käytä MANUAALISTA 10 NIMEÄ - EI 4 nimeä
    if len(top_results) < 10:
        print("Using MANUAALINEN 10 NIMEÄ fallback - käyttäjän päivittämä - V8 - EI 4 nimeä")
        top_results = [
            {"rank": 1, "name": "@kantanen8", "total": 35, "plus_minus": "-6", "date": "Jul 4, 2026", "source": "udisc.com - MANUAALINEN 10"},
            {"rank": 2, "name": "@valkoparta", "total": 36, "plus_minus": "-5", "date": "Jul 6, 2026", "source": "MANUAALINEN"},
            {"rank": 3, "name": "@mattiasss", "total": 36, "plus_minus": "-5", "date": "Aug 19, 2026", "source": "MANUAALINEN"},
            {"rank": 4, "name": "@dashyy", "total": 38, "plus_minus": "-3", "date": "Sep 13, 2025", "source": "MANUAALINEN"},
            {"rank": 5, "name": "Toni Luoma-aho", "total": 39, "plus_minus": "-2", "date": "10/5/25", "source": "MANUAALINEN 10"},
            {"rank": 6, "name": "Benjamin Turja", "total": 40, "plus_minus": "-1", "date": "10/5/25", "source": "MANUAALINEN"},
            {"rank": 7, "name": "Julius Luoma-aho", "total": 41, "plus_minus": "0", "date": "10/5/25", "source": "MANUAALINEN"},
            {"rank": 8, "name": "Eino Vistiaho", "total": 42, "plus_minus": "+1", "date": "10/5/25", "source": "MANUAALINEN"},
            {"rank": 9, "name": "Jari Vistiaho", "total": 43, "plus_minus": "+2", "date": "10/5/25", "source": "MANUAALINEN"},
            {"rank": 10, "name": "Aapo Penttilä", "total": 44, "plus_minus": "+3", "date": "10/5/25", "source": "MANUAALINEN"},
        ]
    
    result = {
        "version": "V8 - MANUAALINEN 10 NIMELLÄ - SÄILYTETTY",
        "course": "UDISC - Luoma-aho",
        "url": URL,
        "course_url": COURSE_URL,
        "layout_url": LAYOUT_URL,
        "layout_id": "143835",
        "holes": 12,
        "par": 41,
        "top10": top_results[:10],
        "fetched_at": datetime.now().isoformat(),
        "fetched_at_fi": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "source": "MANUAALINEN 10 NIMELLÄ - käyttäjän päivitys säilytetty - V8",
        "note": "10 nimeä - 4 UDisc @ + 6 Metrix - manuaalisesti päivitetty - V8",
        "manual_update": False,  # auto fetcher generoi, mutta säilyttää manuaalisen jos olemassa
        "real_stats": {
            "pelattujen_kierrosten_maara": 435,
            "virkistystunnit": 613,
            "ainutlaatuiset_pelaajat": 67,
            "otettujen_askelten_maara": 1296732,
            "tilasto_paivitetty": "4.10.2026 manuaalinen 10",
            "layout_id": "143835"
        }
    }
    return result

def main():
    data = fetch_udisc_top10()
    # Jos data on manuaalinen ja säilytetty, älä ylikirjoita jos se on manuaalinen
    if data.get('manual_update') and 'MANUAALINEN' in data.get('source',''):
        print(f"Säilytetään manuaalinen 10 - {data.get('manual_update_fi')}")
        out = DATA_DIR / "udisc.json"
        # Päivitä vain timestamp jos manuaalinen
        if out.exists():
            existing = json.loads(out.read_text(encoding='utf-8'))
            if existing.get('manual_update'):
                print("Manuaalinen 10 säilytetty - ei ylikirjoiteta")
                return
    
    out = DATA_DIR / "udisc.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out} - {len(data['top10'])} entries - V8 MANUAALINEN 10")
    
    out2 = DATA_DIR / "udisc_top10.json"
    out2.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out2}")

if __name__ == "__main__":
    main()
