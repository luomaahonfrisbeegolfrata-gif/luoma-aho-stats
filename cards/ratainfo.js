(function(){
  try{
    for(const d of document.querySelectorAll('.card div')){
      if(d.textContent.includes('Kalliopohjaisessa')){
        d.style.fontSize='16px';
        d.style.lineHeight='1.7';
        d.style.color='#ccc';
      }
    }
  }catch(e){
    console.warn('[ratainfo] virhe:', e);
  }
})();