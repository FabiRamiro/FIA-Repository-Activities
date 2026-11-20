"use strict";

const byId = (id) => document.getElementById(id);
const decimal = (value, digits = 2) => value.toFixed(digits).replace("-", "−");
const classLabel = (value) => value === 1 ? "+1" : "−1";
const predict = (score) => score >= 0 ? 1 : -1;
const forest = "#203d2a";
const green = "#386b47";
const blue = "#42618e";
const amber = "#98602e";

// Los ejes usan unidades de datos. Esta función traduce esas unidades a píxeles.
function drawPlot(canvas, { x, y, xTicks, yTicks, labels, lines = [], points = [] }) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (!width || !height) return;

  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.round(width * ratio);
  canvas.height = Math.round(height * ratio);
  const context = canvas.getContext("2d");
  context.scale(ratio, ratio);

  const margin = { left: 47, right: 15, top: 16, bottom: 43 };
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const horizontal = (value) => margin.left + (value - x[0]) / (x[1] - x[0]) * plotWidth;
  const vertical = (value) => margin.top + (y[1] - value) / (y[1] - y[0]) * plotHeight;

  function segment(startX, startY, endX, endY, color) {
    context.strokeStyle = color;
    context.beginPath();
    context.moveTo(startX, startY);
    context.lineTo(endX, endY);
    context.stroke();
  }

  context.font = "11px Segoe UI, sans-serif";
  context.fillStyle = "#515b49";
  context.textBaseline = "top";
  context.textAlign = "center";
  for (const tick of xTicks) {
    const px = horizontal(tick);
    segment(px, margin.top, px, margin.top + plotHeight, "#e1e5d8");
    context.fillText(tick, px, margin.top + plotHeight + 6);
  }
  context.textBaseline = "middle";
  context.textAlign = "right";
  for (const tick of yTicks) {
    const py = vertical(tick);
    segment(margin.left, py, width - margin.right, py, "#e1e5d8");
    context.fillText(tick, margin.left - 5, py);
  }
  context.strokeStyle = "#aab7a2";
  context.strokeRect(margin.left, margin.top, plotWidth, plotHeight);

  context.save();
  context.beginPath();
  context.rect(margin.left, margin.top, plotWidth, plotHeight);
  context.clip();
  for (const line of lines) {
    context.strokeStyle = line.color ?? forest;
    context.lineWidth = line.dashed ? 1.8 : 2.35;
    context.setLineDash(line.dashed ? [5, 4] : []);
    context.beginPath();
    line.data.forEach(([a, b], index) => {
      const method = index ? "lineTo" : "moveTo";
      context[method](horizontal(a), vertical(b));
    });
    context.stroke();
  }
  for (const { a, b, kind, radius } of points) {
    const px = horizontal(a);
    const py = vertical(b);
    context.fillStyle = kind === "positive" ? green : kind === "negative" ? blue : forest;
    context.beginPath();
    if (kind === "positive") {
      context.moveTo(px, py - radius);
      context.lineTo(px + radius, py);
      context.lineTo(px, py + radius);
      context.lineTo(px - radius, py);
      context.closePath();
    } else {
      context.arc(px, py, radius, 0, Math.PI * 2);
    }
    context.fill();
  }
  context.restore();

  context.textAlign = "center";
  context.textBaseline = "middle";
  context.fillText(labels[0], margin.left + plotWidth / 2, height - 12);
  context.save();
  context.translate(12, margin.top + plotHeight / 2);
  context.rotate(-Math.PI / 2);
  context.fillText(labels[1], 0, 0);
  context.restore();
}

const andExamples = [[-1, -1, -1], [-1, 1, -1], [1, -1, -1], [1, 1, 1]];

function renderAnd() {
  const bias = Number(byId("bias").value);
  const biasHundredths = Math.round(bias * 100);
  let correct = 0;
  const rows = andExamples.map(([a, b, label]) => {
    // Los pesos tienen dos decimales. Puntuar en centésimas resuelve exacto el empate en cero.
    const score = 5 * a + 105 * b + biasHundredths;
    const prediction = predict(score);
    if (prediction === label) correct++;
    const row = document.createElement("tr");
    for (const value of [`(${a}, ${b})`, decimal(score / 100), `${classLabel(prediction)} / ${classLabel(label)}`]) {
      row.insertCell().textContent = value;
    }
    return row;
  });
  byId("bias-value").textContent = decimal(bias);
  byId("and-rows").replaceChildren(...rows);
  byId("and-score").textContent = `${correct} de 4 casos correctos`;
  drawPlot(byId("and-plot"), {
    x: [-1.5, 1.5], y: [-1.4, 2.1], xTicks: [-1, 0, 1], yTicks: [-1, 0, 1, 2],
    labels: ["Entrada x₁", "Entrada x₂"],
    lines: [{ data: [-1.5, 1.5].map(a => [a, -(0.05 * a + bias) / 1.05]) }],
    points: andExamples.map(([a, b, label]) => ({ a, b, kind: label === 1 ? "positive" : "negative", radius: 7 })),
  });
}

