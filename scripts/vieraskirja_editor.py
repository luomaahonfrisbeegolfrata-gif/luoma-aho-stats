#!/usr/bin/env python3
"""
vieraskirja_editor.py - Turvallinen käsinmuokkaus työkalu vieraskirjalle
- Ei riko JSONia, validoi ennen tallennusta
- Toimii tyhjälläkin (0 viestiä)
- Päivittää stats automaattisesti
- Backup ennen kirjoitusta

Käyttö:
  python vieraskirja_editor.py --list
  python vieraskirja_editor.py --add --name "Jari S." --message "Rata huippukunnossa!" --rating 5
  python vieraskirja_editor.py --delete 0
  python vieraskirja_editor.py --clear
  python vieraskirja_editor.py (interaktiivinen)
"""

import json
import pathlib
import argparse
import shutil
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [
    BASE / "data" / "vieraskirja.json",
    BASE / "vieraskirja.json",
    BASE.parent / "data" / "vieraskirja.json",
    pathlib.Path.cwd() / "data" / "vieraskirja.json",
    pathlib.Path.cwd() / "vieraskirja.json",
]

def find_path():
    for p in CANDIDATES:
        if p.exists():
            return p
    fallback = BASE / "data" / "vieraskirja.json"
    fallback.parent.mkdir(parents=True, exist_ok=True)
    return fallback

