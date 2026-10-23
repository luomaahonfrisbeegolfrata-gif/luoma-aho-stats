import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';

const METRIX_COURSES = [
  {id:43119, url:'https://discgolfmetrix.com/course/43119', file:'data/metrix_43119.json'},
  {id:44010, url:'https://discgolfmetrix.com/course/44010', file:'data/metrix_44010.json'},
  {id:44763, url:'https://discgolfmetrix.com/course/44763', file:'data/metrix_44763.json'},
  {id:48112, url:'https://discgolfmetrix.com/course/48112', file:'data/metrix_48112.json'}
];
const UDISC_LAYOUTS = [
  {id:143835, url:'https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835', file:'data/udisc.json'}
];

async function fetchMetrix(page,course){
  try{
    await page.goto(course.url,{waitUntil:'networkidle2',timeout:45000});
    const rounds = await page.evaluate(()=>{ 
      // parsii "619 kierrosta" / "Rounds" tekstistä, ei kovakoodia
      const txt=document.body.innerText;
      const m=txt.match(/(\d+)\s*(kierrosta|rounds)/i);
      return m?parseInt(m[1]):null;
    });
    // jos rounds löytyy, päivitä config.json layouts[metrix_{id}].rounds
    // jos ei löydy, ÄLÄ poista vanhaa -> säilytä
    // tallenna top10 + total_rounds
  }catch(e){
    // fail -> älä ylikirjoita vanhaa tiedostoa, logaa error
  }
}
