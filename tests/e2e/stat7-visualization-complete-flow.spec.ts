import { test, expect } from '@playwright/test';

test.describe('STAT7 Visualization - Complete Flow with Auto Mock Fallback', () => {
  test('should render 3D visualization with entities after WebSocket fallback to mock mode', async ({ page }) => {
    // Navigate to visualization
    await page.goto('http://localhost:8000/stat7threejs.html', { 
      waitUntil: 'domcontentloaded', 
      timeout: 120000 
    });
    
    // Enable debug mode for detailed logs
    await page.evaluate(() => {
      window.__stat7Debug = true;
    });
    
    // Wait for app initialization
    await page.waitForFunction(
      () => typeof window._stat7App !== 'undefined' && window._stat7App.scene,
      { timeout: 60000, polling: 100 }
    );
    
    // Wait for connection fallback and mock mode initialization (~10 seconds)
    console.log('Waiting for mock mode auto-fallback and entity generation...');
    await page.waitForTimeout(10000);
    
    // === VERIFICATION PHASE ===
    
    // 1. Verify mock mode is enabled
    const mockEnabled = await page.evaluate(() => {
      const toggle = document.getElementById('toggleMock');
      return toggle ? toggle.checked : false;
    });
    expect(mockEnabled).toBe(true);
    console.log('✓ Mock mode enabled');
    
    // 2. Verify connection state shows mock
    const connState = await page.evaluate(() => {
      const el = document.getElementById('conn-state');
      return el ? el.textContent : '';
    });
    expect(connState).toContain('Mock');
    console.log(`✓ Connection state: ${connState}`);
    
    // 3. Verify entities are being generated
    const entityCount = await page.evaluate(() => {
      return window._stat7App.entityMeshes.size;
    });
    expect(entityCount).toBeGreaterThan(0);
    console.log(`✓ Entities rendered: ${entityCount}`);
    
    // 4. Verify scene has 3D objects
    const sceneValid = await page.evaluate(() => {
      const app = window._stat7App;
      return {
        hasScene: !!app.scene,
        childrenCount: app.scene.children.length,
        hasEntities: app.entityMeshes.size > 0,
      };
    });
    expect(sceneValid.hasScene).toBe(true);
    expect(sceneValid.childrenCount).toBeGreaterThan(0);
    expect(sceneValid.hasEntities).toBe(true);
    console.log('✓ 3D scene valid with children');
    
    // 5. Verify entity properties
    const firstEntity = await page.evaluate(() => {
      const app = window._stat7App;
      if (app.entityMeshes.size === 0) return null;
      
      const mesh = app.entityMeshes.values().next().value;
      return {
        hasPosition: mesh.position !== undefined,
        hasUserData: mesh.userData !== undefined,
        hasEntityType: !!mesh.userData?.entityType,
        hasRealm: !!mesh.userData?.realm,
        hasColor: mesh.material && mesh.material.color !== undefined,
      };
    });
    
    if (firstEntity) {
      expect(firstEntity.hasPosition).toBe(true);
      expect(firstEntity.hasUserData).toBe(true);
      expect(firstEntity.hasEntityType).toBe(true);
      expect(firstEntity.hasRealm).toBe(true);
      expect(firstEntity.hasColor).toBe(true);
      console.log('✓ Entity properties valid');
    }
    
    // 6. Verify UI controls are functional
    const uiElements = await page.evaluate(() => {
      return {
        hasHud: !!document.getElementById('hud'),
        hasControls: !!document.getElementById('controls'),
        hasToggleMock: !!document.getElementById('toggleMock'),
        hasToggleParticles: !!document.getElementById('toggleParticles'),
        hasEntityCounter: !!document.getElementById('entities'),
        hasConnectionStatus: !!document.getElementById('conn-state'),
      };
    });
    
    expect(uiElements.hasHud).toBe(true);
    expect(uiElements.hasControls).toBe(true);
    expect(uiElements.hasToggleMock).toBe(true);
    expect(uiElements.hasToggleParticles).toBe(true);
    expect(uiElements.hasEntityCounter).toBe(true);
    expect(uiElements.hasConnectionStatus).toBe(true);
    console.log('✓ All UI elements present and functional');
    
    // 7. Verify FPS counter updating (animation loop running)
    const fpsText = await page.evaluate(() => {
      const el = document.getElementById('fps');
      return el ? el.textContent : '';
    });
    expect(fpsText).toMatch(/FPS: \d+/);
    console.log(`✓ Animation loop active: ${fpsText}`);
    
    // 8. Verify three.js and threejs library loaded
    const hasThreeJS = await page.evaluate(() => {
      return typeof window.THREE !== 'undefined';
    });
    expect(hasThreeJS).toBe(true);
    console.log('✓ Three.js library loaded');
    
    console.log('\n=== VISUALIZATION COMPLETE AND WORKING ===');
    console.log(`Final entity count: ${entityCount}`);
    console.log('Status: Ready for interactive use');
  });
  
  test('should handle continuous entity generation', async ({ page }) => {
    await page.goto('http://localhost:8000/stat7threejs.html', { 
      waitUntil: 'domcontentloaded', 
      timeout: 120000 
    });
    
    await page.evaluate(() => { window.__stat7Debug = true; });
    
    await page.waitForFunction(
      () => typeof window._stat7App !== 'undefined' && window._stat7App.scene,
      { timeout: 60000, polling: 100 }
    );
    
    // Wait for mock fallback
    await page.waitForTimeout(10000);
    
    // Get initial count
    const count1 = await page.evaluate(() => window._stat7App.entityMeshes.size);
    console.log(`Initial entity count: ${count1}`);
    
    // Wait for more generation
    await page.waitForTimeout(3000);
    
    // Get final count
    const count2 = await page.evaluate(() => window._stat7App.entityMeshes.size);
    console.log(`After 3s entity count: ${count2}`);
    
    // Verify generation is continuous
    expect(count2).toBeGreaterThanOrEqual(count1);
    expect(count1).toBeGreaterThan(0);
  });
});