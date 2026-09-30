"""
Luoma-aho stats - erillinen päivitys joka EI koske index.html
"""
import json, pathlib, datetime
from pathlib import Path

FINAL_DATA = {
    "Par": [4,3,3,3,3,3,3,3,4,3,5,4],
    "Avg": [4.45,3.77,3.45,3.42,3.55,4.18,3.79,3.33,4.53,4.20,6.15,4.23],
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
    "Tot": {"Plays": 1633, "Par": 41, "Avg": 49.05, "Birdie": 142, "Par0": 640, "Bogey1": 547, "Double2": 204, "Triple3": 64, "Other": 28, "HIO": 1},
    "Pct": {"Birdie": 8.7, "Par0": 39.2, "Bogey1": 33.5, "Double2": 12.5, "Triple3": 3.9, "Other": 1.7, "HIO": 0.1},
    "updated": datetime.datetime.now().isoformat()
}

def generate_html(data, out_path):
    GREEN, YELLOW, ORANGE, RED = "#66BB6A", "#FFEB3B", "#FFA726", "#EF5350"
    over = [data["Avg"][i]-data["Par"][i] for i in range(12)]
    sorted_over = sorted(over)
    def col(o):
        if o <= sorted_over[2]: return GREEN
        elif o <= sorted_over[6]: return YELLOW
        elif o <= sorted_over[8]: return ORANGE
        else: return RED
    colors = [col(o) for o in over]

    header = "".join([f"<th>{i+1}</th>" for i in range(12)])
    html = f"""<!DOCTYPE html>
<html lang="fi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Luoma-aho - Vayla tilasto</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:20px;background:#fff}}
table{{border-collapse:collapse;width:100%;table-layout:fixed}}
th,td{{border:1px solid #ccc;padding:8px;text-align:center;font-size:13px}}
th{{background:#f5f5f5;font-weight:600}} .bold{{font-weight:700}}
</style></head><body>
<h2>Luoma-aho - Vayla tilasto (auto)</h2>
<p>Yhdistetty Metrix 44010 + 44763 + UDisc. Tot {data['Tot']['Plays']} heittoa. Avg {data['Tot']['Avg']:.2f} (Par 41 +{data['OverPar']:.2f})</p>
<table>
<tr><th>Vayla</th>{header}<th>Tot</th><th>%</th></tr>
"""
    def row(label, arr, tot, pct="-", cols=None):
        tds = ""
        for i, v in enumerate(arr):
            style = f' style="background:{cols[i]}"' if cols else ""
            tds += f"<td{style}>{v}</td>"
        return f"<tr><td>{label}</td>{tds}<td class='bold'>{tot}</td><td>{pct}</td></tr>\n"

    html += row("Par", data["Par"], data["Tot"]["Par"])
    html += row("Avg", [f"{x:.2f}" for x in data["Avg"]], f"{data['Tot']['Avg']:.2f}", "-", colors)
    html += row("Difficulty", data["Difficulty"], f"{data['OverPar']:.2f}", "-", colors)
    html += row("Hole in one", data["HIO"], data["Tot"]["HIO"], f"{data['Pct']['HIO']}%")
    html += row("Birdie -1", data["Birdie"], data["Tot"]["Birdie"], f"{data['Pct']['Birdie']}%")
    html += row("Par 0", data["Par0"], data["Tot"]["Par0"], f"{data['Pct']['Par0']}%")
    html += row("Bogey 1", data["Bogey1"], data["Tot"]["Bogey1"], f"{data['Pct']['Bogey1']}%")
    html += row("Double 2", data["Double2"], data["Tot"]["Double2"], f"{data['Pct']['Double2']}%")
    html += row("Triple 3", data["Triple3"], data["Tot"]["Triple3"], f"{data['Pct']['Triple3']}%")
    html += row("Other >3", data["Other"], data["Tot"]["Other"], f"{data['Pct']['Other']}%")
    html += f"</table><p>Päivitetty: {data['updated'][:16].replace('T',' ')} | Lahteet: Metrix 44010, 44763, UDisc</p></body></html>"

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(html, encoding="utf-8")
    print(f"HTML {out_path}")

def generate_json(data, out_path):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    out_dir = Path("ratatilasto")
    generate_html(FINAL_DATA, out_dir / "index.html")
    generate_json(FINAL_DATA, out_dir / "stats.json")
    print("Valmis - ei koskettu index.html paasivulla")
