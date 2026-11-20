// Comprueba las descargas reales del módulo sin requerir un navegador.
import assert from 'node:assert/strict';
import { CurvePlot } from '../static/plot.js';

const blobs = [], filenames = [];
const originalURL = URL.createObjectURL;
URL.createObjectURL = (blob) => { blobs.push(blob); return 'blob:test'; };
globalThis.document = { createElement: () => ({ click() { filenames.push(this.download); } }) };
const plot = Object.create(CurvePlot.prototype);
const count = 20001;
plot.data = {
  variable: 'x', start: -10, end: 10, points: count,
  x: Array.from({ length: count }, (_, i) => -10 + i * .001),
  series: [0, 1].map((offset) => ({ expression: `x+${offset}`, y: Array.from({ length: count }, (_, i) => i + offset), corrections: Array(count).fill(0), errors: Array(count).fill(null), break_before: Array(count).fill(false) })),
  policy: { mode: 'strict', epsilon: 1e-9, max_value: 1e12 }, fixed_variables: {}, sampling: { mode: 'step', step: .001 },
  metrics: [{ expression: 'x+1', n: count, invalid: 0, mse: 1, rmse: 1, nmse: .01, r2: .99, note: null }],
};
plot.exportCSV();
plot.exportMetrics();
const dataCSV = await blobs[0].text(), metricCSV = await blobs[1].text();
assert.equal(dataCSV.split('\r\n').length, count + 1, 'La descarga debe conservar las 20,001 muestras');
assert.match(dataCSV, /residuo \(objetivo-candidata\)/);
assert.match(dataCSV.split('\r\n')[1], /"-1","1"/);
assert.match(metricCSV, /"MSE","RMSE","NMSE","R2"/);
assert.match(metricCSV, /"20001","0","1","1","0.01","0.99"/);
assert.deepEqual(filenames, ['arboria-resultados.csv', 'arboria-metricas.csv']);
URL.createObjectURL = originalURL;
console.log('CSV verificado: 20,001 filas completas, residuos y métricas.');
