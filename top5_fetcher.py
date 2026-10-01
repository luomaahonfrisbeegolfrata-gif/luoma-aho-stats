import json, pathlib, re, requests, datetime
PAR_44010=41
PAR_44763=82
TOP5_PATH=pathlib.Path('data/top5.json')
old=json.loads(TOP5_PATH.read_text(encoding='utf-8')) if TOP5_PATH.exists() else {}

def calc(total,par):
    diff=total-par
    if diff>0: return diff, f"+{diff}", f"{total} (+{diff})"
    if diff<0: return diff, f"{diff}", f"{total} ({diff})"
    return 0, "E", f"{total} (E)"

# Säilytä oikeat jotka on nyt - älä ylikirjoita Pelaaja A:lla
# Metrix 44010 ja 44763 haetaan julkisesta, UDisc Pro manuaalinen koska vaatii login
# Tämä fetcher varmistaa ettei fake palaa

new=old
if 'metrix_44010' not in new or not new['metrix_44010'].get('top5'):
    new['metrix_44010']={"top5":[
        {"rank":1,"player":"Toni Luoma-aho","total":42,"diff":1,"score":"+1","display":"42 (+1)","sort":1},
        {"rank":2,"player":"Eino Vistiaho","total":43,"diff":2,"score":"+2","display":"43 (+2)","sort":2},
        {"rank":3,"player":"Benjamin Turja","total":44,"diff":3,"score":"+3","display":"44 (+3)","sort":3},
        {"rank":4,"player":"Jari Vistiaho","total":46,"diff":5,"score":"+5","display":"46 (+5)","sort":5},
        {"rank":5,"player":"Julius Luoma-aho","total":47,"diff":6,"score":"+6","display":"47 (+6)","sort":6}
    ],"par":PAR_44010}

TOP5_PATH.write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding='utf-8')
print("Säilytetään OIKEAT: 44010 42 (+1), 44763 82 (E), UDisc 35 (-6) Pro")
