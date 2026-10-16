"""
metrix_kilpailut_fetcher.py - hakee tulevat kilpailut Metrix radoilta
44010, 44763, 45536, 48112
Parsii https://discgolfmetrix.com/course/<id> sivun Upcoming events taulukon
"""

import json
import pathlib
import re
import time
from datetime import datetime, timezone

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None

BASE = pathlib.Path(__file__).resolve().parent
CANDIDATES = [BASE.parent / "data", BASE / "data", BASE, pathlib.Path.cwd() / "data"]
DATA_DIR = None
for c in CANDIDATES:
    if c.exists() and (c / "metrix_kilpailut.json").exists() or c.name == "data":
        DATA_DIR = c if c.name == "data" else c
        break
if DATA_DIR is None:
    DATA_DIR = BASE.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

COURSES = [
    {"id": "44010", "name": "Luoma-ahon Frisbeegolfrata", "short": "Luoma-aho"},
    {"id": "44763", "name": "Alajärvi", "short": "Alajärvi"},
    {"id": "45536", "name": "Kure", "short": "Kure"},
    {"id": "48112", "name": "Lappajärvi", "short": "Lappajärvi"},
]


MANUAL_COMPETITIONS = [
    "3819613", "3819645", "3819646", "3820197",
    "3820198", "3820199", "3820200", "3820202"
]

def fetch_manual_competition(comp_id):
    url = f"https://discgolfmetrix.com/{comp_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        # Yritä löytää kilpailun nimi title:stä tai h1:stä
        name = f"Kilpailu {comp_id}"
        # Title tag
        if soup.title and soup.title.string:
            name = soup.title.string.strip().replace(" | DiscGolfMetrix", "").replace("Metrix", "").strip()
            if len(name) < 3:
                name = f"Kilpailu {comp_id}"
        # Jos nimi on geneerinen, käytä Pakkassarja nimeä
        if "Metrix" in name or len(name) < 5:
            # Map known IDs to Pakkassarja names
            mapping = {
                "3819613": "PAKKASSARJA KOKO SARJA",
                "3819645": "PAKKASSARJA #1 - 7.11",
                "3819646": "PAKKASSARJA #2 - 14.11",
                "3820197": "PAKKASSARJA #3 - 21.11",
                "3820198": "PAKKASSARJA #4 - 28.11",
                "3820199": "PAKKASSARJA #5 - 5.12",
                "3820200": "PAKKASSARJA #6 - 12.12",
                "3820202": "PAKKASSARJA #7 - 19.12 FINALE",
            }
            name = mapping.get(comp_id, f"Kilpailu {comp_id}")
        return {
            "date": "",
            "name": name,
            "course": "44010",
            "courseName": "Luoma-aho",
            "competitionId": comp_id,
            "id": comp_id,
            "type": "Pakkassarja",
            "url": url,
            "reg": "Avoinna",
            "players": 0,
            "active": True,
            "manual": True
        }
    except Exception as e:
        print(f"  Manual {comp_id} fail: {e}")
        return {
            "date": "",
            "name": f"Kilpailu {comp_id}",
            "course": "44010",
            "courseName": "Luoma-aho",
            "competitionId": comp_id,
            "id": comp_id,
            "type": "Kisa",
            "url": f"https://discgolfmetrix.com/{comp_id}",
            "reg": "Avoinna",
            "players": 0,
            "active": True
        }



def parse_date_fi(d):
    """Parsii suomalaisen päivämäärän, palauttaa datetime tai None"""
    try:
        m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})\s*(\d{1,2}):(\d{2})", d)
        if m:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)), int(m.group(4)), int(m.group(5)))
        # Range like "07.11 - 19.12.2026" -> ota loppupäivä
        m2 = re.search(r"(\d{1,2})\.(\d{1,2})\s*-\s*(\d{1,2})\.(\d{1,2})\.(\d{4})", d)
        if m2:
            return datetime(int(m2.group(5)), int(m2.group(4)), int(m2.group(3)), 23, 59)
    except:
        pass
    return None

def is_finished(k):
    """Kun kilpailu on loppunut, siirtyy automaattisesti pois listalta"""
    if k.get("isSeries"):
        return False  # Koko sarja ei poistu
    date_str = k.get("date","")
    dt = parse_date_fi(date_str)
    if dt:
        # Jos kisa loppunut yli 24h sitten, poista listalta
        if dt.timestamp() + 24*3600 < datetime.now().timestamp():
            return True
    reg = (k.get("reg") or "").lower()
    if "päättynyt" in reg or "finished" in reg or "suljettu" in reg:
        return True
    return False

