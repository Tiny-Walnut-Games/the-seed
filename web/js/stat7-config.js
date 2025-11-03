// Configuration for STAT7 Visualizer
export const Config = {
  title: 'STAT7 Visualizer',
  websocketUrl: (location.protocol === 'https:' ? 'wss://' : 'ws://') + (location.hostname || 'localhost') + ':8000/ws',
  tickIntervalMs: 100,
  mockEventIntervalMs: 150,
  maxReconnectAttempts: 5,
  reconnectDelayMs: 2000,
  websocket: {
    retryBackoffMs: [500, 1000, 2000, 5000, 10000],
    heartbeatMs: 10000,
    handshakeTimeoutMs: 5000,
  },
  graph: {
    autoLayout: true,
    repel: 1200,
    spring: 0.06,
    damping: 0.85,
    edgeLen: 200,
    maxDt: 0.033,
  },
  view: {
    background: 0x0b0e13,
    palette: {
      api: 0x80cbc4,
      eventstore: 0x82b1ff,
      tick: 0xa5d6a7,
      governance: 0xffab91,
      link: 0x546e7a,
      linkActive: 0xb0bec5,
      text: 0xcfd8dc,
      danger: 0xef9a9a,
      warn: 0xffe082,
      ok: 0xa5d6a7,
    },
    node: {
      baseSize: 16,
      scaleByLoad: true,
      halo: true,
    },
    particles: {
      enabled: true,
      pool: 2048,
      speed: 280,
      size: 5,
      decayMs: 1200,
    },
    labels: true,
  },
  roles: {
    API_GATEWAY: 'api',
    EVENT_STORE: 'eventstore',
    TICK_ENGINE: 'tick',
    GOVERNANCE: 'governance',
  },
  thresholds: {
    throughputHigh: 200,
    latencyWarnMs: 120,
    latencyErrorMs: 300,
    errorRateWarn: 0.02,
    errorRateError: 0.05,
  }
};
