import json, pathlib, datetime, re, requests
HEADERS={"User-Agent":"Mozilla/5.0"}
TILASTO_PATH=pathlib.Path('data/tilasto.json')
old=json.loads(TILASTO_PATH.read_text(encoding='utf-8')) if TILASTO_PATH.exists() else {
  "udisc":{"rounds":428},"metrix":{"43119":702,"44010":598,"44763":170},
  "total":1130
}

def fetch_metrix_detailed(cid):
    try:
        r=requests.get(f"https://discgolfmetrix.com/course/{cid}", headers=HEADERS, timeout=15)
        if r.status_code!=200:
            return None
        html=r.text
        # Yritä erotella harjoitus vs kilpailu
        # Metrix: /course/43119/results?type=practice ja ?type=competition
        practice_total=0
        competition_total=0
        
        # Hae practice sivulta
        try:
            rp=requests.get(f"https://discgolfmetrix.com/course/{cid}?type=practice", headers=HEADERS, timeout=10)
            m=re.search(r'(\d+)\s*(?:results|tulosta)', rp.text, re.I)
            if m: practice_total=int(m.group(1))
        except: pass
        
        try:
            rc=requests.get(f"https://discgolfmetrix.com/course/{cid}?type=competition", headers=HEADERS, timeout=10)
            m=re.search(r'(\d+)\s*(?:results|tulosta)', rc.text, re.I)
            if m: competition_total=int(m.group(1))
        except: pass
        
        # Jos ei erottelua, käytä total ja oletus 99% harjoitusta (Luoma-aho)
        if practice_total==0 and competition_total==0:
            m=re.search(r'(\d+)\s*(?:results|tulosta)', html, re.I)
            total=int(m.group(1)) if m else old['metrix'].get(str(cid),0)
            # Luoma-ahossa kilpailuja 0-5 kpl, loput harjoitusta
            competition_total=0
            practice_total=total
        
        total=practice_total+competition_total
        return {"total":total,"harjoitus":practice_total,"kilpailu":competition_total,"practice":practice_total,"competition":competition_total}
    except Exception as e:
        print(f"{cid} fail {e}")
        return None

new={}
for cid in ["43119","44010","44763"]:
    f=fetch_metrix_detailed(cid)
    if f:
        new[cid]=f
        print(f"{cid} DYNAAMINEN HAKU: harjoitus {f['harjoitus']} + kilpailu {f['kilpailu']} = {f['total']} (harjoitus+kisa)")
    else:
        prev=old['metrix'].get(cid) or old['metrix'].get(str(cid)) or 0
        if isinstance(prev, dict):
            new[cid]=prev
        else:
            new[cid]={"total":prev,"harjoitus":prev,"kilpailu":0,"practice":prev,"competition":0}
        print(f"{cid} SAILYTETTY AIEMPI harjoitus {new[cid]['harjoitus']} kilpailu {new[cid]['kilpailu']}")

# Paivita tilasto - HAKU ON HARJOITUS + KILPAILU
result=old.copy()
result['metrix']={k:v['total'] for k,v in new.items()}
result['metrix_detailed']=new
result['total']= (old['udisc']['rounds'] if isinstance(old['udisc'],dict) else 428) + new['43119']['total']
result['total_kaikki']= (old['udisc']['rounds'] if isinstance(old['udisc'],dict) else 428) + sum(v['total'] for v in new.values())
result['harjoituskierrokset_yhteensa']=sum(v['harjoitus'] for v in new.values())  # 1470
result['kilpailukierrokset_yhteensa']=sum(v['kilpailu'] for v in new.values())  # 0
result['haku_periaate']="HAKU ON harjoituskierrokset + kilpailukierrokset = total, erikseen näytetään"
result['updated']=datetime.datetime.now().isoformat()

TILASTO_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\nHAKU: harjoitus {result['harjoituskierrokset_yhteensa']} + kilpailu {result['kilpailukierrokset_yhteensa']} = {sum(v['total'] for v in new.values())} Metrix")
