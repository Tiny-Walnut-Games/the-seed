// STAT7 Visualization Orchestrator
// Renders 7-dimensional STAT7 bitchain entities into 3D Three.js space
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { Config } from './stat7-config.js';
import { DataService } from './stat7-data.js';
import { WorldState } from './stat7-model.js';
import { LayoutEngine } from './stat7-layout.js';
import { View } from './stat7-view.js';
import { Effects } from './stat7-effects.js';
import { nowMs } from './stat7-utils.js';
import './stat7-ui.js';

// Attach to window for backward compatibility with tests and global access
window.THREE = THREE;
window.THREE.OrbitControls = OrbitControls;

// Map realm names to realm indices for coordinate projection
const REALM_INDICES = {
  'data': 0,
  'narrative': 1,
  'system': 2,
  'faculty': 3,
  'event': 4,
  'pattern': 5,
  'void': 6,
};

// Realm color mapping
const REALM_COLORS = {
  'data': 0x64B5F6,      // Blue
  'narrative': 0xFFD54F,  // Yellow
  'system': 0xEF5350,     // Red
  'faculty': 0x81C784,    // Green
  'event': 0xBA68C8,      // Purple
  'pattern': 0xFFB74D,    // Orange
  'void': 0x757575,       // Gray
};

/**
 * Project 7D STAT7 coordinates into 3D space for Three.js rendering.
 * 
 * Mental model:
 * - Realm determines color family and broad spatial region
 * - Lineage hash + adjacency spreads entities horizontally (X)
 * - Horizon (visibility range) maps to vertical positioning (Y)
 * - Resonance (coherence) affects Y and glow intensity
 * - Velocity maps to Z depth and movement speed
 * - Density affects mesh size and opacity
 * 
 * Result: 7D coordinates become (x, y, z) with size and color
 */
function projectStat7Coordinates(coords, metadata = {}) {
  const realmIdx = REALM_INDICES[coords.realm] || 0;
  
  // Spread realms in different sectors
  const realmAngle = (realmIdx / 7) * Math.PI * 2;
  const realmRadius = 150;
  const realmX = Math.cos(realmAngle) * realmRadius;
  const realmZ = Math.sin(realmAngle) * realmRadius;
  
  // Hash lineage for deterministic pseudo-random spread
  const lineageHash = (coords.lineage || '').split('').reduce((h, c) => {
    return ((h << 5) - h) + c.charCodeAt(0);
  }, 0);
  const lineageSpread = Math.sin(lineageHash) * 80 + Math.cos(lineageHash * 1.3) * 80;
  
  // Adjacency count affects clustering
  const adjacencyCount = (coords.adjacency && coords.adjacency.length) || 0;
  const clusterRadius = 30 + adjacencyCount * 5;
  
  // Horizon affects vertical distribution (visibility ranges)
  const horizonY = (parseFloat(coords.horizon) || 0) * 50 - 100;
  
  // Resonance amplifies position and affects visual properties
  const resonance = Math.max(0, Math.min(1, parseFloat(coords.resonance) || 0.5));
  const resonanceAmplify = 0.8 + resonance * 0.4;
  
  // Velocity affects Z depth and movement
  const velocity = parseFloat(coords.velocity) || 0;
  const velocityZ = velocity * 100;
  
  // Density affects mesh size
  const density = Math.max(0.3, parseFloat(coords.density) || 1.0);
  
  return {
    position: {
      x: realmX + lineageSpread * resonanceAmplify + clusterRadius * Math.random(),
      y: horizonY + resonance * 100,
      z: realmZ + velocityZ + clusterRadius * Math.random(),
    },
    size: 5 + density * 10,
    color: metadata.color || 0xcccccc,
    opacity: 0.7 + resonance * 0.3,
  };
}

