
import json, pathlib
from datetime import datetime
DATA_DIR=pathlib.Path("data")
data={"version":"V26 vaylatilasto","fetched_at":datetime.now().isoformat()}
(DATA_DIR/"vaylatilasto.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print("Vaylatilasto V26")
