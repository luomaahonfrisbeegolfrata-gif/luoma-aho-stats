"""
udisc_fetcher.py - V30 LIVE
- Yrittää hakea UDisc leaderboardin Luoma-aho radalle
- UDiscilla ei ole virallista public APIa ilman authia, joten kokeillaan:
  1. https://udisc.com/courses/luoma-ahon-frisbeegolfrata-4z8T (html parse)
  2. https://udisc.com/api/courses/... (jos toimii)
  3. Fallback: lukittu V29 data (sääntö 5)
- Parent 43119 huomioitu: UDiscilla on vain yksi layout (12 väylää Par 41), joten parent ei vaikuta UDisciin

GitHub Actions: pip install requests beautifulsoup4 lxml
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

# UDisc course slug - löydetty haulla: luoma-ahon-frisbeegolfrata-4z8T
UDISC_SLUGS = [
    "luoma-ahon-frisbeegolfrata-4z8T",
    "luoma-ahon-frisbeegolfrata",
]

# lukittu fallback V29 - korjattu nimet
FALLBACK_TOP = [
    {"rank": 1, "name": "@kantanen8", "total": 35, "plus_minus": "-6"},
    {"rank": 2, "name": "@valkoparta", "total": 36, "plus_minus": "-5"},
    {"rank": 3, "name": "@mattiass", "total": 36, "plus_minus": "-5"},
    {"rank": 4, "name": "@dashyy", "total": 38, "plus_minus": "-3"},
    {"rank": 5, "name": "@tikonenjere", "total": 38, "plus_minus": "-3"},
    {"rank": 6, "name": "@neetu7", "total": 39, "plus_minus": "-2"},
    {"rank": 7, "name": "@taspak", "total": 42, "plus_minus": "+1"},
    {"rank": 8, "name": "@adusti", "total": 43, "plus_minus": "+2"},
    {"rank": 9, "name": "@tommivuoma", "total": 47, "plus_minus": "+6"},
    {"rank": 10, "name": "@attekolis", "total": 48, "plus_minus": "+7"},
]

def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def parse_udisc_leaderboard(html):
    """Yrittää parsia UDisc leaderboardin html:stä"""
    soup = BeautifulSoup(html, "lxml")
    results = []

    # etsi taulukko jossa on pelaajia ja tuloksia
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue
        # tarkista onko leaderboard
        txt = table.get_text(" ", strip=True).lower()
        if "player" not in txt and "@" not in txt and "total" not in txt:
            continue
        for tr in rows[1:]:
            tds = tr.find_all(["td","th"])
            if len(tds) < 2:
                continue
            cells = [c.get_text(strip=True) for c in tds]
            # yritä löytää nimi ja total
            # UDisc rakenne vaihtelee, etsitään @-alkuinen nimi
            name = None
            total = None
            plus = None
            for c in cells:
                if c.startswith("@"):
                    name = c
                elif re.match(r"^-?\d+$", c) and len(c) <= 3:
                    # voi olla total
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
                    # laske par 41: plus = total-41
                    diff = total - 41
                    if diff == 0:
                        plus = "E"
                    elif diff > 0:
                        plus = f"+{diff}"
                    else:
                        plus = f"{diff}"
                results.append({"name": name, "total": total, "plus_minus": plus})
        if results:
            break

    # myös etsi json-ld tai script tag jossa leaderboard data
    if not results:
        # etsi <script> jossa @kantanen8 tyyppisiä
        for script in soup.find_all("script"):
            txt = script.string or ""
            # etsi pattern @username
            matches = re.findall(r'"username"\s*:\s*"([^"]+)"[^}]*"score"\s*:\s*(\d+)', txt)
            for username, score in matches:
                name = f"@{username}" if not username.startswith("@") else username
                total = int(score)
                diff = total - 41
                plus = "E" if diff==0 else (f"+{diff}" if diff>0 else f"{diff}")
                results.append({"name": name, "total": total, "plus_minus": plus})
            if results:
                break

    # dedup best per player
    best = {}
    for r in results:
        n = r["name"]
        if n not in best or r["total"] < best[n]["total"]:
            best[n] = r
    sorted_best = sorted(best.values(), key=lambda x: x["total"])
    top10 = []
    for i, r in enumerate(sorted_best[:10], 1):
        top10.append({"rank": i, "name": r["name"], "total": r["total"], "plus_minus": r["plus_minus"]})
    return top10, results

def try_fetch_udisc():
    if requests is None:
        return None, None

    for slug in UDISC_SLUGS:
        urls = [
            f"https://udisc.com/courses/{slug}",
            f"https://udisc.com/courses/{slug}/leaderboard",
            f"https://udisc.com/courses/{slug}/leaderboards",
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
    print("=== udisc_fetcher.py V30 LIVE - parent 43119 mukana (UDisc 1 layout) ===")
    print(f"DATA_DIR={DATA_DIR}")

    top10_live = None
    source_url = None

    if requests:
        top10_live, source_url = try_fetch_udisc()
    else:
        print("requests puuttuu, käytetään fallback")

    if not top10_live:
        print("UDisc live haku feilasi, käytetään fallback V29")
        top10_live = FALLBACK_TOP
        source_url = "fallback V29"

    data = {
        "course": "UDISC Luoma-aho 12 väylää Par 41 (parent 43119)",
        "parent_course": "43119",
        "par": 41,
        "top10": top10_live,
        "total_rounds": len(top10_live),  # jos live, tämä on vain top10 määrä, oikea total vaatisi API
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "fetched_at_fi": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "source_url": source_url,
        "version": "V30 LIVE - UDisc, parent 43119, fallback jos ei live"
    }

    # jos live löysi enemmän kuin 10, tallenna myös total
    if top10_live and len(top10_live) == 10 and source_url != "fallback V29":
        # yritä arvioida total jos saatiin all_results?
        data["total_rounds"] = len(top10_live)

    (DATA_DIR / "udisc.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: UDisc V30 - {len(top10_live)} pelaajaa, lähde {source_url}")
    for r in top10_live:
        print(f"  {r['rank']}. {r['name']} {r['total']} {r['plus_minus']}")

if __name__ == "__main__":
    main()
