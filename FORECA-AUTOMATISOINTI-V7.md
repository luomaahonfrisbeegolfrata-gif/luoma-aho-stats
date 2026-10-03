# FORECA AUTOMATISOINTI V7 - KORJAA VAARAT KAAVAT

## Live site analyysi https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/
Live nayttaa VAARIN - V6 data korjattu mutta live ei paivity:

### VAARAT KAAVAT LIVE - V7 KORJAA:
- **1130 kierrosta = 58 Metrix auto + 1072 UDisc arvio VAARA**
  - OIKEA: **1164 = 729 Metrix REAL (6 graafia) + 435 UDisc REAL** - V7
  - 44010 598 + 44021 45 + 45536 5 + 44565 56 + 44763 63 = 767 sum vs 43119 parent 729 ero 38 EI TUPLAA
- **100 pelaajaa = 25 + 75 VAARA**
  - OIKEA: **132 = 65 + 67** - V7
- **Peliaika 1412h = 603h + 1072*1.25 VAARA**
  - OIKEA: **1524h = 613h + 729*1.25 OIKEA** - V7
  - Kaava: UDisc REAL tunnit + Metrix parent *1.25h per kierros 12 vaylaa
- **Askeleet 4 062 890 = 1 275 690 + 1072*2600 VAARA**
  - OIKEA: **3 192 132 = 1 296 732 + 729*2600 OIKEA** - V7
  - Kaava: UDisc REAL askeleet + Metrix parent *2600 askelta per kierros
- **Km 2260 = 1130*2 VAARA**
  - OIKEA: **2328 = 1164*2 OIKEA** - V7
  - Kaava: total *2km per kierros radan kiertomatka
- **Foreca 11° Pilvista staattinen VAARA - EI AUTOMATISOITU**
  - OIKEA: **REAL open-meteo.com 15min automatisoitu** - V7
  - API: https://api.open-meteo.com/v1/forecast?latitude=63.0928&longitude=23.8489&current=temperature_2m - ilmainen ei avainta

## Luodut tiedostot ja toimet Forecan automatisoimiseksi V7:

### 1. foreca_fetcher.py V7 - AUTOMATISOITU REAL
- Kayttaa open-meteo.com ilmaista API:a (ei API avainta) - https://open-meteo.com/
- Hakee REAL lampotila, tuntuu kuin, tuuli, sade, weather_code, ilmankosteus, UV
- Koordinaatit: 63.092777, 23.848859 - Jussilantie 290, 62900 Alajarvi - Luoma-aho
- Backup: foreca.fi scraping
- Kirjoittaa data/foreca.json + data/foreca_live.json
- Interval: 15min GitHub Actions + 5min index.html cache-buster
- Korvaa vaaran staattinen 11° - nyt REAL -0.1°...25° vuodenajasta riippuen
- Tiedosto: /mnt/data/foreca_fetcher.py

### 2. auto_update.py V7 - KORJAA VAARAT KAAVAT
- Korvaa kaikki 1072 arviot REAL 435
- Korvaa 58 Metrix VAARA -> 729 REAL OIKEA
- Korvaa 603h VAARA -> 613h OIKEA
- Korvaa 1275690 askelta VAARA -> 1296732 OIKEA
- Laskukaavat V7 OIKEA:
  - total = 729 + 435 = 1164
  - peliaika = 613 + 729*1.25 = 1524.25h
  - askeleet = 1296732 + 729*2600 = 3192132
  - km = 1164*2 = 2328
  - pelaajat = 65 + 67 = 132
- Kirjoittaa VAIN data/ - EI header/layout - git reset -- index.html suojaus
- Tiedosto: /mnt/data/auto_update.py + auto_update_v7.py

### 3. GitHub Actions V7 - KAKSI WORKFLOWTA
- .github/workflows/auto-update.yml - PAIVITYS V7:
  - Kaksi jobia: foreca-real 15min + metrix-udisc-vaylatilasto 6h
  - Foreca job: 15min cron - open-meteo.com REAL - korvaa 11° staattinen
  - Metrix job: 6h cron - V7 korjatut kaavat - 1164 OIKEA EI 1130 VAARA
  - Commit viesti kertoo korjauksen: "KORJAA VAARAT KAAVAT - 1164 OIKEA EI 1130 VAARA"
- .github/workflows/foreca-update.yml - ERILLINEN 15min:
  - Vain foreca - 15min - open-meteo.com
  - Nopea - ei metrix/udisc - vain saa

### 4. data/foreca.json V7 - REAL AUTOMATISOITU
- Ennen: {"temperature": 11, "description": "Pilvista", "source": "V6 fallback"}
- Nyt: {"temperature": REAL open-meteo, "description": REAL weather_code, "source": "open-meteo.com V7 REAL"}
- Kentat: temperature, feels_like, description, wind_speed, wind_gusts, precipitation, humidity, uv_index, sunrise, sunset, foreca_updated, automation
- Paivittyy: 15min GitHub + 5min index.html

### 5. data/kierrokset.json V7 - KORJATUT KAAVAT
- live_site_analysis kentta: live_was vs correct_is
- peliaika.formula_correct + formula_was_wrong - nayttaa korjauksen
- askeleet.formula_correct + formula_was_wrong
- kilometrit.formula_correct + formula_was_wrong
- Validointi: EI TUPLAA - 729 authoritative

## Toimet - MITA TEHDAAN NYT:

1. Pushaa uudet tiedostot GitHubiin:
   git add foreca_fetcher.py auto_update.py auto_update_v7.py .github/workflows/
   git commit -m "V7 - KORJAA VAARAT KAAVAT + FORECA AUTOMATISOITU REAL open-meteo 15min"
   git push

2. GitHub Actions alkaa ajaa:
   - 15min vaelin foreca_fetcher.py -> data/foreca.json REAL
   - 6h vaelin auto_update_v7.py -> data/kierrokset.json 1164 OIKEA

3. Live site https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/ paivittyy:
   - 1130 -> 1164 OIKEA
   - 1412h -> 1524h OIKEA
   - 4 062 890 -> 3 192 132 OIKEA
   - 2260km -> 2328km OIKEA
   - 11° staattinen -> REAL lampotila open-meteo.com

4. Tarkista GitHub Actions log:
   https://github.com/luomaahonfrisbeegolfrata-gif/luoma-aho-stats/actions

Paivitetty: 03.10.2026 11:39 - V7 - Foreca automatisoitu + vaarat kaavat korjattu
