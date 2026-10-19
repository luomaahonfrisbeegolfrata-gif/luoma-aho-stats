#!/usr/bin/env python3
"""build_stats.py V1.1 FIXED - Automaatioarkkitehtuuri V1.0 - polut vakaa + logit"""
import json
import pathlib
import sys
from datetime import datetime, timezone

print("=== build_stats.py V1.1 FIXED start ===")
HERE = pathlib.Path(__file__).resolve().parent
print(f"HERE={HERE} cwd={pathlib.Path.cwd()}")

# CONFIG etsi
def find_config():
    candidates = [
        HERE / "config.json",
        HERE.parent / "config.json",
        pathlib.Path.cwd() / "config.json",
        pathlib.Path.cwd() / "scripts" / "config.json",
        HERE.parent.parent / "config.json",
    ]
    print(f"Etsitään config.json: {candidates}")
    for c in candidates:
        if c.exists():
            print(f"Löytyi {c}")
            return c
    raise FileNotFoundError(f"config.json ei löydy, kokeiltu: {candidates}")

def find_data():
    if len(sys.argv) > 1:
        p = pathlib.Path(sys.argv[1])
        print(f"DATA arg: {p} exists={p.exists()}")
        return p
    candidates = [
        HERE.parent / "data",
        HERE / "data",
        pathlib.Path.cwd() / "data",
        pathlib.Path.cwd() / "AUTOMAATIO_V1.0" / "data",
        pathlib.Path.cwd() / "AUTOMAATIO_V1.1_FIXED" / "data",
    ]
    print(f"Etsitään data: {candidates}")
    for cand in candidates:
        if cand.exists():
            print(f"DATA löytyi {cand}")
            return cand
        # jos parent on olemassa, luo data
        if cand.parent.exists():
            cand.mkdir(parents=True, exist_ok=True)
            print(f"DATA luotu {cand}")
            return cand
    # fallback
    d = HERE.parent / "data"
    d.mkdir(parents=True, exist_ok=True)
    print(f"DATA fallback {d}")
    return d

try:
    CFG_PATH = find_config()
    DATA = find_data()
    print(f"CONFIG={CFG_PATH} DATA={DATA}")
    CFG = json.loads(CFG_PATH.read_text(encoding="utf-8"))
except Exception as e:
    print(f"CONFIG/DATA FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

VOLATILE = ("fetched_at", "updated")

def load(p, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"load {p} fail: {e}")
        return default

def strip(o):
    return {k: v for k, v in o.items() if k not in VOLATILE}

def write_if_changed(name, obj):
    p = DATA / name
    p.parent.mkdir(parents=True, exist_ok=True)
    old = load(p)
    if old is not None and strip(old) == strip(obj):
        print(f"  {name}: ei muutosta")
        return False
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
    print(f"  {name}: päivitetty -> {p}")
    return True

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
    h_lap, s_lap = u_hours / u_rounds, u_steps / u_rounds
    laps = sum(v["rounds"] * v["lap_equivalents"] for v in metrix.values())
    hours = round(u_hours + laps * h_lap)
    steps = round(u_steps + laps * s_lap)
    km = round(steps * CFG["metres_per_step"] / 1000)
    return {
        "total_rounds": total, "total": total, "count": total,
        "metrix_total": metrix_total, "udisc_total": u_rounds,
        "metrix_breakdown": metrix_rounds,
        "udisc_breakdown": {"rounds": u_rounds, "players": udisc.get("unique_players"), "hours": u_hours, "steps": u_steps, "measured": True},
        "unique_players": CFG["unique_players_manual"],
        "peliaika": {"display": f"{hours}h", "hours": hours},
        "askeleet": {"display": f"{steps:,}".replace(",", " "), "count": steps},
        "kilometrit": {"display": f"{km} km", "km": km},
        "estimated": {
            "unique_players": CFG["unique_players_note"],
            "metrix_hours_steps": f"Arvio: {laps:g} kierrosta x UDisc keskiarvo ({h_lap:.2f} h, {s_lap:.0f} askelta)",
            "km": f"askeleet x {CFG['metres_per_step']} m",
        },
        "as_of": CFG["as_of"],
        "updated": now_fi(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V1.1 FIXED",
        "locked": True,
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
        diff[idx] = rank
    dist = CFG["distribution"]
    hio = [CFG["hole_in_one"].get(str(i + 1), 0) for i in range(n)]
    rows = {"hio": hio, **dist}
    grand = sum(sum(r) for r in rows.values())
    out_rows = {}
    for k, r in rows.items():
        out_rows[k] = r + [sum(r), f"{sum(r) / grand * 100:.1f}%"]
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
        "as_of": CFG["as_of"],
        "updated": now_fi(),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "version": "V1.1 FIXED",
    }

def main():
    print(f"CONFIG={CFG_PATH} DATA={DATA}")
    udisc_path = DATA / "udisc.json"
    print(f"Etsitään udisc.json: {udisc_path} exists={udisc_path.exists()}")
    udisc = load(udisc_path)
    if not udisc:
        # etsi muualta
        for alt in [Path.cwd() / "data" / "udisc.json", HERE.parent / "data" / "udisc.json", Path.cwd() / "AUTOMAATIO_V1.0" / "data" / "udisc.json"]:
            print(f"Kokeillaan alt {alt} exists={alt.exists()}")
            udisc = load(alt)
            if udisc:
                print(f"Löytyi alt {alt}")
                break
    if not udisc:
        print("UDISC.JSON PUUTTUU - luodaan fallback 453")
        udisc = {
            "total_rounds": 453, "total": 453, "unique_players": 70,
            "peliaika": {"display": "630h", "hours": 630},
            "askeleet": {"display": "1 344 654", "count": 1344654}
        }
    write_if_changed("kierrokset.json", build_rounds(udisc))
    write_if_changed("vaylatilasto.json", build_holes())
    print("=== build_stats.py V1.1 FIXED DONE ===")

if __name__ == "__main__":
    main()
