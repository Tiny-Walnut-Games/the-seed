/**
 * DataService: Event bridge between WebSocket and tick-aligned world state.
 *
 * Mental model:
 * - Connects to real WebSocket server OR generates mock events at tick-aligned intervals.
 * - Queues events for processing within tick cycles (100ms).
 * - Tracks latency, throughput, and connection stats.
 * - Emits normalized events to subscriber callbacks (on event).
 * - Respects deterministic timing to avoid race conditions with visualization loop.
 */

export class DataService {
  constructor(cfg) {
    this.cfg = cfg;
    this.websocket = null;
    this.connectionState = 'closed'; // 'open', 'closed', 'connecting'
    this.mockMode = false;
    this.mockEventInterval = cfg.mockEventIntervalMs || 150; // Generate event every 150ms (slightly off-tick)
    this.lastMockEventTime = 0;

    // Event callbacks registered by consumers
    this.subscribers = [];

    // Stats tracking
    this.stats = {
      eventsReceived: 0,
      eventsSent: 0,
      totalLatencyMs: 0,
      latencyCount: 0,
      avgLatencyMs: 0,
      avgThroughput: 0, // msgs/s
      throughputWindow: [], // Recent message timestamps for throughput calc
      reconnectAttempts: 0,
      maxReconnectAttempts: cfg.maxReconnectAttempts || 5,
      reconnectDelayMs: cfg.reconnectDelayMs || 2000,
    };

    // Tick-aligned event queuing
    this.tickIntervalMs = cfg.tickIntervalMs || 100;
    this.eventQueue = [];
    this.lastTickTime = Date.now();
  }

  /**
   * Register a callback: (event) => void
   * Events: { type: 'connection', state, mock }
   *         { type: 'event', data }
   */
  on(callback) {
    if (typeof callback === 'function') {
      this.subscribers.push(callback);
    }
  }

  /**
   * Initiate connection (real WebSocket or mock mode).
   */
  async connect() {
    if (this.mockMode) {
      this.setupMockMode();
    } else {
      this.setupWebSocket();
    }
  }

  /**
   * Enable/disable mock mode.
   */
  setMock(enabled) {
    this.mockMode = enabled;
    if (enabled && this.websocket) {
      this.websocket.close();
      this.websocket = null;
      this.setupMockMode();
      this.emitConnectionEvent('open', true);
    } else if (!enabled && !this.websocket) {
      this.setupWebSocket();
    }
  }

