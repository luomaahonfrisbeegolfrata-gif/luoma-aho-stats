
(function(){
  const JSON_URL = './data/ratatilasto.json';
  const PNG_URL = './ratatilasto.png';
  function init(){
    let target=null;
    for(const t of document.querySelectorAll('table')){ if(t.textContent.includes('Pituus')){target=t;break;} }
    if(!target) target=document.querySelector('#vaylatilasto')||document.body;
    fetch(JSON_URL+'?t='+Date.now()).then(r=>r.json()).then(data=>{
      if(document.getElementById('luoma-aho-stats')) return;
      const pituus=data.Pituus||[125,103,72,57,94,96,103,80,116,85,197,120];
      const totP=pituus.reduce((a,b)=>a+b,0);
      const over=data.Avg.map((a,i)=>a-data.Par[i]);
      const sorted=[...over].sort((a,b)=>a-b);
      function col(o){ if(o<=sorted[2]) return '#66BB6A'; if(o<=sorted[6]) return '#FFEB3B'; if(o<=sorted[8]) return '#FFA726'; return '#EF5350'; }
      const colors=over.map(col);
      const div=document.createElement('div');
      div.id='luoma-aho-stats';
      div.style.cssText='margin-top:30px;padding:20px;background:#000;color:#fff;border-radius:12px;overflow-x:auto;border:1px solid #333';
      div.innerHTML=`
        <h2 style="color:#fff;margin:0 0 10px">📊 Väylätilasto (Live) - ${data.Tot.Plays} heittoa</h2>
        <p style="color:#ccc;margin:0 0 10px">Pituus ${totP}m | Avg ${data.Tot.Avg.toFixed(2)} (Par ${data.Tot.Par} +${data.OverPar.toFixed(2)}) | Päivitetty ${data.updated.slice(0,16).replace('T',' ')}</p>
        <img src="${PNG_URL}?t=${Date.now()}" style="width:100%;max-width:1150px;border:1px solid #444;border-radius:8px;display:block;margin-bottom:15px">
        <table style="border-collapse:collapse;width:100%;font-size:12px;color:#fff;background:#000">
          <tr style="background:#222"><th>Väylä</th>${[...Array(12)].map((_,i)=>`<th>${i+1}</th>`).join('')}<th>Tot</th><th>%</th></tr>
          <tr style="background:#111"><td><b>Pituus</b></td>${pituus.map(v=>`<td>${v}m</td>`).join('')}<td><b>${totP}m</b></td><td>-</td></tr>
          <tr style="background:#1a1a1a"><td><b>Par</b></td>${data.Par.map(v=>`<td>${v}</td>`).join('')}<td><b>${data.Tot.Par}</b></td><td>-</td></tr>
          <tr><td><b>Avg</b></td>${data.Avg.map((v,i)=>`<td style="background:${colors[i]};color:#000">${v.toFixed(2)}</td>`).join('')}<td style="background:#1a1a1a"><b>${data.Tot.Avg.toFixed(2)}</b></td><td>-</td></tr>
        </table>
      `;
      if(target&&target.tagName==='TABLE') target.parentNode.insertBefore(div, target.nextSibling);
      else target.appendChild(div);
    }).catch(e=>console.log('Ratatilasto skip',e));
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
