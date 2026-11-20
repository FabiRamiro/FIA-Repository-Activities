// Gráfica SVG sin dependencias: los valores siempre vienen del evaluador Python.
const SVG_NS = 'http://www.w3.org/2000/svg';
const COLORS = ['#df7d49', '#7c90b2', '#819873', '#a386b0'];
const number = (value) => value == null ? 'sin definir' : Math.abs(value) >= 1e5 || value !== 0 && Math.abs(value) < .0001 ? value.toExponential(3) : new Intl.NumberFormat('es-MX', { maximumSignificantDigits: 6 }).format(value);

function element(tag, attributes = {}, text = null) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
  if (text !== null) node.textContent = text;
  return node;
}

// Para dibujar se conservan extremos de cada bloque y bordes de discontinuidades.
// Las métricas, la inspección y las descargas conservan siempre todas las filas.
function displayIndices(series, width) {
  const stride = Math.max(1, Math.ceil(series.y.length / Math.max(1, width * 2)));
  const selected = new Set();
  for (let first = 0; first < series.y.length; first += stride) {
    const last = Math.min(series.y.length - 1, first + stride - 1);
    selected.add(first); selected.add(last);
    let minimum = null, maximum = null;
    for (let index = first; index <= last; index++) {
      const value = series.y[index];
      if (value !== null) {
        if (minimum === null || value < series.y[minimum]) minimum = index;
        if (maximum === null || value > series.y[maximum]) maximum = index;
      }
      if (series.break_before[index] || index > 0 && (value === null) !== (series.y[index - 1] === null)) {
        selected.add(index); if (index) selected.add(index - 1);
      }
    }
    if (minimum !== null) { selected.add(minimum); selected.add(maximum); }
  }
  return [...selected].sort((a, b) => a - b);
}

