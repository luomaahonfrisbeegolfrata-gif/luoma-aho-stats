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

  // FORECA EHDOTTOMASTI - puhdas ilman mainoksia, 185px kiintea ei venyta
  const sc=document.getElementById('saa-content');
  if(sc){
    try{
      const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>r.json());
      const cur=fc.current;
      const hourly=fc.hourly;
      const daily=fc.daily;
      sc.innerHTML = `
        <div style="display:flex; flex-direction:column; height:185px; overflow:hidden; background:#0f0f0f;">
          <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
              <div style="font-size:26px; font-weight:900; color:#fff; line-height:1;">${cur.temp}</div>
              <div style="font-size:10px; color:#888; margin-top:2px;">Tuntuu kuin ${cur.feels} • ${cur.cloud}</div>
            </div>
            <div style="text-align:right; font-size:9px; color:#aaa; line-height:1.35;">
              <div>Tuuli ${cur.wind} ↑</div>
              <div>Puuskat ${cur.gust}</div>
              <div>Sade ${cur.precip}</div>
              <div style="color:#66BB6A; font-weight:700;">LIVE Foreca</div>
            </div>
          </div>
          <div style="display:flex; justify-content:space-between; margin:8px 0 0 0; border-top:1px solid #222; padding-top:6px;">
            ${hourly.slice(0,8).map(h=>`
              <div style="text-align:center; flex:1;">
                <div style="font-size:8px; color:#666;">${h.hour}</div>
                <div style="font-size:13px;">${h.icon}</div>
                <div style="font-size:10px; color:#fff; font-weight:700;">${h.temp}°</div>
                <div style="font-size:8px; color:#0f0;">${h.wind}</div>
              </div>
            `).join('')}
          </div>
          <div style="margin-top:auto; border-top:1px solid #222; padding-top:4px;">
            <div style="display:flex; justify-content:space-between; font-size:8px; color:#666;">
              ${daily.map(d=>`<span>${d.day} ${d.max}/${d.min}°</span>`).join('')}
            </div>
            <div style="font-size:7px; color:#333; text-align:center; margin-top:2px;">Foreca Täsmäsää™ Luoma-aho, Alajärvi • <a href="https://www.foreca.fi/Finland/Alajarvi" target="_blank" style="color:#00ff00; text-decoration:none;">foreca.fi →</a> • ${new Date(fc.paivitys).toLocaleTimeString('fi-FI',{hour:'2-digit',minute:'2-digit'})}</div>
          </div>
        </div>
      `;
    }catch(e){
      sc.innerHTML='<div style="font-size:11px; color:#666; text-align:center; padding:30px 0;">Foreca lataa...<br><a href="https://www.foreca.fi/Finland/Alajarvi" target="_blank" style="color:#0f0;">foreca.fi</a></div>';
    }
  }
  try{const img=document.getElementById('vayla-live-img');if(img) img.src='./vaylatilasto.png?t='+Date.now();}catch(e){}
}
loadAll();setInterval(loadAll,300000);
