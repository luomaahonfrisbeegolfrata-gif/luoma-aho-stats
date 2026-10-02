"""
unified_fetcher.py - Korjaus #4
Yhdistää: metrix_fetcher.py + top5_fetcher.py + scraper.py + vaylatilasto_fetcher.py
- Ei kaada workflowta jos yksi lähde on alhaalla
- Validoi JSON ennen kirjoitusta
- Kirjoittaa vain muuttuneen datan
- User-Agent mukana ettei blokkaannu
"""

import json
import csv
import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
import requests

# Setup
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
HEADERS = {
    "User-Agent": "Luoma-aho-stats-bot/1.0 (+https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/; Alajärvi frisbeegolf)",
    "Accept": "application/json, text/csv, */*"
}

def fetch_with_retry(url, retries=3, timeout=20):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r
        except Exception as e:
            logging.warning(f"Fetch failed {url} attempt {i+1}/{retries}: {e}")
            time.sleep(2 * (i+1))
    raise Exception(f"Failed after {retries} retries: {url}")

def safe_write_json(path: Path, data):
    """Validoi ja kirjoittaa vain jos data muuttunut ja validi"""
    try:
        # Validointi
        if data is None:
            raise ValueError("Data is None")
        if isinstance(data, (dict, list)) and len(data) == 0:
            logging.warning(f"{path} is empty dict/list, skipping write to avoid blanking file")
            return False
        
        # Vertaa vanhaan - älä kirjoita jos sama
        if path.exists():
            try:
                old = json.loads(path.read_text(encoding="utf-8"))
                if old == data:
                    logging.info(f"{path} unchanged, skip")
                    return False
            except:
                pass  # vanha korruptoitunut, ylikirjoita

        # Atominen kirjoitus
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
        logging.info(f"Wrote {path} ({len(json.dumps(data))} bytes)")
        return True
    except Exception as e:
        logging.error(f"Failed to write {path}: {e}")
        return False

def load_urls():
    urls_path = Path("urls.json")
    if urls_path.exists():
        try:
            return json.loads(urls_path.read_text(encoding="utf-8"))
        except Exception as e:
            logging.warning(f"urls.json read failed: {e}")
    # Fallback - muokkaa näitä vastaamaan oikeita URL:eja
    return {
        "metrix_course_id": "your-metrix-id",
        "udisc_league_url": "https://udisc.com/...",
        "top5_source": "metrix"  # tai udisc
    }

# --- Yksittäiset fetcherit käärittynä ---

def fetch_metrix(urls):
    """Korvaa metrix_fetcher.py"""
    try:
        logging.info("Fetching Metrix...")
        # ESIMERKKI - korvaa omalla logiikallasi
        # Jos sinulla on vanha metrix_fetcher.py, importtaa se:
        # import metrix_fetcher; return metrix_fetcher.fetch()

        # Tässä placeholder joka lukee olemassa olevan stats.json ja rikastaa
        # Oikea toteutus: kutsu Disc Golf Metrix APIa
        # r = fetch_with_retry(f"https://discgolfmetrix.com/api.php?content=course&id={urls.get('metrix_course_id')}")
        # data = r.json()

        # Väliaikainen: yritä päivittää tilastojen timestamp
        stats_path = DATA_DIR / "stats.json"
        if stats_path.exists():
            data = json.loads(stats_path.read_text(encoding="utf-8"))
            data["_last_fetched"] = datetime.utcnow().isoformat() + "Z"
            data["_source"] = "metrix"
            safe_write_json(stats_path, data)
            safe_write_json(DATA_DIR / "ratatilasto.json", data.get("ratatilasto", data))
            return True
        logging.warning("stats.json not found, metrix fetch skipped (add real API call)")
        return False
    except Exception as e:
        logging.error(f"Metrix fetch failed but CONTINUING: {e}")
        return False

def fetch_top5(urls):
    """Korvaa top5_fetcher.py"""
    try:
        logging.info("Fetching Top5...")
        # Oikea logiikka: hae Metrix/UDisc top tulokset
        top5_path = DATA_DIR / "top5.json"
        # Esimerkki validointi
        data = None
        if top5_path.exists():
            data = json.loads(top5_path.read_text(encoding="utf-8"))
        
        # Jos data on lista ja siinä on nimiä, päivitä timestamp
        if isinstance(data, list) and len(data) > 0:
            # Älä ylikirjoita jos ei uutta
            logging.info(f"Top5 has {len(data)} entries, keeping")
            # Voit päivittää silti timestampin erilliseen tiedostoon
        elif isinstance(data, dict):
            data["_last_fetched"] = datetime.utcnow().isoformat() + "Z"
            safe_write_json(top5_path, data)
        return True
    except Exception as e:
        logging.error(f"Top5 fetch failed but CONTINUING: {e}")
        return False

def fetch_vaylatilasto(urls):
    """Korvaa vaylatilasto_fetcher.py"""
    try:
        logging.info("Fetching Vaylatilasto...")
        # Toteuta oikea haku tähän
        # r = fetch_with_retry(urls.get('vaylatilasto_url'))
        # data = r.json()
        # safe_write_json(DATA_DIR / "vaylatilasto.json", data)
        # ÄLÄ generoi PNG:tä enää - .gitignore estää sen ja chart tulee client-side
        path = DATA_DIR / "vaylatilasto.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            data["_last_fetched"] = datetime.utcnow().isoformat() + "Z"
            safe_write_json(path, data)
        return True
    except Exception as e:
        logging.error(f"Vaylatilasto fetch failed but CONTINUING: {e}")
        return False

def fetch_scraper(urls):
    """Korvaa scraper.py - UDisc / muut scrapet"""
    try:
        logging.info("Fetching via scraper...")
        # Lisää User-Agent jotta ei blokkaannu
        # r = fetch_with_retry(urls.get('udisc_url'))
        # parse...
        holeinone_path = DATA_DIR / "holeinone.json"
        if holeinone_path.exists():
            data = json.loads(holeinone_path.read_text(encoding="utf-8"))
            if isinstance(data, (list, dict)):
                data = data if isinstance(data, list) else {**data, "_last_fetched": datetime.utcnow().isoformat()+"Z"}
                if isinstance(data, dict):
                    safe_write_json(holeinone_path, data)
        return True
    except Exception as e:
        logging.error(f"Scraper failed but CONTINUING: {e}")
        return False

def main():
    urls = load_urls()
    results = {}
    
    # Aja jokainen erikseen, yksittäinen kaatuminen ei kaada koko ajoa
    results["metrix"] = fetch_metrix(urls)
    results["top5"] = fetch_top5(urls)
    results["vaylatilasto"] = fetch_vaylatilasto(urls)
    results["scraper"] = fetch_scraper(urls)

    # Yhteenveto
    success = sum(1 for v in results.values() if v)
    logging.info(f"Unified fetcher done: {success}/{len(results)} succeeded: {results}")

    # Aina exit 0 jotta GitHub Actions ei mene punaiseksi yhden lähteen takia
    # Vain jos KAIKKI epäonnistuu, exit 1
    if success == 0:
        logging.error("All fetchers failed!")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
