#!/usr/bin/env python3
"""build_stats.py V2.0 - laskee data/kierrokset.json ja data/vaylatilasto.json config.json:sta.

Kaava (sama kuin julkaistu V4.0 REAL):
  väyläkeskiarvo = (Metrix_avg * metrix_kierrokset + UDisc_avg * udisc_kierrokset) / yhteensä
Tarkistukset: väyläkohtainen jakaumasumma = kierrosten kokonaismäärä, muuten ajo kaatuu
(vanha data jää voimaan, eikä virheellistä lukua julkaista).

Käyttö: python scripts/build_stats.py [data-kansio]
"""
import json
import pathlib
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent


def first(paths):
    for p in paths:
        if p.exists():
            return p
    sys.exit(f"config.json ei löydy: {[str(p) for p in paths]}")


CFG_PATH = first([HERE / "config.json", HERE.parent / "config.json", pathlib.Path.cwd() / "config.json"])
CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
DATA = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE.parent / "data" if HERE.name == "scripts" else HERE / "data")
DATA.mkdir(parents=True, exist_ok=True)
VOLATILE = ("fetched_at", "updated")


def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def write_if_changed(name, obj):
    p = DATA / name
    strip = lambda o: {k: v for k, v in o.items() if k not in VOLATILE}
    old = load(p)
    if old is not None and strip(old) == strip(obj):
        print(f"  {name}: ei muutosta")
        return
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
    print(f"  {name}: päivitetty")


def now_fi():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Europe/Helsinki")).strftime("%d.%m.%Y %H:%M")
    except Exception:
        return datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")


def stamp():
    return {"updated": now_fi(), "fetched_at": datetime.now(timezone.utc).isoformat()}


def metrix_layouts():
    return {k.split("_", 1)[1]: v for k, v in CFG["layouts"].items() if k.startswith("metrix_")}


def build_rounds(udisc):
    metrix = metrix_layouts()
    m_rounds = {cid: v["rounds"] for cid, v in metrix.items()}
    m_total, u_rounds = sum(m_rounds.values()), int(udisc["total_rounds"])
    total = m_total + u_rounds
    u_hours, u_steps = float(udisc["peliaika"]["hours"]), int(udisc["askeleet"]["count"])
    mps = CFG["metres_per_step"]
    # Laskettu arvio: Metrix-kierrokset (24 väylää = 2 kierrosta jne.) x UDiscin keskiarvo / kierros
    laps = sum(v["rounds"] * v["lap_equivalents"] for v in metrix.values())
    calc_h = round(u_hours + laps * u_hours / u_rounds)
    calc_s = round(u_steps + laps * u_steps / u_rounds)
    man = CFG.get("manual_totals")  # käsin lukittu arvo ohittaa laskennan, jos annettu
    hours, steps = (man["peliaika_h"], man["askeleet"]) if man else (calc_h, calc_s)
    km = round(steps * mps / 1000)
    return {
        "total_rounds": total, "total": total, "count": total,
        "metrix_total": m_total, "udisc_total": u_rounds, "metrix_breakdown": m_rounds,
        "udisc_breakdown": {"rounds": u_rounds, "players": udisc.get("unique_players"), "hours": u_hours, "steps": u_steps},
        "unique_players": CFG["unique_players_manual"],
        "peliaika": {"display": f"{hours}h", "hours": hours},
        "askeleet": {"display": f"{steps:,}".replace(",", " "), "count": steps},
        "kilometrit": {"display": f"{km} km", "km": km},
        "estimated": {
            "unique_players": CFG["unique_players_note"],
            "hours_steps": "käsin lukittu (config.manual_totals)" if man else f"laskettu: {laps:g} kierrosta x UDisc-keskiarvo",
            "calculated_alternative": {"hours": calc_h, "steps": calc_s, "km": round(calc_s * mps / 1000)},
            "km": f"askeleet x {mps} m",
        },
        "as_of": CFG["as_of"], "version": "V2.0", **stamp(),
    }


