// Domain model for STAT7 services, nodes, edges, and events
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

export class Node {
  constructor({ id, role, name }) {
    this.id = id; this.role = role; this.name = name || id;
    this.load = 0; // msgs/s or normalized load
    this.errorRate = 0; // 0..1
    this.latencyMs = 0;
    this.pos = new THREE.Vector3();
    this.vel = new THREE.Vector3();
    this.fixed = false;
  }
}

export class Edge {
  constructor({ id, a, b, topic }) {
    this.id = id; this.a = a; this.b = b; this.topic = topic || '';
    this.throughput = 0; // msgs/s
    this.latencyMs = 0;
    this.activity = 0; // 0..1 recent activity
  }
}

export class Graph {
  constructor() { this.nodes = new Map(); this.edges = new Map(); }
  ensureNode(key, init) { if (!this.nodes.has(key)) this.nodes.set(key, new Node({ id: key, ...init })); return this.nodes.get(key); }
  ensureEdge(key, init) { if (!this.edges.has(key)) this.edges.set(key, new Edge({ id: key, ...init })); return this.edges.get(key); }
}

export class WorldState {
  constructor() { this.graph = new Graph(); this.time = 0; }
  upsertNode(id, props) { const n = this.graph.ensureNode(id, props); Object.assign(n, props); return n; }
  upsertEdge(id, props) { const e = this.graph.ensureEdge(id, props); Object.assign(e, props); return e; }
}
