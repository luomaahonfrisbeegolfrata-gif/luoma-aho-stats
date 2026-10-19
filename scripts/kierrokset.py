
"""
kierrokset.py - V6.3 AUTOMAATTINEN + YLIKIRJOITUSSUOJA
- Laskee automaattisesti total_rounds Metrix + UDisc tiedoista
- YLIKIRJOITUS ESTETTY: ei koskaan laske alaspäin, vain ylöspäin
- Jos fetcher epäonnistuu tai antaa pienemmän luvun, säilytetään vanha
- Käytetään GitHub Actionsissa automaattisesti
- V6.2: 1221 kierrosta (768+453) -> V6.3 automaattinen suoja
"""

import json
import pathlib
from datetime import datetime, timezone

BASE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [
    BASE.parent / "data",
    BASE / "data",
    BASE.parent.parent / "data",
    BASE,
    pathlib.Path.cwd() / "data",
]
DATA_DIR = None
for c in CANDIDATES:
    if c.exists():
        if (c / "metrix_44010.json").exists() or c.name == "data":
            DATA_DIR = c if c.name == "data" else c
            break
if DATA_DIR is None:
    DATA_DIR = BASE.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Referenssiarvot laskentaan (keskiarvot per kierros)
REF_TOTAL = 1194  # vanha ref 750+444
REF_PELIAIKA = 1594  # tuntia
REF_ASKELEET = 3364508
REF_KM = 2453

# Nykyiset lukitut arvot (19.10.2026) - minimi jota ei aliteta
MIN_TOTAL = 1221
MIN_METRIX = 768
MIN_UDISC = 453
MIN_PELIAIKA = 1627
MIN_ASKELEET = 3437283
MIN_KM = 2506
MIN_UNIQUE = 133

def load_json(name):
    try:
        p = DATA_DIR / name
        if not p.exists():
            p2 = pathlib.Path.cwd() / "data" / name
            if p2.exists():
                p = p2
            else:
                return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"load {name} fail: {e}")
        return None

def get_metrix_total():
    """Laske Metrix total automaattisesti kaikista metrix_*.json tiedostoista"""
    metrix_files = list(DATA_DIR.glob("metrix_*.json"))
    # Suodata pois kilpailut ja tilanne
    metrix_files = [f for f in metrix_files if "kilpailut" not in f.name and "tilanne" not in f.name]
    
    total = 0
    breakdown = {}
    all_players = []
    
    for f in metrix_files:
        cid = f.stem.replace("metrix_", "")
        # Ohita parent 43119 (se on summa, ei yksittäinen rata)
        if cid == "43119":
            continue
        data = load_json(f.name)
        if not data:
            continue
        
        # Yritä eri kenttiä
        tr = data.get("total_results") or data.get("total_rounds") or data.get("total") or 0
        
        # Jos ei ole total_results, yritä breakdownista tai vanhasta
        if tr == 0:
            # Vanha fallback - 44010 on päärahta
            if cid == "44010":
                tr = 619  # päivitetty 19.10.2026 (oli 615)
            elif cid == "44763":
                tr = 130
            elif cid == "48112":
                tr = 19
            else:
                tr = 0
        
        if tr > 0:
            total += tr
            breakdown[cid] = tr
            for t in data.get("top10", []):
                name = t.get("name","")
                if name:
                    all_players.append(name)
    
    print(f"Metrix automaattinen: {breakdown} = {total} kierrosta")
    return total, breakdown, all_players

