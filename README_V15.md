# V15 - KAIKKI KORJAUKSET - HEADER/ LAYOUT/ KORTIT LUKITTU

## Mitä korjattu (ei koske header/layout/korttien koko/sijainti)

### 1. Väylätilasto difficulty V14 B -> V15
- Vanha: kovakoodattu [4,8,5,3,7,11,9,2,6,12,10,1] VÄÄRIN
- Uusi: calculate_difficulty_from_avg(avg, par) -> avg-par = [8,5,9,10,6,2,4,11,7,1,3,12] OIKEA
- Värit: 1-3 punainen, 4-6 oranssi, 7-9 keltainen, 10-12 vihreä - dynaaminen

### 2. Automatiikka
- retry 3x + backoff + jitter
- schema validointi: difficulty 1-12 permutaatio, avg 2.0-8.0, totals 500-5000
- fallback viimeiseen toimivaan
- status.json monitoring

### 3. Erilliset workflowt
- vaylatilasto.yml 6h
- kierrokset.yml 12h
- udisc.yml 8h
- saa.yml 15min (open-meteo)

### 4. Laskukaavat V7/V15 säilytetty
- 1164 = 729 + 435 OIKEA (ei 1130)
- 1524h = 613 + 729*1.25
- 3 192 132 askelta
- 2328 km

### 5. Testit
- tests/test_difficulty.py

### Lukitut
- Header lukittu
- Layout lukittu
- Korttien koko ja sijainti lukittu

### Asennus
cp -r V15_KORJATTU_PAKETTI/* .
python -m pytest tests/
python vaylatilasto_fetcher.py
