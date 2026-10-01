async function loadAll(){
  const PAR_44010=41, PAR_44763=82;
  const calc=(t,p)=>{const d=t-p; return d>0?{diff:d, display:`${t} (+${d})`}:d<0?{diff:d, display:`${t} (${d})`}:{diff:0, display:`${t} (E)`};}
  try{
    const til=await fetch('./data/tilasto.json?t='+Date.now()).then(r=>r.json());
    const el=id=>document.getElementById(id);
    if(el('live-kierrokset')) el('live-kierrokset').textContent=til.total||1130;
    if(el('live-pelaajat')) el('live-pelaajat').textContent=til.unique||100;
    if(el('live-aika')) el('live-aika').textContent=(til.playtime||'1004h');
    if(el('live-askeleet')) el('live-askeleet').textContent=(til.steps||1300000).toLocaleString('fi-FI');
    if(el('live-km')) el('live-km').textContent=(til.km||970)+' km';
  }catch(e){}
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>r.json());
    const render=(id,arr,par)=>{
      const e=document.getElementById(id); if(!e) return;
      let use=arr.filter(x=>!x.player.includes('Pelaaja A'));
      use=use.map(x=>{const tot=x.total||parseInt((x.display||'').match(/\d+/)?.[0]||0); const d=calc(tot,par); return {...x, display:d.display, sort:d.diff};}).sort((a,b)=>a.diff-b.diff);
      e.innerHTML=use.slice(0,5).map((x,i)=>`<li>${i+1}. ${x.player} ${x.display}</li>`).join('');
    };
    render('top5-44010', top.metrix_44010?.top5, PAR_44010);
    render('top5-44763', top.metrix_44763?.top5, PAR_44763);
    render('top5-udisc', top.udisc?.top5, PAR_44010);
  }catch(e){}
  const sc=document.getElementById('saa-content');
  if(sc){ try{ const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>r.json()); if(fc.current && fc.hourly){ sc.innerHTML=`<div style="margin-top:8px;"><div style="font-size:28px;font-weight:900;">${fc.current.temp}</div><div style="font-size:10px;color:#888;">Tuntuu ${fc.current.feels} • ${fc.current.cloud}</div><div style="display:flex;gap:8px;margin-top:8px;">${fc.hourly.slice(0,4).map(h=>`<div style="text-align:center;"><div style="font-size:9px;color:#888;">${h.hour}</div><div>${h.icon}</div><div style="font-size:11px;font-weight:800;">${h.temp}°</div></div>`).join('')}</div></div>`; } }catch(e){ sc.textContent='12°C Foreca'; } }
  try{
    const hio=await fetch('./data/holeinone.json?t='+Date.now()).then(r=>r.json());
    const c=document.getElementById('hio-count'), l=document.getElementById('hio-list');
    if(c) c.textContent=hio.count||0;
    if(l && hio.players) l.innerHTML=hio.players.map(p=>`${p.player} #${p.hole}`).join('<br>');
  }catch(e){}
}
loadAll(); setInterval(loadAll,300000);
