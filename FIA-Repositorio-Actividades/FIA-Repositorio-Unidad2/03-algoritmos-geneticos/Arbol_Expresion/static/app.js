import { CurvePlot } from './plot.js';

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const expressionInput = $('#expression');
const state = { data: null, nodes: new Map(), values: Object.assign(Object.create(null), { x: 3, y: 4 }), selected: null, order: 'postorder', step: 0, playing: false, timer: null, request: 0, scene: null, generation: null, operationsLoaded: false };
const KIND_NAMES = { function: 'FUNCIÓN', operator: 'OPERADOR', variable: 'VARIABLE', number: 'NÚMERO', constant: 'CONSTANTE', unary: 'OPERADOR UNARIO' };
const SYMBOLS = { sqrt: '√', '*': '×', '/': '÷', neg: '−', pos: '+', pi: 'π', tau: 'τ' };
const symbolFor = (label) => SYMBOLS[label] || label;
const DETAILS = {
  sqrt: ['Raíz cuadrada', 'Devuelve el número que, multiplicado por sí mismo, produce el valor de su hijo.'],
  root: ['Raíz de índice n', 'El primer hijo es el radicando; el segundo es el índice de la raíz. Por ejemplo, root(27, 3) vale 3.'],
  '+': ['Suma', 'Combina los valores de sus dos hijos. Para conocer el resultado, primero evaluamos cada rama.'],
  '-': ['Resta', 'Resta el valor del hijo derecho al valor del hijo izquierdo. El orden de los hijos importa.'],
  '*': ['Multiplicación', 'Multiplica los resultados de sus dos ramas. La multiplicación implícita también crea este nodo.'],
  '/': ['División', 'Divide el resultado del hijo izquierdo entre el derecho. El divisor debe ser distinto de cero.'],
  '^': ['Potencia', 'Eleva la base (hijo izquierdo) al exponente (hijo derecho). Las potencias se agrupan desde la derecha.'],
  '%': ['Módulo', 'Calcula el residuo de la división. Usa la convención de Python: el residuo tiene el signo del divisor.'],
  neg: ['Negación', 'Cambia el signo del valor de su único hijo. Una potencia se resuelve antes que este signo.'],
  pos: ['Signo positivo', 'Conserva el valor de su único hijo. Es un operador unario porque recibe un solo argumento.'],
  '!': ['Factorial', 'Multiplica todos los enteros desde 1 hasta el argumento. Por ejemplo, 4! = 4 × 3 × 2 × 1 = 24.'],
  sin: ['Seno', 'Calcula el seno de su argumento. El ángulo se interpreta en radianes: sin(pi/2) = 1.'],
  cos: ['Coseno', 'Calcula el coseno de su argumento en radianes. Por ejemplo, cos(0) = 1.'],
  tan: ['Tangente', 'Calcula la tangente de un ángulo en radianes.'],
  ln: ['Logaritmo natural', 'Calcula el logaritmo en base e. El argumento debe ser positivo.'],
  log: ['Logaritmo', 'Con un argumento usa base e. Con dos argumentos, el segundo indica la base: log(8, 2) = 3.'],
  log10: ['Logaritmo decimal', 'Calcula el logaritmo en base 10 de un argumento positivo.'],
  abs: ['Valor absoluto', 'Devuelve la distancia del argumento al cero, siempre no negativa.'],
  exp: ['Exponencial', 'Eleva la constante e al valor de su único hijo.'],
  min: ['Mínimo', 'Devuelve el menor valor entre todos sus hijos.'],
  max: ['Máximo', 'Devuelve el mayor valor entre todos sus hijos.'],
  pow: ['Potencia', 'El primer argumento es la base; el segundo, el exponente.'],
  hypot: ['Hipotenusa', 'Calcula la raíz de la suma de los cuadrados de sus argumentos.'],
  floor: ['Redondeo inferior', 'Devuelve el mayor entero que no supera al argumento.'],
  ceil: ['Redondeo superior', 'Devuelve el menor entero que es mayor o igual que el argumento.'],
  round: ['Redondeo', 'Redondea al entero más cercano; los empates exactos se redondean al entero par.'],
  asin: ['Arcoseno', 'Devuelve el ángulo en radianes cuyo seno es el argumento, que debe estar entre -1 y 1.'],
  acos: ['Arcocoseno', 'Devuelve el ángulo en radianes cuyo coseno es el argumento, que debe estar entre -1 y 1.'],
  atan: ['Arcotangente', 'Devuelve el ángulo en radianes cuya tangente es el argumento.'],
  sinh: ['Seno hiperbólico', 'Calcula (e^x − e^(-x)) / 2 para el valor de su hijo.'],
  cosh: ['Coseno hiperbólico', 'Calcula (e^x + e^(-x)) / 2 para el valor de su hijo.'],
  tanh: ['Tangente hiperbólica', 'Calcula sinh(x) / cosh(x) para el valor de su hijo.'],
};
const EXAMPLES = [
  ['01 / EL CLÁSICO', 'sqrt(x^2 + y^2)', 'Pitágoras, desde sus raíces.', { x: 3, y: 4 }],
  ['02 / PRIORIDADES', '(3 + 5) * 2 - 4 / 2', 'Los paréntesis cambian el camino.', {}],
  ['03 / ONDAS', 'sin(pi/2) + cos(0)', 'Un encuentro entre funciones.', {}],
  ['04 / CRECIMIENTO', '2^3^2', 'Una potencia dentro de otra.', {}],
  ['05 / CONEXIONES', '2x(x + 1)', 'Multiplicaciones que se sobreentienden.', { x: 3 }],
  ['06 / MÁS ALLÁ', 'root(27, 3) + log(8, 2)', 'Raíces cúbicas y logaritmos.', {}],
];
const formatNumber = (value) => value === null || value === undefined ? '—' : new Intl.NumberFormat('es-MX', { maximumSignificantDigits: 10 }).format(value);
const curvePlot = new CurvePlot($('#curve-chart'));
$('.guide-limit').textContent = 'Trabajamos con valores reales y dos modos: estricto o protegido. El protegido usa reglas como sqrt(abs(x)) y divisores ±epsilon; puedes ver todas las reglas y los ajustes en la barra de evaluación. Hasta 512 caracteres, 160 nodos y 48 niveles. No se admiten ecuaciones, asignaciones, derivadas ni código Python.';
let plotRequest = 0;
const nodeWarning = document.createElement('p');
nodeWarning.className = 'node-warning';
nodeWarning.hidden = true;
$('#selected-description').after(nodeWarning);

