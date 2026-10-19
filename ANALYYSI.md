# Luoma-aho stats – analyysi 19.10.2026

## Kriittiset virheet (korjattu)
1. **build_stats.py olisi ylikirjoittanut julkaistut luvut väärillä.** Vanha skripti laski väyläkeskiarvot configin `layouts.avg`-arvoista (väyläsumma 50.61, joka on config-tiedoston "virheellinen v3.0" -luku) ja jakauman configin vanhasta `distribution`-taulukosta (väyläkohtaiset summat 1143–1228 eikä 1221). Julkaistu V4.0 (48.74) oli käsin tehty, eikä skripti tuottanut sitä. Uusi skripti toteuttaa julkaistun kaavan `(Metrix_avg*768 + UDisc_avg*453)/1221` ja tuottaa täsmälleen julkaistut väylätilaston luvut.
2. **Peliaika/askeleet/km:** vanha skripti olisi muuttanut luvut 1630 h / 3 440 589 / 2508 km → 1892 h / 4 038 414 / 2944 km. Julkaistut arvot ovat käsin lukittuja (`config.manual_totals`), joten ne säilyvät. Laskettu vaihtoehto näkyy `kierrokset.json`:n kentässä `estimated.calculated_alternative`. **Päätä, kumpi on oikea** (1630 h vastaa noin 719 Metrix-kierrosta/UDisc-vauhdilla, config sanoo 907,5).
3. **Sivu ei hakenut dataa latautuessaan.** `refreshAll()` kutsuttiin vain 5 min ajastimella ja välilehden vaihdolla, joten uusi kävijä näki ensin kovakoodatun varadatan (mm. vanha Metrix-only 49.55 ja keksityt tiedotteet) jopa 5 min ajan. Nyt haku tehdään heti.
4. **Skriptin `Path`-virhe:** `main()` käytti `Path.cwd()` vaikka vain `pathlib` oli importattu → NameError aina kun udisc.json puuttui.
5. **XSS:** nimet Metrixistä/UDiscistä ja tiedotteet menivät `innerHTML`:iin escapettamatta. Lisätty `esc()`.
6. **Par ja pituus kovakoodattu** (`LOCKED_PAR`, `LOCKED_PITUUS`) ja ylikirjoittivat JSONin, vaikka kommentti lupasi config-ohjauksen. Nyt data ohjaa, kovakoodi on vain varalla (tärkeää, jos tuotteistat muille radoille).

## Pienemmät korjaukset
- Top10: tasapisteet saavat saman sijan (UDisc-data sanoi 2./2., sivu näytti 2./3.); "+0" näkyy "E" (oli punainen +0).
- Kilpailun tilanne -badge näytti 0, vaikka 1 ilmoittautunut.
- Käyttäjän valitsema kilpailu ei enää nollaudu 5 min välein.
- "⭐ 0.0/5 (0 arviota)" → "⭐ –/5"; Difficulty-sarakkeen turha summa "78" → "-".
- Päivämäärä 07.11.2026, tekstivirheet (mäntymetsämaastossa, huippukuntoinen, teknisyydessä, Väylä).
- config.json: kurssin nimestä poistettu "V4.0 REAL 48.74", turhat/ristiriitaiset kentät poistettu, `metrix_avg_per_hole` ja `manual_totals` lisätty.

## Huomioita, joita EN korjannut (tarvitsevat päätöksesi)
- **Birdie = 45 viidellä väylällä (2, 5, 6, 7, 10)** vaikka UDisc-prosentit eroavat (3–4 %). Näyttää paikkamerkiltä. Tarkista oikeat luvut.
- **Metrixin automaattiset laskurit ovat katkaistu 30 tulokseen** (`total_results: 30`, `metrix_43119.json` kertoo 60 kierrosta vs. käsin 768). Älä käytä niitä tilastoihin; käsin ylläpidetyt luvut ovat oikeampia.
- **Metrix-kierrosten haku (metrix_44010/44763.json) ei kuulunut uploadiin** – en voi arvioida sitä. Sama koskee `update.yml`:ää ja `palkintolaskuri.html`:ää.
- **Pakkassarja "4 parasta 7:stä":** metrix_competitions.py ei laske sarjan kokonaistilannetta itse. Varmista 7.11. mennessä, palauttaako Metrix API sarjan yhteistuloksen; muuten pitää toteuttaa (säännöt: tasapisteet, alle 4 kisaa pelanneet).
- **Vieraskirja ei tallenna mitään:** vieras näkee viestinsä sivulla, mutta se katoaa latauksessa ja ylläpitäjän pitää liittää JSON käsin GitHubiin. Vieraalle näyttää, että viesti on julkaistu. Tarvitaan lomakepalvelu (esim. Formspree) tai selkeä teksti.
- **tiedotteet_fetcher.py** kirjoittaa tiedoston joka ajolla uudelleen (`fetched_at`) → turhia committeja. Rikkinäisen JSONin tilalle kirjoitetaan "Tervetuloa!"-oletus.
- **"Kierros noin 1.5 km, peliaika noin tunti"** ei vastaa dataa: UDisc-keskiarvo on 1,39 h ja 2,17 km/kierros (askeleet × 0,729 m).
- Hole in one -nimet ovat kovakoodattuna HTML:ssä, eikä configissa.
- Tuplalaskenta: sama kierros voi olla sekä Metrixissä että UDiscissä (1221 = 768 + 453 summataan).

