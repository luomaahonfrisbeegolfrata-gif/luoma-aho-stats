#!/bin/bash
# V17 FINAL CLEANUP - poista kaikki turhat .1 .2 ja vanhat
echo "=== V17 FINAL CLEANUP ==="
rm -f *_1.png *_2.png *_1.json *_2.json
rm -f data/*_1.png data/*_1.json data/*_2.png data/*_2.json
rm -f data/vaylatilasto_manual.json data/foreca.json data/udisc_top10.json
rm -f data/vaylatilasto_V*.json data/vaylatilasto_V*.png
rm -f auto_update_v*.py vaylatilasto_fetcher_v*.py
rm -f .github/workflows/auto-update.yml .github/workflows/foreca-update.yml
rm -f V15*.zip V16*.zip FINAL*.zip
rm -f *_FIXED.py *_FIXED.yml
echo "Jäljelle jää vain V17 FINAL"
ls -lh
echo ""
echo "Aja: python health_check.py"
