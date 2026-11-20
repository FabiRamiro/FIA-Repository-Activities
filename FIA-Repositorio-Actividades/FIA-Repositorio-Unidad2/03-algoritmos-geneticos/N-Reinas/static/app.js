// Python produce generaciones; JavaScript conserva el historial y Three.js lo anima.
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);
const format = (number) => new Intl.NumberFormat('es-MX').format(number);
const state = { n: 8, mode: 'steps', data: null, traceIndex: 0, positions: [], conflicts: [],
  playing: false, timer: null, loading: false, animating: false, motion: Promise.resolve(),
  playEpoch: 0, visualEpoch: 0, controller: null };
let board = null, fallback = false, audio = null, toastTimer;

function toast(message) {
  clearTimeout(toastTimer);
  $('#toast').textContent = message; $('#toast').hidden = false;
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 5000);
}

function analyzePositions(positions) {
  // Contamos columnas y diagonales en O(N), sin comparar cada pareja de reinas.
  const columns = new Map(), down = new Map(), up = new Map();
  const increment = (map, key) => map.set(key, (map.get(key) || 0) + 1);
  positions.forEach((column, row) => {
    if (column < 0) return;
    increment(columns, column); increment(down, row - column); increment(up, row + column);
  });
  const conflicts = [];
  positions.forEach((column, row) => {
    if (column >= 0 && (columns.get(column) > 1 || down.get(row - column) > 1 || up.get(row + column) > 1)) conflicts.push(row);
  });
  let pairs = 0;
  for (const map of [columns, down, up]) for (const count of map.values()) pairs += count * (count - 1) / 2;
  return { conflicts, pairs };
}

function controls() {
  const hasHistory = Boolean(state.data?.trace.length);
  const interactive = hasHistory && !state.loading && state.mode !== 'challenge';
  $('#play').disabled = !interactive;
  $('#step').disabled = !interactive || state.animating || state.traceIndex >= state.data.trace.length - 1;
  $('#reset').disabled = state.loading || !state.data;
  $('#previous-solution').disabled = !interactive || state.animating || state.traceIndex === 0;
  $('#next-solution').disabled = !interactive || state.animating || state.traceIndex >= state.data.trace.length - 1;
  $('#jump-final').disabled = !interactive;
  $('#play').innerHTML = `<svg class="icon"><use href="#i-${state.playing ? 'pause' : 'play'}"/></svg>`;
  $('#play').setAttribute('aria-label', state.playing ? 'Pausar reproducción' : 'Reproducir generaciones');
}

function drawFallback() {
  if (!fallback) return;
  const target = $('#render-error'); target.hidden = false; target.replaceChildren();
  const message = document.createElement('div');
  message.textContent = `Vista 2D: WebGL no está disponible.${state.n > 16 ? ' Se muestra una ventana de 16 × 16; usa las coordenadas para colocar fuera de ella.' : ''}`;
  const grid = document.createElement('div'); grid.className = 'fallback-grid';
  const visible = Math.min(state.n, 16);
  grid.style.gridTemplateColumns = `repeat(${visible}, 1fr)`;
  for (let row = 0; row < visible; row++) for (let column = 0; column < visible; column++) {
    const square = document.createElement('button'), occupied = state.positions[row] === column;
    square.className = `${(row + column) % 2 ? '' : 'light'} ${occupied && state.conflicts.includes(row) ? 'conflict' : ''}`;
    square.textContent = occupied ? '♛' : '';
    square.setAttribute('aria-label', `Fila ${row + 1}, columna ${column + 1}${occupied ? ', reina' : ''}`);
    square.disabled = state.mode !== 'challenge' || state.loading;
    square.addEventListener('click', () => onSquareClick(row, column)); grid.append(square);
  }
  target.append(message, grid);
  if (state.mode === 'challenge') {
    const form = document.createElement('form'); form.className = 'genetic-fields';
    for (const name of ['Fila', 'Columna']) {
      const label = document.createElement('label'); label.textContent = name;
      const input = document.createElement('input'); input.type = 'number'; input.min = '1';
      input.max = String(state.n); input.step = '1'; input.value = '1'; input.required = true;
      input.name = name; label.append(input); form.append(label);
    }
    const submit = document.createElement('button'); submit.className = 'primary-button';
    submit.textContent = 'Colocar / retirar'; form.append(submit);
    form.addEventListener('submit', (event) => {
      event.preventDefault(); onSquareClick(Number(form.elements.Fila.value) - 1, Number(form.elements.Columna.value) - 1);
    }); target.append(form);
  }
}

