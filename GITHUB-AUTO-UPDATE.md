# GitHub Auto Update – Luoma-aho Frisbeegolf – FINAL V5

GitHub tekee tämän automaattisesti 6h välein – kaikki 6 graafia huomioitu.

## Workflow: .github/workflows/auto-update.yml

- **Ajastus:** `cron: '0 */6 * * *'` – 00:00, 06:00, 12:00, 18:00 UTC
- **Manuaalinen ajo:** `workflow_dispatch` – GitHub UI -> Actions -> Run workflow
- **Auto push:** Jos `data/kierrokset.json` muuttuu, commitoi automaattisesti:
  `Auto update: 2026-10-03 12:00 UTC – FINAL V5 – 1164 kierrosta (729 Metrix + 435 UDisc) – 1524h – 3 192 132 askelta – 2328km`

## Mitä päivitetään automaattisesti

- `auto_update.py` – master fetcher:
  - 44010 REAL 598 (551H+47K) Jul25-Oct26
  - 44021 REAL 45 (42H+3K) Jul-Sep25
  - 45536 REAL 5 (5H+0K) Nov25
  - 44565 REAL 56 (18H+38K) Sep25-Mar26
  - 44763 REAL 63 (15H+48K) Sep25-Sep26
  - Sum 767 vs 43119 parent 729 ero 38 (5.2%) – EI TUPLAA – AUTHORITATIVE 729
  - UDisc REAL 435 (613h, 67 pelaajaa, 1 296 732 askelta) 3.10.2026 klo 5.02
  - YHT 1164 = 729 + 435 FINAL

- Kaavat:
  - Tuntimäärä: 613 + 729×1.25 = 1524.25h – 1.25h per 12 väylää
  - Askeleet: 1 296 732 + 729×2600 = 3 192 132 – 2600 per kierros
  - Km: 1164×2 = 2328km – 2km per kierros

- `udisc_fetcher.py` – Top10 REAL 12 väylää Par41 (35-44) EI 82-97
- `data/foreca.json` – sää Luoma-aho
- `data/auto_status.json` – last_update timestamp

## Päivitetty: 2026-10-03T10:37:36.244551

## GitHub Secrets – ei tarvita – ilmainen taso requests+bs4

## Testaa paikallisesti
```bash
python auto_update.py
python udisc_fetcher.py
```
