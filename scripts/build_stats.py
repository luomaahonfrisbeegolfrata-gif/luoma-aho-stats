#!/usr/bin/env python3
"""build_stats.py - rakentaa data/kierrokset.json ja data/vaylatilasto.json tiedostosta scripts/config.json
(+ UDisc-luvut data/udisc.json:sta).

Korvaa: kierrokset.py, vaylatilasto_updater.py, udisc_image_parser.py (laskentaosa).
- ei kovakoodattuja REF-lukuja, ei 'locked'-ylikirjoituksia
- arviot merkitään (estimated), mitattu data erikseen
- kirjoittaa tiedoston vain jos sisältö muuttui (ei turhia committeja)

Käyttö: python scripts/build_stats.py [data-kansio]
"""
import json
import pathlib
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
DATA = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data"
CFG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
VOLATILE = ("fetched_at", "updated")


def load(p, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def strip(o):
    return {k: v for k, v in o.items() if k not in VOLATILE}


def write_if_changed(name, obj):
    p = DATA / name
    old = load(p)
    if old is not None and strip(old) == strip(obj):
        print(f"  {name}: ei muutosta")
        return
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
    print(f"  {name}: päivitetty")


def now_fi():
    return datetime.now().strftime("%d.%m.%Y %H:%M")


def build_rounds(udisc):
    metrix = {k.split("_", 1)[1]: v for k, v in CFG["layouts"].items() if k.startswith("metrix_")}
    metrix_rounds = {cid: v["rounds"] for cid, v in metrix.items()}
    metrix_total = sum(metrix_rounds.values())
    u_rounds = int(udisc["total_rounds"])
    u_hours = float(udisc["peliaika"]["hours"])
    u_steps = int(udisc["askeleet"]["count"])
    total = metrix_total + u_rounds

    # Metrix ei mittaa aikaa/askelia -> arvio UDiscin mitatusta keskiarvosta per 12 väylän kierros
    h_lap, s_lap = u_hours / u_rounds, u_steps / u_rounds
    laps = sum(v["rounds"] * v["lap_equivalents"] for v in metrix.values())
    hours = round(u_hours + laps * h_lap)
    steps = round(u_steps + laps * s_lap)
    km = round(steps * CFG["metres_per_step"] / 1000)
    return {
        "total_rounds": total, "total": total, "count": total,
        "metrix_total": metrix_total, "udisc_total": u_rounds,
        "metrix_breakdown": metrix_rounds,
        "udisc_breakdown": {"rounds": u_rounds, "players": udisc.get("unique_players"),
                            "hours": u_hours, "steps": u_steps, "measured": True},
        "unique_players": CFG["unique_players_manual"],
        "peliaika": {"display": f"{hours}h", "hours": hours},
        "askeleet": {"display": f"{steps:,}".replace(",", " "), "count": steps},
        "kilometrit": {"display": f"{km} km", "km": km},
        "estimated": {
            "unique_players": CFG["unique_players_note"],
            "metrix_hours_steps": f"Arvio: Metrix-kierrokset ({laps:g} 12-väyläkierrosta) x UDiscin keskiarvo "
                                  f"({h_lap:.2f} h, {s_lap:.0f} askelta/kierros)",
            "km": f"askeleet x {CFG['metres_per_step']} m",
        },
        "double_counting_warning": "Samat kierrokset voivat olla sekä Metrixissä että UDiscissä; kokonaismäärä on yläraja.",
        "as_of": CFG["as_of"],
        "updated": now_fi(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V6.3 config-pohjainen",
    }


def cls_avg(avg, par):
    d = avg - par
    return "cell-red" if d >= 1.0 else "cell-orange" if d >= 0.5 else "cell-yellow" if d >= 0.2 else "cell-green"


def cls_diff(n):
    return "cell-green" if n <= 3 else "cell-yellow" if n <= 6 else "cell-orange" if n <= 9 else "cell-red"


def build_holes():
    par = CFG["course"]["par"]
    length = CFG["course"]["length_m"]
    n = len(par)
    srcs = []
    for key, v in CFG["layouts"].items():
        w = v["hole_plays"] if "hole_plays" in v else [v["rounds"] * v["hole_plays_per_round"]] * n
        srcs.append((v["avg"], w))
    avg = []
    for i in range(n):
        tw = sum(w[i] for _, w in srcs)
        avg.append(sum(a[i] * w[i] for a, w in srcs) / tw)
    over = [avg[i] - par[i] for i in range(n)]
    order = sorted(range(n), key=lambda i: (over[i], i))
    diff = [0] * n
    for rank, idx in enumerate(order, 1):
        diff[idx] = rank  # 1 = helpoin, 12 = vaikein

    dist = CFG["distribution"]
    hio = [CFG["hole_in_one"].get(str(i + 1), 0) for i in range(n)]
    rows = {"hio": hio, **dist}
    grand = sum(sum(r) for r in rows.values())
    out_rows = {}
    for k, r in rows.items():
        out_rows[k] = r + [sum(r), f"{sum(r) / grand * 100:.1f}%"]

    warnings = []
    per_hole = [sum(r[i] for r in rows.values()) for i in range(n)]
    if max(per_hole) - min(per_hole) > 0.02 * max(per_hole):
        warnings.append(f"Jakauman väyläsummat poikkeavat toisistaan: {per_hole}")

    return {
        "vayla_count": n,
        "par_total": str(sum(par)), "pituus_total": f"{sum(length)}m",
        "avg_total": f"{sum(avg):.2f}", "avg_total_calc": round(sum(avg), 2),
        "over_par_total": f"{sum(over):.2f}", "difficulty_total": str(sum(diff)),
        "pituus": [f"{x}m" for x in length] + [f"{sum(length)}m", "-"],
        "par": [str(p) for p in par] + [str(sum(par)), "-"],
        "avg": [f"{a:.2f}" for a in avg] + [f"{sum(avg):.2f}", "-"],
        "avgCls": [cls_avg(avg[i], par[i]) for i in range(n)] + ["cell-dark"] * 2,
        "difficulty": [str(d) for d in diff] + [str(sum(diff)), "-"],
        "diffCls": [cls_diff(d) for d in diff] + ["cell-dark"] * 2,
        **out_rows,
        "avg_method": "Painotettu keskiarvo: Metrix-kierrokset x väylän pelikerrat; UDisc painotetaan vain 31-34 pelikerralla",
        "difficulty_note": "1 = helpoin, 12 = vaikein (keskiarvo - par)",
        "distribution_verified": CFG["distribution_verified"],
        "distribution_note": CFG["distribution_note"],
        "warnings": warnings,
        "as_of": CFG["as_of"],
        "updated": now_fi(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V6.3 config-pohjainen",
    }


def main():
    print("=== build_stats.py ===")
    udisc = load(DATA / "udisc.json")
    if not udisc:
        sys.exit("data/udisc.json puuttuu tai on rikki")
    write_if_changed("kierrokset.json", build_rounds(udisc))
    holes = build_holes()
    for w in holes["warnings"]:
        print("  VAROITUS:", w)
    write_if_changed("vaylatilasto.json", holes)


if __name__ == "__main__":
    main()
