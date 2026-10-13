"""
udisc_fetcher.py - V5.1 FIXED - Ei enää vaihtele joka päivityksessä
- Syy vaihteluun: vanha fallback ylikirjoitti käsin korjatun Top10:n joka kerta kun live-haku feilasi (UDiscilla ei public APIa)
- Fix: 
  1. Lukittu oikea Top10 (12.10.2026 kuvasta päivitetty) fallbackiksi
  2. Jos live-haku feilaa, säilytä olemassa oleva tiedosto eikä ylikirjoita
  3. Säilytä total_rounds=444, unique_players=69 jne. älä ylikirjoita len(top10)=10
"""

import json
import pathlib
import re
from datetime import datetime, timezone

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None

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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8",
}

UDISC_SLUGS = [
    "luoma-ahon-frisbeegolfrata-4z8T",
    "luoma-ahon-frisbeegolfrata",
]

# LUKITTU OIKEA TOP10 - päivitetty 12.10.2026 kuvasta (toinen kuvasi)
# Tämä ei enää vaihtele
FALLBACK_TOP = [
    {
        "rank": 1,
        "name": "@kantanen8",
        "total": 35,
        "plus_minus": "-6",
        "plus": "-6",
        "date": "4.7.2026"
    },
    {
        "rank": 2,
        "name": "@valkoparta",
        "total": 36,
        "plus_minus": "-5",
        "plus": "-5",
        "date": "6.7.2026"
    },
    {
        "rank": 2,
        "name": "@mattiasss",
        "total": 36,
        "plus_minus": "-5",
        "plus": "-5",
        "date": "19.8.2026"
    },
    {
        "rank": 4,
        "name": "@dashyy",
        "total": 38,
        "plus_minus": "-3",
        "plus": "-3",
        "date": "13.9.2025"
    },
    {
        "rank": 4,
        "name": "@itkonenjere",
        "total": 38,
        "plus_minus": "-3",
        "plus": "-3",
        "date": "29.4.2026"
    },
    {
        "rank": 6,
        "name": "@peetu7",
        "total": 39,
        "plus_minus": "-2",
        "plus": "-2",
        "date": "24.7.2026"
    },
    {
        "rank": 6,
        "name": "@kimmoke",
        "total": 39,
        "plus_minus": "-2",
        "plus": "-2",
        "date": "11.10.2026"
    },
    {
        "rank": 8,
        "name": "@taspak",
        "total": 42,
        "plus_minus": "+1",
        "plus": "+1",
        "date": "16.7.2026"
    },
    {
        "rank": 9,
        "name": "@adusti",
        "total": 43,
        "plus_minus": "+2",
        "plus": "+2",
        "date": "20.7.2026"
    },
    {
        "rank": 10,
        "name": "@tommivluoma",
        "total": 47,
        "plus_minus": "+6",
        "plus": "+6",
        "date": "8.8.2026"
    }
]

def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def parse_udisc_leaderboard(html):
    soup = BeautifulSoup(html, "lxml")
    results = []
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue
        txt = table.get_text(" ", strip=True).lower()
        if "player" not in txt and "@" not in txt and "total" not in txt:
            continue
        for tr in rows[1:]:
            tds = tr.find_all(["td","th"])
            if len(tds) < 2:
                continue
            cells = [c.get_text(strip=True) for c in tds]
            name = None
            total = None
            plus = None
            for c in cells:
                if c.startswith("@"):
                    name = c
                elif re.match(r"^-?\d+$", c) and len(c) <= 3:
                    try:
                        v = int(c)
                        if 20 <= v <= 100:
                            total = v
                    except:
                        pass
                elif re.match(r"^[+-]\d+|E$", c):
                    plus = c
            if name and total:
                if not plus:
                    diff = total - 41
                    plus = "E" if diff==0 else (f"+{diff}" if diff>0 else f"{diff}")
                results.append({"name": name, "total": total, "plus_minus": plus})
        if results:
            break
    if not results:
        for script in soup.find_all("script"):
            txt = script.string or ""
            matches = re.findall(r'"username"\s*:\s*"([^"]+)"[^}]*"score"\s*:\s*(\d+)', txt)
            for username, score in matches:
                name = f"@{username}" if not username.startswith("@") else username
                total = int(score)
                diff = total - 41
                plus = "E" if diff==0 else (f"+{diff}" if diff>0 else f"{diff}")
                results.append({"name": name, "total": total, "plus_minus": plus})
            if results:
                break
    best = {}
    for r in results:
        n = r["name"]
        if n not in best or r["total"] < best[n]["total"]:
            best[n] = r
    sorted_best = sorted(best.values(), key=lambda x: x["total"])
    top10 = []
    for i, r in enumerate(sorted_best[:10], 1):
        top10.append({"rank": i, "name": r["name"], "total": r["total"], "plus_minus": r["plus_minus"], "plus": r["plus_minus"]})
    return top10, results

