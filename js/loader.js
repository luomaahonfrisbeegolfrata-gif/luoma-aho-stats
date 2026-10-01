(function(){
  const CARDS = [
    'js/cards/ratainfo.js',
    'js/cards/tuloskierrokset.js',
    'js/cards/peliaika.js',
    'js/cards/askeleet.js',
    'js/cards/kilometrit.js',
    'js/cards/metrix44010.js',
    'js/cards/metrix44763.js',
    'js/cards/udisc.js',
    'js/cards/saa.js',
    'js/cards/hio.js',
    'js/cards/vaylatilasto.js'
  ];

  function loadScript(src){
    return new Promise((resolve)=>{
      try{
        const s = document.createElement('script');
        s.src = src + '?v=' + Date.now();
        s.async = false;
        s.onload = ()=> resolve({src, ok:true});
        s.onerror = (e)=> {
          console.warn('[loader] FAIL:', src, e);
          resolve({src, ok:false, error:e});
        };
        document.head.appendChild(s);
      }catch(e){
        console.warn('[loader] exception:', src, e);
        resolve({src, ok:false, error:e});
      }
    });
  }

  async function run(){
    console.log('[loader] start', CARDS.length, 'korttia');
    for(let i=0;i<CARDS.length;i++){
      const src = CARDS[i];
      try{
        const res = await loadScript(src);
        if(res.ok) console.log('[loader] OK:', src);
        else console.warn('[loader] SKIP:', src);
      }catch(e){
        console.warn('[loader] catch:', src, e);
      }
      // 50ms väli ettei blokkaa renderiä
      await new Promise(r=>setTimeout(r, 50));
    }
    console.log('[loader] kaikki ladattu (virheelliset ohitettu)');
  }

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded', run);
  }else{
    run();
  }
})();