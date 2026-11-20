import test from 'node:test';
import assert from 'node:assert/strict';
import { sampleMotion } from '../static/motion.js';

const from = {x: -3, y: .06, z: 2, scale: 1};
const target = {x: 3, y: .06, z: 2, scale: 1};
const close = (a, b) => assert.ok(Math.abs(a - b) < 1e-10);

test('primero se eleva sin cambiar de casilla', () => {
  const sample = sampleMotion(from, target, .15, 1);
  close(sample.x, from.x); close(sample.z, from.z);
  assert.ok(sample.y > from.y);
});
test('se desplaza elevada y mantiene la fila', () => {
  const sample = sampleMotion(from, target, .5, 1);
  assert.ok(sample.x > from.x && sample.x < target.x);
  close(sample.y, from.y + 1); close(sample.z, from.z);
});
test('llega a la columna antes de terminar el aterrizaje', () => {
  const sample = sampleMotion(from, target, .85, 1);
  close(sample.x, target.x); assert.ok(sample.y > target.y);
});
test('los extremos son exactos y nunca cruza bajo el tablero', () => {
  assert.deepEqual(sampleMotion(from, target, 0, 1), from);
  const end = sampleMotion(from, target, 1, 1);
  for (const key of Object.keys(target)) close(end[key], target[key]);
  for (let t = 0; t <= 1; t += .01) assert.ok(sampleMotion(from, target, t, 1).y >= from.y - 1e-10);
});
test('la retirada termina con escala cero y admite interrupciones', () => {
  const middle = sampleMotion(from, target, .5, 1);
  const removed = {...middle, y: 2, scale: 0};
  assert.deepEqual(sampleMotion(middle, removed, 0, 1), middle);
  close(sampleMotion(middle, removed, 1, 1).scale, 0);
});
