
import json, pathlib
ROOT = pathlib.Path(__file__).parent.parent
DATA = ROOT / "data"
cfg = json.loads((DATA / "config.json").read_text(encoding='utf-8'))
layouts = cfg["layouts"]
metrix_rounds = layouts["metrix_44010"]["rounds"] + layouts["metrix_44763"]["rounds"] + layouts.get("metrix_48112",{}).get("rounds",0)
udisc_rounds = layouts["udisc"]["rounds"]
total = metrix_rounds + udisc_rounds
par = cfg["course"]["par"]
length = cfg["course"]["length_m"]
metrix_avg = cfg["metrix_avg_per_hole"]
udisc_avg = cfg["udisc_real_avg_per_hole"]
avg_combined = [round((metrix_avg[i]*metrix_rounds + udisc_avg[i]*udisc_rounds)/total,2) for i in range(12)]
AVG_RATING=868.6
PPS=15.15
offset=(AVG_RATING-1000)/PPS
ssa_holes=[round(a+offset/12,2) for a in avg_combined]
ssa_total=round(sum(ssa_holes),2)
# 100% AUTO - ei kovakoodia, säilyttää vanhat jos haku epäonnistuu
udisc_path = data_dir / "udisc.json"
metrix_files = {
  "metrix_44010": data_dir / "metrix_44010.json",
  "metrix_44763": data_dir / "metrix_44763.json", 
  "metrix_48112": data_dir / "metrix_48112.json"
}

def get_cfg_rounds(key):
  try: return cfg.get("layouts",{}).get(key,{}).get("rounds",0)
  except: return 0

udisc_rounds = get_cfg_rounds("udisc")
m44010 = get_cfg_rounds("metrix_44010")
m44763 = get_cfg_rounds("metrix_44763")
m48112 = get_cfg_rounds("metrix_48112")

def read_live(path):
  try:
    if path.exists():
      j = load(path)
      r = j.get("total_rounds") or j.get("rounds")
      if isinstance(r,int) and r>0: return r
  except: pass
  return None

# live voittaa cfg:n jos >0
for k,p in [("udisc",udisc_path),("metrix_44010",metrix_files["metrix_44010"])]:
  live = read_live(p)
  # ... sama 44763,48112
  if live: # päivitä vastaava muuttuja

# fallback vanhaan kierrokset.json jos kaikki 0
if (m44010+m44763+m48112+udisc_rounds)==0:
  try:
    old=load(data_dir/"kierrokset.json")
    # säilytä old metrix_rounds, udisc_rounds, total_rounds
  except: pass

metrix_rounds = m44010+m44763+m48112
total_rounds = metrix_rounds+udisc_rounds
# jos vielä 0 -> säilytä vanha, älä poista
    if p>=4:
        return {"label":"HELPPO" if pct>=20 else "TEKNINEN" if pct>=10 else "EROTTELEVA" if pct>=5 else "VAIKEA", "cls":"cell-green" if pct>=20 else "cell-yellow" if pct>=10 else "cell-orange" if pct>=5 else "cell-red"}
    else:
        return {"label":"HELPPO" if pct>=15 else "TEKNINEN" if pct>=8 else "EROTTELEVA" if pct>=5 else "VAIKEA", "cls":"cell-green" if pct>=15 else "cell-yellow" if pct>=8 else "cell-orange" if pct>=5 else "cell-red"}
luokitus=[get_luok(birdie_pct[i], par[i]) for i in range(12)]
v={
    "vayla_count":12,
    "par_total":str(sum(par)),
    "pituus_total":f"{sum(length)}m",
    "avg_total":f"{sum(avg_combined):.2f}",
    "avg_total_calc":round(sum(avg_combined),2),
    "over_par_total":f"{sum(avg_combined)-sum(par):.2f}",
    "ssa_total_authentic":ssa_total,
    "pituus":[f"{m}m" for m in length]+[f"{sum(length)}m","-"],
    "par":[str(p) for p in par]+[str(sum(par)),"-"],
    "avg":[f"{a:.2f}" for a in avg_combined]+[f"{sum(avg_combined):.2f}","-"],
    "difficulty":[f"{r}" for r in rank]+["-","-"],
    "diffCls":diff_cls+["cell-dark","cell-dark"],
    "luokitus":luokitus,
    "hio":hio+[sum(hio), f"{sum(hio)/total*100:.1f}%"],
    "birdie":birdie+[sum(birdie), f"{sum(birdie)/total*100:.1f}%"],
    "par0":dist["par0"]+[sum(dist["par0"]), f"{sum(dist['par0'])/total*100:.1f}%"],
    "bogey":dist["bogey"]+[sum(dist["bogey"]), f"{sum(dist['bogey'])/total*100:.1f}%"],
    "dbl":dist["dbl"]+[sum(dist["dbl"]), f"{sum(dist['dbl'])/total*100:.1f}%"],
    "tpl":dist["tpl"]+[sum(dist["tpl"]), f"{sum(dist['tpl'])/total*100:.1f}%"],
    "other":dist["other"]+[sum(dist["other"]), f"{sum(dist['other'])/total*100:.1f}%"],
    "birdie_pct":[round(p,1) for p in birdie_pct],
    "calculation":{"total_rounds":total,"metrix_rounds":metrix_rounds,"udisc_rounds":udisc_rounds}
}
(DATA/"vaylatilasto.json").write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding='utf-8')
# UDisc only
udisc_avg_total=round(sum(udisc_avg),2)
v2={
    "vayla_count":12,
    "par_total":str(sum(par)),
    "pituus_total":f"{sum(length)}m",
    "avg_total":f"{udisc_avg_total:.2f}",
    "avg_total_calc":udisc_avg_total,
    "pituus":[f"{m}m" for m in length]+[f"{sum(length)}m","-"],
    "par":[str(p) for p in par]+[str(sum(par)),"-"],
    "avg":[f"{a:.2f}" for a in udisc_avg]+[f"{udisc_avg_total:.2f}","-"],
    "difficulty":[f"{r}" for r in rank]+["-","-"],
    "diffCls":diff_cls+["cell-dark","cell-dark"],
    "luokitus":luokitus,
    "birdie_pct":[round(p,1) for p in birdie_pct],
    "birdie":[0]*14,"par0":[0]*14,"bogey":[0]*14,"dbl":[0]*14,"tpl":[0]*14,"other":[0]*14,"hio":[0]*14,
    "calculation":{"udisc_rounds":udisc_rounds}
}
(DATA/"vaylatilasto_udisc_only.json").write_text(json.dumps(v2, ensure_ascii=False, indent=2), encoding='utf-8')
kierrokset={"total_rounds":total,"metrix_rounds":metrix_rounds,"udisc_rounds":udisc_rounds,"unique_players":133,"peliaika":{"display":f"{int(total*1.335)}h"},"askeleet":{"display":f"{total*2664}"},"kilometrit":{"display":f"{int(total*2.054)}km"}}
(DATA/"kierrokset.json").write_text(json.dumps(kierrokset, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"Built {total}")
