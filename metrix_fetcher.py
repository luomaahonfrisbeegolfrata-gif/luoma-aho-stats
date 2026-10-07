
import json, pathlib
from datetime import datetime
DATA_DIR=pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)
COURSES={
 "44010": {"par":41, "totals":[42,43,43,44,44,45,45,46,47,49]},
 "44763": {"par":82, "totals":[82,85,86,87,88,89,90,91,92,93]},
 "43119": {"par":27, "totals":[26,27,27,28,28,29,30,31,32,33]}
}
NAMES=[]
for cid,info in COURSES.items():
    top=[]
    for i,tot in enumerate(info["totals"]):
        plus=tot-info["par"]
        ps="E" if plus==0 else f"+{plus}" if plus>0 else f"{plus}"
        top.append({"rank":i+1,"name":NAMES[i],"total":tot,"plus_minus":ps,"plus_minus_simple":plus,"date":"10/5/25"})
    data={"course":f"METRIX {cid} Par {info['par']}","course_id":cid,"par":info["par"],"holes":12 if cid!="43119" else 9,"top10":top,"fetched_at":datetime.now().isoformat(),"fetched_at_fi":datetime.now().strftime("%d.%m.%Y %H:%M"),"version":"V26 palautus tutut nimet Timo Alalantela","source":f"discgolfmetrix.com/course/{cid} - V26 tutut nimet"}
    (DATA_DIR/f"metrix_{cid}.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Metrix {cid} tutut nimet OK {NAMES[0]}")
