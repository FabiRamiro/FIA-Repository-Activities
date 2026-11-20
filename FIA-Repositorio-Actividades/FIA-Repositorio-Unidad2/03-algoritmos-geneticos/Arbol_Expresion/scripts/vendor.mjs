import { mkdir, copyFile } from 'node:fs/promises';

// Copiamos únicamente los módulos utilizados. El navegador no necesita un CDN.
const destination = new URL('../static/vendor/', import.meta.url);
await mkdir(destination, { recursive: true });
for (const file of ['three.module.js', 'three.core.js']) {
  await copyFile(new URL(`../node_modules/three/build/${file}`, import.meta.url), new URL(file, destination));
}
await copyFile(new URL('../node_modules/three/examples/jsm/controls/OrbitControls.js', import.meta.url), new URL('OrbitControls.js', destination));
await copyFile(new URL('../node_modules/three/LICENSE', import.meta.url), new URL('THREE-LICENSE.txt', destination));
console.log('Three.js listo en static/vendor.');
