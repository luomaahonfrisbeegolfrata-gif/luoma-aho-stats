// Luoma-aho - puskee suoraan olemassa olevaan Väylätilasto-taulukkoon
// Lisää index.html:ään KERRAN ennen </body>:
// <script src="./ratatilasto/widget-vayla.js"></script>
// Sen jälkeen tämä löytää sivun "Pituus" taulukon ja lisää sen jälkeen automaattisesti live-kuvan + tarkan taulun
// Ei koske index.html:ää enää koskaan - päivittyy stats.json + png kautta

(function(){
  const JSON_URL = "./ratatilasto/stats.json";
  const PNG_URL = "./ratatilasto/ratatilasto.png";
  
  function findVaylaTable(){
    // Etsi taulukko jossa on "Pituus" rivi - se on sun nykyinen Väylätilasto
    const tables = document.querySelectorAll('table');
    for(const t of tables){
      if(t.textContent.includes('Pituus') && t.textContent.includes('Väylä')){
        return t;
      }
    }
    return null;
  }

  function makeColor(over){
    const sorted = [...over].sort((a,b)=>a-b);
    const GREEN="#66BB6A", YELLOW="#FFEB3B", ORANGE="#FFA726", RED="#EF5350";
    return over.map(o=>{
      if(o <= sorted[2]) return GREEN;
      if(o <= sorted[6]) return YELLOW;
      if(o <= sorted[8]) return ORANGE;
      return RED;
    });
  }

  fetch(JSON_URL + "?t=" + Date.now())
    .then(r=>r.json())
    .then(data=>{
      const target = findVaylaTable();
      if(!target){
        console.log("Väylätilasto-taulukkoa ei löytynyt");
        return;
      }

      // Estä tuplalisäys
      if(document.getElementById('luoma-aho-auto-stats')) return;

      const over = data.Avg.map((a,i)=>a-data.Par[i]);
      const colors = makeColor(over);

      const div = document.createElement('div');
      div.id = 'luoma-aho-auto-stats';
      div.style.marginTop = '20px';
      div.innerHTML = `
        <h3>📊 Live Väylätilasto - automaattisesti päivitetty</h3>
        <p><b>${data.Tot.Plays} heittoa</b> (Metrix 44010 ${data.sources['44010_plays']} + 44763 ${data.sources['44763_plays']} + UDisc ${data.sources['udisc_plays']}) | 
        <b>Avg ${data.Tot.Avg.toFixed(2)}</b> (Par ${data.Tot.Par} +${data.OverPar.toFixed(2)})</p>
        
        <img src="${PNG_URL}?t=${Date.now()}" alt="Ratatilasto" style="width:100%;max-width:1150px;border:1px solid #ddd;border-radius:8px;display:block;margin:10px 0">
        
        <details open style="margin-top:15px">
          <summary style="cursor:pointer;font-weight:600">Näytä tarkka taulukko (Birdie/Par/Bogey...)</summary>
          <div style="overflow-x:auto;margin-top:10px">
            <table style="border-collapse:collapse;width:100%;table-layout:fixed;font-size:12px;min-width:700px">
              <tr><th>Väylä</th>${[...Array(12)].map((_,i)=>`<th>${i+1}</th>`).join('')}<th>Tot</th><th>%</th></tr>
              <tr><td>Par</td>${data.Par.map(v=>`<td>${v}</td>`).join('')}<td><b>${data.Tot.Par}</b></td><td>-</td></tr>
              <tr><td>Avg</td>${data.Avg.map((v,i)=>`<td style="background:${colors[i]}">${v.toFixed(2)}</td>`).join('')}<td><b>${data.Tot.Avg.toFixed(2)}</b></td><td>-</td></tr>
              <tr><td>Difficulty</td>${data.Difficulty.map((v,i)=>`<td style="background:${colors[i]}">${v}</td>`).join('')}<td><b>${data.OverPar.toFixed(2)}</b></td><td>-</td></tr>
              <tr><td>Birdie -1</td>${data.Birdie.map(v=>`<td>${v}</td>`).join('')}<td><b>${data.Tot.Birdie}</b></td><td>${data.Pct.Birdie}%</td></tr>
              <tr><td>Par 0</td>${data.Par0.map(v=>`<td>${v}</td>`).join('')}<td><b>${data.Tot.Par0}</b></td><td>${data.Pct.Par0}%</td></tr>
              <tr><td>Bogey 1</td>${data.Bogey1.map(v=>`<td>${v}</td>`).join('')}<td><b>${data.Tot.Bogey1}</b></td><td>${data.Pct.Bogey1}%</td></tr>
              <tr><td>Double 2</td>${data.Double2.map(v=>`<td>${v}</td>`).join('')}<td><b>${data.Tot.Double2}</b></td><td>${data.Pct.Double2}%</td></tr>
              <tr><td>Triple 3</td>${data.Triple3.map(v=>`<td>${v}</td>`).join('')}<td><b>${data.Tot.Triple3}</b></td><td>${data.Pct.Triple3}%</td></tr>
              <tr><td>Other >3</td>${data.Other.map(v=>`<td>${v}</td>`).join('')}<td><b>${data.Tot.Other}</b></td><td>${data.Pct.Other}%</td></tr>
            </table>
          </div>
        </details>
        <p style="font-size:11px;color:#666;margin-top:8px">
          Värit: <span style="background:#66BB6A;padding:2px 6px">🟢 helpoin</span> 
          <span style="background:#FFEB3B;padding:2px 6px">🟡 keskitaso</span> 
          <span style="background:#FFA726;padding:2px 6px">🟠 vaativa</span> 
          <span style="background:#EF5350;padding:2px 6px">🔴 vaikein</span> 
          | Päivitetty: ${data.updated.slice(0,16).replace('T',' ')} | 
          <a href="./ratatilasto/" target="_blank">Avaa erillisenä sivuna</a>
        </p>
        <hr style="margin:20px 0">
      `;

      // Lisää heti nykyisen Väylätilasto-taulukon jälkeen
      target.parentNode.insertBefore(div, target.nextSibling);
      
      // Päivitä myös se "Helpoin 3 (vihreä...)" teksti automaattisesti
      const infoText = document.evaluate("//text()[contains(., 'Helpoin')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
      if(infoText){
        const sortedIdx = over.map((o,i)=>({o,i})).sort((a,b)=>a.o-b.o).map(x=>x.i+1);
        const green = sortedIdx.slice(0,3).join(',');
        const yellow = sortedIdx.slice(3,7).join(',');
        const orange = sortedIdx.slice(7,9).join(',');
        const red = sortedIdx.slice(9,12).join(',');
        infoText.textContent = `Helpoin 3 (vihreä 1-3) ${green}  Keskitaso 3 (keltainen 4-6) ${yellow}  Vaativa 3 (oranssi 7-9) ${orange}  Vaikein 3 (punainen 10-12) ${red} | Auto-päivitetty ${data.updated.slice(0,10)}`;
      }
    })
    .catch(e=>console.error("Ratatilasto widget virhe:", e));
})();
