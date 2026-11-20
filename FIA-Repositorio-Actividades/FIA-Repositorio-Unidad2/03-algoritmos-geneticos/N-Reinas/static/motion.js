// Interpolación independiente de Three.js para poder comprobar la trayectoria.
const clamp = (value) => Math.max(0, Math.min(1, value));
const smooth = (value) => value * value * (3 - 2 * value);
const lerp = (from, to, amount) => from + (to - from) * amount;

export function sampleMotion(from, target, progress, height) {
  const t = clamp(progress);
  // La pieza primero sube verticalmente, viaja elevada y baja al final.
  const travel = smooth(clamp((t - .22) / .56));
  const lift = t < .22 ? smooth(t / .22) : t > .78 ? 1 - smooth((t - .78) / .22) : 1;
  return { x: lerp(from.x, target.x, travel), z: lerp(from.z, target.z, travel),
    y: lerp(from.y, target.y, smooth(t)) + height * lift,
    scale: lerp(from.scale, target.scale, smooth(t)) };
}
