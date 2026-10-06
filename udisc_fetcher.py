
import json, pathlib
from datetime import datetime
DATA_DIR=pathlib.Path("data")
# UDisc TOP10 - oikeat UDisc käyttäjät, ei Metrix nimiä
UDISC_TOP=[
    {"rank":1,"name":"@kantanen8","display":"@kantanen8","total":35,"plus_minus":"-6"},
    {"rank":2,"name":"@valkoparta","display":"@valkoparta","total":36,"plus_minus":"-5"},
    {"rank":3,"name":"@mattiasss","display":"@mattiasss","total":36,"plus_minus":"-5"},
    {"rank":4,"name":"@dashyy","display":"@dashyy","total":38,"plus_minus":"-3"},
    {"rank":5,"name":"@kalle","display":"@kalle","total":38,"plus_minus":"-3"},
    {"rank":6,"name":"@juhafrisbee","display":"@juhafrisbee","total":39,"plus_minus":"-2"},
    {"rank":7,"name":"@olli_he","display":"@olli_he","total":40,"plus_minus":"-1"},
    {"rank":8,"name":"@eino","display":"@eino","total":40,"plus_minus":"-1"},
    {"rank":9,"name":"@mikko","display":"@mikko","total":41,"plus_minus":"E"},
    {"rank":10,"name":"@teemu","display":"@teemu","total":42,"plus_minus":"+1"},
]
data={"course":"UDISC Luoma-aho 12 väylää Par 41","par":41,"top10":UDISC_TOP,"fetched_at":datetime.now().isoformat(),"fetched_at_fi":datetime.now().strftime("%d.%m.%Y %H:%M"),"version":"V26 UDisc palautus oikeat nimet ei Metrix sekoitus"}
(DATA_DIR/"udisc.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
(DATA_DIR/"udisc_top10.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("UDisc V26 palautettu oikeat @ nimet")
