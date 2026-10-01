(function(){
  try{
    const body = document.getElementById('vaylatilasto-body');
    if(!body) return;
    fetch('./data/ratatilasto.json?v='+Date.now())
      .then(r=>r.json())
      .then(j=>{
        const rows = j.vaylat || j.holes || [];
        body.innerHTML = rows.map((r)=>{
          const isAvg = String(r.vayla||r.hole||'').toLowerCase().includes('avg') || r.isAvg;
          const bg = isAvg ? 'background:rgba(255,204,0,0.08);border-left:2px solid #ffcc00;' : '';
          const col = isAvg ? 'color:#ffcc00;font-weight:800;' : 'color:#ccc;';
          return `<div style="display:flex;justify-content:space-between;padding:6px 8px;border-bottom:1px solid #1a1a1a;font-size:12px;${bg}">
            <span style="${col}">${r.vayla ?? r.hole ?? ''}</span>
            <span style="${col}">${r.avg ?? r.keskiarvo ?? ''}</span>
            <span style="color:#666;">${r.par ?? ''}</span>
          </div>`;
        }).join('');
      })
      .catch(()=>{});
  }catch(e){
    console.warn('[vaylatilasto] virhe:', e);
  }
})();