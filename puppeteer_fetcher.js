import puppeteer from 'puppeteer';
import fs from 'fs';

const METRIX_COURSES = [43119, 44010, 44763]; // parent + 2 layout
const UDISC_COURSE = 'luoma-aho'; // tarkennetaan myöhemmin

async function fetchMetrix(page, courseId) {
  const url = `https://discgolfmetrix.com/course/${courseId}`;
  await page.goto(url, {waitUntil: 'networkidle2', timeout: 30000});
  await page.waitForTimeout(2000);
  // Hae result taulukko
  const data = await page.evaluate(() => {
    const rows = Array.from(document.querySelectorAll('table tr'));
    return rows.slice(0,20).map(r => r.innerText);
  });
  return {courseId, url, preview: data.slice(0,5)};
}

async function fetchUDisc(page) {
  // UDisc ei julkista APIa - haetaan public course stats jos saatavilla
  // Tämä vaatii manuaalisen config.json jossa round count
  // Puppeteer hakee UDisc Live leaderboardin
  try {
    const url = 'https://udisc.com/courses/luoma-aho-disc-golf-course';
    await page.goto(url, {waitUntil: 'networkidle2', timeout: 30000});
    await page.waitForTimeout(3000);
    const title = await page.title();
    return {title, url, status: 'ok'};
  } catch(e) {
    return {error: e.message};
  }
}

async function main() {
  console.log('Starting puppeteer...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox','--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
  
  const results = {};
  
  // Metrix
  for (const id of METRIX_COURSES) {
    console.log(`Fetching Metrix ${id}...`);
    try {
      results[`metrix_${id}`] = await fetchMetrix(page, id);
    } catch(e) {
      console.log(`Metrix ${id} fail: ${e.message}`);
      results[`metrix_${id}`] = {error: e.message};
    }
  }
  
  // UDisc
  console.log('Fetching UDisc...');
  results.udisc = await fetchUDisc(page);
  
  // Tallenna log
  fs.mkdirSync('data', {recursive:true});
  fs.writeFileSync('data/puppeteer_log.json', JSON.stringify(results, null, 2));
  
  // Päivitä kierrokset.json - laske total = 768 Metrix + UDisc config
  try {
    const config = JSON.parse(fs.readFileSync('data/config.json','utf8'));
    const udiscRounds = config.udiscRounds || 453;
    const metrixRounds = 768;
    const total = metrixRounds + udiscRounds;
    const kierrokset = {metrix: metrixRounds, udisc: udiscRounds, total, updated: new Date().toISOString()};
    fs.writeFileSync('data/kierrokset.json', JSON.stringify(kierrokset, null, 2));
    console.log(`Kierrokset päivitetty: ${total} (Metrix ${metrixRounds} + UDisc ${udiscRounds})`);
  } catch(e) {
    console.log('config.json puuttuu, luodaan default');
    fs.writeFileSync('data/kierrokset.json', JSON.stringify({metrix:768, udisc:453, total:1221, updated: new Date().toISOString()}, null, 2));
  }
  
  await browser.close();
  console.log('Done');
}

main().catch(e => { console.error(e); process.exit(1); });
