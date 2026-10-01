(function(){
  try{
    const t=document.getElementById('live-kierrokset');
    const u=document.getElementById('live-pelaajat');
    if(!t||!u) return;
    const tc=t.closest('.card');
    const uc=u.closest('.card');
    if(!tc||!uc||tc===uc||tc.dataset.combined) return;
    tc.innerHTML=`
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;">
        <div style="font-size:11px;font-weight:800;letter-spacing:0.05em;">UDISC & METRIX TULOSKIERROKSET - <span style="color:#00ff00;">AUTO 15/5MIN</span></div>
        <div id="live-kierrokset" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">${t.textContent}</div>
      </div>
      <div style="height:1px;background:#222;margin:8px 0;"></div>
      <div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;">
        <div style="font-size:11px;font-weight:800;letter-spacing:0.05em;">UNIIKIT PELAAJAT - <span style="color:#00ff00;">AUTO</span></div>
        <div id="live-pelaajat" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">${u.textContent}</div>
      </div>`;
    tc.dataset.combined='true';
    tc.style.display='flex';
    tc.style.flexDirection='column';
    if(uc) uc.style.display='none';
  }catch(e){
    console.warn('[tuloskierrokset] virhe:', e);
  }
})();