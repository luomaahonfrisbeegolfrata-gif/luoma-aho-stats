// js/loader.js - LOPULLINEN VERSIO
// Staattinen + Dynaaminen - Luoma-aho Stats

document.addEventListener('DOMContentLoaded', () => {
  console.log('[LOADER] Kaynnistys...');

  // ================= STATIC =================
  
  // 1. RATAINFO - staattinen, ei koskaan muutu
  function initRataInfo() {
    const divs = document.querySelectorAll('div');
    for (const div of divs) {
      if (div.textContent.includes('Kalliopohjaisessa')) {
        div.style.fontSize = '16px';
        div.style.lineHeight = '1.7';
        div.style.color = '#ccc';
        div.style.maxWidth = '65ch';
        console.log('[STATIC] RATAINFO styled 16px');
        break;
      }
    }
  }

  // 2. HIO - staattinen, manuaalinen paivitys harvoin
  function initHIO() {
    const hardcodedHIO = [
      "Sami Lahti #5",
      "Joonas Niemi #12 (2x)", 
      "Mikko Korhonen #7",
      "Petri Virtanen #18",
      "Akseli Mäki #3"
    ];
    
    const countEl = document.getElementById('hio-count');
    const listEl = document.getElementById('hio-list');
    
    if (countEl) {
      countEl.textContent = `${hardcodedHIO.length}`;
      countEl.style.fontSize = '36px';
      countEl.style.fontWeight = '800';
      countEl.style.color = '#ffcc00';
      countEl.style.lineHeight = '1';
    }
    if (listEl) {
      listEl.innerHTML = hardcodedHIO.map(n => 
        `<div style="font-size:15px; line-height:1.6; color:#ddd;">${n}</div>`
      ).join('');
      console.log('[STATIC] HIO hardcoded 5 kpl');
    }
    
    // Fallback: jos holeinone.json olemassa, yliaja
    fetch('data/holeinone.json').then(r => r.json()).then(data => {
      if(data && data.length && countEl && listEl) {
        countEl.textContent = data.length;
        listEl.innerHTML = data.map((p:any) => 
          `<div style="font-size:15px; color:#ddd;">${p.nimi} #${p.vayla}</div>`
        ).join('');
        console.log('[STATIC] HIO yliajettu JSON:sta');
      }
    }).catch(() => {});
  }

  initRataInfo();
  initHIO();

  // ================= DYNAMIC =================

  // 3. TILASTO.JSON -> 5 korttia
  async function loadTilasto() {
    try {
      const res = await fetch('data/tilasto.json?v=' + Date.now());
      const data = await res.json();
      const set = (id: string, val: any) => {
        const el = document.getElementById(id);
        if(el) el.textContent = val;
      };
      set('live-kierrokset', data.kierrokset ?? data.totalRounds);
      set('live-pelaajat', data.uniikit ?? data.uniquePlayers);
      set('live-aika', data.peliaika ?? data.playTime);
      set('live-askeleet', data.askeleet?.toLocaleString('fi-FI') ?? data.steps);
      set('live-km', data.kilometrit ?? data.km);
      console.log('[AUTO] tilasto.json paivitetty', data);
    } catch(e) { console.error('[AUTO] tilasto.json virhe', e); }
  }

  // 4. TOP5.JSON -> 3 Metrix korttia + UDisc
  async function loadTop5() {
    try {
      const res = await fetch('data/top5.json?v=' + Date.now());
      const data = await res.json();
      
      const renderTop5 = (id: string, list: any[]) => {
        const el = document.getElementById(id);
        if(!el || !list) return;
        const filtered = list.filter((p:any) => !p.nimi.includes('Pelaaja A'));
        el.innerHTML = filtered.slice(0,5).map((p:any, i:number) => {
          const diff = p.tulos - p.par;
          const diffStr = diff === 0 ? 'E' : (diff > 0 ? `+${diff}` : `${diff}`);
          return `<div style="display:flex; justify-content:space-between; font-size:13px; padding:4px 0; border-bottom:1px solid #222;">
            <span>${i+1}. ${p.nimi}</span><span style="color:${diff <= -3 ? '#00ff00' : '#ccc'}">${p.tulos} (${diffStr})</span>
          </div>`;
        }).join('');
      };
      
      renderTop5('top5-44010', data['44010'] || data.metrix44010);
      renderTop5('top5-44763', data['44763'] || data.metrix44763);
      renderTop5('top5-udisc', data.udisc || data.UDisc);
      console.log('[AUTO] top5.json paivitetty');
    } catch(e) { console.error('[AUTO] top5.json virhe', e); }
  }

  // 5. FORECA.JSON -> SÄÄ
  async function loadSaa() {
    try {
      const res = await fetch('data/foreca.json?v=' + Date.now());
      const data = await res.json();
      const el = document.getElementById('saa-content');
      if(!el) return;
      
      // Oletus: data.tunnit = [{klo, ikoni, lampotila}, ...]
      const hours = data.tunnit || data.hours || [];
      const main = data.nykyinen || data.current || hours[0];
      
      el.innerHTML = `
        <div style="text-align:center; margin-bottom:12px;">
          <div style="font-size:36px; line-height:1;">${main?.ikoni || '⛅'} ${main?.lampotila || '--'}°</div>
          <div style="font-size:12px; color:#888; margin-top:4px;">${main?.kuvaus || 'Luoma-aho'}</div>
        </div>
        <div style="display:grid; grid-template-columns:repeat(${Math.min(hours.length,6)},1fr); gap:4px;">
          ${hours.slice(0,6).map((h:any) => `
            <div style="text-align:center; background:#1a1a1a; border-radius:6px; padding:6px 2px;">
              <div style="font-size:11px; color:#888;">${h.klo || h.time}</div>
              <div style="font-size:32px; line-height:1.2;">${h.ikoni || '🌤️'}</div>
              <div style="font-size:14px; font-weight:600;">${h.lampotila}°</div>
            </div>
          `).join('')}
        </div>`;
      console.log('[AUTO] foreca.json paivitetty');
    } catch(e) { console.error('[AUTO] saa virhe', e); }
  }

  // 6. RATATILASTO.JSON -> VÄYLÄTILASTO varitys
  async function loadVaylaTilasto() {
    try {
      const res = await fetch('data/ratatilasto.json?v=' + Date.now());
      const data = await res.json();
      const container = document.getElementById('vaylatilasto');
      if(!container) return;
      
      // data.vaylat = [{vayla, avg, vaikein}, ...]
      const vaylat = data.vaylat || data.holes || [];
      container.innerHTML = vaylat.map((v:any) => {
        const avg = v.keskiarvo || v.avg || 0;
        const par = v.par || 3;
        const diff = avg - par;
        let color = '#ccc';
        if(diff < -0.2) color = '#00ff00'; // helppo
        if(diff > 0.5) color = '#ff4444'; // vaikea
        if(diff > 0.2 && diff <= 0.5) color = '#ffcc00';
        return `<div style="display:flex; justify-content:space-between; padding:6px 8px; background:#111; margin-bottom:2px; border-left:3px solid ${color};">
          <span style="font-size:13px;">Väylä ${v.numero || v.vayla}</span>
          <span style="font-size:13px; color:${color}; font-weight:700;">${avg.toFixed(2)}</span>
        </div>`;
      }).join('');
      console.log('[AUTO] ratatilasto.json varitetty');
    } catch(e) { console.error('[AUTO] ratatilasto virhe', e); }
  }

  // KAIKKI DYNAAMISET
  function loadAllDynamic() {
    loadTilasto();
    loadTop5();
    loadSaa();
    loadVaylaTilasto();
  }

  loadAllDynamic();
  
  // AUTO REFRESH 5min = 300000ms
  setInterval(loadAllDynamic, 300000);
  console.log('[LOADER] AUTO refresh 5min kaynnistetty');
});
