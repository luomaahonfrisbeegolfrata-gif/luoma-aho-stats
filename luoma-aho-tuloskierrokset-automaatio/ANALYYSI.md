# ANALYYSI - UDisc & Metrix tuloskierrokset

Lähde: https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/

## Nykyinen tila 29.9.2026 klo 08:12
- UDisc 428 + Metrix 43119 702 = 1130 OIKEIN
- Ei tuplata 1895 (44010 595 + 44763 170 sisältyy jo 43119)
- Metrix 43119: 702 KAIKKI layoutit (588 harjoitus + 114 kilpailu)
- UDisc: 428 kierrosta, 67 uniikkia, 603h, 1,275,690 askelta
- Uniikit: 100 (67 + ~60 - päällekkäisyydet)
- Peliaika: 1481h (603 + 702×1.25)
- Askeleet: 3,100,890 (1,275,690 + 702×2600)
- Km: 2260 km (1130×2km) / 2825 km (UDisc 1.6mi×2.5km)

## Väylätilasto
- Pohja: Metrix 43119 702 + UDisc 428
- Pituudet: 125,103,72,57,94,96,103,80,116,85,197,120 = 1248m
- Par: 4,3,3,3,3,3,3,3,4,3,5,4 = 41
- Värit: helpoin 3 vihreä (4,12,8), keskitaso keltainen (5,1,3), vaativa oranssi (2,9,7), vaikein punainen (10,6,11)
- Avg: 4.45,3.77,3.45,3.42,3.55,4.18,3.79,3.33,4.53,4.2,6.15,4.23 = 49.05

## Automaatio
1. GitHub 5min: .github/workflows/auto-5min.yml cron */5 * * * *
   - Ajaa scraper.py
   - Päivittää data/tilasto.json + data/ratatilasto.json
   - Generoi vaylatilasto.png musta pohja + Pituus rivi Väylä ja Par väliin

2. Frontend 1s: js/tilasto.js + js/ratatilasto.js
   - setInterval 1000ms
   - Fetch data/*.json + PNG?t=Date.now()
   - Näyttää sivun alaosassa <div id="vaylatilasto-auto">

3. Logot header: urls.json määrittää 10 logoa, vasen L-A FRIBA lukittu 28.9.2026

## Top5
- UDisc @kantanen8 35 (4.7.2026)
- Metrix Toni Luoma-aho +1 (42) ja Timo Alalantela E (82) 2 kierrosta

## Korjaukset
- 29.9.2026: Automaatio korjattu + Header lukittu Sääntö 1 + Uudet logot