export async function bootstrap(container, ui, cfg = Config) {
  // Scene setup
  console.log(`[STAT7 CORE] Creating renderer for container: ${container.clientWidth}x${container.clientHeight}`);
  
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  renderer.setClearColor(cfg.view.background, 1);
  container.appendChild(renderer.domElement);
  
  console.log(`[STAT7 CORE] Canvas element created: ${renderer.domElement.width}x${renderer.domElement.height}`);
  console.log(`[STAT7 CORE] Canvas is visible: ${renderer.domElement.offsetWidth > 0 && renderer.domElement.offsetHeight > 0}`);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 5000);
  camera.position.set(0, 220, 560);
  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.zoomSpeed = 0.6;

  const lights = new THREE.Group();
  const amb = new THREE.AmbientLight(0xffffff, 0.35);
  lights.add(amb);
  const dir = new THREE.DirectionalLight(0xffffff, 0.7);
  dir.position.set(200, 400, 200);
  lights.add(dir);
  scene.add(lights);

  // Core subsystems
  const world = new WorldState();
  const layout = new LayoutEngine(cfg, world);
  const view = new View(cfg, world, scene, camera);
  const fx = new Effects(cfg, world, scene);
  const data = new DataService(cfg);

  // Entity meshes: map entity_id -> THREE.Mesh
  const entityMeshes = new Map();
  const entityGroup = new THREE.Group();
  scene.add(entityGroup);

  // Narration panel state
  let selectedEntityId = null;
  let narrationPanel = null;

  // Build initial canonical nodes (keep for backward compat with service metrics)
  const roles = cfg.roles;
  world.upsertNode('api-gateway', { role: roles.API_GATEWAY, name: 'API Gateway' });
  world.upsertNode('event-store', { role: roles.EVENT_STORE, name: 'Event Store' });
  world.upsertNode('tick-engine', { role: roles.TICK_ENGINE, name: 'Tick Engine' });
  world.upsertNode('governance', { role: roles.GOVERNANCE, name: 'Governance' });
  // Known edges for default flow
  world.upsertEdge('api->eventstore', { a: 'api-gateway', b: 'event-store', topic: 'events' });
  world.upsertEdge('eventstore->tick', { a: 'event-store', b: 'tick-engine', topic: 'stream' });
  world.upsertEdge('eventstore->governance', { a: 'event-store', b: 'governance', topic: 'audit' });

  // Update UI legend for STAT7 realms
  const legend = ui.legend;
  if (legend) {
    legend.innerHTML = '';
    const mk = (label, color) => {
      const d = document.createElement('div');
      d.style.display = 'flex';
      d.style.alignItems = 'center';
      d.style.gap = '6px';
      d.style.marginRight = '10px';
      const sw = document.createElement('span');
      sw.style.width = '10px';
      sw.style.height = '10px';
      sw.style.borderRadius = '50%';
      sw.style.background = `#${color.toString(16).padStart(6, '0')}`;
      const tx = document.createElement('span');
      tx.textContent = label;
      tx.style.fontSize = '12px';
      tx.style.opacity = '0.9';
      d.appendChild(sw);
      d.appendChild(tx);
      legend.appendChild(d);
    };
    Object.entries(REALM_COLORS).forEach(([realm, color]) => {
      mk(`${realm.charAt(0).toUpperCase() + realm.slice(1)}`, color);
    });
  }

  /**
   * Create or update an entity mesh for a STAT7 entity.
   */
  function createEntityMesh(entityId, data, metadata) {
    // DEBUG: Log mesh creation
    if (window.__stat7Debug) {
      console.log('[STAT7 CORE] Creating mesh for entity:', {
        entityId,
        entityType: data.entity_type,
        realm: data.realm,
        hasCoordinates: !!data.coordinates,
        meshCount: entityMeshes.size,
      });
    }

    // Check if mesh already exists
    if (entityMeshes.has(entityId)) {
      const existing = entityMeshes.get(entityId);
      entityGroup.remove(existing);
    }

    // Project coordinates
    const projection = projectStat7Coordinates(data.coordinates || {}, metadata);

    // Create mesh
    const geometry = new THREE.IcosahedronGeometry(projection.size / 2, 2);
    const color = new THREE.Color(metadata.color || 0xcccccc);
    const material = new THREE.MeshPhongMaterial({
      color: color,
      emissive: color,
      emissiveIntensity: 0.3,
      wireframe: false,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(projection.position);
    mesh.userData = {
      entityId,
      entityType: data.entity_type,
      realm: data.realm,
      coordinates: data.coordinates,
      projection,
    };

    // Add halo effect
    const haloGeo = new THREE.IcosahedronGeometry(projection.size / 2 + 2, 2);
    const haloMat = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.2,
      side: THREE.BackSide,
    });
    const halo = new THREE.Mesh(haloGeo, haloMat);
    halo.position.copy(projection.position);
    mesh.halo = halo;

    entityGroup.add(mesh);
    entityGroup.add(halo);
    entityMeshes.set(entityId, mesh);

    if (window.__stat7Debug) {
      console.log('[STAT7 CORE] Mesh created successfully. Total meshes:', entityMeshes.size);
    }

    return mesh;
  }

  // Data wiring: handle both STAT7 entities and legacy service metrics
  data.on((evt) => {
    if (evt.type === 'connection') {
      const st = data.getStats();
      setConnState(ui.conn, evt.state, evt.mock);
      setLatency(ui.lat, st.avgLatencyMs);
    }

    if (evt.type === 'stat7_entity') {
      // Handle STAT7 bitchain entity events
      const entityData = evt.data || {};
      const entityId = entityData.address || `entity_${evt.timestamp}`;

      if (window.__stat7Debug) {
        console.log('[STAT7 CORE] Processing stat7_entity event:', {
          entityId,
          eventType: evt.event_type,
          hasData: !!evt.data,
          hasMetadata: !!evt.metadata,
        });
      }

      // Create or update entity mesh
      createEntityMesh(entityId, entityData, evt.metadata);

      // Also add to world state for layout engine
      world.upsertNode(entityId, {
        role: 'entity',
        name: entityData.entity_type || 'Unknown',
        type: 'stat7_entity',
        realm: entityData.realm,
        data: entityData,
      });
    }

    if (evt.type === 'entity_narration') {
      // Handle entity narration responses
      if (selectedEntityId === evt.entity_id && evt.narration) {
        displayNarration(evt.entity_id, evt.narration);
      }
    }

    if (evt.type === 'service_metric') {
      // Handle legacy service metrics (backward compat)
      const m = evt.data;
      const roleId =
        m.service === 'api'
          ? 'api-gateway'
          : m.service === 'eventstore'
            ? 'event-store'
            : m.service === 'tick'
              ? 'tick-engine'
              : m.service === 'governance'
                ? 'governance'
                : m.service;

      const n = world.upsertNode(roleId, { role: m.service, name: roleId });
      if (m.metrics) {
        n.latencyMs = m.metrics.latencyMs ?? n.latencyMs;
        n.errorRate = m.metrics.errorRate ?? n.errorRate;
        n.load = m.metrics.throughput ?? n.load;
      }

      const topic = m.topic || 'events';
      const target = topic.includes('audit')
        ? 'governance'
        : topic.includes('tick') || topic.includes('stream')
          ? 'tick-engine'
          : 'event-store';
      const edgeId = `${roleId}->${target}`;
      const e = world.upsertEdge(edgeId, { a: roleId, b: target, topic });
      if (m.metrics) {
        e.latencyMs = m.metrics.latencyMs ?? e.latencyMs;
        e.throughput = m.metrics.throughput ?? e.throughput;
        e.activity = 1.0;
      }

      fx.emitMessage(edgeId, m);
    }
  });

  // Raycaster for entity selection (Warbler narration)
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  /**
   * Create or update the narration display panel.
   */
  function createNarrationPanel() {
    if (!narrationPanel) {
      narrationPanel = document.createElement('div');
      narrationPanel.id = 'narration-panel';
      narrationPanel.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        max-height: 300px;
        background: rgba(0, 0, 0, 0.85);
        color: #e0e0e0;
        border: 2px solid #64B5F6;
        border-radius: 8px;
        padding: 16px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
        overflow-y: auto;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        z-index: 1000;
      `;
      
      // Add close button
      const closeBtn = document.createElement('button');
      closeBtn.textContent = '✕';
      closeBtn.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        background: none;
        border: none;
        color: #64B5F6;
        font-size: 18px;
        cursor: pointer;
        padding: 4px 8px;
      `;
      closeBtn.onclick = () => {
        narrationPanel.style.display = 'none';
        selectedEntityId = null;
      };
      narrationPanel.appendChild(closeBtn);
      
      // Add content container
      const contentDiv = document.createElement('div');
      contentDiv.id = 'narration-content';
      contentDiv.style.cssText = `
        padding-right: 8px;
      `;
      narrationPanel.appendChild(contentDiv);
      
      document.body.appendChild(narrationPanel);
    }
    return narrationPanel;
  }

  /**
   * Display narration for a selected entity.
   */
  function displayNarration(entityId, narration) {
    if (!narration) {
      console.warn(`No narration available for ${entityId}`);
      return;
    }

    const panel = createNarrationPanel();
    const contentDiv = panel.querySelector('#narration-content');
    
    // Clear previous content
    contentDiv.innerHTML = '';
    
    // Add header
    const header = document.createElement('div');
    header.style.cssText = `
      color: #FFD54F;
      font-weight: bold;
      margin-bottom: 8px;
      border-bottom: 1px solid #64B5F6;
      padding-bottom: 8px;
    `;
    header.textContent = `📖 Entity Narration`;
    contentDiv.appendChild(header);
    
    // Add entity ID
    const idDiv = document.createElement('div');
    idDiv.style.cssText = `
      color: #81C784;
      font-size: 11px;
      margin-bottom: 8px;
      opacity: 0.7;
    `;
    idDiv.textContent = `ID: ${entityId}`;
    contentDiv.appendChild(idDiv);
    
    // Add narration text
    const narrationDiv = document.createElement('div');
    narrationDiv.style.cssText = `
      color: #e0e0e0;
      line-height: 1.7;
      font-style: italic;
    `;
    narrationDiv.textContent = narration;
    contentDiv.appendChild(narrationDiv);
    
    // Show panel
    panel.style.display = 'block';
  }

  function onMouseClick(event) {
    // Calculate mouse position in normalized device coordinates
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    // Check for entity intersection
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(Array.from(entityMeshes.values()));

    if (intersects.length > 0) {
      const mesh = intersects[0].object;
      const entityId = mesh.userData.entityId;
      const entityData = mesh.userData;
      
      console.log(`📖 Selected entity: ${entityId}`, entityData);
      
      selectedEntityId = entityId;
      
      // Create panel immediately (show loading state)
      const panel = createNarrationPanel();
      panel.style.display = 'block';
      const contentDiv = panel.querySelector('#narration-content');
      contentDiv.innerHTML = `<div style="color: #FFD54F;">⏳ Loading narration...</div>`;
      
      // Request narration from backend
      data.requestEntityNarration(entityId, entityData, (narration) => {
        if (narration && selectedEntityId === entityId) {
          displayNarration(entityId, narration);
        }
      });
    }
  }

  renderer.domElement.addEventListener('click', onMouseClick);

  // Resize handling
  const onResize = () => {
    const w = container.clientWidth,
      h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
  };
  window.addEventListener('resize', onResize);

  // Main loop
  let last = nowMs();
  let running = true;
  let hudVisible = true;
  let labelsEnabled = true;
  let particlesEnabled = cfg.view.particles.enabled;
  let autoLayout = cfg.graph.autoLayout;

  function frame() {
    if (!running) return;
    const t = nowMs();
    const dt = Math.min((t - last) / 1000, cfg.graph.maxDt);
    last = t;

    layout.update(dt, autoLayout);
    view.update(dt, { labels: labelsEnabled });
    fx.update(dt, particlesEnabled);

    renderer.render(scene, camera);

    // UI stats
    const stats = data.getStats();
    if (ui.fps) ui.fps.textContent = `FPS: ${Math.round(1 / Math.max(0.001, dt))}`;
    if (ui.tp) ui.tp.textContent = `Msgs/s: ${stats.avgThroughput}`;
    if (ui.lat) setLatency(ui.lat, stats.avgLatencyMs);
    if (ui.entities) ui.entities.textContent = `Entities: ${entityMeshes.size}`;

    controls.update();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  data.connect();

  function setConnState(el, state, mock = false) {
    el.classList.remove('ok', 'warn', 'err');
    if (state === 'open') {
      el.classList.add('ok');
      el.textContent = mock ? 'Mock Connected' : 'Connected';
    } else if (state === 'closed') {
      el.classList.add('warn');
      el.textContent = 'Disconnected';
    } else {
      el.classList.add('warn');
      el.textContent = 'Connecting...';
    }
  }

  function setLatency(el, ms) {
    const th = cfg.thresholds;
    el.classList.remove('ok', 'warn', 'err');
    const state =
      ms >= th.latencyErrorMs ? 'err' : ms >= th.latencyWarnMs ? 'warn' : 'ok';
    el.classList.add(state);
    el.textContent = `Latency: ${ms} ms`;
  }

  // Public API for UI toggles
  return {
    // Entity rendering state
    entityMeshes,
    scene,
    particlesEnabled: () => particlesEnabled,
    labelsEnabled: () => labelsEnabled,
    autoLayoutEnabled: () => autoLayout,
    
    // UI controls
    setParticlesEnabled(v) {
      particlesEnabled = v;
    },
    setLabelsEnabled(v) {
      labelsEnabled = v;
    },
    setAutoLayout(v) {
      autoLayout = v;
    },
    setMockMode(v) {
      data.setMock(v);
    },
    toggleHUD() {
      hudVisible = !hudVisible;
      document.getElementById('hud').style.display = hudVisible ? 'block' : 'none';
    },
    pauseResume() {
      running = !running;
      if (running) {
        last = nowMs();
        requestAnimationFrame(frame);
      }
    },
    onMouseClick(obj) {
      // Placeholder for entity selection logic
      // Will be enhanced with Warbler narration callback
    },
  };
}
