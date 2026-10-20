#!/usr/bin/env python3
"""vieraskirja_import.py - lisää hyväksytyn vieraskirjaviestin (GitHub Issue) data/vieraskirja.json:iin.
Käyttö (Actions): python scripts/vieraskirja_import.py [data-kansio]   - lukee GITHUB_EVENT_PATH"""
import json, os, pathlib, re, sys
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    today = datetime.now(ZoneInfo("Europe/Helsinki"))
except Exception:
    today = datetime.now()

DATA = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "data")
ev = json.loads(pathlib.Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
m = re.search(r"```json\s*(\{.*\})\s*```", ev["issue"].get("body") or "", re.S)
if not m:
    sys.exit("Issuessa ei ole JSON-lohkoa")
try:
    d = json.loads(m.group(1))
    rating = int(d.get("rating"))
except (ValueError, TypeError):
    sys.exit("Virheellinen JSON tai arvosana")
name = " ".join(str(d.get("name") or "Anonyymi").split())[:30] or "Anonyymi"
msg = str(d.get("message") or "").strip()[:500]
if len(msg) < 3 or not 1 <= rating <= 5:
    sys.exit("Virheellinen viesti tai arvosana")

p = DATA / "vieraskirja.json"
j = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"entries": []}
if any(x.get("name") == name and x.get("message") == msg for x in j["entries"]):
    print("Viesti on jo vieraskirjassa - ei muutoksia")
    sys.exit(0)
j["entries"].insert(0, {"date": today.strftime("%d.%m.%Y"), "name": name, "message": msg, "rating": rating})
rs = [x["rating"] for x in j["entries"] if x.get("rating")]
j["stats"] = {"count": len(j["entries"]), "avg": round(sum(rs) / len(rs), 1) if rs else 0, "ratings": len(rs)}
j["updated"] = today.strftime("%Y-%m-%d")
j["version"] = "V6 - viestit hyväksyntäjonon kautta"
j.pop("locked", None); j.pop("note", None)
p.write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Lisätty: {name} ({rating}★), viestejä yhteensä {len(j['entries'])}")
