"""
metrix_tilanne_fetcher.py - hakee valitun kilpailun live-tilanteen Metrixistä
API: https://discgolfmetrix.com/api.php?content=result&id=COMPETITION_ID
"""

import json
import pathlib
import re
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    requests = None

BASE = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE / "data" if (BASE / "data").exists() else BASE.parent / "data" if (BASE.parent / "data").exists() else BASE
DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_competition_results(comp_id):
    url = f"https://discgolfmetrix.com/api.php?content=result&id={comp_id}"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        j = r.json()
        comp = j.get("Competition")
        if not comp:
            return None
        results = []
        for i, p in enumerate(comp.get("Results", []), 1):
            results.append({
                "rank": i,
                "name": p.get("Name"),
                "total": p.get("Sum"),
                "plus": f"+{p.get('Diff')}" if p.get('Diff',0)>0 else ("E" if p.get('Diff')==0 else f"{p.get('Diff')}"),
                "diff": p.get("Diff"),
                "userId": p.get("UserID")
            })
        return {
            "id": comp_id,
            "name": comp.get("Name"),
            "date": comp.get("Date"),
            "course": comp.get("CourseName"),
            "courseId": comp.get("CourseID"),
            "url": f"https://discgolfmetrix.com/{comp_id}",
            "results": results,
            "tracks": comp.get("Tracks", [])
        }
    except Exception as e:
        print(f"Fail {comp_id}: {e}")
        return None

def main():
    # Lue metrix_kilpailut.json ja hae aktiivisin kilpailu
    kilpailut_path = DATA_DIR / "metrix_kilpailut.json"
    active_id = None
    active_name = None

    if kilpailut_path.exists():
        try:
            kj = json.loads(kilpailut_path.read_text(encoding="utf-8"))
            upcoming = kj.get("upcoming") or kj.get("kilpailut") or []
            # Etsi aktiivinen (Avoinna / Käynnissä)
            for k in upcoming:
                reg = (k.get("reg") or "").lower()
                if "avoin" in reg or "käynn" in reg or "live" in reg:
                    # Yritä kaivaa ID URL:sta
                    url = k.get("url","")
                    m = re.search(r"competition/(\d+)", url)
                    if m:
                        active_id = m.group(1)
                        active_name = k.get("name")
                        break
            # Jos ei aktiivista, ota uusin
            if not active_id and upcoming:
                k = upcoming[0]
                url = k.get("url","")
                m = re.search(r"competition/(\d+)", url)
                if m:
                    active_id = m.group(1)
                    active_name = k.get("name")
        except Exception as e:
            print(f"Kilpailut JSON luku fail: {e}")

    # Jos ei kilpailut.json:ssa ID:tä, yritä lukea nykyinen tilanne.json ja päivitä se
    tilanne_path = DATA_DIR / "kilpailu_tilanne.json"
    existing = []
    if tilanne_path.exists():
        try:
            old = json.loads(tilanne_path.read_text(encoding="utf-8"))
            existing = old.get("competitions") or []
            if not active_id and existing:
                active_id = str(existing[0].get("id"))
        except:
            pass

    if not active_id:
        print("Ei aktiivista kilpailu ID:tä löytynyt - kortti pysyy tyhjänä kunnes kilpailu valitaan")
        # Kirjoita tyhjä tai säilytä vanha
        if not tilanne_path.exists():
            tilanne_path.write_text(json.dumps({
                "competitions": [],
                "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "version": "V1.0 - ei aktiivista"
            }, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    print(f"Haetaan tilanne kilpailulle {active_id} {active_name or ''}...")
    comp = fetch_competition_results(active_id)
    if not comp:
        print("Ei tuloksia")
        return

    # Päivitä tilanne.json
    data = {
        "competitions": [comp],
        "current": comp,
        "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": f"Metrix API {active_id}",
        "version": "V1.1 live-tilanne"
    }

    tilanne_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Tallennettu {tilanne_path} - {len(comp['results'])} tulosta")

if __name__ == "__main__":
    main()
