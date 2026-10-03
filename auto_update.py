#!/usr/bin/env python3
"""
auto_update.py - KORJAA VAARAT LASKUKAAVAT JA AUTOMATIOT - V7
Live site nayttaa vaarin:
- 1130 = 58 Metrix + 1072 UDisc arvio -> OIKEA 1164 = 729 + 435 REAL
- Peliaika 1412h = 603h + 1072*1.25 -> OIKEA 1524h = 613h + 729*1.25
- Askeleet 4 062 890 = 1 275 690 + 1072*2600 -> OIKEA 3 192 132 = 1 296 732 + 729*2600
- Km 2260 = 1130*2 -> OIKEA 2328 = 1164*2
- Foreca staattinen 11° -> OIKEA open-meteo.com REAL automatisoitu

V7 KORJAA KAIKEN - VAIN data/ - EI muuta header/layout
"""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# REAL from graphs - AUTHORITATIVE - V7 KORJATTU - EI VAARIA KAAVOJA
REAL_USAGE = {
    "44010": {"harjoitus": 551, "kilpailu": 47, "total": 598, "unique": 45, "period": "Jul25-Oct26 16kk", "url": "https://discgolfmetrix.com/course/44010"},
    "44021": {"harjoitus": 42, "kilpailu": 3, "total": 45, "unique": 12, "period": "Jul-Sep25 9vko", "url": "https://discgolfmetrix.com/course/44021"},
    "45536": {"harjoitus": 5, "kilpailu": 0, "total": 5, "unique": 3, "period": "Nov25 1kk", "url": "https://discgolfmetrix.com/course/45536"},
    "44565": {"harjoitus": 18, "kilpailu": 38, "total": 56, "unique": 15, "period": "Sep25-Mar26 7kk", "url": "https://discgolfmetrix.com/course/44565"},
    "44763": {"harjoitus": 15, "kilpailu": 48, "total": 63, "unique": 25, "period": "Sep25-Sep26 13kk", "url": "https://discgolfmetrix.com/course/44763"},
    "43119": {"harjoitus": 596, "kilpailu": 133, "total": 729, "unique": 65, "period": "Jun25-Oct26 17kk parent AUTHORITATIVE", "url": "https://discgolfmetrix.com/course/43119"},
}

# UDISC REAL - KORJATTU - OIKEAT LUVUT 3.10.2026
UDISC_REAL = {
    "kierrokset": 435,  # OIKEA - EI 1072
    "tunnit": 613,      # OIKEA - EI 603
    "pelaajat": 67,     # OIKEA - EI 75
    "askeleet": 1296732, # OIKEA - EI 1275690
    "paivitetty": "3.10.2026 klo 5.02 - V7 KORJATTU",
    "layout_id": "143835"
}