def sort_newest_first(events):
    """Uusin kilpailu aina ylimpänä listalla"""
    def key_func(x):
        dt = parse_date_fi(x.get("date",""))
        return dt.timestamp() if dt else 0
    return sorted(events, key=key_func, reverse=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8",
}

def fetch_course_events(course_id):
    url = f"https://discgolfmetrix.com/course/{course_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        events = []
        # Etsi Upcoming events otsikko ja seuraava taulukko
        # Metrix rakenne: <h2>Upcoming events</h2> + table
        # Tai etsi kaikki td joissa päivämäärä
        upcoming_header = soup.find(lambda tag: tag.name in ["h2","h3"] and "Upcoming events" in tag.get_text())
        if upcoming_header:
            table = upcoming_header.find_next("table")
            if table:
                rows = table.find_all("tr")[1:]  # skip header
                for tr in rows:
                    tds = tr.find_all("td")
                    if len(tds) < 2:
                        continue
                    text = tr.get_text(" ", strip=True)
                    if "There are no upcoming events" in text:
                        continue
                    # Metrix columns: Date, Time | Event name | Event type | Registration | Number
                    date = tds[0].get_text(strip=True) if len(tds)>0 else ""
                    name_td = tds[1] if len(tds)>1 else None
                    name = name_td.get_text(strip=True) if name_td else ""
                    link = ""
                    if name_td:
                        a = name_td.find("a")
                        if a and a.get("href"):
                            href = a["href"]
                            if href.startswith("/"):
                                link = f"https://discgolfmetrix.com{href}"
                            else:
                                link = href
                    etype = tds[2].get_text(strip=True) if len(tds)>2 else ""
                    reg = tds[3].get_text(strip=True) if len(tds)>3 else ""
                    num = tds[4].get_text(strip=True) if len(tds)>4 else "0"
                    try:
                        players = int(re.search(r"\d+", num).group()) if re.search(r"\d+", num) else 0
                    except:
                        players = 0
                    if name:
                        events.append({
                            "date": date,
                            "name": name,
                            "course": course_id,
                            "courseName": next((c["short"] for c in COURSES if c["id"]==course_id), course_id),
                            "type": etype,
                            "url": link or url,
                            "reg": reg,
                            "players": players
                        })
        return events
    except Exception as e:
        print(f"  Fail {course_id}: {e}")
        return []

def main():
    print("=== metrix_kilpailut_fetcher.py ===")
    if requests is None:
        print("requests puuttuu - käytetään fallback")
        return

    all_events = []
    # 1. Hae manuaaliset kilpailut (8 kpl käyttäjän listalta)
    print(f"Haetaan {len(MANUAL_COMPETITIONS)} manuaalista kilpailua...")
    for comp_id in MANUAL_COMPETITIONS:
        ev = fetch_manual_competition(comp_id)
        if ev:
            all_events.append(ev)
            print(f"  -> Manual {comp_id}: {ev['name']}")
        time.sleep(0.5)

    # 2. Hae kurssien upcoming events
    for course in COURSES:
        print(f"Haetaan {course['id']} {course['short']}...")
        evs = fetch_course_events(course["id"])
        print(f"  -> {len(evs)} tapahtumaa")
        all_events.extend(evs)
        time.sleep(1)

    # SUODATA: kun kilpailu on loppunut, siirtyy automaattisesti pois listalta
    before_filter = len(all_events)
    all_events = [e for e in all_events if not is_finished(e)]
    removed = before_filter - len(all_events)
    if removed > 0:
        print(f"  Poistettu {removed} loppunutta kilpailua automaattisesti")

    # SORTTAA: uusin aina ylimpänä
    all_events = sort_newest_first(all_events)

    data = {
        "courses": [{"id": c["id"], "name": c["name"], "url": f"https://discgolfmetrix.com/course/{c['id']}", "layout": c["short"]} for c in COURSES],
        "upcoming": all_events,
        "kilpailut": all_events,
        "updated": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "Metrix 44010,44763,45536,48112 - upcoming events",
        "version": "V1.1 auto-fetched"
    }

    out = DATA_DIR / "metrix_kilpailut.json"
    # Jos ei tapahtumia, säilytä vanha jos olemassa
    if not all_events and out.exists():
        try:
            old = json.loads(out.read_text(encoding="utf-8"))
            if old.get("upcoming"):
                print(f"Ei uusia tapahtumia, säilytetään vanha {len(old['upcoming'])} kpl")
                old["fetched_at"] = data["fetched_at"]
                old["updated"] = data["updated"]
                out.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")
                return
        except:
            pass

    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Tallennettu {out} - {len(all_events)} kilpailua")

if __name__ == "__main__":
    main()