function drawBoard() {
  const epoch = ++state.visualEpoch;
  board?.setAnimationSpeed(Number($('#speed').value));
  state.animating = Boolean(board);
  state.motion = board?.setQueens(state.positions, state.conflicts) || Promise.resolve();
  const occupied = state.positions.filter((column) => column >= 0).length;
  $('#stat-queens').innerHTML = `${occupied - state.conflicts.length} <em>/ ${state.n}</em>`;
  $('#board-dimension').innerHTML = `${String(state.n).padStart(2, '0')} <span>×</span> ${String(state.n).padStart(2, '0')}`;
  drawFallback(); controls();
  state.motion.then(() => { if (epoch === state.visualEpoch) { state.animating = false; controls(); } });
  return state.motion;
}

function stopPlayback() {
  state.playEpoch++; clearTimeout(state.timer); state.playing = false;
  board?.setPaused(true); controls();
}

const resultMessages = {
  solved: 'Solución encontrada: ninguna reina amenaza a otra.',
  impossible: 'Este N no tiene solución: es un caso matemático conocido.',
  time_limit: 'Tiempo agotado. Este es el mejor candidato; puedes volver a evolucionar.',
  generation_limit: 'Se alcanzó el máximo de generaciones. Aún hay conflictos; prueba otra semilla o más generaciones.',
  cancelled: 'Búsqueda detenida. Se conserva el mejor candidato recibido.',
};

function displayFrame(index) {
  const frame = state.data?.trace[index];
  if (!frame) return Promise.resolve();
  state.traceIndex = index; state.positions = [...frame.positions];
  state.conflicts = analyzePositions(state.positions).conflicts;
  const final = index === state.data.trace.length - 1 && Boolean(state.data.result);
  $('#solution-index').textContent = String(frame.generation).padStart(2, '0');
  $('#solution-total').textContent = `/ ${format(state.data.result?.generation ?? frame.generation)} generaciones`;
  $('#solution-label').textContent = frame.conflicts === 0 ? 'SOLUCIÓN ENCONTRADA' : final ? 'MEJOR CANDIDATO' : 'MEJOR INDIVIDUO';
  $('#solution-caption').textContent = final ? resultMessages[state.data.result.status]
    : `Generación ${frame.generation} · ${format(frame.conflicts)} pares en conflicto.${state.data.stride > 1 ? ` Historial resumido cada ${state.data.stride} generaciones.` : ''}`;
  $('#scene-status').textContent = frame.conflicts === 0 ? 'En perfecto equilibrio'
    : `Generación ${frame.generation} · ${format(frame.conflicts)} conflictos`;
  const before = state.data.trace[index - 1];
  const changed = before ? frame.positions.reduce((count, column, row) => count + (column !== before.positions[row] ? 1 : 0), 0) : state.n;
  $('#step-message').textContent = `Generación ${frame.generation}: ${changed} reinas cambian de posición · mutación ${(frame.mutation_rate * 100).toFixed(0)} %.`;
  $('#fitness-label').textContent = `APTITUD ${frame.fitness.toFixed(3)} / 1`;
  $('#stat-solutions').textContent = format(frame.conflicts);
  $('#stat-visited').textContent = format(frame.evaluations);
  $('#stat-time').innerHTML = `${frame.duration_ms.toLocaleString('es-MX', { maximumFractionDigits: 1 })} <em>ms</em>`;
  $('#timeline-fill').style.width = `${state.data.trace.length > 1 ? index / (state.data.trace.length - 1) * 100 : 100}%`;
  return drawBoard();
}