function downloadCSV(headers, rows, filename) {
  const quote = (value) => `"${String(value ?? '').replaceAll('"', '""')}"`;
  const blob = new Blob(['\ufeff' + [headers, ...rows].map((row) => row.map(quote).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a'); link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

export class CurvePlot {
  constructor(container) {
    this.container = container;
    this.svg = container.querySelector('svg');
    this.tooltip = container.querySelector('.curve-tooltip');
    this.scale = 'linear';
    this.index = 0;
    this.observer = new ResizeObserver(() => this.draw());
    this.observer.observe(container);
    this.svg.addEventListener('pointermove', (event) => {
      if (!this.data) return;
      const bounds = this.svg.getBoundingClientRect();
      const x = event.clientX - bounds.left;
      if (x < this.left || x > this.width - this.right) { this.hideTooltip(); return; }
      const ratio = Math.max(0, Math.min(1, (x - this.left) / this.plotWidth));
      const value = this.data.start * (1 - ratio) + this.data.end * ratio;
      // El último intervalo puede ser menor que el paso: buscamos la muestra
      // más cercana por su valor real, no por un índice de separación uniforme.
      let low = 0, high = this.data.x.length - 1;
      while (low < high) {
        const middle = Math.floor((low + high) / 2);
        if (this.data.x[middle] < value) low = middle + 1;
        else high = middle;
      }
      const index = low > 0 && Math.abs(this.data.x[low - 1] - value) < Math.abs(this.data.x[low] - value) ? low - 1 : low;
      this.inspect(index);
    });
    this.svg.addEventListener('pointerleave', () => this.hideTooltip());
    this.svg.addEventListener('blur', () => this.hideTooltip());
    this.svg.addEventListener('keydown', (event) => {
      if (!this.data || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const index = event.key === 'Home' ? 0 : event.key === 'End' ? this.data.x.length - 1 : this.index + (event.key === 'ArrowRight' ? 1 : -1);
      this.inspect(Math.max(0, Math.min(this.data.x.length - 1, index)));
    });
  }

  setData(data) {
    this.data = data;
    this.index = 0;
    document.querySelector('#curve-empty').hidden = true;
    this.draw();
    this.renderDetails();
  }

  setScale(scale) { this.scale = scale; this.draw(); }
  transform(value) { return this.scale === 'symlog' ? Math.sign(value) * Math.log10(1 + Math.abs(value)) : value; }
  inverse(value) { return this.scale === 'symlog' ? Math.sign(value) * (10 ** Math.abs(value) - 1) : value; }

  draw() {
    if (!this.data) return;
    this.hideTooltip();
    this.width = Math.max(this.container.clientWidth, 240);
    this.height = 330;
    this.left = this.width < 500 ? 60 : 78;
    this.right = 24;
    this.top = 28;
    this.bottom = 45;
    this.plotWidth = this.width - this.left - this.right;
    this.plotHeight = this.height - this.top - this.bottom;
    this.svg.setAttribute('viewBox', `0 0 ${this.width} ${this.height}`);
    this.svg.replaceChildren();
    let minimum = Infinity, maximum = -Infinity, validCount = 0;
    for (const series of this.data.series) for (const value of series.y) {
      if (value === null) continue;
      const transformed = this.transform(value);
      minimum = Math.min(minimum, transformed); maximum = Math.max(maximum, transformed); validCount++;
    }
    if (!validCount) { minimum = -1; maximum = 1; }
    const margin = maximum === minimum ? Math.max(Math.abs(maximum) * .1, 1) : (maximum - minimum) * .09;
    minimum -= margin; maximum += margin;
    this.yPosition = (value) => this.top + (maximum - this.transform(value)) / (maximum - minimum) * this.plotHeight;
    this.xPosition = (index) => this.left + (this.data.x[index] - this.data.start) / (this.data.end - this.data.start) * this.plotWidth;
    const defs = element('defs');
    const clip = element('clipPath', { id: 'curve-clip' });
    clip.append(element('rect', { x: this.left, y: this.top, width: this.plotWidth, height: this.plotHeight }));
    defs.append(clip); this.svg.append(defs);
    for (let tick = 0; tick <= 5; tick++) {
      const ratio = tick / 5;
      const x = this.left + ratio * this.plotWidth;
      const y = this.top + ratio * this.plotHeight;
      this.svg.append(element('line', { x1: this.left, y1: y, x2: this.width - this.right, y2: y, stroke: '#e8e9de', 'stroke-width': 1, 'stroke-dasharray': '3 5' }));
      this.svg.append(element('text', { x: this.left - 12, y: y + 3, 'text-anchor': 'end', class: 'curve-tick' }, number(this.inverse(maximum - ratio * (maximum - minimum)))));
      const domainValue = this.data.start * (1 - ratio) + this.data.end * ratio;
      this.svg.append(element('text', { x, y: this.height - 20, 'text-anchor': 'middle', class: 'curve-tick' }, number(domainValue)));
    }
    if (minimum <= 0 && maximum >= 0) this.svg.append(element('line', { x1: this.left, y1: this.yPosition(0), x2: this.width - this.right, y2: this.yPosition(0), stroke: '#b9c1ad', 'stroke-width': 1 }));
    this.svg.append(element('text', { x: this.left, y: 14, class: 'curve-axis-title' }, this.scale === 'symlog' ? 'f · escala log simétrica' : 'f'));
    this.svg.append(element('text', { x: this.width - this.right, y: this.height - 5, class: 'curve-axis-title', 'text-anchor': 'end' }, this.data.variable));
    const curves = element('g', { 'clip-path': 'url(#curve-clip)' });
    this.data.series.forEach((series, seriesIndex) => {
      let path = '', connected = false;
      displayIndices(series, this.plotWidth).forEach((index) => {
        const value = series.y[index];
        if (value === null) { connected = false; return; }
        const x = this.xPosition(index), y = this.yPosition(value);
        path += `${connected && !series.break_before[index] ? 'L' : 'M'}${x.toFixed(2)},${y.toFixed(2)} `;
        connected = true;
        if (series.corrections[index] && index % Math.max(1, Math.floor(series.y.length / 100)) === 0) curves.append(element('circle', { cx: x, cy: y, r: 2.6, fill: '#df7d49', stroke: '#fffefa', 'stroke-width': .8 }));
        // Una rama de una sola muestra también necesita una marca visible.
        if ((index === 0 || series.y[index - 1] === null || series.break_before[index]) && (index === series.y.length - 1 || series.y[index + 1] === null || series.break_before[index + 1])) curves.append(element('circle', { cx: x, cy: y, r: 3, fill: COLORS[seriesIndex], stroke: 'none' }));
      });
      curves.prepend(element('path', { d: path, stroke: COLORS[seriesIndex], fill: 'none', 'stroke-width': 2.2, 'vector-effect': 'non-scaling-stroke' }));
    });
    this.svg.append(curves);
    this.crosshair = element('line', { x1: 0, y1: this.top, x2: 0, y2: this.top + this.plotHeight, stroke: '#a1aa91', 'stroke-dasharray': '4 4', visibility: 'hidden' });
    this.svg.append(this.crosshair);
    if (!validCount) this.svg.append(element('text', { x: this.width / 2, y: this.height / 2, class: 'curve-empty-text', 'text-anchor': 'middle' }, 'No hay resultados reales en este dominio.'));
  }

  inspect(index) {
    this.index = index;
    const x = this.xPosition(index);
    this.crosshair.setAttribute('x1', x); this.crosshair.setAttribute('x2', x);
    this.crosshair.setAttribute('visibility', 'visible');
    this.tooltip.replaceChildren();
    const title = document.createElement('strong');
    title.textContent = `${this.data.variable} = ${number(this.data.x[index])}`;
    this.tooltip.append(title);
    this.data.series.forEach((series, seriesIndex) => {
      const row = document.createElement('div');
      row.style.color = COLORS[seriesIndex];
      row.textContent = `f${seriesIndex + 1} = ${number(series.y[index])}${series.corrections[index] ? ' · protegida' : ''}`;
      if (series.errors[index]) row.title = series.errors[index];
      this.tooltip.append(row);
    });
    this.tooltip.hidden = false;
    this.tooltip.style.left = `${Math.min(this.width - 210, Math.max(8, x + 15))}px`;
    this.tooltip.style.top = '32px';
    this.svg.setAttribute('aria-label', this.tooltip.textContent + '. Usa las flechas para cambiar de muestra.');
  }

  hideTooltip() {
    this.tooltip.hidden = true;
    this.crosshair?.setAttribute('visibility', 'hidden');
  }

  renderDetails() {
    const legend = document.querySelector('#curve-legend');
    legend.replaceChildren();
    this.data.series.forEach((series, index) => {
      const item = document.createElement('div');
      const dot = document.createElement('i'); dot.style.background = COLORS[index];
      const label = document.createElement('code'); label.textContent = `f${index + 1}${index === 0 ? ' · objetivo' : ' · candidata'} = ${series.expression}`;
      const stats = document.createElement('span'); stats.textContent = `mín ${number(series.stats.min)} · máx ${number(series.stats.max)}`;
      item.append(dot, label, stats); legend.append(item);
    });
    const table = document.createElement('table');
    const head = document.createElement('tr');
    for (const title of [this.data.variable, ...this.data.series.map((_, index) => `f${index + 1}`)]) {
      const cell = document.createElement('th'); cell.textContent = title; head.append(cell);
    }
    const thead = document.createElement('thead'); thead.append(head); table.append(thead);
    const body = document.createElement('tbody');
    this.data.x.slice(0, 20).forEach((x, index) => {
      const row = document.createElement('tr');
      const first = document.createElement('td'); first.textContent = number(x); row.append(first);
      this.data.series.forEach((series) => {
        const cell = document.createElement('td');
        cell.textContent = number(series.y[index]) + (series.corrections[index] ? ' *' : '');
        row.append(cell);
      });
      body.append(row);
    });
    table.append(body);
    document.querySelector('#plot-table').replaceChildren(table);
    const metrics = document.querySelector('#metrics-table');
    metrics.replaceChildren();
    if (!this.data.metrics?.length) {
      metrics.textContent = 'Agrega una candidata para medir qué tan lejos está del objetivo.';
      return;
    }
    const metricTable = document.createElement('table');
    const metricHead = document.createElement('thead'), titles = document.createElement('tr');
    for (const title of ['Candidata', 'MSE ↓', 'RMSE ↓', 'NMSE ↓', 'R² ↑', 'Muestras', 'Observaciones']) {
      const cell = document.createElement('th'); cell.textContent = title; titles.append(cell);
    }
    metricHead.append(titles); metricTable.append(metricHead);
    const metricBody = document.createElement('tbody');
    for (const metric of this.data.metrics) {
      const row = document.createElement('tr');
      for (const value of [`f${metric.series_index + 1}`, ...['mse', 'rmse', 'nmse', 'r2'].map((key) => number(metric[key])), metric.n, metric.note || 'Todos los pares evaluados']) {
        const cell = document.createElement('td'); cell.textContent = value; row.append(cell);
      }
      metricBody.append(row);
    }
    metricTable.append(metricBody); metrics.append(metricTable);
  }

  exportCSV() {
    if (!this.data) return;
    const headers = [this.data.variable];
    this.data.series.forEach((series, index) => headers.push(`f${index + 1}: ${series.expression}`, `f${index + 1}: nodos corregidos`, `f${index + 1}: error`, `f${index + 1}: corte anterior`));
    this.data.series.slice(1).forEach((_, index) => headers.push(`f${index + 2}: residuo (objetivo-candidata)`, `f${index + 2}: error cuadrado`));
    const rows = [headers];
    this.data.x.forEach((x, index) => {
      const row = [x];
      this.data.series.forEach((series) => row.push(series.y[index], series.corrections[index], series.errors[index], series.break_before[index]));
      this.data.series.slice(1).forEach((series) => {
        const target = this.data.series[0].y[index], prediction = series.y[index];
        const residual = target === null || prediction === null ? null : target - prediction;
        row.push(residual, residual === null ? null : residual ** 2);
      });
      rows.push(row);
    });
    // Metadatos en columnas: el CSV conserva las reglas usadas para producirlo.
    rows[0].push('modo', 'epsilon', 'limite_protegido', 'variables_fijas', 'muestreo', 'paso_solicitado');
    rows.slice(1).forEach((row) => row.push(this.data.policy.mode, this.data.policy.epsilon, this.data.policy.max_value, JSON.stringify(this.data.fixed_variables), this.data.sampling?.mode, this.data.sampling?.step));
    downloadCSV(rows[0], rows.slice(1), 'arboria-resultados.csv');
  }

  exportMetrics() {
    if (!this.data?.metrics?.length) return;
    const headers = ['objetivo', 'candidata', 'n', 'pares_invalidos', 'MSE', 'RMSE', 'NMSE', 'R2', 'nota', 'definicion_NMSE', 'modo', 'epsilon', 'limite_protegido', 'variables_fijas', 'desde', 'hasta', 'muestreo', 'paso_solicitado'];
    const rows = this.data.metrics.map((metric) => [this.data.series[0].expression, metric.expression, metric.n, metric.invalid, metric.mse, metric.rmse, metric.nmse, metric.r2, metric.note, 'MSE / varianza poblacional del objetivo', this.data.policy.mode, this.data.policy.epsilon, this.data.policy.max_value, JSON.stringify(this.data.fixed_variables), this.data.start, this.data.end, this.data.sampling?.mode, this.data.sampling?.step]);
    downloadCSV(headers, rows, 'arboria-metricas.csv');
  }
}
