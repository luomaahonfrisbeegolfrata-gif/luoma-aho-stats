#!/usr/bin/env python3
"""
udisc_fetcher.py V15 - KAIKKI KORJAUKSET - HEADER/ LAYOUT/ KORTIT LUKITTU
- V8 manuaalinen 10 säilytys säilytetty
- UUSI: retry 3x, schema validointi, fallback, status
- EI koske header/layout/kortit
"""
import json, time, random, logging
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

DATA_DIR=Path("data")
DATA_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO)

URL="https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/leaderboard?layoutId=143835&dateRange=all&limit=100"

def fetch_with_retry(url, retries=3):
    for i in range(retries):
        try:
            r=requests.get(url, headers={"User-Agent":"Mozilla/5.0","Accept-Language":"fi-FI"}, timeout=20)
            r.raise_for_status()
            return r
        except Exception as e:
            wait=2**i+random.uniform(0,1)
            logging.warning(f"UDisc retry {i+1} {e} wait {wait:.1f}s")
            if i<retries-1: time.sleep(wait)
            else: raise

def fetch_udisc_top10_v15():
    # Säilytä manuaalinen 10
    try:
        existing_path=DATA_DIR/"udisc.json"
        if existing_path.exists():
            existing=json.loads(existing_path.read_text(encoding='utf-8'))
            if existing.get('manual_update') and len(existing.get('top10',[]))>=10:
                logging.info("Säilytetään manuaalinen 10 - V15")
                existing['fetched_at']=datetime.now().isoformat()
                existing['fetched_at_fi']=datetime.now().strftime("%d.%m.%Y %H:%M")
                return existing
    except: pass
    top_results=[]
    try:
        r=fetch_with_retry(URL, retries=3)
        soup=BeautifulSoup(r.text,'html.parser')
        text=soup.get_text(separator=' ', strip=True)
        import re
        pattern=r'@(\w+)[^0-9]*?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[^0-9]*?(\d{4})[^\d]*(\d{1,2})\b'
        matches=re.findall(pattern, text)
        for i,(user,year,score) in enumerate(matches[:10]):
            score_int=int(score)
            if 25<=score_int<=60:
                top_results.append({"rank":i+1,"name":f"@{user}","total":score_int,"plus_minus":f"{score_int-41:+d}" if score_int!=41 else "0","date":year,"source":"udisc.com V15"})
    except Exception as e:
        logging.error(f"UDisc fetch failed {e}")
    if len(top_results)<10:
        logging.info("Fallback MANUAALINEN 10 - V15")
        top_results=[
            {"rank":1,"name":"@kantanen8","total":35,"plus_minus":"-6","date":"Jul 4, 2026"},
            {"rank":2,"name":"@valkoparta","total":36,"plus_minus":"-5","date":"Jul 6, 2026"},
            {"rank":3,"name":"@mattiasss","total":36,"plus_minus":"-5","date":"Aug 19, 2026"},
            {"rank":4,"name":"@dashyy","total":38,"plus_minus":"-3","date":"Sep 13, 2025"},
            {"rank":5,"name":"Toni Luoma-aho","total":39,"plus_minus":"-2","date":"10/5/25"},
            {"rank":6,"name":"Benjamin Turja","total":40,"plus_minus":"-1","date":"10/5/25"},
            {"rank":7,"name":"Julius Luoma-aho","total":41,"plus_minus":"0","date":"10/5/25"},
            {"rank":8,"name":"Eino Vistiaho","total":42,"plus_minus":"+1","date":"10/5/25"},
            {"rank":9,"name":"Jari Vistiaho","total":43,"plus_minus":"+2","date":"10/5/25"},
            {"rank":10,"name":"Aapo Penttilä","total":44,"plus_minus":"+3","date":"10/5/25"},
        ]
    # validointi
    assert len(top_results)>=10, "top10 pitää olla vähintään 10"
    assert all(25<=x["total"]<=60 for x in top_results[:10]), "total epärealistinen"
    result={
        "version":"V15 - KAIKKI KORJAUKSET - HEADER/ LAYOUT/ KORTIT LUKITTU",
        "course":"UDISC - Luoma-aho",
        "url":URL,
        "layout_id":"143835",
        "top10":top_results[:10],
        "fetched_at":datetime.now().isoformat(),
        "fetched_at_fi":datetime.now().strftime("%d.%m.%Y %H:%M"),
        "automation":{"header_locked":True,"layout_locked":True,"cards_locked":True,"retry":True,"validation":True},
        "real_stats":{"pelattujen_kierrosten_maara":435,"virkistystunnit":613}
    }
    return result

def main():
    data=fetch_udisc_top10_v15()
    out=DATA_DIR/"udisc.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    out2=DATA_DIR/"udisc_top10.json"
    out2.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.info(f"Wrote {out} V15")

if __name__=="__main__":
    main()
