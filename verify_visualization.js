import { chromium } from 'playwright';

async function verifyVisualization() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    console.log('[TEST] Navigating to http://localhost:8000/stat7threejs.html');
    await page.goto('http://localhost:8000/stat7threejs.html', { waitUntil: 'domcontentloaded', timeout: 30000 });
    
    // Wait for Three.js to load
    console.log('[TEST] Waiting for Three.js library...');
    await page.waitForFunction(() => typeof window.THREE !== 'undefined', { timeout: 10000 });
    console.log('âœ“ Three.js loaded');
    
    // Wait for app to initialize
    console.log('[TEST] Waiting for app initialization...');
    await page.waitForFunction(() => typeof window._stat7App !== 'undefined' && window._stat7App.scene, { timeout: 30000, polling: 500 });
    console.log('âœ“ App initialized');
    
    // Give it time for mock mode fallback
    console.log('[TEST] Waiting for mock mode auto-fallback (30s timeout)...');
    await page.waitForTimeout(35000);
    
    // Check if 3D rendering is happening
    const renderingStatus = await page.evaluate(() => {
      const app = window._stat7App;
      const canvas = document.querySelector('canvas');
      return {
        appExists: !!app,
        hasScene: !!app.scene,
        sceneChildren: app.scene?.children?.length || 0,
        entityCount: app.entityMeshes?.size || 0,
        canvasExists: !!canvas,
        canvasWidth: canvas?.width || 0,
        canvasHeight: canvas?.height || 0,
        mockModeEnabled: document.getElementById('toggleMock')?.checked || false,
        connectionState: document.getElementById('conn-state')?.textContent || 'Unknown'
      };
    });
    
    console.log('[RESULT] Rendering Status:');
    console.log('  3D Canvas exists:', renderingStatus.canvasExists);
    console.log('  Canvas dimensions:', renderingStatus.canvasWidth + 'x' + renderingStatus.canvasHeight);
    console.log('  Three.js scene children:', renderingStatus.sceneChildren);
    console.log('  Entities rendered:', renderingStatus.entityCount);
    console.log('  Mock mode enabled:', renderingStatus.mockModeEnabled);
    console.log('  Connection state:', renderingStatus.connectionState);
    
    if (renderingStatus.canvasExists && renderingStatus.entityCount > 0) {
      console.log('\nâœ“âœ“âœ“ SUCCESS: VISUALIZATION IS RENDERING WITH', renderingStatus.entityCount, 'ENTITIES âœ“âœ“âœ“');
    } else {
      console.log('\nâœ—âœ—âœ— PROBLEM: No entities rendered yet âœ—âœ—âœ—');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'visualization-screenshot.png' });
    console.log('âœ“ Screenshot saved to visualization-screenshot.png');
    
  } finally {
    await browser.close();
  }
}

verifyVisualization().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
