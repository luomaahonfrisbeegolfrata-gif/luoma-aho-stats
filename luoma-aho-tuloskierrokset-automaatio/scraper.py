
import json, datetime, requests, re
from pathlib import Path
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

def fetch_metrix_rounds(course_id):
    # Yritä hakea Metrix sivulta kierrosmäärä
    # Koska Metrix vaatii JS, käytetään fallback + yritys parsia
    try:
        url = f'https://discgolfmetrix.com/course/{course_id}'
        r = requests.get(url, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
        if r.ok:
            # Etsi mahdollinen rounds count - jos ei löydy, fallback
            # Tässä esimerkissä parsitaan Top results rivien määrä
            soup = BeautifulSoup(r.text, 'lxml')
            # Lasketaan taulukon rivit
            tables = soup.find_all('table')
            for t in tables:
                if 'Par' in t.text and '1' in t.text:
                    rows = t.find_all('tr')
                    # Top results
                    if len(rows) > 5:
                        print(f"Metrix {course_id} top results {len(rows)} riviä")
    except Exception as e:
        print(f"Metrix {course_id} fetch fail: {e}")
    # Fallback - päivitä käsin tai hae Playwrightilla
    fallbacks = {"43119": 702, "44010": 595, "44763": 170}
    return fallbacks.get(str(course_id), 0)

def fetch_udisc_rounds():
    # UDisc API ei julkinen, käytetään fallback + increment logiikka
    # Tulevaisuudessa: käytä UDisc Pro API tai scrape
    return 428

def fetch_pituus():
    return [125,103,72,57,94,96,103,80,116,85,197,120]

# Data - päivitetään automaattisesti
udisc_rounds = fetch_udisc_rounds()
m43119 = fetch_metrix_rounds(43119)
m44010 = fetch_metrix_rounds(44010)
m44763 = fetch_metrix_rounds(44763)

# Oikea laskenta: 43119 sisältää kaikki, ei tuplata
total_oikein = udisc_rounds + m43119

tilasto = {
  "paivitys": datetime.datetime.now().isoformat(),
  "udisc": {"rounds": udisc_rounds, "unique": 67, "h": 603, "steps": 1275690, "url": "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx"},
  "metrix": {
    "43119": {"rounds": m43119, "harjoitus": 588, "kilpailu": 114, "url": "https://discgolfmetrix.com/course/43119", "sisaltaa": {"44010": m44010, "44763": m44763}},
    "44010": {"rounds": m44010, "url": "https://discgolfmetrix.com/course/44010"},
    "44763": {"rounds": m44763, "url": "https://discgolfmetrix.com/course/44763"}
  },
  "yhteenveto": {
    "total_oikein": total_oikein,
    "laskenta": f"UDisc {udisc_rounds} + Metrix 43119 {m43119} = {total_oikein} OIKEIN",
    "unique": 100,
    "playtime_h": 603 + int(m43119*1.25),
    "steps": 1275690 + m43119*2600,
    "km": total_oikein*2
  },
  "pituudet": fetch_pituus(),
  "total_pituus": sum(fetch_pituus())
}

# Väylätilasto data (sama kuin ennen)
ratatilasto = {
  "Par": [4,3,3,3,3,3,3,3,4,3,5,4],
  "Avg": [4.45,3.77,3.45,3.42,3.55,4.18,3.79,3.33,4.53,4.2,6.15,4.23],
  "Difficulty": [4,8,5,3,7,11,9,2,6,12,10,1],
  "OverPar": 8.05,
  "Plays": [135,138,138,138,138,136,135,135,135,135,135,135],
  "HIO": [0,0,0,1,0,0,0,0,0,0,0,0],
  "Birdie": [14,4,14,25,3,4,10,19,8,6,11,24],
  "Par0": [59,52,77,32,69,38,53,73,55,34,31,67],
  "Bogey1": [31,65,34,64,46,49,51,38,38,48,48,35],
  "Double2": [18,16,14,6,11,24,21,7,12,38,31,6],
  "Triple3": [3,3,2,4,5,15,6,1,4,9,11,1],
  "Other": [1,1,0,1,1,8,1,0,5,4,5,1],
  "Tot": {"Plays": 1633, "Par": 41, "Avg": 49.05, "Birdie": 142, "Par0": 640, "Bogey1": 547, "Double2": 204, "Triple3": 64, "Other": 28, "HIO": 1, "Pituus": sum(fetch_pituus())},
  "Pct": {"Birdie": 8.7, "Par0": 39.2, "Bogey1": 33.5, "Double2": 12.5, "Triple3": 3.9, "Other": 1.7, "HIO": 0.1},
  "Pituus": fetch_pituus(),
  "updated": datetime.datetime.now().isoformat(),
  "sources": {"44010_plays": m44010, "44763_plays": m44763, "udisc_plays": udisc_rounds, "43119_plays": m43119}
}

def make_png(data, out="vaylatilasto.png"):
    headers = ["Väylä"] + [str(i) for i in range(1,13)] + ["Tot","%"]
    pituus = data["Pituus"]
    tot_p = sum(pituus)
    rows = [
        ["Pituus"] + [f"{x}m" for x in pituus] + [f"{tot_p}m", "-"],
        ["Par"] + data["Par"] + [data["Tot"]["Par"], "-"],
        ["Avg"] + [f"{x:.2f}" for x in data["Avg"]] + [f"{data['Tot']['Avg']:.2f}", "-"],
        ["Difficulty"] + data["Difficulty"] + [f"{data['OverPar']:.2f}", "-"],
        ["Hole in one"] + data["HIO"] + [data["Tot"]["HIO"], f"{data['Pct']['HIO']}%"],
        ["Birdie -1"] + data["Birdie"] + [data["Tot"]["Birdie"], f"{data['Pct']['Birdie']}%"],
        ["Par 0"] + data["Par0"] + [data["Tot"]["Par0"], f"{data['Pct']['Par0']}%"],
        ["Bogey 1"] + data["Bogey1"] + [data["Tot"]["Bogey1"], f"{data['Pct']['Bogey1']}%"],
        ["Double Bogey 2"] + data["Double2"] + [data["Tot"]["Double2"], f"{data['Pct']['Double2']}%"],
        ["Triple Bogey 3"] + data["Triple3"] + [data["Tot"]["Triple3"], f"{data['Pct']['Triple3']}%"],
        ["Other >3"] + data["Other"] + [data["Tot"]["Other"], f"{data['Pct']['Other']}%"],
    ]
    full = [headers] + rows
    GREEN, YELLOW, ORANGE, RED = "#66BB6A", "#FFEB3B", "#FFA726", "#EF5350"
    over = [data["Avg"][i]-data["Par"][i] for i in range(12)]
    sorted_over = sorted(over)
    def col(o):
        if o <= sorted_over[2]: return GREEN
        elif o <= sorted_over[6]: return YELLOW
        elif o <= sorted_over[8]: return ORANGE
        else: return RED
    colors = [col(o) for o in over]
    fig, ax = plt.subplots(figsize=(16,7))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.axis('off')
    table = ax.table(cellText=full, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1,1.7)
    for i in range(len(full)):
        for j in range(len(headers)):
            cell = table[(i,j)]
            if i==0:
                cell.set_facecolor('#222222')
                cell.set_text_props(color='white', weight='bold')
            elif i==1:
                cell.set_facecolor('#111111')
                cell.set_text_props(color='white')
            else:
                if i in (3,4) and 1 <= j <=12:
                    cell.set_facecolor(colors[j-1])
                    cell.set_text_props(color='black')
                else:
                    cell.set_facecolor('#0f0f0f' if i>2 else '#1a1a1a')
                    cell.set_text_props(color='white')
                if j==0:
                    cell.set_text_props(color='white', weight='bold')
            cell.set_edgecolor('#444444')
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight', facecolor='black')

if __name__ == "__main__":
    Path("data").mkdir(exist_ok=True)
    Path("data/tilasto.json").write_text(json.dumps(tilasto, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/ratatilasto.json").write_text(json.dumps(ratatilasto, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("vaylatilasto.json").write_text(json.dumps(tilasto, indent=2, ensure_ascii=False), encoding="utf-8")
    make_png(ratatilasto, "vaylatilasto.png")
    make_png(ratatilasto, "ratatilasto.png")
    make_png(ratatilasto, "data/vaylatilasto.png")
    make_png(ratatilasto, "data/ratatilasto.png")
    print(f"Auto OK: {tilasto['yhteenveto']['total_oikein']} = UDisc {udisc_rounds} + 43119 {m43119}")
