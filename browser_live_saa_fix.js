
// v7.2 BROWSER FIX - lisätään index.html:n foreca scriptin perään, ei muuta layouttia
(function(){
  async function fetchOpenMeteoLive(){
    try{
      const url = 'https://api.open-meteo.com/v1/forecast?latitude=63.0772&longitude=23.867&current=temperature_2m,wind_speed_10m,relative_humidity_2m,precipitation,weather_code&timezone=Europe%2FHelsinki';
      const r = await fetch(url, {cache:'no-store'});
      if(!r.ok) throw new Error('open-meteo fail');
      const j = await r.json();
      const cur = j.current;
      if(cur && cur.temperature_2m != null){
        // Päivitä window.__LATEST_DATA__.saa jos mahdollista
        if(window.__LATEST_DATA__ && window.__LATEST_DATA__.saa){
          window.__LATEST_DATA__.saa.nyky.temp_c = cur.temperature_2m;
          window.__LATEST_DATA__.saa.nyky.wind_ms = cur.wind_speed_10m;
          window.__LATEST_DATA__.saa.nyky.humidity = cur.relative_humidity_2m;
          window.__LATEST_DATA__.saa.nyky.lahde = 'Open-Meteo LIVE browser';
        }
        const el = document.getElementById('foreca-temp');
        if(el) el.textContent = Math.round(cur.temperature_2m) + '°C';
        const windEl = document.getElementById('foreca-wind');
        if(windEl) windEl.textContent = 'Tuuli ' + cur.wind_speed_10m + ' m/s';
        console.log('v7.2 browser live sää', cur.temperature_2m);
      }
    }catch(e){ console.log('v7.2 browser sää fail', e); }
  }
  // Aja heti ja 5min välein
  setTimeout(fetchOpenMeteoLive, 2000);
  setInterval(fetchOpenMeteoLive, 300000);
})();
