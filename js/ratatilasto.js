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
  }catch(e){}

  // FORECA WIDGET - korvaa vanhan meteo SAA:n
  const sc=document.getElementById('saa-content');
  if(sc){
    sc.innerHTML = `
      <div style="margin:-10px -10px -10px -10px; border-radius:12px; overflow:hidden; background:#181818;">
        <!-- Foreca Täsmäsää Alajärvi - virallinen widget -->
        <iframe 
          src="https://www.foreca.fi/Finland/Alajarvi?detail=20251001&quick=true" 
          style="width:100%; height:420px; border:0; background:#181818; filter:invert(0.9) hue-rotate(180deg);" 
          loading="lazy"
          title="Foreca Alajarvi">
        </iframe>
        <div style="font-size:9px; color:#666; padding:4px 8px; background:#000; display:flex; justify-content:space-between;">
          <span>Foreca Täsmäsää™ Luoma-aho, Alajärvi - tarkin Suomen malli</span>
          <a href="https://www.foreca.fi/Finland/Alajarvi" target="_blank" style="color:#00ff00; text-decoration:none;">Avaa Foreca →</a>
        </div>
      </div>
    `;
  }

  try{const img=document.getElementById('vayla-live-img');if(img) img.src='./vaylatilasto.png?t='+Date.now();}catch(e){}
}
loadAll();setInterval(loadAll,30000);
