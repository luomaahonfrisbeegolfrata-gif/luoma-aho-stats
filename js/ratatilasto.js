async function loadAll(){
  try{
    const t=Date.now();
    const til=await fetch('./data/tilasto.json?t='+t).then(r=>r.json());
    const el=id=>document.getElementById(id);
    if(el('live-kierrokset')) el('live-kierrokset').textContent=til.total??1130;
    if(el('live-pelaajat')) el('live-pelaajat').textContent=til.unique??100;
    if(el('live-aika')) el('live-aika').textContent=(til.playtime??1481)+'h';
    if(el('live-askeleet')) el('live-askeleet').textContent=(til.steps??3100890).toLocaleString('fi-FI');
    if(el('live-km')) el('live-km').textContent=(til.km??2260)+' km';
  }catch(e){}
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>r.json());
    const render=(id,arr)=>{const e=document.getElementById(id);if(!e||!arr)return;e.innerHTML=arr.map(x=>'<li><span>'+x.rank+'. '+x.player+'</span><span>'+x.score+'</span></li>').join('');};
    render('top5-44010',top.metrix_44010?.top5);
    render('top5-44763',top.metrix_44763?.top5);
    render('top5-udisc',top.udisc?.top5);
  }catch(e){}

  // FORECA PUHDAS - EI IFRAME KOKO SIVUA, EI MAINOKSIA, 190px KIINTEA EI VENYTA
  const sc=document.getElementById('saa-content');
  if(sc){
    try{
      const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>r.json());
      const cur=fc.current;
      sc.innerHTML = `
        <div style="display:flex; flex-direction:column; height:175px; overflow:hidden; background:#0f0f0f;">
          <div style="display:flex; justify-content:space-between;">
            <div><div style="font-size:26px; font-weight:900; color:#fff;">${cur.temp}</div><div style="font-size:9px; color:#888;">Tuntuu ${cur.feels} • ${cur.cloud}</div></div>
            <div style="text-align:right; font-size:9px; color:#aaa; line-height:1.3;"><div>Tuuli ${cur.wind}</div><div>Puuskat ${cur.gust}</div><div>Sade ${cur.precip}</div><div style="color:#00ff00; font-weight:700;">Foreca LIVE</div></div>
          </div>
          <div style="display:flex; justify-content:space-between; margin-top:8px; border-top:1px solid #222; padding-top:5px;">
            ${fc.hourly.map(h=>`<div style="text-align:center; flex:1;"><div style="font-size:8px; color:#666;">${h.hour}</div><div style="font-size:12px;">${h.icon}</div><div style="font-size:9px; color:#fff; font-weight:700;">${h.temp}°</div></div>`).join('')}
          </div>
          <div style="margin-top:auto; border-top:1px solid #222; padding-top:3px; display:flex; justify-content:space-between; font-size:8px; color:#666;">
            ${fc.daily.map(d=>`<span>${d.day} ${d.max}/${d.min}°</span>`).join('')}
          </div>
        </div>
      `;
    }catch(e){ sc.innerHTML='<div style="font-size:11px; color:#666; text-align:center;">Foreca lataa...</div>'; }
  }
  // Vaylatilasto cache bust
  try{const img=document.getElementById('vayla-live-img');if(img) img.src='./vaylatilasto.png?t='+Date.now();}catch(e){}
}
loadAll();setInterval(loadAll,300000);

// ESTA RIVIN VENYMINEN - korjaa grid-4 align-items
const style=document.createElement('style');
style.textContent='.grid-4{align-items:start !important;} .grid-4 .card{height:auto !important; min-height:200px; max-height:220px; overflow:hidden;} #saa-content{max-height:180px; overflow:hidden;}';
document.head.appendChild(style);
