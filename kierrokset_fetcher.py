#!/usr/bin/env python3
"""Kierrokset V7 KORJAA VAARAT KAAVAT - wrapper auto_update_v7.py"""
import subprocess, sys
print("=== kierrokset_fetcher_v2.py V7 KORJAA VAARAT ===")
print("Live 1130=58+1072 VAARA -> 1164=729+435 OIKEA")
for script in ["auto_update_v7.py", "auto_update.py"]:
    try:
        subprocess.run([sys.executable, script], check=True)
        print(f"Ran {script} - 1164 OIKEA")
        break
    except Exception as e:
        print(f"{script} failed: {e}")
        continue
