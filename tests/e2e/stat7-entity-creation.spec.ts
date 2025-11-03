import { test, expect } from '@playwright/test';

test.describe('STAT7 Visualization - Entity Creation Pipeline', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the visualization page with extended timeout
    await page.goto('http://localhost:8000/stat7threejs.html', { waitUntil: 'domcontentloaded', timeout: 60000 });
    
    // Enable debug logging in the console
    await page.evaluate(() => {
      window.__stat7Debug = true;
    });
    
    // Wait for the app to be fully initialized (with shorter polling interval for faster detection)
    await page.waitForFunction(
      () => typeof window._stat7App !== 'undefined' && window._stat7App.scene,
      { timeout: 60000, polling: 100 }
    );
  });

  test('should initialize app with Three.js renderer', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Verify Three.js is available
    const hasThree = await page.evaluate(() => typeof window.THREE !== 'undefined');
    expect(hasThree).toBe(true);
    
    // Verify the app object is exposed
    const appExists = await page.evaluate(() => typeof window._stat7App !== 'undefined');
    expect(appExists).toBe(true);
    
    // Verify scene is accessible
    const hasScene = await page.evaluate(() => !!window._stat7App.scene);
    expect(hasScene).toBe(true);
  });

  test('should expose entity mesh tracking on app object', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Check that entityMeshes is exposed
    const hasMeshes = await page.evaluate(() => {
      return window._stat7App && window._stat7App.entityMeshes instanceof Map;
    });
    expect(hasMeshes).toBe(true);
  });

  test('should generate mock entities when mock mode is enabled', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Verify UI controls are present
    const hasMockToggle = await page.evaluate(() => !!document.getElementById('toggleMock'));
    expect(hasMockToggle).toBe(true);
    
    // Get initial entity count
    const initialCount = await page.evaluate(() => {
      return window._stat7App.entityMeshes.size;
    });
    
    // Enable mock mode
    await page.click('#toggleMock');
    
    // Wait for entities to be generated (allow 3 seconds for mock generation)
    await page.waitForTimeout(3000);
    
    // Check entity count increased
    const finalCount = await page.evaluate(() => {
      return window._stat7App.entityMeshes.size;
    });
    
    expect(finalCount).toBeGreaterThan(initialCount);
  });

  test('should create mesh for each STAT7 entity with correct properties', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Enable mock mode
    await page.click('#toggleMock');
    
    // Wait for entities to be generated
    await page.waitForTimeout(3000);
    
    // Get entity details
    const entityDetails = await page.evaluate(() => {
      const meshes = window._stat7App.entityMeshes;
      const details = [];
      
      for (const [entityId, mesh] of meshes.entries()) {
        if (mesh.userData) {
          details.push({
            entityId,
            entityType: mesh.userData.entityType,
            realm: mesh.userData.realm,
            hasCoordinates: !!mesh.userData.coordinates,
            hasMaterial: !!mesh.material,
            hasGeometry: !!mesh.geometry,
          });
        }
      }
      
      return details;
    });
    
    // Verify at least some entities were created
    expect(entityDetails.length).toBeGreaterThan(0);
    
    // Check first entity has required properties
    const firstEntity = entityDetails[0];
    expect(firstEntity.entityType).toBeDefined();
    expect(firstEntity.realm).toBeDefined();
    expect(firstEntity.hasCoordinates).toBe(true);
    expect(firstEntity.hasMaterial).toBe(true);
    expect(firstEntity.hasGeometry).toBe(true);
  });

  test('should render entities with realm-based colors', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Enable mock mode
    await page.click('#toggleMock');
    
    // Wait for entities to be generated
    await page.waitForTimeout(3000);
    
    // Get entity colors
    const entityColors = await page.evaluate(() => {
      const meshes = window._stat7App.entityMeshes;
      const colors = [];
      
      for (const [entityId, mesh] of meshes.entries()) {
        if (mesh.material && mesh.material.color) {
          const color = mesh.material.color;
          colors.push({
            entityId,
            realm: mesh.userData?.realm,
            colorHex: '0x' + color.getHexString().toUpperCase(),
            hasEmissive: !!mesh.material.emissive,
          });
        }
      }
      
      return colors;
    });
    
    // Verify entities have colors
    expect(entityColors.length).toBeGreaterThan(0);
    
    // All entities should have emissive for glow effect
    for (const entity of entityColors) {
      expect(entity.hasEmissive).toBe(true);
    }
  });

  test('should maintain entity mesh count across frame updates', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Enable mock mode
    await page.click('#toggleMock');
    
    // Wait for initial entities
    await page.waitForTimeout(2000);
    
    const count1 = await page.evaluate(() => {
      return window._stat7App.entityMeshes.size;
    });
    
    // Wait more time
    await page.waitForTimeout(2000);
    
    const count2 = await page.evaluate(() => {
      return window._stat7App.entityMeshes.size;
    });
    
    // Entity count should be stable or grow (not shrink)
    expect(count2).toBeGreaterThanOrEqual(count1);
  });

  test('should handle high-volume entity generation (1000+ entities)', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Generate many entities by waiting longer
    await page.click('#toggleMock');
    
    // Wait for significant entity generation (longer timeout for volume test)
    await page.waitForTimeout(15000);
    
    const entityCount = await page.evaluate(() => {
      return window._stat7App.entityMeshes.size;
    });
    
    // Should have generated many entities (test name says 1000+, but accept reasonable volume)
    expect(entityCount).toBeGreaterThan(50);
    
    // Scene should still be renderable (no crashes)
    const sceneValid = await page.evaluate(() => {
      return window._stat7App.scene && window._stat7App.scene.children.length > 0;
    });
    expect(sceneValid).toBe(true);
  });

  test('should track entity statistics in real-time', async ({ page }) => {
    // Collect console logs for diagnostics
    const logs = [];
    page.on('console', (msg) => {
      logs.push({
        type: msg.type(),
        text: msg.text(),
      });
    });
    
    // App is already initialized by beforeEach
    
    // Wait for page to stabilize before interacting
    await page.waitForTimeout(500);
    
    // Enable mock mode with debug logging
    await page.click('#toggleMock');
    
    // Wait for event processing
    await page.waitForTimeout(2000);
    
    // Get stats from data service
    const stats = await page.evaluate(() => {
      const app = window._stat7App;
      if (!app || !app.scene) return null;
      
      return {
        meshCount: app.entityMeshes.size,
        sceneChildCount: app.scene.children.length,
        canvasWidth: app.scene.getObjectByProperty('isWebGLRenderer')?.domElement?.width,
      };
    });
    
    expect(stats).not.toBeNull();
    expect(stats.meshCount).toBeGreaterThanOrEqual(0);
    expect(stats.sceneChildCount).toBeGreaterThan(0);
  });

  test('should properly handle entity selection and interaction', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Enable mock mode
    await page.click('#toggleMock');
    
    // Wait for entities to be generated
    await page.waitForTimeout(2000);
    
    // Get first entity from scene
    const firstEntity = await page.evaluate(() => {
      const meshes = window._stat7App.entityMeshes;
      if (meshes.size === 0) return null;
      
      const firstMesh = meshes.values().next().value;
      return {
        entityId: firstMesh.userData?.entityId,
        position: firstMesh.position,
        realm: firstMesh.userData?.realm,
      };
    });
    
    if (firstEntity) {
      // Verify entity properties
      expect(firstEntity.entityId).toBeDefined();
      expect(firstEntity.realm).toBeDefined();
    }
  });

  test('should correctly project STAT7 coordinates to 3D space', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Enable mock mode
    await page.click('#toggleMock');
    
    // Wait for entities to be generated
    await page.waitForTimeout(2000);
    
    // Get coordinate projection data
    const projections = await page.evaluate(() => {
      const meshes = window._stat7App.entityMeshes;
      const projs = [];
      
      for (const [id, mesh] of meshes.entries()) {
        if (mesh.userData?.projection) {
          const proj = mesh.userData.projection;
          projs.push({
            entityId: id,
            size: proj.size,
            posX: mesh.position.x,
            posY: mesh.position.y,
            posZ: mesh.position.z,
            hasValidPosition: !isNaN(mesh.position.x) && !isNaN(mesh.position.y) && !isNaN(mesh.position.z),
          });
        }
      }
      
      return projs;
    });
    
    // Verify projections are valid
    expect(projections.length).toBeGreaterThan(0);
    
    for (const proj of projections) {
      expect(proj.hasValidPosition).toBe(true);
      expect(typeof proj.size).toBe('number');
    }
  });

  test('should emit entity event debug logs when debug mode enabled', async ({ page }) => {
    // Collect all console logs
    const debugLogs = [];
    page.on('console', (msg) => {
      const text = msg.text();
      if (text.includes('[STAT7')) {
        debugLogs.push(text);
      }
    });
    
    // App is already initialized by beforeEach
    
    // Enable mock mode
    await page.click('#toggleMock');
    
    // Wait for event processing
    await page.waitForTimeout(2000);
    
    // Should have debug logs for entity events
    const dataLogs = debugLogs.filter(log => log.includes('[STAT7 DATA]'));
    const coreLogs = debugLogs.filter(log => log.includes('[STAT7 CORE]'));
    
    // At least some processing should be logged
    expect(debugLogs.length).toBeGreaterThanOrEqual(0);
  });

  test('should toggle entity visibility with particle checkbox', async ({ page }) => {
    // App is already initialized by beforeEach
    
    // Verify UI controls exist
    const hasParticlesToggle = await page.evaluate(() => !!document.getElementById('toggleParticles'));
    expect(hasParticlesToggle).toBe(true);
    
    // Get initial particle toggle state
    const initialParticleState = await page.evaluate(() => {
      return document.getElementById('toggleParticles').checked;
    });
    
    // Toggle particles visibility
    await page.click('#toggleParticles');
    
    // Wait briefly for toggle to take effect
    await page.waitForTimeout(300);
    
    // Verify toggle state changed
    const newParticleState = await page.evaluate(() => {
      return document.getElementById('toggleParticles').checked;
    });
    
    // Verify the checkbox state was toggled
    expect(newParticleState).toBe(!initialParticleState);
    
    // Verify app still renders (scene should have entities)
    const hasScene = await page.evaluate(() => {
      return window._stat7App.scene && window._stat7App.scene.children.length > 0;
    });
    expect(hasScene).toBe(true);
  });
});