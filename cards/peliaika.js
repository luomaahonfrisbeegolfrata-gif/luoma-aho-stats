(function(){
  try{
    const el = document.getElementById('live-peliaika');
    if(!el) return;
    fetch('./data/tilasto.json?v='+Date.now())
      .then(r=>r.json())
      .then(j=>{
        if(j.peliaika) el.textContent = j.peliaika;
        if(j.peliaika_raw) el.setAttribute('title', j.peliaika_raw+' min');
      })
      .catch(()=>{});
  }catch(e){
    console.warn('[peliaika] virhe:', e);
  }
})();