function readPolicy() {
  if ($('#evaluation-mode').value === 'strict') return { mode: 'strict' };
  return { mode: $('#evaluation-mode').value, epsilon: $('#epsilon').valueAsNumber, max_value: $('#max-value').valueAsNumber };
}

function updateCorrections() {
  const corrections = state.data.corrections || [];
  $('#corrections-title').textContent = corrections.length ? `${corrections.length} nodo(s) con protección numérica · ver ajustes` : `Sin correcciones · modo ${state.data.policy.mode === 'protected' ? 'protegido' : 'estricto'}`;
  $('#correction-report').classList.toggle('has-corrections', corrections.length > 0);
  $('#correction-list').replaceChildren();
  if (!corrections.length) {
    const item = document.createElement('li'); item.textContent = state.data.evaluation.error ? 'La evaluación no tiene resultado. Las variables faltantes y las operaciones inválidas en modo estricto conservan sus errores.' : 'El cálculo actual no necesitó protección.'; $('#correction-list').append(item);
  }
  corrections.forEach((correction) => {
    const item = document.createElement('li');
    item.textContent = `${correction.node_id} · ${correction.label}: ${correction.messages.join(' ')}`;
    $('#correction-list').append(item);
  });
}

function schedulePlot() {
  clearTimeout(schedulePlot.timer);
  plotRequest++;
  schedulePlot.timer = setTimeout(generatePlot, 150);
}

function readDomain() {
  const domain = { start: $('#domain-start').valueAsNumber, end: $('#domain-end').valueAsNumber };
  if (!Number.isFinite(domain.start) || !Number.isFinite(domain.end)) throw new Error('Completa los extremos del dominio con números válidos.');
  if (domain.start >= domain.end) throw new Error('El inicio del dominio debe ser menor que el final.');
  if ($('#sampling-mode').value === 'step') {
    domain.step = $('#plot-step').valueAsNumber;
    if (!Number.isFinite(domain.step) || domain.step <= 0) throw new Error('El tamaño de paso debe ser un número positivo.');
  } else {
    domain.points = $('#plot-points').valueAsNumber;
    if (!Number.isInteger(domain.points) || domain.points < 2 || domain.points > 100001) throw new Error('Elige entre 2 y 100001 muestras.');
  }
  return domain;
}

