async function loadAll(){
  // 1. TILASTO - harjoitus+kilpailu dynaaminen, sailytä aiempi jos fail
  try{
    const til=await fetch('./data/tilasto.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error('tilasto fail'); return r.json();});
    const el=id=>document.getElementById(id);
    if(til.total && til.total>=500 && el('live-kierrokset')) el('live-kierrokset').textContent=til.total;
    // Kortti erikseen harjoitus+kilpailu
    document.querySelectorAll('.card').forEach(card=>{
      if(card.textContent.includes('UDisc') && card.textContent.includes('Metrix')){
        const udisc=til.udisc?.rounds||428;
        const m43119=til.metrix?.['43119']||702;
        const total=til.total||1130;
        const harj=til.harjoituskierrokset_yhteensa||1470;
        const kilp=til.kilpailukierrokset_yhteensa||0;
        const kaikki=til.total_kaikki||1898;
        card.querySelectorAll('div, span, p').forEach(d=>{
          if(d.textContent.includes('UDisc') && d.textContent.includes('Metrix')){
            d.innerHTML=`UDisc ${udisc} + Metrix 43119 ${m43119} = ${total} OIKEIN<br>Harjoitus ${harj} + Kilpailu ${kilp} = ${harj+kilp} Metrix<br>Kaikki 3 rataa ${kaikki}<br><span style="font-size:9px; color:#888;">43119:${til.metrix_detailed?.['43119']?.harjoitus||702}H 44010:${til.metrix_detailed?.['44010']?.harjoitus||598}H 44763:${til.metrix_detailed?.['44763']?.harjoitus||170}H - DYNAAMINEN</span>`;
            d.style.fontSize='11px'; d.style.lineHeight='1.3';
          }
        });
      }
    });
    if(el('live-pelaajat') && til.unique) el('live-pelaajat').textContent=til.unique;
    if(el('live-aika') && til.playtime) el('live-aika').textContent=til.playtime+'h';
    if(el('live-askeleet') && til.steps) el('live-askeleet').textContent=til.steps.toLocaleString('fi-FI');
    if(el('live-km') && til.km) el('live-km').textContent=til.km+' km';
  }catch(e){console.log('tilasto sailytetaan aiempi DOMissa',e);}

  // 2. TOP5 - KORJATTU: hajoaa vari siirron jalkeen koska puuttui
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error('top5 fail'); return r.json();});
    const render=(id,arr)=>{
      const e=document.getElementById(id);
      if(!e){console.log(id+' ei loydy'); return;}
      if(!arr||!arr.length){
        // Jos tyhjä, sailytä aiempi - älä jätä Ladataan...
        if(e.textContent.includes('Ladataan')) e.innerHTML='<li style="color:#888; font-size:11px;">Ei tuloksia - haetaan 5min</li>';
        console.log(id+' tyhjä, sailytetään aiempi');
        return;
      }
      // Suodata placeholder Pelaaja A pois
      const real=arr.filter(x=>!x.player.includes('Pelaaja A') && !x.player.includes('Pelaaja X') && !x.player.includes('UDisc Pro'));
      const use=real.length>=3?real:arr;
      e.innerHTML=use.map(x=>`<li style="display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #222;"><span>${x.rank}. ${x.player}</span><span style="font-weight:800; color:#fff;">${x.score}</span></li>`).join('');
    };
    render('top5-44010', top.metrix_44010?.top5 || top['metrix_44010']?.top5);
    render('top5-44763', top.metrix_44763?.top5 || top['metrix_44763']?.top5);
    render('top5-udisc', top.udisc?.top5 || top['udisc']?.top5);
    console.log('TOP5 DYNAAMINEN paivitetty');
  }catch(e){console.log('TOP5 sailytetaan aiempi, ei Ladataan',e);}

  // 3. SÄÄ - KORJATTU: hajoaa vari siirron jalkeen
  const sc=document.getElementById('saa-content');
  if(sc){
    try{
      const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error('foreca fail'); return r.json();});
      if(fc.current && fc.hourly){
        sc.innerHTML=`
          <div style="display:flex; flex-direction:column; height:175px; overflow:hidden; background:#0f0f0f; padding:6px;">
            <div style="display:flex; justify-content:space-between;">
              <div><div style="font-size:26px; font-weight:900; color:#fff;">${fc.current.temp}</div><div style="font-size:9px; color:#888;">Tuntuu ${fc.current.feels} • ${fc.current.cloud}</div></div>
              <div style="text-align:right; font-size:9px; color:#aaa; line-height:1.3;"><div>Tuuli ${fc.current.wind}</div><div>Puuskat ${fc.current.gust}</div><div>Sade ${fc.current.precip}</div><div style="color:#00ff00; font-weight:700;">Foreca LIVE DYNAAMINEN</div></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:8px; border-top:1px solid #222; padding-top:6px;">
              ${fc.hourly.map(h=>`<div style="text-align:center; flex:1;"><div style="font-size:9px; color:#888;">${h.hour}</div><div style="font-size:20px; line-height:1.1;">${h.icon}</div><div style="font-size:11px; color:#fff; font-weight:800; margin-top:2px;">${h.temp}°</div></div>`).join('')}
            </div>
            <div style="margin-top:auto; border-top:1px solid #222; padding-top:4px; display:flex; justify-content:space-between; font-size:8px; color:#666;">
              ${fc.daily.map(d=>`<span>${d.day} ${d.max}/${d.min}°</span>`).join('')}
            </div>
          </div>
        `;
      }
    }catch(e){console.log('foreca sailytetaan aiempi',e); if(sc.textContent.includes('Ladataan')) sc.innerHTML='<div style="color:#fff; font-size:12px;">12°C - haetaan...</div>';}
  }

  // 4. VÄYLÄTILASTO VARI + TEKSTI EI MAHDU KORJAUS
  try{
    const rat=await fetch('./data/ratatilasto.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error('ratatilasto fail'); return r.json();});
    document.querySelectorAll('table').forEach(table=>{
      if(table.textContent.includes('Vayla')){
        const over=rat.Avg.map((a,i)=>a-rat.Par[i]);
        const sorted=[...over].sort((a,b)=>a-b);
        const col=o=> o<=sorted[2]?'#66BB6A':o<=sorted[6]?'#FFEB3B':o<=sorted[8]?'#FFA726':'#EF5350';
        table.querySelectorAll('tr').forEach(tr=>{
          const firstCell=tr.querySelector('td, th');
          if(!firstCell) return;
          const label=firstCell.textContent.trim().toLowerCase();
          // VARI KORJATTU: vain Avg ja Difficulty, ei Par
          if(label==='avg' || label==='difficulty'){
            tr.querySelectorAll('td').forEach((td,i)=>{
              if(i>=1&&i<=12){
                td.style.background=col(over[i-1]);
                td.style.color='#000';
                td.style.fontWeight='800';
              }
            });
          }
          if(label==='par'){
            tr.querySelectorAll('td').forEach(td=>{td.style.background='#0f0f0f'; td.style.color='white';});
          }
          // TEKSTI EI MAHDU KORJAUS: eka sarake leveämmäksi, wrap sallittu
          if(firstCell){
            firstCell.style.whiteSpace='nowrap';
            firstCell.style.minWidth='95px';
            firstCell.style.maxWidth='110px';
            firstCell.style.fontSize='11px';
            firstCell.style.overflow='visible';
            // Lyhennä pitkät jos ei mahdu
            if(firstCell.textContent.includes('Double Bogey')) firstCell.textContent='Dbl Bogey 2';
            if(firstCell.textContent.includes('Triple Bogey')) firstCell.textContent='Tpl Bogey 3';
          }
        });
        // Koko taulukko: pienempi fontti, auto layout
        table.style.fontSize='11px';
        table.style.tableLayout='auto';
        table.style.width='100%';
        table.querySelectorAll('td, th').forEach(c=>{
          c.style.fontSize='11px';
          c.style.padding='4px 5px';
          c.style.whiteSpace='nowrap';
          c.style.overflow='hidden';
          c.style.textOverflow='ellipsis';
        });
        // Eka sarake ei ellipsis, vaan näkyy kokonaan
        table.querySelectorAll('td:first-child, th:first-child').forEach(c=>{
          c.style.whiteSpace='nowrap';
          c.style.overflow='visible';
          c.style.textOverflow='clip';
          c.style.minWidth='95px';
        });
      }
    });
  }catch(e){console.log('vaylatilasto sailytetaan aiempi',e);}
}
loadAll(); setInterval(loadAll,300000);
// CSS korjaus grid + teksti ei mahdu
const style=document.createElement('style');
style.textContent=`
  .grid-4{align-items:start !important;}
  .grid-4 .card{height:auto !important; min-height:210px; max-height:260px; overflow:hidden;}
  #saa-content{max-height:180px; overflow:hidden;}
  table td:first-child{white-space:nowrap !important; min-width:95px !important; font-size:11px !important;}
  .vaylatilasto-wrapper{overflow-x:auto;}
`;
document.head.appendChild(style);