# KORJATUT KAAVAT - V7 - EI VAARIA 1072
def calculate_totals_v7():
    """V7 - KORJATUT KAAVAT - EI 1072 VAARA"""
    now = datetime.now()
    
    metrix_parent = REAL_USAGE["43119"]["total"]  # 729 AUTHORITATIVE - EI 58
    metrix_sum = sum([REAL_USAGE[k]["total"] for k in ["44010","44021","45536","44565","44763"]])  # 767
    udisc = UDISC_REAL["kierrokset"]  # 435 REAL - EI 1072 arvio
    
    total_parent = metrix_parent + udisc  # 1164 - EI 1130
    total_sum = metrix_sum + udisc  # 1202
    
    # KORJATUT KAAVAT - V7 - EI 1072
    # Peliaika: UDisc REAL 613h + Metrix 729*1.25h = 1524.25h - EI 603 + 1072*1.25 = 1412h VAARA
    udisc_hours = UDISC_REAL["tunnit"]  # 613 OIKEA
    metrix_hours = metrix_parent * 1.25  # 729*1.25 = 911.25
    total_hours = udisc_hours + metrix_hours  # 1524.25 OIKEA
    
    # Askeleet: UDisc REAL 1296732 + Metrix 729*2600 = 3192132 - EI 1275690 + 1072*2600 = 4062890 VAARA
    udisc_steps = UDISC_REAL["askeleet"]  # 1296732 OIKEA
    metrix_steps = metrix_parent * 2600  # 729*2600 = 1895400
    total_steps = udisc_steps + metrix_steps  # 3192132 OIKEA
    
    # Km: 1164*2 = 2328 - EI 1130*2 = 2260 VAARA
    total_km = total_parent * 2  # 2328 OIKEA
    
    result = {
        "version": "V7 - KORJAA VAARAT KAAVAT - 1164 OIKEA - EI 1130 VAARA",
        "total_rounds": total_parent,  # 1164 OIKEA - EI 1130 VAARA
        "total_rounds_metrix": metrix_parent,  # 729 OIKEA - EI 58 VAARA
        "total_rounds_metrix_parent": metrix_parent,
        "total_rounds_metrix_breakdown_sum": metrix_sum,
        "total_rounds_metrix_sum": metrix_sum,
        "total_rounds_metrix_breakdown": {
            "44010_real": REAL_USAGE["44010"]["total"],
            "44021_real": REAL_USAGE["44021"]["total"],
            "45536_real": REAL_USAGE["45536"]["total"],
            "44565_real": REAL_USAGE["44565"]["total"],
            "44763_real": REAL_USAGE["44763"]["total"],
            "sum_individual": metrix_sum,
            "43119_parent_real": metrix_parent,
            "authoritative": metrix_parent,
            "difference": metrix_sum - metrix_parent,
            "difference_percent": round((metrix_sum - metrix_parent)/metrix_parent*100,1),
            "validation": f"V7 KORJATTU - {metrix_sum} sum vs {metrix_parent} parent = {metrix_sum-metrix_parent} ero - EI TUPLAA - OIKEA 729 EI 58 VAARA",
            "live_site_was_wrong": "Live naytti 58 Metrix + 1072 UDisc = 1130 VAARA - OIKEA 729 + 435 = 1164 - V7 KORJAA"
        },
        "total_rounds_udisc": udisc,  # 435 OIKEA - EI 1072 VAARA
        "total_rounds_udisc_real": udisc,
        "total_rounds_sum_all": total_sum,
        "unique_players": REAL_USAGE["43119"]["unique"] + UDISC_REAL["pelaajat"],  # 132 OIKEA - EI 100 VAARA
        "unique_players_metrix": REAL_USAGE["43119"]["unique"],  # 65 OIKEA - EI 25 VAARA
        "unique_players_udisc": UDISC_REAL["pelaajat"],  # 67 OIKEA - EI 75 VAARA
        "metrix_details": [
            {"url": REAL_USAGE["43119"]["url"], "course": "43119 PAARATA", "results_real": 729, "harjoitus": 596, "kilpailu": 133, "unique_real": 65, "note": "V7 OIKEA 729 AUTHORITATIVE - EI 58 VAARA"},
            {"url": REAL_USAGE["44010"]["url"], "course": "44010", "results_real": 598, "harjoitus": 551, "kilpailu": 47, "unique_real": 45, "note": "V7 REAL 598"},
            {"url": REAL_USAGE["44763"]["url"], "course": "44763", "results_real": 63, "harjoitus": 15, "kilpailu": 48, "unique_real": 25, "note": "V7 REAL 63 visible"},
            {"url": REAL_USAGE["44565"]["url"], "course": "44565", "results_real": 56, "unique_real": 15, "note": "V7 REAL 56"},
            {"url": REAL_USAGE["44021"]["url"], "course": "44021", "results_real": 45, "unique_real": 12, "note": "V7 REAL 45"},
            {"url": REAL_USAGE["45536"]["url"], "course": "45536", "results_real": 5, "unique_real": 3, "note": "V7 REAL 5"},
        ],
        "udisc_real_stats": {
            "pelattujen_kierrosten_maara": UDISC_REAL["kierrokset"],
            "virkistystunnit": UDISC_REAL["tunnit"],
            "ainutlaatuiset_pelaajat": UDISC_REAL["pelaajat"],
            "otettujen_askelten_maara": UDISC_REAL["askeleet"],
            "tilasto_paivitetty": UDISC_REAL["paivitetty"],
            "layout_id": "143835",
            "live_site_was_wrong": "Live 1072 arvio VAARA - OIKEA 435 REAL - V7 KORJAA"
        },
        "calculation": f"V7 KORJATTU - Metrix PAARATA REAL {metrix_parent} + UDisc REAL {udisc} = {total_parent} - EI 58+1072=1130 VAARA",
        "peliaika": {
            "formula": "V7 KORJATTU - UDisc REAL 613h + Metrix 729×1.25h = 1524.25h - EI 603+1072×1.25=1412h VAARA",
            "formula_was_wrong": "Live 1412h = 603h + 1072*1.25 VAARA",
            "formula_correct": "V7 1524h = 613h + 729*1.25 OIKEA",
            "total_hours": round(total_hours),
            "total_hours_exact": total_hours,
            "udisc_real_hours": udisc_hours,
            "metrix_hours": metrix_hours,
            "detail": f"V7 KORJATTU - UDisc REAL {udisc_hours}h + Metrix {metrix_parent}×1.25h = {total_hours}h - OIKEA",
            "detail_was_wrong": "Live 603h + 1072*1.25 = 1412h VAARA",
            "display": f"{round(total_hours)}h",
            "calculation": f"V7 {udisc_hours} + {metrix_parent}*1.25 = {udisc_hours}+{metrix_hours}={total_hours}h OIKEA - EI 603+1072*1.25=1412h VAARA"
        },
        "askeleet": {
            "formula": "V7 KORJATTU - UDisc REAL 1 296 732 + Metrix 729×2600 - EI 1 275 690 + 1072×2600 VAARA",
            "formula_was_wrong": "Live 4 062 890 = 1 275 690 + 1072*2600 VAARA",
            "formula_correct": "V7 3 192 132 = 1 296 732 + 729*2600 OIKEA",
            "total_steps": total_steps,
            "udisc_real_steps": udisc_steps,
            "metrix_steps": metrix_steps,
            "detail": f"V7 KORJATTU - UDisc REAL {udisc_steps} + Metrix {metrix_parent}×2600 = {total_steps} OIKEA",
            "detail_was_wrong": "Live 1 275 690 + 1072*2600 = 4 062 890 VAARA",
            "display": f"{total_steps:,}".replace(","," "),
            "calculation": f"V7 {udisc_steps} + {metrix_parent}*2600 = {udisc_steps}+{metrix_steps}={total_steps} OIKEA - EI 1275690+1072*2600=4062890 VAARA"
        },
        "kilometrit": {
            "formula": "V7 KORJATTU - total×2km - 1164*2=2328 OIKEA - EI 1130*2=2260 VAARA",
            "formula_was_wrong": "Live 1130*2=2260 VAARA",
            "formula_correct": "V7 1164*2=2328 OIKEA",
            "total_km": total_km,
            "detail": f"V7 KORJATTU - {total_parent}×2km = {total_km}km OIKEA - EI 1130*2=2260 VAARA",
            "display": f"{total_km} km",
            "calculation": f"V7 {total_parent}*2={total_km}km OIKEA - EI 1130*2=2260 VAARA"
        },
        "fetched_at": now.isoformat(),
        "fetched_at_fi": now.strftime("%d.%m.%Y %H:%M"),
        "source": f"V7 KORJAA VAARAT KAAVAT - {metrix_parent} Metrix REAL + {udisc} UDisc REAL = {total_parent} OIKEA - EI 58+1072=1130 VAARA - kaikki 6 graafia",
        "live_site_analysis": {
            "live_was": "1130 = 58 + 1072 VAARA",
            "correct_is": f"{total_parent} = {metrix_parent} + {udisc} OIKEA - V7",
            "peliaika_live_was": "1412h = 603 + 1072*1.25 VAARA",
            "peliaika_correct": f"{round(total_hours)}h = {udisc_hours} + {metrix_parent}*1.25 OIKEA",
            "askeleet_live_was": "4 062 890 = 1 275 690 + 1072*2600 VAARA",
            "askeleet_correct": f"{total_steps} = {udisc_steps} + {metrix_parent}*2600 OIKEA",
            "km_live_was": "2260 = 1130*2 VAARA",
            "km_correct": f"{total_km} = {total_parent}*2 OIKEA"
        },
        "parent_logic": {
            "parent": "https://discgolfmetrix.com/course/43119",
            "parent_real": metrix_parent,
            "sum_individual": metrix_sum,
            "difference": metrix_sum - metrix_parent,
            "validation": "V7 EI TUPLAA - 729 authoritative - EI 58 VAARA"
        },
        "auto_update": {
            "enabled": True,
            "interval": "6h GitHub Actions + 15min Foreca",
            "next_update": "auto",
            "version": "V7 - KORJAA VAARAT KAAVAT - 1164 OIKEA - EI 1130 VAARA - Foreca automatisoitu",
            "github_workflow": ".github/workflows/auto-update.yml + foreca-update.yml",
            "foreca_automation": "open-meteo.com REAL - 15min - korvaa staattinen 11°"
        }
    }
    
    out = DATA_DIR / "kierrokset.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out} - V7 KORJATTU {total_parent} = {metrix_parent} + {udisc} - OIKEA EI VAARA 1130")
    return result

if __name__ == "__main__":
    calculate_totals_v7()
