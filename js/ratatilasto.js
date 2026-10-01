async function loadAll(){
  try{
    const t=Date.now();
    const til=await fetch('./data/tilasto.json?t='+t).then(r=>r.json());
    const el=id=>document.getElementById(id);
    if(el('live-kierrokset')) el('live-kierrokset').textContent=til.total??1130;
    if(el('live-pelaajat')) el('live-pelaajat').textContent=til.unique??100;
    if(el('live-aika')) el('live-aika').textContent=(til.playtime??1481)+'h';
    if(el('live-askeleet')) el('live-askeleet').textContent=(til.steps??3100890).toLocaleString('fi-FI');
    if(el('live-km')) el('live-km').textContent=(til.km??2260)+' km';
  }catch(e){}
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>r.json());
    const render=(id,arr)=>{const e=document.getElementById(id);if(!e||!arr)return;e.innerHTML=arr.map(x=>'<li><span>'+x.rank+'. '+x.player+'</span><span>'+x.score+'</span></li>').join('');};
    render('top5-44010',top.metrix_44010?.top5);
    render('top5-44763',top.metrix_44763?.top5);
    render('top5-udisc',top.udisc?.top5);
    const s=top.saa?.current;
    const sc=document.getElementById('saa-content');
    if(sc&&s){sc.innerHTML='<div class="big">'+s.temp+'</div><div class="small">'+s.feels+' | '+s.humidity+' | '+s.wind+' | '+s.cloud+'<br>'+s.precip+' sade | Gust '+s.gust+'<br><span style="color:#00ff00">'+s.updated+'</span></div>';}
  }catch(e){}
  try{const img=document.getElementById('vayla-live-img');if(img) img.src='./vaylatilasto.png?t='+Date.now();}catch(e){}
}
loadAll();setInterval(loadAll,5000);
