#!/usr/bin/env python3
"""
fetch_metrix.py - Hakee Metrix datan GitHub Actions ilmaisissa rajoissa
- Ilmainen: public repo = rajaton minuutit (private 2000 min/kk), meillä ~2 min/ajo * 120 = 240 min/kk << 2000
- Metrix API: https://discgolfmetrix.com/api.php?content=result&id=COMP_ID tai course stats
- UDisc: EI virallista public API:ta - jätetään manuaaliseksi (config.json udisc_real_*), 
  tai scraapataan vain jos sinulla on UDisc Pro ja token (ei suositella ToS vuoksi)

Käyttö: python scripts/fetch_metrix.py --layouts 44010 44763 --out data/
"""
import argparse, json, pathlib, sys, time
import requests

METRIX_COURSE_API = "https://discgolfmetrix.com/api.php?content=courseStats&id={course_id}"
METRIX_RESULT_API = "https://discgolfmetrix.com/api.php?content=result&id={comp_id}"
METRIX_COURSE_PAGE = "https://discgolfmetrix.com/course/{course_id}"

def fetch_course_stats(course_id):
    """Hakee Metrix kurssin tilastot - top10, avg, jne."""
    # Metrix ei julkaise virallista courseStats API:a, joten parsitaan HTML tai käytetään course/{id}/stats
    # Tässä esimerkki joka hakee top10 ja avg per väylä
    try:
        # Yritä API
        url = f"https://discgolfmetrix.com/api.php?content=course&id={course_id}"
        r = requests.get(url, timeout=15, headers={"User-Agent": "luoma-aho-stats/1.0 (github actions)"})
        if r.ok:
            # API palauttaa JSON jos kurssi on public
            try:
                return r.json()
            except:
                pass
        # Fallback: hae HTML ja parsi
        r = requests.get(METRIX_COURSE_PAGE.format(course_id=course_id), timeout=15)
        r.raise_for_status()
        # Tässä pitäisi parsia HTML:stä top10 ja väyläkeskiarvot - yksinkertaistettu
        # Palautetaan tyhjä jos ei onnistu, build_stats.py käyttää fallbackia
        return None
    except Exception as e:
        print(f"  [WARN] course {course_id} fetch fail: {e}", file=sys.stderr)
        return None

def fetch_competition(comp_id):
    try:
        url = METRIX_RESULT_API.format(comp_id=comp_id)
        r = requests.get(url, timeout=15, headers={"User-Agent": "luoma-aho-stats/1.0"})
        if r.ok:
            return r.json()
    except Exception as e:
        print(f"  [WARN] comp {comp_id} fail: {e}", file=sys.stderr)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layouts", nargs="+", default=["44010", "44763"], help="Metrix layout IDs")
    ap.add_argument("--out", default="data", help="Output dir")
    ap.add_argument("--config", default="config.json", help="Config file to update rounds")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    cfg_path = pathlib.Path(args.config)
    cfg = json.loads(cfg_path.read_text(encoding='utf-8')) if cfg_path.exists() else {}

    # 1. Hae Metrix layoutit
    for lid in args.layouts:
        print(f"Fetching Metrix layout {lid}...")
        data = fetch_course_stats(lid)
        if data:
            (out / f"metrix_{lid}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"  -> {out / f'metrix_{lid}.json'} ok")
        else:
            # Älä ylikirjoita vanhaa jos fetch epäonnistuu - säilytä edellinen data
            print(f"  -> skip, keep old data for {lid}")
        time.sleep(1)  # Rate limit - älä spämmää Metrixiä

    # 2. UDisc - EI automaattista hakuja ilmaiseksi
    # UDiscilla ei ole public API:ta world averageille. Vaihtoehdot:
    # - Manuaalinen: päivitä config.json udisc_real_avg_per_hole ja udisc_real_distribution_perc käsin (nykyinen tapa)
    # - UDisc Pro API: vaatii tokenin, maksullinen, ToS kieltää scraappauksen
    # - Jätetään toistaiseksi manuaaliseksi, mutta luodaan tyhjä data/udisc.json jos puuttuu
    udisc_path = out / "udisc.json"
    if not udisc_path.exists():
        print("Creating placeholder data/udisc.json (manuaalinen UDisc data config.json:ssa)")
        placeholder = {
            "total_rounds": cfg.get("layouts", {}).get("udisc", {}).get("rounds", 453),
            "unique_players": 133,
            "peliaika": {"hours": 1200},
            "askeleet": {"count": 2500000},
            "top10": []
        }
        udisc_path.write_text(json.dumps(placeholder, ensure_ascii=False, indent=2), encoding='utf-8')

    print("Fetch done. Free tier: ~1-2 min per run, 4x päivässä = 120-240 min/kk << 2000 min free limit.")

if __name__ == "__main__":
    main()
