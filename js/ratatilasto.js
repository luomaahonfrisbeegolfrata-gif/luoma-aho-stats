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

  // FORECA - isommat kuvakkeet 09 12 15 18 21 00 03 06
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
          <div style="display:flex; justify-content:space-between; margin-top:8px; border-top:1px solid #222; padding-top:6px;">
            ${fc.hourly.map(h=>`
              <div style="text-align:center; flex:1;">
                <div style="font-size:9px; color:#888;">${h.hour}</div>
                <div style="font-size:20px; line-height:1.1; filter: drop-shadow(0 0 2px #000);">${h.icon}</div>
                <div style="font-size:11px; color:#fff; font-weight:800; margin-top:2px;">${h.temp}°</div>
              </div>
            `).join('')}
          </div>
          <div style="margin-top:auto; border-top:1px solid #222; padding-top:3px; display:flex; justify-content:space-between; font-size:8px; color:#666;">
            ${fc.daily.map(d=>`<span>${d.day} ${d.max}/${d.min}°</span>`).join('')}
          </div>
        </div>
      `;
    }catch(e){}
  }

  // VÄYLÄTILASTO - värit ja isompi teksti HTML taulukkoon
  try{
    const rat=await fetch('./data/ratatilasto.json?t='+Date.now()).then(r=>r.json());
    const tables=document.querySelectorAll('table');
    tables.forEach(table=>{
      const rows=table.querySelectorAll('tr');
      if(rows.length < 5) return;
      // Etsi Avg rivi ja Difficulty rivi
      let avgRow=null, diffRow=null;
      rows.forEach(r=>{
        const txt=r.textContent.toLowerCase();
        if(txt.includes('avg') && !txt.includes('vayla')) avgRow=r;
        if(txt.includes('difficulty')) diffRow=r;
      });
      if(avgRow && diffRow){
        const par=rat.Par;
        const avg=rat.Avg;
        const over=avg.map((a,i)=>a-par[i]);
        const sorted=[...over].sort((a,b)=>a-b);
        const getColor=(o)=>{
          if(o <= sorted[2]) return '#66BB6A';
          if(o <= sorted[6]) return '#FFEB3B';
          if(o <= sorted[8]) return '#FFA726';
          return '#EF5350';
        };
        // Avg rivi: 2nd col = vayla 1 jne (skip first and last 2)
        [avgRow, diffRow].forEach(row=>{
          const cells=row.querySelectorAll('td');
          cells.forEach((cell, idx)=>{
            if(idx>=1 && idx<=12){
              const c=getColor(over[idx-1]);
              cell.style.background=c;
              cell.style.color='#000';
              cell.style.fontWeight='800';
              cell.style.fontSize='12px';
            }
          });
        });
      }
      // Isompi teksti koko taulukkoon
      table.style.fontSize='12px';
      table.querySelectorAll('td, th').forEach(c=>{
        c.style.fontSize='12px';
        c.style.padding='5px 6px';
      });
    });
  }catch(e){console.log('ratatilasto vari fail',e);}

  try{const img=document.getElementById('vayla-live-img');if(img) img.src='./vaylatilasto.png?t='+Date.now();}catch(e){}
}
loadAll();setInterval(loadAll,300000);

// grid korjaus
const style=document.createElement('style');
style.textContent='.grid-4{align-items:start !important;} .grid-4 .card{height:auto !important; min-height:200px; max-height:220px; overflow:hidden;} #saa-content{max-height:180px; overflow:hidden;} table{font-size:12px !important;}';
document.head.appendChild(style);
