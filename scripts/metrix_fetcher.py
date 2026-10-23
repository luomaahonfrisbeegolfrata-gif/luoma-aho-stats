
import requests, json, pathlib
from bs4 import BeautifulSoup
BASE=pathlib.Path("data")
BASE.mkdir(exist_ok=True)
for cid in [44010,44763]:
    url=f"https://discgolfmetrix.com/course/{cid}"
    try:
        r=requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        soup=BeautifulSoup(r.text,"html.parser")
        top=[]
        for tr in soup.select("table tr")[:12]:
            tds=tr.find_all("td")
            if len(tds)>=2:
                top.append({"name":tds[0].get_text(strip=True),"total":tds[1].get_text(strip=True)})
        (BASE/f"metrix_{cid}.json").write_text(json.dumps({"course_id":cid,"top10":top[:10]}, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"{cid} OK")
    except Exception as e:
        print(f"{cid} fail {e}")
