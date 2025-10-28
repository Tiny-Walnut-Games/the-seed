// Visual effects: message particles moving along edges
import { clamp } from './stat7-utils.js';

export class Effects {
  constructor(cfg, world, scene) {
    this.cfg = cfg; this.world = world; this.scene = scene;
    this.group = new THREE.Group(); scene.add(this.group);

    this.pool = [];
    this.active = [];
    this._initPool();
  }

  _initPool() {
    const count = this.cfg.view.particles.pool;
    const geom = new THREE.SphereGeometry(this.cfg.view.particles.size, 8, 8);
    const mat = new THREE.MeshBasicMaterial({ color:0xb0bec5, transparent:true, opacity:0.9 });
    for (let i=0;i<count;i++) {
      const m = new THREE.Mesh(geom, mat.clone());
      m.visible = false; this.group.add(m); this.pool.push(m);
    }
  }

  spawnParticle() {
    return this.pool.length ? this.pool.pop() : null;
  }

  emitMessage(edgeId, message) {
    const e = this.world.graph.edges.get(edgeId); if (!e) return;
    const a = this.world.graph.nodes.get(e.a), b = this.world.graph.nodes.get(e.b); if (!a||!b) return;
    const p = this.spawnParticle(); if (!p) return;
    p.visible = true; p.position.copy(a.pos);
    const color = message.topic && message.topic.includes('audit') ? 0xffab91 : message.topic && message.topic.includes('command') ? 0x82b1ff : 0xa5d6a7;
    p.material.color.setHex(color);
    const speed = this.cfg.view.particles.speed * (1 + clamp(e.throughput/300, 0, 2));
    this.active.push({ mesh:p, a, b, t:0, speed, life:this.cfg.view.particles.decayMs/1000 });
    e.activity = Math.min(1, e.activity + 0.4);
  }

  update(dt, enabled=true) {
    for (let i=this.active.length-1;i>=0;i--) {
      const it = this.active[i];
      it.t += dt * it.speed / 300; // normalize
      if (!enabled) { it.mesh.visible = false; }
      else {
        const t = clamp(it.t, 0, 1);
        it.mesh.visible = true;
        it.mesh.position.lerpVectors(it.a.pos, it.b.pos, t);
        it.mesh.material.opacity = 0.9 * (1 - t);
        it.mesh.scale.setScalar(1 + 0.8 * (1 - t));
      }
      it.life -= dt; if (it.t >= 1 || it.life <= 0) {
        it.mesh.visible = false; this.pool.push(it.mesh); this.active.splice(i,1);
      }
    }
  }
}
