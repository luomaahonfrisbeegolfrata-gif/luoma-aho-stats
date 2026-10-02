# Luoma-aho Frisbeegolfrata - LIVE Stats

[GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-LIVE-green)
[Auto Update](https://img.shields.io/badge/AUTO-5min-blue)
[Commits](https://img.shields.io/badge/commits-561-blue)

**Live-sivusto:** https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/

Alajärven Luoma-ahon tekninen metsärata - täysin automatisoitu tilastosivu.

## RATAINFO

Kalliopohjaisessa mäkisessä mäntymetsä maastossa. Tekninen / vaativa mutta helposti lähestyttävä. Pienellä alueella jossa olemattomat siirtymät. Loistava kunto metsäradaksi. Väylien pituudet 57-197m. OB:t ja Mandot haastavat päätöksentekoa.

## Mitä sivulla on (AUTO)

- **SÄÄ** - Foreca LIVE 5min välein `data/foreca.json`
- **UDisc + Metrix kierrokset** - 1130+ kierrosta, uniikit pelaajat ~100
- **TOP5** - parhaat tulokset
- **Ratatilasto & Väylätilasto** - Chart.js client-side, ei PNG:tä gitissä
- **Hole-in-one** `data/holeinone.json`

## Arkkitehtuuri (Korjattu #1-5)

```
GitHub Actions (auto_5min.yml 5min + fetch.yml 60min)
   ↓
unified_fetcher.py (metrix + top5 + vayla + scraper) - ei kaadu yhdestä lähteestä
   ↓
data/*.json (vain JSON/CSV, ei PNG) - validoitu ennen commitia [skip ci]
   ↓
GitHub Pages (index.html + js/loader.js + js/ratatilasto.js Chart.js)
   ↓
Selain - cache-buster ?v=Date.now(), auto-refresh 5min
```

## Kansiot

- `.github/workflows/` - automaatio, loop-estot + concurrency
- `data/` - totuus, vain JSON/CSV (PNGt ignorattu .gitignore)
- `js/` - `loader.js` (cache-buster, error handling) + `ratatilasto.js` (Chart.js)
- `logot/` - integraatio-logot (siivottu duplikaateista)

## Kehitys

```bash
pip install -r requirements.txt
python unified_fetcher.py
python -m http.server 8000
# avaa http://localhost:8000
```

## Korjaukset tehty (2026-10-02)

1. **Workflow loop-riski** - poistettu push-trigger, lisätty `[skip ci]` + concurrency + `if: actor != foreca-bot`
2. **Git turpoaminen** - `.gitignore` data/*.png, poistettu juuren duplikaatti PNGt, logot duplikaatit (ig-logo vs instagram-logo)
3. **Frontend cache + SEO** - loader.js cache-buster, noscript fallback, JSON-LD, Open Graph
4. **Fetcher yhdistetty** - unified_fetcher.py, safe_write_json, retry, User-Agent
5. **PNG -> Chart.js** - ei enää kuvagenerointia gitiin, 99% säästö historiassa

## TODO (vapaaehtoinen)

- [ ] Lisää Metrix oikea API-kutsu unified_fetcher.py sisään
- [ ] Siirrä vanha git-historia kevyemmäksi: `git filter-repo` PNGt pois
- [ ] Lisää status-badge README:n alkuun

## Lisenssi

MIT - Luoma-ahon frisbeegolfrata ry
