// V16.2 FIX - sää kortti fallback jos data/saa.json vanha
async function updateSaaKortti() {
  try {
    const res = await fetch('data/saa.json?v='+Date.now());
    const data = await res.json();
    const fetched = new Date(data.fetched_at);
    const now = new Date();
    const diffHours = (now - fetched) / 1000 / 3600;
    
    let temp = data.temp;
    
    // Jos data vanhempi kuin 1h, hae suoraan open-meteo client-puolella
    if (diffHours > 1) {
      console.log('Sää vanha '+diffHours.toFixed(1)+'h, haetaan suoraan open-meteo');
      const omRes = await fetch('https://api.open-meteo.com/v1/forecast?latitude=62.996&longitude=23.5&current=temperature_2m&timezone=Europe/Helsinki');
      const omData = await omRes.json();
      temp = omData.current.temperature_2m;
      document.querySelector('#saa-kortti .temp').textContent = temp + '°C (live)';
    } else {
      document.querySelector('#saa-kortti .temp').textContent = temp + '°C';
    }
    document.querySelector('#saa-kortti .updated').textContent = 'Päivitetty ' + data.fetched_at_fi;
  } catch(e) {
    console.error('Sää kortti error', e);
  }
}
// Kutsu joka 15min
updateSaaKortti();
setInterval(updateSaaKortti, 15*60*1000);