function applyCurve(data) {
  curvePlot.setData(data);
  $('#plot-error').hidden = true;
  $('#export-csv').disabled = false;
  const invalid = data.series.reduce((sum, series) => sum + series.stats.invalid, 0);
  const corrected = data.series.reduce((sum, series) => sum + series.stats.corrected, 0);
  const sampling = data.sampling?.mode === 'step' ? ` · paso ${formatNumber(data.sampling.step)}${data.sampling.short_final_interval ? ' (último intervalo más corto para incluir el final)' : ''}` : '';
  $('#plot-status').textContent = `${data.points} muestras por curva · ${data.series.length} curva(s) · ${invalid} resultado(s) sin definir · ${corrected} resultado(s) protegido(s)${sampling}`;
  const fixed = Object.entries(data.fixed_variables).map(([name, value]) => `${name} = ${formatNumber(value)}`);
  $('#plot-context').textContent = `Dominio de ${data.variable}: [${formatNumber(data.start)}, ${formatNumber(data.end)}] · Modo ${data.policy.mode === 'protected' ? 'protegido' : 'estricto'}${fixed.length ? ` · Variables fijas: ${fixed.join(', ')}` : ''}. ${data.reference?.source === 'csv' ? 'Objetivo y valores de x del CSV; las fórmulas son candidatas.' : 'Objetivo: última expresión generada; las fórmulas adicionales son candidatas.'}`;
  $('#export-metrics').disabled = !data.metrics?.length;
}

async function generatePlot() {
  if (!state.data) return;
  const requestId = ++plotRequest;
  $('#plot-error').hidden = true;
  $('#plot-generate').disabled = true;
  $('#plot-status').textContent = 'Evaluando el dominio en Python…';
  try {
    const extras = $('#plot-comparisons').value.split('\n').map((line) => line.trim()).filter(Boolean);
    const fromCSV = $('#reference-source').value === 'csv';
    const payload = { expressions: [state.data.expression, ...extras], variable: $('#plot-variable').value.trim(), ...(fromCSV ? {} : readDomain()), variables: { ...state.values }, policy: state.data.policy };
    let response;
    if (fromCSV) {
      const file = $('#reference-file').files[0];
      if (!file) throw new Error('Selecciona un CSV objetivo.');
      if (file.size > 16 * 1024 * 1024) throw new Error('El CSV supera los 16 MB.');
      payload.x_column = $('#csv-x').value.trim(); payload.y_column = $('#csv-y').value.trim();
      const form = new FormData(); form.append('file', file); form.append('options', JSON.stringify(payload));
      response = await fetch('/api/compare-csv', { method: 'POST', body: form });
    } else {
      response = await fetch('/api/sample', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    }
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo muestrear la expresión.');
    if (requestId !== plotRequest) return;
    applyCurve(data);
  } catch (error) {
    if (requestId !== plotRequest) return;
    $('#plot-error').textContent = error instanceof TypeError ? 'No se pudo conectar con Python para graficar.' : error.message;
    $('#plot-error').hidden = false;
    $('#plot-status').textContent = 'No se actualizó la gráfica. Si existe una anterior, conserva sus datos originales.';
  } finally {
    if (requestId === plotRequest) $('#plot-generate').disabled = false;
  }
}

function toast(message) {
  $('#toast').textContent = message;
  $('#toast').hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { $('#toast').hidden = true; }, 3600);
}

function setConnection(connected) {
  $('.connection').classList.toggle('offline', !connected);
  $('#connection-label').textContent = connected ? 'Python conectado' : 'Sin conexión con Python';
}

function indexNodes(tree) {
  state.nodes.clear();
  const visit = (node) => {
    state.nodes.set(node.id, node);
    node.children.forEach(visit);
  };
  visit(tree);
}

async function requestTree(expression, variables) {
  const response = await fetch('/api/parse', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ expression, variables, policy: readPolicy() }) });
  const data = await response.json();
  setConnection(true);
  if (!response.ok) {
    const error = new Error(data.error || 'No se pudo interpretar la expresión.');
    error.position = data.position;
    throw error;
  }
  if (!data.policy) throw new Error('La API responde con una versión anterior. Reinicia el servidor Python de Arboria y recarga la página.');
  return data;
}

function applyReport(data, generation = null) {
  state.data = data;
  state.generation = generation;
  if (!data.simplification) $('#simplify-status').textContent = 'Ejemplo: (2 + 3) * x → 5 * x. Conserva errores y protecciones.';
  state.step = 0;
  indexNodes(data.tree);
  buildVariableInputs(data.variables);
  updateResult();
  updateStats();
  updateCorrections();
  $('#plot-variables').replaceChildren();
  data.variables.forEach((name) => { const option = document.createElement('option'); option.value = name; $('#plot-variables').append(option); });
  if (data.variables.length && !data.variables.includes($('#plot-variable').value)) $('#plot-variable').value = data.variables[0];
  state.scene?.build(data.tree);
  selectNode(data.tree.id);
  renderTraversal();
  $('#syntax-state').replaceChildren();
  const dot = document.createElement('span'); dot.className = 'status-dot';
  $('#syntax-state').append(dot, document.createTextNode('Sintaxis válida'));
  $('#graph-subtitle').textContent = `${data.stats.nodes} nodos · ${data.stats.depth} niveles${generation ? ` / máximo ${generation.max_height}` : ''} · infinitas conexiones`;
  $('#generated-result').hidden = !generation;
  if (generation) {
    $('#generated-formula').textContent = generation.formula;
    $('#generated-stats').textContent = `Altura ${data.stats.depth} ≤ ${generation.max_height} · ${data.stats.nodes} nodos`;
    $('#generated-status').textContent = `Aridades verificadas · ${generation.operations.length} operación(es) permitida(s) · ${generation.seed === null ? 'semilla aleatoria' : `semilla ${generation.seed}`}. La fórmula puede contener solo algunas de las operaciones seleccionadas.`;
  }
  if (data.curve && $('#reference-source').value !== 'csv') {
    clearTimeout(schedulePlot.timer);
    plotRequest++;
    $('#plot-generate').disabled = false;
    applyCurve(data.curve);
  } else schedulePlot();
}

