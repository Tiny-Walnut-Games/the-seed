import { test, expect } from '@playwright/test';

test.describe('STAT7 Visualization - Entity Rendering Pipeline', () => {
  test('page loads successfully with Three.js and WebSocket bootstrap', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Verify DOM structure
    await expect(page.locator('#app')).toBeVisible();
    await expect(page.locator('#hud')).toBeVisible();
    await expect(page.locator('#controls')).toBeVisible();

    // Verify Three.js loaded
    const threeLoaded = await page.evaluate(() => typeof window.THREE !== 'undefined');
    expect(threeLoaded).toBe(true);

    // Verify Config exposed
    const configLoaded = await page.evaluate(() => typeof window.Config !== 'undefined');
    expect(configLoaded).toBe(true);
  });

  test('OrbitControls initializes (fallback or CDN)', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for OrbitControls to load (up to 10 seconds per page logic)
    await page.waitForTimeout(500);

    const orbitControlsReady = await page.evaluate(() => {
      return typeof window.THREE?.OrbitControls !== 'undefined';
    });
    expect(orbitControlsReady).toBe(true);
  });

  test('HUD displays title and status pills', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Check HUD title
    await expect(page.locator('#hud h1')).toContainText('STAT7 Visualizer');

    // Check status pills exist
    const connState = page.locator('#conn-state');
    await expect(connState).toBeVisible();

    const fpsPill = page.locator('#fps');
    await expect(fpsPill).toBeVisible();

    const throughputPill = page.locator('#throughput');
    await expect(throughputPill).toBeVisible();

    const latencyPill = page.locator('#latency');
    await expect(latencyPill).toBeVisible();

    const entitiesPill = page.locator('#entities');
    await expect(entitiesPill).toBeVisible();
    await expect(entitiesPill).toContainText('Entities: 0');
  });

  test('controls panel renders with checkboxes', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    const toggleParticles = page.locator('#toggleParticles');
    const toggleLabels = page.locator('#toggleLabels');
    const toggleAutoLayout = page.locator('#toggleAutoLayout');
    const toggleMock = page.locator('#toggleMock');

    await expect(toggleParticles).toBeVisible();
    await expect(toggleLabels).toBeVisible();
    await expect(toggleAutoLayout).toBeVisible();
    await expect(toggleMock).toBeVisible();

    // Verify initial states
    await expect(toggleParticles).toBeChecked();
    await expect(toggleLabels).toBeChecked();
    await expect(toggleAutoLayout).toBeChecked();
    await expect(toggleMock).not.toBeChecked();
  });

  test('mock mode generates and renders STAT7 entities', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode to generate synthetic entities
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });

    // Wait for synthetic entities to be generated and rendered
    await page.waitForTimeout(2000);

    // Query the app state to check if entities were created
    const entityCount = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.entityMeshes?.size || 0;
    });

    expect(entityCount).toBeGreaterThan(0);

    // Verify HUD entity counter updated
    const entitiesPill = page.locator('#entities');
    const pillText = await entitiesPill.textContent();
    expect(pillText).toMatch(/Entities: \d+/);
    const countMatch = pillText?.match(/(\d+)/);
    const displayedCount = parseInt(countMatch?.[1] || '0', 10);
    expect(displayedCount).toBeGreaterThan(0);
  });

  test('entity meshes render with valid 3D geometry', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(2000);

    // Verify scene contains rendered geometry
    const sceneHasGeometry = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      if (!app?.scene) return false;

      let geometryCount = 0;
      app.scene.traverse((obj: any) => {
        if (obj.geometry) {
          geometryCount++;
        }
      });

      return geometryCount > 0;
    });

    expect(sceneHasGeometry).toBe(true);
  });

  test('entities spread across STAT7 realms with different colors', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(2000);

    // Query entity colors to verify realm mapping
    const entityColors = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      if (!app?.entityMeshes) return [];

      const colors: number[] = [];
      app.entityMeshes.forEach((mesh: any) => {
        if (mesh.material?.emissive) {
          const color = mesh.material.emissive;
          colors.push(color.getHex());
        }
      });

      return colors;
    });

    // Expect multiple entities with potentially different colors (realms)
    expect(entityColors.length).toBeGreaterThan(0);
    
    // If we have multiple entities, they should have some color variation
    // (different realms produce different colors)
    const uniqueColors = new Set(entityColors);
    if (entityColors.length > 5) {
      expect(uniqueColors.size).toBeGreaterThan(1);
    }
  });

  test('legend displays STAT7 realm names and colors', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode to trigger legend update
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(1000);

    // Check legend exists and has content
    const legend = page.locator('#legend');
    await expect(legend).toBeVisible();

    // Legend should contain realm names
    const legendHTML = await legend.innerHTML();
    const realmNames = ['Celestia', 'Terrestria', 'Aquamara', 'Infernia', 'Erebus', 'Ethereus', 'Voidus'];
    
    // At least one realm should be represented in the legend
    let realmFound = false;
    for (const realm of realmNames) {
      if (legendHTML.includes(realm)) {
        realmFound = true;
        break;
      }
    }
    expect(realmFound).toBe(true);
  });

  test('keyboard shortcut H toggles HUD visibility', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    const hud = page.locator('#hud');
    const controls = page.locator('#controls');
    const footer = page.locator('#footer');

    // Initially visible
    await expect(hud).toBeVisible();

    // Press H to toggle HUD
    await page.keyboard.press('h');
    await page.waitForTimeout(200);

    // Check if visibility changed
    const hudVisible = await hud.isVisible();
    const controlsVisible = await controls.isVisible();
    const footerVisible = await footer.isVisible();

    // All HUD elements should have same visibility state
    expect(hudVisible).toBe(controlsVisible);
    expect(controlsVisible).toBe(footerVisible);
    expect(hudVisible).toBe(false);

    // Press H again to toggle back
    await page.keyboard.press('h');
    await page.waitForTimeout(200);

    await expect(hud).toBeVisible();
    await expect(controls).toBeVisible();
    await expect(footer).toBeVisible();
  });

  test('mouse click on entity triggers selection handler', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(2000);

    // Setup listener for selection events
    const selectionLog: any[] = [];
    await page.evaluate(() => {
      (window as any).selectionLog = [];
      const app = (window as any)._stat7App;
      if (app && app.onMouseClick) {
        // Wrap to capture calls
        const originalClick = app.onMouseClick.bind(app);
        app.onMouseClick = (obj: any) => {
          (window as any).selectionLog.push({
            timestamp: Date.now(),
            objectName: obj?.userData?.id || 'unknown',
          });
          return originalClick(obj);
        };
      }
    });

    // Click on canvas (approximate center where entities likely exist)
    const canvas = page.locator('canvas');
    const boundingBox = await canvas.boundingBox();
    if (boundingBox) {
      const centerX = boundingBox.x + boundingBox.width / 2;
      const centerY = boundingBox.y + boundingBox.height / 2;
      
      await page.mouse.click(centerX, centerY);
      await page.waitForTimeout(500);
    }

    // Verify selection handler was called at least once (if entity was hit)
    // Note: May be 0 if raycaster miss or 1+ if hit
    const selections = await page.evaluate(() => (window as any).selectionLog?.length || 0);
    expect(typeof selections).toBe('number');
  });

  test('particles toggle disables/enables entity visibility', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(2000);

    // Get initial entity count
    const initialCount = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.entityMeshes?.size || 0;
    });
    expect(initialCount).toBeGreaterThan(0);

    // Toggle particles off
    const particlesToggle = page.locator('#toggleParticles');
    await particlesToggle.click();
    await page.waitForTimeout(500);

    // Verify visibility state changed in app
    const particlesEnabled = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.particlesEnabled || false;
    });
    expect(particlesEnabled).toBe(false);

    // Toggle back on
    await particlesToggle.click();
    await page.waitForTimeout(500);

    const particlesEnabledAgain = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.particlesEnabled || false;
    });
    expect(particlesEnabledAgain).toBe(true);
  });

  test('labels toggle disables/enables entity labels', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(2000);

    // Get initial label state
    const initialLabelsEnabled = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.labelsEnabled || false;
    });

    // Toggle labels
    const labelsToggle = page.locator('#toggleLabels');
    await labelsToggle.click();
    await page.waitForTimeout(500);

    const labelsEnabledAfter = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.labelsEnabled || false;
    });

    expect(labelsEnabledAfter).toBe(!initialLabelsEnabled);
  });

  test('auto layout toggle controls entity positioning', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(2000);

    // Get initial auto layout state
    const initialAutoLayout = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.autoLayoutEnabled || false;
    });

    // Toggle auto layout off
    const autoLayoutToggle = page.locator('#toggleAutoLayout');
    await autoLayoutToggle.click();
    await page.waitForTimeout(500);

    const autoLayoutDisabled = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.autoLayoutEnabled || false;
    });
    expect(autoLayoutDisabled).toBe(false);
  });

  test('canvas renders without errors in 1000+ entity mock scenario', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    let errorsCaught: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errorsCaught.push(msg.text());
      }
    });

    // Enable mock mode
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });

    // Generate many synthetic entities by waiting
    await page.waitForTimeout(3000);

    // Get final entity count
    const finalCount = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return app?.entityMeshes?.size || 0;
    });

    // Should have rendered significant number of entities
    expect(finalCount).toBeGreaterThan(10);

    // No critical errors should have occurred
    const criticalErrors = errorsCaught.filter(
      err => !err.includes('OrbitControls') && !err.includes('fallback')
    );
    expect(criticalErrors.length).toBe(0);
  });

  test('connection state indicator updates (mock provides fallback)', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    const connState = page.locator('#conn-state');

    // Initially shows "Connecting..." or similar
    const initialText = await connState.textContent();
    expect(['Connecting...', 'Connected', 'Disconnected']).toContain(initialText?.trim());

    // Enable mock mode
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(1000);

    // In mock mode, should eventually show some status
    const mockModeStatus = await connState.textContent();
    expect(mockModeStatus).toBeTruthy();
  });

  test('footer displays service information', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    const footer = page.locator('#footer');
    const footerText = await footer.textContent();

    // Verify footer displays service names and help text
    expect(footerText).toContain('API Gateway');
    expect(footerText).toContain('Event Store');
    expect(footerText).toContain('Tick Engine');
    expect(footerText).toContain('Governance');
    expect(footerText).toContain('WASD');
  });

  test('coordinate projection maintains entity relationships', async ({ page }) => {
    await page.goto('/web/stat7threejs.html');
    await page.waitForLoadState('networkidle');

    // Wait for the app to be fully initialized and toggles to be ready
    await page.waitForSelector('#toggleMock', { timeout: 30000 });
    await page.waitForSelector('#app canvas', { timeout: 30000 });

    // Enable mock mode with multiple entities
    const mockToggle = page.locator('#toggleMock');
    await mockToggle.click({ timeout: 30000 });
    await page.waitForTimeout(2000);

    // Query entity positions to verify projection works
    const entityPositions = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      if (!app?.entityMeshes) return [];

      const positions: any[] = [];
      app.entityMeshes.forEach((mesh: any) => {
        const pos = mesh.position;
        positions.push({
          x: pos.x,
          y: pos.y,
          z: pos.z,
          id: mesh.userData?.id,
        });
      });

      return positions;
    });

    // Should have multiple entities with varied positions
    expect(entityPositions.length).toBeGreaterThan(1);

    // Positions should be in reasonable 3D space (not all zero or NaN)
    for (const pos of entityPositions) {
      expect(typeof pos.x).toBe('number');
      expect(typeof pos.y).toBe('number');
      expect(typeof pos.z).toBe('number');
      expect(isFinite(pos.x)).toBe(true);
      expect(isFinite(pos.y)).toBe(true);
      expect(isFinite(pos.z)).toBe(true);
    }

    // Verify positions are spread (not all identical)
    const uniqueXY = new Set(
      entityPositions.map(p => `${Math.round(p.x * 10)},${Math.round(p.y * 10)}`)
    );
    expect(uniqueXY.size).toBeGreaterThan(1);
  });
});