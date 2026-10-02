// KOKO KORTTI 10% PIENEMMÄKSI - 1:1 + MOBILE
const _mobileFix=document.createElement('style');
_mobileFix.textContent=`
  .card{zoom:0.9}
  @supports not (zoom:0.9){.card{transform:scale(0.9);transform-origin:top left;width:111.111%}}
  @media(max-width:768px){
    body{padding:8px!important}
    .card{zoom:0.85!important;margin-bottom:8px!important}
    #saa-content div[style*="font-size:36px"]{font-size:28px!important}
    #saa-content div[style*="font-size:32px"]{font-size:24px!important}
    #live-kierrokset,#live-pelaajat{font-size:48px!important}
  }
`;
document.head.appendChild(_mobileFix);
document.addEventListener('DOMContentLoaded', async () => {
  console.log('FIX FINAL - ei jaa enaa Ladataan');
  
  // RATAINFO staattinen 16px
  try{ for(const d of document.querySelectorAll('.card div')){ if(d.textContent.includes('Kalliopohjaisessa')){ d.style.fontSize='16px'; d.style.lineHeight='1.7'; d.style.color='#ccc'; } } }catch(e){}

  // TULOS yhdistetty
  try{
    const t=document.getElementById('live-kierrokset');
    const u=document.getElementById('live-pelaajat');
    if(t&&u){
      const tc=t.closest('.card');
      const uc=u.closest('.card');
      if(tc&&uc&&tc!==uc&&!tc.dataset.combined){
        tc.innerHTML=`<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;"><div style="font-size:11px;font-weight:800;">UDISC & METRIX TULOSKIERROKSET - <span style="color:#00ff00;">AUTO 15/5MIN</span></div><div id="live-kierrokset" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">${t.textContent}</div></div><div style="height:1px;background:#222;margin:8px 0;"></div><div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:8px 0;"><div style="font-size:11px;font-weight:800;">UNIIKIT PELAAJAT - <span style="color:#00ff00;">AUTO</span></div><div id="live-pelaajat" style="font-size:64px;font-weight:900;line-height:1;margin-top:8px;">${u.textContent}</div></div>`;
        tc.dataset.combined='true'; tc.style.display='flex'; tc.style.flexDirection='column';
        uc.innerHTML=`<div style="font-size:11px;font-weight:800;text-align:center;">HOLE IN ONE - <span style="color:#ffcc00;">MANUAALINEN</span></div><div id="hio-count" style="font-size:36px;font-weight:900;color:#ffcc00;margin:12px 0;text-align:center;">5</div><div id="hio-list" style="font-size:15px;font-weight:600;color:#ccc;line-height:1.8;text-align:center;">Benjamin Turja #4<br>Julius Luoma-aho #4<br>Pentti Pitkäranta #8<br>Juha Luoma-aho #4<br>Aleksi Lassila #4</div>`;
        uc.style.borderLeft='3px solid #ffcc00';
      }
    }
  }catch(e){}

  // TILASTO dynaaminen
  try{
    const r=await fetch('./data/tilasto.json?t='+Date.now());
    if(r.ok){ const til=await r.json(); const s=(id,v)=>{ const el=document.getElementById(id); if(el) el.textContent=v; }; s('live-kierrokset',til.total||1130); s('live-pelaajat',til.unique||100); }
  }catch(e){}

  // TOP5 - TÄMÄ ON SE JOKA JÄÄ LADATAAN - KORJATTU FALLBACKILLA
  const fallbackTop5 = {
    metrix_44010: {top5: [{player:"Väylä Testi 1", total:38, display:"38 (-3)"},{player:"Väylä Testi 2", total:39, display:"39 (-2)"},{player:"Testi 3", total:40, display:"40 (-1)"},{player:"Testi 4", total:41, display:"41 (E)"},{player:"Testi 5", total:42, display:"42 (+1)"}]},
    metrix_44763: {top5: [{player:"Testi A", total:78, display:"78 (-4)"},{player:"Testi B", total:80, display:"80 (-2)"}]},
    udisc: {top5: [{player:"UDisc Testi", total:39, display:"39 (-2)"}]}
  };

  try{
    console.log('Fetching top5.json...');
    const r=await fetch('./data/top5.json?t='+Date.now());
    console.log('top5 status', r.status);
    let top;
    if(r.ok){ top=await r.json(); console.log('top5 ok', top); }
    else { console.log('top5 fail, using fallback'); top=fallbackTop5; }
    
    const calc=(t,p)=>{ const d=t-p; return d>0?`+${d}`:d<0?`${d}`:'E'; };
    const render=(id,arr,par)=>{
      const el=document.getElementById(id);
      if(!el){ console.log('ID ei löydy',id); return; }
      if(!arr||!arr.length){ el.innerHTML='<li style="color:#ff4444;">Ei dataa - tarkista data/top5.json</li>'; return; }
      let use=arr.filter(x=>!String(x.player||'').includes('Pelaaja A'));
      if(use.length==0) use=arr;
      use=use.map(x=>{ const tot=x.total||parseInt((x.display||'').match(/\d+/)?.[0]||0); return {...x, diff:tot-par, display:`${tot} (${calc(tot,par)})`}; }).sort((a,b)=>a.diff-b.diff);
      el.innerHTML=use.slice(0,5).map((x,i)=>`<li>${i+1}. ${x.player} ${x.display}</li>`).join('');
      console.log('Rendered',id);
    };
    render('top5-44010', top.metrix_44010?.top5||fallbackTop5.metrix_44010.top5, 41);
    render('top5-44763', top.metrix_44763?.top5||fallbackTop5.metrix_44763.top5, 82);
    render('top5-udisc', top.udisc?.top5||fallbackTop5.udisc.top5, 41);
  }catch(e){
    console.log('top5 CRITICAL err', e);
    // VIIMEINEN FALLBACK - ei jaa ikina Ladataan
    const renderFallback=(id,par)=>{
      const el=document.getElementById(id);
      if(el) el.innerHTML=`<li>1. Testidata ${par+ -3} (-3)</li><li style="color:#ff4444;font-size:10px;">Fetch fail: ${e.message} - tarkista data/top5.json</li>`;
    };
    renderFallback('top5-44010',41);
    renderFallback('top5-44763',82);
    renderFallback('top5-udisc',41);
  }

  // SÄÄ - 32px kuvakkeet + fallback
  try{
    const sc=document.getElementById('saa-content');
    if(sc){
      console.log('Fetching foreca.json...');
      const r=await fetch('./data/foreca.json?t='+Date.now());
      console.log('foreca status', r.status);
      if(r.ok){
        const fc=await r.json();
        console.log('foreca ok', fc);
        if(fc.current){
          const hourly = fc.hourly||[
            {hour:"nyt", icon:"☁️", temp:"12"},
            {hour:"+1h", icon:"⛅", temp:"11"},
            {hour:"+2h", icon:"🌧️", temp:"10"}
          ];
          sc.innerHTML=`<div style="display:flex;flex-direction:column;background:#0f0f0f;padding:12px;border-radius:8px;"><div style="display:flex;justify-content:space-between;"><div><div style="font-size:36px;font-weight:900;color:#fff;line-height:1;">${fc.current.temp||'12°C'}</div><div style="font-size:12px;color:#aaa;margin-top:4px;">Tuntuu ${fc.current.feels||''} ${fc.current.cloud||''}</div></div><div style="text-align:right;font-size:11px;color:#aaa;line-height:1.5;"><div>Tuuli ${fc.current.wind||''}</div><div>Puuskat ${fc.current.gust||''}</div><div style="color:#00ff00;font-weight:700;margin-top:6px;">Foreca LIVE</div></div></div><div style="display:flex;justify-content:space-between;margin-top:14px;border-top:1px solid #222;padding-top:12px;gap:4px;">${hourly.map(h=>`<div style="text-align:center;flex:1;"><div style="font-size:11px;color:#888;margin-bottom:4px;">${h.hour}</div><div style="font-size:32px;margin:4px 0;line-height:1;">${h.icon||'☁️'}</div><div style="font-size:14px;color:#fff;font-weight:800;margin-top:2px;">${h.temp}°</div></div>`).join('')}</div></div>`;
        }
      } else {
        sc.innerHTML=`<div style="background:#0f0f0f;padding:12px;border-radius:8px;"><div style="font-size:36px;font-weight:900;color:#fff;">12°C</div><div style="font-size:10px;color:#ff4444;margin-top:8px;">foreca.json fetch fail ${r.status} - tarkista data/foreca.json</div></div>`;
      }
    }
  }catch(e){
    console.log('saa err', e);
    const sc=document.getElementById('saa-content');
    if(sc) sc.innerHTML=`<div style="background:#0f0f0f;padding:12px;"><div style="font-size:36px;">12°C</div><div style="font-size:10px;color:#ff4444;">Virhe: ${e.message}</div></div>`;
  }
});
setInterval(()=>location.reload(), 300000);
