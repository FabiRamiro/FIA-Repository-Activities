import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const PALETTE = {
  function: { fill: '#e58a52', rim: '#e5a16e' },
  operator: { fill: '#eff1e7', rim: '#b9c4a5' },
  unary: { fill: '#eff1e7', rim: '#b9c4a5' },
  variable: { fill: '#ded5ec', rim: '#b7a7cb' },
  constant: { fill: '#e8e9dc', rim: '#c7ccb5' },
  number: { fill: '#f4f3e7', rim: '#cccfb8' },
};
export const symbolFor = (label) => ({ sqrt: '√', '*': '×', '/': '÷', neg: '−', pos: '+', pi: 'π', tau: 'τ', '^': '^' })[label] || label;

export class TreeScene {
  constructor(container, onSelect) {
    this.container = container;
    this.labels = container.querySelector('#node-labels');
    this.onSelect = onSelect;
    this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.scene = new THREE.Scene();
    this.camera = new THREE.OrthographicCamera(-7, 7, 4, -4, .1, 100);
    this.camera.position.set(0, 0, 20);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0xfdfcf8, 0);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1;
    this.renderer.domElement.setAttribute('aria-label', 'Árbol interactivo en Three.js. Los nodos también son botones accesibles con el teclado.');
    container.prepend(this.renderer.domElement);
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = .09;
    this.controls.minZoom = .18;
    this.controls.maxZoom = 20;
    this.controls.screenSpacePanning = true;
    this.controls.zoomSpeed = .7;
    this.setView(false);
    this.scene.add(new THREE.AmbientLight(0xffffff, 1.5));
    const sun = new THREE.DirectionalLight(0xfff8e9, 2.2);
    sun.position.set(-5, 8, 14);
    this.scene.add(sun);
    const fill = new THREE.DirectionalLight(0xe5e8fa, .7);
    fill.position.set(6, -4, 7);
    this.scene.add(fill);
    this.rootGroup = new THREE.Group();
    this.scene.add(this.rootGroup);
    this.nodes = new Map();
    this.edges = [];
    this.selected = null;
    this.visited = new Set();
    this.active = null;
    this.started = performance.now();
    this.viewHeight = 8;
    this.observer = new ResizeObserver(() => this.resize());
    this.observer.observe(container);
    this.renderer.domElement.addEventListener('webglcontextlost', (event) => {
      event.preventDefault();
      const message = document.querySelector('#graph-loading');
      message.textContent = 'Se perdió el contexto gráfico. Recarga la página para recuperar la vista 3D.';
      message.hidden = false;
    });
    this.animate = this.animate.bind(this);
    this.frame = requestAnimationFrame(this.animate);
  }

  clear() {
    this.rootGroup.traverse((object) => {
      object.geometry?.dispose();
      if (object.material) object.material.dispose();
    });
    this.rootGroup.clear();
    this.labels.replaceChildren();
    this.nodes.clear();
    this.edges = [];
  }

  build(tree) {
    this.clear();
    this.tree = tree;
    this.visited.clear();
    this.active = null;
    const ordered = [];
    let leafIndex = 0;
    let deepest = 0;
    const positionNode = (node, depth) => {
      deepest = Math.max(deepest, depth);
      const entry = { data: node, depth, index: ordered.length };
      ordered.push(entry);
      const children = node.children.map((child) => positionNode(child, depth + 1));
      entry.x = children.length ? (children[0].x + children.at(-1).x) / 2 : leafIndex++ * 1.8;
      entry.y = -depth * 1.55;
      return entry;
    };
    positionNode(tree, 0);
    this.spanX = Math.max((leafIndex - 1) * 1.8, 1);
    this.spanY = deepest * 1.55;
    for (const entry of ordered) {
      entry.x -= this.spanX / 2;
      entry.y += this.spanY / 2;
      this.createNode(entry);
    }
    for (const entry of ordered) {
      for (const child of entry.data.children) this.createEdge(this.nodes.get(entry.data.id), this.nodes.get(child.id));
    }
    this.started = performance.now();
    this.fit();
  }

  createNode(entry) {
    const node = entry.data;
    const palette = PALETTE[node.kind];
    const group = new THREE.Group();
    group.position.set(entry.x, entry.y, this.is3D ? -entry.depth * .5 : 0);
    const material = new THREE.MeshStandardMaterial({ color: palette.fill, roughness: .48, metalness: .04 });
    const body = new THREE.Mesh(new THREE.CylinderGeometry(.375, .375, .15, 56), material);
    body.rotation.x = Math.PI / 2;
    group.add(body);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(.391, .009, 8, 64), new THREE.MeshBasicMaterial({ color: palette.rim, transparent: true, opacity: .85 }));
    rim.position.z = .09;
    group.add(rim);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(.49, .012, 8, 64), new THREE.MeshBasicMaterial({ color: '#dc975f', transparent: true, opacity: 0 }));
    ring.position.z = .06;
    group.add(ring);
    const halo = new THREE.Mesh(new THREE.CircleGeometry(.66, 48), new THREE.MeshBasicMaterial({ color: '#edc091', transparent: true, opacity: 0, depthWrite: false }));
    halo.position.z = -.1;
    group.add(halo);
    this.rootGroup.add(group);
    const label = document.createElement('button');
    label.type = 'button';
    label.className = 'node-label';
    label.dataset.kind = node.kind;
    label.dataset.nodeId = node.id;
    label.setAttribute('aria-label', `${node.label}, ${node.kind === 'function' ? 'función' : node.kind === 'operator' ? 'operador' : node.kind === 'variable' ? 'variable' : 'valor'}. Inspeccionar nodo.`);
    const symbol = document.createElement('span');
    symbol.className = 'node-symbol';
    symbol.textContent = symbolFor(node.label);
    label.append(symbol);
    const caption = document.createElement('span');
    caption.className = 'node-caption';
    caption.textContent = entry.depth === 0 ? 'RAÍZ DEL ÁRBOL' : node.kind === 'variable' ? 'VARIABLE' : node.kind === 'function' ? node.label : '';
    label.append(caption);
    label.addEventListener('click', () => this.onSelect(node.id));
    this.labels.append(label);
    this.nodes.set(node.id, { ...entry, group, body, ring, halo, label, symbol, baseColor: new THREE.Color(palette.fill), warmColor: new THREE.Color('#f4c99e') });
  }

  createEdge(parent, child) {
    const start = parent.group.position.clone().add(new THREE.Vector3(0, -.38, -.03));
    const end = child.group.position.clone().add(new THREE.Vector3(0, .39, -.03));
    const middleY = (start.y + end.y) / 2;
    const curve = new THREE.CubicBezierCurve3(start, new THREE.Vector3(start.x, middleY, start.z), new THREE.Vector3(end.x, middleY, end.z), end);
    const line = new THREE.Mesh(new THREE.TubeGeometry(curve, 40, .009, 5, false), new THREE.MeshBasicMaterial({ color: '#bec5af', transparent: true, opacity: .65 }));
    const dot = new THREE.Mesh(new THREE.SphereGeometry(.026, 8, 8), new THREE.MeshBasicMaterial({ color: '#dc9c65', transparent: true, opacity: .7 }));
    this.rootGroup.add(line, dot);
    this.edges.push({ curve, line, dot, parent: parent.data.id, child: child.data.id, delay: child.index * .13 });
  }

  updateData(tree) {
    const update = (node) => {
      const entry = this.nodes.get(node.id);
      if (entry) entry.data = node;
      node.children.forEach(update);
    };
    this.tree = tree;
    update(tree);
  }

  select(id) {
    this.selected = id;
    for (const [key, node] of this.nodes) {
      node.label.classList.toggle('is-selected', key === id);
      node.label.setAttribute('aria-pressed', String(key === id));
    }
  }

  highlight(visited = [], active = null) {
    this.visited = new Set(visited);
    this.active = active;
    for (const [id, node] of this.nodes) node.label.classList.toggle('is-visited', this.visited.has(id));
  }

  setView(is3D) {
    this.is3D = is3D;
    this.controls.enableRotate = is3D;
    this.controls.mouseButtons.LEFT = is3D ? THREE.MOUSE.ROTATE : THREE.MOUSE.PAN;
    this.controls.touches.ONE = is3D ? THREE.TOUCH.ROTATE : THREE.TOUCH.PAN;
    if (this.tree) {
      // Volvemos a crear las curvas para que sus extremos coincidan con el relieve.
      const selected = this.selected;
      this.build(this.tree);
      this.select(selected);
    }
  }

  fit() {
    const aspect = this.container.clientWidth / Math.max(this.container.clientHeight, 1);
    this.viewHeight = Math.max((this.spanY || 1) + 2.3, ((this.spanX || 1) + 2.4) / aspect, 5.8);
    this.controls.target.set(0, 0, 0);
    this.camera.position.set(this.is3D ? 7 : 0, this.is3D ? 3 : 0, 20);
    this.camera.zoom = 1;
    this.camera.lookAt(0, 0, 0);
    this.resize();
    this.controls.update();
    this.controls.saveState();
  }

  zoom(factor) {
    this.camera.zoom = THREE.MathUtils.clamp(this.camera.zoom * factor, .18, 20);
    this.camera.updateProjectionMatrix();
  }

  resize() {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    if (!width || !height) return;
    const aspect = width / height;
    // Recalculamos ambos límites al cambiar de pantalla: un árbol ancho también
    // debe caber al pasar de escritorio a móvil, sin cortar sus hojas laterales.
    this.viewHeight = Math.max((this.spanY || 1) + 2.3, ((this.spanX || 1) + 2.4) / aspect, 5.8);
    this.camera.left = -this.viewHeight * aspect / 2;
    this.camera.right = this.viewHeight * aspect / 2;
    this.camera.top = this.viewHeight / 2;
    this.camera.bottom = -this.viewHeight / 2;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  animate(now) {
    this.frame = requestAnimationFrame(this.animate);
    const time = (now - this.started) / 1000;
    this.controls.update();
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    for (const [id, node] of this.nodes) {
      const elapsed = Math.max(0, time - node.depth * .12 - node.index * .025);
      const progress = this.reducedMotion ? 1 : Math.min(1, elapsed / .65);
      const scale = 1 - Math.pow(1 - progress, 3);
      node.group.scale.setScalar(Math.max(.001, scale));
      const active = id === this.active;
      const selected = id === this.selected;
      node.body.material.color.lerpColors(node.baseColor, node.warmColor, active ? .45 : this.visited.has(id) ? .2 : 0);
      const pulse = this.reducedMotion ? 0 : Math.sin(now * .0025) * .05;
      node.ring.material.opacity = active ? .95 : selected ? .55 : 0;
      node.ring.scale.setScalar(active ? 1.07 + pulse : 1 + pulse * .35);
      node.halo.material.opacity = active ? .2 : selected ? .09 : 0;
      const point = node.group.position.clone().add(new THREE.Vector3(0, 0, .12)).project(this.camera);
      const x = (point.x * .5 + .5) * width;
      const y = (-point.y * .5 + .5) * height;
      const diameter = .77 * height / this.viewHeight * this.camera.zoom * Math.max(scale, .001);
      node.label.style.width = `${diameter}px`;
      node.label.style.height = `${diameter}px`;
      node.label.style.transform = `translate(${x - diameter / 2}px, ${y - diameter / 2}px)`;
      const textLength = symbolFor(node.data.label).length;
      const fontRatio = Math.min(node.data.kind === 'function' || node.data.kind === 'variable' ? .47 : .38, 1.12 / textLength);
      node.symbol.style.fontSize = `${Math.max(4, diameter * fontRatio)}px`;
      node.label.querySelector('.node-caption').style.display = diameter < 26 ? 'none' : '';
      node.label.style.opacity = String(progress);
      node.label.style.visibility = point.z < -1 || point.z > 1 || progress < .05 ? 'hidden' : 'visible';
    }
    for (const edge of this.edges) {
      const appeared = this.reducedMotion ? 1 : Math.min(1, Math.max(0, time - edge.delay) * 2);
      const active = this.active === edge.parent && this.visited.has(edge.child) || this.active === edge.child;
      edge.line.material.color.set(active ? '#df9d64' : '#bec5af');
      edge.line.material.opacity = appeared * (active ? 1 : .7);
      edge.dot.visible = !this.reducedMotion && appeared === 1;
      edge.dot.position.copy(edge.curve.getPoint(1 - ((time * .18 + edge.delay) % 1)));
    }
    this.renderer.render(this.scene, this.camera);
  }

  async exportPNG(expression) {
    // Leemos el canvas de WebGL y añadimos las etiquetas HTML a una imagen final.
    const canvas = document.createElement('canvas');
    const scale = 2;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    canvas.width = width * scale;
    canvas.height = (height + 74) * scale;
    const context = canvas.getContext('2d');
    context.scale(scale, scale);
    context.fillStyle = '#fdfcf8';
    context.fillRect(0, 0, width, height + 74);
    context.fillStyle = '#3e4935';
    context.font = '600 17px sans-serif';
    context.fillText('arboria. / árbol de expresión', 24, 30);
    context.fillStyle = '#929b83';
    context.font = '11px monospace';
    context.fillText(expression.length > 75 ? expression.slice(0, 72) + '…' : expression, 24, 53);
    this.renderer.render(this.scene, this.camera);
    context.drawImage(this.renderer.domElement, 0, 74, width, height);
    for (const node of this.nodes.values()) {
      if (node.label.style.visibility === 'hidden') continue;
      const labelBox = node.label.getBoundingClientRect();
      const graphBox = this.container.getBoundingClientRect();
      context.textAlign = 'center';
      context.textBaseline = 'middle';
      context.fillStyle = node.data.kind === 'function' ? '#fff9f1' : '#48503e';
      context.font = `${node.data.kind === 'variable' ? 'italic ' : ''}${node.symbol.style.fontSize} ${node.data.kind === 'variable' || node.data.kind === 'function' ? 'Georgia' : 'sans-serif'}`;
      context.fillText(symbolFor(node.data.label), labelBox.x - graphBox.x + labelBox.width / 2, 74 + labelBox.y - graphBox.y + labelBox.height / 2);
    }
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
    if (!blob) throw new Error('No se pudo generar la imagen.');
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.download = 'arboria-arbol.png';
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1500);
  }
}