function setGenerating(value) {
  $('#generate').disabled = value;
  $('#simplify-tree').disabled = value;
  $('#generate-random').disabled = value || !state.operationsLoaded;
  $$('#variable-inputs input').forEach((input) => { input.disabled = value; });
}

async function loadOperationLibrary() {
  try {
    const response = await fetch('/api/operations');
    if (!response.ok) throw new Error('No se pudo cargar la biblioteca. Reinicia el servidor Python y recarga la página.');
    const data = await response.json();
    const legend = document.createElement('legend'); legend.className = 'sr-only'; legend.textContent = 'Operaciones permitidas en el generador';
    $('#operation-library').replaceChildren(legend);
    for (const operation of data.operations) {
      const label = document.createElement('label'); label.className = 'operation-option';
      const input = document.createElement('input'); input.type = 'checkbox'; input.value = operation.id; input.checked = true;
      input.setAttribute('aria-label', `${operation.name}, aridad ${operation.arity}`);
      input.addEventListener('change', markGeneratorPending);
      const symbol = document.createElement('span'); symbol.className = 'operation-symbol'; symbol.textContent = operation.symbol;
      const name = document.createElement('span'); name.className = 'operation-name'; name.textContent = operation.name;
      const arity = document.createElement('span'); arity.className = 'operation-arity'; arity.textContent = operation.arity; arity.title = `${operation.arity} hijo(s)`;
      label.append(input, symbol, name, arity); $('#operation-library').append(label);
    }
    state.operationsLoaded = true;
    $('#generate-random').disabled = $('#generate').disabled;
  } catch (error) {
    $('#generator-error').textContent = error.message;
    $('#generator-error').hidden = false;
  }
}

function markGeneratorPending() {
  if (state.generation) $('#generated-status').textContent = 'Configuración modificada. La fórmula mostrada conserva los parámetros de su generación anterior; pulsa «Generar fórmula libre» para aplicar los nuevos.';
}

