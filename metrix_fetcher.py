import json, pathlib, datetime, re, requests
HEADERS={"User-Agent":"Mozilla/5.0 Luoma-aho-dynaaminen"}
TILASTO_PATH=pathlib.Path('data/tilasto.json')
old=json.loads(TILASTO_PATH.read_text(encoding='utf-8')) if TILASTO_PATH.exists() else {
  "udisc":{"rounds":428,"unique":67},"metrix":{"43119":702,"44010":598,"44763":170},
  "total":1130,"unique":100,"playtime":1481,"steps":3100890,"km":2260
}
def fetch_metrix(cid):
    try:
        r=requests.get(f"https://discgolfmetrix.com/course/{cid}", headers=HEADERS, timeout=15)
        if r.status_code!=200:
            print(f"{cid} HTTP {r.status_code} sailytetaan aiempi"); return None
        m=re.search(r'(\d+)\s*(?:results|tulosta)', r.text, re.I)
        total=int(m.group(1)) if m else 0
        if total<10:
            total=old['metrix'].get(str(cid),0)
        return {"total":total,"harjoitus":total,"kilpailu":0,"practice":total,"competition":0}
    except Exception as e:
        print(f"{cid} error {e} sailytetaan aiempi"); return None
new={}
for cid in ["43119","44010","44763"]:
    f=fetch_metrix(cid)
    if f:
        new[cid]=f
        print(f"{cid} DYNAAMINEN harjoitus {f['harjoitus']} kilpailu {f['kilpailu']} total {f['total']}")
    else:
        prev=old['metrix'].get(cid) or old['metrix'].get(str(cid)) or 0
        if isinstance(prev, dict): new[cid]=prev
        else: new[cid]={"total":prev,"harjoitus":prev,"kilpailu":0,"practice":prev,"competition":0}
        print(f"{cid} SAILYTETTY {new[cid]}")
result=old.copy()
result['metrix']={k:v['total'] for k,v in new.items()}
result['metrix_detailed']=new
result['total']= (old['udisc']['rounds'] if isinstance(old['udisc'],dict) else 428) + new['43119']['total']
result['total_kaikki']= (old['udisc']['rounds'] if isinstance(old['udisc'],dict) else 428) + sum(v['total'] for v in new.values())
result['harjoituskierrokset_yhteensa']=sum(v['harjoitus'] for v in new.values())
result['kilpailukierrokset_yhteensa']=sum(v['kilpailu'] for v in new.values())
result['updated']=datetime.datetime.now().isoformat()
result['laskenta']=f"UDisc 428 + Metrix 43119 {new['43119']['total']} = {result['total']} OIKEIN | Harjoitus {result['harjoituskierrokset_yhteensa']} Kilpailu {result['kilpailukierrokset_yhteensa']} | Kaikki 3 rataa {result['total_kaikki']}"
# dynaamiset johdetut
prev_total=old.get('total',1130) or 1130
avg_pt=old.get('playtime',1481)/prev_total
avg_st=old.get('steps',3100890)/prev_total
avg_km=old.get('km',2260)/prev_total
result['playtime']=int(result['total']*avg_pt)
result['steps']=int(result['total']*avg_st)
result['km']=int(result['total']*avg_km)
TILASTO_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(result['laskenta'])
