// V21 FORECA CLIENT - Luoma-aho Alajärvi https://www.foreca.fi/Finland/Alajarvi/Luoma-aho
// Foreca.fi ei salli suoraa CORS fetchiä, joten haetaan data/saa.json joka päivitetään GitHub Actionsilla Forecasta
// Fallback Open-Meteo jos data/saa.json vanha
console.log("V21 FORECA CLIENT Luoma-aho https://www.foreca.fi/Finland/Alajarvi/Luoma-aho");

(async function(){
  const FORECA_URL = "https://www.foreca.fi/Finland/Alajarvi/Luoma-aho";
  const OPEN_METEO = "https://api.open-meteo.com/v1/forecast?latitude=63.00&longitude=23.822&current=temperature_2m,wind_speed_10m&timezone=Europe/Helsinki";
  
  async function updateSaa() {
    try {
      let temp = null;
      let source = "";
      let timeStr = "";
      
      // 1. Yritä data/saa.json (päivitetty Forecasta Actionsilla)
      try {
        const r = await fetch('data/saa.json?v=' + Date.now(), {cache: 'no-store'});
        if (r.ok) {
          const j = await r.json();
          const age = (Date.now() - new Date(j.fetched_at)) / 1000 / 3600;
          if (age < 3 && j.temp) {
            temp = j.temp;
            source = j.source || FORECA_URL;
            timeStr = j.fetched_at_fi;
            console.log(`Sää data/saa.json Foreca tuore ${age.toFixed(1)}h: ${temp}°C`);
          } else {
            throw new Error("vanha");
          }
        }
      } catch(e) {
        // 2. Fallback Open-Meteo live (toimii aina)
        console.log("data/saa.json vanha, haetaan Open-Meteo live, linkki Forecaan");
        const r = await fetch(OPEN_METEO);
        const j = await r.json();
        temp = j.current.temperature_2m;
        source = FORECA_URL + " (live Open-Meteo fallback)";
        timeStr = new Date().toLocaleString('fi-FI') + " (live)";
      }
      
      if (temp !== null) {
        // Päivitä DOM
        document.querySelectorAll('#saa-kortti .temp, .saa-card .temp, [data-card="saa"] .temp').forEach(el => {
          el.textContent = temp + '°C';
        });
        // Päivitä linkki Forecaan
        document.querySelectorAll('#saa-kortti a, .saa-card a').forEach(a => {
          if (a.href.includes('foreca') || a.textContent.toLowerCase().includes('foreca')) {
            a.href = FORECA_URL;
          }
        });
        // Jos ei linkkiä, lisää
        const card = document.querySelector('#saa-kortti, .saa-card, [data-card="saa"]');
        if (card && !card.querySelector('a[href*="foreca"]')) {
          const link = document.createElement('a');
          link.href = FORECA_URL;
          link.target = "_blank";
          link.textContent = "Foreca Luoma-aho";
          link.style = "display:block;margin-top:5px;font-size:12px;color:#0af;";
          card.appendChild(link);
        }
        // Updated
        document.querySelectorAll('#saa-kortti .updated, .saa-card .updated').forEach(el => {
          el.textContent = 'Päivitetty ' + timeStr;
        });
        // Debug box
        let box = document.getElementById('saa-foreca-debug');
        if (!box) {
          box = document.createElement('div');
          box.id = 'saa-foreca-debug';
          box.style = 'position:fixed;bottom:10px;right:10px;background:#111;color:#0f0;padding:10px;border:2px solid #0af;z-index:99999;font-family:monospace;font-size:11px;';
          document.body.appendChild(box);
        }
        box.innerHTML = `V21 FORECA<br>Temp: ${temp}°C<br><a href="${FORECA_URL}" target="_blank" style="color:#0af;">${FORECA_URL}</a><br>${timeStr}`;
      }
    } catch(e) {
      console.error("V21 Foreca fail", e);
    }
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { updateSaa(); setInterval(updateSaa, 5*60*1000); });
  } else {
    updateSaa(); setInterval(updateSaa, 5*60*1000);
  }
  setTimeout(updateSaa, 3000);
})();