async function generateRandom() {
  clearTimeout(updateVariables.timer);
  clearTimeout(schedulePlot.timer);
  plotRequest++;
  const requestId = ++state.request;
  setGenerating(true);
  pause();
  $('#generator-error').hidden = true;
  try {
    const height = $('#generator-height').valueAsNumber;
    if (!Number.isInteger(height) || height < 1 || height > 12) throw new Error('La altura máxima debe ser un entero entre 1 y 12 niveles.');
    const seed = $('#generator-seed').value.trim() ? $('#generator-seed').valueAsNumber : null;
    if (seed !== null && !Number.isSafeInteger(seed)) throw new Error('La semilla debe ser un entero válido o estar vacía.');
    const operations = $$('#operation-library input:checked').map((input) => input.value);
    if (!operations.length) throw new Error('Activa al menos una operación de la biblioteca.');
    const response = await fetch('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ operations, max_height: height, variable: $('#generator-variable').value.trim(), seed, constants: $('#generator-constants').checked, variables: { ...state.values }, policy: readPolicy(), domain: readDomain() }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo generar la fórmula.');
    if (requestId !== state.request) return;
    expressionInput.value = data.expression;
    $('#character-count').textContent = `${data.expression.length} / 512`;
    state.values[data.generation.variable] = data.generation.initial_value;
    $('#plot-variable').value = data.generation.variable;
    $('#plot-comparisons').value = '';
    $('#parse-error').hidden = true;
    applyReport(data, data.generation);
    setConnection(true);
  } catch (error) {
    if (requestId !== state.request) return;
    $('#generator-error').textContent = error instanceof TypeError ? 'No se pudo conectar con el generador Python.' : error.message;
    $('#generator-error').hidden = false;
    $('#plot-generate').disabled = false;
  } finally {
    if (requestId === state.request) setGenerating(false);
  }
}

async function generate() {
  clearTimeout(updateVariables.timer);
  const requestId = ++state.request;
  const expression = expressionInput.value.trim();
  setGenerating(true);
  $('#parse-error').hidden = true;
  pause();
  try {
    let data = await requestTree(expression, state.values);
    // Una variable recién encontrada recibe un valor inicial antes de evaluar.
    let needsValues = false;
    for (const name of data.variables) {
      if (!Object.hasOwn(state.values, name)) { state.values[name] = 1; needsValues = true; }
    }
    if (needsValues) data = await requestTree(expression, state.values);
    if (requestId !== state.request) return;
    applyReport(data, state.generation && state.data?.expression === data.expression ? state.generation : null);
  } catch (error) {
    if (requestId !== state.request) return;
    const networkError = error instanceof TypeError;
    if (networkError) setConnection(false);
    $('#parse-error').textContent = networkError ? 'No hay conexión con Python. Ejecuta python app.py y recarga la página.' : `${error.message}${Number.isInteger(error.position) ? ` Posición ${error.position + 1}.` : ''}`;
    $('#parse-error').hidden = false;
    $('#syntax-state').textContent = 'Revisa la expresión';
    if (Number.isInteger(error.position)) {
      expressionInput.focus();
      expressionInput.setSelectionRange(error.position, error.position + 1);
    }
    if (state.data) $('#graph-subtitle').textContent = 'Se muestra el último árbol válido';
  } finally {
    if (requestId === state.request) {
      setGenerating(false);
    }
  }
}

async function simplifyTree() {
  clearTimeout(updateVariables.timer);
  const requestId = ++state.request;
  setGenerating(true); pause();
  $('#simplify-tree').disabled = true;
  try {
    const response = await fetch('/api/simplify', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ expression: expressionInput.value.trim(), variables: { ...state.values }, policy: readPolicy() }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'No se pudo simplificar.');
    if (requestId !== state.request) return;
    expressionInput.value = data.expression;
    $('#character-count').textContent = `${data.expression.length} / 512`;
    $('#parse-error').hidden = true;
    applyReport(data);
    $('#simplify-status').textContent = `${data.simplification.before} → ${data.simplification.after} nodos. ${data.simplification.before === data.simplification.after ? 'No hay subárboles constantes que se puedan reducir sin alterar errores o protecciones.' : 'Constantes calculadas una sola vez; se conserva la evaluación numérica.'}`;
  } catch (error) {
    if (requestId !== state.request) return;
    $('#parse-error').textContent = error.message; $('#parse-error').hidden = false;
  } finally {
    if (requestId === state.request) setGenerating(false);
    $('#simplify-tree').disabled = false;
  }
}

function buildVariableInputs(names) {
  $('#variable-inputs').replaceChildren();
  if (!names.length) {
    const empty = document.createElement('span');
    empty.className = 'variables-empty';
    empty.textContent = 'Esta expresión solo tiene constantes.';
    $('#variable-inputs').append(empty);
  }
  names.forEach((name, index) => {
    const field = document.createElement('div');
    field.className = 'variable-field';
    const label = document.createElement('label');
    label.textContent = name;
    label.htmlFor = `variable-${index}`;
    const input = document.createElement('input');
    input.type = 'number';
    input.step = 'any';
    input.id = `variable-${index}`;
    input.dataset.variable = name;
    input.value = String(state.values[name]);
    input.addEventListener('input', () => {
      if (input.value.trim() && Number.isFinite(input.valueAsNumber)) {
        state.values[name] = input.valueAsNumber;
        input.setAttribute('aria-invalid', 'false');
        updateVariables();
      } else {
        input.setAttribute('aria-invalid', 'true');
        $('#variable-hint').textContent = 'Introduce un número válido para actualizar el resultado.';
      }
    });
    field.append(label, input);
    $('#variable-inputs').append(field);
  });
  $('#variable-hint').textContent = names.length ? 'Cambia un valor y observa el resultado.' : 'No necesitas asignar ningún valor.';
}

function updateVariables() {
  clearTimeout(updateVariables.timer);
  pause();
  const requestId = ++state.request;
  updateVariables.timer = setTimeout(async () => {
    if (!state.data) return;
    try {
      const data = await requestTree(state.data.expression, state.values);
      if (requestId !== state.request) return;
      state.data = data;
      indexNodes(data.tree);
      state.scene?.updateData(data.tree);
      updateResult();
      updateCorrections();
      schedulePlot();
      selectNode(state.selected);
      $('#variable-hint').textContent = 'Cambia un valor y observa el resultado.';
    } catch (error) {
      if (requestId !== state.request) return;
      if (error instanceof TypeError) setConnection(false);
      $('#variable-hint').textContent = error.message;
    }
  }, 220);
}

