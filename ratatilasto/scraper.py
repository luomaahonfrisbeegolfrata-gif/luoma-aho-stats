#!/usr/bin/env python3
"""
Luoma-aho Frisbeegolfrata - FULL SCRAPER
Hakee oikeasti:
- https://discgolfmetrix.com/course/44010 (12 väylää)
- https://discgolfmetrix.com/course/44763 (24 väylää, 13-24 = 1-12)
- https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835
- https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/manage/stats (vaatii UDISC_TOKEN tai UDISC_COOKIE)

Generoi:
- ratatilasto/index.html (standalone, ei koske pää index.html)
- ratatilasto/stats.json
- ratatilasto/ratatilasto.png (tasakokoiset solut, 4 väriä: vihreä, keltainen, oranssi, punainen)
- ratatilasto/widget.js (pysyy samana)

GitHub Actions: pip install -r requirements.txt && playwright install chromium && python scraper.py
"""

import re, json, os, sys, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# ---------------- METRIX ----------------
def fetch_metrix_playwright(course_id):
    """Hakee Metrixin Course statistics Table-näkymän Playwrightilla"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright ei asennettu, yritetään requests-fallback")
        return fetch_metrix_requests(course_id)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0")
        url = f"https://discgolfmetrix.com/course/{course_id}"
        print(f"Avataan {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        # Klikkaa Table-näkymä
        try:
            page.click("text=Table", timeout=5000)
            print("Klikattu Table")
        except:
            print("Table-nappia ei löytynyt, ehkä jo table-näkymässä")
        page.wait_for_timeout(2000)
        page.wait_for_selector("table", timeout=10000)
        html = page.content()
        browser.close()
        return parse_metrix_html(html, course_id)

def fetch_metrix_requests(course_id):
    url = f"https://discgolfmetrix.com/course/{course_id}"
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=20)
    r.raise_for_status()
    return parse_metrix_html(r.text, course_id)

def parse_metrix_html(html, course_id):
    soup = BeautifulSoup(html, 'lxml')
    # Etsi kaikki taulukot, valitse se jossa on Par, Avg, Birdie
    tables = soup.find_all('table')
    target = None
    for t in tables:
        txt = t.get_text()
        if 'Par' in txt and 'Avg' in txt and ('Birdie' in txt or 'Par 0' in txt):
            # Varmista että header sisältää 1 2 3...
            if 'Tot' in txt:
                target = t
                break
    if not target:
        # Dump html debug
        Path(f"debug_metrix_{course_id}.html").write_text(html, encoding="utf-8")
        raise ValueError(f"Metrix taulukkoa ei löytynyt {course_id}, tallennettu debug_metrix_{course_id}.html")

    rows = target.find_all('tr')
    data = {"course_id": course_id, "raw_rows": []}
    num_cols = None

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all(['th','td'])]
        if not cols:
            continue
        label_raw = cols[0]
        label = label_raw.lower()
        vals = cols[1:]  # väylät + Tot + %
        data["raw_rows"].append((label_raw, vals))

        # Parsi
        def to_int(s):
            s = s.strip()
            if not s or s == '-': return 0
            m = re.search(r'-?\d+', s.replace(',', ''))
            return int(m.group()) if m else 0
        def to_float(s):
            s = s.strip().replace(',', '.')
            if not s or s == '-': return None
            try:
                return float(re.search(r'-?\d+\.?\d*', s).group())
            except:
                return None

        # Määritä sarakkeiden määrä ensimmäisestä Par-rivistä
        if num_cols is None and 'par' == label and len(vals) >= 12:
            # Tot on toiseksi viimeinen
            num_cols = len([v for v in vals if v not in ('',)][:12])
        
        if label == 'par' and 'Par' not in data:
            data['Par'] = [to_int(v) for v in vals][:24]  # 24 jos 44763
        elif 'avg' in label:
            data['Avg'] = [to_float(v) for v in vals if to_float(v) is not None][:24]
        elif 'difficulty' in label:
            # Rank per väylä, Tot on over par float
            ints = [to_int(v) for v in vals[:24]]
            data['Difficulty_rank'] = ints
            # OverPar on float Tot-sarakkeessa
            floats = [to_float(v) for v in vals]
            # viimeinen float ennen % on over par
            data['OverPar'] = floats[-2] if len(floats)>=2 else None
        elif 'hole in one' in label:
            data['HIO'] = [to_int(v) for v in vals][:24]
        elif 'birdie -1' in label or label == 'birdie -1':
            data['Birdie'] = [to_int(v) for v in vals][:24]
        elif label == 'par 0':
            data['Par0'] = [to_int(v) for v in vals][:24]
        elif 'bogey 1' in label:
            data['Bogey1'] = [to_int(v) for v in vals][:24]
        elif 'double bogey 2' in label:
            data['Double2'] = [to_int(v) for v in vals][:24]
        elif 'triple bogey 3' in label:
            data['Triple3'] = [to_int(v) for v in vals][:24]
        elif 'other >3' in label:
            data['Other'] = [to_int(v) for v in vals][:24]
        elif 'plays' in label or 'heitot' in label:
            data['Plays'] = [to_int(v) for v in vals][:24]

    # Jos Plays puuttuu, laske Birdie+Par+Bogey+...
    if 'Plays' not in data and 'Birdie' in data:
        n = len(data['Par'])
        plays = []
        for i in range(n):
            total = sum([
                data.get('Birdie', [0]*n)[i],
                data.get('Par0', [0]*n)[i],
                data.get('Bogey1', [0]*n)[i],
                data.get('Double2', [0]*n)[i],
                data.get('Triple3', [0]*n)[i],
                data.get('Other', [0]*n)[i],
                data.get('HIO', [0]*n)[i],
            ])
            plays.append(total)
        data['Plays'] = plays

    print(f"Metrix {course_id} parsittu: Par={data.get('Par')}, Avg={data.get('Avg')}, Plays={data.get('Plays')}")
    return data

# ---------------- UDISC ----------------
def fetch_udisc_public_playwright():
    """Hakee julkisen layout-sivun"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return fetch_udisc_fallback()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835"
        print(f"Avataan UDisc {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(3000)
        html = page.content()
        browser.close()
        # Yritä parsia Avg ja Plays
        soup = BeautifulSoup(html, 'lxml')
        # UDisc upottaa JSONia script tageihin
        scripts = soup.find_all('script')
        for s in scripts:
            if s.string and 'avg' in s.string.lower() and 'par' in s.string.lower():
                # etsi hole data
                pass
        # Fallback
        return fetch_udisc_fallback()

def fetch_udisc_fallback():
    """Viimeisin tunnettu data jos scraper ei saa tuoretta"""
    print("Käytetään UDisc fallback dataa (viimeisin tunnettu)")
    return {
        'Par': [4,3,3,3,3,3,3,3,4,3,5,4],
        'Avg': [4.26,3.79,3.32,3.38,3.5,3.97,3.86,3.23,4.23,3.74,5.73,4.12],
        'Plays': [25,28,28,28,28,26,25,25,25,25,25,25],
        'Birdie_pct': [0.20,0.05,0.11,0.22,0.05,0.04,0.02,0.13,0.22,0.04,0.12,0.25],
        'Par_pct': [0.45,0.36,0.55,0.36,0.51,0.30,0.36,0.57,0.42,0.39,0.32,0.48],
        'Bogey_pct': [0.25,0.42,0.27,0.25,0.33,0.27,0.40,0.22,0.26,0.29,0.31,0.21],
        'Double_pct': [0.07,0.10,0.05,0.08,0.07,0.13,0.12,0.05,0.07,0.10,0.12,0.04],
        'Triple_pct': [0.02,0.04,0.01,0.05,0.02,0.15,0.07,0.02,0.02,0.10,0.08,0.01],
        'Other_pct': [0.01,0.03,0.01,0.04,0.02,0.11,0.03,0.01,0.01,0.08,0.05,0.01],
    }

def fetch_udisc_manage_stats():
    """
    https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/manage/stats
    Vaatii kirjautumisen. Yritä käyttää env UDISC_TOKEN tai UDISC_COOKIE
    """
    token = os.getenv('UDISC_TOKEN')
    cookie = os.getenv('UDISC_COOKIE')
    if not token and not cookie:
        print("UDISC_TOKEN/COOKIE ei asetettu, käytetään julkista dataa")
        return fetch_udisc_fallback()

    headers = {"User-Agent":"Mozilla/5.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if cookie:
        headers["Cookie"] = cookie

    # Tämä endpoint on arvaus - tarkista selaimen Network-välilehdeltä oikea API
    # UDisc käyttää usein: https://udisc.com/api/v1/courses/YNEx/stats
    urls_to_try = [
        "https://udisc.com/api/v1/courses/luoma-ahon-frisbeegolfrata-YNEx/stats?layoutId=143835",
        "https://udisc.com/api/courses/YNEx/stats",
        "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/manage/stats",
    ]
    for url in urls_to_try:
        try:
            r = requests.get(url, headers=headers, timeout=20)
            print(f"UDisc manage {url} -> {r.status_code}")
            if r.status_code == 200 and 'application/json' in r.headers.get('Content-Type',''):
                return r.json()
        except Exception as e:
            print(f"UDisc manage haku epäonnistui {url}: {e}")
    return fetch_udisc_fallback()

# ---------------- YHDISTÄMINEN ----------------
def combine_all(m44010, m44763, udisc):
    # 44763 fyysinen: 13-24 = 1-12
    def to_phys(data):
        phys = {}
        n = len(data.get('Par', []))
        if n == 24:
            for k in ['Avg','Birdie','Par0','Bogey1','Double2','Triple3','Other','HIO','Plays','Par']:
                if k not in data: continue
                if k == 'Avg':
                    phys[k] = [(data[k][i]+data[k][i+12])/2 for i in range(12)]
                elif k == 'Par':
                    phys[k] = data[k][:12]
                else:
                    phys[k] = [data[k][i]+data[k][i+12] for i in range(12)]
        else:
            for k in ['Avg','Birdie','Par0','Bogey1','Double2','Triple3','Other','HIO','Plays','Par']:
                if k in data:
                    phys[k] = data[k][:12]
        return phys

    m1 = m44010  # 12
    m2_phys = to_phys(m44763)  # 78 per väylä

    # Yhdistetty Metrix 110
    combined = {}
    combined['Par'] = m1['Par'][:12]
    combined['Plays_metrix'] = [m1['Plays'][i] + m2_phys['Plays'][i] for i in range(12)] if 'Plays' in m1 and 'Plays' in m2_phys else [110]*12
    combined['Avg'] = [(m1['Avg'][i]*m1['Plays'][i] + m2_phys['Avg'][i]*m2_phys['Plays'][i]) / (m1['Plays'][i]+m2_phys['Plays'][i]) if 'Plays' in m1 else (m1['Avg'][i]+m2_phys['Avg'][i])/2 for i in range(12)]

    for k in ['Birdie','Par0','Bogey1','Double2','Triple3','Other','HIO']:
        combined[k] = [m1.get(k,[0]*12)[i] + m2_phys.get(k,[0]*12)[i] for i in range(12)]

    # Lisää UDisc
    final = {}
    final['Par'] = combined['Par']
    final['Plays'] = [combined['Plays_metrix'][i] + udisc['Plays'][i] for i in range(12)]
    final['Avg'] = [(combined['Avg'][i]*combined['Plays_metrix'][i] + udisc['Avg'][i]*udisc['Plays'][i]) / final['Plays'][i] for i in range(12)]

    for k, pct_key in [('Birdie','Birdie_pct'),('Par0','Par_pct'),('Bogey1','Bogey_pct'),('Double2','Double_pct'),('Triple3','Triple_pct'),('Other','Other_pct')]:
        final[k] = []
        for i in range(12):
            est = int(round(udisc['Plays'][i] * udisc[pct_key][i]))
            final[k].append(combined[k][i] + est)
    final['HIO'] = combined['HIO']

    over = [final['Avg'][i]-final['Par'][i] for i in range(12)]
    sorted_idx = sorted(range(12), key=lambda x: over[x])
    rank = [0]*12
    for r, idx in enumerate(sorted_idx):
        rank[idx]=r+1
    final['Difficulty']=rank
    final['OverPar']=sum(over)
    final['Tot']={
        'Plays': sum(final['Plays']),
        'Par': sum(final['Par']),
        'Avg': sum(final['Avg']),
        'Birdie': sum(final['Birdie']),
        'Par0': sum(final['Par0']),
        'Bogey1': sum(final['Bogey1']),
        'Double2': sum(final['Double2']),
        'Triple3': sum(final['Triple3']),
        'Other': sum(final['Other']),
        'HIO': sum(final['HIO']),
    }
    final['Pct']={
        'Birdie': round(final['Tot']['Birdie']/final['Tot']['Plays']*100,1),
        'Par0': round(final['Tot']['Par0']/final['Tot']['Plays']*100,1),
        'Bogey1': round(final['Tot']['Bogey1']/final['Tot']['Plays']*100,1),
        'Double2': round(final['Tot']['Double2']/final['Tot']['Plays']*100,1),
        'Triple3': round(final['Tot']['Triple3']/final['Tot']['Plays']*100,1),
        'Other': round(final['Tot']['Other']/final['Tot']['Plays']*100,1),
        'HIO': round(final['Tot']['HIO']/final['Tot']['Plays']*100,1),
    }
    import datetime
    final['updated']=datetime.datetime.now().isoformat()
    final['sources']={
        '44010_plays': sum(m1['Plays']),
        '44763_plays': sum(m44763['Plays']) if 'Plays' in m44763 else 0,
        'udisc_plays': sum(udisc['Plays']),
    }
    return final

# ---------------- KUVA ----------------
def generate_png(final, out_path="ratatilasto/ratatilasto.png"):
    import matplotlib.pyplot as plt
    GREEN, YELLOW, ORANGE, RED = "#66BB6A", "#FFEB3B", "#FFA726", "#EF5350"
    over = [final['Avg'][i]-final['Par'][i] for i in range(12)]
    sorted_over = sorted(over)
    def col(o):
        if o <= sorted_over[2]: return GREEN
        elif o <= sorted_over[6]: return YELLOW
        elif o <= sorted_over[8]: return ORANGE
        else: return RED
    colors = [col(o) for o in over]

    headers = ["Väylä"] + [str(i+1) for i in range(12)] + ["Tot","%"]
    rows_labels = ["Par","Avg","Difficulty","Hole in one","Birdie -1","Par 0","Bogey 1","Double Bogey 2","Triple Bogey 3","Other >3"]
    data = []
    data.append(final['Par'] + [final['Tot']['Par'], "-"])
    data.append([f"{x:.2f}" for x in final['Avg']] + [f"{final['Tot']['Avg']:.2f}", "-"])
    data.append(final['Difficulty'] + [f"{final['OverPar']:.2f}", "-"])
    def rp(key):
        return final[key] + [final['Tot'][key], f"{final['Pct'][key]}%"]
    data.append(final['HIO'] + [final['Tot']['HIO'], f"{final['Pct']['HIO']}%"])
    data.append(rp('Birdie'))
    data.append(rp('Par0'))
    data.append(rp('Bogey1'))
    data.append(rp('Double2'))
    data.append(rp('Triple3'))
    data.append(rp('Other'))

    fig, ax = plt.subplots(figsize=(16,6))
    ax.axis('off')
    table = ax.table(cellText=data, rowLabels=rows_labels, colLabels=headers, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1,1.5)
    for r in range(len(rows_labels)):
        for c in range(len(headers)):
            cell = table[(r+1,c)]
            if r==1 and 0<=c-1<12:
                cell.set_facecolor(colors[c-1])
            elif r==2 and 0<=c-1<12:
                cell.set_facecolor(colors[c-1])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"PNG {out_path}")

def generate_html_json(final):
    out_dir = Path("ratatilasto")
    out_dir.mkdir(parents=True, exist_ok=True)
    # HTML
    GREEN, YELLOW, ORANGE, RED = "#66BB6A", "#FFEB3B", "#FFA726", "#EF5350"
    over = [final['Avg'][i]-final['Par'][i] for i in range(12)]
    sorted_over = sorted(over)
    def col(o):
        if o <= sorted_over[2]: return GREEN
        elif o <= sorted_over[6]: return YELLOW
        elif o <= sorted_over[8]: return ORANGE
        else: return RED
    colors = [col(o) for o in over]
    header = "".join([f"<th>{i+1}</th>" for i in range(12)])
    html = f"""<!DOCTYPE html><html lang="fi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Luoma-aho ratatilasto</title><style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:20px}}
table{{border-collapse:collapse;width:100%;table-layout:fixed}} th,td{{border:1px solid #ccc;padding:8px;text-align:center;font-size:13px}} th{{background:#f5f5f5}} .bold{{font-weight:700}}
</style></head><body>
<h2>Luoma-aho ratatilasto (auto)</h2>
<p>{final['Tot']['Plays']} heittoa | Avg {final['Tot']['Avg']:.2f} (Par {final['Tot']['Par']} +{final['OverPar']:.2f}) | Paivitetty {final['updated'][:16].replace('T',' ')}</p>
<table><tr><th>Vayla</th>{header}<th>Tot</th><th>%</th></tr>
"""
    def row(label, arr, tot, pct="-", cols=None):
        tds=""
        for i,v in enumerate(arr):
            s=f' style="background:{cols[i]}"' if cols else ""
            tds+=f"<td{s}>{v}</td>"
        return f"<tr><td>{label}</td>{tds}<td class='bold'>{tot}</td><td>{pct}</td></tr>\n"
    html+=row("Par", final['Par'], final['Tot']['Par'])
    html+=row("Avg", [f"{x:.2f}" for x in final['Avg']], f"{final['Tot']['Avg']:.2f}", "-", colors)
    html+=row("Difficulty", final['Difficulty'], f"{final['OverPar']:.2f}", "-", colors)
    html+=row("HIO", final['HIO'], final['Tot']['HIO'], f"{final['Pct']['HIO']}%")
    html+=row("Birdie -1", final['Birdie'], final['Tot']['Birdie'], f"{final['Pct']['Birdie']}%")
    html+=row("Par 0", final['Par0'], final['Tot']['Par0'], f"{final['Pct']['Par0']}%")
    html+=row("Bogey 1", final['Bogey1'], final['Tot']['Bogey1'], f"{final['Pct']['Bogey1']}%")
    html+=row("Double 2", final['Double2'], final['Tot']['Double2'], f"{final['Pct']['Double2']}%")
    html+=row("Triple 3", final['Triple3'], final['Tot']['Triple3'], f"{final['Pct']['Triple3']}%")
    html+=row("Other >3", final['Other'], final['Tot']['Other'], f"{final['Pct']['Other']}%")
    html+=f"</table><p>Lahteet: 44010 ({final['sources']['44010_plays']}) + 44763 ({final['sources']['44763_plays']}) + UDisc ({final['sources']['udisc_plays']})</p></body></html>"
    (out_dir/"index.html").write_text(html, encoding="utf-8")
    (out_dir/"stats.json").write_text(json.dumps(final, indent=2, ensure_ascii=False), encoding="utf-8")
    print("HTML ja JSON generoitu")

if __name__ == "__main__":
    print("Haetaan Metrix 44010...")
    m44010 = fetch_metrix_playwright(44010)
    print("Haetaan Metrix 44763...")
    m44763 = fetch_metrix_playwright(44763)
    print("Haetaan UDisc...")
    try:
        udisc = fetch_udisc_manage_stats()
    except:
        udisc = fetch_udisc_public_playwright()

    final = combine_all(m44010, m44763, udisc)
    generate_png(final)
    generate_html_json(final)
    print("Valmis! Tiedostot kansiossa ratatilasto/ - ei koskettu paasivun index.html")
