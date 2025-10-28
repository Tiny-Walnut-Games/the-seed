/**
 * STAT7 WebSocket Manager
 * Handles WebSocket connections and message processing
 */

class STAT7WebSocketManager {
    constructor(core) {
        this.core = core;
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
    }

    async setupWebSocket() {
        try {
            this.websocket = new WebSocket('ws://localhost:8765');

            this.websocket.onopen = () => {
                console.log('🔌 Connected to STAT7 WebSocket server');
                this.updateConnectionStatus(true);
                this.reconnectAttempts = 0;
            };

            this.websocket.onmessage = (event) => {
                this.handleMessage(event.data);
            };

            this.websocket.onclose = () => {
                console.log('🔌 Disconnected from STAT7 WebSocket server');
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };

            this.websocket.onerror = (error) => {
                console.error('🔌 WebSocket error:', error);
                this.updateConnectionStatus(false);
            };

        } catch (error) {
            console.error('🔌 Failed to setup WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    handleMessage(data) {
        try {
            const event = JSON.parse(data);
            this.core.stats.eventsReceived++;

            switch (event.event_type) {
                case 'bitchain_created':
                    this.handleBitChainCreated(event);
                    break;
                case 'experiment_completed':
                    this.handleExperimentCompleted(event);
                    break;
                default:
                    console.log('📊 Unknown event type:', event.event_type);
            }

        } catch (error) {
            console.error('📊 Error parsing WebSocket message:', error);
        }
    }

    handleBitChainCreated(event) {
        const bitchainData = event.data.bitchain;

        // Add to points array
        this.core.points.push(bitchainData);

        // Create visual representation
        const point = this.core.createPoint(bitchainData);

        // Update stats
        this.core.stats.totalPoints = this.core.pointObjects.size;
        this.core.stats.visiblePoints = this.core.pointObjects.size;

        // Add to active experiments if specified
        if (event.experiment_id) {
            this.core.stats.activeExperiments.add(event.experiment_id);
        }

        console.log(`📊 Created entity: ${bitchainData.entity_type} in ${bitchainData.realm}`);
    }

    handleExperimentCompleted(event) {
        const experimentId = event.experiment_id;
        this.core.stats.activeExperiments.delete(experimentId);

        // Update UI button state
        const button = document.querySelector(`[data-exp="${experimentId}"]`);
        if (button) {
            button.classList.remove('active');
        }

        console.log(`🧪 Experiment ${experimentId} completed`);
    }

    sendMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
            return true;
        } else {
            console.warn('🔌 WebSocket not connected, message not sent:', message);
            return false;
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔌 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

            setTimeout(() => {
                this.setupWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('🔌 Max reconnection attempts reached');
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        const indicatorClass = connected ? 'status-connected' : 'status-disconnected';
        const statusText = connected ? 'Connected' : 'Disconnected';

        statusElement.innerHTML = `<span class="status-indicator ${indicatorClass}"></span>${statusText}`;
    }

    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }
}