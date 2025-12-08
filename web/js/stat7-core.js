// Orchestrator: initializes Three.js, data service, model, layout, view, and UI
import { Config } from './stat7-config.js';
import { DataService } from './stat7-data.js';
import { WorldState } from './stat7-model.js';
import { LayoutEngine } from './stat7-layout.js';
import { View } from './stat7-view.js';
import { Effects } from './stat7-effects.js';
import { nowMs } from './stat7-utils.js';
import './stat7-ui.js'; // side-effect: HUD legend builder if needed

export async function bootstrap(container, ui, cfg = Config) {
  // Scene setup
  const renderer = new THREE.WebGLRenderer({ antialias:true, alpha:false });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  renderer.setClearColor(cfg.view.background, 1);
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 5000);
  camera.position.set(0, 220, 560);
  const controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; controls.dampingFactor = 0.08; controls.zoomSpeed = 0.6;

  const lights = new THREE.Group();
  const amb = new THREE.AmbientLight(0xffffff, 0.35); lights.add(amb);
  const dir = new THREE.DirectionalLight(0xffffff, 0.7); dir.position.set(200,400,200); lights.add(dir);
  scene.add(lights);

  // Core subsystems
  const world = new WorldState();
  const layout = new LayoutEngine(cfg, world);
  const view = new View(cfg, world, scene, camera);
  const fx = new Effects(cfg, world, scene);
  const data = new DataService(cfg);

  // Build initial canonical nodes from your backend roles
  const roles = cfg.roles;
  world.upsertNode('api-gateway', { role: roles.API_GATEWAY, name: 'API Gateway' });
  world.upsertNode('event-store', { role: roles.EVENT_STORE, name: 'Event Store' });
  world.upsertNode('tick-engine', { role: roles.TICK_ENGINE, name: 'Tick Engine' });
  world.upsertNode('governance', { role: roles.GOVERNANCE, name: 'Governance' });
  // Known edges for default flow
  world.upsertEdge('api->eventstore', { a:'api-gateway', b:'event-store', topic:'events' });
  world.upsertEdge('eventstore->tick', { a:'event-store', b:'tick-engine', topic:'stream' });
  world.upsertEdge('eventstore->governance', { a:'event-store', b:'governance', topic:'audit' });

  // UI legend build based on config palette
  const legend = ui.legend;
  if (legend) {
    legend.innerHTML = '';
    const mk = (label, color) => {
      const d = document.createElement('div'); d.style.display='flex'; d.style.alignItems='center'; d.style.gap='6px'; d.style.marginRight='10px';
      const sw = document.createElement('span'); sw.style.width='10px'; sw.style.height='10px'; sw.style.borderRadius='50%'; sw.style.background = `#${color.toString(16).padStart(6,'0')}`;
      const tx = document.createElement('span'); tx.textContent = label; tx.style.fontSize='12px'; tx.style.opacity='0.9';
      d.appendChild(sw); d.appendChild(tx); legend.appendChild(d);
    };
    mk('API Gateway', cfg.view.palette.api);
    mk('Event Store', cfg.view.palette.eventstore);
    mk('Tick Engine', cfg.view.palette.tick);
    mk('Governance', cfg.view.palette.governance);
  }

  // Data wiring: use existing websocket protocol where possible
  data.on((evt) => {
    if (evt.type === 'connection') {
      const st = data.getStats();
      setConnState(ui.conn, evt.state, evt.mock);
      setLatency(ui.lat, st.avgLatencyMs);
    }
    if (evt.type === 'event') {
      const m = evt.data;
      // Normalize to role ids
      const roleId =
        m.service === 'api' ? 'api-gateway' :
        m.service === 'eventstore' ? 'event-store' :
        m.service === 'tick' ? 'tick-engine' :
        m.service === 'governance' ? 'governance' : m.service;

      // Update node metrics
      const n = world.upsertNode(roleId, { role: m.service, name: roleId });
      if (m.metrics) {
        n.latencyMs = m.metrics.latencyMs ?? n.latencyMs;
        n.errorRate = m.metrics.errorRate ?? n.errorRate;
        n.load = m.metrics.throughput ?? n.load;
      }

      // Guess edges by topic or pairings
      const topic = m.topic || 'events';
      const target = topic.includes('audit') ? 'governance' : topic.includes('tick') || topic.includes('stream') ? 'tick-engine' : 'event-store';
      const edgeId = `${roleId}->${target}`;
      const e = world.upsertEdge(edgeId, { a: roleId, b: target, topic });
      if (m.metrics) {
        e.latencyMs = m.metrics.latencyMs ?? e.latencyMs;
        e.throughput = m.metrics.throughput ?? e.throughput;
        e.activity = 1.0;
      }

      // Visual effects: spawn message along edge
      fx.emitMessage(edgeId, m);
    }
  });

  // Resize handling
  const onResize = () => {
    const w = container.clientWidth, h = container.clientHeight;
    camera.aspect = w/h; camera.updateProjectionMatrix();
    renderer.setSize(w,h,false);
  };
  window.addEventListener('resize', onResize);

  // Main loop
  let last = nowMs(); let running = true; let hudVisible = true; let labelsEnabled = true; let particlesEnabled = cfg.view.particles.enabled; let autoLayout = cfg.graph.autoLayout;
  function frame() {
    if (!running) return;
    const t = nowMs();
    const dt = Math.min((t - last)/1000, cfg.graph.maxDt);
    last = t;

    layout.update(dt, autoLayout);
    view.update(dt, { labels: labelsEnabled });
    fx.update(dt, particlesEnabled);

    renderer.render(scene, camera);

    // UI stats
    const stats = data.getStats();
    if (ui.fps) ui.fps.textContent = `FPS: ${Math.round(1/Math.max(0.001, dt))}`;
    if (ui.tp) ui.tp.textContent = `Msgs/s: ${stats.avgThroughput}`;
    if (ui.lat) setLatency(ui.lat, stats.avgLatencyMs);

    controls.update();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  data.connect();

  function setConnState(el, state, mock=false) {
    el.classList.remove('ok','warn','err');
    if (state === 'open') { el.classList.add('ok'); el.textContent = mock ? 'Mock Connected' : 'Connected'; }
    else if (state === 'closed') { el.classList.add('warn'); el.textContent = 'Disconnected'; }
    else { el.classList.add('warn'); el.textContent = 'Connecting...'; }
  }
  function setLatency(el, ms) {
    const th = cfg.thresholds;
    el.classList.remove('ok','warn','err');
    const state = ms >= th.latencyErrorMs ? 'err' : ms >= th.latencyWarnMs ? 'warn' : 'ok';
    el.classList.add(state); el.textContent = `Latency: ${ms} ms`;
  }

  // Public API for UI toggles
  return {
    setParticlesEnabled(v){ particlesEnabled = v; },
    setLabelsEnabled(v){ labelsEnabled = v; },
    setAutoLayout(v){ autoLayout = v; },
    setMockMode(v){ data.setMock(v); },
    toggleHUD(){ hudVisible = !hudVisible; document.getElementById('hud').style.display = hudVisible ? 'block':'none'; },
    pauseResume(){ running = !running; if (running) { last = nowMs(); requestAnimationFrame(frame);} },
  };
}
