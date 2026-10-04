// Luoma-aho Väylätilasto - Difficulty korjaus
// Säännöt:
// Difficulty 1 = suurin avg = punainen
// Difficulty 12 = pienin avg = vihreä
// 1-3 punainen, 4-6 oranssi, 7-9 keltainen, 10-12 vihreä
// Tämä tiedosto korvaa vain difficulty-logiikan, ei koske muuhun dataan

function getDifficultyColor(difficulty) {
  if (difficulty >=1 && difficulty <=3) return { name: 'red', hex: '#E74C3C', fi: 'punainen' };
  if (difficulty >=4 && difficulty <=6) return { name: 'orange', hex: '#F39C12', fi: 'oranssi' };
  if (difficulty >=7 && difficulty <=9) return { name: 'yellow', hex: '#F1C40F', fi: 'keltainen' };
  return { name: 'green', hex: '#2ECC71', fi: 'vihreä' };
}

function laskeDifficulty(avgTaulukko) {
  // avgTaulukko: [4.45, 3.77, ...] 12 kpl, index 0 = väylä 1
  const jarjestetty = avgTaulukko
    .map((avg, i) => ({ vayla: i+1, avg: Number(avg) }))
    .sort((a,b) => b.avg - a.avg); // suurin ensin

  const result = new Array(12);
  jarjestetty.forEach((item, idx) => {
    const difficulty = idx + 1; // 1 = vaikein
    result[item.vayla - 1] = {
      vayla: item.vayla,
      avg: item.avg,
      difficulty: difficulty,
      ...getDifficultyColor(difficulty)
    };
  });
  return result;
}

// Esimerkki käyttö dynaamisessa päivityksessä:
// const avgData = haeLiveData().map(v => v.avg); // 12 lukua
// const korjattu = laskeDifficulty(avgData);
// korjattu.forEach(r => {
//   document.querySelector(`#vayla-${r.vayla} .difficulty`).textContent = r.difficulty;
//   document.querySelector(`#vayla-${r.vayla} .difficulty`).style.backgroundColor = r.hex;
//   document.querySelector(`#vayla-${r.vayla} .avg`).style.backgroundColor = r.hex;
// });

// Export jos käytät moduleja
if (typeof module !== 'undefined') module.exports = { laskeDifficulty, getDifficultyColor };
