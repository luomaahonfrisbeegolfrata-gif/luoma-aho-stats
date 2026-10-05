// V22 FORECA CLIENT - PAKOLLISET: lämpötila, tuuli, ennuste, vesisade, pilvisyys
// https://www.foreca.fi/Finland/Alajarvi/Luoma-aho
console.log("V22 FORECA PAKOLLISET LADATAAN - Luoma-aho");

(async function(){
  const FORECA_URL = "https://www.foreca.fi/Finland/Alajarvi/Luoma-aho";
  const OPEN_METEO = "https://api.open-meteo.com/v1/forecast?latitude=63.00&longitude=23.822&current=temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,cloud_cover,relative_humidity_2m,apparent_temperature,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=Europe/Helsinki&forecast_days=2";
  
  function renderSaaCard(data) {
    // Etsi sää kortti
    const card = document.querySelector('#saa-kortti, .saa-card, [data-card="saa"], .card-saa') || 
                 document.querySelector('.card');
    
    if (!card) return;
    
    // Luo tai päivitä sisältö kaikilla pakollisilla kentillä
    const html = `
      <h3 style="margin:0 0 10px 0;">Sää - Luoma-aho Alajärvi</h3>
      <div style="display:grid;gap:8px;">
        <div><strong>Lämpötila:</strong> <span class="saa-temp" style="font-size:24px;font-weight:bold;">${data.temp}°C</span> (tuntuu ${data.feels_like}°C)</div>
        <div><strong>Tuuli:</strong> <span class="saa-wind">${data.wind_speed} m/s ${data.wind_direction_text || ''} (${data.wind_direction}°)</span></div>
        <div><strong>Vesisade:</strong> <span class="saa-precip">${data.precipitation} mm</span> (tänään ${data.precipitation_today} mm)</div>
        <div><strong>Pilvisyys:</strong> <span class="saa-cloud">${data.cloudiness}%</span></div>
        <div><strong>Ennuste:</strong> <span class="saa-forecast">${data.forecast}</span></div>
        <div style="font-size:11px;color:#888;margin-top:8px;">
          Kosteus ${data.humidity}% | Päivitetty ${data.fetched_at_fi || new Date().toLocaleString('fi-FI')}<br>
          <a href="${FORECA_URL}" target="_blank" style="color:#0af;">${FORECA_URL}</a>
        </div>
      </div>
    `;
    
    // Jos kortti on tyhjä tai vanha, korvaa koko sisältö
    if (card.textContent.includes('11°C') || card.textContent.includes('Päivitetty eilen') || !card.querySelector('.saa-temp')) {
      card.innerHTML = html;
    } else {
      // Päivitä vain arvot
      const tEl = card.querySelector('.saa-temp, .temp, [data-temp]');
      if (tEl) tEl.textContent = data.temp + '°C';
      const wEl = card.querySelector('.saa-wind');
      if (wEl) wEl.textContent = data.wind_speed + ' m/s ' + (data.wind_direction_text||'');
      const pEl = card.querySelector('.saa-precip');
      if (pEl) pEl.textContent = data.precipitation + ' mm';
      const cEl = card.querySelector('.saa-cloud');
      if (cEl) cEl.textContent = data.cloudiness + '%';
      const fEl = card.querySelector('.saa-forecast');
      if (fEl) fEl.textContent = data.forecast;
    }
    
    // Debug box
    let box = document.getElementById('saa-v22-debug');
    if (!box) {
      box = document.createElement('div');
      box.id = 'saa-v22-debug';
      box.style = 'position:fixed;bottom:10px;right:10px;background:#111;color:#0f0;padding:12px;border:2px solid #0af;z-index:99999;font-family:monospace;font-size:11px;max-width:320px;';
      document.body.appendChild(box);
    }
    box.innerHTML = `V22 FORECA PAKOLLISET<br>🌡️ ${data.temp}°C<br>💨 ${data.wind_speed} m/s<br>🌧️ ${data.precipitation} mm<br>☁️ ${data.cloudiness}%<br>📝 ${data.forecast_text}<br><a href="${FORECA_URL}" target="_blank" style="color:#0af;">Foreca Luoma-aho</a><br>${new Date().toLocaleString('fi-FI')}`;
  }
  
  async function updateSaa() {
    try {
      let data = null;
      // 1. Yritä data/saa.json
      try {
        const r = await fetch('data/saa.json?v=' + Date.now(), {cache: 'no-store'});
        if (r.ok) {
          const j = await r.json();
          const age = (Date.now() - new Date(j.fetched_at)) / 1000 / 3600;
          if (age < 3 && j.temp) {
            data = j;
            console.log(`Sää data/saa.json tuore ${age.toFixed(1)}h`);
          } else throw new Error("vanha");
        }
      } catch(e) {
        // 2. Fallback Open-Meteo live - kaikki pakolliset kentät
        console.log("Haetaan Open-Meteo live kaikki kentät");
        const r = await fetch(OPEN_METEO + '&_=' + Date.now());
        const j = await r.json();
        const cur = j.current;
        const daily = j.daily;
        const codes = {0:"Selkeää",1:"Melkein selkeää",2:"Puolipilvistä",3:"Pilvistä",61:"Heikkoa sadetta",63:"Sadetta",65:"Voimakasta sadetta",80:"Sadekuuroja",95:"Ukkosta"};
        const forecastText = codes[cur.weather_code] || "Sää";
        const dirText = ["P","Koillinen","I","Kaakko","E","Lounas","L","Luode"][Math.round(cur.wind_direction_10m/45)%8];
        data = {
          temp: cur.temperature_2m,
          feels_like: cur.apparent_temperature,
          wind_speed: cur.wind_speed_10m,
          wind_direction: cur.wind_direction_10m,
          wind_direction_text: dirText,
          precipitation: cur.precipitation,
          precipitation_today: daily.precipitation_sum[0],
          cloudiness: cur.cloud_cover,
          forecast: `${forecastText}. Ylin ${daily.temperature_2m_max[0]}°C, alin ${daily.temperature_2m_min[0]}°C.`,
          forecast_text: forecastText,
          humidity: cur.relative_humidity_2m,
          fetched_at_fi: new Date().toLocaleString('fi-FI') + " (live)",
        };
      }
      if (data) renderSaaCard(data);
    } catch(e) {
      console.error("V22 fail", e);
    }
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { updateSaa(); setInterval(updateSaa, 5*60*1000); });
  } else {
    updateSaa(); setInterval(updateSaa, 5*60*1000);
  }
  setTimeout(updateSaa, 2000);
})();
