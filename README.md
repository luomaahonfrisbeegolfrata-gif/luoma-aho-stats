# Luoma-ahon Frisbeegolfrata - Stats - TÄYDELLINEN PAKETTI GITHUBIIN

## Uusi data 29.9.2026 (korjattu, ei tuplalaskentaa)

### Metrix 43119 sisältää KAIKKIEN layouttien kierrosmäärät
- Metrix 43119: 702 kierrosta (588 harjoitus + 114 kilpailu) - KAIKKI layoutit
- Metrix 44010: 595 kierrosta (544+51) - SISÄLTYY jo 43119, ei lisätä erikseen
- Metrix 44763: 170 kierrosta (37+133) - SISÄLTYY jo 43119, ei lisätä erikseen
- UDisc: 428 kierrosta, 67 uniikkia, 603h, 1,275,690 askelta (Elinikäiset 28.9.2026 klo 5.03)

### Yhdistetty OIKEIN (ei tuplata):
- **Tuloskierrokset:** 428 + 702 = **1130** (aiempi 1895 oli väärä: 428+595+170+702 tuplasi)
- **Uniikit:** ~100 (UDisc 67 + Metrix 43119 ~60 - päällekkäisyyksiä)
- **Peliaika:** 603h + 702×1.25h = **1481h**
- **Askelmäärä:** 1,275,690 + 702×2600 (2km×1300) = **3,100,890**
- **Kilometrit:** 1130×2km=**2260km** (käyttäjä 2km) / 1130×2.5km=**2825km** (UDisc 1.6mi)

### Top 5 OIKEAT:
- **UDisc Leaderboard (kuva.png):** @kantanen8 35 (4.7.2026), @valkoparta 36 (6.7.2026), @mattiasss 36 (19.8.2026), @dashyy 38, @itkonenjere 38
- **Metrix 44010 Par 41:** Toni Luoma-aho +1 (42), Eino Vistiaho +2 (43), Benjamin Turja +3 (44), Toni Luoma-aho +4 (45), Jari Vistiaho +5 (46)
- **Metrix 44763 Par 82:** Timo Alalantela E (82), Aapo Penttilä +1 (83), Eevert Väkeväinen +3 (85), Daniel Turja +5 (87), Eero Tuohimaa +6 (88)

## Header Lukittu - Sääntö 1
Järjestys oikealta vasemmalle: **ratamestari -> fgr -> ig -> udisc -> yt -> rata-kuvat -> loytokiekot -> parkdly (väyläopasteet) -> metrix -> gmaps**
Vasen: **L-A FRIBA LUOMA-AHO** (oma logo, lihaksikas mies frisbeellä, musta badge)

### Uudet logot tässä zipissä:
- Vasen: `logot/luoma-aho-logo.jpg` = L-A FRIBA LUOMA-AHO (sun oma luoma, ei henkilökuva - artifact filtteri blokkasi, mutta GitHubissa toimii)
- Oikea reuna: `ratamestari-logo.png` = FRISBEEGOLF RATAMESTARI (vihreä kori + kuuset + kruunu)
- `fgr-logo.png` = frisbeegolfradat.fi sininen puhekupla
- `ig-logo.png` = Instagram gradient
- `yt-logo.png` = YouTube
- `rata-kuvat-icon.jpg` = metsä tee pad aurinko
- `loytokiekot-logo.png` = LÖYTÖKIEKOT musta teksti
- `metrix-logo.png` = DISC GOLF METRIX oranssi
- `udisc-logo.png` = UDisc oranssi U
- `parkdly-logo.png` = parkdly vihreä (väyläopasteet)
- `gmaps-logo.jpg` = Google Maps uusi värikäs pin (punainen-violetti-sininen-vihreä-keltainen liukuväri) - UUSI 29.9.2026

## GitHubiin siirto - OHJE

### 1. Lataa ja pura tämä zip
Pura kaikki tiedostot koneellesi

### 2. Clone repo
```bash
git clone https://github.com/luomaahonfrisbeegolfrata-gif/luoma-aho-stats.git
cd luoma-aho-stats
```

### 3. Kopioi tiedostot
Kopioi tämän zipin kaikki tiedostot repoon (korvaa vanhat):
- index.html (lukittu header + Ratainfo + 1130 + Väylätilasto)
- data/ (stats.json 1130, vaylatilasto.json, hole-scores.csv)
- logot/ (14 logoa, uudet mukana: L-A FRIBA, RATAMESTARI, Google Maps pin)
- url/urls.json (lukittu järjestys)
- js/update.js
- HEADER_LOCKED.md

### 4. Push GitHubiin
```bash
git add .
git commit -m "feat: täydellinen korjattu - 1130 kierrosta (43119 kaikki, ei tuplata 1895), Top5 @kantanen8 35, uudet logot L-A FRIBA vasen + RATAMESTARI oikea + Google Maps pin, header lukittu"
git push
```

### 5. Ota GitHub Pages päälle
- GitHub repo → Settings → Pages
- Source: Deploy from branch → main / root
- Save
- Sivu aukeaa: https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/

### 6. Automaatio
- .github/workflows/update.yml ajaa 5min välein
- js/update.js hakee Metrix 43119 (KAIKKI, sisältää 44010 ja 44763) + UDisc + Foreca
- data/stats.json päivittyy automaattisesti
- Sivusto lataa 1s, päivittyy 5min välein

## Tiedostot tässä zipissä
- index.html (lukittu header, Ratainfo 6 korttia, Top5 4 korttia, Väylätilasto alin)
- data/stats.json (1130 OIKEIN, ei tuplata, Top5 @kantanen8 35)
- data/vaylatilasto.json (12 väylää, värit vihreä helpoimmat 3, keltainen, oranssi, punainen vaikeimmat 3, pituus ylimpänä)
- data/hole-scores.csv (UDisc)
- logot/ (14 tiedostoa, uudet logot)
- url/urls.json (lukittu järjestys ratamestari->fgr->ig->udisc->yt->rata-kuvat->loytokiekot->parkdly->metrix->gmaps)
- js/update.js (automaatio 5min)
- HEADER_LOCKED.md (header lukittu 28.9.2026)

Valmis GitHubiin!