  /**
   * Setup real WebSocket connection to stat7 backend.
   */
  setupWebSocket() {
    this.connectionState = 'connecting';
    this.emitConnectionEvent('connecting', false);

    try {
      const wsUrl = this.cfg.websocketUrl || 'ws://localhost:8765';
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('🔌 DataService: Connected to WebSocket', wsUrl);
        this.connectionState = 'open';
        this.stats.reconnectAttempts = 0;
        this.emitConnectionEvent('open', false);
      };

      this.websocket.onmessage = (evt) => {
        this.onWebSocketMessage(evt.data);
      };

      this.websocket.onclose = () => {
        console.log('🔌 DataService: Disconnected from WebSocket');
        this.connectionState = 'closed';
        this.emitConnectionEvent('closed', false);
        this.attemptReconnect();
      };

      this.websocket.onerror = (error) => {
        console.error('🔌 DataService: WebSocket error:', error);
        this.connectionState = 'closed';
        this.emitConnectionEvent('closed', false);
      };
    } catch (error) {
      console.error('🔌 DataService: Failed to setup WebSocket:', error);
      this.connectionState = 'closed';
      this.emitConnectionEvent('closed', false);
      this.attemptReconnect();
    }
  }

  /**
   * Setup mock event generation for testing/demo.
   */
  setupMockMode() {
    console.log('🎭 DataService: Mock mode enabled');
    this.connectionState = 'open';
    this.mockMode = true;

    // Start generating synthetic events
    if (!this.mockTimer) {
      this.mockTimer = setInterval(() => {
        this.generateMockEvent();
      }, this.mockEventInterval);
    }
  }

  /**
   * Generate a synthetic event for demo purposes.
   */
  generateMockEvent() {
    const services = ['api', 'eventstore', 'tick', 'governance'];
    const topics = ['events', 'stream', 'audit'];
    const service = services[Math.floor(Math.random() * services.length)];
    const topic = topics[Math.floor(Math.random() * topics.length)];

    const evt = {
      timestamp: Date.now(),
      service,
      topic,
      metrics: {
        latencyMs: Math.random() * 50,
        errorRate: Math.random() * 0.1,
        throughput: 100 + Math.random() * 50,
      },
    };

    this.onDataEvent(evt);
  }

  /**
   * Handle incoming WebSocket message (real backend).
   */
  onWebSocketMessage(data) {
    try {
      const msg = JSON.parse(data);
      const receivedTime = Date.now();

      // Track stats
      this.stats.eventsReceived++;
      this.stats.throughputWindow.push(receivedTime);
      this.updateThroughputStats();

      // Normalize message to data event
      const evt = {
        timestamp: msg.timestamp || receivedTime,
        service: msg.service || 'unknown',
        topic: msg.topic || 'events',
        metrics: msg.metrics || {},
      };

      // Track latency if server provided it
      if (msg.server_time) {
        const latency = receivedTime - msg.server_time;
        this.stats.totalLatencyMs += latency;
        this.stats.latencyCount++;
        this.stats.avgLatencyMs = Math.round(
          this.stats.totalLatencyMs / this.stats.latencyCount
        );
      }

      this.onDataEvent(evt);
    } catch (error) {
      console.error('🔌 DataService: Error parsing WebSocket message:', error);
    }
  }

  /**
   * Process a data event: normalize, queue, emit to subscribers.
   */
  onDataEvent(evt) {
    const now = Date.now();

    // Queue event for tick-aligned processing (prevents race conditions)
    this.eventQueue.push({
      receivedAt: now,
      data: evt,
    });

    // If we've crossed a tick boundary, emit all queued events
    if (now - this.lastTickTime >= this.tickIntervalMs) {
      this.flushEventQueue();
      this.lastTickTime = now;
    }

    // Also emit immediately for real-time responsiveness (UI updates)
    this.emitDataEvent(evt);
  }

  /**
   * Flush queued events at tick boundary.
   */
  flushEventQueue() {
    while (this.eventQueue.length > 0) {
      const item = this.eventQueue.shift();
      this.emitDataEvent(item.data);
    }
  }

  /**
   * Emit an event to all subscribers.
   */
  emitDataEvent(evt) {
    const event = {
      type: 'event',
      data: evt,
    };
    this.subscribers.forEach((cb) => cb(event));
  }

  /**
   * Emit connection state change to subscribers.
   */
  emitConnectionEvent(state, mock = false) {
    const event = {
      type: 'connection',
      state,
      mock,
    };
    this.subscribers.forEach((cb) => cb(event));
  }

  /**
   * Attempt to reconnect on WebSocket close.
   */
  attemptReconnect() {
    if (this.stats.reconnectAttempts < this.stats.maxReconnectAttempts) {
      this.stats.reconnectAttempts++;
      const delay = this.stats.reconnectDelayMs * this.stats.reconnectAttempts;
      console.log(
        `🔌 DataService: Reconnect attempt ${this.stats.reconnectAttempts}/${this.stats.maxReconnectAttempts} in ${delay}ms`
      );

      setTimeout(() => {
        this.setupWebSocket();
      }, delay);
    } else {
      console.error(
        '🔌 DataService: Max reconnection attempts reached. Switch to mock mode or check server.'
      );
      this.emitConnectionEvent('closed', false);
    }
  }

  /**
   * Update throughput stats (rolling window: last 5 seconds).
   */
  updateThroughputStats() {
    const now = Date.now();
    const fiveSecondsAgo = now - 5000;

    // Remove old events from window
    this.stats.throughputWindow = this.stats.throughputWindow.filter(
      (ts) => ts > fiveSecondsAgo
    );

    // Calculate msgs/sec
    const windowDurationSec = 5;
    this.stats.avgThroughput = Math.round(
      this.stats.throughputWindow.length / windowDurationSec
    );
  }

  /**
   * Get current stats snapshot.
   */
  getStats() {
    return {
      avgLatencyMs: this.stats.avgLatencyMs,
      avgThroughput: this.stats.avgThroughput,
      eventsReceived: this.stats.eventsReceived,
      connectionState: this.connectionState,
    };
  }

  /**
   * Cleanup: disconnect and stop timers.
   */
  disconnect() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    if (this.mockTimer) {
      clearInterval(this.mockTimer);
      this.mockTimer = null;
    }
  }
}