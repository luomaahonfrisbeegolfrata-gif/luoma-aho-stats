"""
vaylatilasto_fetcher.py - V30 LIVE - yrittää hakea oikean väylätilaston Metrixistä
- Kokeilee useita URL patterneja course statistics Table näkymälle
- Parsii: Pituus, Par, Avg, Difficulty, HIO, Birdie, Par, Bogey, Dbl, Tpl, Other
- Fallback: käyttää lukittua dataa kuvasta (V29) jos fetch feilaa -> ei riko layoutia (sääntö 6)

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
    if c.exists() and ((c / "vaylatilasto.json").exists() or c.name == "data"):
        DATA_DIR = c if c.name == "data" else c
        break
if DATA_DIR is None:
    DATA_DIR = BASE.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8",
}

# lukittu fallback kuvasta - V29
FALLBACK = {
    "vayla_count": 12,
    "par_total": 41,
    "pituus_total": "1248m",
    "avg_total": "49.05",
    "difficulty_total": 78,
    "pituus": ["125m", "103m", "72m", "57m", "94m", "96m", "103m", "80m", "116m", "85m", "197m", "120m", "1248m", "-"],
    "par": ["4", "3", "3", "3", "3", "3", "3", "3", "4", "3", "5", "4", "41", "-"],
    "avg": ["4.45", "3.77", "3.45", "3.42", "3.55", "4.18", "3.79", "3.33", "4.53", "4.20", "6.15", "4.23", "49.05", "-"],
    "avgCls": ["cell-red", "cell-yellow", "cell-green", "cell-green", "cell-yellow", "cell-orange", "cell-yellow", "cell-green", "cell-red", "cell-orange", "cell-red", "cell-orange", "cell-dark", "cell-dark"],
    "difficulty": ["8", "5", "9", "10", "6", "2", "4", "11", "7", "1", "3", "12", "78", "-"],
    "diffCls": ["cell-yellow", "cell-orange", "cell-yellow", "cell-green", "cell-orange", "cell-red", "cell-orange", "cell-green", "cell-yellow", "cell-red", "cell-red", "cell-green", "cell-dark", "cell-dark"],
    "hio": ["0", "0", "0", "4", "0", "0", "0", "1", "0", "0", "0", "0", "5", "0.3%"],
    "birdie": ["14", "4", "14", "25", "3", "4", "10", "19", "8", "6", "11", "24", "142", "8.7%"],
    "par0": ["59", "52", "77", "32", "69", "38", "53", "73", "55", "34", "31", "67", "640", "39.2%"],
    "bogey": ["31", "65", "34", "64", "46", "49", "51", "38", "38", "48", "48", "35", "547", "33.5%"],
    "dbl": ["18", "16", "14", "6", "11", "24", "21", "7", "12", "38", "31", "6", "204", "12.5%"],
    "tpl": ["3", "3", "2", "4", "5", "15", "6", "1", "4", "9", "11", "1", "64", "3.9%"],
    "other": ["1", "1", "0", "1", "1", "8", "1", "0", "5", "4", "5", "1", "28", "1.7%"],
}

def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.text

def parse_vaylatilasto_from_html(html):
    """
    Yrittää parsia Course statistics Table näkymän.
    Rakenne: rivejä: Par, Avg, Difficulty, Birdie, Par, Bogey jne.
    Sarakkeet: 1..12, Tot, %
    """
    soup = BeautifulSoup(html, "lxml")
    # etsi taulukko jossa otsikko "Par" ja sarakkeet 1..12
    for table in soup.find_all("table"):
        text = table.get_text(" ", strip=True)
        # pitää sisältää Par ja Avg tai Birdie
        if "Par" not in text:
            continue
        rows = table.find_all("tr")
        if len(rows) < 3:
            continue
        # kerää rivit
        data = {}
        for tr in rows:
            cells = [c.get_text(strip=True) for c in tr.find_all(["th","td"])]
            if not cells:
                continue
            first = cells[0].lower()
            # tunnista rivit
            if "pituus" in first or "distance" in first:
                data["pituus"] = cells[1:]
            elif first == "par" or first.startswith("par "):
                data["par"] = cells[1:]
            elif "avg" in first:
                data["avg"] = cells[1:]
            elif "difficult" in first:
                data["difficulty"] = cells[1:]
            elif "hole in one" in first or "hio" in first:
                data["hio"] = cells[1:]
            elif "birdie" in first:
                data["birdie"] = cells[1:]
            elif "bogey" in first and "dbl" not in first and "tpl" not in first:
                # tarkista onko Par vai Bogey
                if "par" in first and "0" in first:
                    data["par0"] = cells[1:]
                elif first == "bogey" or "bogey 1" in first:
                    data["bogey"] = cells[1:]
            elif "dbl" in first or "double" in first:
                data["dbl"] = cells[1:]
            elif "tpl" in first or "triple" in first:
                data["tpl"] = cells[1:]
            elif "other" in first or ">3" in first:
                data["other"] = cells[1:]
        # jos löytyi par ja avg, se on oikea taulukko
        if "par" in data and "avg" in data:
            return data
    return None

def try_fetch_course_stats(course_id):
    # kokeillaan useita URL patterneja - Metrix voi vaatia eri view param
    patterns = [
        f"https://discgolfmetrix.com/course/{course_id}",
        f"https://discgolfmetrix.com/course/{course_id}?view=statistics_table",
        f"https://discgolfmetrix.com/course/{course_id}?view=table",
        f"https://discgolfmetrix.com/?u=course_statistics&ID={course_id}",
        f"https://discgolfmetrix.com/?u=course&ID={course_id}&view=statistics",
    ]
    for url in patterns:
        try:
            print(f"  Kokeillaan {url}")
            html = fetch_html(url)
            parsed = parse_vaylatilasto_from_html(html)
            if parsed:
                print(f"    -> löytyi tilasto {list(parsed.keys())}")
                return parsed, url
        except Exception as e:
            print(f"    fail {url}: {e}")
            continue
    return None, None

def build_full_vaylatilasto(parsed_partial=None):
    # yhdistä parsed + fallback
    # jos parsinta onnistui osittain, käytä sitä, muuten fallback
    data = {}
    base = FALLBACK.copy()
    if parsed_partial:
        # yritä yhdistää
        for k in ["pituus","par","avg","difficulty","hio","birdie","par0","bogey","dbl","tpl","other"]:
            if k in parsed_partial and len(parsed_partial[k]) >= 12:
                # siisti
                base[k] = parsed_partial[k][:14]  # 12 + Tot + %
        data = base
        # laske värikoodit uudelleen jos avg muuttui
        # jätetään fallback värit jos ei lasketa
    else:
        data = base

    # varmista että kaikki kentät on olemassa
    for k in FALLBACK:
        if k not in data:
            data[k] = FALLBACK[k]

    # lisää meta
    data["vayla_count"] = 12
    data["par_total"] = data["par"][-2] if len(data["par"])>=13 else "41"
    data["pituus_total"] = data["pituus"][-2] if len(data["pituus"])>=13 else "1248m"
    data["avg_total"] = data["avg"][-2] if len(data["avg"])>=13 else "49.05"
    data["difficulty_total"] = 78
    data["fetched_at"] = datetime.now(timezone.utc).isoformat()
    data["version"] = "V30 LIVE - yrittää Metrix, fallback lukittu"
    return data

def main():
    print("=== vaylatilasto_fetcher.py V30 LIVE ===")
    print(f"DATA_DIR={DATA_DIR}")
    if requests is None:
        print("requests puuttuu, käytetään fallback")
        data = build_full_vaylatilasto(None)
        (DATA_DIR / "vaylatilasto.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    # yritä hakea 44010 (12 väylää) ensin, sitten 43119 parent
    parsed = None
    url_ok = None
    for cid in ["44010", "43119", "44763"]:
        p, u = try_fetch_course_stats(cid)
        if p:
            parsed = p
            url_ok = u
            print(f"OK: saatiin väylätilasto course {cid} url {u}")
            break

    data = build_full_vaylatilasto(parsed)
    if url_ok:
        data["source_url"] = url_ok
        data["source_course"] = cid

    (DATA_DIR / "vaylatilasto.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: vaylatilasto.json -> {data['vayla_count']} väylää Tot {data['pituus_total']} Par {data['par_total']}")

if __name__ == "__main__":
    main()
