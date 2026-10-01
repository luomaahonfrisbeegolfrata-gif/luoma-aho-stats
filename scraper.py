import json
import pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data_path = pathlib.Path('data/ratatilasto.json')
if not data_path.exists():
    data_path = pathlib.Path('ratatilasto.json')
data = json.loads(data_path.read_text(encoding='utf-8'))

def make_tiukka(d, out_path):
    headers = ["Vayla"] + [str(i) for i in range(1,13)] + ["Tot","%"]
    pituus = d.get("Pituus", [125,103,72,57,94,96,103,80,116,85,197,120])
    tot_p = sum(pituus)
    rows = [
        ["Pituus"] + [f"{x}m" for x in pituus] + [f"{tot_p}m","-"],
        ["Par"] + d["Par"] + [d["Tot"]["Par"],"-"],
        ["Avg"] + [f"{x:.2f}" for x in d["Avg"]] + [f"{d['Tot']['Avg']:.2f}","-"],
        ["Difficulty"] + d["Difficulty"] + [f"{d['OverPar']:.2f}","-"],
        ["Hole in one"] + d["HIO"] + [d["Tot"]["HIO"], f"{d['Pct']['HIO']}%"],
        ["Birdie -1"] + d["Birdie"] + [d["Tot"]["Birdie"], f"{d['Pct']['Birdie']}%"],
        ["Par 0"] + d["Par0"] + [d["Tot"]["Par0"], f"{d['Pct']['Par0']}%"],
        ["Bogey 1"] + d["Bogey1"] + [d["Tot"]["Bogey1"], f"{d['Pct']['Bogey1']}%"],
        ["Double Bogey 2"] + d["Double2"] + [d["Tot"]["Double2"], f"{d['Pct']['Double2']}%"],
        ["Triple Bogey 3"] + d["Triple3"] + [d["Tot"]["Triple3"], f"{d['Pct']['Triple3']}%"],
        ["Other >3"] + d["Other"] + [d["Tot"]["Other"], f"{d['Pct']['Other']}%"],
    ]
    full = [headers] + rows
    fig, ax = plt.subplots(figsize=(16,3.8))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.axis('off')
    table = ax.table(cellText=full, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1,1.15)
    for i in range(len(full)):
        for j in range(len(headers)):
            cell = table[(i,j)]
            cell.set_edgecolor('#444444')
            if i == 0:
                cell.set_facecolor('#222222')
                cell.set_text_props(color='white', weight='bold')
            else:
                cell.set_facecolor('#0f0f0f')
                cell.set_text_props(color='white')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    pathlib.Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=350, bbox_inches='tight', pad_inches=0, facecolor='black')
    plt.close()

make_tiukka(data, 'vaylatilasto.png')
make_tiukka(data, 'data/vaylatilasto.png')
make_tiukka(data, 'ratatilasto.png')
make_tiukka(data, 'data/ratatilasto.png')
print("PNG tiukka OK")
