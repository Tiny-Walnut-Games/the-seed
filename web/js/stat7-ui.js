/**
 * STAT7 UI Controller
 * Handles all UI interactions, controls, and user input
 */

class STAT7UIController {
    constructor(core, websocketManager) {
        this.core = core;
        this.websocketManager = websocketManager;
        this.setupControls();
    }

    setupControls() {
        // Projection mode
        document.getElementById('projection-mode').addEventListener('change', (e) => {
            this.core.settings.projectionMode = e.target.value;
            this.updateProjection();
        });

        // Point size
        document.getElementById('point-size').addEventListener('input', (e) => {
            this.core.settings.pointSize = parseFloat(e.target.value);
            document.getElementById('point-size-value').textContent = this.core.settings.pointSize.toFixed(1);
            this.core.updatePointSizes();
        });

        // Animation speed
        document.getElementById('animation-speed').addEventListener('input', (e) => {
            this.core.settings.animationSpeed = parseFloat(e.target.value);
            document.getElementById('speed-value').textContent = this.core.settings.animationSpeed.toFixed(1);
        });

        // Realm filter
        document.getElementById('realm-filter').addEventListener('change', (e) => {
            this.core.settings.realmFilter = new Set(Array.from(e.target.selectedOptions).map(opt => opt.value));
            this.core.updateRealmFilter();
        });

        // Basic buttons
        document.getElementById('reset-camera').addEventListener('click', () => {
            this.core.resetCamera();
        });

        document.getElementById('clear-points').addEventListener('click', () => {
            this.core.clearAllPoints();
        });

        document.getElementById('clear-ghosts').addEventListener('click', () => {
            this.clearGhostEntities();
        });

        // Search functionality
        document.getElementById('search-btn').addEventListener('click', () => {
            this.performSearch();
        });

        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Query functionality
        document.getElementById('query-btn').addEventListener('click', () => {
            this.performNaturalLanguageQuery();
        });

        document.getElementById('query-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.performNaturalLanguageQuery();
            }
        });

        // Experiment controls
        this.setupExperimentControls();

        // Entity click handler
        this.core.renderer.domElement.addEventListener('click', (e) => {
            this.handleEntityClick(e);
        });
    }

    setupExperimentControls() {
        // Individual experiment buttons
        document.querySelectorAll('.experiment-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const expId = e.target.dataset.exp;
                this.toggleExperiment(expId, e.target);
            });
        });

        // Batch controls
        document.getElementById('play-all').addEventListener('click', () => {
            this.playAllExperiments();
        });

        document.getElementById('stop-all').addEventListener('click', () => {
            this.stopAllExperiments();
        });

        document.getElementById('clear-all').addEventListener('click', () => {
            this.clearAllExperiments();
        });

        // Advanced proof controls
        document.getElementById('semantic-fidelity').addEventListener('click', () => {
            this.runSemanticFidelityProof();
        });

        document.getElementById('resilience-test').addEventListener('click', () => {
            this.runResilienceTest();
        });
    }

    updateProjection() {
        // Reproject all points based on new projection mode
        this.core.pointObjects.forEach((point, id) => {
            const coords = point.userData.bitchain.stat7_coordinates;
            const newPosition = this.core.project7DTo3D(coords);
            point.userData.metadata.originalPosition = newPosition.clone();
            point.position.copy(newPosition);
        });
    }

    performSearch() {
        const searchTerm = document.getElementById('search-input').value.toLowerCase();
        const resultsDiv = document.getElementById('search-results');

        if (!searchTerm) {
            resultsDiv.innerHTML = '<span style="color: #888;">Enter a search term</span>';
            return;
        }

        const results = this.core.points.filter(bitchainData => {
            return (bitchainData.id && bitchainData.id.toLowerCase().includes(searchTerm)) ||
                   (bitchainData.entity_type && bitchainData.entity_type.toLowerCase().includes(searchTerm)) ||
                   (bitchainData.realm && bitchainData.realm.toLowerCase().includes(searchTerm)) ||
                   (bitchainData.address && bitchainData.address.toLowerCase().includes(searchTerm));
        });

        resultsDiv.innerHTML = `<span style="color: #3498db;">Found ${results.length} results</span>`;

        if (results.length > 0) {
            resultsDiv.innerHTML += '<div style="margin-top: 5px;">';
            results.slice(0, 5).forEach((result, index) => {
                const point = this.core.pointObjects.get(result.id || result.address);
                if (point) {
                    resultsDiv.innerHTML += `
                        <div style="cursor: pointer; padding: 2px; border-radius: 3px;"
                             onmouseover="this.style.background='#333'"
                             onmouseout="this.style.background='transparent'"
                             onclick="window.stat7Viz.uiController.focusOnEntity('${result.id || result.address}')">
                            ${index + 1}. ${result.entity_type} - ${result.realm} (${result.id ? result.id.substring(0, 8) + '...' : 'No ID'})
                        </div>
                    `;
                }
            });
            resultsDiv.innerHTML += '</div>';
        }

        // Highlight matching entities
        this.highlightSearchResults(results);
    }

    highlightSearchResults(results) {
        // Reset all highlights
        this.core.pointObjects.forEach(point => {
            const material = point.material;
            material.emissiveIntensity = 0.2;
            point.scale.setScalar(1.0);
        });

        // Highlight search results
        results.forEach(result => {
            const point = this.core.pointObjects.get(result.id || result.address);
            if (point) {
                const material = point.material;
                material.emissiveIntensity = 0.6;
                point.scale.setScalar(1.3);
            }
        });
    }

    performNaturalLanguageQuery() {
        const query = document.getElementById('query-input').value.toLowerCase();
        const resultsDiv = document.getElementById('query-results');

        if (!query) {
            resultsDiv.innerHTML = '<span style="color: #888;">Enter a query</span>';
            return;
        }

        // Simple natural language processing
        let filteredPoints = [...this.core.points];

        // Parse realm filters
        const realms = ['data', 'narrative', 'system', 'faculty', 'event', 'pattern', 'void'];
        realms.forEach(realm => {
            if (query.includes(realm)) {
                filteredPoints = filteredPoints.filter(p =>
                    (p.realm && p.realm.toLowerCase() === realm) ||
                    (p.coordinates && p.coordinates.realm === realm)
                );
            }
        });

        // Parse entity type filters
        const types = ['concept', 'artifact', 'agent', 'lineage', 'adjacency', 'horizon', 'fragment'];
        types.forEach(type => {
            if (query.includes(type)) {
                filteredPoints = filteredPoints.filter(p =>
                    p.entity_type && p.entity_type.toLowerCase() === type
                );
            }
        });

        resultsDiv.innerHTML = `<span style="color: #2ecc71;">Query matched ${filteredPoints.length} entities</span>`;

        // Highlight query results
        this.highlightSearchResults(filteredPoints);
    }

    handleEntityClick(event) {
        // Convert mouse position to 3D coordinates
        const mouse = new THREE.Vector2();
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        const raycaster = new THREE.Raycaster();
        raycaster.setFromCamera(mouse, this.core.camera);

        // Check for intersections with point objects
        const intersects = raycaster.intersectObjects(Array.from(this.core.pointObjects.values()));

        if (intersects.length > 0) {
            const clickedPoint = intersects[0].object;
            const bitchainData = clickedPoint.userData.bitchain;
            this.showEntityDetails(bitchainData, clickedPoint);
        }
    }

    showEntityDetails(bitchainData, pointObject) {
        const detailsPanel = document.getElementById('entity-details');
        const coords = bitchainData.coordinates || bitchainData.stat7_coordinates || {};

        // Update title
        document.getElementById('entity-title').textContent =
            `🔮 ${bitchainData.entity_type || 'Entity'} - ${bitchainData.realm || coords.realm || 'Unknown'}`;

        // Basic information
        document.getElementById('entity-basic').innerHTML = `
            <div><strong>ID:</strong> <span style="color: #3498db; font-family: monospace; font-size: 10px;">${bitchainData.id || 'Unknown'}</span></div>
            <div><strong>Type:</strong> <span style="color: #2ecc71;">${bitchainData.entity_type || 'Unknown'}</span></div>
            <div><strong>Realm:</strong> <span style="color: #e74c3c;">${bitchainData.realm || coords.realm || 'Unknown'}</span></div>
            <div><strong>Address:</strong> <span style="color: #f39c12; font-family: monospace; font-size: 10px;">${bitchainData.address || 'Unknown'}</span></div>
            <div><strong>Created:</strong> <span style="color: #9b59b6;">${bitchainData.created_at || 'Unknown'}</span></div>
        `;

        // STAT7 coordinates
        document.getElementById('entity-coordinates').innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 11px;">
                <div><strong>Realm:</strong> ${coords.realm || 'Unknown'}</div>
                <div><strong>Lineage:</strong> ${coords.lineage || 'Unknown'}</div>
                <div><strong>Horizon:</strong> ${coords.horizon || 'Unknown'}</div>
                <div><strong>Resonance:</strong> ${coords.resonance || 'Unknown'}</div>
                <div><strong>Velocity:</strong> ${coords.velocity || 'Unknown'}</div>
                <div><strong>Density:</strong> ${coords.density || 'Unknown'}</div>
            </div>
            ${coords.adjacency ? `
                <div style="margin-top: 10px;">
                    <strong>Adjacency:</strong> ${(coords.adjacency || []).join(', ') || 'None'}
                </div>
            ` : ''}
        `;

        // Narrative payload
        const narrativeContent = this.extractNarrativeContent(bitchainData);
        document.getElementById('entity-narrative').innerHTML = narrativeContent ||
            '<div style="color: #666; font-style: italic;">No narrative content available</div>';

        // Related entities
        const relatedContent = this.findRelatedEntities(bitchainData);
        document.getElementById('entity-related').innerHTML = relatedContent ||
            '<div style="color: #666; font-style: italic;">No related entities found</div>';

        // Show panel
        detailsPanel.style.display = 'block';

        // Highlight selected entity
        this.highlightEntity(pointObject);
    }

    extractNarrativeContent(bitchainData) {
        const state = bitchainData.state || {};
        const content = [];

        // Extract dialogue
        if (state.dialogue) {
            content.push(`
                <div style="margin-bottom: 10px;">
                    <strong style="color: #3498db;">💬 Dialogue:</strong>
                    <div style="background: rgba(52, 152, 219, 0.1); padding: 8px; border-radius: 5px; margin-top: 5px;">
                        ${state.dialogue}
                    </div>
                </div>
            `);
        }

        // Extract narrative text
        if (state.narrative) {
            content.push(`
                <div style="margin-bottom: 10px;">
                    <strong style="color: #e74c3c;">📖 Narrative:</strong>
                    <div style="background: rgba(231, 76, 60, 0.1); padding: 8px; border-radius: 5px; margin-top: 5px;">
                        ${state.narrative}
                    </div>
                </div>
            `);
        }

        // Extract description
        if (state.description) {
            content.push(`
                <div style="margin-bottom: 10px;">
                    <strong style="color: #2ecc71;">📝 Description:</strong>
                    <div style="background: rgba(46, 204, 113, 0.1); padding: 8px; border-radius: 5px; margin-top: 5px;">
                        ${state.description}
                    </div>
                </div>
            `);
        }

        return content.join('');
    }

    findRelatedEntities(bitchainData) {
        const coords = bitchainData.coordinates || bitchainData.stat7_coordinates || {};
        const adjacency = coords.adjacency || [];

        if (adjacency.length === 0) return null;

        const related = this.core.points.filter(p => {
            if (p.id === bitchainData.id) return false;
            return adjacency.includes(p.id) || adjacency.includes(p.address);
        });

        if (related.length === 0) return null;

        return related.slice(0, 5).map(entity => `
            <div style="padding: 5px; background: rgba(255,255,255,0.05); border-radius: 3px; margin-bottom: 5px; cursor: pointer;"
                 onclick="window.stat7Viz.uiController.focusOnEntity('${entity.id || entity.address}')">
                <div style="color: #3498db; font-size: 11px;">${entity.entity_type || 'Unknown'}</div>
                <div style="color: #aaa; font-size: 10px;">${entity.realm || 'Unknown'} - ${(entity.id || '').substring(0, 8)}...</div>
            </div>
        `).join('');
    }

    highlightEntity(pointObject) {
        // Reset previous highlights
        this.core.pointObjects.forEach(point => {
            const material = point.material;
            material.emissiveIntensity = 0.2;
            point.scale.setScalar(1.0);
        });

        // Highlight selected entity
        const material = pointObject.material;
        material.emissiveIntensity = 0.8;
        pointObject.scale.setScalar(1.5);
    }

    focusOnEntity(entityId) {
        const point = this.core.pointObjects.get(entityId);
        if (point) {
            // Move camera to focus on entity
            const targetPosition = point.position.clone();
            targetPosition.z += 20; // Offset camera back

            // Smooth camera transition
            const startPosition = this.core.camera.position.clone();
            const startTime = Date.now();
            const duration = 1000; // 1 second transition

            const animateCamera = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3); // Ease out cubic

                this.core.camera.position.lerpVectors(startPosition, targetPosition, eased);
                this.core.camera.lookAt(point.position);

                if (progress < 1) {
                    requestAnimationFrame(animateCamera);
                } else {
                    // Show entity details when camera arrives
                    const bitchainData = point.userData.bitchain;
                    this.showEntityDetails(bitchainData, point);
                }
            };

            animateCamera();
        }
    }

    clearGhostEntities() {
        console.log('👻 Clearing ghost entities...');

        let ghostCount = 0;
        const validPointIds = new Set(this.core.points.map(p => p.id || p.address));

        // Find and remove ghost entities
        this.core.pointObjects.forEach((point, entityId) => {
            if (!validPointIds.has(entityId)) {
                console.log(`👻 Removing ghost entity: ${entityId}`);
                this.core.scene.remove(point);
                point.geometry.dispose();
                point.material.dispose();
                ghostCount++;
            }
        });

        // Clean up the pointObjects map
        const cleanedPointObjects = new Map();
        this.core.pointObjects.forEach((point, entityId) => {
            if (validPointIds.has(entityId)) {
                cleanedPointObjects.set(entityId, point);
            }
        });
        this.core.pointObjects = cleanedPointObjects;

        // Update stats
        this.core.stats.totalPoints = this.core.pointObjects.size;
        this.core.stats.visiblePoints = this.core.pointObjects.size;

        this.core.updateStats();
        console.log(`✅ Cleared ${ghostCount} ghost entities. ${this.core.pointObjects.size} entities remaining.`);
    }

    // Experiment Control Methods
    toggleExperiment(expId, button) {
        const isActive = button.classList.contains('active');

        if (isActive) {
            // Stop experiment
            button.classList.remove('active');
            this.stopExperiment(expId);
            this.logExperiment(`${expId} stopped`);
        } else {
            // Start experiment
            button.classList.add('active');
            this.startExperiment(expId);
            this.logExperiment(`${expId} started (30s run)`);
        }
    }

    startExperiment(expId) {
        this.core.stats.activeExperiments.add(expId);

        // Send start message to WebSocket server
        this.websocketManager.sendMessage({
            type: 'start_experiment',
            experiment_id: expId,
            duration: 30 // 30 seconds
        });

        // Auto-stop after 30 seconds
        setTimeout(() => {
            if (this.core.stats.activeExperiments.has(expId)) {
                this.stopExperiment(expId);
                const button = document.querySelector(`[data-exp="${expId}"]`);
                if (button) button.classList.remove('active');
                this.logExperiment(`${expId} auto-completed`);
            }
        }, 30000);
    }

    stopExperiment(expId) {
        this.core.stats.activeExperiments.delete(expId);
        this.websocketManager.sendMessage({
            type: 'stop_experiment',
            experiment_id: expId
        });
    }

    playAllExperiments() {
        const buttons = document.querySelectorAll('.experiment-btn');
        buttons.forEach(button => {
            const expId = button.dataset.exp;
            if (!button.classList.contains('active')) {
                button.classList.add('active');
                this.startExperiment(expId);
            }
        });
        this.logExperiment('All experiments started');
    }

    stopAllExperiments() {
        const buttons = document.querySelectorAll('.experiment-btn');
        buttons.forEach(button => {
            button.classList.remove('active');
        });

        this.core.stats.activeExperiments.forEach(expId => {
            this.stopExperiment(expId);
        });

        this.logExperiment('All experiments stopped');
    }

    clearAllExperiments() {
        this.stopAllExperiments();
        this.core.clearAllPoints();
        this.logExperiment('All experiments cleared');
    }

    logExperiment(message) {
        const logDiv = document.getElementById('experiment-log');
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.style.cssText = 'font-size: 11px; margin-bottom: 3px; color: #aaa;';
        logEntry.innerHTML = `<span style="color: #666;">[${timestamp}]</span> ${message}`;

        logDiv.appendChild(logEntry);
        logDiv.scrollTop = logDiv.scrollHeight;

        // Keep only last 10 log entries
        while (logDiv.children.length > 10) {
            logDiv.removeChild(logDiv.firstChild);
        }
    }

    // Advanced Proof Methods
    runSemanticFidelityProof() {
        this.logExperiment('🧠 Starting Semantic Fidelity Proof...');
        this.websocketManager.sendMessage({
            type: 'run_semantic_fidelity_proof',
            sample_size: 200
        });
    }

    runResilienceTest() {
        this.logExperiment('🛡️ Starting Resilience Testing...');
        this.websocketManager.sendMessage({
            type: 'run_resilience_testing',
            sample_size: 150
        });
    }
}
