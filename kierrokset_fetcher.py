#!/usr/bin/env python3
"""
kierrokset_fetcher.py - Automatisoi UDISC & METRIX KIERROKSET + PELIAIKA + ASKELMÄÄRÄ + KILOMETRIT
- Hakee Metrix 44010, 44763, 43119 automaattisesti
- Laskee yhteensä kierrokset, uniikit, peliaika, askeleet, kilometrit
- Kaikki 4 päivittyy samalla kun total kasvaa
"""
import json
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

METRIX_URLS = [
    "https://discgolfmetrix.com/course/44010",
    "https://discgolfmetrix.com/course/44763",
    "https://discgolfmetrix.com/course/43119"
]

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "fi-FI"}

def fetch_metrix(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        players=set()
        count=0
        for tr in soup.find_all('tr'):
            tds=tr.find_all('td')
            if len(tds)>=2:
                name=tds[1].get_text(strip=True)
                if name and len(name)>2 and not name.lower().startswith('par') and not name.replace(' ','').isdigit():
                    players.add(name)
                    count+=1
        return {"results":count,"players":players,"unique":len(players)}
    except Exception as e:
        print(f"Failed {url}: {e}")
        return {"results":0,"players":set(),"unique":0}

def main():
    print("=== KAIKKI AUTO - Kierrokset + Peliaika + Askeleet + Kilometrit ===")
    all_players=set()
    total_metrix=0
    for url in METRIX_URLS:
        d=fetch_metrix(url)
        total_metrix+=d["results"]
        all_players.update(d["players"])
        print(f"{url}: {d['results']} tulosta, {d['unique']} uniikkia")

    # Base arvot live sivulta
    BASE_UDISC_ROUNDS=702
    BASE_UDISC_HOURS=603
    BASE_UDISC_STEPS=1275690
    BASE_TOTAL=1130
    BASE_UNIQUE=100
    BASE_METRIX=58

    # UDisc arvio - jos Metrix kasvanut, kasvata totalia
    metrix_growth=max(0,total_metrix-BASE_METRIX)
    total_rounds=BASE_TOTAL+metrix_growth
    total_udisc=BASE_UDISC_ROUNDS+metrix_growth  # oletetaan UDisc kasvaa samalla
    unique_players=BASE_UNIQUE+len(all_players)-25

    total_rounds=max(total_rounds,BASE_TOTAL)
    unique_players=max(unique_players,BASE_UNIQUE)

    # KAIKKI 3 LASKENTA SAMALLA
    peliaika_hours=BASE_UDISC_HOURS + total_udisc*1.25
    peliaika_total=round(total_rounds*1.25)  # yksinkertainen total*1.25

    askeleet_total=BASE_UDISC_STEPS + total_udisc*2600
    kilometrit_total=total_rounds*2

    result={
        "total_rounds":total_rounds,
        "total_rounds_metrix":total_metrix,
        "total_rounds_udisc":total_udisc,
        "unique_players":unique_players,
        "unique_players_metrix":len(all_players),
        "unique_players_udisc_estimate":unique_players-len(all_players),
        "peliaika":{
            "total_hours":peliaika_total,
            "base_hours":BASE_UDISC_HOURS,
            "per_round":1.25,
            "detail":f"UDisc {BASE_UDISC_HOURS}h + {total_udisc}×1.25h",
            "display":f"{peliaika_total}h"
        },
        "askeleet":{
            "total_steps":askeleet_total,
            "base_steps":BASE_UDISC_STEPS,
            "per_round":2600,
            "detail":f"UDisc {BASE_UDISC_STEPS:,} + {total_udisc}×2600".replace(","," "),
            "display":f"{askeleet_total:,}".replace(","," ")
        },
        "kilometrit":{
            "total_km":kilometrit_total,
            "per_round":2,
            "detail":f"{total_rounds}×2km - radan kiertomatka",
            "display":f"{kilometrit_total} km"
        },
        "calculation":f"{total_metrix} Metrix auto + {total_udisc} UDisc arvio = {total_rounds} yhteensä | Peliaika {peliaika_total}h | Askeleet {askeleet_total} | Km {kilometrit_total}",
        "fetched_at":datetime.now().isoformat(),
        "source":"Kaikki AUTO - kierrokset + peliaika + askeleet + kilometrit päivittyy samalla",
        "automation":"Metrix TÄYSIN AUTO, UDisc OSITTAIN, kaikki 3 lasketaan samalla"
    }

    out=DATA_DIR/"kierrokset.json"
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"\nWrote {out}")
    print(f"Kierrokset: {total_rounds} (Metrix {total_metrix} + UDisc {total_udisc})")
    print(f"Peliaika: {result['peliaika']['display']} - {result['peliaika']['detail']}")
    print(f"Askeleet: {result['askeleet']['display']} - {result['askeleet']['detail']}")
    print(f"Kilometrit: {result['kilometrit']['display']} - {result['kilometrit']['detail']}")

    # Tilastot kaikki
    (DATA_DIR/"tilastot_kaikki.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")

if __name__=="__main__":
    main()
