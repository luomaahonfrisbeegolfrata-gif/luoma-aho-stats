(function(){
  try{
    const countEl = document.getElementById('hio-count');
    const listEl = document.getElementById('hio-list');
    if(!countEl && !listEl) return;
    fetch('./data/holeinone.json?v='+Date.now())
      .then(r=>r.json())
      .then(j=>{
        const count = j.count ?? (j.players?.length || 0);
        const players = j.players || [];
        if(countEl){
          countEl.textContent = String(count);
          countEl.style.fontSize='36px';
          countEl.style.fontWeight='900';
          countEl.style.lineHeight='1';
        }
        if(listEl){
          listEl.innerHTML = players.map((p)=>{
            const name = typeof p==='string' ? p : p.player;
            const hole = typeof p==='object' ? p.hole : '';
            return `<div style="font-size:15px;padding:3px 0;border-bottom:1px solid #1a1a1a;display:flex;justify-content:space-between;">
              <span style="color:#ccc;">${name}</span>
              <span style="color:#ffcc00;font-weight:700;">#${hole}</span>
            </div>`;
          }).join('');
          listEl.style.fontSize='15px';
        }
      })
      .catch(()=>{});
  }catch(e){
    console.warn('[hio] virhe:', e);
  }
})();