function initializeMode() {
  stopPlayback(); board?.setChallenge(state.mode === 'challenge');
  const challenge = state.mode === 'challenge';
  $('#playback-title').textContent = challenge ? 'Encuentra tu equilibrio' : state.mode === 'steps' ? 'Generación a generación' : 'Explora la evolución';
  $('#algorithm-tag').textContent = challenge ? 'TU TURNO' : 'GENÉTICO';
  $('#mode-description').textContent = { explore: 'Explora los mejores candidatos de esta búsqueda.',
    steps: 'Las reinas se elevan, se desplazan y aterrizan.', challenge: 'Coloca reinas con clics o con flechas y Enter.' }[state.mode];
  $('#solve-button span').textContent = challenge ? 'Preparar tablero' : 'Evolucionar reinas';
  $$('.mode-switch button').forEach((button) => {
    const active = button.dataset.mode === state.mode;
    button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active));
  });
  if (challenge) {
    state.positions = Array(state.n).fill(-1); state.conflicts = [];
    $('#solution-label').textContent = 'TU PROPIO CAMINO'; $('#solution-index').textContent = '00';
    $('#solution-total').textContent = `/ ${state.n} reinas`;
    $('#solution-caption').textContent = 'Una reina por fila. Haz clic de nuevo para retirarla.';
    $('#scene-status').textContent = 'El jardín espera tus decisiones';
    $('#step-message').textContent = 'Los conflictos se marcan en rosa.';
    $('#fitness-label').textContent = 'TU TURNO'; $('#stat-solutions').textContent = '0';
    $('#timeline-fill').style.width = '0%'; drawBoard();
  } else if (state.data?.trace.length) {
    displayFrame(state.mode === 'explore' ? state.data.trace.length - 1 : 0);
  } else {
    state.positions = []; state.conflicts = [];
    $('#scene-status').textContent = 'Evoluciona una población para comenzar';
    $('#solution-label').textContent = 'SIN BÚSQUEDA'; $('#solution-index').textContent = '00';
    $('#solution-total').textContent = '/ generaciones';
    $('#solution-caption').textContent = 'Elige N y pulsa Evolucionar reinas.'; drawBoard();
  }
  controls();
}

async function advance() {
  if (state.loading || state.mode === 'challenge' || !state.data) return false;
  if (state.traceIndex >= state.data.trace.length - 1) return false;
  await displayFrame(state.traceIndex + 1); return true;
}

async function startPlayback() {
  if (!state.data?.trace.length || state.mode === 'challenge' || state.loading) return;
  state.playing = true; const epoch = ++state.playEpoch;
  board?.setPaused(false); controls();
  if (state.traceIndex >= state.data.trace.length - 1) await displayFrame(0);
  else await state.motion;
  async function tick() {
    if (!state.playing || state.playEpoch !== epoch) return;
    if (!await advance()) { stopPlayback(); return; }
    if (state.playing && state.playEpoch === epoch) {
      if (state.traceIndex === state.data.trace.length - 1) stopPlayback();
      else state.timer = setTimeout(tick, Math.max(80, Number($('#speed').value) * .18));
    }
  }
  if (state.playing && state.playEpoch === epoch) tick();
}

function queryParameters() {
  const fields = ['board-size', 'population', 'generations', 'mutation', 'search-seconds', 'seed'];
  for (const id of fields) if (!$(`#${id}`).reportValidity()) return null;
  const n = Number($('#board-size').value);
  if (!Number.isSafeInteger(n) || n < 1) { toast('Escribe N como un entero positivo representable por el navegador.'); return null; }
  const query = new URLSearchParams({ n, population: $('#population').value,
    generations: $('#generations').value, mutation: Number($('#mutation').value) / 100,
    seconds: $('#search-seconds').value });
  if ($('#seed').value !== '') query.set('seed', $('#seed').value);
  return query;
}

function setBusy(busy) {
  state.loading = busy;
  for (const id of ['solve-button', 'board-size', 'population', 'generations', 'mutation', 'search-seconds', 'seed']) $(`#${id}`).disabled = busy;
  $$('.mode-switch button, .size-presets button').forEach((button) => { button.disabled = busy; });
  $('#cancel-search').hidden = !busy; controls();
}

