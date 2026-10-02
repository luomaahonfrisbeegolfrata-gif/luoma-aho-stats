// js/loader.js - TÄYSIN DYNAAMINEN GitHub-versio
// Kaikki data haetaan data/ kansiosta joka päivittyy GitHub Actionsilla (foreca auto 5min + stats auto)
// Ei kovakoodattuja arvoja - fallback vain jos GitHub API nurin

const DATA_BASE = 'data/';
const bust = () => `?v=${Date.now()}`;
const OPTS = { cache: 'no-store' };

async function fetchJSON(file) {
  try {
    const res = await fetch(DATA_BASE + file + bust(), OPTS);
    if (!res.ok) throw new Error(`${file} ${res.status}`);
    return await res.json();
  } catch (e) {
    console.warn(`[AUTO] ${file} ei ladannut:`, e);
    return null;
  }
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el && text !== undefined && text !== null) el.textContent = text;
}
function setHTML(id, html) {
  const el = document.getElementById(id);
  if (el && html !== undefined) el.innerHTML = html;
}

async function loadAllDynamic() {
  // 1. Hae kaikki JSONit rinnakkain - TÄYSIN DYNAAMINEN
  const [foreca, stats, tilasto, top5, hio, vaylaJson, ratatilasto] = await Promise.all([
    fetchJSON('foreca.json'),
    fetchJSON('stats.json'),
    fetchJSON('tilasto.json'),
    fetchJSON('top5.json'),
    fetchJSON('holeinone.json'),
    fetchJSON('vaylatilasto.json'),
    fetchJSON('ratatilasto.json')
  ]);

  // 2. SÄÄ - Foreca AUTO
  if (foreca) {
    const temp = foreca.temperature ?? foreca.temp ?? foreca.current?.temp ?? foreca.main?.temp ?? null;
    if (temp !== null) setText('saa-temp', Math.round(temp) + '°C');
    const desc = foreca.description || foreca.text || foreca.condition || foreca.current?.description || 'Foreca LIVE';
    setText('saa-desc', desc);
    if (foreca.html) setHTML('foreca-widget', foreca.html);
  }

  // 3. UDISC & METRIX TULOSKIERROKSET + UNIIKIT - yhdistetty kortti dynaamisesti
  // stats.json tai tilasto.json sisältää total ja unique
  const totalRounds = stats?.total ?? stats?.kierrokset ?? tilasto?.total ?? tilasto?.rounds ?? null;
  const uniquePlayers = stats?.unique ?? stats?.unique_players ?? tilasto?.unique ?? null;
  
  if (totalRounds !== null) setText('total-rounds', totalRounds);
  if (uniquePlayers !== null) setText('unique-players', uniquePlayers);
  
  if (stats?.total_desc) setText('total-desc', stats.total_desc);
  if (stats?.unique_desc) {
    const el = document.getElementById('unique-players-desc');
    if (el) el.textContent = stats.unique_desc;
  }

  // 4. PELIAIKA / ASKELMÄÄRÄ / KILOMETRIT - dynaamisesti stats.json:sta
  if (stats) {
    if (stats.peliaika) setText('peliaika', stats.peliaika);
    if (stats.askelmaara) setText('askelmaara', stats.askelmaara);
    if (stats.kilometrit) setText('kilometrit', stats.kilometrit);
    if (stats.peliaika_desc) setText('peliaika-desc', stats.peliaika_desc);
    if (stats.askelmaara_desc) setText('askelmaara-desc', stats.askelmaara_desc);
  }

  // 5. HOLE IN ONE - dynaaminen holeinone.json:sta
  if (hio) {
    const list = Array.isArray(hio) ? hio : (hio.list || hio.holarit || hio.hole_in_ones || []);
    const total = list.length || hio.total || hio.count || 0;
    setText('hio-total', total);
    if (list.length > 0) {
      const html = list.slice(0, 10).map(item => {
        if (typeof item === 'string') return `<div class="hio-item">${item}</div>`;
        const player = item.player || item.name || item.pelaaja || 'Tuntematon';
        const hole = item.hole || item.vayla || '?';
        const date = item.date || item.pvm || '';
        return `<div class="hio-item">${player} - Väylä ${hole} ${date}</div>`;
      }).join('');
      setHTML('hio-list', html);
    }
  }

  // 6. METRIX 44010, 44763, UDISC - dynaamiset tuloslistat
  function renderTulosList(id, data) {
    const el = document.getElementById(id);
    if (!el) return;
    if (!data || (Array.isArray(data) && data.length === 0)) {
      el.innerHTML = '<div style="color:#555;font-size:11px">Odottaa GitHub päivitystä (AUTO 1s/5min)...</div>';
      return;
    }
    const arr = Array.isArray(data) ? data : (data.results || data.list || data.players || []);
    if (arr.length === 0) {
      el.innerHTML = `<pre style="font-size:10px;white-space:pre-wrap">${JSON.stringify(data).slice(0,800)}</pre>`;
      return;
    }
    el.innerHTML = arr.slice(0, 15).map((r, i) => {
      if (typeof r === 'string') return `<div class="row"><span>${i+1}. ${r}</span></div>`;
      const name = r.name || r.player || r.pelaaja || r.nick || 'Pelaaja';
      const score = r.score ?? r.tulos ?? r.total ?? r.result ?? '';
      const diff = r.diff ?? r['+/-'] ?? '';
      return `<div class="row"><span>${i+1}. ${name}</span><span>${score} ${diff}</span></div>`;
    }).join('');
  }

  // Metrix 44010 ja 44763 voivat olla tilasto.json:ssa avaimilla tai erillisissä tiedostoissa
  if (tilasto || top5) {
    const m44010_data = tilasto?.['44010'] || tilasto?.metrix_44010 || top5?.['44010'] || top5?.metrix_44010 || null;
    const m44763_data = tilasto?.['44763'] || tilasto?.metrix_44763 || top5?.['44763'] || top5?.metrix_44763 || null;
    const udisc_data = tilasto?.udisc || tilasto?.UDisc || top5?.udisc || null;

    if (m44010_data) renderTulosList('m44010', m44010_data);
    else {
      // Yritä erillinen tiedosto metrix_44010.json jos on
      const m1 = await fetchJSON('metrix_44010.json');
      if (m1) renderTulosList('m44010', m1);
    }

    if (m44763_data) renderTulosList('m44763', m44763_data);
    else {
      const m2 = await fetchJSON('metrix_44763.json');
      if (m2) renderTulosList('m44763', m2);
    }

    if (udisc_data) renderTulosList('udisc', udisc_data);
    else {
      const u = await fetchJSON('udisc.json');
      if (u) renderTulosList('udisc', u);
    }
  }

  // 7. VÄYLÄTILASTO - KUVA + TAULUKKO molemmat dynaamisia
  // Kuva päivittyy GitHub Actionsilla (vaylatilasto_fetcher.py generoi data/vaylatilasto.png)
  const vaylaImg = document.getElementById('vayla-img');
  if (vaylaImg) {
    // Cache-buster jotta aina tuore kuva GitHubista
    vaylaImg.src = 'data/vaylatilasto.png' + bust();
    vaylaImg.style.display = 'block';
    vaylaImg.onerror = () => {
      // Jos kuva ei löydy (esim. .gitignore estää), näytä taulukko JSON:sta
      console.warn('vaylatilasto.png ei löytynyt, näytetään taulukko');
      vaylaImg.style.display = 'none';
      document.getElementById('vayla-wrap')?.classList.add('show-table');
      if (vaylaJson) buildVaylaTable(vaylaJson);
      else buildVaylaTable(ratatilasto);
    };
    vaylaImg.onload = () => {
      // Kuva ladattu onnistuneesti, piilota taulukko
      const table = document.getElementById('vayla-table');
      if (table) table.style.display = 'none';
    };
  }

  // Taulukko varalle - rakennetaan JSON:sta dynaamisesti
  if (vaylaJson) buildVaylaTable(vaylaJson);
  else if (ratatilasto) buildVaylaTable(ratatilasto);

  // Päivitetty leima
  const now = new Date().toLocaleString('fi-FI', { timeZone: 'Europe/Helsinki' });
  setText('last-update', now);
  const status = document.getElementById('status');
  if (status) status.innerHTML = `Päivitetty: ${now} | Lähde: UDisc + Metrix AUTO | GitHub Pages LIVE`;

  console.log('[AUTO] Kaikki data ladattu dynaamisesti GitHubista');
}

