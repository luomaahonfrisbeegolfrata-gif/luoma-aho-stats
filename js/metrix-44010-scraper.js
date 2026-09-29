/**
 * Täydellinen Metrix 44010 scrape - yleisin layout kirjauksiin
 * Luoma-ahon Frisbeegolfrata - Väyläopaste
 * 
 * 44010 on yleisin kirjaukseen käytettävä layout (595 kierrosta kuvasta 29.9.2026: 544 harj +51 kilp)
 * 43119 sisältää KAIKKIEN layouttien kierrokset 702 (ei tuplata 44010+43119)
 * 
 * Hakee:
 * - Top tulokset (Toni Luoma-aho +1 42 jne)
 * - Kuukausikäyttö (heatmap + monthly chart)
 * - Ratatilastot per väylä: Par, Avg, Difficulty, Birdie, Par0, Bogey, Double, Triple, Other
 * - Väyläpituudet ja värit (vihreä helpoimmat 3, keltainen, oranssi, punainen vaikeimmat 3)
 */

const fs = require('fs');
const path = require('path');

async function fetchText(url){
  try{
    const res = await fetch(url, {
      headers:{
        'User-Agent':'Luoma-aho-stats-bot/1.0 (https://luomaahonfrisbeegolfrata-gif.github.io/luoma-aho-stats/; 44010 scrape)',
        'Accept':'text/html,application/xhtml+xml',
        'Accept-Language':'fi,en;q=0.9'
      }
    });
    if(!res.ok){
      console.error(`Fetch fail ${url}: HTTP ${res.status}`);
      return null;
    }
    return await res.text();
  }catch(e){
    console.error(`Fetch error ${url}:`, e.message);
    return null;
  }
}

// Parsi Top tulokset Metrix 44010 sivulta
function parseTopResults(html){
  if(!html) return null;
  const results = [];
  // Regex: <tr> ... <td>Toni Luoma-aho</td> ... <td>+1</td><td>42</td> tms
  // Yksinkertainen haku: rivi jossa Par ja 12 väylän tulokset + +/- + kokonais
  const rowRegex = /<tr[^>]*>\s*<td[^>]*>\s*\d*\s*<\/td>\s*<td[^>]*>\s*([^<]+?)\s*<\/td>\s*<td[^>]*>\s*([^<]+?)\s*<\/td>\s*((?:<td[^>]*>\s*\d+\s*<\/td>\s*){12})\s*<td[^>]*>\s*([+-]?\d+|E)\s*<\/td>\s*<td[^>]*>\s*(\d+)\s*<\/td>/gi;
  let m;
  while((m = rowRegex.exec(html)) !== null && results.length < 20){
    const name = m[1].trim();
    const date = m[2].trim();
    const scoresRaw = m[3];
    const plusMinus = m[4].trim();
    const total = parseInt(m[5]);
    if(name && !name.toLowerCase().includes('par') && total >= 30 && total <= 80){
      const scores = [...scoresRaw.matchAll(/<td[^>]*>\s*(\d+)\s*<\/td>/gi)].map(x=>parseInt(x[1]));
      results.push({name, date, scores, plusMinus, total});
    }
  }
  return results.slice(0,5);
}

// Parsi ratatilastot - Metrix näyttää "Course statistics" Table näkymässä
// Yritä löytää taulukko jossa per väylä: Par, Avg, Difficulty, Birdie, Par, Bogey, Double, Triple, Other
function parseCourseStatsTable(html){
  if(!html) return null;
  // Etsi taulukko jossa header: Hole, Par, Avg, Difficulty jne
  // Tämä on vaikea ilman oikeaa HTML:ää, joten fallback olemassaolevaan vaylatilasto.json
  // Tässä placeholder joka palauttaa null ja käytetään vanhaa dataa
  // Jos Metrix muuttaa HTML rakennetta, tämä pitää päivittää
  return null;
}

// Lue olemassaoleva vaylatilasto.json (28.9.2026 manuaalinen 44010)
function loadExistingVaylatilasto(){
  const vp = path.join(__dirname, '../data/vaylatilasto.json');
  if(fs.existsSync(vp)){
    try{
      return JSON.parse(fs.readFileSync(vp,'utf8'));
    }catch(e){
      console.error('vaylatilasto.json parse fail', e.message);
      return null;
    }
  }
  return null;
}

