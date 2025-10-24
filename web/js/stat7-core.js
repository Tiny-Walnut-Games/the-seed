/**
 * STAT7 Core Visualization Engine
 * Handles Three.js setup, rendering, and basic entity management
 */

class STAT7Core {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.points = [];
        this.pointObjects = new Map();
        this.stats = {
            totalPoints: 0,
            visiblePoints: 0,
            fps: 0,
            eventsReceived: 0,
            activeExperiments: new Set()
        };
        this.settings = {
            pointSize: 1.0,
            animationSpeed: 1.0,
            projectionMode: '7d-to-3d',
            realmFilter: new Set(['data', 'narrative', 'system', 'faculty', 'event', 'pattern', 'void'])
        };
        this.lastFrameTime = performance.now();
        this.frameCount = 0;

        this.init();
    }

    init() {
        this.setupThreeJS();
        this.setupMouseControls();
        this.animate();
    }

    setupThreeJS() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(50, 50, 50);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: document.getElementById('stat7-canvas'),
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        // Lights
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        this.scene.add(directionalLight);

        // Grid helper
        const gridHelper = new THREE.GridHelper(100, 20, 0x444444, 0x222222);
        this.scene.add(gridHelper);

        // Axes helper
        const axesHelper = new THREE.AxesHelper(20);
        this.scene.add(axesHelper);

        // Handle resize
        window.addEventListener('resize', () => this.onWindowResize());
    }

    setupMouseControls() {
        let mouseDown = false;
        let mouseX = 0;
        let mouseY = 0;
        let rightMouseDown = false;

        this.renderer.domElement.addEventListener('mousedown', (e) => {
            if (e.button === 0) { // Left click
                mouseDown = true;
                mouseX = e.clientX;
                mouseY = e.clientY;
            } else if (e.button === 2) { // Right click
                rightMouseDown = true;
                mouseX = e.clientX;
                mouseY = e.clientY;
            }
        });

        this.renderer.domElement.addEventListener('mouseup', (e) => {
            if (e.button === 0) mouseDown = false;
            else if (e.button === 2) rightMouseDown = false;
        });

        this.renderer.domElement.addEventListener('mousemove', (e) => {
            if (mouseDown) {
                // Rotate camera around origin (left click)
                const deltaX = e.clientX - mouseX;
                const deltaY = e.clientY - mouseY;

                const spherical = new THREE.Spherical();
                spherical.setFromVector3(this.camera.position);
                spherical.theta -= deltaX * 0.01;
                spherical.phi += deltaY * 0.01;
                spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi));

                this.camera.position.setFromSpherical(spherical);
                this.camera.lookAt(0, 0, 0);

                mouseX = e.clientX;
                mouseY = e.clientY;
            } else if (rightMouseDown) {
                // Pan camera (right click)
                const deltaX = (e.clientX - mouseX) * 0.1;
                const deltaY = (e.clientY - mouseY) * 0.1;

                const right = new THREE.Vector3();
                const up = new THREE.Vector3(0, 1, 0);
                right.crossVectors(up, this.camera.position).normalize();

                this.camera.position.add(right.multiplyScalar(-deltaX));
                this.camera.position.add(up.multiplyScalar(deltaY));

                mouseX = e.clientX;
                mouseY = e.clientY;
            }
        });

        // Zoom with mouse wheel
        this.renderer.domElement.addEventListener('wheel', (e) => {
            const scale = e.deltaY > 0 ? 1.1 : 0.9;
            this.camera.position.multiplyScalar(scale);
        });

        // Prevent context menu on right click
        this.renderer.domElement.addEventListener('contextmenu', (e) => {
            e.preventDefault();
        });
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    createPoint(bitchainData) {
        const coords = bitchainData.coordinates || bitchainData.stat7_coordinates || {};
        const position = this.project7DTo3D(coords);

        // Create geometry and material
        const geometry = new THREE.SphereGeometry(0.5, 16, 16);
        const material = new THREE.MeshPhongMaterial({
            color: this.getRealmColor(coords.realm || bitchainData.realm),
            emissive: this.getRealmColor(coords.realm || bitchainData.realm),
            emissiveIntensity: 0.2,
            shininess: 100
        });

        const point = new THREE.Mesh(geometry, material);
        point.position.copy(position);
        point.userData = {
            bitchain: bitchainData,
            metadata: {
                color: this.getRealmColor(coords.realm || bitchainData.realm),
                size: this.getEntitySize(bitchainData.entity_type),
                originalPosition: position.clone(),
                animationOffset: Math.random() * Math.PI * 2
            }
        };

        // Store in map
        const entityId = bitchainData.id || bitchainData.address;
        this.pointObjects.set(entityId, point);
        this.scene.add(point);

        return point;
    }

    project7DTo3D(coords) {
        // Simple 7D to 3D projection
        const x = (coords.lineage || 0) * 0.5;
        const y = (coords.resonance || 0) * 20;
        const z = (coords.velocity || 0) * 10;

        return new THREE.Vector3(x, y, z);
    }

    getRealmColor(realm) {
        const realmColors = {
            'data': 0x3498db,      // Blue
            'narrative': 0xe74c3c, // Red
            'system': 0x2ecc71,     // Green
            'faculty': 0xf39c12,    // Orange
            'event': 0x9b59b6,      // Purple
            'pattern': 0x1abc9c,    // Teal
            'void': 0x34495e,       // Dark gray
        };
        return realmColors[realm] || 0x95a5a6; // Default gray
    }

    getEntitySize(entityType) {
        const entitySizes = {
            'concept': 1.0,
            'artifact': 1.5,
            'agent': 2.0,
            'lineage': 1.2,
            'adjacency': 0.8,
            'horizon': 1.8,
            'fragment': 0.6,
        };
        return entitySizes[entityType] || 1.0;
    }

    updatePointSizes() {
        this.pointObjects.forEach(point => {
            const baseSize = point.userData.metadata.size;
            point.scale.setScalar(this.settings.pointSize);
        });
    }

    updateRealmFilter() {
        let visibleCount = 0;
        this.pointObjects.forEach((point, entityId) => {
            const bitchain = point.userData.bitchain;
            const coords = bitchain.coordinates || bitchain.stat7_coordinates;
            const realm = coords ? coords.realm : (bitchain.realm || 'unknown');
            const visible = this.settings.realmFilter.has(realm);
            point.visible = visible;
            if (visible) visibleCount++;
        });
        this.stats.visiblePoints = visibleCount;
        console.log(`🔍 Realm filter updated: ${visibleCount}/${this.pointObjects.size} entities visible`);
    }

    resetCamera() {
        this.camera.position.set(50, 50, 50);
        this.camera.lookAt(0, 0, 0);
    }

    clearAllPoints() {
        console.log(`🗑️ Clearing ${this.pointObjects.size} point objects and ${this.points.length} data points`);

        // Remove all point objects from scene
        this.pointObjects.forEach((point, id) => {
            this.scene.remove(point);
            point.geometry.dispose();
            point.material.dispose();
        });

        // Clear all collections
        this.pointObjects.clear();
        this.points = [];

        // Reset stats
        this.stats.totalPoints = 0;
        this.stats.visiblePoints = 0;

        console.log('✅ All points cleared successfully');
    }

    updateStats() {
        // Count visible points first
        let visibleCount = 0;
        this.pointObjects.forEach(point => {
            if (point.visible !== false) visibleCount++;  // Default to visible if not set
        });
        this.stats.visiblePoints = visibleCount;

        // Update display
        document.getElementById('total-points').textContent = this.stats.totalPoints;
        document.getElementById('visible-points').textContent = this.stats.visiblePoints;
        document.getElementById('fps').textContent = this.stats.fps.toFixed(1);
        document.getElementById('events-received').textContent = this.stats.eventsReceived;
        document.getElementById('active-experiments').textContent = this.stats.activeExperiments.size;

        console.log(`Stats updated: Total=${this.stats.totalPoints}, Visible=${this.stats.visiblePoints}, Events=${this.stats.eventsReceived}`);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        // Calculate FPS
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastFrameTime;
        this.frameCount++;

        if (this.frameCount % 30 === 0) {
            this.stats.fps = 1000 / deltaTime;
            this.updateStats();
        }

        this.lastFrameTime = currentTime;

        // Animate points
        if (this.settings.animationSpeed > 0) {
            const time = currentTime * 0.001 * this.settings.animationSpeed;

            this.pointObjects.forEach((point, entityId) => {
                if (!point.visible) return;

                // Gentle floating animation
                const offset = point.userData.metadata.animationOffset;
                const floatY = Math.sin(time + offset) * 0.5;
                const floatX = Math.cos(time * 0.7 + offset) * 0.3;

                point.position.x = point.userData.metadata.originalPosition.x + floatX;
                point.position.y = point.userData.metadata.originalPosition.y + floatY;

                // Gentle rotation
                point.rotation.y += 0.01 * this.settings.animationSpeed;
            });
        }

        this.renderer.render(this.scene, this.camera);
    }
}
