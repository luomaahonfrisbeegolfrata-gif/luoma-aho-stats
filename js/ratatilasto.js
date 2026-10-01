async function loadAll(){
  const PAR_44010=41;
  const PAR_44763=82;
  const calc=(total,par)=>{
    const diff=total-par;
    if(diff>0) return {diff, score:`+${diff}`, display:`${total} (+${diff})`};
    if(diff<0) return {diff, score:`${diff}`, display:`${total} (${diff})`};
    return {diff:0, score:'E', display:`${total} (E)`};
  };
  try{
    const top=await fetch('./data/top5.json?t='+Date.now()).then(r=>r.json());
    const render=(id,arr,par)=>{
      const e=document.getElementById(id); if(!e) return;
      if(!arr||!arr.length){e.innerHTML='<li style="color:#888; font-size:11px;">Haetaan oikeita...</li>'; return;}
      // Suodata Pelaaja A-E fake
      let use=arr.filter(x=>!x.player.includes('Pelaaja A') && !x.player.includes('Pelaaja B') && !x.player.includes('Pelaaja C') && !x.player.includes('Pelaaja D') && !x.player.includes('Pelaaja E') && !x.player.includes('Pelaaja X') && !x.player.includes('Pelaaja Y'));
      if(use.length<3) use=arr.filter(x=>!x.player.includes('Pelaaja A'));
      if(use.length===0) use=arr;
      use=use.map(x=>{
        const total=x.total||parseInt((x.display||'').match(/\d+/)?.[0]||0);
        if(!total) return x;
        const d=calc(total, par);
        return {...x, total, diff:d.diff, score:d.score, display:d.display, sort:d.diff};
      }).sort((a,b)=>a.diff-b.diff);
      e.innerHTML=use.slice(0,5).map((x,i)=>`<li style="display:flex; justify-content:space-between; padding:5px 0; border-bottom:1px solid #222;"><span>${i+1}. ${x.player} ${x.display}</span></li>`).join('');
    };
    render('top5-44010', top.metrix_44010?.top5, PAR_44010);
    render('top5-44763', top.metrix_44763?.top5, PAR_44763);
    render('top5-udisc', top.udisc?.top5, PAR_44010);
  }catch(e){console.log(e);}
}
loadAll(); setInterval(loadAll,300000);
