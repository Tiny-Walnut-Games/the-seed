// View: builds and updates Three.js meshes for nodes/edges and optional labels
import { clamp } from './stat7-utils.js';

export class View {
  constructor(cfg, world, scene, camera) {
    this.cfg = cfg; this.world = world; this.scene = scene; this.camera = camera;
    this.group = new THREE.Group(); scene.add(this.group);

    this.nodeMeshes = new Map();
    this.edgeMeshes = new Map();
    this.labels = new Map();

    this._setup();
  }

  _setup() {
    // Create edge lines group
    this.edgeGroup = new THREE.Group(); this.group.add(this.edgeGroup);
    this.nodeGroup = new THREE.Group(); this.group.add(this.nodeGroup);
    this.labelGroup = new THREE.Group(); this.group.add(this.labelGroup);
  }

  _nodeColor(role) {
    const p = this.cfg.view.palette;
    if (role === 'api' || role === this.cfg.roles.API_GATEWAY) return p.api;
    if (role === 'eventstore' || role === this.cfg.roles.EVENT_STORE) return p.eventstore;
    if (role === 'tick' || role === this.cfg.roles.TICK_ENGINE) return p.tick;
    if (role === 'governance' || role === this.cfg.roles.GOVERNANCE) return p.governance;
    return 0x90a4ae;
  }

  ensureNodeMesh(node) {
    if (this.nodeMeshes.has(node.id)) return this.nodeMeshes.get(node.id);
    const geom = new THREE.SphereGeometry(this.cfg.view.node.baseSize, 24, 24);
    const mat = new THREE.MeshStandardMaterial({ color:this._nodeColor(node.role), metalness:0.15, roughness:0.6 });
    const mesh = new THREE.Mesh(geom, mat); mesh.castShadow = false; mesh.receiveShadow=false;

    // Halo
    if (this.cfg.view.node.halo) {
      const hgeom = new THREE.RingGeometry(1.2*this.cfg.view.node.baseSize, 1.5*this.cfg.view.node.baseSize, 32);
      const hmat = new THREE.MeshBasicMaterial({ color:0xffffff, transparent:true, opacity:0.18, side:THREE.DoubleSide });
      const halo = new THREE.Mesh(hgeom, hmat); halo.rotation.x = -Math.PI/2; mesh.add(halo); mesh.userData.halo = halo;
    }

    this.nodeGroup.add(mesh);
    this.nodeMeshes.set(node.id, mesh);

    // Label
    const div = document.createElement('div');
    div.style.position='absolute'; div.style.pointerEvents='none'; div.style.color='#cfd8dc'; div.style.fontSize='12px'; div.style.opacity='0.9';
    div.textContent = node.name;
    const label = { el: div };
    document.body.appendChild(div);
    this.labels.set(node.id, label);

    return mesh;
  }

  ensureEdgeMesh(edge) {
    if (this.edgeMeshes.has(edge.id)) return this.edgeMeshes.get(edge.id);
    const mat = new THREE.LineBasicMaterial({ color: this.cfg.view.palette.link, transparent:true, opacity:0.8 });
    const geom = new THREE.BufferGeometry(); geom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(6), 3));
    const line = new THREE.Line(geom, mat);
    this.edgeGroup.add(line);
    this.edgeMeshes.set(edge.id, line);
    return line;
  }

  update(dt, opts) {
    // Ensure meshes
    for (const node of this.world.graph.nodes.values()) {
      const mesh = this.ensureNodeMesh(node);
      mesh.position.copy(node.pos);
      const scale = 1 + clamp(node.load/300, 0, 2);
      mesh.scale.setScalar(scale);

      // Halo color by health state
      if (mesh.userData.halo) {
        const err = node.errorRate;
        const th = this.cfg.thresholds;
        const state = err >= th.errorRateError ? 'err' : err >= th.errorRateWarn ? 'warn' : 'ok';
        const color = state==='err'?0xef9a9a: state==='warn'?0xffe082: 0xa5d6a7;
        mesh.userData.halo.material.color.setHex(color);
        mesh.userData.halo.material.opacity = 0.15 + clamp(node.load/400, 0, 0.35);
      }

      // Update label screen-space position
      const label = this.labels.get(node.id);
      if (label) {
        const p = node.pos.clone().project(this.camera);
        const x = (p.x * 0.5 + 0.5) * window.innerWidth;
        const y = (-p.y * 0.5 + 0.5) * window.innerHeight;
        label.el.style.transform = `translate(${x}px,${y}px)`;
        label.el.style.display = opts.labels ? 'block':'none';
        label.el.textContent = `${node.name} · ${Math.round(node.load)} msg/s`;
      }
    }

    // Edges
    for (const edge of this.world.graph.edges.values()) {
      const a = this.world.graph.nodes.get(edge.a), b = this.world.graph.nodes.get(edge.b); if (!a||!b) continue;
      const line = this.ensureEdgeMesh(edge);
      const pos = line.geometry.attributes.position.array;
      pos[0] = a.pos.x; pos[1]=a.pos.y; pos[2]=a.pos.z;
      pos[3] = b.pos.x; pos[4]=b.pos.y; pos[5]=b.pos.z;
      line.geometry.attributes.position.needsUpdate = true;
      const opacity = 0.3 + clamp(edge.activity, 0, 0.7);
      line.material.color.setHex(edge.activity > 0.3 ? this.cfg.view.palette.linkActive : this.cfg.view.palette.link);
      line.material.opacity = opacity;
    }
  }
}