def build_holes(total):
    par, length = CFG["course"]["par"], CFG["course"]["length_m"]
    n = len(par)
    m_avg, u_avg = CFG["metrix_avg_per_hole"], CFG["udisc_real_avg_per_hole"]
    wm = sum(v["rounds"] for v in metrix_layouts().values())
    wu = CFG["layouts"]["udisc"]["rounds"]
    assert wm + wu == total, f"kierrosmäärät eivät täsmää: {wm}+{wu} != {total}"
    avg = [(m_avg[i] * wm + u_avg[i] * wu) / total for i in range(n)]
    over = [avg[i] - par[i] for i in range(n)]
    diff = [0] * n
    for rank, idx in enumerate(sorted(range(n), key=lambda i: (over[i], i)), 1):
        diff[idx] = rank  # 1 = helpoin
    dist = {k: list(v) for k, v in CFG["distribution"].items()}
    est = CFG.get("birdie_estimated_holes", [])
    for h in est:  # birdie = UDiscin birdie-% x kierrokset; erotus par0:sta, jotta väyläsumma pysyy
        i = h - 1
        b = round(total * CFG["udisc_real_distribution_perc"][str(h)]["birdie"] / 100)
        dist["par0"][i] -= b - dist["birdie"][i]
        dist["birdie"][i] = b
    est_info = {"estimated": {"birdie_holes": est, "note": f"Birdie-luvut väylillä {', '.join(map(str, est))} on arvioitu UDiscin jakaumasta (sama osuus kaikille kierroksille)."}} if est else {}
    rows = {"hio": [CFG["hole_in_one"].get(str(i + 1), 0) for i in range(n)], **dist}
    sums = [sum(r[i] for r in rows.values()) for i in range(n)]
    if sums != [total] * n:
        sys.exit(f"VIRHE: jakaumasummat {sums} != {total} - vaylatilasto.json jätetään ennalleen")
    grand = sum(sums)
    out = {k: r + [sum(r), f"{sum(r) / grand * 100:.1f}%"] for k, r in rows.items()}
    cls_avg = lambda o: "cell-red" if o >= 1 else "cell-orange" if o >= .5 else "cell-yellow" if o >= .2 else "cell-green"
    cls_diff = lambda d: "cell-green" if d <= 3 else "cell-yellow" if d <= 6 else "cell-orange" if d <= 9 else "cell-red"
    return {
        "vayla_count": n, "par_total": str(sum(par)), "pituus_total": f"{sum(length)}m",
        "avg_total": f"{sum(avg):.2f}", "avg_total_calc": round(sum(avg), 2), "over_par_total": f"{sum(over):.2f}",
        "pituus": [f"{x}m" for x in length] + [f"{sum(length)}m", "-"],
        "par": [str(p) for p in par] + [str(sum(par)), "-"],
        "avg": [f"{a:.2f}" for a in avg] + [f"{sum(avg):.2f}", "-"],
        "avgCls": [cls_avg(o) for o in over] + ["cell-dark"] * 2,
        "difficulty": [str(d) for d in diff] + ["-", "-"],
        "diffCls": [cls_diff(d) for d in diff] + ["cell-dark"] * 2,
        **out,
        **est_info,
        "calculation": {
            "formula": "(Metrix_avg * metrix_rounds + UDisc_avg * udisc_rounds) / total_rounds",
            "metrix_rounds": wm, "udisc_rounds": wu, "total_rounds": total,
            "metrix_avg_total": round(sum(m_avg), 2), "udisc_avg_total": round(sum(u_avg), 2),
        },
        "as_of": CFG["as_of"], "version": "V2.0", **stamp(),
    }


def main():
    udisc = load(DATA / "udisc.json")
    if not udisc:
        sys.exit(f"{DATA / 'udisc.json'} puuttuu tai on rikki - ei kirjoiteta mitään")
    rounds = build_rounds(udisc)
    holes = build_holes(rounds["total_rounds"])  # kaatuu ennen kirjoitusta, jos data ei täsmää
    write_if_changed("kierrokset.json", rounds)
    write_if_changed("vaylatilasto.json", holes)
    print("build_stats OK")


if __name__ == "__main__":
    main()
