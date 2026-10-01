async function loadAll(){
  try{
    const til=await fetch('./data/tilasto.json?t='+Date.now()).then(r=>{if(!r.ok) throw new Error('fail'); return r.json();});
    const el=id=>document.getElementById(id);
    if(til.total && til.total>=500 && el('live-kierrokset')) el('live-kierrokset').textContent=til.total;
    // Näytä harjoitus + kilpailu erikseen
    const cards=document.querySelectorAll('.card');
    cards.forEach(card=>{
      if(card.textContent.includes('UDisc') && card.textContent.includes('Metrix')){
        const udisc=til.udisc?.rounds||428;
        const m43119=til.metrix?.['43119']||702;
        const total=til.total||1130;
        const harj=til.harjoituskierrokset_yhteensa||1470;
        const kilp=til.kilpailukierrokset_yhteensa||0;
        const kaikki=til.total_kaikki||1898;
        card.querySelectorAll('div, span, p').forEach(d=>{
          if(d.textContent.includes('UDisc') && d.textContent.includes('Metrix')){
            d.innerHTML=`UDisc ${udisc} + Metrix 43119 ${m43119} = ${total} OIKEIN<br>Harjoitus ${harj} + Kilpailu ${kilp} = ${harj+kilp} Metrix (haku molemmat)<br>Kaikki 3 rataa ${kaikki}<br><span style="font-size:9px; color:#888;">43119:${til.metrix_detailed?.['43119']?.harjoitus||702}H+${til.metrix_detailed?.['43119']?.kilpailu||0}K 44010:${til.metrix_detailed?.['44010']?.harjoitus||598}H 44763:${til.metrix_detailed?.['44763']?.harjoitus||170}H</span>`;
            d.style.fontSize='11px'; d.style.lineHeight='1.3';
          }
        });
      }
    });
    if(el('live-pelaajat') && til.unique) el('live-pelaajat').textContent=til.unique;
    if(el('live-aika') && til.playtime) el('live-aika').textContent=til.playtime+'h';
    if(el('live-askeleet') && til.steps) el('live-askeleet').textContent=til.steps.toLocaleString('fi-FI');
    if(el('live-km') && til.km) el('live-km').textContent=til.km+' km';
  }catch(e){}

  // VÄYLÄTILASTO - KORJATTU VARI DIFFICULTY RIVILLÄ
  try{
    const rat=await fetch('./data/ratatilasto.json?t='+Date.now()).then(r=>r.json());
    document.querySelectorAll('table').forEach(table=>{
      if(table.textContent.includes('Vayla')){
        const over=rat.Avg.map((a,i)=>a-rat.Par[i]);
        const sorted=[...over].sort((a,b)=>a-b);
        const col=o=> o<=sorted[2]?'#66BB6A':o<=sorted[6]?'#FFEB3B':o<=sorted[8]?'#FFA726':'#EF5350';
        // KORJAUS: Etsi oikeat rivit nimellä, älä indeksillä
        table.querySelectorAll('tr').forEach(tr=>{
          const firstCell=tr.querySelector('td, th');
          if(!firstCell) return;
          const label=firstCell.textContent.trim().toLowerCase();
          if(label==='avg' || label==='difficulty'){
            tr.querySelectorAll('td').forEach((td,i)=>{
              if(i>=1&&i<=12){
                td.style.background=col(over[i-1]);
                td.style.color='#000';
                td.style.fontWeight='800';
                td.style.fontSize='12px';
              }
            });
          }
          if(label==='par'){
            // Par rivi EI saa olla värillinen - palauta musta
            tr.querySelectorAll('td').forEach(td=>{
              td.style.background='#0f0f0f';
              td.style.color='white';
            });
          }
        });
      }
    });
  }catch(e){}
}
loadAll();setInterval(loadAll,300000);
