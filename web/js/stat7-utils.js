// Utility helpers for STAT7 visualizer
export const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
export const lerp = (a, b, t) => a + (b - a) * t;
export const smoothstep = (edge0, edge1, x) => {
  const t = clamp((x - edge0) / (edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
};
export const nowMs = () => performance.now();
export const uid = (() => { let i = 0; return (p='id') => `${p}-${++i}`; })();

export function colorHexToThree(hex) { return new THREE.Color(hex); }

export function movingAverage(windowSize = 30) {
  let buf = new Array(windowSize).fill(0), i = 0, sum = 0, n = 0;
  return {
    push(v) { sum -= buf[i]; buf[i] = v; sum += v; i = (i + 1) % windowSize; n = Math.min(n + 1, windowSize); },
    avg() { return n ? sum / n : 0; }
  };
}

export function ringColorState(value, thresholds) {
  if (value >= thresholds.error) return 'err';
  if (value >= thresholds.warn) return 'warn';
  return 'ok';
}

export function easeTowards(current, target, rate, dt) {
  const inv = Math.exp(-rate * dt);
  return current * inv + target * (1 - inv);
}