function updateResult() {
  const { value, error } = state.data.evaluation;
  $('#result-value').textContent = formatNumber(value);
  const resultText = $('#result-value').textContent;
  const resultWidth = $('#result-value').clientWidth;
  $('#result-value').style.fontSize = `${Math.max(14, Math.min(33, resultWidth / Math.max(1, resultText.length) / .62))}px`;
  $('#result-detail').textContent = error || (state.data.variables.length ? state.data.variables.map((name) => `${name} = ${formatNumber(state.values[name])}`).join('   ·   ') : 'Evaluado en los números reales');
  $('.result-card').classList.toggle('has-error', Boolean(error));
  $('#result-value').classList.remove('updated');
  void $('#result-value').offsetWidth;
  $('#result-value').classList.add('updated');
}

function updateStats() {
  for (const key of ['nodes', 'depth', 'leaves', 'operations']) $(`#stat-${key}`).textContent = state.data.stats[key];
}

function selectNode(id) {
  const node = state.nodes.get(id);
  if (!node) return;
  state.selected = id;
  state.scene?.select(id);
  const defaultDetails = node.kind === 'function' ? [`Función ${node.label}`, 'Recibe los valores de sus hijos como argumentos y aplica la función registrada en Python.'] : node.kind === 'variable' ? [`Variable ${node.label}`, 'Una hoja cuyo valor puedes cambiar en el panel de variables. No tiene hijos: es un dato de entrada.'] : node.kind === 'constant' ? ['Constante matemática', 'Un valor matemático fijo. Las constantes son hojas del árbol y no necesitan variables de entrada.'] : ['Valor numérico', 'Un número escrito directamente en la expresión. Es una hoja del árbol: no necesita ninguna operación para obtener su valor.'];
  const [title, description] = DETAILS[node.label] || defaultDetails;
  $('#selected-symbol').textContent = symbolFor(node.label);
  $('#selected-symbol').style.fontSize = node.label.length > 3 ? '17px' : '';
  $('#selected-title').textContent = title;
  $('#selected-description').textContent = description;
  $('#selected-kind').textContent = KIND_NAMES[node.kind];
  $('#selected-id').textContent = node.id;
  $('#selected-children').textContent = node.children.length;
  $('#selected-value').textContent = formatNumber(node.value);
  $('#selected-value').title = node.error || String(node.value);
  if (node.error) $('#selected-description').textContent = `${description} ${node.error}`;
  nodeWarning.textContent = (node.warnings || []).join(' ');
  nodeWarning.hidden = !node.warnings?.length;
}

const ORDER_EXPLANATIONS = {
  preorder: 'Raíz → izquierda → derecha. Conocemos cada operación antes de visitar sus argumentos.',
  inorder: 'Izquierda → raíz → derecha. Las funciones conservan su nombre antes de sus argumentos.',
  postorder: 'Izquierda → derecha → raíz. Primero resolvemos los hijos; después, su padre.',
};

function renderTraversal() {
  $('#traversal-track').replaceChildren();
  if (!state.data) return;
  state.data.traversals[state.order].forEach((id, index) => {
    if (index) {
      const arrow = document.createElement('span');
      arrow.className = 'track-arrow';
      arrow.textContent = '→';
      arrow.setAttribute('aria-hidden', 'true');
      $('#traversal-track').append(arrow);
    }
    const node = state.nodes.get(id);
    const button = document.createElement('button');
    button.className = `track-node kind-${node.kind}`;
    button.textContent = symbolFor(node.label);
    button.title = `${index + 1}. ${node.label}`;
    button.dataset.nodeId = id;
    button.setAttribute('aria-label', `Paso ${index + 1}: ${node.label}. Inspeccionar nodo.`);
    button.addEventListener('click', () => selectNode(id));
    $('#traversal-track').append(button);
  });
  $('#traversal-explanation').textContent = ORDER_EXPLANATIONS[state.order];
  updateTraversalHighlight();
}

function updateTraversalHighlight() {
  if (!state.data) return;
  const sequence = state.data.traversals[state.order];
  const visited = sequence.slice(0, state.step);
  const current = visited.at(-1);
  state.scene?.highlight(visited, current);
  $$('.track-node').forEach((node, index) => {
    node.classList.toggle('visited', index < state.step);
    node.classList.toggle('current', index === state.step - 1);
  });
  $('#traversal-progress').textContent = `${state.step} / ${sequence.length} nodos`;
  const currentButton = $('.track-node.current');
  if (currentButton) {
    const track = $('#traversal-track');
    if (currentButton.offsetLeft > track.scrollLeft + track.clientWidth - 45 || currentButton.offsetLeft < track.scrollLeft) track.scrollTo({ left: currentButton.offsetLeft - track.offsetLeft - 20, behavior: 'smooth' });
  }
}

function step() {
  if (!state.data) return;
  const sequence = state.data.traversals[state.order];
  if (state.step >= sequence.length) state.step = 0;
  state.step++;
  selectNode(sequence[state.step - 1]);
  updateTraversalHighlight();
  if (state.step === sequence.length) pause();
}

