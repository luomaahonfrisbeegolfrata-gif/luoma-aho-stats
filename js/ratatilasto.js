async function loadAll(){
  const PAR=41;
  const calc=(total)=>{
    const diff=total-PAR;
    if(diff>0) return {diff, score:`+${diff}`, display:`${total} (+${diff})`};
    if(diff<0) return {diff, score:`${diff}`, display:`${total} (${diff})`};
    return {diff:0, score:'E', display:`${total} (E)`};
  };
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>r.json());
    const render=(id,arr)=>{
      const e=document.getElementById(id); if(!e) return;
      if(!arr||!arr.length){e.innerHTML='<li>Haetaan...</li>'; return;}
      // PAR 41: yli 41 = +, alle 41 = -
      let use=arr.filter(x=>x.player && !x.player.includes('Pelaaja A') && !x.player.includes('Pelaaja B')).map(x=>{
        const total=x.total||parseInt((x.display||'').match(/\d+/)?.[0]||0);
        const d=total?calc(total):{diff:x.diff, score:x.score, display:x.display};
        return {...x, total: total||x.total, diff: d.diff, score: d.score, display: d.display, sort: d.diff};
      });
      use=use.sort((a,b)=>a.diff-b.diff);
      e.innerHTML=use.slice(0,5).map((x,i)=>`<li style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #222;"><span>${i+1}. ${x.player} ${x.display}</span></li>`).join('');
    };
    render('top5-44010', top.metrix_44010?.top5);
    render('top5-44763', top.metrix_44763?.top5);
    render('top5-udisc', top.udisc?.top5);
  }catch(e){}
}
loadAll(); setInterval(loadAll,300000);
