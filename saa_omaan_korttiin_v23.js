// V23 OMAAN KORTTIIN - päivittää siihen korttiin mikä sivulla jo oli - HEADER/LAYOUT/KORTIT LUKITTU
// Pakolliset: lämpötila, tuuli, ennuste, vesisade, pilvisyys
// https://www.foreca.fi/Finland/Alajarvi/Luoma-aho
console.log("V23 OMAAN KORTTIIN - Luoma-aho Foreca");

(async function(){
  const FORECA_URL = "https://www.foreca.fi/Finland/Alajarvi/Luoma-aho";
  const API = "https://api.open-meteo.com/v1/forecast?latitude=63.00&longitude=23.822&current=temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,cloud_cover,relative_humidity_2m,apparent_temperature,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=Europe/Helsinki&forecast_days=2";

  function updateExistingCard(data) {
    // Etsi SE kortti mikä sivulla jo oli - KAIKKI mahdolliset selektorit
    const cardSelectors = [
      '#saa-kortti', '.saa-card', '[data-card="saa"]', '.card-saa',
      '#saa', '.saa', '.weather-card', '.card[data-card="saa"]',
      '.card:nth-child(1)', 'main .card:first-child' // fallback jos sää on eka kortti
    ];
    
    let card = null;
    for (const sel of cardSelectors) {
      const el = document.querySelector(sel);
      if (el && (el.textContent.toLowerCase().includes('sää') || el.textContent.toLowerCase().includes('saa') || sel.includes('saa') || sel.includes('weather'))) {
        card = el;
        console.log("V23 löytyi sää kortti:", sel, card);
        break;
      }
    }
    // Jos ei löytynyt sää-tekstillä, etsi ensimmäinen kortti jossa on °C
    if (!card) {
      document.querySelectorAll('.card, [class*="card"]').forEach(c => {
        if (!card && c.textContent.includes('°C')) {
          card = c;
          console.log("V23 löytyi kortti jossa °C:", card);
        }
      });
    }
    if (!card) {
      console.warn("V23 EI löytynyt sää korttia - katso console");
      return;
    }

    // ÄLÄ KORVAA KOKO KORTTIA - päivitä vain kentät säilyttäen header/layout
    // 1. Lämpötila
    let tempEl = card.querySelector('.temp, .temperature, [data-temp], .saa-temp, #saa-temp, .value.temp, span.temp');
    if (!tempEl) {
      // Etsi teksti joka on pelkkä "11°C"
      card.querySelectorAll('*').forEach(el => {
        if (!tempEl && el.children.length === 0 && /^\s*-?\d+\.?\d*°C\s*$/.test(el.textContent)) {
          tempEl = el;
        }
      });
    }
    if (tempEl) {
      tempEl.textContent = data.temp + '°C';
      tempEl.setAttribute('data-updated', 'V23');
    }

    // 2. Tuuli - etsi olemassa oleva tai luo uuteen riviin kortin sisään
    let windEl = card.querySelector('.wind, .saa-wind, [data-wind], .tuuli');
    if (windEl) {
      windEl.textContent = data.wind_speed + ' m/s ' + (data.wind_direction_text||'');
    } else {
      // Luo uusi div KORTIN SISÄLLE, ei korvaa koko korttia
      const div = document.createElement('div');
      div.className = 'saa-wind';
      div.innerHTML = `<strong>Tuuli:</strong> ${data.wind_speed} m/s ${data.wind_direction_text||''} (${data.wind_direction}°)`;
      div.style.fontSize = '14px';
      card.appendChild(div);
    }

    // 3. Vesisade
    let precipEl = card.querySelector('.precip, .saa-precip, [data-precip], .sade, .vesisade');
    if (precipEl) {
      precipEl.textContent = data.precipitation + ' mm';
    } else {
      const div = document.createElement('div');
      div.className = 'saa-precip';
      div.innerHTML = `<strong>Vesisade:</strong> ${data.precipitation} mm (tänään ${data.precipitation_today} mm)`;
      div.style.fontSize = '14px';
      card.appendChild(div);
    }

    // 4. Pilvisyys
    let cloudEl = card.querySelector('.cloud, .saa-cloud, [data-cloud], .pilvisyys');
    if (cloudEl) {
      cloudEl.textContent = data.cloudiness + '%';
    } else {
      const div = document.createElement('div');
      div.className = 'saa-cloud';
      div.innerHTML = `<strong>Pilvisyys:</strong> ${data.cloudiness}%`;
      div.style.fontSize = '14px';
      card.appendChild(div);
    }

    // 5. Ennuste
    let forecastEl = card.querySelector('.forecast, .saa-forecast, [data-forecast], .ennuste');
    if (forecastEl) {
      forecastEl.textContent = data.forecast;
    } else {
      const div = document.createElement('div');
      div.className = 'saa-forecast';
      div.innerHTML = `<strong>Ennuste:</strong> ${data.forecast}`;
      div.style.fontSize = '14px';
      card.appendChild(div);
    }

    // Päivitetty aika
    let updatedEl = card.querySelector('.updated, .aika, small, .saa-updated');
    if (updatedEl) {
      updatedEl.textContent = 'Päivitetty ' + (data.fetched_at_fi || new Date().toLocaleString('fi-FI')) + ' (live)';
    }

    // Lisää Foreca linkki jos ei ole
    if (!card.querySelector('a[href*="foreca"]')) {
      const link = document.createElement('a');
      link.href = FORECA_URL;
      link.target = '_blank';
      link.textContent = 'Foreca Luoma-aho';
      link.style = 'display:block;margin-top:8px;font-size:11px;color:#0af;';
      card.appendChild(link);
    }

    console.log("V23 päivitti omaan korttiin:", data);
  }

  async function fetchAndUpdate() {
    try {
      let data = null;
      // 1. data/saa.json
      try {
        const r = await fetch('data/saa.json?v=' + Date.now(), {cache: 'no-store'});
        if (r.ok) {
          const j = await r.json();
          const age = (Date.now() - new Date(j.fetched_at)) / 1000 / 3600;
          if (age < 3 && j.temp) {
            data = j;
            console.log(`V23 data/saa.json tuore ${age.toFixed(1)}h`);
          } else throw new Error("vanha");
        }
      } catch(e) {
        console.log("V23 haetaan live Open-Meteo kaikki 5 kenttää");
        const r = await fetch(API + '&_=' + Date.now());
        const j = await r.json();
        const cur = j.current;
        const daily = j.daily;
        const codes = {0:"Selkeää",1:"Melkein selkeää",2:"Puolipilvistä",3:"Pilvistä",61:"Heikkoa sadetta",63:"Sadetta",65:"Voimakasta sadetta",80:"Sadekuuroja",95:"Ukkosta"};
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
          forecast: `${codes[cur.weather_code]||"Sää"}. Ylin ${daily.temperature_2m_max[0]}°C, alin ${daily.temperature_2m_min[0]}°C. Tuulta ${daily.wind_speed_10m_max[0]} m/s. Sadetta ${daily.precipitation_sum[0]} mm.`,
          fetched_at_fi: new Date().toLocaleString('fi-FI') + " (live)"
        };
      }
      if (data) updateExistingCard(data);
    } catch(err) {
      console.error("V23 fail", err);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { fetchAndUpdate(); setInterval(fetchAndUpdate, 5*60*1000); });
  } else {
    fetchAndUpdate(); setInterval(fetchAndUpdate, 5*60*1000);
  }
  setTimeout(fetchAndUpdate, 2500);
})();
