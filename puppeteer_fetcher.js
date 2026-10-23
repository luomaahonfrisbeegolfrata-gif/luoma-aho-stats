import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';

const METRIX_COURSES = [
  { id: 43119, url: 'https://discgolfmetrix.com/course/43119', file: 'data/metrix_43119.json', name: 'parent' },
  { id: 44010, url: 'https://discgolfmetrix.com/course/44010', file: 'data/metrix_44010.json', name: 'layout 12' },
  { id: 44763, url: 'https://discgolfmetrix.com/course/44763', file: 'data/metrix_44763.json', name: 'layout 24' },
  { id: 48112, url: 'https://discgolfmetrix.com/course/48112', file: 'data/metrix_48112.json', name: 'layout 18' }
];

const UDISC_LAYOUTS = [
  { id: 143835, url: 'https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835', file: 'data/udisc.json', fileLayout: 'data/udisc_143835.json', course: 'luoma-aho' }
];

async function fetchMetrix(page, course) { /* hakee TOP10 taulukosta, tallentaa data/metrix_{id}.json */ }
async function fetchUDisc(page, layout) { /* hakee UDisc layout 143835 leaderboardin, tallentaa data/udisc.json */ }

async function main() {
  // launch puppeteer, fetch kaikki 4 Metrix + UDisc 143835, tallenna log ja kierrokset 1221
}
