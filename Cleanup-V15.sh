#!/bin/bash
# CLEANUP V15 - poista vanhat data tiedostot - HEADER/ LAYOUT/ KORTIT LUKITTU - ei koske index.html
echo "=== V15 CLEANUP - vanhat tiedostot ==="
# Varmista että ollaan repo juuressa
# Poista vanhat versiot - säilytä vain V15
rm -f data/vaylatilasto_manual.json
rm -f data/vaylatilasto_V*.png
rm -f data/vaylatilasto_V*.json
rm -f data/foreca.json
rm -f data/kierrokset_v*.json
rm -f data/vaylatilasto_old.json
rm -f data/udisc_top10.json
rm -f data/metrix_*_top10.json
rm -f auto_update_v7.py auto_update_v6.py
rm -f vaylatilasto_fetcher_v*.py
rm -f vaylatilasto_fetcher_KORJATTU_*.py
rm -f .github/workflows/auto-update.yml
rm -f .github/workflows/foreca-update.yml
rm -f .github/workflows/auto_update.yml
rm -f vaylatilasto_V*.png
rm -f vaylatilasto_KORJATTU*.png
rm -f vaylatilasto_KORJATTU*.json
rm -f V15_KAIKKI_KORJAUKSET_LUKITTU.zip
rm -f V15_KORJATTU_PAKETTI -r

echo "Jäljelle jää:"
ls -lh data/
echo ""
echo "Pakolliset tiedostot jotka pitää olla:"
echo " - vaylatilasto_fetcher.py (V15 B avg-par)"
echo " - auto_update.py (V15 1164)"
echo " - udisc_fetcher.py (V15)"
echo " - data/vaylatilasto.json"
echo " - data/vaylatilasto.png"
echo " - data/holeinone.json"
echo " - data/kierrokset.json"
echo " - data/udisc.json"
echo " - data/saa.json (open-meteo)"
echo " - data/status.json"
echo " - .github/workflows/vaylatilasto.yml, kierrokset.yml, udisc.yml, saa.yml"
echo ""
echo "HEADER/ LAYOUT/ KORTIT lukittu - ei muutoksia index.html"
