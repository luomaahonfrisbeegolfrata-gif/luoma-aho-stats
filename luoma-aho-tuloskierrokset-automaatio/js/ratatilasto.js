
// Väylätilasto LIVE - 1s frontend, 5min GitHub
(function(){
  const JSON_URL='./data/ratatilasto.json';
  const PNG_URL='./vaylatilasto.png';
  function init(){
    let target=document.getElementById('vaylatilasto-auto');
    if(!target){ target=document.createElement('div'); target.id='vaylatilasto-auto'; document.body.appendChild(target); }
    function load(){
      fetch(JSON_URL+'?t='+Date.now()).then(r=>r.json()).then(data=>{
        const el=document.getElementById('vaylatilasto-auto');
        if(!el) return;
        if(!document.getElementById('live-vayla-inner')){
          el.innerHTML=`
            <div id="live-vayla-inner" style="margin-top:40px;padding:20px;background:#000;color:#fff;border-radius:12px;border:1px solid #333">
              <div style="display:flex;justify-content:space-between;align-items:center"><h2 style="color:#fff;margin:0">📊 Väylätilasto LIVE (sivun alaosassa)</h2><span style="background:#00ff00;color:#000;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:bold">● LIVE 1s / 5min</span></div>
              <p id="vayla-meta" style="color:#ccc"></p>
              <img id="vayla-png" src="${PNG_URL}?t=${Date.now()}" style="width:100%;max-width:1150px;border:1px solid #444;border-radius:8px">
            </div>`;
        }
        document.getElementById('vayla-meta').textContent=`${data.Tot.Plays} heittoa | Pituus ${data.Pituus.reduce((a,b)=>a+b,0)}m | Avg ${data.Tot.Avg.toFixed(2)} | Päivitetty ${data.updated?.slice(0,19).replace('T',' ')||''}`;
        document.getElementById('vayla-png').src=PNG_URL+'?t='+Date.now();
      }).catch(()=>{});
    }
    load(); setInterval(load,1000);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