def try_fetch_udisc():
    if requests is None:
        return None, None
    for slug in UDISC_SLUGS:
        urls = [
            f"https://udisc.com/courses/{slug}",
            f"https://udisc.com/courses/{slug}/leaderboard",
        ]
        for url in urls:
            try:
                print(f"  Kokeillaan UDisc {url}")
                html = fetch_html(url)
                top10, all_res = parse_udisc_leaderboard(html)
                if top10:
                    print(f"    -> löytyi {len(top10)} tulosta")
                    return top10, url
            except Exception as e:
                print(f"    fail {url}: {e}")
                continue
    return None, None

def main():
    print("=== udisc_fetcher.py V5.1 FIXED - ei enää vaihtele ===")
    print(f"DATA_DIR={DATA_DIR}")
    
    existing_path = DATA_DIR / "udisc.json"
    existing_data = None
    if existing_path.exists():
        try:
            existing_data = json.loads(existing_path.read_text(encoding="utf-8"))
            print(f"Olemassa oleva: {len(existing_data.get('top10',[]))} top, total_rounds={existing_data.get('total_rounds')}")
        except:
            existing_data = None

    top10_live = None
    source_url = None

    if requests:
        top10_live, source_url = try_fetch_udisc()
    else:
        print("requests puuttuu")

    if top10_live:
        print(f"✅ Live haku onnistui: {len(top10_live)} tulosta")
        # Päivitä vain top10, säilytä total_rounds jne. olemassa olevasta
        if existing_data:
            existing_data["top10"] = top10_live
            existing_data["fetched_at"] = datetime.now(timezone.utc).isoformat()
            existing_data["fetched_at_fi"] = datetime.now().strftime("%d.%m.%Y %H:%M")
            existing_data["source_url"] = source_url
            existing_data["version"] = "V5.1 FIXED - live top10 päivitetty, stats säilytetty"
            data = existing_data
        else:
            data = {
                "course_id": "luoma-ahon-frisbeegolfrata-YNEx",
                "total_rounds": 444,
                "total": 444,
                "unique_players": 69,
                "virkistystunnit": 618,
                "peliaika": {"display": "618h", "hours": 618},
                "askeleet": {"display": "1 318 270", "count": 1318270},
                "top10": top10_live,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source_url": source_url,
                "version": "V5.1 FIXED"
            }
    else:
        print("⚠️ Live haku feilasi (UDisc ei public API) - käytetään lukittua oikeaa listaa")
        if existing_data and existing_data.get("top10") and len(existing_data.get("top10")) == 10:
            # Säilytä olemassa oleva, älä ylikirjoita fallbackilla -> estää vaihtelun
            print(f"   Säilytetään olemassa oleva Top10: {[x['name'] for x in existing_data['top10']]}")
            existing_data["fetched_at"] = datetime.now(timezone.utc).isoformat()
            existing_data["version"] = "V5.1 FIXED - säilytetty olemassa oleva (ei ylikirjoitettu fallbackilla)"
            data = existing_data
        else:
            print(f"   Ei olemassa olevaa -> käytetään lukittua FALLBACK_TOP: {[x['name'] for x in FALLBACK_TOP]}")
            data = {
                "course_id": "luoma-ahon-frisbeegolfrata-YNEx",
                "total_rounds": 444,
                "total": 444,
                "unique_players": 69,
                "virkistystunnit": 618,
                "peliaika": {"display": "618h", "hours": 618},
                "askeleet": {"display": "1 318 270", "count": 1318270},
                "askelten_maara": 1318270,
                "updated": "12.10.2026 - Top10 lukittu, ei vaihtele",
                "source": "UDisc Elinikäiset tilastot - lukittu V5.1",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "top10": FALLBACK_TOP
            }

    (DATA_DIR / "udisc.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ UDisc V5.1 FIXED tallennettu - {len(data['top10'])} pelaajaa, total_rounds={data.get('total_rounds')} (ei 10)")
    for r in data["top10"]:
        print(f"  {r['rank']}. {r['name']} {r['total']} {r.get('plus_minus','')}")

if __name__ == "__main__":
    main()
