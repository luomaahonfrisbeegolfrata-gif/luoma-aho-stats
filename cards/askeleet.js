(function(){
  try{
    const el = document.getElementById('live-askeleet');
    if(!el) return;
    fetch('./data/tilasto.json?v='+Date.now())
      .then(r=>r.json())
      .then(j=>{
        if(j.askeleet) el.textContent = Number(j.askeleet).toLocaleString('fi-FI');
      })
      .catch(()=>{});
  }catch(e){
    console.warn('[askeleet] virhe:', e);
  }
})();