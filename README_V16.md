# V16 FINAL PUHAS - KAIKKI KORJAUKSET - HEADER/LAYOUT/KORTIT LUKITTU

## Toimiva kuten pitää - B avg-par

- Difficulty: [8,5,9,10,6,2,4,11,7,1,3,12] = avg-par logiikka
  - 10 vaikein +1.20, 6 +1.18, 11 +1.15 = punainen 1-3
  - 7 +0.79, 2 +0.77, 5 +0.55 = oranssi 4-6
  - 9 +0.53, 1 +0.45, 3 +0.45 = keltainen 7-9
  - 4 +0.42, 8 +0.33, 12 +0.23 = vihreä 10-12
- Avg värit: 3 pienintä vihreä (8,4,3), 3 keltainen (5,2,7), 3 oranssi (6,10,12), 3 suurinta punainen (1,9,11)
- Kierrokset: 1164 = 729+435 OIKEA
- Header lukittu, Layout lukittu, Kortit lukittu

## Poistetut turhat tiedostot
- data/vaylatilasto_manual.json
- data/foreca.json
- data/udisc_top10.json
- data/vaylatilasto_V*.png/json
- auto_update_v*.py
- vaylatilasto_fetcher_v*.py
- .github/workflows/auto-update.yml (vanha)

## Ajo GitHubissa
- vaylatilasto.yml 6h
- kierrokset.yml 12h
- udisc.yml 8h
- saa.yml 15min

Kaikki sisältää retry 3x + validointi + status.json