const irisPoints = datosIris.map(([, , a, b, label]) => ({
  a, b, kind: label === 1 ? "positive" : "negative", radius: 3.25,
}));

function irisConstant(length, width) {
  return -1.3 * length + 4 * width - 0.74;
}

function irisPlot(id, constant) {
  drawPlot(byId(id), {
    x: [0, 7.2], y: [0, 2.8], xTicks: [0, 1, 2, 3, 4, 5, 6, 7], yTicks: [0, 0.5, 1, 1.5, 2, 2.5],
    labels: ["Largo del pétalo (cm)", "Ancho del pétalo (cm)"],
    lines: [{ data: [0, 7.2].map(a => [a, (constant - 0.93 * a) / 2.05]) }],
    points: irisPoints,
  });
}

const irisFullMatches = datosIris.filter(([length, width, a, b, label]) =>
  predict(irisConstant(length, width) - 0.93 * a - 2.05 * b) === label).length;

function renderIris() {
  const length = Number(byId("sepal-length").value);
  const width = Number(byId("sepal-width").value);
  const constant = irisConstant(length, width);
  const sliceMatches = datosIris.filter(([, , a, b, label]) =>
    predict(constant - 0.93 * a - 2.05 * b) === label).length;
  byId("sepal-length-value").textContent = `${decimal(length, 3)} cm`;
  byId("sepal-width-value").textContent = `${decimal(width, 3)} cm`;
  byId("iris-score").textContent = `Corte: ${sliceMatches} de ${datosIris.length} aciertos`;
  byId("iris-formula").textContent = `x₄ = (${decimal(constant, 4)} − 0.93x₃) / 2.05`;
  byId("iris-full").textContent = `Modelo con las cuatro medidas reales: ${irisFullMatches} de ${datosIris.length} aciertos en estas filas.`;
  irisPlot("iris-plot", constant);
}

function renderXor() {
  const first = Number(byId("xor-first").value);
  const second = Number(byId("xor-second").value);
  const or = first === 1 || second === 1;
  const nand = !(first === 1 && second === 1);
  byId("xor-or").textContent = classLabel(or ? 1 : -1);
  byId("xor-nand").textContent = classLabel(nand ? 1 : -1);
  byId("xor-out").textContent = classLabel(or && nand ? 1 : -1);
}

const sigmoid = (z) => 1 / (1 + Math.exp(-z));
const geluFactor = (z) => Math.sqrt(2 / Math.PI) * (z + 0.044715 * z ** 3);

const functions = {
  step: {
    value: predict, derivative: (z) => z === 0 ? null : 0, breakAtZero: true,
    note: "g(Z) pasa de −1 a +1 en cero. Ahí hay un salto. Fuera de cero la derivada es 0.",
  },
  linear: { value: (z) => z, derivative: () => 1, note: "g(Z) = Z. La pendiente vale 1 en todo el dominio." },
  sigmoid: {
    value: sigmoid, derivative: (z) => sigmoid(z) * (1 - sigmoid(z)),
    note: "g′(Z) = g(Z) · (1 − g(Z)). Su pendiente máxima es 0.25, cuando Z = 0.",
  },
  tanh: {
    value: Math.tanh, derivative: (z) => 1 - Math.tanh(z) ** 2,
    note: "g′(Z) = 1 − tanh²(Z). La pendiente tiende a cero hacia los extremos.",
  },
  relu: {
    value: (z) => Math.max(0, z), derivative: (z) => z === 0 ? null : Number(z > 0), breakDerivative: true,
    note: "La derivada es 0 para Z negativo y 1 para Z positivo. En cero hay un quiebre.",
  },
  leaky: {
    value: (z) => z < 0 ? 0.01 * z : z, derivative: (z) => z === 0 ? null : z < 0 ? 0.01 : 1, breakDerivative: true,
    note: "Esta curva usa α = 0.01. La pendiente negativa también vale 0.01 y la positiva vale 1.",
  },
  gelu: {
    value: (z) => 0.5 * z * (1 + Math.tanh(geluFactor(z))),
    derivative: (z) => {
      const t = Math.tanh(geluFactor(z));
      return 0.5 * (1 + t) + 0.5 * z * (1 - t ** 2) * Math.sqrt(2 / Math.PI) * (1 + 3 * 0.044715 * z ** 2);
    },
    note: "El gráfico usa la aproximación de GELU con tanh. Su transición cerca de cero es suave.",
  },
  silu: {
    value: (z) => z * sigmoid(z), derivative: (z) => sigmoid(z) + z * sigmoid(z) * (1 - sigmoid(z)),
    note: "g(Z) = Z · σ(Z). Al derivar el producto aparecen la sigmoide y su derivada.",
  },
};

function sampleCurve(fn, color, dashed, split) {
  const domains = split ? [[-6, -0.00001], [0.00001, 6]] : [[-6, 6]];
  return domains.map(([start, end]) => ({
    color, dashed, data: Array.from({ length: 121 }, (_, i) => {
      const z = start + (end - start) * i / 120;
      return [z, fn(z)];
    }),
  }));
}

