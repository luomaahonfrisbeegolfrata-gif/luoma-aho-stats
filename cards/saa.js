(function(){
  try{
    const wrap = document.getElementById('saa-wrap');
    if(!wrap) return;
    fetch('./data/foreca.json?v='+Date.now())
      .then(r=>r.json())
      .then(j=>{
        const cur = j.current || j;
        const hours = j.hourly || j.tunnit || [];
        const mainTemp = cur.temp ?? cur.temperature ?? '--';
        const mainIcon = cur.icon || '☀️';
        const hourlyHtml = hours.slice(0,8).map((h)=>{
          return `<div style="display:flex;flex-direction:column;align-items:center;min-width:42px;">
            <div style="font-size:11px;color:#777;">${h.hour ?? h.time ?? ''}</div>
            <div style="font-size:32px;line-height:1;margin:2px 0;">${h.icon || '⛅'}</div>
            <div style="font-size:14px;font-weight:700;">${h.temp ?? h.temperature ?? ''}°</div>
          </div>`;
        }).join('');
        wrap.innerHTML = `
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
            <div style="font-size:36px;font-weight:900;">${mainTemp}°</div>
            <div style="font-size:32px;">${mainIcon}</div>
            <div style="font-size:12px;color:#888;line-height:1.3;">${cur.desc || cur.description || 'Luoma-aho'}<br/>${cur.wind || ''}</div>
          </div>
          <div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;">${hourlyHtml}</div>
        `;
      })
      .catch(()=>{});
  }catch(e){
    console.warn('[saa] virhe:', e);
  }
})();