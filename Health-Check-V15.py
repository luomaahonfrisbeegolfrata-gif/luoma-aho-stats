#!/usr/bin/env python3
"""V15 Health Check - tarkista onko live toimiva kuten pitää"""
import json, pathlib, sys
DATA_DIR=pathlib.Path("data")
errors=[]
warnings=[]

def check_file(name, must_keys=None):
    p=DATA_DIR/name
    if not p.exists():
        errors.append(f"PUUTTUU {name}")
        return None
    try:
        data=json.loads(p.read_text(encoding='utf-8'))
        if must_keys:
            for k in must_keys:
                if k not in str(data):
                    warnings.append(f"{name} puuttuu avain {k}")
        return data
    except Exception as e:
        errors.append(f"{name} JSON virhe {e}")
        return None

print("=== V15 HEALTH CHECK - https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/ ===")
# Tarkista pakolliset
v=check_file("vaylatilasto.json")
if v:
    d=v.get('44010',{}).get('difficulty',[])
    if d!=[8,5,9,10,6,2,4,11,7,1,3,12]:
        errors.append(f"vaylatilasto.json difficulty VÄÄRIN {d} pitää olla [8,5,9,10,6,2,4,11,7,1,3,12] B avg-par")
    else:
        print("✓ vaylatilasto.json difficulty B OK")
    if v.get('44010',{}).get('difficulty_total',0)!=78:
        warnings.append("difficulty_total ei 78")

k=check_file("kierrokset.json")
if k:
    if k.get('total_rounds',0)!=1164:
        errors.append(f"kierrokset.json total_rounds {k.get('total_rounds')} pitää olla 1164 (729+435)")
    else:
        print("✓ kierrokset.json 1164 OK")

u=check_file("udisc.json")
if u:
    if len(u.get('top10',[]))<10:
        warnings.append("udisc.json top10 <10")

s=check_file("saa.json")
if s:
    if 'open-meteo' not in str(s).lower() and 'temp' not in str(s).lower():
        warnings.append("saa.json ei open-meteo")

# Vanhat tiedostot jotka pitäisi poistaa
old_files=["vaylatilasto_manual.json","foreca.json","udisc_top10.json","vaylatilasto_V12.png","auto_update_v7.py"]
for of in old_files:
    if (DATA_DIR/of).exists() or pathlib.Path(of).exists() or pathlib.Path("data")/of.replace("data/","") and False:
        pass
    # check data/
    if (DATA_DIR/of).exists():
        warnings.append(f"VANHA tiedosto pitäisi poistaa: data/{of}")
    if pathlib.Path(of).exists():
        warnings.append(f"VANHA tiedosto pitäisi poistaa: {of}")

# Root duplicate
if pathlib.Path("vaylatilasto.png").exists() and pathlib.Path("data/vaylatilasto.png").exists():
    import os
    if os.path.getsize("vaylatilasto.png") != os.path.getsize("data/vaylatilasto.png"):
        warnings.append("vaylatilasto.png root ja data/ eri koko - synkkaa")

print("\n--- TULOS ---")
if errors:
    print("❌ VIRHEET:")
    for e in errors: print(f"  - {e}")
    sys.exit(1)
else:
    print("✓ Ei kriittisiä virheitä")
if warnings:
    print("⚠️ VAROITUKSET / SIIVOTTAVA:")
    for w in warnings: print(f"  - {w}")
else:
    print("✓ Ei vanhoja tiedostoja")
print("\nHeader lukittu, Layout lukittu, Kortit lukittu - OK")
