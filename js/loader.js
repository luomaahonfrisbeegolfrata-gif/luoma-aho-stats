// Päivitetty loader tukemaan uutta yhdistettyä korttia + Hole in one korttia
const DATA_BASE = 'data/';
const v = () => `?v=${Date.now()}`;
const OPTS = { cache: 'no-store' };
async function fetchJSON(f){ try{ const r=await fetch(DATA_BASE+f+v(),OPTS); if(!r.ok) throw 0; return await r.json(); }catch(e){ console.warn(f,e); return null; } }
function setH(id,h){ const el=document.getElementById(id); if(el) el.innerHTML=h; }

async function loadAll(){
  // Hae data
  const foreca = await fetchJSON('foreca.json');
  const stats = await fetchJSON('stats.json');
  const tilasto = await fetchJSON('tilasto.json');
  const top5 = await fetchJSON('top5.json');
  const hio = await fetchJSON('holeinone.json');
  const vayla = await fetchJSON('vaylatilasto.json') || await fetchJSON('ratatilasto.json');

  // SÄÄ
  if(foreca){
    const t = foreca.temperature ?? foreca.temp ?? 12;
    setH('saa-temp', Math.round(t)+'°C');
    setH('saa-data', (foreca.description||'')+'<br><small>Foreca LIVE</small>');
  }

  // UDISC & METRIX yhdistetty
  if(stats || tilasto){
    const total = stats?.total || stats?.kierrokset || tilasto?.total || 1130;
    const uniq = stats?.unique_players || tilasto?.uniikit || 100;
    setH('total-rounds', total);
    setH('unique-players', uniq);
    const d1 = stats?.desc || 'UDisc 428 + Metrix 431+19 702 = 1130 OIKEIN';
    const d2 = stats?.unique_desc || 'UDisc 67 + Metrix ~60 - päällekkäisyydet ~100';
    setH('total-rounds-desc', d1);
    setH('unique-players-desc', d2);
    setH('peliaika', (stats?.peliaika||'1481h'));
    setH('askelmaara', (stats?.askelmaara||'3,100,890'));
    setH('kilometrit', (stats?.kilometrit||'2260 km'));
  }

  // HOLE IN ONE - uusi kortti
  if(hio){
    const tot = Array.isArray(hio) ? hio.length : (hio.total||hio.count||1);
    setH('hio-total', tot);
    const renderHio = (arr)=>{
      if(!arr || !arr.length) return '<div class="hio-item">Ei holareita vielä</div>';
      return arr.slice(0,10).map(x=>{
        if(typeof x==='string') return `<div class="hio-item">${x}</div>`;
        return `<div class="hio-item">${x.player||x.name||''} - Väylä ${x.hole||x.vayla||'?'} ${x.date||''}</div>`;
      }).join('');
    };
    const list = Array.isArray(hio) ? hio : (hio.list||hio.holarit||[]);
    setH('hole-in-one-data', renderHio(list));
  } else {
    setH('hio-total','1');
    setH('hole-in-one-data','<div class="hio-item">Väylä 4 - 1kpl - 0.1%</div>');
  }

  // METRIX + UDISC listat
  const renderList = (arr)=>{
    if(!arr || !arr.length) return 'Ladataan...';
    return arr.slice(0,12).map((r,i)=>{
      const name = r.name||r.player|| (typeof r==='string'?r:JSON.stringify(r).slice(0,30));
      const sc = r.score||r.tulos||'';
      return `<div class="row"><span>${i+1}. ${name}</span><span>${sc}</span></div>`;
    }).join('');
  };
  if(tilasto || top5){
    const d = tilasto||{};
    setH('metrix-44010-data', renderList(d['44010']||d.metrix_44010||top5||[]));
    setH('metrix-44763-data', renderList(d['44763']||d.metrix_44763||[]));
    setH('udisc-data', renderList(d.udisc||[]));
  }

  // VÄYLÄTILASTO
  let data = vayla;
  if(!data || Object.keys(data).length<3){
    data = { pituus:[125,103,72,57,94,96,103,80,116,85,197,120], par:[4,3,3,3,3,3,3,3,4,3,5,4], avg:[4.45,3.77,3.45,3.42,3.55,4.18,3.79,3.33,4.53,4.20,6.15,4.23], difficulty:[4,8,5,3,7,11,9,2,6,12,10,1], hole_in_one:[0,0,0,1,0,0,0,0,0,0,0,0], birdie:[14,4,14,25,3,4,10,19,8,6,11,24], par0:[59,52,77,32,69,38,53,73,55,34,31,67], bogey:[31,65,34,64,46,49,51,38,38,48,48,35], dbl_bogey:[18,16,14,6,11,24,21,7,12,38,31,6], tpl_bogey:[3,3,2,4,5,15,6,1,4,9,11,1], other:[1,1,0,1,1,8,1,0,5,4,5,1] };
  }
  buildVayla(data);

  const lu = document.getElementById('last-update');
  if(lu) lu.textContent = new Date().toLocaleString('fi-FI');
}

