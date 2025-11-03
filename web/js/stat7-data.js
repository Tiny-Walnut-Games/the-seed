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
      
      // Set a connection timeout (2 seconds) since browsers don't timeout WebSocket connections
      // This allows fast fallback to mock mode if the real server isn't available
      let connectionTimeout = setTimeout(() => {
        if (this.websocket && this.websocket.readyState === WebSocket.CONNECTING) {
          console.warn('🔌 DataService: WebSocket connection timeout (2s). Closing connection.');
          this.websocket.close();
          this.connectionState = 'closed';
          this.emitConnectionEvent('closed', false);
          this.attemptReconnect();
        }
      }, 2000);

      this.websocket.onopen = () => {
        clearTimeout(connectionTimeout);
        console.log('🔌 DataService: Connected to WebSocket', wsUrl);
        this.connectionState = 'open';
        this.stats.reconnectAttempts = 0;
        this.emitConnectionEvent('open', false);
      };

      this.websocket.onmessage = (evt) => {
        this.onWebSocketMessage(evt.data);
      };

      this.websocket.onclose = () => {
        clearTimeout(connectionTimeout);
        console.log('🔌 DataService: Disconnected from WebSocket');
        this.connectionState = 'closed';
        this.emitConnectionEvent('closed', false);
        this.attemptReconnect();
      };

      this.websocket.onerror = (error) => {
        clearTimeout(connectionTimeout);
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
    
    // Update checkbox UI to reflect mock mode state
    const mockToggle = document.getElementById('toggleMock');
    if (mockToggle) {
      mockToggle.checked = true;
      console.log('🎭 DataService: Updated mock toggle checkbox');
    } else {
      console.warn('🎭 DataService: Mock toggle checkbox not found in DOM');
    }

    // Start generating synthetic events
    if (!this.mockTimer) {
      this.mockTimer = setInterval(() => {
        this.generateMockEvent();
      }, this.mockEventInterval);
      console.log(`🎭 DataService: Started mock event generation (interval: ${this.mockEventInterval}ms)`);
    }
  }

  /**
   * Generate a synthetic event for demo purposes.
   * Generates either STAT7 entities (50%) or service metrics (50%).
   */
  generateMockEvent() {
    const now = Date.now();
    const rand = Math.random();

    // 60% chance: generate STAT7 entity event
    if (rand < 0.6) {
      const realms = ['data', 'narrative', 'system', 'faculty', 'event', 'pattern', 'void'];
      const realm = realms[Math.floor(Math.random() * realms.length)];
      const entityTypes = ['node', 'nexus', 'beacon', 'echo', 'probe'];
      const entityType = entityTypes[Math.floor(Math.random() * entityTypes.length)];
      
      const evt = {
        event_type: 'bitchain_created',
        timestamp: now,
        data: {
          address: `entity_${now}_${Math.random().toString(36).substr(2, 9)}`,
          entity_type: entityType,
          realm,
          coordinates: {
            realm,
            lineage: `lineage_${Math.random().toString(36).substr(2, 9)}`,
            adjacency: [],
            horizon: Math.random() * 3,
            resonance: Math.random(),
            velocity: Math.random() * 2 - 1,
            density: 0.3 + Math.random() * 1.7,
          },
        },
        metadata: {
          color: this.getRealmColor(realm),
        },
      };
      this.onDataEvent(evt);
    } else {
      // 40% chance: generate service metrics event (for backward compat)
      const services = ['api', 'eventstore', 'tick', 'governance'];
      const topics = ['events', 'stream', 'audit'];
      const service = services[Math.floor(Math.random() * services.length)];
      const topic = topics[Math.floor(Math.random() * topics.length)];

      const evt = {
        timestamp: now,
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
  }

  /**
   * Get color for a realm.
   */
  getRealmColor(realm) {
    const colors = {
      'data': 0x64B5F6,      // Blue
      'narrative': 0xFFD54F,  // Yellow
      'system': 0xEF5350,     // Red
      'faculty': 0x81C784,    // Green
      'event': 0xBA68C8,      // Purple
      'pattern': 0xFFB74D,    // Orange
      'void': 0x757575,       // Gray
    };
    return colors[realm] || 0xcccccc;
  }

  /**
   * Handle incoming WebSocket message (real backend).
   * Supports both STAT7 bitchain events and legacy service metrics events.
   */
  onWebSocketMessage(data) {
    try {
      const msg = JSON.parse(data);
      const receivedTime = Date.now();

      // Track stats
      this.stats.eventsReceived++;
      this.stats.throughputWindow.push(receivedTime);
      this.updateThroughputStats();

      // Detect event type and normalize appropriately
      let evt;
      
      if (msg.event_type === 'bitchain_created' || (msg.data && msg.data.coordinates)) {
        // STAT7 bitchain event - pass through with minimal normalization
        evt = {
          type: 'stat7_entity',
          event_type: msg.event_type,
          timestamp: msg.timestamp || receivedTime,
          data: msg.data || {},
          metadata: msg.metadata || {},
          experiment_id: msg.experiment_id,
          receivedAt: receivedTime,
        };
      } else {
        // Legacy service metrics event
        evt = {
          type: 'service_metric',
          timestamp: msg.timestamp || receivedTime,
          service: msg.service || 'unknown',
          topic: msg.topic || 'events',
          metrics: msg.metrics || {},
        };
      }

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
    const receivedTime = Date.now();

    // Track stats
    this.stats.eventsReceived++;
    this.stats.throughputWindow.push(receivedTime);
    this.updateThroughputStats();

    // Normalize the event to standard format
    let normalizedEvt;
    
    if (evt.event_type === 'bitchain_created' || (evt.data && evt.data.coordinates)) {
      // STAT7 bitchain event - normalize to standard format
      normalizedEvt = {
        type: 'stat7_entity',
        event_type: evt.event_type,
        timestamp: evt.timestamp || receivedTime,
        data: evt.data || {},
        metadata: evt.metadata || {},
        experiment_id: evt.experiment_id,
        receivedAt: receivedTime,
      };
      // DEBUG: Log entity event normalization
      if (window.__stat7Debug) {
        console.log('[STAT7 DATA] Entity event normalized:', {
          entityType: normalizedEvt.data.entity_type,
          realm: normalizedEvt.data.realm,
          address: normalizedEvt.data.address,
          hasCoordinates: !!normalizedEvt.data.coordinates,
        });
      }
    } else if (evt.service && evt.metrics) {
      // Legacy service metrics event
      normalizedEvt = {
        type: 'service_metric',
        timestamp: evt.timestamp || receivedTime,
        service: evt.service || 'unknown',
        topic: evt.topic || 'events',
        metrics: evt.metrics || {},
      };
    } else {
      // Unknown event type - pass through
      normalizedEvt = evt;
    }

    // Queue event for tick-aligned processing (prevents race conditions)
    this.eventQueue.push({
      receivedAt: now,
      data: normalizedEvt,
    });

    // If we've crossed a tick boundary, emit all queued events
    if (now - this.lastTickTime >= this.tickIntervalMs) {
      this.flushEventQueue();
      this.lastTickTime = now;
    }

    // Also emit immediately for real-time responsiveness (UI updates)
    this.emitDataEvent(normalizedEvt);
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
   * Events are passed directly (not wrapped) so listeners can check evt.type === 'stat7_entity' etc.
   */
  emitDataEvent(evt) {
    this.subscribers.forEach((cb) => cb(evt));
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
        `🔌 DataService: Max reconnection attempts reached (${this.stats.reconnectAttempts}/${this.stats.maxReconnectAttempts}). Falling back to mock mode for visualization.`
      );
      // Auto-enable mock mode after connection failures
      console.log('🎭 DataService: ✓✓✓ AUTOMATICALLY ENABLING MOCK MODE ✓✓✓');
      this.setupMockMode();
      this.emitConnectionEvent('open', true);
      console.log('🎭 DataService: Mock mode fallback complete');
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
   * Request narration for a specific entity via HTTP API.
   * @param {string} entityId - The entity ID to get narration for
   * @param {object} entityData - Entity metadata (type, realm, coordinates)
   * @param {function} callback - Callback: (narration) => void
   */
  async requestEntityNarration(entityId, entityData = {}, callback) {
    try {
      const apiUrl = this.cfg.apiUrl || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/query/entity-narration`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Include auth token if available
          'Authorization': localStorage.getItem('authToken') || '',
        },
        body: JSON.stringify({
          entity_id: entityId,
          entity_type: entityData.entity_type || 'unknown',
          realm: entityData.realm || 'void',
          coordinates: entityData.coordinates || {},
        }),
      });

      if (!response.ok) {
        console.error(`🔌 DataService: Narration request failed: ${response.status}`);
        if (callback) callback(null);
        return;
      }

      const data = await response.json();
      console.log(`📖 DataService: Narration received for ${entityId}:`, data);
      
      if (callback) {
        callback(data.narration);
      }

      // Emit as event for subscribers to handle
      this.emitDataEvent({
        type: 'entity_narration',
        entity_id: entityId,
        narration: data.narration,
        source: data.source,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.error('🔌 DataService: Error requesting narration:', error);
      if (callback) callback(null);
    }
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