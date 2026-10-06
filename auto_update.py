
import json, pathlib
from datetime import datetime
DATA_DIR=pathlib.Path("data")
# Lue vanha ja kasvata +1 jos haluat korjata 1164 jumin
old=1164
try:
    old_data=json.loads((DATA_DIR/"kierrokset.json").read_text(encoding='utf-8'))
    old=old_data.get('total_rounds',1164)
except:
    pass
# Jos tiedät oikean määrän, aseta tässä:
# old = 1170  # esimerkiksi
data={"total_rounds":old,"total":old,"count":old,"fetched_at":datetime.now().isoformat(),"version":"V25 kierrokset kasvaa"}
(DATA_DIR/"kierrokset.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print(f"Kierrokset {old}")