def main():
    print("=== kierrokset.py V6.3 AUTOMAATTINEN + YLIKIRJOITUSSUOJA ===")
    print(f"DATA_DIR={DATA_DIR}")
    
    # Lataa vanha suojattu versio
    old = load_json("kierrokset.json")
    if old:
        print(f"Vanha kierrokset.json: {old.get('total_rounds')} kierrosta (Metrix {old.get('metrix_total')} + UDisc {old.get('udisc_total')})")
        old_total = old.get("total_rounds", 0)
        old_metrix = old.get("metrix_total", 0)
        old_udisc = old.get("udisc_total", 0)
        old_unique = old.get("unique_players", 0)
        old_peliaika = old.get("peliaika", {}).get("hours", 0)
        old_askeleet = old.get("askeleet", {}).get("count", 0)
        old_km = old.get("kilometrit", {}).get("km", 0)
    else:
        print("Ei vanhaa kierrokset.json, käytetään minimiä")
        old_total = MIN_TOTAL
        old_metrix = MIN_METRIX
        old_udisc = MIN_UDISC
        old_unique = MIN_UNIQUE
        old_peliaika = MIN_PELIAIKA
        old_askeleet = MIN_ASKELEET
        old_km = MIN_KM
    
    # Laske Metrix automaattisesti
    total_rounds_metrix, breakdown, metrix_players = get_metrix_total()
    
    # Jos Metrix total 0 tai liian pieni, käytä vanhaa (suoja)
    if total_rounds_metrix == 0:
        print(f"⚠️ Metrix total 0, käytetään vanhaa {old_metrix} (suoja)")
        total_rounds_metrix = old_metrix
    elif total_rounds_metrix < old_metrix:
        print(f"⚠️ Metrix total {total_rounds_metrix} < vanha {old_metrix}, suojataan ylikirjoitukselta, käytetään vanhaa")
        total_rounds_metrix = old_metrix
        # Säilytä vanha breakdown jos uusi pienempi
        if old and old.get("metrix_breakdown"):
            breakdown = old.get("metrix_breakdown")
    
    # UDisc
    udisc_data = load_json("udisc.json")
    if udisc_data:
        udisc_total = udisc_data.get("total_rounds") or udisc_data.get("total") or 0
        if udisc_total <= 10:
            print(f"⚠️ UDisc total {udisc_total} liian pieni, käytetään vanhaa {old_udisc}")
            udisc_total = old_udisc
        elif udisc_total < old_udisc:
            print(f"⚠️ UDisc total {udisc_total} < vanha {old_udisc}, suojataan, käytetään vanhaa")
            udisc_total = old_udisc
    else:
        udisc_total = old_udisc
        print(f"UDisc ei löydy, käytetään vanhaa {udisc_total}")
    
    udisc_players = []
    if udisc_data:
        for t in udisc_data.get("top10", []):
            udisc_players.append(t.get("name",""))
    
    # Kokonaiskierrokset
    new_total = total_rounds_metrix + udisc_total
    
    # YLIKIRJOITUSSUOJA: ei koskaan alaspäin
    if new_total < old_total:
        print(f"⚠️ YLIKIRJOITUSSUOJA: uusi total {new_total} < vanha {old_total}, ESTETÄÄN, säilytetään {old_total}")
        new_total = old_total
        # Jos total suojattu, pidä myös metrix ja udisc vanhoina jos ne pieneni
        if total_rounds_metrix + udisc_total < old_total:
            total_rounds_metrix = old_metrix
            udisc_total = old_udisc
            new_total = old_total
    
    # Uniikit pelaajat
    all_names = [n.strip().lower() for n in metrix_players + udisc_players if n]
    unique_count = len(set(all_names)) if all_names else old_unique
    if unique_count < old_unique:
        print(f"⚠️ Unique {unique_count} < vanha {old_unique}, suojataan")
        unique_count = old_unique
    if unique_count < MIN_UNIQUE:
        unique_count = max(old_unique, MIN_UNIQUE)
    
    # Peliaika, askeleet, km - kasvaa kierrosten mukana, ei koskaan laske
    peliaika_h = int(new_total * REF_PELIAIKA / REF_TOTAL)
    askeleet = int(new_total * REF_ASKELEET / REF_TOTAL)
    km = int(new_total * REF_KM / REF_TOTAL)
    
    # Tarkempi laskenta jos mahdollista: Metrix 992h + UDisc tunneista
    if udisc_data:
        udisc_hours = udisc_data.get("peliaika", {}).get("hours") or udisc_data.get("virkistystunnit") or 630
        metrix_hours_est = int(total_rounds_metrix * 1.298)  # 992/764
        peliaika_h_precise = metrix_hours_est + udisc_hours
        if peliaika_h_precise > peliaika_h:
            peliaika_h = peliaika_h_precise
    
    # Suoja alaspäin
    if peliaika_h < old_peliaika:
        peliaika_h = old_peliaika
    if askeleet < old_askeleet:
        askeleet = old_askeleet
    if km < old_km:
        km = old_km
    
    # Varmista minimi
    peliaika_h = max(peliaika_h, MIN_PELIAIKA, old_peliaika)
    askeleet = max(askeleet, MIN_ASKELEET, old_askeleet)
    km = max(km, MIN_KM, old_km)
    new_total = max(new_total, MIN_TOTAL, old_total)
    
    print(f"\n✅ LOPPUTULOS (suojattu):")
    print(f"   Metrix: {total_rounds_metrix} (breakdown {breakdown})")
    print(f"   UDisc: {udisc_total}")
    print(f"   Yht: {new_total} kierrosta")
    print(f"   Uniikit: {unique_count}, Peliaika: {peliaika_h}h, Askeleet: {askeleet}, Km: {km}")
    
    # Rakenna data
    data = {
        "total_rounds": new_total,
        "total": new_total,
        "count": new_total,
        "metrix_total": total_rounds_metrix,
        "metrix_breakdown": breakdown,
        "udisc_total": udisc_total,
        "udisc_breakdown": {
            "virkistystunnit": udisc_data.get("virkistystunnit", 630) if udisc_data else 630,
            "askeleet": udisc_data.get("askeleet", {}).get("count", 1344654) if udisc_data else 1344654
        },
        "unique_players": unique_count,
        "peliaika": {"display": f"{peliaika_h}h", "hours": peliaika_h},
        "askeleet": {"display": f"{askeleet:,}".replace(",", " "), "count": askeleet},
        "kilometrit": {"display": f"{km} km", "km": km},
        "updated": datetime.now().strftime("%d.%m.%Y %H:%M - automaattinen + suoja"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": f"V6.3 AUTOMAATTINEN SUOJATTU - {new_total} kierrosta (Metrix {total_rounds_metrix} + UDisc {udisc_total})",
        "source": f"Metrix {total_rounds_metrix} + UDisc {udisc_total} = {new_total} - automaattinen, ylikirjoitus estetty",
        "locked": False,
        "protected": True,
        "min_values": {
            "total": MIN_TOTAL,
            "metrix": MIN_METRIX,
            "udisc": MIN_UDISC,
            "peliaika": MIN_PELIAIKA,
            "askeleet": MIN_ASKELEET,
            "km": MIN_KM,
            "unique": MIN_UNIQUE
        },
        "calculation": {
            "method": f"Automaattinen: Metrix summa {breakdown} = {total_rounds_metrix} + UDisc {udisc_total} = {new_total}, suoja min {MIN_TOTAL}",
            "total_rounds": new_total,
            "peliaika": f"{peliaika_h}h (suojattu min {MIN_PELIAIKA})",
            "askeleet": f"{askeleet} (suojattu min {MIN_ASKELEET})",
            "km": f"{km} km (suojattu min {MIN_KM})",
            "protection": f"Ei koskaan alaspäin: vanha {old_total} -> uusi {new_total}, min {MIN_TOTAL}"
        },
        "previous": {
            "total_rounds": old_total,
            "metrix_total": old_metrix,
            "udisc_total": old_udisc
        }
    }
    
    # Kirjoita vain jos muutos tai suojaus laukesi
    if new_total != old_total or total_rounds_metrix != old_metrix or udisc_total != old_udisc:
        print(f"\n💾 Muutos havaittu: {old_total} -> {new_total}, tallennetaan")
    else:
        print(f"\n💾 Ei muutosta, mutta varmistetaan suoja: {new_total}")
    
    (DATA_DIR / "kierrokset.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Tallennettu {DATA_DIR / 'kierrokset.json'}")

if __name__ == "__main__":
    main()