function avgColor(a,p){ const d=a-p; if(d<0.3) return 'bg-green'; if(d<0.6) return 'bg-yellow'; if(d<1) return 'bg-orange'; return 'bg-red'; }
function diffColor(r){ if(r<=2) return 'bg-green'; if(r<=5) return 'bg-yellow'; if(r<=9) return 'bg-orange'; return 'bg-red'; }

function buildVayla(d){
  const body=document.getElementById('vaylatilasto-body'); if(!body) return;
  const get=k=>d[k]||[];
  let pituus=get('pituus'), par=get('par'), avg=get('avg'), diff=get('difficulty'), hio=get('hole_in_one'), birdie=get('birdie'), par0=get('par0'), bogey=get('bogey'), dbl=get('dbl_bogey'), tpl=get('tpl_bogey'), other=get('other');
  const tot=(arr)=>arr.reduce((a,b)=>a+(b||0),0);
  const grand=tot(hio)+tot(birdie)+tot(par0)+tot(bogey)+tot(dbl)+tot(tpl)+tot(other)||1;
  const pct=v=>((v/grand)*100).toFixed(1)+'%';
  const row=(label,arr,total,showPct)=>{
    let h=`<tr><td><strong>${label}</strong></td>`;
    arr.forEach((val,i)=>{ let cls=''; if(label==='Avg') cls=avgColor(val,par[i]||3); if(label==='Difficulty') cls=diffColor(val); h+=`<td class="${cls} avg-cell">${typeof val==='number'?(label==='Avg'?val.toFixed(2):val):val}</td>`; });
    h+=`<td>${typeof total==='number'? (Number.isInteger(total)?total:total.toFixed(2)):total}</td><td>${showPct?pct(total):'-'}</td></tr>`; return h;
  };
  let html='';
  html+=row('Pituus',pituus.map(p=>p+'m'), tot(pituus)+'m', false);
  html+=row('Par',par, tot(par), false);
  html+=row('Avg',avg, tot(avg).toFixed(2), false);
  html+=row('Difficulty',diff, (tot(avg)-tot(par)).toFixed(2), false);
  html+=row('Hole in one',hio, tot(hio), true);
  html+=row('Birdie -1',birdie, tot(birdie), true);
  html+=row('Par 0',par0, tot(par0), true);
  html+=row('Bogey 1',bogey, tot(bogey), true);
  html+=row('Dbl Bogey 2',dbl, tot(dbl), true);
  html+=row('Tpl Bogey 3',tpl, tot(tpl), true);
  html+=row('Other >3',other, tot(other), true);
  body.innerHTML=html;
}

document.addEventListener('DOMContentLoaded',()=>{ loadAll(); setInterval(loadAll, 60*1000); });
