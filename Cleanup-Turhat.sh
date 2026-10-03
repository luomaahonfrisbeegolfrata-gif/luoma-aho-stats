#!/bin/bash
# CLEANUP - poista turhat - V8 - säilytä core
echo "=== POISTETAAN TURHAT - SÄILYTETÄÄN CORE V7/V8 ==="
echo "Core: index.html 1164 OIKEA, data/*.json V7, fetchers V7, .github/workflows/fetch-all-auto.yml V8, logot/"

# 1. Dokumentaatio juuressa - turha prod
rm -f ANALYYSI-FIX1.md Analyysi-luoma-aho-frisbeegolf-sivusta.py FORECA-AUTOMATISOINTI-V7.md GITHUB-AUTO-UPDATE.md HEADER-LAYOUT-LUKITTU-V6.md
rm -f ANALYYSI_FIX1.md CLEANUP.md GITHUB_AUTO_UPDATE.md INDEX_LOCKED_README.md LOGOT_CLEANUP.md MITEN_AJAA.md README_LINKS.md UNIFIED_README.md WORKFLOW_ANALYYSI_V8.md OIKEAT_LINKIT_FINAL.txt

# 2. Root duplikaatit
rm -f vaylatilasto.png holeinone.txt holeinone.json
rm -f gmaps_logo_clean.png logo4_clean.png parkdly_logo_clean.png rain_icon.png sunrise_icon.png sunset_icon.png yt_logo_clean.png
rm -f loader.js ratatilasto.js

# 3. Vanhat fetchers juuressa
rm -f kierrokset_fetcher.py kierrokset_fetcher_1.py kierrokset_fetcher_2.py kierrokset_fetcher_3.py kierrokset_fetcher_4.py kierrokset_fetcher_5.py kierrokset_fetcher_6.py kierrokset_fetcher_7.py kierrokset_fetcher_8.py kierrokset_fetcher_fixed.py
rm -f auto_update_1.py auto_5min.yml fetch.yml fetch_all_auto_15min_fixed.yml fetch_all_vaylatilasto.yml fetch_final.yml fetch_unified.yml foreca_auto_5min_fixed.yml foreca_fetcher_24h.py foreca_fetcher_enhanced.py foreca_fetcher_fixed.py github_workflow_top10.yml unified_fetcher.py crop_logos.py auto_dashboard.html

# 4. Vanhat index variantit - 30+ kpl - säästä vain index.html + index.käytössä.html
rm -f index_1.html index_2.html index_3.html index_4.html index_5.html index_6.html index_all_350px.html index_clean_no_info_green_dot.html index_cropped_logos.html index_dark_fixed.html index_final_locked_perfect.html index_final_tarkennus.html index_fixed_all.html index_fixed_header_no_text_ig.html index_foreca_ikonit.html index_foreca_real.html index_header_isompi.html index_hio_42px_names_bigger.html index_hio_centered.html index_hio_kavennettu.html index_isot_numerot.html index_kaikki_auto.html index_kavennettu_ratainfoon.html index_kierrokset_auto.html index_linkit_palautettu.html index_logot_equal.html index_metrix_udisc_same_300x350.html index_plusminus_clean.html index_plusminus_colors_swapped.html index_ratainfo_300px_font_fit.html index_ratainfo_50prossaa.html index_ratainfo_rivitys_final.html index_ratainfo_width_match.html index_restored_fixed.html index_saa_korkeus_pinottu.html index_saa_ylariviin.html index_top10_auto.html index_udisc_fixed.html index_udisc_real_435_final.html index_v6_prompt_100.html index_vaylatilasto_restored.html index_with_location.html index.käytössä_1.html index.käytössä_2.html index.käytössä_3.html index.käytössä_4.html

# 5. Data duplikaatit
rm -f data/*_1.json data/*_2.json data/*_3.json data/*_4.json data/*_5.json data/*_6.json data/*_7.json data/*_8.json
rm -f data/tilastot*.json data/vaylatilasto_1.png data/vaylatilasto_simple*.json data/udisc_real.json

# 6. Vanhat workflows - säästä vain fetch-all-auto.yml + auto-update.yml + foreca-update.yml
cd .github/workflows || exit 1
ls *.yml | grep -v -E "fetch-all-auto.yml|auto-update.yml|foreca-update.yml" | xargs rm -f
cd ../..

# 7. js kansio - vanha - JS nyt inline
rm -rf js/

echo "=== VALMIS - TURHAT POISTETTU - CORE JÄLJELLÄ V7/V8 ==="
echo "Jäljellä: index.html 1164 OIKEA, data/ 8 JSON + PNG, 6 fetcheriä, 1 workflow V8, logot/"
ls -1 | head -20
ls -1 data/ | head -20
