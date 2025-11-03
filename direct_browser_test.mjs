import { chromium } from 'playwright';

async function runDirectBrowserTest() {
  const browser = await chromium.launch({ headless: false }); // Not headless so you can see it
  const page = await browser.newPage();
  
  console.log('Opening visualization page...');
  await page.goto('http://localhost:8000/stat7threejs.html', { waitUntil: 'domcontentloaded', timeout: 60000 });
  
  // Collect all console output
  page.on('console', msg => {
    console.log(`[BROWSER] ${msg.type()}: ${msg.text()}`);
  });
  
  // Wait for Three.js
  console.log('Waiting for Three.js library...');
  await page.waitForFunction(() => typeof window.THREE !== 'undefined', { timeout: 10000 });
  console.log('✓ Three.js available');
  
  // Wait for app object
  console.log('Waiting for app initialization...');
  await page.waitForFunction(
    () => typeof window._stat7App !== 'undefined' && window._stat7App.scene,
    { timeout: 30000, polling: 500 }
  );
  console.log('✓ App initialized with scene');
  
  // Now wait for mock mode auto-fallback (up to 35 seconds)
  console.log('\n' + '='.repeat(60));
  console.log('WAITING FOR MOCK MODE AUTO-FALLBACK (30-35 seconds)');
  console.log('='.repeat(60));
  
  for (let i = 0; i < 40; i++) {
    await new Promise(r => setTimeout(r, 1000));
    
    const status = await page.evaluate(() => {
      const app = window._stat7App;
      const canvas = document.querySelector('canvas');
      return {
        mockEnabled: document.getElementById('toggleMock')?.checked || false,
        connState: document.getElementById('conn-state')?.textContent || 'Unknown',
        entityCount: app.entityMeshes?.size || 0,
        sceneChildren: app.scene?.children?.length || 0,
        canvasExists: !!canvas,
        canvasWidth: canvas?.width || 0,
        canvasHeight: canvas?.height || 0,
      };
    });
    
    console.log(`[${i}s] Mock: ${status.mockEnabled ? 'ON' : 'OFF'} | State: ${status.connState} | Entities: ${status.entityCount} | Scene children: ${status.sceneChildren}`);
    
    if (status.mockEnabled && status.entityCount > 0 && status.sceneChildren > 0) {
      console.log('\n✓✓✓ SUCCESS! Mock mode engaged and rendering entities ✓✓✓\n');
      break;
    }
  }
  
  // Final detailed status
  const finalStatus = await page.evaluate(() => {
    const app = window._stat7App;
    const canvas = document.querySelector('canvas');
    const meshes = [];
    
    for (const [id, mesh] of app.entityMeshes.entries()) {
      meshes.push({
        id,
        type: mesh.userData?.entityType,
        realm: mesh.userData?.realm,
        position: { x: mesh.position.x, y: mesh.position.y, z: mesh.position.z },
      });
    }
    
    return {
      appExists: !!app,
      sceneExists: !!app.scene,
      sceneChildren: app.scene?.children?.length || 0,
      entityCount: app.entityMeshes?.size || 0,
      canvasWidth: canvas?.width || 0,
      canvasHeight: canvas?.height || 0,
      mockEnabled: document.getElementById('toggleMock')?.checked || false,
      connectionState: document.getElementById('conn-state')?.textContent || 'Unknown',
      meshSamples: meshes.slice(0, 5),
    };
  });
  
  console.log('\nFinal Status:');
  console.log(JSON.stringify(finalStatus, null, 2));
  
  // Keep browser open for 10 more seconds so you can see it
  console.log('\nBrowser will stay open for 10 more seconds so you can view the visualization...');
  await new Promise(r => setTimeout(r, 10000));
  
  await browser.close();
}

runDirectBrowserTest().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});