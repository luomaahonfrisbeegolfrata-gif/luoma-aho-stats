"""
metrix_fetcher.py - V30 LIVE - parent 43119 + lapset 44010,44763
- Hakee oikeasti discgolfmetrix.com/course/{id}
- Parsii TOP10 (paras per pelaaja) + kaikki tulokset total_rounds ja unique_players
- Parent 43119: kerää kaikki child layout id:t sivulta ja summaa
- Toimii GitHub Actionsissa (requests + bs4)
- Fallback: jos fetch feilaa, lukee vanhan jsonin ja säilyttää layoutin (sääntö 5)

Asenna Actionsissa:
pip install requests beautifulsoup4 lxml
"""
import json
import pathlib
import re
import sys
from datetime import datetime, timezone
from collections import defaultdict

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None

# Polku: toimii sekä scripts/ että rootista
BASE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [
    BASE.parent / "data",
    BASE / "data",
    BASE.parent.parent / "data",
    BASE,
    pathlib.Path.cwd() / "data",
]
DATA_DIR = None
for c in CANDIDATES:
    if c.exists():
        # jos tässä on metrix_*.json tai se on nimeltään data, käytä
        if (c / "metrix_44010.json").exists() or c.name == "data":
            DATA_DIR = c if c.name == "data" else c
            break
if DATA_DIR is None:
    DATA_DIR = BASE.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8",
}

# tunnetut layoutit parentin 43119 alta
KNOWN_LAYOUTS = {
    "44010": {"par": 41, "name": "Väyläopaste / Pro 12 väylää"},
    "44763": {"par": 82, "name": "2 kierrosta 24 väylää Par 82"},
    # lisää jos löytyy parentista
}

PARENT_ID = "43119"

def fetch_html(url, timeout=20):
    if requests is None:
        raise RuntimeError("requests puuttuu")
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    # Metrix voi palauttaa 200 vaikka sisältö on login-wall - tarkista
    if "Login" in r.text and "Top results" not in r.text and "Layouts" not in r.text:
        # yritä silti parsia
        pass
    return r.text

def parse_top_results_table(html, course_id):
    """Parsii Top results taulukon. Palauttaa listan dict: name,total,plus_minus,date,all_scores"""
    soup = BeautifulSoup(html, "lxml" if "lxml" in sys.modules else "html.parser")
    results = []

    # etsi kaikki taulukot
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue
        # tarkista onko Par-rivi
        table_text = table.get_text(" ", strip=True)
        if "Par" not in table_text:
            continue
        # header tarkistus: sisältää 1 2 3 ...
        first_row_cells = [c.get_text(strip=True) for c in rows[0].find_all(["th","td"])]
        if not any(c == "1" or c.startswith("1") for c in first_row_cells):
            # joskus eka rivi on tyhjä, toka on Par
            pass

        # yritä löytää Par-rivi
        par_row_idx = -1
        for idx, tr in enumerate(rows):
            cells = [c.get_text(strip=True) for c in tr.find_all(["th","td"])]
            if "Par" in cells:
                par_row_idx = idx
                break
        if par_row_idx == -1:
            continue
        # kaikki sen jälkeen on tuloksia
        for tr in rows[par_row_idx+1:]:
            tds = tr.find_all(["td","th"])
            if len(tds) < 4:
                continue
            cells = [c.get_text(strip=True) for c in tds]
            # rakenne: 0=rank,1=name,2=date, ..., -2=+/-, -1=total
            # rank voi olla "1" tai "1 " etc
            rank_raw = cells[0]
            if not re.match(r"^\d+", rank_raw):
                continue
            name = cells[1]
            if not name or len(name) < 2:
                continue
            if name.lower() in ("par","avg","name"):
                continue
            # total ja plus
            try:
                total_raw = cells[-1]
                plus_raw = cells[-2] if len(cells) >= 2 else "E"
                # total voi olla "42" tai "82"
                total_match = re.search(r"(\d+)", total_raw)
                if not total_match:
                    continue
                total = int(total_match.group(1))
                plus = plus_raw.strip()
                if plus == "":
                    # laske parista jos tiedetään? jätetään E
                    plus = "E"
                # normalisoi plus: "E", "+1", "-6" etc
                if plus != "E" and not plus.startswith(("+","-")):
                    # jos plus on numero ilman merkkiä, lisää +
                    if plus.isdigit():
                        plus = f"+{plus}"
                date = cells[2] if len(cells) > 2 else ""
                results.append({
                    "rank_raw": rank_raw,
                    "name": name,
                    "total": total,
                    "plus_minus": plus,
                    "date": date,
                    "course_id": course_id,
                })
            except Exception as e:
                continue
        if results:
            # löydettiin tuloksia tästä taulukosta
            break

    return results

def parse_parent_layouts(html):
    """Parent 43119 sivulta: etsi kaikki /course/<id> linkit"""
    soup = BeautifulSoup(html, "lxml" if "lxml" in sys.modules else "html.parser")
    ids = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = re.search(r"/course/(\d+)", href)
        if m:
            cid = m.group(1)
            if cid != PARENT_ID:
                ids.add(cid)
    # myös tekstistä
    for m in re.finditer(r"/course/(\d+)", html):
        cid = m.group(1)
        if cid != PARENT_ID:
            ids.add(cid)
    return sorted(ids)

