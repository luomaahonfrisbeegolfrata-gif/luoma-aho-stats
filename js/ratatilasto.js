// KIRURGIENEN KORJAUS - EI KOSKE INDEX.HTML:ÄÄ
// Yhdistää 2 korttia JS:llä lennossa, layout 100% sama
async function loadAll(){
  const PAR_44010=41, PAR_44763=82;
  const calc=(t,p)=>{const d=t-p; return d>0?{diff:d, display:`${t} (+${d})`}:d<0?{diff:d, display:`${t} (${d})`}:{diff:0, display:`${t} (E)`};}

  // === 1. KIRURGIENEN YHDISTÄMINEN ILMAN INDEX.HTML MUUTOSTA ===
  try{
    const tulosEl = document.getElementById('live-kierrokset');
    const uniikitEl = document.getElementById('live-pelaajat');
    if(tulosEl && uniikitEl){
      const tulosCard = tulosEl.closest('.card') || tulosEl.parentElement;
      const uniikitCard = uniikitEl.closest('.card') || uniikitEl.parentElement;
      
      if(tulosCard && uniikitCard && tulosCard !== uniikitCard && !tulosCard.dataset.combined){
        // Tallenna uniikit sisältö
        const uniikitHTML = uniikitEl.outerHTML;
        const uniikitLabel = uniikitCard.querySelector('[class*="label"], div:first-child')?.textContent || 'UNIIKIT PELAAJAT - AUTO';
        
        // Yhdistä tuloskorttiin: säilytä alkuperäinen 1130 ylhäällä, lisää 100 alhaalle
        // Poista turha info-teksti jos haluat isommat luvut
        const tulosLabel = tulosCard.querySelector('[class*="label"], div:first-child')?.innerHTML || 'UDISC & METRIX TULOSKIERROKSET - AUTO 15/5MIN';
        
        // Rakenna yhdistetty ilman info-tekstiä - isot luvut
        tulosCard.innerHTML = `
          <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;">
            <div style="font-size:11px;font-weight:600;letter-spacing:0.5px;">UDISC & METRIX TULOSKIERROKSET - <span style="color:#00ff00;">AUTO 15/5MIN</span></div>
            <div id="live-kierrokset" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">${tulosEl.textContent}</div>
          </div>
          <div style="height:1px;background:#222;margin:8px 0;"></div>
          <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;">
            <div style="font-size:11px;font-weight:600;letter-spacing:0.5px;">UNIIKIT PELAAJAT - <span style="color:#00ff00;">AUTO</span></div>
            <div id="live-pelaajat" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">${uniikitEl.textContent}</div>
          </div>
        `;
        tulosCard.dataset.combined = 'true';
        tulosCard.style.display='flex';
        tulosCard.style.flexDirection='column';
        tulosCard.style.minHeight='180px';

        // Muuta oikea kortti (oli uniikit) -> HOLE IN ONE samassa paikassa
        uniikitCard.innerHTML = `
          <div style="font-size:11px;font-weight:800;letter-spacing:0.5px;text-align:center;">HOLE IN ONE - <span style="color:#ffcc00;"></span></div>
          <div id="hio-count" style="font-size:36px;font-weight:600;color:#ffcc00;line-height:1;margin:16px 0;text-align:center;">3</div>
          <div id="hio-list" style="font-size:15px;color:#aaa;line-height:1.8;text-align:center;">Ladataan HIO...</div>
          <div style="font-size:8px;color:#555;margin-top:8px;text-align:center;">Päivitä data/holeinone.json</div>
        `;
        uniikitCard.style.borderLeft='3px solid #ffcc00';
        uniikitCard.dataset.hio='true';
      }
    }
  }catch(e){ console.log('yhdistäminen', e); }

  // === 2. TILASTO - OIKEAT LUVUT ===
  try{
    const til=await fetch('./data/tilasto.json?t='+Date.now()).then(r=>r.json());
    const el=id=>document.getElementById(id);
    if(el('live-kierrokset')) el('live-kierrokset').textContent=til.total||1130;
    if(el('live-pelaajat')) el('live-pelaajat').textContent=til.unique||100;
    if(el('live-aika')) el('live-aika').textContent=(til.playtime||'1004h');
    if(el('live-askeleet')) el('live-askeleet').textContent=(til.steps||1300000).toLocaleString('fi-FI');
    if(el('live-km')) el('live-km').textContent=(til.km||970)+' km';
  }catch(e){}

  // === 3. TOP5 OIKEAT - PAR 41 yli=+, alle=- ===
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>r.json());
    const render=(id,arr,par)=>{
      const e=document.getElementById(id); if(!e) return;
      if(!arr||!arr.length){e.innerHTML='<li>Haetaan...</li>'; return;}
      let use=arr.filter(x=>!String(x.player).includes('Pelaaja A'));
      if(use.length===0) use=arr;
      use=use.map(x=>{const tot=x.total||parseInt((x.display||'').match(/\d+/)?.[0]||0); if(!tot) return x; const d=calc(tot,par); return {...x, display:d.display, sort:d.diff};}).sort((a,b)=>a.sort-b.sort);
      e.innerHTML=use.slice(0,5).map((x,i)=>`<li style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #222;"><span>${i+1}. ${x.player} ${x.display}</span></li>`).join('');
    };
    render('top5-44010', top.metrix_44010?.top5, PAR_44010);
    render('top5-44763', top.metrix_44763?.top5, PAR_44763);
    render('top5-udisc', top.udisc?.top5, PAR_44010);
    if(top.metrix_43119) render('top5-43119', top.metrix_43119?.top5, PAR_44010);
  }catch(e){ console.log('top5',e); }

  // === 4. SÄÄ ===
  const sc=document.getElementById('saa-content');
  if(sc){
    try{
      const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>r.json());
      if(fc.current && fc.hourly){
        sc.innerHTML=`<div style="display:flex;flex-direction:column;height:175px;background:#0f0f0f;padding:8px;border-radius:8px;"><div style="display:flex;justify-content:space-between;"><div><div style="font-size:32px;font-weight:900;color:#fff;line-height:1;">${fc.current.temp}</div><div style="font-size:10px;color:#888;">Tuntuu ${fc.current.feels} • ${fc.current.cloud}</div></div><div style="text-align:right;font-size:10px;color:#aaa;"><div>Tuuli ${fc.current.wind}</div><div>Puuskat ${fc.current.gust}</div><div style="color:#00ff00;font-weight:700;margin-top:4px;">Foreca LIVE</div></div></div><div style="display:flex;justify-content:space-between;margin-top:12px;border-top:1px solid #222;padding-top:8px;">${fc.hourly.map(h=>`<div style="text-align:center;flex:1;"><div style="font-size:9px;color:#888;">${h.hour}</div><div style="font-size:20px;margin:2px 0;">${h.icon}</div><div style="font-size:11px;color:#fff;font-weight:800;">${h.temp}°</div></div>`).join('')}</div></div>`;
      }
    }catch(e){}
  }

  // === 5. HOLE IN ONE MANUAALINEN ===
  try{
    const hio=await fetch('./data/holeinone.json?t='+Date.now()).then(r=>r.json());
    const c=document.getElementById('hio-count'), l=document.getElementById('hio-list');
    if(c) c.textContent=hio.count||hio.players?.length||0;
    if(l && hio.players) l.innerHTML=hio.players.slice(0,5).map(p=>`${p.player} #${p.hole}`).join('<br>');
  }catch(e){}

  // === 6. VÄYLÄTILASTO VARI ===
  try{
    const rat=await fetch('./data/ratatilasto.json?t='+Date.now()).then(r=>r.json());
    document.querySelectorAll('table').forEach(table=>{
      if(table.textContent.includes('Vayla')||table.textContent.includes('Avg')){
        const over=rat.Avg.map((a,i)=>a-rat.Par[i]);
        const sorted=[...over].sort((a,b)=>a-b);
        const col=o=> o<=sorted[2]?'#66BB6A':o<=sorted[6]?'#FFEB3B':o<=sorted[8]?'#FFA726':'#EF5350';
        table.querySelectorAll('tr').forEach(tr=>{
          const label=tr.querySelector('td, th')?.textContent.trim().toLowerCase();
          if(label==='avg' || label==='difficulty'){
            tr.querySelectorAll('td').forEach((td,i)=>{if(i>=1&&i<=12){td.style.background=col(over[i-1]); td.style.color='#000'; td.style.fontWeight='800';}});
          }
        });
      }
    });
  }catch(e){}
}
loadAll(); setInterval(loadAll,300000);
