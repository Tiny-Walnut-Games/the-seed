// Simple force-directed layout with gentle edge targets
import { clamp } from './stat7-utils.js';

export class LayoutEngine {
  constructor(cfg, world) { this.cfg = cfg; this.world = world; this._initPositions(); }
  _initPositions() {
    // Arrange initial roles on a ring
    const nodes = Array.from(this.world.graph.nodes.values());
    if (!nodes.length) return;
    const R = 260; const y = 0; const roles = ['api-gateway','event-store','tick-engine','governance'];
    for (let i=0;i<roles.length;i++) {
      const n = this.world.graph.nodes.get(roles[i]); if (!n) continue; const a = i/roles.length * Math.PI*2;
      n.pos.set(Math.cos(a)*R, y, Math.sin(a)*R);
    }
  }

  update(dt, enabled=true) {
    if (!enabled) return;
    const g = this.world.graph; const cfg = this.cfg.graph;
    const nodes = Array.from(g.nodes.values());
    const edges = Array.from(g.edges.values());

    // Pairwise repulsion (limited N)
    for (let i=0;i<nodes.length;i++) {
      for (let j=i+1;j<nodes.length;j++) {
        const a = nodes[i], b = nodes[j];
        const dx = b.pos.x - a.pos.x, dy = b.pos.y - a.pos.y, dz = b.pos.z - a.pos.z;
        const dist2 = dx*dx+dy*dy+dz*dz + 0.01; const dist = Math.sqrt(dist2);
        const force = cfg.repel / dist2;
        const fx = force * dx/dist, fy = force * dy/dist, fz = force * dz/dist;
        if (!a.fixed) { a.vel.x -= fx*dt; a.vel.y -= fy*dt; a.vel.z -= fz*dt; }
        if (!b.fixed) { b.vel.x += fx*dt; b.vel.y += fy*dt; b.vel.z += fz*dt; }
      }
    }

    // Edge springs
    for (const e of edges) {
      const a = g.nodes.get(e.a), b = g.nodes.get(e.b); if (!a || !b) continue;
      const dx = b.pos.x - a.pos.x, dy = b.pos.y - a.pos.y, dz = b.pos.z - a.pos.z;
      const dist = Math.sqrt(dx*dx+dy*dy+dz*dz) + 0.0001; const dirx = dx/dist, diry = dy/dist, dirz = dz/dist;
      const target = this.cfg.graph.edgeLen;
      const stretch = dist - target; // positive if too long
      const k = this.cfg.graph.spring * (1 + clamp(e.throughput / 200, 0, 4));
      const f = -k * stretch;
      if (!a.fixed) { a.vel.x += f * dirx * dt; a.vel.y += f * diry * dt; a.vel.z += f * dirz * dt; }
      if (!b.fixed) { b.vel.x -= f * dirx * dt; b.vel.y -= f * diry * dt; b.vel.z -= f * dirz * dt; }
    }

    // Integrate with damping
    for (const n of nodes) {
      n.vel.x *= this.cfg.graph.damping; n.vel.y *= this.cfg.graph.damping; n.vel.z *= this.cfg.graph.damping;
      n.pos.x += n.vel.x; n.pos.y += n.vel.y; n.pos.z += n.vel.z;
    }

    // Decay edge activity
    for (const e of edges) e.activity = Math.max(0, e.activity - dt * 0.6);
  }
}