def best_per_player(results):
    best = {}
    for r in results:
        n = r["name"]
        # pidä paras (pienin total)
        if n not in best or r["total"] < best[n]["total"]:
            best[n] = r
    # järjestä
    sorted_best = sorted(best.values(), key=lambda x: x["total"])
    return sorted_best, best

def fetch_course(course_id, par_hint=None):
    url = f"https://discgolfmetrix.com/course/{course_id}"
    print(f"Fetching {course_id} -> {url}")
    try:
        html = fetch_html(url)
        results = parse_top_results_table(html, course_id)
        if not results:
            print(f"  VARO: ei tuloksia {course_id}, html len {len(html)}")
            # tallenna debug
            # (DATA_DIR / f"debug_{course_id}.html").write_text(html, encoding="utf-8")
        sorted_best, best_dict = best_per_player(results)
        top10 = []
        for i, r in enumerate(sorted_best[:10], 1):
            top10.append({
                "rank": i,
                "name": r["name"],
                "total": r["total"],
                "plus_minus": r["plus_minus"],
                "date": r.get("date",""),
                "course_id": course_id,
            })
        return {
            "course_id": course_id,
            "par": par_hint,
            "top10": top10,
            "all_results": results,
            "unique_players": list(best_dict.keys()),
            "total_results": len(results),
            "fetched": True,
        }
    except Exception as e:
        print(f"  FAIL {course_id}: {e}")
        return {
            "course_id": course_id,
            "par": par_hint,
            "top10": [],
            "all_results": [],
            "unique_players": [],
            "total_results": 0,
            "fetched": False,
            "error": str(e),
        }

def load_fallback(course_id):
    try:
        data = json.loads((DATA_DIR / f"metrix_{course_id}.json").read_text(encoding="utf-8"))
        return data.get("top10", [])
    except:
        return []

def main():
    print("=== metrix_fetcher.py V30 LIVE - parent 43119 ===")
    print(f"DATA_DIR={DATA_DIR}")

    # 1. hae parent ja sen lapset
    all_course_ids = set(KNOWN_LAYOUTS.keys())
    try:
        if requests:
            html_parent = fetch_html(f"https://discgolfmetrix.com/course/{PARENT_ID}")
            child_ids = parse_parent_layouts(html_parent)
            print(f"Parent {PARENT_ID} löytyi {len(child_ids)} layoutia: {child_ids}")
            # lisää tunnetut + löydetyt, suodata järkevät (vain ne jotka on Luoma-aho)
            for cid in child_ids:
                # rajaa vain jos näyttää Luoma-ahoihin liittyvältä? Nyt otetaan kaikki, mutta max 15
                all_course_ids.add(cid)
    except Exception as e:
        print(f"Parent haku feilasi: {e}, käytetään tunnetut {list(all_course_ids)}")

    # rajaa: ota vain 43119 + 44010 + 44763 jos muita paljon (ettei spämmätä)
    # Jos parent löysi yli 10, ota vain ne jotka on KNOWN tai par 41/82
    if len(all_course_ids) > 6:
        print(f"Liikaa layouteja ({len(all_course_ids)}), rajataan tunnettuihin + 44010,44763")
        all_course_ids = set(KNOWN_LAYOUTS.keys())

    # lisää parent itse listaan jos halutaan laskea sen kautta kaikki?
    # Parentilla ei ole suoraan tuloksia, mutta sen childien kautta

    results_by_course = {}
    all_players_global = []
    total_rounds_global = 0

    for cid in sorted(all_course_ids):
        par_hint = KNOWN_LAYOUTS.get(cid, {}).get("par")
        res = fetch_course(cid, par_hint)
        # fallback jos ei saatu
        if not res["top10"]:
            fb = load_fallback(cid)
            if fb:
                print(f"  Käytetään fallback top10 {cid} ({len(fb)} kpl)")
                res["top10"] = fb
                # älä laske total_rounds fallbackista
        results_by_course[cid] = res
        all_players_global.extend(res["unique_players"])
        total_rounds_global += res["total_results"]

        # kirjoita course json
        out = {
            "course_id": cid,
            "par": res.get("par") or (KNOWN_LAYOUTS.get(cid, {}).get("par") if cid in KNOWN_LAYOUTS else None),
            "top10": res["top10"],
            "total_results": res["total_results"],
            "unique_players": len(res["unique_players"]),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "version": "V30 LIVE - parent 43119",
        }
        # säilytä myös all_results jos halutaan debug
        (DATA_DIR / f"metrix_{cid}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {cid}: top10 {len(res['top10'])} total_results {res['total_results']} uniikit {len(res['unique_players'])}")

    # Parent kooste
    parent_out = {
        "parent_id": PARENT_ID,
        "child_courses": sorted(list(all_course_ids)),
        "total_rounds_all_layouts": total_rounds_global,
        "unique_players_all_layouts": len(set(all_players_global)),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V30 LIVE - parent kooste",
    }
    (DATA_DIR / f"metrix_{PARENT_ID}.json").write_text(json.dumps(parent_out, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. Laske kierrokset.json myös tässä (jos kierrokset.py ei aja)
    # Mutta jätetään varsinainen laskenta kierrokset.py:lle, tässä vain info
    print(f"OK: total_rounds_global (Metrix) = {total_rounds_global}, uniikit Metrix = {len(set(all_players_global))}")
    print(f"Kirjoitettu {len(results_by_course)} kurssitiedostoa")

if __name__ == "__main__":
    main()
