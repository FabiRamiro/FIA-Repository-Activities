// Three.js se encarga únicamente de dibujar: el algoritmo vive en Python.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import { sampleMotion } from './motion.js';

const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

export class SakuraBoard {
  constructor(container, onSquareClick) {
    this.container = container;
    this.onSquareClick = onSquareClick;
    this.n = 8;
    this.positions = [];
    this.motionClock = 0;
    this.animationDuration = 0.8;
    this.queenStates = new Map();
    this.paused = false;
    this.challenge = false;
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(36, 1, 0.1, 100);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.35;
    container.append(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.06;
    this.controls.enablePan = false;
    this.controls.minDistance = 3;
    this.controls.maxDistance = 27;
    this.controls.minPolarAngle = 0.2;
    this.controls.maxPolarAngle = Math.PI / 2.35;
    this.resetCamera();

    this.scene.add(new THREE.HemisphereLight(0xe6d5ff, 0x58405c, 2.8));
    const key = new THREE.DirectionalLight(0xffe0ed, 4.2);
    key.position.set(-5, 12, 5);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7 });
    key.shadow.bias = -0.0005;
    key.shadow.normalBias = 0.03;
    this.scene.add(key);
    const rim = new THREE.DirectionalLight(0xbdb5ff, 3);
    rim.position.set(7, 5, -5);
    this.scene.add(rim);
    const pinkLight = new THREE.PointLight(0xf1a6cc, 18, 18);
    pinkLight.position.set(-5, 2, 3);
    this.scene.add(pinkLight);

