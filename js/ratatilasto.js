// js/ratatilasto.js - Korjaus #5: PNG -> Chart.js client-side
// Ei enää generoi data/ratatilasto.png gitiin, renderöi selaimessa

// Lataa Chart.js dynaamisesti jos ei ole jo
function ensureChartJs() {
  return new Promise((resolve) => {
    if (window.Chart) return resolve();
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
    s.onload = resolve;
    document.head.appendChild(s);
  });
}

async function renderRatatilasto(data) {
  await ensureChartJs();
  const container = document.getElementById('ratatilasto-data');
  const canvas = document.getElementById('ratatilasto-chart');
  if (!canvas) return;

  // data voi olla { average: [...], par: [...], labels: [...] } tai vastaava
  // Tehdään fiksu fallback jos rakenne erilainen
  let labels = data.labels || data.vaylat || Array.from({length: 20}, (_,i)=>`Väylä ${i+1}`);
  let values = data.average || data.keskiarvot || data.scores || [];
  
  // Jos data on objekti jossa avaimet on väylänumerot
  if (!values.length && typeof data === 'object' && !Array.isArray(data)) {
    // yritä kerätä numerot
    const entries = Object.entries(data).filter(([k])=>!k.startsWith('_')).sort((a,b)=>parseInt(a[0])-parseInt(b[0]));
    if (entries.length) {
      labels = entries.map(([k])=>`Väylä ${k}`);
      values = entries.map(([,v])=> typeof v === 'object' ? (v.average || v.avg || 0) : v);
    }
  }

  if (!values.length) {
    if (container) container.innerHTML = `<pre style="font-size:0.8em; white-space:pre-wrap;">${JSON.stringify(data, null, 2).slice(0,2000)}</pre>`;
    return;
  }

  const ctx = canvas.getContext('2d');
  if (window._rataChart) window._rataChart.destroy();

  window._rataChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.slice(0, 24),
      datasets: [{
        label: 'Keskiarvo',
        data: values.slice(0, 24),
        backgroundColor: 'rgba(34, 197, 94, 0.7)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title: { display: true, text: 'Ratatilasto - Väylien keskiarvot' }
      },
      scales: {
        y: { beginAtZero: false, title: { display: true, text: 'Heitot' } }
      }
    }
  });
}

async function renderVaylatilasto(data) {
  await ensureChartJs();
  const el = document.getElementById('vaylatilasto-data');
  if (!el) return;

  // Luo canvas jos ei ole
  let canvas = document.getElementById('vaylatilasto-chart');
  if (!canvas) {
    canvas = document.createElement('canvas');
    canvas.id = 'vaylatilasto-chart';
    el.innerHTML = '';
    el.appendChild(canvas);
  }

  // Yritä piirtää esim. birdie% / par%
  const labels = data.labels || Object.keys(data).filter(k=>!k.startsWith('_'));
  const birdieData = data.birdiePct || data.birdies || [];
  
  if (!labels.length) {
    el.innerHTML = `<pre style="font-size:0.8em;">${JSON.stringify(data, null,2).slice(0,2000)}</pre>`;
    return;
  }

  const ctx = canvas.getContext('2d');
  if (window._vaylaChart) window._vaylaChart.destroy();

  window._vaylaChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels.slice(0,24),
      datasets: [{
        label: 'Väylätilasto',
        data: (Array.isArray(data) ? data : Object.values(data).slice(0,24)).map(v=> typeof v==='object' ? (v.average||0) : v),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.3,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: { title: { display: true, text: 'Väylätilasto' } }
    }
  });
}

// Export global
window.renderRatatilasto = renderRatatilasto;
window.renderVaylatilasto = renderVaylatilasto;
