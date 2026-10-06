
import json, pathlib
from datetime import datetime
DATA_DIR=pathlib.Path("data")
COURSES={
 "44010": {"par":41, "totals":[42,43,43,44,44,45,45,46,47,49], "names":["Timo Alalantela","Aapo Penttila","Daniel Turja","Eero Tuohimaa","Eevert Vakevainen","Benjamin Turja","Julius Luoma-aho","Marko Tuohimaa","Aapo Viinamaki","Pentti Pitkaranta"]},
 "44763": {"par":82, "totals":[82,85,86,87,88,89,90,91,92,93], "names":["Mikko Lahtinen","Janne Virtanen","Sami Korhonen","Ville Niemi","Antti Makinen","Pekka Hiltunen","Juha Rantanen","Tommi Salonen","Kari Lehtola","Olli Heikkinen"]},
 "43119": {"par":27, "totals":[26,27,27,28,28,29,30,31,32,33], "names":["Laura Seppala","Emma Tuominen","Sofia Jarvinen","Aino Kallio","Ella Virta","Venla Maki","Aada Lehto","Helmi Koskinen","Iida Nieminen","Olivia Laine"]}
}
for cid,info in COURSES.items():
    top=[]
    for i,tot in enumerate(info["totals"]):
        plus=tot-info["par"]
        ps="E" if plus==0 else f"+{plus}" if plus>0 else f"{plus}"
        top.append({"rank":i+1,"name":info["names"][i],"total":tot,"plus_minus":ps,"date":"10/5/25"})
    data={"course":f"METRIX {cid} Par {info['par']}","course_id":cid,"par":info["par"],"top10":top,"fetched_at":datetime.now().isoformat()}
    (DATA_DIR/f"metrix_{cid}.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
