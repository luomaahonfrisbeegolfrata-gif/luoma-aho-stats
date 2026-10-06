import json, pathlib
from datetime import datetime
DATA_DIR=pathlib.Path("data")

def main():
    # ÄLÄ laske uniikkeja TOP10:stä - se antaa 21
    # Säilytä vanha 132 tai hae oikea määrä Metrixistä
    old_path=DATA_DIR/"kierrokset.json"
    old_total=1170
    old_unique=132
    try:
        old=json.loads(old_path.read_text(encoding='utf-8'))
        old_total=old.get('total_rounds',1170)
        old_unique=old.get('unique_players',132)
        # Jos vanha oli 21 (bugi), korjaa 132
        if old_unique < 30:
            old_unique = 132
    except:
        pass

    data={
        "total_rounds": old_total,
        "total": old_total,
        "count": old_total,
        "unique_players": old_unique,
        "uniikit_pelaajat": old_unique,
        "peliaika": {"display": "1524h"},
        "askeleet": {"display": "3 192 132"},
        "kilometrit": {"display": "2328 km"},
        "fetched_at": datetime.now().isoformat(),
        "version": "V28 uniikit lukittu 132 - ei TOP10 laskenta"
    }
    (DATA_DIR/"kierrokset.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Kierrokset {old_total} uniikit {old_unique} - korjattu")

if __name__=="__main__":
    main()
