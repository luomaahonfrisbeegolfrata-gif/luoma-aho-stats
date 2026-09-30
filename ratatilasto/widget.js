// Luoma-aho widget - upota ilman että kosket index.html:ään pysyvästi
// Lisää index.html:ään KERRAN: <div id="luoma-aho-ratatilasto"></div><script src="./ratatilasto/widget.js"></script>
// Sen jälkeen tämä hakee ratatilasto/stats.json ja renderöi taulun automaattisesti
(function(){
  const targetId = "luoma-aho-ratatilasto";
  const jsonUrl = "./ratatilasto/stats.json";
  const container = document.getElementById(targetId);
  if(!container) return;
  fetch(jsonUrl).then(r=>r.json()).then(data=>{
    const GREEN="#66BB6A", YELLOW="#FFEB3B", ORANGE="#FFA726", RED="#EF5350";
    const over = data.Avg.map((a,i)=>a-data.Par[i]);
    const sortedOver = [...over].sort((a,b)=>a-b);
    function col(o){
      if(o<=sortedOver[2]) return GREEN;
      if(o<=sortedOver[6]) return YELLOW;
      if(o<=sortedOver[8]) return ORANGE;
      return RED;
    }
    let html = `<table style="border-collapse:collapse;width:100%;table-layout:fixed;font-size:12px"><tr><th>Väylä</th>${[...Array(12)].map((_,i)=>`<th>${i+1}</th>`).join('')}<th>Tot</th><th>%</th></tr>`;
    function addRow(label, arr, tot, pct, colors){
      html+=`<tr><td>${label}</td>`;
      arr.forEach((v,i)=>{
        const style = colors ? `style="background:${colors[i]}"` : "";
        html+=`<td ${style}>${v}</td>`;
      });
      html+=`<td><b>${tot}</b></td><td>${pct||'-'}</td></tr>`;
    }
    const colors = over.map(col);
    addRow("Par", data.Par, data.Tot.Par);
    addRow("Avg", data.Avg.map(x=>x.toFixed(2)), data.Tot.Avg.toFixed(2), "-", colors);
    addRow("Difficulty", data.Difficulty, data.OverPar.toFixed(2), "-", colors);
    addRow("Birdie -1", data.Birdie, data.Tot.Birdie, data.Pct.Birdie+"%");
    addRow("Par 0", data.Par0, data.Tot.Par0, data.Pct.Par0+"%");
    addRow("Bogey 1", data.Bogey1, data.Tot.Bogey1, data.Pct.Bogey1+"%");
    addRow("Double 2", data.Double2, data.Tot.Double2, data.Pct.Double2+"%");
    addRow("Triple 3", data.Triple3, data.Tot.Triple3, data.Pct.Triple3+"%");
    addRow("Other >3", data.Other, data.Tot.Other, data.Pct.Other+"%");
    html+="</table><small>Päivitetty: "+data.updated.slice(0,16).replace('T',' ')+"</small>";
    container.innerHTML = html;
  });
})();
