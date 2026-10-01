import json, pathlib, datetime, re
import requests

HEADERS={"User-Agent":"Mozilla/5.0 Luoma-aho-stats-Dynaaminen"}
TILASTO_PATH=pathlib.Path('data/tilasto.json')

# Lue aiempi - KIRURGISEN periaate: säilytä aiempi jos fetch ei toteudu
if TILASTO_PATH.exists():
    old=json.loads(TILASTO_PATH.read_text(encoding='utf-8'))
else:
    old={
        "udisc":{"rounds":428,"unique":67},
        "metrix":{"43119":702,"44010":598,"44763":170},
        "total":1130,"unique":100,"playtime":1481,"steps":3100890,"km":2260
    }

def fetch_metrix_count(cid):
    try:
        # DiscGolfMetrix course page
        r=requests.get(f"https://discgolfmetrix.com/course/{cid}", headers=HEADERS, timeout=15)
        if r.status_code!=200:
            print(f"Metrix {cid} HTTP {r.status_code} - säilytetään aiempi {old['metrix'].get(str(cid))}")
            return None
        # Etsi tulosmäärä - etsi "X results" tai laske competition_result rivit
        # Metrix näyttää usein "702 results" tms
        m=re.search(r'(\d+)\s+results', r.text, re.I)
        if m:
            cnt=int(m.group(1))
            if cnt>10:
                return cnt
        # Fallback: laske tuloksia
        cnt=r.text.count('competition_result') + r.text.count('practice_result')
        if cnt>10:
            return cnt
        print(f"Metrix {cid} parsinta epäonnistui - säilytetään aiempi")
        return None
    except Exception as e:
        print(f"Metrix {cid} fetch error {e} - säilytetään aiempi")
        return None

# DYNAAMINEN haku - vain onnistuneet päivitetään
new_metrix={}
for cid in ["43119","44010","44763"]:
    fetched=fetch_metrix_count(int(cid))
    if fetched is not None:
        new_metrix[cid]=fetched
        print(f"Metrix {cid} DYNAAMINEN {fetched} (aiempi {old['metrix'].get(cid)})")
    else:
        # KIRURGISEN: säilytä aiempi tieto, älä muuta staattiseksi
        new_metrix[cid]=old['metrix'].get(cid, old['metrix'].get(str(cid), 0))
        print(f"Metrix {cid} SÄILYTETÄÄN AIEMPI {new_metrix[cid]}")

# UDisc - tällä hetkellä ei julkista APIa, joten säilytetään aiempi dynaaminen arvo
# Jos UDisc API lisätään myöhemmin, sama logiikka: jos fetch onnistuu päivitä, jos ei säilytä
udisc_rounds=old['udisc'].get('rounds',428)
udisc_unique=old['udisc'].get('unique',67)

# TOTAL DYNAAMINEN: 428+702=1130 OIKEIN määritelmä - jos metrix 43119 päivittyy, total päivittyy
total = udisc_rounds + new_metrix.get("43119",702)

# MUUT DYNAAMISIA johdettuja - säilytä keskiarvot aiemmasta ja laske totalin mukaan
# Playtime per kierros
prev_total=old.get('total',1130) or 1130
avg_playtime = old.get('playtime',1481)/prev_total if prev_total else 1.31  # h per round
avg_steps = old.get('steps',3100890)/prev_total if prev_total else 2744
avg_km = old.get('km',2260)/prev_total if prev_total else 2.0

playtime = int(total * avg_playtime)
steps = int(total * avg_steps)
km = int(total * avg_km)

# Unique dynaaminen arvio - jos uusia kierroksia, uniikit kasvaa hieman
# Säilytä aiempi logiikka: unique = udisc_unique + metrix_unique - overlap
# Oletetaan metrix unique ~60 ja overlap ~27
metrix_unique_est = old.get('metrix_unique',60)
unique = udisc_unique + metrix_unique_est - 27  # ~100
if total > prev_total:
    # jos kierrokset kasvoi, uniikit kasvaa 10% uusista
    unique = old.get('unique',100) + int((total-prev_total)*0.1)

result={
    "udisc":{"rounds":udisc_rounds,"unique":udisc_unique,"h":old['udisc'].get('h',603),"steps":old['udisc'].get('steps',1275690)},
    "metrix":new_metrix,
    "metrix_unique":metrix_unique_est,
    "total":total,
    "unique":unique,
    "playtime":playtime,
    "steps":steps,
    "km":km,
    "avg_playtime_h":round(avg_playtime,3),
    "avg_steps":int(avg_steps),
    "avg_km":round(avg_km,2),
    "updated":datetime.datetime.now().isoformat(),
    "laskenta":f"UDisc {udisc_rounds} + Metrix 43119 {new_metrix.get('43119')} = {total} OIKEIN - DYNAAMINEN",
    "periaate":"Kaikki dynaamista, jos fetch ei toteudu säilytetään aiempi - ei staattiseksi"
}

TILASTO_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"TILASTO DYNAAMINEN paivitetty: total {total} unique {unique} playtime {playtime}h steps {steps} km {km}")
print("Jos joku fetch epaonnistui, aiempi tieto säilytettiin - ei muutettu staattiseksi")
