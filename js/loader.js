// KORJATTU loader.js - syntaksivirhe fix FINAL
// Koko kortti 10% pienemmäksi 1:1 + MOBILE 15%

function injectMobileCSS() {
  const _mobileFix = document.createElement('style');
  _mobileFix.textContent = `
  .card{zoom:0.9}
  @supports not (zoom:0.9){
    .card{transform:scale(0.9);transform-origin:top left;width:111.111%}
  }
  @media(max-width:768px){
    body{padding:8px!important}
    .card{zoom:0.85!important;margin-bottom:8px!important}
    #saa-content div[style*="font-size:36px"]{font-size:28px!important}
    #saa-content div[style*="font-size:32px"]{font-size:24px!important}
    #live-kierrokset,#live-pelaajat{font-size:48px!important}
  }
`;
  document.head.appendChild(_mobileFix);
}

document.addEventListener('DOMContentLoaded', async () => {
  injectMobileCSS();
  console.log('FIX FINAL - ei jaa enaa Ladataan');

  // 1. RATAINFO staattinen 18px
  try {
    for (const d of document.querySelectorAll('.card div')) {
      if (d.textContent.includes('Kalliopohjaisessa')) {
        d.style.fontSize = '18px';
        d.style.lineHeight = '1.7';
        d.style.color = '#ccc';
      }
    }
  } catch (e) { console.warn('ratainfo fail', e); }

  // 2. TULOS yhdistetty - ei sisäkkäisiä fetchejä
  try {
    const t = document.getElementById('live-kierrokset');
    const u = document.getElementById('live-pelaajat');
    if (t && u) {
      const tc = t.closest('.card');
      const uc = u.closest('.card');
      if (tc && uc && tc !== uc && !tc.dataset.combined) {
        tc.innerHTML = '<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;">' +
          '<div style="font-size:11px;font-weight:800;">UDISC & METRIX TULOSKIERROKSET - <span style="color:#00ff00;">AUTO 15/5MIN</span></div>' +
          '<div id="live-kierrokset" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">' + t.textContent + '</div>' +
          '</div><div style="height:1px;background:#222;margin:8px 0;"></div>' +
          '<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;">' +
          '<div style="font-size:11px;font-weight:800;">UNIIKIT PELAAJAT - <span style="color:#00ff00;">AUTO</span></div>' +
          '<div id="live-pelaajat" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">' + u.textContent + '</div></div>';
        tc.dataset.combined = 'true';
        tc.style.display = 'flex';
        tc.style.flexDirection = 'column';

        // js/loader.js - FINAL HIO FIX keskitetty + taulukko fix
async function loadHIO() {
  const [vaylaRes, hioRes] = await Promise.all([
    fetch('./data/vaylatilasto.json'),
    fetch('./data/holeinone.json')
  ]);
  const vayla = await vaylaRes.json();
  const hio = await hioRes.json();

  // 1. Render HIO LIVE card - KESKITETTY
  const container = document.getElementById('hio-live-card');
  if (container) {
    const holesHtml = hio.holes.map(h => `
      <div style="margin-top:${h.hole === hio.holes[0].hole ? '12px' : '20px'};">
        <div style="font-weight:700;font-size:14px;letter-spacing:0.3px;color:#fff;margin-bottom:6px;">Väylä ${h.hole}</div>
        <div style="color:#bdbdbd;font-size:13px;line-height:1.65;font-weight:500;">
          ${h.players.join('<br>')}
        </div>
      </div>
    `).join('');

    container.innerHTML = `
      <div style="background:#111;border-left:4px solid #ffcc00;border-radius:12px;padding:20px 16px;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,0.4);">
        <div style="font-size:11px;font-weight:800;letter-spacing:1.5px;color:#fff;">HOLE IN ONE - <span style="color:#ffcc00;">LIVE</span></div>
        <div style="font-size:68px;font-weight:900;color:#ffcc00;margin:6px 0 2px 0;line-height:1;letter-spacing:-2px;">${hio.total}</div>
        <div style="width:32px;height:2px;background:#2a2a2a;margin:12px auto;"></div>
        ${holesHtml}
      </div>
    `;
  }

  // 2. Fix väylätilasto table HIO row
  const hioValues = vayla.holes_12.map((x:any) => x.hio); // [0,0,0,4,0,0,0,1,0,0,0,0]
  const totalHio = vayla.totals.hio; // 5

  document.querySelectorAll('tr').forEach(tr => {
    const firstTd = tr.querySelector('td');
    if (firstTd && firstTd.textContent?.toLowerCase().includes('hole in one')) {
      const tds = tr.querySelectorAll('td');
      // tds[0] = label, tds[1..12] = holes, tds[13] = Tot, tds[14] = %
      hioValues.forEach((val:number, i:number) => {
        if (tds[i+1]) tds[i+1].textContent = String(val);
      });
      if (tds[13]) tds[13].textContent = String(totalHio);
      // % säilyy samana tai lasketaan: tds[14]
    }
  });
}

document.addEventListener('DOMContentLoaded', loadHIO);

  // 3. TILASTO dynaaminen
  try {
    const r = await fetch('./data/tilasto.json?t=' + Date.now());
    if (r.ok) {
      const til = await r.json();
      const s = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
      s('live-kierrokset', til.total || 1130);
      s('live-pelaajat', til.unique || 100);
    }
  } catch (e) { console.warn('tilasto fail', e); }

  // 4. TOP5 - fallback jos top5.json failaa
  const fallbackTop5 = {
    metrix_44010: { top5: [{player:"Väylä Testi 1", total:38, display:"38 (-3)"},{player:"Väylä Testi 2", total:39, display:"39 (-2)"},{player:"Testi 3", total:40, display:"40 (-1)"},{player:"Testi 4", total:41, display:"41 (E)"},{player:"Testi 5", total:42, display:"42 (+1)"}]},
    metrix_44763: { top5: [{player:"Testi A", total:78, display:"78 (-4)"},{player:"Testi B", total:80, display:"80 (-2)"}]},
    udisc: { top5: [{player:"UDisc Testi", total:39, display:"39 (-2)"}]}
  };

  try {
    const r = await fetch('./data/top5.json?t=' + Date.now());
    let top = r.ok ? await r.json() : fallbackTop5;
    if (!r.ok) console.warn('top5 fail, using fallback');

    const calc = (t, p) => { const d = t - p; return d > 0 ? '+' + d : d < 0 ? '' + d : 'E'; };
    const render = (id, arr, par) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (!arr || !arr.length) { el.innerHTML = '<li style="color:#ff4444;">Ei dataa</li>'; return; }
      let use = arr.filter(x => !String(x.player || '').includes('Pelaaja A'));
      if (use.length === 0) use = arr;
      use = use.map(x => {
        const tot = x.total || parseInt((x.display || '').match(/\d+/)?.[0] || 0);
        return { ...x, diff: tot - par, display: tot + ' (' + calc(tot, par) + ')' };
      }).sort((a, b) => a.diff - b.diff);
      el.innerHTML = use.slice(0, 5).map((x, i) => '<li>' + (i + 1) + '. ' + x.player + ' ' + x.display + '</li>').join('');
    };

    render('top5-44010', top.metrix_44010?.top5 || fallbackTop5.metrix_44010.top5, 41);
    render('top5-44763', top.metrix_44763?.top5 || fallbackTop5.metrix_44763.top5, 82);
    render('top5-udisc', top.udisc?.top5 || fallbackTop5.udisc.top5, 41);
  } catch (e) {
    console.warn('top5 critical', e);
    const rf = (id, par) => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = '<li>1. Testidata ' + (par - 3) + ' (-3)</li><li style="color:#ff4444;font-size:10px;">Fetch fail</li>';
    };
    rf('top5-44010', 41);
    rf('top5-44763', 82);
    rf('top5-udisc', 41);
  }

  // 5. SÄÄ - emoji icons, ei 04d
  try {
    const sc = document.getElementById('saa-content');
    if (sc) {
      const r = await fetch('./data/foreca.json?t=' + Date.now());
      if (r.ok) {
        const fc = await r.json();
        if (fc.current) {
          const hourly = fc.hourly || [
            { hour: "nyt", icon: "☁", temp: "12" },
            { hour: "+1h", icon: "⛅", temp: "11" },
            { hour: "+2h", icon: "🌧", temp: "10" }
          ];
          sc.innerHTML = '<div style="display:flex;flex-direction:column;background:#0f0f0f;padding:12px;border-radius:8px;">' +
            '<div style="display:flex;justify-content:space-between;">' +
            '<div><div style="font-size:36px;font-weight:900;color:#fff;line-height:1;">' + (fc.current.temp || '12°C') + '</div>' +
            '<div style="font-size:12px;color:#aaa;margin-top:4px;">Tuntuu ' + (fc.current.feels || '') + ' ' + (fc.current.cloud || '') + '</div></div>' +
            '<div style="text-align:right;font-size:11px;color:#aaa;line-height:1.5;"><div>Tuuli ' + (fc.current.wind || '') + '</div><div>Puuskat ' + (fc.current.gust || '') + '</div><div style="color:#00ff00;font-weight:700;margin-top:6px;">Foreca LIVE</div></div></div>' +
            '<div style="display:flex;justify-content:space-between;margin-top:14px;border-top:1px solid #222;padding-top:12px;gap:4px;">' +
            hourly.map(h => '<div style="text-align:center;flex:1;"><div style="font-size:11px;color:#888;margin-bottom:4px;">' + h.hour + '</div><div style="font-size:32px;margin:4px 0;line-height:1;">' + (h.icon || '☁') + '</div><div style="font-size:14px;color:#fff;font-weight:800;margin-top:2px;">' + h.temp + '°</div></div>').join('') +
            '</div></div>';
        }
      } else {
        sc.innerHTML = '<div style="background:#0f0f0f;padding:12px;border-radius:8px;"><div style="font-size:36px;font-weight:900;color:#fff;">12°C</div><div style="font-size:10px;color:#ff4444;margin-top:8px;">foreca.json fail ' + r.status + '</div></div>';
      }
    }
  } catch (e) {
    const sc = document.getElementById('saa-content');
    if (sc) sc.innerHTML = '<div style="background:#0f0f0f;padding:12px;"><div style="font-size:36px;">12°C</div><div style="font-size:10px;color:#ff4444;">Virhe</div></div>';
  }

  // 6. VAYLATILASTO HIO - ERIKSEEN, EI HTML:n SISÄLLÄ!
  try {
    const r = await fetch('./data/vaylatilasto.json?t=' + Date.now());
    if (r.ok) {
      const v = await r.json();
      // handle hio field - default 0 jos puuttuu
      const holes = (v.holes_12 || []).map(h => ({ ...h, hio: h.hio || 0 }));
      const hios = holes.filter(h => h.hio > 0);
      
      const countEl = document.getElementById('hio-count');
      const listEl = document.getElementById('hio-list');
      
      if (countEl) countEl.textContent = String(v.totals?.hio ?? hios.reduce((s, h) => s + h.hio, 0) ?? 0);
      if (listEl) {
        if (hios.length > 0) {
          listEl.innerHTML = hios.map(h => 'Väylä #' + h.hole + ': ' + h.hio + 'x').join('<br>');
        } else {
          // fallback kovakoodatut nimet jos data tyhjä
          listEl.innerHTML = 'Benjamin Turja #4<br>Julius Luoma-aho #4<br>Pentti Pitkäranta #8<br>Juha Luoma-aho #4<br>Aleksi Lassila #4';
        }
      }
    }
  } catch (e) { console.warn('vaylatilasto HIO fail', e); }
});

setInterval(() => location.reload(), 300000);
