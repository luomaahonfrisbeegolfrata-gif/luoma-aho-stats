
// FULL AUTO 1s - TOP5 + SÄÄ + KIERROKSET + VAYLATILASTO
(function(){
  const TILASTO='./data/tilasto.json';
  const TOP5='./data/top5.json';
  const RATATILASTO='./data/ratatilasto.json';
  const PNG='./vaylatilasto.png';

  function init(){
    function load(){
      // TOP5 + SÄÄ
      fetch(TOP5+'?t='+Date.now()).then(r=>r.json()).then(d=>{
        // Metrix 44010
        const m1=document.getElementById('top5-44010');
        if(m1){
          m1.innerHTML=d.metrix_44010.top5.map(x=>`<li><span>${x.rank}. ${x.player}</span><span>${x.score}</span></li>`).join('');
        }
        const m2=document.getElementById('top5-44763');
        if(m2){
          m2.innerHTML=d.metrix_44763.top5.map(x=>`<li><span>${x.rank}. ${x.player}</span><span>${x.score}</span></li>`).join('');
        }
        const u=document.getElementById('top5-udisc');
        if(u){
          u.innerHTML=d.udisc.top5.map(x=>`<li><span>${x.rank}. ${x.player}</span><span>${x.score} (${x.date})</span></li>`).join('');
        }
        const s=document.getElementById('saa-content');
        if(s){
          const c=d.saa.current;
          s.innerHTML=`
            <div style="display:flex;justify-content:space-between;align-items:center"><div class="big">${c.temp}</div><div style="font-size:11px;color:#888">💧 ${c.humidity}<br>${c.precip}</div></div>
            <div class="small">Tuntuu ${c.feels}<br>${c.cloud}<br>Tuuli ${c.wind} | Puuska ${c.gust}<br>Näkyvyys ${c.visibility} | UV ${c.uv}</div>
          `;
        }
      });

      // Kierrokset, pelaajat, aika, askeleet, km
fetch('./data/tilasto.json?t='+Date.now()).then(r=>r.json()).then(d=>{
  document.getElementById('live-kierrokset').textContent = d.total || d.laskenta.kierrokset.arvo;
  document.getElementById('live-pelaajat').textContent = d.unique;
  document.getElementById('live-aika').textContent = d.playtime+'h';
  document.getElementById('live-askeleet').textContent = d.steps.toLocaleString('fi-FI');
  document.getElementById('live-km').textContent = d.km+' km';
});
      });

      // PNG alaosaan
      const img=document.getElementById('vayla-live-img');
      if(img) img.src=PNG+'?t='+Date.now();
    }
    load(); setInterval(load,1000);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