function buildVaylaTable(d) {
  if (!d || typeof d !== 'object') return;
  const body = document.getElementById('vayla-body');
  if (!body) return;

  // Tuki eri JSON rakenteille
  const getArr = (keys) => {
    for (const k of keys) {
      if (d[k] && Array.isArray(d[k])) return d[k];
      if (d[k.toLowerCase()] && Array.isArray(d[k.toLowerCase()])) return d[k.toLowerCase()];
    }
    return [];
  };

  let pituus = getArr(['pituus', 'length', 'distance']);
  let par = getArr(['par']);
  let avg = getArr(['avg', 'average', 'keskiarvo']);
  let diff = getArr(['difficulty', 'vaikeus']);
  let hio = getArr(['hole_in_one', 'hio']);
  let birdie = getArr(['birdie']);
  let par0 = getArr(['par0', 'par_0']);
  let bogey = getArr(['bogey']);
  let dbl = getArr(['dbl_bogey', 'dbl', 'double_bogey']);
  let tpl = getArr(['tpl_bogey', 'tpl', 'triple_bogey']);
  let other = getArr(['other', 'muut']);

  // Jos data on objekti jossa avaimet 1,2,3...
  if (pituus.length === 0 && d['1']) {
    const nums = Object.keys(d).filter(k => !isNaN(parseInt(k))).sort((a,b)=>parseInt(a)-parseInt(b)).slice(0,12);
    pituus = nums.map(k => d[k].pituus || d[k].length || 0);
    par = nums.map(k => d[k].par || 3);
    avg = nums.map(k => d[k].avg || 0);
    diff = nums.map(k => d[k].difficulty || 0);
    hio = nums.map(k => d[k].hio || 0);
    birdie = nums.map(k => d[k].birdie || 0);
    par0 = nums.map(k => d[k].par0 || 0);
    bogey = nums.map(k => d[k].bogey || 0);
    dbl = nums.map(k => d[k].dbl || 0);
    tpl = nums.map(k => d[k].tpl || 0);
    other = nums.map(k => d[k].other || 0);
  }

  if (pituus.length === 0) return; // ei dataa

  const tot = arr => arr.reduce((a,b) => a + (Number(b)||0), 0);
  const grand = tot(hio)+tot(birdie)+tot(par0)+tot(bogey)+tot(dbl)+tot(tpl)+tot(other) || 1;
  const pct = v => ((v/grand)*100).toFixed(1)+'%';
  const colAvg = (a,p) => { const df=a-p; if(df<0.3) return 'g'; if(df<0.6) return 'y'; if(df<1) return 'o'; return 'r'; };
  const colDiff = r => { if(r<=2) return 'g'; if(r<=5) return 'y'; if(r<=9) return 'o'; return 'r'; };

  const row = (label, arr, total, showPct) => {
    let h = `<tr><td><strong>${label}</strong></td>`;
    arr.forEach((val,i) => {
      let cls = '';
      if (label==='Avg') cls = colAvg(val, par[i]||3);
      if (label==='Difficulty') cls = colDiff(val);
      const display = typeof val==='number' ? (label==='Avg'?val.toFixed(2):val) : val;
      h += `<td class="${cls} c">${display}</td>`;
    });
    h += `<td>${typeof total==='number' ? (Number.isInteger(total)?total:total.toFixed(2)) : total}</td>`;
    h += `<td>${showPct ? pct(total) : '-'}</td></tr>`;
    return h;
  };

  let html = '';
  html += row('Pituus', pituus.map(p=>typeof p==='number'?p+'m':p), tot(pituus)+'m', false);
  html += row('Par', par, tot(par), false);
  html += row('Avg', avg, tot(avg).toFixed(2), false);
  html += row('Difficulty', diff, (tot(avg)-tot(par)).toFixed(2), false);
  html += row('Hole in one', hio, tot(hio), true);
  html += row('Birdie -1', birdie, tot(birdie), true);
  html += row('Par 0', par0, tot(par0), true);
  html += row('Bogey 1', bogey, tot(bogey), true);
  html += row('Dbl Bogey 2', dbl, tot(dbl), true);
  html += row('Tpl Bogey 3', tpl, tot(tpl), true);
  html += row('Other >3', other, tot(other), true);

  body.innerHTML = html;
}

// Käynnistä ja auto-refresh 60s välein (GitHub Actions päivittää taustalla 1s/5min)
document.addEventListener('DOMContentLoaded', () => {
  loadAllDynamic();
  setInterval(loadAllDynamic, 60 * 1000);
});