async function loadEvolution() {
  if (state.loading) return;
  const query = queryParameters(); if (!query) return;
  stopPlayback(); setBusy(true); state.controller = new AbortController();
  const data = { n: Number(query.get('n')), trace: [], result: null, stride: 1 };
  const previousData = state.data;
  let latest = null;
  $('#scene-status').textContent = 'Python prepara una nueva población…';
  try {
    const response = await fetch(`/api/${state.mode === 'challenge' ? 'validate' : 'evolve'}?${query}`, { signal: state.controller.signal });
    if (!response.ok) { const error = await response.json(); throw new Error(error.error); }
    state.n = Number(query.get('n')); board?.setSize(state.n);
    if (state.mode === 'challenge') {
      if (state.data?.n !== state.n) state.data = data;
      setBusy(false); initializeMode(); return;
    }
    state.data = data;
    const reader = response.body.getReader(), decoder = new TextDecoder();
    let pending = '';
    const accept = (event) => {
      if (event.type === 'result') { data.result = event; return; }
      latest = event;
      if (event.generation % data.stride === 0) data.trace.push(event);
      // Conservamos todas las generaciones normales. El historial grande se
      // resume explícitamente para no agotar la memoria de la pestaña.
      if (data.trace.length > Math.max(2, Math.min(4000, Math.floor(1000000 / state.n)))) {
        data.trace = data.trace.filter((_, index) => index % 2 === 0); data.stride *= 2;
      }
      if (event.generation === 0) displayFrame(0);
      $('#scene-status').textContent = `Evolucionando · generación ${event.generation} · ${event.conflicts} conflictos`;
    };
    while (true) {
      const { value, done } = await reader.read();
      pending += decoder.decode(value, { stream: !done });
      const lines = pending.split('\n'); pending = lines.pop();
      for (const line of lines) if (line.trim()) accept(JSON.parse(line));
      if (done) break;
    }
    if (pending.trim()) accept(JSON.parse(pending));
    if (!data.result) throw new Error('La transmisión terminó sin un resultado completo.');
  } catch (error) {
    if (error.name === 'AbortError' && latest) data.result = { ...latest, status: 'cancelled', solved: latest.conflicts === 0 };
    else {
      state.data = previousData;
      if (previousData && state.n !== previousData.n) { state.n = previousData.n; board?.setSize(state.n); }
      toast(error.name === 'AbortError' ? 'Búsqueda cancelada.' : `No se pudo evolucionar: ${error.message}`);
    }
  } finally {
    if (latest && data.result && data.trace.at(-1)?.generation !== latest.generation) data.trace.push(latest);
    setBusy(false); state.controller = null;
    initializeMode();
    if (state.data === data && state.mode === 'steps' && data.result && data.result.status !== 'cancelled') startPlayback();
  }
}

function onSquareClick(row, column) {
  if (state.mode !== 'challenge' || state.loading) return;
  state.positions[row] = state.positions[row] === column ? -1 : column;
  const { conflicts, pairs } = analyzePositions(state.positions); state.conflicts = conflicts;
  const count = state.positions.filter((value) => value >= 0).length, solved = count === state.n && !pairs;
  $('#solution-index').textContent = String(count).padStart(2, '0');
  $('#solution-label').textContent = solved ? '¡LO HAS CONSEGUIDO!' : pairs ? 'HAY CONFLICTOS' : 'TU PROPIO CAMINO';
  $('#solution-caption').textContent = solved ? 'Encontraste tu propia solución.' : `${format(pairs)} pares en conflicto. Coloca una reina por fila.`;
  $('#scene-status').textContent = solved ? 'Tu jardín está en perfecto equilibrio' : `${count} de ${state.n} reinas · ${pairs} conflictos`;
  $('#stat-solutions').textContent = format(pairs);
  $('#timeline-fill').style.width = `${count / state.n * 100}%`;
  if (solved) toast('✿ Encontraste la armonía. ¡Desafío completado!'); drawBoard();
}