def load(path=None):
    p = pathlib.Path(path) if path else find_path()
    if not p.exists():
        return {"entries": [], "stats": {"count": 0, "avg": 0, "ratings": 0}, "updated": datetime.now().strftime("%Y-%m-%d")}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, list):
            data = {"entries": data, "stats": {"count": len(data), "avg": 0, "ratings": 0}, "updated": datetime.now().strftime("%Y-%m-%d")}
        if "entries" not in data:
            data = {"entries": [], "stats": {"count": 0, "avg": 0, "ratings": 0}, "updated": datetime.now().strftime("%Y-%m-%d")}
        for e in data.get("entries", []):
            e.setdefault("date", datetime.now().strftime("%d.%m.%Y"))
            e.setdefault("name", "Anonyymi")
            e.setdefault("message", "")
            e.setdefault("rating", 0)
        return data
    except Exception as ex:
        print(f"JSON luku epäonnistui {p}: {ex}")
        try:
            backup = p.with_suffix(f".json.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy(p, backup)
            print(f"Backup tehty: {backup}")
        except:
            pass
        return {"entries": [], "stats": {"count": 0, "avg": 0, "ratings": 0}, "updated": datetime.now().strftime("%Y-%m-%d")}

def calc_stats(entries):
    count = len(entries)
    ratings = [e.get("rating",0) for e in entries if e.get("rating",0) > 0]
    avg = round(sum(ratings)/len(ratings),1) if ratings else 0
    return {"count": count, "avg": avg, "ratings": len(ratings)}

def save(data, path=None):
    p = pathlib.Path(path) if path else find_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        try:
            bak = p.with_suffix(f".json.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy(p, bak)
            print(f"Backup: {bak.name}")
        except Exception as e:
            print(f"Backup fail: {e}")
    data["stats"] = calc_stats(data.get("entries",[]))
    data["updated"] = datetime.now().strftime("%Y-%m-%d")
    try:
        txt = json.dumps(data, ensure_ascii=False, indent=2)
        json.loads(txt)
    except Exception as e:
        print(f"JSON validointi epäonnistui: {e}")
        return False
    p.write_text(txt, encoding="utf-8")
    print(f"Tallennettu {p} - {data['stats']['count']} viestiä, avg {data['stats']['avg']}")
    return True

def list_entries(data):
    entries = data.get("entries",[])
    if not entries:
        print("Ei vielä viestejä - tyhjä vieraskirja")
        print("Lisää: python vieraskirja_editor.py --add --name Nimi --message Viesti --rating 5")
        return
    print(f"\nVieraskirja: {len(entries)} viestiä, avg {data.get('stats',{}).get('avg',0)}")
    print("-"*60)
    for i, e in enumerate(entries):
        stars = "★"*e.get("rating",0) + "☆"*(5-e.get("rating",0))
        print(f"{i}: [{e.get('date')}] {e.get('name')} {stars}")
        print(f"   {e.get('message')}")
    print("-"*60)

def add_entry(data, name, message, rating=0, date=None):
    if not date:
        date = datetime.now().strftime("%d.%m.%Y")
    if len(message.strip()) < 3:
        print("Viesti liian lyhyt (min 3 merkkiä)")
        return False
    if rating and (rating < 1 or rating > 5):
        print("Rating pitää olla 1-5")
        return False
    if len(name) > 30:
        print(f"Nimi liian pitkä ({len(name)}), katkaistaan 30")
        name = name[:30]
    if len(message) > 500:
        print(f"Viesti liian pitkä ({len(message)}), katkaistaan 500")
        message = message[:500]
    entry = {
        "date": date,
        "name": name.strip() or "Anonyymi",
        "message": message.strip(),
        "rating": int(rating) if rating else 0
    }
    data["entries"].append(entry)
    print(f"Lisätty: [{date}] {entry['name']} {entry['rating']} tähteä")
    return True

def main():
    parser = argparse.ArgumentParser(description="Vieraskirja editori - turvallinen käsinmuokkaus")
    parser.add_argument("--path", help="Polku vieraskirja.json")
    parser.add_argument("--list", action="store_true", help="Listaa viestit")
    parser.add_argument("--add", action="store_true", help="Lisää viesti")
    parser.add_argument("--name", help="Nimi / nimimerkki (max 30)")
    parser.add_argument("--message", help="Viesti (max 500, min 3)")
    parser.add_argument("--rating", type=int, help="Tähdet 1-5")
    parser.add_argument("--date", help="Päivä DD.MM.YYYY (default tänään)")
    parser.add_argument("--delete", type=int, help="Poista index")
    parser.add_argument("--clear", action="store_true", help="Tyhjennä kaikki")
    args = parser.parse_args()

    path = pathlib.Path(args.path) if args.path else find_path()
    print(f"JSON: {path}")
    data = load(path)

    if args.list:
        list_entries(data)
        return

    if args.delete is not None:
        entries = data.get("entries",[])
        idx = args.delete
        if 0 <= idx < len(entries):
            e = entries[idx]
            print(f"Poistetaan {idx}: [{e.get('date')}] {e.get('name')}")
            confirm = input("Varmista (k/e): ").lower()
            if confirm in ["k","y"]:
                data["entries"].pop(idx)
                save(data, path)
        else:
            print(f"Index {idx} ei välillä 0-{len(entries)-1}")
        return

    if args.clear:
        print(f"Tyhjennetään kaikki {len(data.get('entries',[]))} viestiä!")
        confirm = input("Kirjoita TYHJENNA varmistaaksesi: ")
        if confirm == "TYHJENNA":
            data["entries"] = []
            save(data, path)
            print("Tyhjennetty")
        return

    if args.add:
        if not args.name or not args.message or not args.rating:
            print("--add vaatii --name, --message ja --rating")
            return
        if add_entry(data, args.name, args.message, args.rating, args.date):
            save(data, path)
        return

    print("\n=== Vieraskirja Editori - Interaktiivinen ===")
    list_entries(data)
    print("\n1) Lisää viesti")
    print("2) Poista viesti")
    print("3) Listaa")
    print("4) Tyhjennä kaikki")
    print("0) Lopeta")
    choice = input("\nValinta: ").strip()
    if choice == "1":
        name = input("Nimi (max 30) [Anonyymi]: ").strip() or "Anonyymi"
        message = input("Viesti (max 500, min 3): ").strip()
        while len(message) < 3:
            print("Liian lyhyt!")
            message = input("Viesti: ").strip()
        rating_str = input("Tähdet 1-5: ").strip()
        try:
            rating = int(rating_str)
        except:
            rating = 0
        date = input(f"Päivä DD.MM.YYYY [{datetime.now().strftime('%d.%m.%Y')}]: ").strip() or datetime.now().strftime("%d.%m.%Y")
        if add_entry(data, name, message, rating, date):
            save(data, path)
    elif choice == "2":
        idx_str = input("Poistettava index: ").strip()
        try:
            idx = int(idx_str)
            entries = data.get("entries",[])
            if 0 <= idx < len(entries):
                if input("Varmista k/e: ").lower() in ["k","y"]:
                    data["entries"].pop(idx)
                    save(data, path)
        except:
            print("Virheellinen index")

if __name__ == "__main__":
    main()