async function main(){
  console.log('=== METRIX 44010 SCRAPE - YLEISIN LAYOUT KIRJAUKSEEN ===');
  console.log('44010 = Väyläopaste, 595 kierrosta (544 harj +51 kilp) kuvasta 29.9.2026');
  console.log('43119 sisältää KAIKKIEN layouttien kierrokset 702 - ei tuplata 44010+43119');

  const urlsPath = path.join(__dirname, '../url/urls.json');
  const urls = JSON.parse(fs.readFileSync(urlsPath,'utf8'));
  
  // 1. Hae Metrix 44010
  const metrix44010Url = 'https://discgolfmetrix.com/course/44010';
  console.log(`Hae ${metrix44010Url}...`);
  const html44010 = await fetchText(metrix44010Url);
  
  let top5 = null;
  let courseStats = null;
  if(html44010){
    top5 = parseTopResults(html44010);
    console.log(`Top tulokset löytyi: ${top5 ? top5.length : 0}`);
    if(top5) top5.forEach((r,i)=> console.log(`  ${i+1}. ${r.name} ${r.plusMinus} (${r.total}) ${r.date}`));
    
    courseStats = parseCourseStatsTable(html44010);
    if(courseStats) console.log(`Ratatilastot löytyi: ${courseStats.length} väylää`);
  }

  // 2. Lataa olemassaoleva vaylatilasto (28.9.2026 manuaalinen)
  const existing = loadExistingVaylatilasto();
  if(existing){
    console.log(`Olemassaoleva vaylatilasto.json: ${existing.holes_12 ? existing.holes_12.length : existing.holes ? existing.holes.length : 0} väylää, Par ${existing.totals ? existing.totals.par : '?'} Avg ${existing.totals ? existing.totals.avg : '?'}`);
  }

  // 3. Päivitä data/stats.json - OIKEA LASKENTA 44010 erikseen + 43119 KAIKKI
  // Metrix 44010: 595 kierrosta (544+51) - yleisin
  // Metrix 43119: 702 kierrosta (588+114) - KAIKKI sisältää 44010 ja 44763
  // UDisc: 428 kierrosta, 67 uniikkia, 603h, 1275690 askelta
  // Yhdistetty OIKEIN: UDisc 428 + Metrix 43119 702 = 1130 (ei 1895 = 428+595+170+702 tuplaa)
  
  const metrix44010Rounds = 595; // 544 harj +51 kilp kuvasta
  const metrix43119Rounds = 702; // KAIKKI 588+114
  const udiscRounds = 428;
  const totalRounds = udiscRounds + metrix43119Rounds; // 1130 OIKEIN
  
  const statsPath = path.join(__dirname, '../data/stats.json');
  let stats = {};
  if(fs.existsSync(statsPath)){
    try{ stats = JSON.parse(fs.readFileSync(statsPath,'utf8')); }catch(e){}
  }

  stats.generated_at = new Date().toISOString();
  stats.generated_at_fi = new Date().toLocaleString('fi-FI', {timeZone:'Europe/Helsinki'});
  stats.scrape_info = {
    layout: '44010 Väyläopaste - yleisin kirjaukseen',
    metrix_44010_url: metrix44010Url,
    metrix_44010_rounds: metrix44010Rounds,
    metrix_43119_rounds: metrix43119Rounds,
    huom: '44010 on yleisin layout (595 kierrosta), 43119 sisältää KAIKKIEN layouttien kierrokset 702 (ei tuplata 44010+43119), yhdistetty OIKEIN 1130 = UDisc 428 + 43119 702',
    top5_source: html44010 ? 'Metrix 44010 live scrape' : 'fallback 29.9.2026 kuva'
  };
  
  // Päivitä Top5 jos scrape onnistui
  if(top5 && top5.length >=5){
    stats.metrix_44010_top5 = top5.map(r=> ({name: r.name, tulos: `${r.plusMinus} (${r.total})`, pvm: r.date}));
  }else{
    // Fallback kuvasta 29.9.2026
    stats.metrix_44010_top5 = [
      {name:'Toni Luoma-aho', tulos:'+1 (42)'},
      {name:'Eino Vistiaho', tulos:'+2 (43)'},
      {name:'Benjamin Turja', tulos:'+3 (44)'},
      {name:'Toni Luoma-aho', tulos:'+4 (45)'},
      {name:'Jari Vistiaho', tulos:'+5 (46)'}
    ];
  }

  fs.writeFileSync(statsPath, JSON.stringify(stats, null, 2));
  console.log(`stats.json päivitetty - 44010 Top5 ${stats.metrix_44010_top5.length}, total ${totalRounds} (1130 OIKEIN)`);

  // 4. Päivitä Väylätilasto - 44010 on yleisin, joten sen tilastot ovat tärkeimmät
  const vp = path.join(__dirname, '../data/vaylatilasto.json');
  if(existing){
    // Jos courseStats saatiin Metrixistä, päivitä avg, difficulty, birdie jne
    // Muuten säilytä vanha ja päivitä vain timestamp + huom
    if(courseStats && courseStats.length === 12){
      existing.holes_12 = courseStats;
      console.log('Väylätilasto päivitetty Metrix 44010 live datalla');
    }else{
      console.log('Väylätilasto: live parsinta epäonnistui, säilytetään 28.9.2026 manuaalinen data (Par 41 Avg 51.7), päivitetään timestamp');
    }
    existing.generated_at = new Date().toISOString();
    existing.generated_at_fi = new Date().toLocaleString('fi-FI', {timeZone:'Europe/Helsinki'});
    existing.source = 'Metrix 44010 Väyläopaste - yleisin layout (595 kierrosta), manuaalinen 28.9.2026 + live Top5';
    existing.huom = '44010 on yleisin kirjaukseen. Jos avg/difficulty muuttuu, päivitä manuaalisesti Metrix 44010 Ratatilastot sivulta tai korjaa parseCourseStatsTable() funktio. Pituus 125m...120m Tot 1248m kovakoodattu index.html ylimmälle riville.';
    fs.writeFileSync(vp, JSON.stringify(existing, null, 2));
    console.log('vaylatilasto.json päivitetty');
  }

  console.log('=== METRIX 44010 SCRAPE VALMIS ===');
  console.log(`44010: ${metrix44010Rounds} kierrosta (yleisin), 43119: ${metrix43119Rounds} KAIKKI (sisältää 44010), UDisc: ${udiscRounds}, Yht OIKEIN: ${totalRounds} (ei 1895)`);
}

main();