function renderActivation() {
  const name = byId("activation").value;
  const fn = functions[name];
  const z = Number(byId("activation-z").value);
  const showGradient = byId("show-gradient").checked;
  const value = fn.value(z);
  const derivative = fn.derivative(z);
  const lines = sampleCurve(fn.value, forest, false, fn.breakAtZero);
  if (showGradient) {
    lines.push(...sampleCurve(fn.derivative, amber, true, fn.breakAtZero || fn.breakDerivative));
  }
  const isBounded = ["step", "sigmoid", "tanh"].includes(name);
  const axisY = isBounded ? [-1.25, 1.25] : name === "linear" ? [-6.3, 6.3] : [-1.2, 6.3];
  const ticksY = isBounded ? [-1, -0.5, 0, 0.5, 1] : name === "linear" ? [-6, -3, 0, 3, 6] : [-1, 0, 2, 4, 6];
  byId("activation-z-value").textContent = decimal(z, 1);
  byId("activation-value").textContent = `g(Z) = ${decimal(value, 4)}` +
    (showGradient ? ` · g′(Z) = ${derivative === null ? "indefinida" : decimal(derivative, 4)}` : "");
  byId("activation-help").textContent = fn.note;
  byId("derivative-key").hidden = !showGradient;
  drawPlot(byId("activation-plot"), {
    x: [-6.25, 6.25], y: axisY, xTicks: [-6, -3, 0, 3, 6], yTicks: ticksY,
    labels: ["Entrada Z", showGradient ? "g(Z) y g′(Z)" : "Activación g(Z)"],
    lines, points: [{ a: z, b: value, radius: 5 }],
  });
}

const logitKeys = ["a", "b", "c"];

function renderSoftmax() {
  const inputs = logitKeys.map(key => byId("logit-" + key));
  const logits = inputs.map(input => input.valueAsNumber);
  if (logits.some(value => !Number.isFinite(value) || value < -50 || value > 50)) {
    logitKeys.forEach(key => { byId("softmax-" + key).textContent = "—"; });
    byId("softmax-total").textContent = "Escribe tres valores entre −50 y 50.";
    return;
  }
  // Restar el máximo evita exponenciales enormes y conserva la proporción.
  const maximum = Math.max(...logits);
  const exp = logits.map(value => Math.exp(value - maximum));
  const total = exp.reduce((sum, value) => sum + value, 0);
  const probabilities = exp.map(value => value / total);
  logitKeys.forEach((key, i) => { byId("softmax-" + key).textContent = `${decimal(100 * probabilities[i], 1)} %`; });
  byId("softmax-total").textContent = "Suma antes del redondeo: 100 %.";
}

function setupProgress() {
  const checkboxes = [...document.querySelectorAll("[data-chapter]")];
  const key = "cuaderno-ia-progreso";
  let previous = [];
  try {
    const saved = JSON.parse(localStorage.getItem(key));
    if (Array.isArray(saved)) previous = saved;
  } catch {
    // Cuando el navegador bloquea el almacenamiento, el avance sigue disponible en esta sesión.
  }
  function update() {
    const completed = checkboxes.filter(input => input.checked).map(input => input.dataset.chapter);
    byId("progress").value = completed.length;
    byId("progress-text").textContent = `${completed.length} de ${checkboxes.length}`;
    try { localStorage.setItem(key, JSON.stringify(completed)); } catch { /* Almacenamiento opcional. */ }
  }
  for (const input of checkboxes) {
    input.checked = previous.includes(input.dataset.chapter);
    input.addEventListener("change", update);
  }
  update();
}

function watch(ids, event, render) {
  for (const id of ids) byId(id).addEventListener(event, render);
}

watch(["bias"], "input", renderAnd);
watch(["sepal-length", "sepal-width"], "input", renderIris);
watch(["xor-first", "xor-second"], "change", renderXor);
watch(["activation", "show-gradient"], "change", renderActivation);
watch(["activation-z"], "input", renderActivation);
watch(logitKeys.map(key => "logit-" + key), "input", renderSoftmax);
byId("and-reset").addEventListener("click", () => {
  byId("bias").value = "-1.09";
  renderAnd();
});
byId("iris-reset").addEventListener("click", () => {
  byId("sepal-length").value = "5.797";
  byId("sepal-width").value = "3.196";
  renderIris();
});

const plots = {
  "hero-plot": () => irisPlot("hero-plot", irisConstant(5.797, 3.196)),
  "and-plot": renderAnd,
  "iris-plot": renderIris,
  "activation-plot": renderActivation,
};
const resize = new ResizeObserver(entries => {
  for (const entry of entries) plots[entry.target.id]();
});
for (const [id, render] of Object.entries(plots)) {
  render();
  resize.observe(byId(id));
}

const navigation = [...document.querySelectorAll(".course-nav a")];
function markCurrentChapter() {
  const current = location.hash || "#fundamentos";
  for (const link of navigation) {
    if (link.hash === current) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  }
}
window.addEventListener("hashchange", markCurrentChapter);
markCurrentChapter();
renderXor();
renderSoftmax();
setupProgress();
