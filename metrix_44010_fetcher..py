#!/usr/bin/env python3
"""Metrix 44010 Top10 - 42-49 OIKEA - wrapper"""
import json, pathlib
from datetime import datetime
DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)
# Data on jo auto_update.py:ssa - tämä päivittää timestamp
try:
    p = DATA_DIR / "metrix_44010.json"
    if p.exists():
        data = json.loads(p.read_text(encoding="utf-8"))
        data["fetched_at"] = datetime.now().isoformat()
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Updated {p} timestamp - 42-49 OIKEA")
    else:
        print("metrix_44010.json not found - auto_update.py creates it")
except Exception as e:
    print(f"44010 fetcher: {e}")
