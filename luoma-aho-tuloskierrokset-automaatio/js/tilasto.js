
// UDisc & Metrix tuloskierrokset LIVE - 1s
(function(){
  const URL='./data/tilasto.json';
  function init(){
    let target=document.getElementById('tuloskierrokset-auto');
    if(!target){
      // Etsi otsikko "UDisc & Metrix tuloskierrokset"
      const hs=[...document.querySelectorAll('h3')];
      for(const h of hs){ if(h.textContent.includes('tuloskierrokset')){ target=h.parentElement; break; } }
      if(!target) target=document.body;
    }
    function load(){
      fetch(URL+'?t='+Date.now()).then(r=>r.json()).then(d=>{
        const el=document.getElementById('tuloskierrokset-live');
        if(!el){
          const div=document.createElement('div');
          div.id='tuloskierrokset-live';
          div.style.cssText='background:#111;color:#fff;padding:15px;border-radius:10px;margin:15px 0;border:1px solid #333';
          target.appendChild(div);
        }
        document.getElementById('tuloskierrokset-live').innerHTML=`
          <h3 style="margin:0 0 10px;color:#fff">🔄 LIVE Tuloskierrokset (auto 1s / 5min)</h3>
          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px;font-size:14px">
            <div><b>1130</b><br>UDisc ${d.udisc.rounds} + Metrix 43119 ${d.metrix['43119'].rounds}<br><small style="color:#888">OIKEIN ei tuplata 1895</small></div>
            <div><b>Uniikit</b> ${d.yhteenveto.unique}<br>UDisc 67 + Metrix ~60<br><small style="color:#888">- päällekkäisyydet</small></div>
            <div><b>Peliaika</b> ${d.yhteenveto.playtime_h}h<br>UDisc 603h + 702×1.25h<br><small style="color:#888">${d.yhteenveto.playtime_h}h</small></div>
            <div><b>Askeleet</b> ${d.yhteenveto.steps.toLocaleString()}<br>3,100,890<br><small style="color:#888">2km×1300</small></div>
            <div><b>Kilometrit</b> ${d.yhteenveto.km} km<br>1130×2km<br><small style="color:#888">2825km UDisc 1.6mi</small></div>
            <div><b>Metrix</b><br>43119: ${d.metrix['43119'].rounds} (588+114)<br>44010: ${d.metrix['44010'].rounds} 44763: ${d.metrix['44763'].rounds}</div>
          </div>
          <p style="font-size:11px;color:#666;margin-top:10px">Päivitetty: ${d.paivitys || new Date().toISOString()} | Auto: GitHub 5min, sivu 1s | Lähteet: ${d.udisc.url} + ${d.metrix['43119'].url}</p>
        `;
      });
    }
    load(); setInterval(load,1000);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
