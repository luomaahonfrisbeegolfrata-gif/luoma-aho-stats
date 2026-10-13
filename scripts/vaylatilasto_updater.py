#!/usr/bin/env python3
"""
vaylatilasto_updater.py - V5.3 - Päivitä väylätilasto kuvista (1000+ kierrosta)

Käyttö:
python vaylatilasto_updater.py --metrix-44010 kuva_46b79d.png --metrix-44763 kuva_47fa0d.png --udisc-1-6 kuva_8eb319.png --udisc-7-12 kuva_2407fe.png

Tai interaktiivinen:
python vaylatilasto_updater.py
"""

import json, pathlib, argparse
from datetime import datetime

def parse_args():
    p = argparse.ArgumentParser(description="Väylätilasto updater V5.3 - 1000+ kierrosta")
    p.add_argument('--metrix-44010', help='Metrix 44010 chart kuva')
    p.add_argument('--metrix-44763', help='Metrix 44763 24 väylää kuva')
    p.add_argument('--metrix-48112', help='Metrix 48112 18 väylää kuva')
    p.add_argument('--udisc-1-6', help='UDisc 1-6 kuva')
    p.add_argument('--udisc-7-12', help='UDisc 7-12 kuva')
    return p.parse_args()

# Lukitut avg:t kuvista (OCR manuaalisesti varmistettu)
DEFAULTS = {
    "44010": {"avg": [4.7, 3.8, 3.7, 3.4, 3.6, 4.3, 4.2, 3.6, 5.2, 4.3, 6.6, 4.4], "rounds": 615},
    "44763": {"avg": [4.3, 4.05, 3.6, 3.4, 3.6, 3.85, 3.95, 3.35, 3.8, 4.25, 4.3, 6.1], "rounds": 130},
    "48112": {"avg": [4.5, 3.35, 3.3, 3.35, 3.35, 4.55, 4.6, 3.3, 3.6, 3.4, 5.6, 3.6], "rounds": 19},
    "udisc": {"avg": [4.26, 3.77, 3.25, 3.31, 3.5, 3.95, 3.84, 3.25, 4.17, 3.67, 5.79, 4.05], "rounds": 444},
}

def weighted_avg(lists_with_rounds):
    total_rounds = sum(r for _, r in lists_with_rounds)
    combined = []
    for i in range(12):
        weighted = sum(avg[i] * rnd for avg, rnd in lists_with_rounds) / total_rounds
        combined.append(round(weighted, 2))
    return combined, total_rounds

def main():
    args = parse_args()
    print("=== Väylätilasto Updater V5.3 - 1000+ kierrosta ===")
    
    # Kerää data
    data = []
    data.append((DEFAULTS["44010"]["avg"], DEFAULTS["44010"]["rounds"]))
    data.append((DEFAULTS["44763"]["avg"], DEFAULTS["44763"]["rounds"]))
    data.append((DEFAULTS["48112"]["avg"], DEFAULTS["48112"]["rounds"]))
    data.append((DEFAULTS["udisc"]["avg"], DEFAULTS["udisc"]["rounds"]))
    
    combined, total = weighted_avg(data)
    par = [4,3,3,3,3,3,3,3,4,3,5,4]
    over = [combined[i]-par[i] for i in range(12)]
    sorted_idx = sorted(range(12), key=lambda i: over[i])
    diff = [0]*12
    for rank, idx in enumerate(sorted_idx):
        diff[idx] = rank+1
    
    print(f"Yhdistetty {total} kierrosta: Avg {combined} = {sum(combined):.2f}")
    print(f"Over par: {[round(x,2) for x in over]}")
    print(f"Difficulty: {diff}")
    
    # Päivitä vaylatilasto.json
    base_path = pathlib.Path(__file__).resolve().parent
    data_dir = base_path / "data" if (base_path / "data").exists() else base_path.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Lue olemassa oleva pohja
    try:
        existing = json.loads((data_dir / "vaylatilasto.json").read_text(encoding='utf-8'))
    except:
        existing = {}
    
    # Rakenna uusi
    def color_avg(a,p):
        d=a-p
        if d>=1.0: return "cell-red"
        if d>=0.5: return "cell-orange"
        if d>=0.2: return "cell-yellow"
        return "cell-green"
    def color_diff(d):
        if d<=3: return "cell-green"
        if d<=6: return "cell-yellow"
        if d<=9: return "cell-orange"
        return "cell-red"
    
    avg_cls = [color_avg(combined[i], par[i]) for i in range(12)]
    diff_cls = [color_diff(diff[i]) for i in range(12)]
    
    new_data = {
        "vayla_count": 12,
        "par_total": "41",
        "pituus_total": "1248m",
        "avg_total": f"{sum(combined):.2f}",
        "avg_total_calc": round(sum(combined),2),
        "difficulty_total": "78",
        "over_par_total": f"{sum(combined)-41:.2f}",
        "total_hole_attempts": total*12,
        "total_rounds": total,
        "pituus": ["125m","103m","72m","57m","94m","96m","103m","80m","116m","85m","197m","120m","1248m","-"],
        "par": [str(p) for p in par] + ["41","-"],
        "avg": [f"{x:.2f}" for x in combined] + [f"{sum(combined):.2f}","-"],
        "avgCls": avg_cls + ["cell-dark","cell-dark"],
        "difficulty": [str(d) for d in diff] + ["78","-"],
        "diffCls": diff_cls + ["cell-dark","cell-dark"],
        "hio": existing.get("hio", ["0"]*12 + ["5","0.3%"]),
        "birdie": existing.get("birdie", ["0"]*12 + ["0","0%"]),
        "par0": existing.get("par0", ["0"]*12 + ["0","0%"]),
        "bogey": existing.get("bogey", ["0"]*12 + ["0","0%"]),
        "dbl": existing.get("dbl", ["0"]*12 + ["0","0%"]),
        "tpl": existing.get("tpl", ["0"]*12 + ["0","0%"]),
        "other": existing.get("other", ["0"]*12 + ["0","0%"]),
        "fetched_at": datetime.now().isoformat(),
        "version": f"V5.3 - {total} kierrosta kuvista",
        "source": f"Metrix 44010 (615) + 44763 (130) + 48112 (19) + UDisc (444) = {total}",
        "locked": True
    }
    
    (data_dir / "vaylatilasto.json").write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ {data_dir / 'vaylatilasto.json'} päivitetty V5.3 {total} kierrosta")
    
    # Päivitä myös root
    root_path = pathlib.Path.cwd() / "vaylatilasto.json"
    if root_path.parent != data_dir:
        try:
            root_path.write_text(json.dumps(new_data, ensure_ascii=False, indent=2), encoding='utf-8')
        except:
            pass

if __name__ == "__main__":
    main()