## update.yml (workflow)
- **Ajoi vanhaa `metrix_tilanne_fetcher.py`:tä**, jonka `metrix_competitions.py` korvaa. Puuttuvan tiedoston ohitus oli hiljainen, joten kilpailudata ei välttämättä ole päivittynyt automaattisesti lainkaan (tiedostot ovat "Käsin ylläpidetty"). Nyt ajetaan `metrix_competitions.py`, ja puuttuva skripti kaataa ajon näkyvästi.
- **`metrix_competitions.py` kirjoitti `updated`-leiman joka ajolla** → commit 48 kertaa vuorokaudessa ja Pages-uudelleenjulkaisu joka kerta. Nyt kirjoitetaan vain, jos sisältö muuttui (testattu). Elinmerkki `status.json` 3 h → 24 h.
- `build_stats.py` ei ollut workflow'ssa lainkaan; lisätty (tuottaa nyt identtisen datan, ei turhia committeja). Poistettu tyhjä "Keep kierrokset locked" -vaihe ja `lxml`.
- Commit: haaran nimi `main` ei ole enää kovakoodattu.
- **Riski:** GitHub voi poistaa ajastetun workflow'n käytöstä, jos julkisessa repossa ei ole toimintaa 60 päivään. Elinmerkki-commit 24 h välein on tätä varten; jos muutoksia ei tule, vilkaise Actions-välilehteä silloin tällöin.
- `user_agent` configissa on yhä paikkamerkki "vaihda tähän yhteystieto". Kirjoita siihen oma sähköposti Metrixin API:a varten.

## Metrix-skriptit
- **metrix_tilanne_fetcher.py (vanha) – poista repostasi.** Nimestään huolimatta se hakee vain kilpailulistan eikä kirjoita `kilpailu_tilanne.json`:ia. Se olisi ylikirjoittanut käsin ylläpidetyn `metrix_kilpailut.json`:n huonommalla versiolla: päivämäärät tyhjiä (`"date": ""`), sarjarivi (`isSeries`) puuttuu, pelaajamäärät 0. `metrix_competitions.py` korvaa sen.
- **metrix_fetcher.py kirjoitti `fetched_at`-leiman joka ajolla** kolmeen tiedostoon → commit 48 kertaa vuorokaudessa (tämä oli suurempi syy kuin kilpailuskripti). Nyt kirjoitetaan vain muutokset.
- **Epäonnistunut haku nollasi tiedot ja näytti tuoreelta:** `total_results: 0` ja uusi `fetched_at` kirjoitettiin vanhan päälle. Nyt epäonnistuessa vanha tiedosto jää ennalleen ja ajo päättyy virhekoodiin (vaihe on `continue-on-error`, joten näet keltaisen varoituksen etkä menetä muuta dataa).
- Parsittava "Top results" -taulukko rajaa tulokset 30 riviin, siksi `total_results`/`unique_players` ovat aina ≤30. Älä käytä niitä tilastoissa. Top10 vaatii vähintään 10 eri pelaajaa 30 rivin sisällä; 44010:llä niitä on vain 11, joten lista voi lyhentyä, jos yksi pelaaja täyttää taulukkoa.
- Skripti esiintyy selaimena (Chrome-User-Agent) ja lukee HTML:ää. Tarkista Metrixin ehdot; `metrix_competitions.py` käyttää virallista API:a ja rehellistä User-Agentia.

## Palkintolaskuri
- **Bugi: 3. sijalle maksettiin palkinto, vaikka pelaajia oli alle 3.** 2 × 5 € → 1. 4,5 €, 2. 2 €, **3. 1,5 €**. Nyt jako tehdään vain olemassa oleville sijoille suhteessa 50/30/20 (2 × 5 €: 1. 5 €, 2. 3 €, järjestäjälle 2 €), ja puuttuvat sijat näkyvät "–". **Päätä sääntö:** haluatko alle 3 hengen kisoissa jotain muuta (esim. ei palkintoja)?
- **Näytetty potti ei täsmännyt maksuihin.** "Potti 80 %" näytti pyöristämättömän summan (esim. 3 × 2 €: 4,8 €), mutta palkinnot summautuivat 4,5 €:oon. Nyt rivillä on todellinen palkintopotti, ja palkintopotti + järjestäjä = kerätty summa.
- **Mobiili:** lomakekortin `overflow:hidden` leikkasi kentät pienellä näytöllä tai kun näppäimistö on auki. Nyt rullattava.
- Tekstiä tarkennettu: 1. sijalle menee pyöristysjäännös (siksi se on usein hieman yli 50 %).
- Laskenta erotettu puhtaaksi funktioksi `computePayout()`, ja testattu kaikilla määrillä 0–500 ja kaikilla maksuilla: summa täsmää aina, ei negatiivisia, sijat laskevassa järjestyksessä, ja ≥3 pelaajalla tulos on identtinen alkuperäisen kanssa.
- Maksuvaihtoehdot ovat kiinteät (2/4/5/6/8/10 €); muu maksu (esim. 7 €) ei onnistu.

## Asennus
`scripts/build_stats.py` + `scripts/config.json` (config samaan paikkaan kuin vanha), `index.html` juureen, `data/*.json` korvaavat nykyiset.
