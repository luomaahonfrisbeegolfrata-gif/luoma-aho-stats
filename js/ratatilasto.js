
(function(){
  const PNG_URL='./vaylatilasto.png';
  const JSON_URL='./data/ratatilasto.json';
  function init(){
    let target=document.getElementById('vaylatilasto-uusi');
    if(!target) return;
    function load(){
      // Päivitä PNG 1s välein
      const img=document.getElementById('vayla-live-img');
      if(img) img.src=PNG_URL+'?t='+Date.now();
      // Päivitä meta jos haluat
      fetch(JSON_URL+'?t='+Date.now()).then(r=>r.json()).then(d=>{
        const meta=document.getElementById('vayla-live-meta');
        if(meta) meta.textContent=`${d.Tot.Plays} heittoa | Avg ${d.Tot.Avg.toFixed(2)} | Päivitetty: ${d.updated?.slice(0,19).replace('T',' ')||''} | Auto 1s/5min`;
      });
    }
    load();
    setInterval(load,1000);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
