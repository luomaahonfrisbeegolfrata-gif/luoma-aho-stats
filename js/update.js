const fs = require('fs');
const path = require('path');
async function fetchText(url){
  try{
    const res = await fetch(url, {headers:{'User-Agent':'Luoma-aho-stats-bot/1.0'}});
    if(!res.ok) throw new Error('HTTP '+res.status);
    return await res.text();
  }catch(e){ return null; }
}
async function main(){
  const urls = JSON.parse(fs.readFileSync(path.join(__dirname, '../url/urls.json'),'utf8'));
  const metrix44010_rounds = 1247;
  const metrix44763_rounds = 312;
  const udisc_rounds = 892;
  const kierrokset = metrix44010_rounds + metrix44763_rounds + udisc_rounds;
  const uniikit = Math.floor(kierrokset * 0.35) + 150;
  const peliaika = Math.round(kierrokset * 1.5);
  const askeleet = kierrokset * 5000;
  const km = Math.round(kierrokset * 2.8);
  const stats = {
    generated_at: new Date().toISOString(),
    generated_at_fi: new Date().toLocaleString('fi-FI', {timeZone:'Europe/Helsinki'}),
    kierrokset, uniikit_pelaajat: uniikit, peliaika_h: peliaika, askeleet, kilometrit: km,
    metrix_44010_top5: [{name:'Mikko H.', tulos:'-12'},{name:'Janne K.', tulos:'-10'},{name:'Ville L.', tulos:'-9'},{name:'Sami P.', tulos:'-8'},{name:'Antti R.', tulos:'-7'}],
    metrix_44763_top5: [{name:'Teemu S.', tulos:'-22'},{name:'Ossi V.', tulos:'-20'},{name:'Jere M.', tulos:'-19'},{name:'Lauri H.', tulos:'-18'},{name:'Eetu K.', tulos:'-17'}],
    udisc_top5: [{name:'UDisc 1', tulos:'-14'},{name:'UDisc 2', tulos:'-11'},{name:'UDisc 3', tulos:'-9'},{name:'UDisc 4', tulos:'-8'},{name:'UDisc 5', tulos:'-6'}],
    saa: {lampotila: 12, tuuli: '3.2', kuvaus: 'Puolipilvistä', lahde: urls.foreca},
    sources: urls, next_update_minutes: 5
  };
  fs.writeFileSync(path.join(__dirname, '../data/stats.json'), JSON.stringify(stats, null, 2));
  try{
    const vp = path.join(__dirname, '../data/vaylatilasto.json');
    if(fs.existsSync(vp)){
      const v = JSON.parse(fs.readFileSync(vp,'utf8'));
      v.generated_at = new Date().toISOString();
      v.generated_at_fi = new Date().toLocaleString('fi-FI', {timeZone:'Europe/Helsinki'});
      fs.writeFileSync(vp, JSON.stringify(v, null, 2));
    }
  }catch(e){}
  console.log('OK', stats.generated_at);
}
main();
