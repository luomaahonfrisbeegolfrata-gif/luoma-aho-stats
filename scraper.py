
import json, datetime
from pathlib import Path
import matplotlib.pyplot as plt

def fetch_pituus():
    return [125,103,72,57,94,96,103,80,116,85,197,120]

FINAL = {
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
  "Tot": {"Plays": 1633, "Par": 41, "Avg": 49.05, "Birdie": 142, "Par0": 640, "Bogey1": 547, "Double2": 204, "Triple3": 64, "Other": 28, "HIO": 1, "Pituus": 1248},
  "Pct": {"Birdie": 8.7, "Par0": 39.2, "Bogey1": 33.5, "Double2": 12.5, "Triple3": 3.9, "Other": 1.7, "HIO": 0.1},
  "Pituus": fetch_pituus(),
  "updated": datetime.datetime.now().isoformat(),
}

def make_tiukka(data, out):
    headers=["Väylä"]+[str(i) for i in range(1,13)]+["Tot","%"]
    pituus=data["Pituus"]
    tot_p=sum(pituus)
    rows=[
        ["Pituus"]+[f"{x}m" for x in pituus]+[f"{tot_p}m","-"],
        ["Par"]+data["Par"]+[data["Tot"]["Par"],"-"],
        ["Avg"]+[f"{x:.2f}" for x in data["Avg"]]+[f"{data['Tot']['Avg']:.2f}","-"],
        ["Difficulty"]+data["Difficulty"]+[f"{data['OverPar']:.2f}","-"],
        ["Hole in one"]+data["HIO"]+[data["Tot"]["HIO"], f"{data['Pct']['HIO']}%"],
        ["Birdie -1"]+data["Birdie"]+[data["Tot"]["Birdie"], f"{data['Pct']['Birdie']}%"],
        ["Par 0"]+data["Par0"]+[data["Tot"]["Par0"], f"{data['Pct']['Par0']}%"],
        ["Bogey 1"]+data["Bogey1"]+[data["Tot"]["Bogey1"], f"{data['Pct']['Bogey1']}%"],
        ["Double Bogey 2"]+data["Double2"]+[data["Tot"]["Double2"], f"{data['Pct']['Double2']}%"],
        ["Triple Bogey 3"]+data["Triple3"]+[data["Tot"]["Triple3"], f"{data['Pct']['Triple3']}%"],
        ["Other >3"]+data["Other"]+[data["Tot"]["Other"], f"{data['Pct']['Other']}%"],
    ]
    full=[headers]+rows
    GREEN, YELLOW, ORANGE, RED = "#66BB6A", "#FFEB3B", "#FFA726", "#EF5350"
    over=[data["Avg"][i]-data["Par"][i] for i in range(12)]
    so=sorted(over)
    def col(o):
        if o <= so[2]: return GREEN
        elif o <= so[6]: return YELLOW
        elif o <= so[8]: return ORANGE
        else: return RED
    colors=[col(o) for o in over]
    # TIUKKA: matalampi fig, scale 1.25, pad_inches 0.08
    fig, ax=plt.subplots(figsize=(16,4.2))
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.axis('off')
    table=ax.table(cellText=full, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1,1.25)
    for i in range(len(full)):
      for j in range(len(headers)):
        cell=table[(i,j)]
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
    plt.tight_layout(pad=0.2)
    plt.savefig(out, dpi=300, bbox_inches='tight', pad_inches=0.08, facecolor='black')
    plt.close()

if __name__=="__main__":
    data=FINAL
    data["updated"]=datetime.datetime.now().isoformat()
    Path("data").mkdir(exist_ok=True)
    make_tiukka(data, "vaylatilasto.png")
    make_tiukka(data, "ratatilasto.png")
    make_tiukka(data, "data/vaylatilasto.png")
    make_tiukka(data, "data/ratatilasto.png")
    print("TIUKKA PNG ilman tyhjää tilaa ylä ja alapuolella")
