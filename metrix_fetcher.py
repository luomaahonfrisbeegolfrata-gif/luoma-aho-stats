import json, pathlib, re, sys
from datetime import datetime
import requests

# Metrix 44010, 44763, 43119 - hakee kierrosmäärät ja TOP5
# HUOM: Metrix vaatii joskus evästeen, mutta public course-sivu toimii ilman loginia

HEADERS = {"User-Agent":"Mozilla/5.0 Luoma-aho-stats"}

def fetch_course(course_id):
    url = f"https://discgolfmetrix.com/course/{course_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        html = r.text
        # Etsi kierrosmäärä - Metrix näyttää esim "702 results" tai taulukossa
        # Yritä kahta patternia
        m = re.search(r'"totalResults"\s*:\s*(\d+)', html)
        if m:
            total = int(m.group(1))
        else:
            # fallback: laske <tr> tuloksissa
            total = html.count('class="result"')
        # TOP5 - etsi leaderboard taulukosta (yksinkertaistettu)
        # Haetaan erikseen results-sivu
        url2 = f"https://discgolfmetrix.com/course/{course_id}/results"
        r2 = requests.get(url2, headers=HEADERS, timeout=15)
        # Parsitaan TOP5 - tässä esimerkki, muokkaa tarvittaessa
        top5 = []
        # Regex pelaaja + tulos
        # Esimerkki: <td class="player">Toni Luoma-aho</td><td>+1 (42)</td>
        pattern = re.findall(r'<td class="[^"]*player[^"]*">([^<]+)</td>.*?([+-]?\d+\s*\(\d+\))', r2.text, re.S)
        for i, (player, score) in enumerate(pattern[:5]):
            top5.append({"rank": i+1, "player": player.strip(), "score": score.strip(), "date": datetime.now().strftime("%d.%m.%Y")})
        return total, top5
    except Exception as e:
        print(f"Metrix {course_id} fetch error: {e}")
        return None, []

# Päivitä data
tilasto_path = pathlib.Path('data/tilasto.json')
top5_path = pathlib.Path('data/top5.json')

tilasto = json.loads(tilasto_path.read_text(encoding='utf-8')) if tilasto_path.exists() else {}
top5_data = json.loads(top5_path.read_text(encoding='utf-8')) if top5_path.exists() else {}

for cid, key in [(44010, "metrix_44010"), (44763, "metrix_44763"), (43119, "metrix_43119")]:
    total, top = fetch_course(cid)
    if total is not None:
        print(f"{cid}: {total} kierrosta, TOP5 {len(top)}")
        if key in top5_data and top:
            top5_data[key]["top5"] = top
        if cid == 43119:
            # Päivitä kokonaismäärä
            tilasto["metrix"] = tilasto.get("metrix", {})
            tilasto["metrix"][str(cid)] = total
            tilasto["total"] = tilasto.get("udisc", {}).get("rounds", 428) + total

# Tallenna
if top5_data:
    top5_data["paivitys"] = datetime.now().isoformat()
    top5_path.write_text(json.dumps(top5_data, ensure_ascii=False, indent=2), encoding='utf-8')
if tilasto:
    tilasto["updated"] = datetime.now().isoformat()
    tilasto_path.write_text(json.dumps(tilasto, ensure_ascii=False, indent=2), encoding='utf-8')

print("Metrix fetch OK - jos 44010 3 kierrosta puuttui, nyt pitäisi näkyä TOP5 ja total +3")
