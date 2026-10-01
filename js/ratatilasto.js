async function loadAll(){
  const PAR_44010=41, PAR_44763=82;
  const calc=(t,p)=>{const d=t-p; return d>0?{diff:d, display:`${t} (+${d})`}:d<0?{diff:d, display:`${t} (${d})`}:{diff:0, display:`${t} (E)`};}
  
  // RATAINFO 16px
  try{
    document.querySelectorAll('.card div').forEach(el=>{
      if(el.textContent.includes('Kalliopohjaisessa')){
        el.style.fontSize='16px';
        el.style.lineHeight='1.7';
      }
    });
  }catch(e){}

  // YHDISTETTY + HIO 36px / 15px
  try{
    const tulosEl=document.getElementById('live-kierrokset');
    const uniikitEl=document.getElementById('live-pelaajat');
    if(tulosEl&&uniikitEl){
      const tulosCard=tulosEl.closest('.card');
      const uniikitCard=uniikitEl.closest('.card');
      if(tulosCard&&uniikitCard&&tulosCard!==uniikitCard&&!tulosCard.dataset.combined){
        tulosCard.innerHTML=`<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;"><div style="font-size:11px;font-weight:800;">UDISC & METRIX TULOSKIERROKSET - <span style="color:#00ff00;">AUTO 15/5MIN</span></div><div id="live-kierrokset" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">${tulosEl.textContent}</div></div><div style="height:1px;background:#222;margin:8px 0;"></div><div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;"><div style="font-size:11px;font-weight:800;">UNIIKIT PELAAJAT - <span style="color:#00ff00;">AUTO</span></div><div id="live-pelaajat" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">${uniikitEl.textContent}</div></div>`;
        tulosCard.dataset.combined='true'; tulosCard.style.display='flex'; tulosCard.style.flexDirection='column';
        uniikitCard.innerHTML=`<div style="font-size:11px;font-weight:800;text-align:center;">HOLE IN ONE - <span style="color:#ffcc00;">MANUAALINEN</span></div><div id="hio-count" style="font-size:36px;font-weight:900;color:#ffcc00;margin:12px 0;text-align:center;">3</div><div id="hio-list" style="font-size:15px;font-weight:600;color:#ccc;line-height:1.8;text-align:center;">Ladataan...</div>`;
        uniikitCard.style.borderLeft='3px solid #ffcc00';
      }
    }
  }catch(e){}

  // SÄÄ KUVAKKEET ISOMMAKSI - 32px
  const sc=document.getElementById('saa-content');
  if(sc){
    try{
      const fc=await fetch('./data/foreca.json?t='+Date.now()).then(r=>r.json());
      if(fc.current && fc.hourly){
        sc.innerHTML=`<div style="display:flex;flex-direction:column;background:#0f0f0f;padding:12px;border-radius:8px;"><div style="display:flex;justify-content:space-between;"><div><div style="font-size:36px;font-weight:900;color:#fff;">${fc.current.temp}</div><div style="font-size:12px;color:#aaa;">Tuntuu ${fc.current.feels}</div></div><div style="text-align:right;font-size:11px;color:#aaa;"><div>Tuuli ${fc.current.wind}</div><div style="color:#00ff00;font-weight:700;margin-top:6px;">Foreca LIVE</div></div></div><div style="display:flex;justify-content:space-between;margin-top:14px;border-top:1px solid #222;padding-top:12px;">${fc.hourly.map(h=>`<div style="text-align:center;flex:1;"><div style="font-size:11px;color:#888;margin-bottom:4px;">${h.hour}</div><div style="font-size:32px;margin:4px 0;">${h.icon}</div><div style="font-size:14px;color:#fff;font-weight:800;">${h.temp}°</div></div>`).join('')}</div></div>`;
      }
    }catch(e){}
  }

  try{
    const hio=await fetch('./data/holeinone.json?t='+Date.now()).then(r=>r.json());
    const c=document.getElementById('hio-count'), l=document.getElementById('hio-list');
    if(c) c.textContent=hio.count||hio.players?.length||0;
    if(l&&hio.players) l.innerHTML=hio.players.map(p=>`${p.player} #${p.hole}`).join('<br>');
  }catch(e){}
}
loadAll(); setInterval(loadAll,300000);