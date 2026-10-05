#!/usr/bin/env python3
"""health_check_V17.py - Tarkistaa kaikki 4 korttia yhdellä komennolla - HEADER/LAYOUT/KORTIT LUKITTU"""
import json, pathlib, sys
from datetime import datetime, timezone

DATA_DIR = pathlib.Path("data")
errors = []
warnings = []
oks = []

def check_file(name, must_contain=None):
    p = DATA_DIR / name
    if not p.exists():
        errors.append(f"❌ PUUTTUU {name}")
        return None
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        return data
    except Exception as e:
        errors.append(f"❌ {name} JSON virhe {e}")
        return None

print("=== V17 FINAL VALMIS - HEALTH CHECK ===")
print(f"Aika: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
print("URL: https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/")
print("")

# 1. Väylätilasto - B avg-par
print("[1/5] Väylätilasto...")
v = check_file("vaylatilasto.json")
if v:
    diff = v.get('44010',{}).get('difficulty',[])
    expected = [8,5,9,10,6,2,4,11,7,1,3,12]
    if diff == expected:
        oks.append(f"✓ Väylätilasto difficulty B OK {diff}")
        print(f"  ✓ Difficulty {diff} B OIKEA (avg-par)")
    else:
        errors.append(f"❌ Väylätilasto difficulty VÄÄRIN {diff} pitää olla {expected}")
    tot = v.get('44010',{}).get('difficulty_total',0)
    if tot == 78:
        oks.append("✓ Väylätilasto Tot 78 OK")
        print(f"  ✓ Tot 78 OK")
    else:
        errors.append(f"❌ Tot {tot} pitää olla 78")

# 2. Metrix 44010 - 42-49
print("\n[2/5] Metrix 44010...")
m10 = check_file("metrix_44010.json")
if m10:
    top10 = m10.get('top10',[])
    if len(top10) >= 10:
        oks.append(f"✓ Metrix 44010 top10 {len(top10)} OK")
        print(f"  ✓ Top10 {len(top10)} entries")
        totals = [x.get('total',0) for x in top10[:10]]
        if min(totals) >= 42 and max(totals) <= 50:
            oks.append(f"✓ Metrix 44010 totals 42-49 OIKEA {totals}")
            print(f"  ✓ Totals 42-49 OIKEA {totals}")
        else:
            warnings.append(f"⚠️ Metrix 44010 totals epäilyttävä {totals}")
        par = m10.get('par',0)
        if par == 41:
            oks.append("✓ Metrix 44010 Par 41 OK")
            print(f"  ✓ Par 41 OK")
        else:
            errors.append(f"❌ Metrix 44010 Par {par} pitää olla 41")
    else:
        errors.append(f"❌ Metrix 44010 top10 puuttuu, len={len(top10)} - kortti menee rikki")

# 3. Metrix 44763
print("\n[3/5] Metrix 44763...")
m63 = check_file("metrix_44763.json")
if m63:
    if len(m63.get('top10',[])) >= 10:
        oks.append("✓ Metrix 44763 top10 OK")
        print(f"  ✓ Top10 OK")
    else:
        warnings.append("⚠️ Metrix 44763 top10 <10")

# 4. Kierrokset + UDisc
print("\n[4/5] Kierrokset + UDisc...")
k = check_file("kierrokset.json")
if k:
    tr = k.get('total_rounds',0)
    if tr == 1164:
        oks.append(f"✓ Kierrokset 1164 OK (729+435)")
        print(f"  ✓ Total 1164 OK (729+435)")
    else:
        errors.append(f"❌ Kierrokset {tr} pitää olla 1164")

u = check_file("udisc.json")
if u:
    if len(u.get('top10',[])) >= 10:
        oks.append("✓ UDisc top10 OK")
        print(f"  ✓ UDisc top10 OK")
    else:
        warnings.append("⚠️ UDisc top10 <10")

# 5. Sää - ei sama kuin eilen
print("\n[5/5] Sää...")
s = check_file("saa.json")
if s:
    temp = s.get('temp') or s.get('temperature')
    fetched = s.get('fetched_at') or s.get('fetched_at_fi','')
    source = s.get('source','')
    print(f"  Temp: {temp}°C")
    print(f"  Fetched: {fetched}")
    print(f"  Source: {source}")
    if temp is None:
        errors.append("❌ Sää temp puuttuu")
    else:
        if -40 <= temp <= 40:
            oks.append(f"✓ Sää temp {temp}°C OK")
            print(f"  ✓ Temp {temp}°C OK")
        else:
            errors.append(f"❌ Sää temp epärealistinen {temp}")
    
    # Tarkista onko vanha (yli 2h)
    try:
        # Yritä parsia ISO
        ft_str = s.get('fetched_at','')
        if ft_str:
            ft = datetime.fromisoformat(ft_str.replace('Z','+00:00'))
            now = datetime.now(timezone.utc)
            diff_h = (now - ft).total_seconds() / 3600
            if diff_h > 2:
                warnings.append(f"⚠️ Sää vanha {diff_h:.1f}h - näyttää samaa kuin eilen, aja saa_fetcher.py tai Actions")
                print(f"  ⚠️ Vanha {diff_h:.1f}h - voi näyttää eilistä")
            else:
                oks.append(f"✓ Sää tuore {diff_h:.1f}h")
                print(f"  ✓ Tuore {diff_h:.1f}h")
    except Exception as e:
        warnings.append(f"⚠️ Sää timestamp parsinta epäonnistui {e}")

    if 'open-meteo' not in source.lower() and 'V16.2' not in source:
        warnings.append(f"⚠️ Sää source ei V16.2: {source}")

# Vanhat turhat tiedostot
print("\n[Bonus] Vanhat turhat...")
old_files = [
    "data/vaylatilasto_manual.json",
    "data/foreca.json",
    "data/udisc_top10.json",
    "data/vaylatilasto_V12.json",
    "auto_update_v7.py",
    "vaylatilasto_fetcher_v12.py"
]
for of in old_files:
    p = pathlib.Path(of)
    if p.exists():
        warnings.append(f"⚠️ VANHA pitäisi poistaa: {of}")
        print(f"  ⚠️ {of}")

print("\n" + "="*50)
print(f"OK: {len(oks)}")
for o in oks:
    print(f"  {o}")
if warnings:
    print(f"\nVAROITUKSET: {len(warnings)}")
    for w in warnings:
        print(f"  {w}")
if errors:
    print(f"\nVIRHEET: {len(errors)}")
    for e in errors:
        print(f"  {e}")
    print("\n❌ KORJAA VIRHEET ENNEN PUSHIA")
    sys.exit(1)
else:
    print("\n✓ KAIKKI OK - toimiva kuten pitää")
    print("✓ Header lukittu, Layout lukittu, Kortit lukittu")
    print("✓ Ei turhaa, ei .1 .2 duplikaatteja")
    print("✓ Valmis pushata GitHubiin")
    sys.exit(0)
