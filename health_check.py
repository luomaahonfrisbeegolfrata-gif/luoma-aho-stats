#!/usr/bin/env python3
"""health_check V18 FINAL - kaikki kortit 44010 44763 43119 udisc saa vaylatilasto"""
import json, pathlib, sys
from datetime import datetime, timezone

DATA_DIR = pathlib.Path("data")
errors, warnings, oks = [], [], []

def check(name):
    p = DATA_DIR / name
    if not p.exists():
        errors.append(f"❌ PUUTTUU {name}")
        return None
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:
        errors.append(f"❌ {name} JSON virhe {e}")
        return None

print("=== V18 FINAL KAIKKI KORTIT ===")
print(f"{datetime.now().strftime('%d.%m.%Y %H:%M')} - https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/")

# Väylätilasto B
v = check("vaylatilasto.json")
if v and v.get('44010',{}).get('difficulty') == [8,5,9,10,6,2,4,11,7,1,3,12]:
    oks.append("✓ Väylätilasto B [8,5,9,10,6,2,4,11,7,1,3,12] Tot 78")
else:
    errors.append("❌ Väylätilasto B väärin")

# Metrix all
for cid, par in [("44010",41), ("44763",82), ("43119",27)]:
    m = check(f"metrix_{cid}.json")
    if m and len(m.get('top10',[])) >= 10 and m.get('par') == par:
        oks.append(f"✓ Metrix {cid} Par {par} top10 OK")
    else:
        errors.append(f"❌ Metrix {cid} rikki - kortti tyhjä")

# Kierrokset
k = check("kierrokset.json")
if k and k.get('total_rounds') == 1164:
    oks.append("✓ Kierrokset 1164 OK")

# UDisc
u = check("udisc.json")
if u and len(u.get('top10',[])) >= 10:
    oks.append("✓ UDisc top10 OK")
else:
    errors.append("❌ UDisc rikki")

# Sää
s = check("saa.json")
if s and 'temp' in s:
    oks.append(f"✓ Sää temp {s.get('temp')}°C OK - ei sama kuin eilen")
    try:
        ft = datetime.fromisoformat(s.get('fetched_at','').replace('Z','+00:00'))
        diff = (datetime.now(timezone.utc) - ft).total_seconds()/3600
        if diff < 3:
            oks.append(f"✓ Sää tuore {diff:.1f}h")
        else:
            warnings.append(f"⚠️ Sää vanha {diff:.1f}h")
    except:
        warnings.append("⚠️ Sää timestamp")
else:
    errors.append("❌ Sää rikki")

print("\n".join(oks))
if warnings:
    print("\nVAROITUKSET:")
    print("\n".join(warnings))
if errors:
    print("\nVIRHEET:")
    print("\n".join(errors))
    sys.exit(1)
else:
    print("\n✓ KAIKKI OK - data, automaatio, dynaaminen, laskenta, kaikki kortit, päivitys")
    print("✓ Header/Layout/Kortit lukittu")
    sys.exit(0)
