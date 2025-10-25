/**
 * STAT7 Main Visualization Class
 * Orchestrates all components and provides the main interface
 */

class STAT7Visualization {
    constructor() {
        this.core = null;
        this.websocketManager = null;
        this.uiController = null;

        this.init();
    }

    init() {
        // Initialize core components
        this.core = new STAT7Core();
        this.websocketManager = new STAT7WebSocketManager(this.core);
        this.uiController = new STAT7UIController(this.core, this.websocketManager);

        // Setup WebSocket connection after a delay
        setTimeout(() => {
            console.log('🔌 Initializing WebSocket connection...');
            this.websocketManager.setupWebSocket();
        }, 2000);

        // Handle DPI scaling and monitor changes
        this.handleDPIAndScaling();
    }

    handleDPIAndScaling() {
        const updatePanelScaling = () => {
            const dpi = window.devicePixelRatio || 1;
            const scale = Math.max(0.7, Math.min(1.3, 1 / dpi));
            const windowWidth = window.innerWidth;

            // Apply scaling to control panels
            const panels = ['controls', 'stats', 'experiment-info'];
            panels.forEach(panelId => {
                const panel = document.getElementById(panelId);
                if (panel) {
                    panel.style.transform = `scale(${scale})`;

                    // Adjust position based on panel type
                    if (panelId === 'controls') {
                        panel.style.top = `${20 / scale}px`;
                        panel.style.left = `${20 / scale}px`;
                    } else if (panelId === 'stats') {
                        panel.style.bottom = `${20 / scale}px`;
                        panel.style.right = `${20 / scale}px`;
                    } else if (panelId === 'experiment-info') {
                        panel.style.top = `${20 / scale}px`;
                        panel.style.right = `${20 / scale}px`;
                    }
                }
            });

            console.log(`DPI: ${dpi}, Scale: ${scale}, Window: ${windowWidth}px`);
        };

        // Initial scaling
        updatePanelScaling();

        // Update on resize
        window.addEventListener('resize', updatePanelScaling);

        // Handle DPI changes (Windows display scaling)
        if (window.matchMedia) {
            window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`).addEventListener('change', updatePanelScaling);
        }
    }

    // Public methods for external access
    closeEntityDetails() {
        const detailsPanel = document.getElementById('entity-details');
        if (detailsPanel) {
            detailsPanel.style.display = 'none';
        }

        // Reset highlights
        this.core.pointObjects.forEach(point => {
            const material = point.material;
            material.emissiveIntensity = 0.2;
            point.scale.setScalar(1.0);
        });
    }

    focusOnEntity(entityId) {
        this.uiController.focusOnEntity(entityId);
    }

    // Cleanup method
    destroy() {
        if (this.websocketManager) {
            this.websocketManager.disconnect();
        }
        if (this.core) {
            this.core.clearAllPoints();
        }
    }
}

// Initialize visualization when page loads
window.addEventListener('DOMContentLoaded', () => {
    window.stat7Viz = new STAT7Visualization();

    // Handle page visibility to pause/resume rendering
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            // Page is hidden, reduce rendering frequency
            if (window.stat7Viz && window.stat7Viz.core) {
                window.stat7Viz.core.settings.animationSpeed = 0;
            }
        } else {
            // Page is visible, restore animation
            if (window.stat7Viz && window.stat7Viz.core) {
                const speedSlider = document.getElementById('animation-speed');
                window.stat7Viz.core.settings.animationSpeed = parseFloat(speedSlider.value);
            }
        }
    });
});

// Handle monitor changes and DPI scaling
window.addEventListener('resize', () => {
    if (window.stat7Viz) {
        window.stat7Viz.handleDPIAndScaling();
    }
});
