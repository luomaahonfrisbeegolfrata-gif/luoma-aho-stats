import json, pathlib, re, requests, datetime
PAR=41
HEADERS={"User-Agent":"Luoma-aho PAR41"}
TOP5_PATH=pathlib.Path('data/top5.json')
old=json.loads(TOP5_PATH.read_text(encoding='utf-8')) if TOP5_PATH.exists() else {}

def calc_par_diff(total):
    # PAR 41: yli 41 = +, alle 41 = -
    # 42 -> +1, 45 -> +4, 40 -> -1, 39 -> -2, 41 -> 0 = E
    diff=total-PAR
    if diff>0: return diff, f"+{diff}", f"{total} (+{diff})"
    elif diff<0: return diff, f"{diff}", f"{total} ({diff})"  # -2
    else: return 0, "E", f"{total} (E)"

def fetch_best5(cid):
    try:
        r=requests.get(f"https://discgolfmetrix.com/course/{cid}", headers=HEADERS, timeout=20)
        if r.status_code!=200: return None
        html=r.text
        best={}
        for m in re.finditer(r'<tr[^>]*>.*?<td[^>]*>([A-ZÄÖÅa-zäöå \-]{3,30})</td>.*?<td[^>]*>([+-]?\d+|E)</td>.*?<td[^>]*>(\d{2})</td>', html, re.I|re.S):
            name=m.group(1).strip()
            total=int(m.group(3))
            if total<30 or total>80 or 'Pelaaja' in name or 'Par' in name: continue
            diff,score,display=calc_par_diff(total)
            # Jos diff 41 yli = +, alle = -
            if name.lower() not in best or diff<best[name.lower()][0]:
                best[name.lower()]={"player":name,"total":total,"diff":diff,"score":score,"display":display,"sort":diff}
        res=sorted(best.values(), key=lambda x: x['diff'])[:5]
        return [{"rank":i+1,**r} for i,r in enumerate(res)] if res else None
    except Exception as e:
        print(f"{cid} {e}")
        return None

new={}
for cid,key in [("44010","metrix_44010"),("44763","metrix_44763")]:
    real=fetch_best5(cid)
    if real:
        new[key]={"top5":real,"par":PAR,"updated":datetime.datetime.now().isoformat(),"logic":"PAR 41: yli 41 = +, alle 41 = -, 42=+1, 39=-2"}
    else:
        prev=old.get(key)
        if prev and prev.get('top5'): new[key]=prev
        else:
            new[key]={"top5":[
                {"rank":1,"player":"Esimerkki 1","total":42,"diff":1,"score":"+1","display":"42 (+1)","sort":1},
                {"rank":2,"player":"Esimerkki 2","total":43,"diff":2,"score":"+2","display":"43 (+2)","sort":2},
                {"rank":3,"player":"Esimerkki 3","total":44,"diff":3,"score":"+3","display":"44 (+3)","sort":3},
                {"rank":4,"player":"Esimerkki 4","total":45,"diff":4,"score":"+4","display":"45 (+4)","sort":4},
                {"rank":5,"player":"Esimerkki 5","total":46,"diff":5,"score":"+5","display":"46 (+5)","sort":5},
            ],"par":PAR}

# UDisc sama PAR 41 logiikka
udisc_prev=old.get('udisc',{}).get('top5',[])
if udisc_prev:
    cleaned=[]
    for r in udisc_prev:
        if 'Pelaaja' in r.get('player',''): continue
        total=r.get('total')
        if total:
            diff,score,display=calc_par_diff(total)
            cleaned.append({"player":r['player'],"total":total,"diff":diff,"score":score,"display":display,"sort":diff})
    cleaned=sorted(cleaned, key=lambda x: x['diff'])[:5]
    new['udisc']={"top5":[{"rank":i+1,**r} for i,r in enumerate(cleaned)],"par":PAR} if cleaned else old.get('udisc',{"top5":[]})
else:
    new['udisc']=old.get('udisc',{"top5":[]})

TOP5_PATH.write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"PAR {PAR}: 42 -> +1 (yli), 39 -> -2 (alle), 41 -> E")