    this.boardGroup = new THREE.Group();
    this.queenGroup = new THREE.Group();
    this.scene.add(this.boardGroup, this.queenGroup);
    this.createPetals();
    this.setSize(8);
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    let pointerDown = null;
    const canvas = this.renderer.domElement;
    canvas.tabIndex = 0;
    canvas.setAttribute('aria-label', 'Tablero 3D. En Desafío, usa las flechas para elegir casilla y Enter para colocar o retirar una reina.');
    canvas.addEventListener('keydown', (event) => {
      if (!this.challenge) return;
      const moves = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
      if (moves[event.key]) {
        event.preventDefault();
        const square = this.hoverSquare || { row: 0, column: 0 };
        const [dr, dc] = moves[event.key];
        this.hoverSquare = { row: Math.max(0, Math.min(this.n - 1, square.row + dr)),
          column: Math.max(0, Math.min(this.n - 1, square.column + dc)) };
        this.paintTiles();
        canvas.setAttribute('aria-label', `Fila ${this.hoverSquare.row + 1}, columna ${this.hoverSquare.column + 1}. Enter coloca o retira una reina.`);
      } else if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        const square = this.hoverSquare || { row: 0, column: 0 };
        this.onSquareClick(square.row, square.column);
      }
    });
    canvas.addEventListener('pointerdown', (event) => { pointerDown = [event.clientX, event.clientY]; });
    canvas.addEventListener('pointerup', (event) => {
      if (!this.challenge || !pointerDown) return;
      if (Math.hypot(event.clientX - pointerDown[0], event.clientY - pointerDown[1]) > 6) return;
      const square = this.pickSquare(event);
      if (square) this.onSquareClick(square.row, square.column);
    });
    canvas.addEventListener('pointermove', (event) => {
      if (!this.challenge) return;
      const square = this.pickSquare(event);
      this.hoverSquare = square;
      this.paintTiles();
      canvas.style.cursor = square ? 'pointer' : 'grab';
    });
    canvas.addEventListener('pointerleave', () => { this.hoverSquare = null; this.paintTiles(); });

    this.resizeObserver = new ResizeObserver(() => this.resize());
    this.resizeObserver.observe(container);
    this.lastFrame = 0;
    this.animate = this.animate.bind(this);
    this.renderer.setAnimationLoop(this.animate);
    // Permite comprobar el render sin acoplar el resto de la interfaz a Three.js.
    container.dataset.renderer = 'threejs';
  }

  clearGroup(group) {
    // Liberar la memoria de GPU evita acumular tableros al cambiar N.
    group.traverse((object) => {
      object.geometry?.dispose();
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach((material) => { material?.map?.dispose(); material?.dispose(); });
    });
    group.clear();
  }

  setSize(n) {
    this.finishMotion?.();
    this.finishMotion = null;
    this.container.dataset.animating = 'false';
    this.n = n;
    this.cell = 8 / n;
    this.hoverSquare = null;
    this.clearGroup(this.boardGroup);
    this.clearGroup(this.queenGroup);
    this.queenStates.clear();
    this.positions = [];
    this.instancedQueens = null;
    this.boardPlane = null;
    this.tiles = [];
    const base = new THREE.Mesh(new THREE.BoxGeometry(8.45, 0.38, 8.45),
      new THREE.MeshStandardMaterial({ color: 0x37283f, roughness: 0.5, metalness: 0.35 }));
    base.position.y = -0.27;
    base.receiveShadow = true;
    base.castShadow = true;
    this.boardGroup.add(base);
    for (const height of [-0.12, -0.39]) {
      const rim = new THREE.Mesh(new THREE.BoxGeometry(8.5, 0.025, 8.5),
        new THREE.MeshStandardMaterial({ color: 0xc9a6b8, metalness: 0.7, roughness: 0.35 }));
      rim.position.y = height;
      this.boardGroup.add(rim);
    }
    if (n <= 24) for (let row = 0; row < n; row++) {
      for (let column = 0; column < n; column++) {
        const color = (row + column) % 2 ? 0x685476 : 0xbba6c3;
        const tile = new THREE.Mesh(new THREE.BoxGeometry(this.cell * .982, 0.13, this.cell * .982),
          new THREE.MeshStandardMaterial({ color, roughness: 0.64, metalness: 0.08 }));
        tile.position.set(this.coordinate(column), -0.015, this.coordinate(row));
        tile.receiveShadow = true;
        tile.userData = { row, column, baseColor: color };
        this.boardGroup.add(tile);
        this.tiles.push(tile);
      }
      this.addLabel(String(n - row), -4.17, this.coordinate(row));
      this.addLabel(String(row + 1), this.coordinate(row), 4.18);
    }
    if (n > 24) {
      // Una sola superficie con patrón repetido sustituye N² objetos.
      const image = document.createElement('canvas');
      image.width = image.height = 2;
      const context = image.getContext('2d');
      context.fillStyle = '#bba6c3'; context.fillRect(0, 0, 2, 2);
      context.fillStyle = '#685476'; context.fillRect(1, 0, 1, 1); context.fillRect(0, 1, 1, 1);
      const texture = new THREE.CanvasTexture(image);
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
      texture.repeat.set(n / 2, n / 2);
      texture.magFilter = THREE.NearestFilter;
      this.boardPlane = new THREE.Mesh(new THREE.PlaneGeometry(8, 8),
        new THREE.MeshStandardMaterial({ map: texture, roughness: .64, metalness: .08 }));
      this.boardPlane.rotation.x = -Math.PI / 2;
      this.boardPlane.position.y = .05;
      this.boardPlane.receiveShadow = true;
      this.boardGroup.add(this.boardPlane);
      const stride = Math.ceil(n / 16);
      for (let index = 0; index < n; index += stride) {
        this.addLabel(String(n - index), -4.17, this.coordinate(index));
        this.addLabel(String(index + 1), this.coordinate(index), 4.18);
      }
    }
    this.hoverMarker = new THREE.Mesh(new THREE.PlaneGeometry(this.cell * .98, this.cell * .98),
      new THREE.MeshBasicMaterial({ color: 0xa6c8ba, transparent: true, opacity: .65, depthWrite: false }));
    this.hoverMarker.rotation.x = -Math.PI / 2;
    this.hoverMarker.visible = false;
    this.boardGroup.add(this.hoverMarker);
    if (n > 48) {
      // Instancing: una geometría compartida para todas las reinas grandes.
      const profile = [[0,0],[.28,0],[.30,.08],[.23,.17],[.13,.3],[.10,.58],
        [.20,.68],[.15,.76],[.23,1],[.1,1.07],[.09,1.18],[0,1.22]];
      this.instancedQueens = new THREE.InstancedMesh(
        new THREE.LatheGeometry(profile.map(([x,y]) => new THREE.Vector2(x,y)), 12),
        new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: .25, roughness: .36 }), n);
      this.instancedQueens.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
      this.instancedQueens.castShadow = n <= 256;
      this.instancedQueens.frustumCulled = false;
      this.instanceDummy = new THREE.Object3D();
      this.instanceColor = new THREE.Color();
      for (let index = 0; index < n; index++) {
        this.instanceDummy.scale.setScalar(0); this.instanceDummy.updateMatrix();
        this.instancedQueens.setMatrixAt(index, this.instanceDummy.matrix);
        this.instancedQueens.setColorAt(index, this.instanceColor.setHex(0xf2c9dd));
      }
      this.queenGroup.add(this.instancedQueens);
    }
    const shadow = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.ShadowMaterial({ opacity: 0.17 }));
    shadow.rotation.x = -Math.PI / 2;
    shadow.position.y = -0.5;
    shadow.receiveShadow = true;
    this.boardGroup.add(shadow);
    this.setQueens([]);
  }

  coordinate(index) { return -4 + this.cell * (index + 0.5); }

  addLabel(text, x, z) {
    const canvas = document.createElement('canvas');
    canvas.width = 96;
    canvas.height = 96;
    const context = canvas.getContext('2d');
    context.fillStyle = '#e0c5dd';
    context.font = '44px Georgia';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.fillText(text, 48, 48);
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    const label = new THREE.Mesh(new THREE.PlaneGeometry(0.26, 0.26),
      new THREE.MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false }));
    label.rotation.x = -Math.PI / 2;
    label.position.set(x, -0.055, z);
    this.boardGroup.add(label);
  }

  createQueen(conflict = false) {
    const group = new THREE.Group();
    const material = new THREE.MeshStandardMaterial({ color: conflict ? 0xff6e98 : 0xf2c9dd,
      roughness: 0.3, metalness: 0.22, flatShading: false });
    const trim = new THREE.MeshStandardMaterial({ color: conflict ? 0xe14d7c : 0xc6a0c1,
      roughness: 0.32, metalness: 0.6 });
    // LatheGeometry hace girar este perfil 2D para obtener una pieza de ajedrez.
    const profile = [[0, 0], [.26, 0], [.29, .035], [.29, .08], [.25, .12], [.24, .17],
      [.19, .2], [.17, .25], [.12, .34], [.105, .55], [.14, .64], [.20, .67],
      [.20, .72], [.15, .75], [.18, .8], [.22, .98], [.20, 1.01], [0, 1.01]];
    const body = new THREE.Mesh(new THREE.LatheGeometry(profile.map(([x, y]) => new THREE.Vector2(x, y)), 32), material);
    body.castShadow = true;
    body.receiveShadow = true;
    group.add(body);
    for (const height of [0.12, 0.69, 0.97]) {
      const ring = new THREE.Mesh(new THREE.TorusGeometry(height === .12 ? .25 : .20, .018, 6, 32), trim);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = height;
      group.add(ring);
    }
    for (let point = 0; point < 5; point++) {
      const angle = point / 5 * Math.PI * 2;
      const tip = new THREE.Mesh(new THREE.SphereGeometry(.055, 12, 8), material);
      tip.position.set(Math.sin(angle) * .215, 1.075, Math.cos(angle) * .215);
      const spoke = new THREE.Mesh(new THREE.ConeGeometry(.055, .18, 8), material);
      spoke.position.set(Math.sin(angle) * .20, 1, Math.cos(angle) * .20);
      group.add(tip, spoke);
    }
    const pearl = new THREE.Mesh(new THREE.SphereGeometry(.075, 16, 12), trim);
    pearl.position.y = 1.13;
    group.add(pearl);
    const halo = new THREE.Mesh(new THREE.RingGeometry(.30, .32, 40),
      new THREE.MeshBasicMaterial({ color: conflict ? 0xff779e : 0xf0bedb, transparent: true, opacity: .45, side: THREE.DoubleSide }));
    halo.rotation.x = -Math.PI / 2;
    halo.position.y = .01;
    group.add(halo);
    group.scale.setScalar(Math.min(this.cell * .89, 1.9));
    return group;
  }

  setQueens(positions, conflicts = []) {
    this.finishMotion?.();
    this.finishMotion = null;
    this.paused = false;
    const previous = this.positions;
    this.positions = [...positions];
    this.conflicts = new Set(conflicts);
    let moved = 0;
    for (let row = 0; row < Math.max(positions.length, previous.length); row++) {
      const column = positions[row] ?? -1;
      let entry = this.queenStates.get(row);
      if (!entry && column >= 0) {
        const mesh = this.instancedQueens ? null : this.createQueen();
        if (mesh) this.queenGroup.add(mesh);
        entry = { mesh, x: this.coordinate(column), y: .06 + Math.max(.6, this.cell * 2),
          z: this.coordinate(row), scale: 0, active: false };
        this.queenStates.set(row, entry);
      }
      if (!entry) continue;
      entry.conflict = this.conflicts.has(row);
      entry.mesh?.traverse((object) => {
        if (object.isMesh && object.material.color) {
          object.material.color.setHex(entry.conflict ? 0xef769d : 0xf2c9dd);
        }
      });
      if (column === previous[row] && !entry.motion) continue;
      if (column < 0 && !entry.active && !entry.motion) continue;
      const target = { x: column >= 0 ? this.coordinate(column) : entry.x,
        y: column >= 0 ? .06 : .06 + Math.max(.6, this.cell * 2),
        z: this.coordinate(row), scale: column >= 0 ? 1 : 0 };
      entry.active = column >= 0;
      entry.motion = { from: { x: entry.x, y: entry.y, z: entry.z, scale: entry.scale },
        target, start: this.motionClock + Math.min(moved * .018, .18),
        duration: reducedMotion ? 0 : this.animationDuration,
        lift: Math.max(.35, Math.min(1.5, this.cell * 1.4)) };
      moved++;
    }
    this.paintTiles();
    if (!moved) { this.container.dataset.animating = 'false'; return Promise.resolve(); }
    this.container.dataset.animating = 'true';
    return new Promise((resolve) => { this.finishMotion = resolve; });
  }

  setAnimationSpeed(milliseconds) { this.animationDuration = Math.max(.24, milliseconds / 1000 * .65); }
  setPaused(paused) { this.paused = paused; }

  updateQueens(dt) {
    if (!this.paused) this.motionClock += dt;
    let pending = false;
    let instancesChanged = false;
    for (const [row, entry] of this.queenStates) {
      if (entry.motion) {
        const motion = entry.motion;
        const t = motion.duration === 0 ? 1 : THREE.MathUtils.clamp((this.motionClock - motion.start) / motion.duration, 0, 1);
        Object.assign(entry, sampleMotion(motion.from, motion.target, t, motion.lift));
        if (t === 1) entry.motion = null; else pending = true;
      }
      const scale = Math.min(this.cell * .89, 1.9) * entry.scale;
      if (entry.mesh) {
        entry.mesh.position.set(entry.x, entry.y, entry.z);
        entry.mesh.scale.setScalar(scale);
        entry.mesh.visible = scale > .00001;
      } else if (this.instancedQueens) {
        this.instanceDummy.position.set(entry.x, entry.y, entry.z);
        this.instanceDummy.scale.setScalar(scale);
        this.instanceDummy.updateMatrix();
        this.instancedQueens.setMatrixAt(row, this.instanceDummy.matrix);
        this.instancedQueens.setColorAt(row, this.instanceColor.setHex(entry.conflict ? 0xef769d : 0xf2c9dd));
        instancesChanged = true;
      }
    }
    if (instancesChanged) {
      this.instancedQueens.instanceMatrix.needsUpdate = true;
      this.instancedQueens.instanceColor.needsUpdate = true;
    }
    if (!pending && this.finishMotion) {
      this.container.dataset.animating = 'false';
      this.finishMotion(); this.finishMotion = null;
    }
  }

  setChallenge(enabled) { this.challenge = enabled; this.hoverSquare = null; this.paintTiles(); }

  paintTiles() {
    if (this.hoverMarker) {
      this.hoverMarker.visible = this.challenge && Boolean(this.hoverSquare);
      if (this.hoverMarker.visible) this.hoverMarker.position.set(
        this.coordinate(this.hoverSquare.column), .065, this.coordinate(this.hoverSquare.row));
    }
    this.tiles?.forEach((tile) => {
      tile.material.color.setHex(tile.userData.baseColor);
      tile.material.emissive.setHex(0x000000);
      const { row, column } = tile.userData;
      if (this.positions[row] === column) {
        tile.material.emissive.setHex(this.conflicts?.has(row) ? 0x66152c : 0x492a49);
        tile.material.emissiveIntensity = .35;
      }
      if (this.challenge && this.hoverSquare?.row === row && this.hoverSquare?.column === column) {
        const valid = this.positions.every((other, otherRow) => other < 0 || otherRow === row
          || (other !== column && Math.abs(otherRow - row) !== Math.abs(other - column)));
        tile.material.color.setHex(valid ? 0x9bc8b1 : 0xb85d80);
      }
    });
  }

  pickSquare(event) {
    const rect = this.renderer.domElement.getBoundingClientRect();
    this.pointer.set((event.clientX - rect.left) / rect.width * 2 - 1,
      -(event.clientY - rect.top) / rect.height * 2 + 1);
    this.raycaster.setFromCamera(this.pointer, this.camera);
    if (this.boardPlane) {
      const hit = this.raycaster.intersectObject(this.boardPlane)[0];
      if (!hit) return null;
      return { row: Math.min(this.n - 1, Math.floor((hit.point.z + 4) / this.cell)),
        column: Math.min(this.n - 1, Math.floor((hit.point.x + 4) / this.cell)) };
    }
    return this.raycaster.intersectObjects(this.tiles)[0]?.object.userData;
  }

  createPetals() {
    this.petals = new THREE.Group();
    const shape = new THREE.Shape();
    shape.moveTo(0, -.1);
    shape.bezierCurveTo(-.14, 0, -.09, .12, -.025, .09);
    shape.lineTo(0, .065);
    shape.lineTo(.025, .09);
    shape.bezierCurveTo(.12, .13, .12, 0, 0, -.1);
    const geometry = new THREE.ShapeGeometry(shape);
    const material = new THREE.MeshBasicMaterial({ color: 0xe7b4d0, transparent: true,
      opacity: .55, side: THREE.DoubleSide, depthWrite: false });
    for (let i = 0; i < 32; i++) {
      const petal = new THREE.Mesh(geometry, material);
      petal.position.set(Math.random() * 18 - 9, Math.random() * 9 + 1, Math.random() * 14 - 7);
      petal.rotation.set(Math.random() * 3, Math.random() * 3, Math.random() * 3);
      petal.userData.speed = .3 + Math.random() * .45;
      this.petals.add(petal);
    }
    this.scene.add(this.petals);
  }

  resetCamera() {
    this.camera.position.set(9.2, 10.8, 11.7);
    this.controls.target.set(0, -.1, 0);
    this.controls.update();
  }

  resize() {
    const { clientWidth: width, clientHeight: height } = this.container;
    if (!width || !height) return;
    this.camera.aspect = width / height;
    // En pantallas estrechas alejamos un poco para conservar las esquinas.
    this.camera.fov = 36;
    this.camera.zoom = Math.min(1, this.camera.aspect / 1.35);
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  animate(time) {
    const dt = Math.min((time - this.lastFrame) / 1000, .05);
    this.lastFrame = time;
    if (!document.hidden) this.updateQueens(dt);
    if (!document.hidden && !reducedMotion) {
      this.petals.children.forEach((petal, index) => {
        petal.position.y -= dt * petal.userData.speed;
        petal.position.x += Math.sin(time * .0003 + index) * dt * .16;
        petal.rotation.z += dt * .35;
        petal.rotation.y += dt * .2;
        if (petal.position.y < -.7) petal.position.y = 9;
      });
    }
    this.controls.update();
    if (!document.hidden) this.renderer.render(this.scene, this.camera);
  }
}
