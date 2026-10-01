async function loadAll(){
  // TILASTO - KAIKKI DYNAAMISTA, jos ei toteudu säilytä aiempi
  try{
    const t=Date.now();
    const til=await fetch('./data/tilasto.json?t='+t).then(r=>{
      if(!r.ok) throw new Error('tilasto fetch fail');
      return r.json();
    });
    const el=id=>document.getElementById(id);
    // Kirurginen: vain jos total on validi ja >500, päivitä, muuten säilytä DOMissa aiempi
    let total = til.total;
    if(total && total >= 500){
      if(el('live-kierrokset')) el('live-kierrokset').textContent=total;
      const descEl=document.getElementById('total-desc');
      if(descEl) descEl.textContent=`UDisc ${til.udisc?.rounds||428} + Metrix 43119 ${til.metrix?.["43119"]||702} = ${total} OIKEIN - DYNAAMINEN`;
    } else {
      console.log('total ei toteutunut, säilytetään aiempi DOMissa - ei muuteta staattiseksi');
    }
    // Muut dynaamisia johdettuja - päivitä vain jos validi
    if(til.unique && til.unique>10 && el('live-pelaajat')) el('live-pelaajat').textContent=til.unique;
    if(til.playtime && el('live-aika')) el('live-aika').textContent=til.playtime+'h';
    if(til.steps && el('live-askeleet')) el('live-askeleet').textContent=til.steps.toLocaleString('fi-FI');
    if(til.km && el('live-km')) el('live-km').textContent=til.km+' km';
  }catch(e){
    console.log('tilasto dynaaminen fetch ei toteutunut, säilytetään aiempi tieto DOMissa',e);
  }

  // TOP5 - dynaaminen
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>{
      if(!r.ok) throw new Error('top5 fail');
      return r.json();
    });
    const render=(id,arr)=>{
      const e=document.getElementById(id);
      if(!e||!arr||!arr.length){
        console.log(id+' ei toteutunut, säilytetään aiempi');
        return;
      }
      e.innerHTML=arr.map(x=>'<li><span>'+x.rank+'. '+x.player+'</span><span>'+x.score+'</span></li>').join('');
    };
    render('top5-44010',top.metrix_44010?.top5);
    render('top5-44763',top.metrix_44763?.top5);
    render('top5-udisc',top.udisc?.top5);
  }catch(e){console.log('top5 dynaaminen ei toteutunut, säilytetään aiempi',e);}

  // SAA FORECA - dynaaminen, isommat ikonit 20px, 175px ei venytä
  const sc=document.getElementById('saa-content');
  if(sc){
    try{
      const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>{
        if(!r.ok) throw new Error('foreca fail');
        return r.json();
      });
      if(fc.current && fc.hourly){
        sc.innerHTML = `
          <div style="display:flex; flex-direction:column; height:175px; overflow:hidden; background:#0f0f0f;">
            <div style="display:flex; justify-content:space-between;">
              <div><div style="font-size:26px; font-weight:900; color:#fff;">${fc.current.temp}</div><div style="font-size:9px; color:#888;">Tuntuu ${fc.current.feels} • ${fc.current.cloud}</div></div>
              <div style="text-align:right; font-size:9px; color:#aaa; line-height:1.3;"><div>Tuuli ${fc.current.wind}</div><div>Puuskat ${fc.current.gust}</div><div>Sade ${fc.current.precip}</div><div style="color:#00ff00; font-weight:700;">Foreca LIVE DYNAAMINEN</div></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:8px; border-top:1px solid #222; padding-top:6px;">
              ${fc.hourly.map(h=>`<div style="text-align:center; flex:1;"><div style="font-size:9px; color:#888;">${h.hour}</div><div style="font-size:20px; line-height:1.1;">${h.icon}</div><div style="font-size:11px; color:#fff; font-weight:800; margin-top:2px;">${h.temp}°</div></div>`).join('')}
            </div>
            <div style="margin-top:auto; border-top:1px solid #222; padding-top:3px; display:flex; justify-content:space-between; font-size:8px; color:#666;">
              ${fc.daily.map(d=>`<span>${d.day} ${d.max}/${d.min}°</span>`).join('')}
            </div>
          </div>
        `;
      }
    }catch(e){console.log('foreca dynaaminen ei toteutunut, säilytetään aiempi',e);}
  }

  // VAYLATILASTO varit + koko dynaaminen
  try{
    const rat=await fetch('./data/ratatilasto.json?t='+Date.now()).then(r=>{
      if(!r.ok) throw new Error('ratatilasto fail');
      return r.json();
    });
    document.querySelectorAll('table').forEach(table=>{
      if(table.textContent.includes('Vayla')){
        const over=rat.Avg.map((a,i)=>a-rat.Par[i]);
        const sorted=[...over].sort((a,b)=>a-b);
        const col=o=> o<=sorted[2]?'#66BB6A':o<=sorted[6]?'#FFEB3B':o<=sorted[8]?'#FFA726':'#EF5350';
        table.querySelectorAll('tr').forEach(tr=>{
          const txt=tr.textContent.toLowerCase();
          if(txt.includes('avg') || txt.includes('difficulty')){
            tr.querySelectorAll('td').forEach((td,i)=>{
              if(i>=1&&i<=12){ td.style.background=col(over[i-1]); td.style.color='#000'; td.style.fontWeight='800'; }
            });
          }
        });
        table.style.fontSize='12px';
        table.querySelectorAll('td,th').forEach(c=>{c.style.fontSize='12px'; c.style.padding='5px 6px';});
      }
    });
  }catch(e){console.log('vaylatilasto ei toteutunut, säilytetään aiempi',e);}
}
loadAll();setInterval(loadAll,300000);
const style=document.createElement('style');
style.textContent='.grid-4{align-items:start !important;} .grid-4 .card{height:auto !important; min-height:200px; max-height:220px; overflow:hidden;} #saa-content{max-height:180px; overflow:hidden;}';
document.head.appendChild(style);
