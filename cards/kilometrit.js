(function(){
  try{
    const el = document.getElementById('live-kilometrit');
    if(!el) return;
    fetch('./data/tilasto.json?v='+Date.now())
      .then(r=>r.json())
      .then(j=>{
        if(j.kilometrit) el.textContent = j.kilometrit;
      })
      .catch(()=>{});
  }catch(e){
    console.warn('[kilometrit] virhe:', e);
  }
})();