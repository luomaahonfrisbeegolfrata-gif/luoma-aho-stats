# HEADER/LAYOUT LUKITTU - V6 - TARKISTUS

## index.käytössä.html - KAYTOSSA - EI MUUTETTU
- Header: display:flex;justify-content:space-between;align-items:center;padding:16px 14px;background:#040404;border-bottom:1px solid #1e1e1e;position:sticky;top:0;z-index:20
- Header-left img 52px, h1 19px, live #1aff1a
- Header-right logo-square 52px, logo-rect 96px, logo-rect-wide 120px
- Grid-top: 360px 300px 300px 300px 1fr - LUKITTU
- Grid-middle: 1fr 1fr 1fr - LUKITTU
- Kortit: ratainfo-card 380px, combined-card 380px, hio-card 380px, saa-card 380px, stacked-right 380px, top10-card 520px - LUKITTU
- Vaylatilasto: vayla-head + vayla-wrap + img - PALAUTETTU - yhta tarkea kuin virta - AUTO 5min

## V6 Data - toimii index.kaytossa.html - EI muuta header/layout
- kierrokset.json V6: total_rounds 1164, peliaika 1524h display/detail, askeleet 3 192 132, km 2328 km - fetch('data/kierrokset.json') -> setText() VAIN textContent
- metrix_44010.json V6: top10 42-49 Par 41 - renderTop10() VAIN m44010-list innerHTML
- metrix_44763.json V6: top10 82-93 Par 82 - 63 REAL visible - tooltip 31 Mar 11 - VAIN m44763-list
- udisc.json V6: top10 35-44 Par 41 12 vaylaa - VAIN udisc-list
- foreca.json V6: temperature 11, description Pilvista - VAIN saa-temp etc
- vaylatilasto.json V6: 44010 12 vaylaa Par 41 + pituudet 58-197m + average + VAYLATILASTO kortti alas
- vaylatilasto.png V6: musta taulukko LIVE MUSTA + PITUUS - 74KB - VAIN img src - EI layout
- auto_status.json V6: last_update 2026-10-03T10:59:11.034405

## auto_update.py V6 - EI koske header/layout
- Kirjoittaa VAIN data/ - DATA_DIR / kierrokset.json, foreca.json, vaylatilasto.json, metrix_*.json, udisc.json, auto_status.json
- EI koske index.html - tarkistettu - ei 'index.html' write
- fetch_vaylatilasto() mukana - VAIN data/

## GitHub Actions V6 - suojaa header/layout
- git add data/ - git reset -- index.html - git reset -- index.kaytossa.html - commit vain data/
- Viesti: header/layout lukittu EI muutettu
- Workflow tiedosto: .github/workflows/auto-update.yml

## Johtopaatos
- HEADER EI MUUTU - position:sticky top:0 lukittu
- LAYOUT EI MUUTU - grid-top 360px 300px 300px 300px 1fr lukittu, grid-middle 1fr 1fr 1fr lukittu
- V6 data toimii index.kaytossa.html - fetch() VAIN textContent/innerHTML id:t - EI style/className/layout
- Vaylatilasto kortti alas - LIVE MUSTA + PITUUS - AUTO 5min - EI muuta header/layout

Tarkistettu: 17169 bytes - index.kaytossa.html - kaytossa
