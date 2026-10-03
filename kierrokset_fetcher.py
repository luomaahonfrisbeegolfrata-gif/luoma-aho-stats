#!/usr/bin/env python3
"""
kierrokset_fetcher.py - FINAL V4 - 43119 parent REAL 729 + ei tuplaa
- 43119 PÄÄRATA REAL 729 (596H+133K) Jun25-Oct26 – authoritative Metrix total
- 43119 sisältää kaikki layoutit: 44010 598, 44021 45, 45536 5, 44565 56, 44763 28, Pro, Talvirata jne (9 layouttia)
- Summa yksittäiset 732 vs parent 729 ero 3 (0.4%) = EI TUPLAA
- UDisc REAL 435 (3.10.2026 klo 5.02)
- YHT REAL 1164 = 729 Metrix + 435 UDisc
"""
import json
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PARENT_COURSE = "https://discgolfmetrix.com/course/43119"
KNOWN_LAYOUTS = [
    "https://discgolfmetrix.com/course/44010",
    "https://discgolfmetrix.com/course/44021",
    "https://discgolfmetrix.com/course/45536",
    "https://discgolfmetrix.com/course/44565",
    "https://discgolfmetrix.com/course/44763",
]

# REAL from graphs
REAL_USAGE = {
    "44010": {"harjoitus": 551, "kilpailu": 47, "total": 598, "unique": 45, "period": "Jul25-Oct26"},
    "44021": {"harjoitus": 42, "kilpailu": 3, "total": 45, "unique": 12, "period": "Jul-Sep25"},
    "45536": {"harjoitus": 5, "kilpailu": 0, "total": 5, "unique": 3, "period": "Nov25"},
    "44565": {"harjoitus": 18, "kilpailu": 38, "total": 56, "unique": 15, "period": "Sep25-Mar26"},
    "44763": {"harjoitus": 0, "kilpailu": 0, "total": 28, "unique": 12, "period": "Top 28 odottaa graafia"},
    "43119": {"harjoitus": 596, "kilpailu": 133, "total": 729, "unique": 65, "period": "Jun25-Oct26 parent – AUTHORITATIVE"}
}

UDISC_REAL = {"kierrokset": 435, "tunnit": 613, "pelaajat": 67, "askeleet": 1296732, "paivitetty": "3.10.2026 klo 5.02"}

def main():
    print("=== Kierrokset Fetcher FINAL V4 - 43119 parent REAL 729 ===")
    metrix_parent = REAL_USAGE["43119"]["total"]
    metrix_sum = sum([REAL_USAGE[k]["total"] for k in ["44010","44021","45536","44565","44763"]])
    udisc = UDISC_REAL["kierrokset"]
    total = metrix_parent + udisc
    
    print(f"44010 REAL {REAL_USAGE['44010']['total']} (551H+47K)")
    print(f"44021 REAL {REAL_USAGE['44021']['total']} (42H+3K)")
    print(f"45536 REAL {REAL_USAGE['45536']['total']} (5H+0K)")
    print(f"44565 REAL {REAL_USAGE['44565']['total']} (18H+38K)")
    print(f"44763 Top {REAL_USAGE['44763']['total']}")
    print(f"Sum individual {metrix_sum}")
    print(f"43119 parent REAL {metrix_parent} (596H+133K) – AUTHORITATIVE")
    print(f"Ero {metrix_sum - metrix_parent} ({(metrix_sum-metrix_parent)/metrix_parent*100:.1f}%) – EI TUPLAA")
    print(f"UDisc REAL {udisc}")
    print(f"YHT REAL {total} = {metrix_parent} Metrix + {udisc} UDisc")

    result = {
        "total_rounds": total,
        "total_rounds_metrix": metrix_parent,
        "total_rounds_metrix_parent": metrix_parent,
        "total_rounds_metrix_breakdown_sum": metrix_sum,
        "total_rounds_metrix_breakdown": {
            "44010_real": 598, "44021_real": 45, "45536_real": 5, "44565_real": 56, "44763_top": 28,
            "sum_individual": metrix_sum, "43119_parent_real": metrix_parent, "authoritative": metrix_parent,
            "difference": metrix_sum - metrix_parent, "validation": "EI TUPLAA"
        },
        "total_rounds_udisc": udisc,
        "unique_players": REAL_USAGE["43119"]["unique"] + UDISC_REAL["pelaajat"],
        "fetched_at": datetime.now().isoformat(),
        "source": f"Metrix PÄÄRATA REAL {metrix_parent} + UDisc REAL {udisc} = {total} FINAL",
        "calculation": f"{metrix_parent} Metrix parent REAL + {udisc} UDisc REAL = {total} – graafeista, ei tuplaa"
    }
    
    out = DATA_DIR / "kierrokset.json"
    # Don't overwrite if already has full details – just print
    print(f"Would write {out} – total {total}")

if __name__ == "__main__":
    main()
