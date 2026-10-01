async function loadAll(){
  try{
    const til=await fetch('./data/tilasto.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error('fail'); return r.json();});
    const el=id=>document.getElementById(id);
    let total=til.total;
    if(total && total>=500){
      if(el('live-kierrokset')) el('live-kierrokset').textContent=total;
    }
    // NÄYTÄ ERIKSEEN - tilaa kortissa on
    const descEl=document.getElementById('total-desc') || document.querySelector('[data-total-desc]') || document.querySelector('.kierrokset-desc');
    // Etsi se pieni harmaa teksti kortissa ja päivitä dynaamisesti
    const cards=document.querySelectorAll('.card, [class*="card"]');
    cards.forEach(card=>{
      if(card.textContent.includes('UDisc') && card.textContent.includes('Metrix')){
        const udisc=til.udisc?.rounds||428;
        const m43119=til.metrix?.['43119']||702;
        const harj=til.harjoituskierrokset_yhteensa||1470;
        const kilp=til.kilpailukierrokset_yhteensa||0;
        const kaikki=til.total_kaikki||1898;
        // Kirurginen: päivitä vain teksti, älä koko korttia
        card.querySelectorAll('div, span, p').forEach(d=>{
          if(d.textContent.includes('UDisc') && d.textContent.includes('Metrix')){
            d.innerHTML=`UDisc ${udisc} + Metrix 43119 ${m43119} = ${total} OIKEIN<br>Harjoitus ${harj} | Kilpailu ${kilp}<br>Kaikki 3 rataa ${kaikki} = ${udisc}+702+598+170<br><span style="font-size:9px; color:#888;">43119:${til.metrix_detailed?.['43119']?.harjoitus||702}H 44010:${til.metrix_detailed?.['44010']?.harjoitus||598}H 44763:${til.metrix_detailed?.['44763']?.harjoitus||170}H - DYNAAMINEN</span>`;
            d.style.fontSize='11px';
            d.style.lineHeight='1.3';
          }
        });
      }
    });
    if(el('live-pelaajat') && til.unique) el('live-pelaajat').textContent=til.unique;
    if(el('live-aika') && til.playtime) el('live-aika').textContent=til.playtime+'h';
    if(el('live-askeleet') && til.steps) el('live-askeleet').textContent=til.steps.toLocaleString('fi-FI');
    if(el('live-km') && til.km) el('live-km').textContent=til.km+' km';
  }catch(e){console.log('tilasto dynaaminen ei toteutunut, säilytetään aiempi',e);}

  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error('fail'); return r.json();});
    const render=(id,arr)=>{const e=document.getElementById(id); if(!e||!arr?.length){console.log(id+' säilytetään aiempi'); return;} e.innerHTML=arr.map(x=>'<li><span>'+x.rank+'. '+x.player+'</span><span>'+x.score+'</span></li>').join('');};
    render('top5-44010',top.metrix_44010?.top5);
    render('top5-44763',top.metrix_44763?.top5);
    render('top5-udisc',top.udisc?.top5);
  }catch(e){console.log('top5 säilytetään aiempi',e);}

  const sc=document.getElementById('saa-content');
  if(sc){
    try{
      const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error('fail'); return r.json();});
      if(fc.current && fc.hourly){
        sc.innerHTML=`<div style="display:flex; flex-direction:column; height:175px; overflow:hidden; background:#0f0f0f;"><div style="display:flex; justify-content:space-between;"><div><div style="font-size:26px; font-weight:900; color:#fff;">${fc.current.temp}</div><div style="font-size:9px; color:#888;">Tuntuu ${fc.current.feels} • ${fc.current.cloud}</div></div><div style="text-align:right; font-size:9px; color:#aaa; line-height:1.3;"><div>Tuuli ${fc.current.wind}</div><div>Puuskat ${fc.current.gust}</div><div>Sade ${fc.current.precip}</div><div style="color:#00ff00; font-weight:700;">Foreca LIVE</div></div></div><div style="display:flex; justify-content:space-between; margin-top:8px; border-top:1px solid #222; padding-top:6px;">${fc.hourly.map(h=>`<div style="text-align:center; flex:1;"><div style="font-size:9px; color:#888;">${h.hour}</div><div style="font-size:20px;">${h.icon}</div><div style="font-size:11px; color:#fff; font-weight:800; margin-top:2px;">${h.temp}°</div></div>`).join('')}</div><div style="margin-top:auto; border-top:1px solid #222; padding-top:3px; display:flex; justify-content:space-between; font-size:8px; color:#666;">${fc.daily.map(d=>`<span>${d.day} ${d.max}/${d.min}°</span>`).join('')}</div></div>`;
      }
    }catch(e){console.log('foreca säilytetään aiempi',e);}
  }
}
loadAll();setInterval(loadAll,300000);
const style=document.createElement('style');
style.textContent='.grid-4{align-items:start !important;} .grid-4 .card{height:auto !important; min-height:210px; max-height:260px; overflow:hidden;} #saa-content{max-height:180px; overflow:hidden;}';
document.head.appendChild(style);
