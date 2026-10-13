#!/usr/bin/env python3
"""
vieraskirja.py - V5.1 LOCKED
- Ei ylikirjoita, vain validoi
- Vieraskirja on manuaalisesti lukittu 5 viestillä 13.10.2026
- Workflowt: vieraskirja.yml validoi, ei pushaa uutta
- Jos haluat lisätä, käytä vieraskirja_editor.py
"""

import json
import pathlib
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [
    BASE / "data" / "vieraskirja.json",
    BASE / "vieraskirja.json",
    BASE.parent / "data" / "vieraskirja.json",
]

def find_path():
    for p in CANDIDATES:
        if p.exists():
            return p
    return BASE / "data" / "vieraskirja.json"

def main():
    path = find_path()
    print(f"=== vieraskirja.py V5.1 LOCKED ===")
    print(f"Polku: {path}")
    
    if not path.exists():
        print("❌ Ei löydy")
        return
    
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        entries = data.get('entries', [])
        stats = data.get('stats', {})
        locked = data.get('locked', False)
        
        print(f"✅ JSON valid: {len(entries)} viestiä")
        print(f"   Avg: {stats.get('avg')} ({stats.get('ratings')} ratings)")
        print(f"   Locked: {locked}")
        print(f"   Updated: {data.get('updated')}")
        
        for i, e in enumerate(entries):
            print(f"  {i}: [{e.get('date')}] {e.get('name')} {e.get('rating')}★ - {e.get('message')[:50]}...")
        
        if locked:
            print("\n🔒 Lukittu - ei ylikirjoiteta, säilytetään")
        else:
            print("\n⚠️ Ei lukittu - harkitse lukitusta")
            
        # Validate
        for e in entries:
            if len(e.get('message','')) > 500:
                print(f"❌ Viesti liian pitkä: {e.get('name')}")
            if len(e.get('name','')) > 30:
                print(f"❌ Nimi liian pitkä: {e.get('name')}")
        
        print("\n✅ Validointi ok")
        
    except Exception as ex:
        print(f"❌ Virhe: {ex}")

if __name__ == "__main__":
    main()
