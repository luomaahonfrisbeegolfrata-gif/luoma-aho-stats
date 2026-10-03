// js/loader.js - Korjattu versio #3
// Lisätty: cache-buster, virheenkäsittely, loading states, auto-refresh

const DATA_BASE = 'data/';
const CACHE_BUSTER = () => `?v=${Date.now()}`; // estää selaimen välimuistin
const FETCH_OPTS = { cache: 'no-store' };

const FILES = {
  foreca: 'foreca.json',
  stats: 'stats.json',
  top5: 'top5.json',
  ratatilasto: 'ratatilasto.json',
  vaylatilasto: 'vaylatilasto.json',
  tilasto: 'tilasto.json',
  holeinone: 'holeinone.json',
  holeScores: 'hole-scores.csv'
};

async function fetchJSON(name) {
  const file = FILES[name];
  if (!file) throw new Error(`Unknown file: ${name}`);
  try {
    const res = await fetch(DATA_BASE + file + CACHE_BUSTER(), FETCH_OPTS);
    if (!res.ok) throw new Error(`${file}: ${res.status}`);
    if (file.endsWith('.json')) return await res.json();
    return await res.text(); // csv
  } catch (e) {
    console.warn(`[loader] ${name} failed:`, e);
    return null; // ei kaada koko sivua
  }
}

async function loadAll() {
  const statusEl = document.getElementById('loading-status');
  if (statusEl) statusEl.textContent = 'Päivitetään tilastoja...';

  // Lataa rinnakkain, kaatuminen ei kaada muita
  const results = await Promise.allSettled(
    Object.keys(FILES).map(k => fetchJSON(k).then(data => ({ key: k, data })))
  );

  const data = {};
  results.forEach(r => {
    if (r.status === 'fulfilled' && r.value?.data) {
      data[r.value.key] = r.value.data;
    }
  });

  if (statusEl) {
    const now = new Date().toLocaleString('fi-FI', { timeZone: 'Europe/Helsinki' });
    statusEl.textContent = `Päivitetty: ${now} | Lähde: UDisc + Metrix AUTO`;
    statusEl.dataset.lastUpdate = now;
  }

  // Renderöi - kutsuu olemassa olevia render-funktioita jos ne on määritelty
  try {
    if (typeof renderForeca === 'function' && data.foreca) renderForeca(data.foreca);
    if (typeof renderStats === 'function' && data.stats) renderStats(data.stats);
    if (typeof renderTop5 === 'function' && data.top5) renderTop5(data.top5);
    if (typeof window.renderRatatilasto === 'function' && data.ratatilasto) window.renderRatatilasto(data.ratatilasto);
    if (typeof window.renderVaylatilasto === 'function' && data.vaylatilasto) window.renderVaylatilasto(data.vaylatilasto);
  } catch (e) {
    console.error('Render error', e);
  }

  return data;
}

// Auto-refresh 5min välein (sama kuin foreca workflow)
let autoRefreshTimer = null;
function startAutoRefresh() {
  if (autoRefreshTimer) clearInterval(autoRefreshTimer);
  autoRefreshTimer = setInterval(() => {
    loadAll();
  }, 5 * 60 * 1000);
}

// Käynnistä kun DOM valmis
document.addEventListener('DOMContentLoaded', () => {
  loadAll().then(() => startAutoRefresh());
});

// Export jos tarvitaan muualla
window.luomaAhoLoader = { loadAll, fetchJSON };
