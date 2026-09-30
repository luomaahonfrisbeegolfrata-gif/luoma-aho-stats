
(function(){
  const PNG_URL='./vaylatilasto.png';
  function init(){
    function load(){
      const img=document.getElementById('vayla-live-img');
      if(img) img.src=PNG_URL+'?t='+Date.now();
    }
    load(); setInterval(load,1000);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
