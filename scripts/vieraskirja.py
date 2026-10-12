"""
vieraskirja.py - Tyhjä mutta toimiva vieraskirja-käsittelijä
- Lukee data/vieraskirja.json
- Laskee stats (count, avg)
- Toimii GitHub Actionsissa ja paikallisesti
- Tyhjä aloitus, toimii kun entries on []
"""

import json
import pathlib
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [
    BASE / "data" / "vieraskirja.json",
    BASE / "data" / "vieraskirja.json",
    BASE.parent / "data" / "vieraskirja.json",
    BASE / "vieraskirja.json",
    pathlib.Path.cwd() / "data" / "vieraskirja.json",
]

def find_json_path():
    for p in CANDIDATES:
        if p.exists():
            return p
    # fallback: luo data dir
    fallback = BASE / "data" / "vieraskirja.json"
    if not fallback.parent.exists():
        fallback.parent.mkdir(parents=True, exist_ok=True)
    return fallback

def load_vieraskirja(path=None):
    """Lataa vieraskirja, palauttaa dict"""
    p = pathlib.Path(path) if path else find_json_path()
    try:
        if not p.exists():
            return {"entries": [], "stats": {"count": 0, "avg": 0, "ratings": 0}, "updated": datetime.now().strftime("%Y-%m-%d")}
        data = json.loads(p.read_text(encoding="utf-8"))
        # Tuki myös array-muodolle
        if isinstance(data, list):
            return {"entries": data, "stats": {"count": len(data), "avg": 0, "ratings": 0}, "updated": datetime.now().strftime("%Y-%m-%d")}
        # Varmista rakenne
        if "entries" not in data:
            data = {"entries": data.get("entries", []), "stats": data.get("stats", {"count": 0, "avg": 0, "ratings": 0}), "updated": data.get("updated", datetime.now().strftime("%Y-%m-%d"))}
        return data
    except Exception as e:
        print(f"load fail {p}: {e}")
        return {"entries": [], "stats": {"count": 0, "avg": 0, "ratings": 0}, "updated": datetime.now().strftime("%Y-%m-%d")}

def calc_stats(entries):
    """Laske stats tyhjästäkin"""
    count = len(entries)
    ratings = [e.get("rating", 0) for e in entries if e.get("rating", 0) > 0]
    avg = round(sum(ratings) / len(ratings), 1) if ratings else 0
    return {
        "count": count,
        "avg": avg,
        "ratings": len(ratings)
    }

def save_vieraskirja(data, path=None):
    """Tallenna vieraskirja"""
    p = pathlib.Path(path) if path else find_json_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    # Päivitä stats ja updated
    data["stats"] = calc_stats(data.get("entries", []))
    data["updated"] = datetime.now().strftime("%Y-%m-%d")
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: Tallennettu {p} - {data['stats']['count']} viestiä, avg {data['stats']['avg']}")
    return p

def add_entry(name, message, rating=0, date=None, path=None):
    """Lisää yksi entry (testikäyttöön)"""
    data = load_vieraskirja(path)
    if date is None:
        date = datetime.now().strftime("%d.%m.%Y")
    entry = {
        "date": date,
        "name": (name or "Anonyymi")[:30],
        "message": (message or "")[:500],
        "rating": int(rating) if rating else 0
    }
    data["entries"].append(entry)
    save_vieraskirja(data, path)
    return entry

def main():
    print("=== vieraskirja.py - Tyhjä mutta toimiva ===")
    p = find_json_path()
    print(f"JSON_PATH={p}")
    data = load_vieraskirja(p)
    print(f"Entries: {len(data.get('entries', []))} kpl")
    print(f"Stats: {data.get('stats')}")
    # Jos tyhjä, älä tee mitään, mutta varmista että tiedosto on olemassa ja validi
    if len(data.get("entries", [])) == 0:
        print("Tyhjä vieraskirja - luodaan tyhjä tiedosto")
        save_vieraskirja(data, p)
    else:
        # Päivitä stats jos vanha
        save_vieraskirja(data, p)
    print("OK - vieraskirja toimii")

if __name__ == "__main__":
    main()
