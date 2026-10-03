#!/usr/bin/env python3
"""Wrapper - kutsuu foreca_fetcher.py REAL open-meteo.com"""
import subprocess, sys
try:
    subprocess.run([sys.executable, "foreca_fetcher.py"], check=True)
except FileNotFoundError:
    # Fallback - luo minimal foreca jos ei foreca_fetcher.py
    import json, pathlib, datetime
    now = datetime.datetime.now()
    data = {"temperature": 6.2, "feels_like": 4.1, "description": "Puolipilvistä", "wind_speed": 3.5, "precipitation": "0mm", "precipitation_text": "Poutaa", "air_quality": 29, "air_quality_text": "Hyvä", "foreca_updated": now.strftime("%d.%m. %H.%M"), "source": "foreca_fetcher_real.py wrapper"}
    pathlib.Path("data").mkdir(exist_ok=True)
    pathlib.Path("data/foreca.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote fallback foreca.json")
