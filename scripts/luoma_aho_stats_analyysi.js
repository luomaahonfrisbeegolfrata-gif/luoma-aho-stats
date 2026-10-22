// Nyt 100% ehdollinen:
fetch vaylatilasto.json -> VAYLA_KAIKKI=j; 
  if(currentMode==='kaikki'){ renderVayla(j); updateRatingMini(); }

fetch vaylatilasto_udisc_only.json -> VAYLA_UDISC=j2;
  if(currentMode==='udisc'){ renderVayla(j2); updateRatingMini(); }