function pause() {
  clearTimeout(state.timer);
  state.playing = false;
  $('#play-traversal span').textContent = 'Animar recorrido';
  $('#play-traversal use').setAttribute('href', '#i-play');
}

function scheduleStep() {
  if (!state.playing) return;
  step();
  if (state.playing) state.timer = setTimeout(scheduleStep, Number($('#speed').value));
}

function togglePlay() {
  if (!state.data) return;
  if (state.playing) { pause(); return; }
  state.playing = true;
  $('#play-traversal span').textContent = 'Pausar';
  $('#play-traversal use').setAttribute('href', '#i-pause');
  scheduleStep();
}

function insert(text) {
  const start = expressionInput.selectionStart;
  const end = expressionInput.selectionEnd;
  const selected = expressionInput.value.slice(start, end);
  const replacement = text.includes('()') ? text.replace('()', `(${selected})`) : text;
  if (expressionInput.value.length - (end - start) + replacement.length > 512) { toast('La expresión admite hasta 512 caracteres.'); return; }
  expressionInput.setRangeText(replacement, start, end, 'end');
  expressionInput.focus();
  if (text.includes('()') && !selected) expressionInput.setSelectionRange(start + replacement.length - 1, start + replacement.length - 1);
  expressionInput.dispatchEvent(new Event('input'));
}

