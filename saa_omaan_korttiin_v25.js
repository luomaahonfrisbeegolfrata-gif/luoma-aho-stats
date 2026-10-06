
// V25 OMAAN KORTTIIN - vain sää kortti, ei metrix
console.log("V25 omaan korttiin");
(async function(){
  const API="https://api.open-meteo.com/v1/forecast?latitude=63.00&longitude=23.822&current=temperature_2m,wind_speed_10m,precipitation,cloud_cover,apparent_temperature&timezone=Europe/Helsinki&forecast_days=1";
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
        if(r.ok){ const j=await r.json(); const age=(Date.now()-new Date(j.fetched_at))/1000/3600; if(age<3&&j.temp) data=j; else throw 1; }
      }catch(e){
        const r=await fetch(API); const j=await r.json(); const cur=j.current;
        data={temp:cur.temperature_2m, feels_like:cur.apparent_temperature, wind_speed:cur.wind_speed_10m, precipitation:cur.precipitation, cloudiness:cur.cloud_cover, forecast:"Ylin "+j.daily.temperature_2m_max[0]+"°C"};
      }
      const card=findSaaCard();
      if(!card) return;
      // Päivitä vain sää kortti
      card.querySelectorAll('div').forEach(div=>{
        const t=div.textContent;
        if(t.includes('Tuntuu kuin')) div.textContent=`Tuntuu kuin +${Math.round(data.feels_like||data.temp)}°`;
        if(t.startsWith('Tuuli')) div.textContent=`Tuuli ${data.wind_speed} m/s`;
        if(t.startsWith('Sade')) div.textContent=`Sade ${data.precipitation}mm - ${data.condition||''}`;
      });
      let big=card.querySelector('div'); 
      if(big && /\d+°/.test(big.textContent)) big.textContent='+'+Math.round(data.temp)+'°';
      console.log("V25 sää päivitetty",data.temp);
    }catch(e){ console.error(e); }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>{ upd(); setInterval(upd,5*60*1000); }); else { upd(); setInterval(upd,5*60*1000); }
})();
