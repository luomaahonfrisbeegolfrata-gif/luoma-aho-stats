#!/usr/bin/env python3
# build_stats.py - autenttinen SSA, total päivittyy kun UDisc kasvaa
import json, pathlib, sys

def load(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))

cfg_path = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "data") / "../config.json"
if not cfg_path.exists():
    cfg_path = pathlib.Path("config.json")
cfg = load(cfg_path)

data_dir = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "data")
data_dir.mkdir(parents=True, exist_ok=True)

# Lue UDisc ja Metrix round counts
udisc_path = data_dir / "udisc.json"
metrix_44010 = data_dir / "metrix_44010.json"
metrix_44763 = data_dir / "metrix_44763.json"

udisc_rounds = 453
metrix_rounds = 768

if udisc_path.exists():
    try:
        j = load(udisc_path)
        udisc_rounds = j.get("total_rounds") or j.get("rounds") or 453
        if isinstance(udisc_rounds, dict):
            udisc_rounds = 453
    except: pass

# Jos Metrix tiedostoissa on round count, käytä
# Placeholder: metrix pysyy 768 kunnes fetcher päivittää

total_rounds = metrix_rounds + udisc_rounds

# Päivitä kierrokset.json
kierrokset = {
    "total_rounds": total_rounds,
    "metrix_rounds": metrix_rounds,
    "udisc_rounds": udisc_rounds,
    "unique_players": cfg.get("unique_players_manual", 133),
    "peliaika": {"display": f"{int(total_rounds*1.335)}h", "hours": int(total_rounds*1.335)},
    "askeleet": {"display": f"{total_rounds*2664/1000000:.1f}M", "count": total_rounds*2664},
    "kilometrit": {"display": f"{total_rounds*2.054:.0f}km", "km": total_rounds*2.054},
    "calculation": f"{metrix_rounds} Metrix + {udisc_rounds} UDisc = {total_rounds} total - auto päivittyy kun UDisc kasvaa"
}

(data_dir / "kierrokset.json").write_text(json.dumps(kierrokset, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"kierrokset.json päivitetty: {metrix_rounds} + {udisc_rounds} = {total_rounds}")

# Päivitä vaylatilasto jos configissa uudet avg:t
# (tässä käytetään olemassa olevaa logiikkaa + autenttinen SSA)
# ... existing vaylatilasto build ...

# Lue olemassa olevat
v_path = data_dir / "vaylatilasto.json"
if v_path.exists():
    v = load(v_path)
    # päivitä laskenta teksti
    v["calculation"]["total_rounds"] = total_rounds
    v["calculation"]["metrix_rounds"] = metrix_rounds
    v["calculation"]["udisc_rounds"] = udisc_rounds
    v["calculation"]["formula"] = f"({metrix_rounds} Metrix + {udisc_rounds} UDisc) / {total_rounds}"
    # Autenttinen SSA
    PPS=15.15
    AVG_COMBINED=868.6
    offset = (AVG_COMBINED - 1000)/PPS
    ssa_total = sum([4.38,3.81,3.43,3.38,3.57,4.11,3.97,3.37,4.51,3.92,5.95,4.33]) + offset
    v["ssa_total_authentic"] = round(ssa_total,2)
    v_path.write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"vaylatilasto.json SSA {ssa_total:.2f}")
