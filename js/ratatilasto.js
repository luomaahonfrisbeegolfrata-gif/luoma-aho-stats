async function loadAll(){
  const PAR_44010=41;
  const PAR_44763=82;
  const calc=(total,par)=>{
    const diff=total-par;
    if(diff>0) return {diff, score:`+${diff}`, display:`${total} (+${diff})`};
    if(diff<0) return {diff, score:`${diff}`, display:`${total} (${diff})`};
    return {diff:0, score:'E', display:`${total} (E)`};
  };

  // 1. TILASTO
  try{
    const til=await fetch('./data/tilasto.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error(); return r.json();});
    const el=id=>document.getElementById(id);
    if(el('live-kierrokset') && til.total) el('live-kierrokset').textContent=til.total;
    if(el('live-pelaajat') && til.unique) el('live-pelaajat').textContent=til.unique;
    if(el('live-aika') && til.playtime) el('live-aika').textContent=til.playtime+'h';
    if(el('live-askeleet') && til.steps) el('live-askeleet').textContent=til.steps.toLocaleString('fi-FI');
    if(el('live-km') && til.km) el('live-km').textContent=til.km+' km';
  }catch(e){}

  // 2. TOP5 - OIKEAT KAIKKI 3, PAR 41 yli=+, alle=-
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error(); return r.json();});
    const render=(id,arr,par)=>{
      const e=document.getElementById(id); if(!e) return;
      if(!arr||!arr.length){e.innerHTML='<li style="color:#888; font-size:11px;">Haetaan 5 parasta...</li>'; return;}
      // Suodata vain Pelaaja A-E fake, @kantanen8 on OIKEA UDisc Pro
      let use=arr.filter(x=>!x.player.includes('Pelaaja A') && !x.player.includes('Pelaaja B') && !x.player.includes('Pelaaja C') && !x.player.includes('Pelaaja D') && !x.player.includes('Pelaaja E') && !x.player.includes('Pelaaja X') && !x.player.includes('Pelaaja Y') && !x.player.includes('UDisc #5'));
      if(use.length===0) use=arr;
      use=use.map(x=>{
        const total=x.total||parseInt((x.display||'').match(/\d+/)?.[0]||0);
        if(!total) return x;
        const d=calc(total, par);
        return {...x, total, diff:d.diff, score:d.score, display:d.display, sort:d.diff};
      }).sort((a,b)=>a.diff-b.diff);
      e.innerHTML=use.slice(0,5).map((x,i)=>`<li style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #222;"><span>${i+1}. ${x.player} ${x.display}</span></li>`).join('');
    };
    render('top5-44010', top.metrix_44010?.top5, PAR_44010);
    render('top5-44763', top.metrix_44763?.top5, PAR_44763);
    render('top5-udisc', top.udisc?.top5, PAR_44010);
  }catch(e){console.log('top5',e);}

  // 3. SÄÄ - KORJATTU, ei enää Ladataan...
  const sc=document.getElementById('saa-content');
  if(sc){
    try{
      const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error(); return r.json();});
      if(fc.current && fc.hourly){
        sc.innerHTML=`
          <div style="display:flex; flex-direction:column; height:175px; background:#0f0f0f; padding:8px; border-radius:8px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div><div style="font-size:32px; font-weight:900; color:#fff; line-height:1;">${fc.current.temp}</div><div style="font-size:10px; color:#888; margin-top:2px;">Tuntuu ${fc.current.feels} • ${fc.current.cloud}</div></div>
              <div style="text-align:right; font-size:10px; color:#aaa; line-height:1.4;"><div>Tuuli ${fc.current.wind}</div><div>Puuskat ${fc.current.gust}</div><div>Sade ${fc.current.precip}</div><div style="color:#00ff00; font-weight:700; margin-top:4px;">Foreca LIVE</div></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:12px; border-top:1px solid #222; padding-top:8px;">
              ${fc.hourly.map(h=>`<div style="text-align:center; flex:1;"><div style="font-size:9px; color:#888;">${h.hour}</div><div style="font-size:20px; margin:2px 0;">${h.icon}</div><div style="font-size:11px; color:#fff; font-weight:800;">${h.temp}°</div></div>`).join('')}
            </div>
            <div style="margin-top:auto; border-top:1px solid #222; padding-top:6px; display:flex; justify-content:space-between; font-size:9px; color:#666;">
              ${fc.daily.map(d=>`<span>${d.day} ${d.max}/${d.min}°</span>`).join('')}
            </div>
          </div>
        `;
      }
    }catch(e){
      console.log('foreca',e);
      if(sc.textContent.includes('Ladataan')) sc.innerHTML='<div style="color:#fff;">12°C<br><span style="font-size:10px; color:#888;">Foreca haetaan 5min</span></div>';
    }
  }

  // 4. Väylätilasto vari
  try{
    const rat=await fetch('./data/ratatilasto.json?t='+Date.now()).then(r=>r.json());
    document.querySelectorAll('table').forEach(table=>{
      if(table.textContent.includes('Vayla')){
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