$('#board-size').addEventListener('input', () => {
  const n = Number($('#board-size').value);
  $('#size-value').textContent = Number.isSafeInteger(n) && n > 0 ? `${n} REINAS` : 'N REINAS';
  $('#size-preview').textContent = `${$('#board-size').value || 'N'} × ${$('#board-size').value || 'N'}`;
});
$$('[data-size]').forEach((button) => button.addEventListener('click', () => {
  $('#board-size').value = button.dataset.size; $('#board-size').dispatchEvent(new Event('input'));
}));
$('#solve-button').addEventListener('click', loadEvolution);
$('#board-size').addEventListener('keydown', (event) => { if (event.key === 'Enter') loadEvolution(); });
$('#cancel-search').addEventListener('click', () => state.controller?.abort());
$$('.mode-switch button').forEach((button) => button.addEventListener('click', () => { state.mode = button.dataset.mode; initializeMode(); }));
$('#play').addEventListener('click', () => { if (state.playing) stopPlayback(); else startPlayback(); });
$('#step').addEventListener('click', () => { stopPlayback(); advance(); });
$('#reset').addEventListener('click', initializeMode);
$('#previous-solution').addEventListener('click', () => { stopPlayback(); displayFrame(Math.max(0, state.traceIndex - 1)); });
$('#next-solution').addEventListener('click', () => { stopPlayback(); advance(); });
$('#jump-final').addEventListener('click', () => { stopPlayback(); displayFrame(state.data.trace.length - 1); });
$('#reset-camera').addEventListener('click', () => board?.resetCamera());
$('#fullscreen').addEventListener('click', () => {
  const expanded = $('.board-card').classList.toggle('expanded'); document.body.classList.toggle('board-expanded', expanded);
  $('#fullscreen').setAttribute('aria-label', expanded ? 'Reducir tablero' : 'Ampliar tablero');
});
document.addEventListener('keydown', (event) => { if (event.key === 'Escape') {
  $('.board-card').classList.remove('expanded'); document.body.classList.remove('board-expanded');
  $('#fullscreen').setAttribute('aria-label', 'Ampliar tablero');
} });
$$('[data-open]').forEach((button) => button.addEventListener('click', () => { stopPlayback(); $(`#${button.dataset.open}-dialog`).showModal(); }));
$$('.dialog-close').forEach((button) => button.addEventListener('click', () => button.closest('dialog').close()));
$$('dialog').forEach((dialog) => dialog.addEventListener('click', (event) => {
  const rect = dialog.getBoundingClientRect();
  if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close();
}));
$('#try-steps').addEventListener('click', async () => {
  $('#learn-dialog').close(); state.mode = 'steps'; $('#board-size').value = 16; $('#seed').value = 42;
  $('#board-size').dispatchEvent(new Event('input')); await loadEvolution();
});
$('#sound-toggle').addEventListener('click', async () => {
  try {
    if (!audio) {
      const Audio = window.AudioContext || window.webkitAudioContext; audio = new Audio();
      const gain = audio.createGain(); gain.gain.value = .014; gain.connect(audio.destination);
      [174.61, 261.63, 349.23, 440].forEach((frequency) => {
        const tone = audio.createOscillator(); tone.type = 'sine'; tone.frequency.value = frequency; tone.connect(gain); tone.start();
      }); await audio.suspend();
    }
    if (audio.state === 'running') await audio.suspend(); else await audio.resume();
    const enabled = audio.state === 'running'; $('#sound-toggle').setAttribute('aria-pressed', String(enabled));
    $('#sound-toggle').setAttribute('aria-label', enabled ? 'Desactivar ambiente sonoro' : 'Activar ambiente sonoro');
    $('#sound-toggle').innerHTML = `<svg class="icon"><use href="#i-${enabled ? 'music' : 'volume-off'}"/></svg>`;
  } catch { toast('Este navegador no permite iniciar audio en este momento.'); }
});

try { const { SakuraBoard } = await import('./scene.js'); board = new SakuraBoard($('#three-container'), onSquareClick); }
catch (error) { console.warn('No se pudo iniciar el tablero 3D:', error); fallback = true; }
await loadEvolution();