function openGuide() { $('#guide-dialog').showModal(); }
$('#generate-random').addEventListener('click', generateRandom);
for (const selector of ['#generator-height', '#generator-variable', '#generator-seed', '#generator-constants']) $(selector).addEventListener('input', markGeneratorPending);
for (const [selector, checked] of [['#operations-all', true], ['#operations-none', false]]) $(selector).addEventListener('click', () => {
  $$('#operation-library input').forEach((input) => { input.checked = checked; });
  markGeneratorPending();
});
$('#sampling-mode').addEventListener('change', () => {
  const byStep = $('#sampling-mode').value === 'step';
  $('#plot-step-field').hidden = !byStep;
  $('#plot-points-field').hidden = byStep;
  $('#plot-step').disabled = !byStep;
  $('#plot-points').disabled = byStep;
  markPlotPending();
});
$('#plot-generate').addEventListener('click', () => { clearTimeout(schedulePlot.timer); generatePlot(); });
$('#export-csv').addEventListener('click', () => curvePlot.exportCSV());
$('#export-metrics').addEventListener('click', () => curvePlot.exportMetrics());
$('#simplify-tree').addEventListener('click', simplifyTree);
$('#load-study').addEventListener('click', () => {
  expressionInput.value = '6.87 + 11 * cos(7.23 * x^3)';
  expressionInput.dispatchEvent(new Event('input'));
  $('#domain-start').value = '-10'; $('#domain-end').value = '10'; $('#plot-step').value = '0.001';
  $('#sampling-mode').value = 'step'; $('#sampling-mode').dispatchEvent(new Event('change'));
  $('#reference-source').value = 'expression'; $('#reference-source').dispatchEvent(new Event('change'));
  $('#plot-comparisons').value = '6.87 + 10 * cos(7.23 * x^3)';
  generate();
});
$('#reference-source').addEventListener('change', () => {
  const fromCSV = $('#reference-source').value === 'csv';
  $('#csv-fields').hidden = !fromCSV;
  for (const selector of ['#domain-start', '#domain-end', '#sampling-mode', '#plot-step', '#plot-points']) $(selector).disabled = fromCSV || (selector === '#plot-points' ? $('#sampling-mode').value === 'step' : selector === '#plot-step' && $('#sampling-mode').value !== 'step');
  markPlotPending();
});
$('#plot-scale').addEventListener('change', () => curvePlot.setScale($('#plot-scale').value));
for (const selector of ['#evaluation-mode', '#epsilon', '#max-value']) $(selector).addEventListener('change', () => {
  const strict = $('#evaluation-mode').value === 'strict';
  $('#epsilon').disabled = strict; $('#max-value').disabled = strict;
  generate();
});
function markPlotPending() {
  clearTimeout(schedulePlot.timer);
  plotRequest++;
  $('#plot-generate').disabled = false;
  $('#plot-status').textContent = 'Cambios pendientes: pulsa «Graficar resultados» para aplicarlos.';
}
for (const selector of ['#domain-start', '#domain-end', '#plot-variable', '#plot-points', '#plot-step', '#plot-comparisons', '#csv-x', '#csv-y', '#reference-file']) $(selector).addEventListener('input', markPlotPending);
$('#generate').addEventListener('click', generate);
expressionInput.addEventListener('input', () => {
  $('#character-count').textContent = `${expressionInput.value.length} / 512`;
  $('#syntax-state').textContent = 'Cambios sin generar';
  if (state.data && expressionInput.value.trim() !== state.data.expression) $('#graph-subtitle').textContent = 'Cambios pendientes · genera el árbol para aplicarlos';
});
expressionInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) { event.preventDefault(); generate(); }
});
$$('[data-insert]').forEach((button) => button.addEventListener('click', () => insert(button.dataset.insert)));
$('#examples-open').addEventListener('click', () => $('#examples-dialog').showModal());
$('#guide-nav').addEventListener('click', openGuide);
$('#all-functions').addEventListener('click', openGuide);
$('#lab-nav').addEventListener('click', () => $('.workspace').scrollIntoView({ behavior: 'smooth', block: 'start' }));
$$('[data-close]').forEach((button) => button.addEventListener('click', () => $(`#${button.dataset.close}`).close()));
$$('dialog').forEach((dialog) => dialog.addEventListener('click', (event) => { if (event.target === dialog && (event.offsetX < 0 || event.offsetX > dialog.clientWidth || event.offsetY < 0 || event.offsetY > dialog.clientHeight)) dialog.close(); }));
for (const [title, expression, description, values] of EXAMPLES) {
  const button = document.createElement('button');
  button.className = 'example-card';
  const titleElement = document.createElement('span'); titleElement.textContent = title;
  const formulaElement = document.createElement('strong'); formulaElement.textContent = expression;
  const descriptionElement = document.createElement('small'); descriptionElement.textContent = description;
  button.append(titleElement, formulaElement, descriptionElement);
  button.addEventListener('click', () => {
    state.values = Object.assign(Object.create(null), values);
    expressionInput.value = expression;
    expressionInput.dispatchEvent(new Event('input'));
    $('#examples-dialog').close();
    generate();
  });
  $('#example-grid').append(button);
}
$$('[data-order]').forEach((button) => button.addEventListener('click', () => {
  pause();
  state.order = button.dataset.order;
  state.step = 0;
  $$('[data-order]').forEach((item) => { item.classList.toggle('selected', item === button); item.setAttribute('aria-pressed', String(item === button)); });
  renderTraversal();
}));
$('#play-traversal').addEventListener('click', togglePlay);
$('#step-traversal').addEventListener('click', () => { pause(); step(); });
$('#reset-traversal').addEventListener('click', () => { pause(); state.step = 0; updateTraversalHighlight(); if (state.data) selectNode(state.data.tree.id); });
$('#speed').addEventListener('change', () => { if (state.playing) { clearTimeout(state.timer); state.timer = setTimeout(scheduleStep, Number($('#speed').value)); } });
$('#zoom-in').addEventListener('click', () => state.scene?.zoom(1.2));
$('#zoom-out').addEventListener('click', () => state.scene?.zoom(1 / 1.2));
$('#fit-view').addEventListener('click', () => state.scene?.fit());
$('#export-image').addEventListener('click', async () => {
  if (!state.scene || !state.data) { toast('Primero genera un árbol y activa WebGL.'); return; }
  try { await state.scene.exportPNG(state.data.expression); toast('Tu árbol se descargó como PNG.'); }
  catch (error) { toast(error.message); }
});
for (const mode of ['2d', '3d']) $(`#view-${mode}`).addEventListener('click', () => {
  if (!state.scene) { toast('La vista gráfica necesita WebGL habilitado.'); return; }
  pause(); state.step = 0;
  state.scene.setView(mode === '3d');
  updateTraversalHighlight();
  for (const view of ['2d', '3d']) { $(`#view-${view}`).classList.toggle('selected', mode === view); $(`#view-${view}`).setAttribute('aria-pressed', String(mode === view)); }
  $('#graph-help').textContent = mode === '3d' ? 'ARRASTRA PARA GIRAR · CLIC DERECHO PARA MOVER' : 'ARRASTRA PARA MOVER · SCROLL PARA ZOOM';
});

async function initialize() {
  setGenerating(true);
  const libraryPromise = loadOperationLibrary();
  $('#character-count').textContent = `${expressionInput.value.length} / 512`;
  try {
    const { TreeScene } = await import('./scene.js');
    state.scene = new TreeScene($('#graph'), selectNode);
    $('#graph-loading').hidden = true;
  } catch (error) {
    $('#graph-loading').textContent = 'No se pudo iniciar Three.js. Comprueba que ejecutaste npm install y npm run vendor, y que tu navegador admite WebGL 2. La evaluación y los recorridos siguen disponibles.';
    console.error('Three.js:', error);
  }
  await libraryPromise;
  if (state.operationsLoaded) await generateRandom();
  else await generate();
  try {
    const response = await fetch('/api/functions');
    const data = await response.json();
    for (const item of data.functions) {
      const code = document.createElement('code');
      code.textContent = item.name;
      $('#function-reference').append(code);
    }
  } catch { $('#function-reference').textContent = 'Inicia el servidor Python para consultar las funciones.'; }
}
initialize();
