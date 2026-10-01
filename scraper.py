import json, pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
data=json.loads(pathlib.Path('data/ratatilasto.json').read_text(encoding='utf-8'))
def make(d,out):
    headers=["Vayla"]+[str(i) for i in range(1,13)]+["Tot","%"]
    pituus=d.get("Pituus",[125,103,72,57,94,96,103,80,116,85,197,120])
    rows=[
        ["Pituus"]+[f"{x}m" for x in pituus]+[f"{sum(pituus)}m","-"],
        ["Par"]+d["Par"]+[d["Tot"]["Par"],"-"],
        ["Avg"]+[f"{x:.2f}" for x in d["Avg"]]+[f"{d['Tot']['Avg']:.2f}","-"],
        ["Difficulty"]+d["Difficulty"]+[f"{d['OverPar']:.2f}","-"],
        ["Hole in one"]+d["HIO"]+[d["Tot"]["HIO"],f"{d['Pct']['HIO']}%"],
        ["Birdie -1"]+d["Birdie"]+[d["Tot"]["Birdie"],f"{d['Pct']['Birdie']}%"],
        ["Par 0"]+d["Par0"]+[d["Tot"]["Par0"],f"{d['Pct']['Par0']}%"],
        ["Bogey 1"]+d["Bogey1"]+[d["Tot"]["Bogey1"],f"{d['Pct']['Bogey1']}%"],
        ["Double Bogey 2"]+d["Double2"]+[d["Tot"]["Double2"],f"{d['Pct']['Double2']}%"],
        ["Triple Bogey 3"]+d["Triple3"]+[d["Tot"]["Triple3"],f"{d['Pct']['Triple3']}%"],
        ["Other >3"]+d["Other"]+[d["Tot"]["Other"],f"{d['Pct']['Other']}%"],
    ]
    full=[headers]+rows
    GREEN="#66BB6A"; YELLOW="#FFEB3B"; ORANGE="#FFA726"; RED="#EF5350"
    over=[d["Avg"][i]-d["Par"][i] for i in range(12)]
    so=sorted(over)
    def col(o): return GREEN if o<=so[2] else YELLOW if o<=so[6] else ORANGE if o<=so[8] else RED
    colors=[col(o) for o in over]
    fig,ax=plt.subplots(figsize=(16,4.2))
    fig.patch.set_facecolor('black'); ax.set_facecolor('black'); ax.axis('off')
    table=ax.table(cellText=full, loc='center', cellLoc='center')
    table.auto_set_font_size(False); table.set_fontsize(11); table.scale(1,1.35)
    for i in range(len(full)):
        for j in range(len(headers)):
            cell=table[(i,j)]; cell.set_edgecolor('#444')
            if i==0: cell.set_facecolor('#222'); cell.set_text_props(color='white', weight='bold', fontsize=11)
            elif i in (2,3) and 1<=j<=12: cell.set_facecolor(colors[j-1]); cell.set_text_props(color='black', weight='bold', fontsize=11)
            else: cell.set_facecolor('#0f0f0f' if i>1 else '#111'); cell.set_text_props(color='white', fontsize=11)
            if j==0: cell.set_text_props(color='white', weight='bold', fontsize=11)
    plt.subplots_adjust(left=0,right=1,top=1,bottom=0)
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=350, bbox_inches='tight', pad_inches=0, facecolor='black'); plt.close()
make(data,'vaylatilasto.png')
make(data,'data/vaylatilasto.png')
print("vaylatilasto vari palautettu 11px")
