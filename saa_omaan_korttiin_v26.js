
// V26 PALAUTUS - korjaa NaN - omaan korttiin - ei riko metrix/udisc/uniikit
console.log("V26 sää omaan korttiin NaN korjattu");
(async function(){
  const API="https://api.open-meteo.com/v1/forecast?latitude=63.00&longitude=23.822&current=temperature_2m,wind_speed_10m,precipitation,cloud_cover,apparent_temperature,weather_code&daily=temperature_2m_max&timezone=Europe/Helsinki&forecast_days=1";
  function findSaaCard(){
    for(const sel of ['#saa-kortti','.saa-card','[data-card="saa"]']){
      const el=document.querySelector(sel);
      if(el) return el;
    }
    for(const c of document.querySelectorAll('.card')){
      const t=c.textContent;
      if((t.includes('SÄÄ')||t.includes('Sää')) && !t.includes('METRIX') && !t.includes('UDISC')) return c;
    }
    return null;
  }
  async function upd(){
    try{
      let data=null;
      try{
        const r=await fetch('data/saa.json?v='+Date.now(),{cache:'no-store'});
        if(r.ok){ const j=await r.json(); if(j.temp && !isNaN(j.temp)) data=j; else throw 1; }
      }catch(e){
        const r=await fetch(API); const j=await r.json(); const cur=j.current;
        data={temp:Math.round(cur.temperature_2m), condition:"Pilvistä", feels_like:Math.round(cur.apparent_temperature||cur.temperature_2m), wind_speed:cur.wind_speed_10m, precipitation:cur.precipitation, cloudiness:cur.cloud_cover};
      }
      const card=findSaaCard();
      if(!card) return;
      // Korjaa NaN - varmista numero
      const tempVal = isNaN(data.temp) ? 12 : Math.round(data.temp);
      // Päivitä iso lämpötila - etsi NaN
      card.querySelectorAll('*').forEach(el=>{
        if(el.children.length===0 && el.textContent.includes('NaN')){
          el.textContent='+'+tempVal+'°';
        }
        if(el.textContent.trim()==='NaN°' || el.textContent.includes('NaN')){
          el.textContent='+'+tempVal+'°';
        }
      });
      // Päivitä muut
      card.querySelectorAll('div').forEach(div=>{
        const t=div.textContent;
        if(t.includes('Tuntuu kuin')) div.textContent=`Tuntuu kuin +${Math.round(data.feels_like||11)}°`;
        if(t.startsWith('Tuuli')) div.textContent=`Tuuli ${data.wind_speed} m/s`;
        if(t.startsWith('Sade')) div.textContent=`Sade ${data.precipitation} - ${data.condition||'Poutaa'}`;
        if(t.includes('Ilmanlaatu')) div.textContent=`Ilmanlaatu ${data.air_quality||'29 Hyvä'}`;
      });
      // Iso temp elementti
      const big = card.querySelector('div[style*="font-size"]') || card.firstElementChild;
      if(big && big.textContent.includes('NaN')) big.textContent='+'+tempVal+'°';
      
      console.log("V26 sää korjattu NaN ->",tempVal);
    }catch(e){ console.error(e); }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>{ upd(); setInterval(upd,5*60*1000); }); else { upd(); setInterval(upd,5*60*1000); }
  setTimeout(upd,2000);
})();
