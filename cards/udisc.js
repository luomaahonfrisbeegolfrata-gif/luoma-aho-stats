(function(){
  try{
    const list = document.getElementById('udisc-list');
    if(!list) return;
    fetch('./data/top5.json?v='+Date.now())
      .then(r=>r.json())
      .then(data=>{
        let rows = Array.isArray(data) ? data : data.top5 || data.udisc || [];
        rows = rows.filter((x)=> String(x.source||'').toLowerCase().includes('udisc') || String(x.rata_id||'')==='udisc');
        if(rows.length===0) rows = (Array.isArray(data)?data:data.top5||[]).filter(r=>r.source==='udisc');
        rows = rows.filter((r)=> r.Pelaaja && r.Pelaaja.trim()!=='A' && r.Pelaaja!=='Pelaaja A');
        rows = rows.slice(0,5);
        list.innerHTML = rows.map((p,i)=>{
          const total = Number(p.total ?? p.tulos ?? 0);
          const par = Number(p.par ?? 54);
          const diff = total - par;
          const sign = diff>0 ? '+'+diff : String(diff);
          const col = diff<0 ? '#00ff00' : diff>0 ? '#ff4444' : '#ccc';
          return `<div style="display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid #1a1a1a;font-size:13px;">
            <span style="color:#999;">${i+1}.</span>
            <span style="flex:1;margin-left:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${p.Pelaaja}</span>
            <span style="color:${col};font-weight:800;min-width:32px;text-align:right;">${sign}</span>
          </div>`;
        }).join('') || '<div style="color:#555;font-size:12px;">Ei dataa</div>';
      })
      .catch(()=>{});
  }catch(e){
    console.warn('[udisc] virhe:', e);
  }
})();