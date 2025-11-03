import { test, expect, chromium } from '@playwright/test';
import { spawn } from 'child_process';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';
import * as fs from 'fs';

const execAsync = promisify(exec);
const projectRoot = path.join(__dirname, '../..');

test('Diagnose visualization rendering pipeline', async () => {
  // Start the launcher script
  console.log('[DIAG] Starting servers...');
  
  const launcher = spawn('python', ['web/launchers/full_auto_launch.py'], {
    cwd: projectRoot,
    stdio: 'pipe'
  });

  // Collect launcher output
  let launcherOutput = '';
  launcher.stdout.on('data', (data) => {
    const msg = data.toString();
    console.log('[LAUNCHER]', msg.trim());
    launcherOutput += msg;
  });
  launcher.stderr.on('data', (data) => {
    console.log('[LAUNCHER ERROR]', data.toString().trim());
  });

  // Wait for servers to start
  console.log('[DIAG] Waiting 6 seconds for servers to start...');
  await new Promise(r => setTimeout(r, 6000));

  let browser;
  try {
    // Open browser
    browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    // Listen for console messages
    page.on('console', (msg) => {
      console.log(`[BROWSER-${msg.type().toUpperCase()}]`, msg.text());
    });

    // Listen for errors
    page.on('error', (err) => {
      console.log('[BROWSER-ERROR]', err.message);
    });

    page.on('pageerror', (err) => {
      console.log('[PAGE-ERROR]', err.message);
    });

    // Open the visualization
    console.log('[DIAG] Opening http://localhost:8000/stat7threejs.html...');
    const response = await page.goto('http://localhost:8000/stat7threejs.html', {
      waitUntil: 'networkidle',
      timeout: 10000
    });

    console.log(`[DIAG] Response status: ${response?.status()}`);

    // Wait a moment for scripts to initialize
    await new Promise(r => setTimeout(r, 3000));

    // Run diagnostic checks
    console.log('[DIAG] Running diagnostic checks...\n');

    // Check 1: WebSocket
    console.log('=== CHECK 1: WebSocket Connection ===');
    const wsState = await page.evaluate(() => {
      if ((window as any).ws) {
        return {
          exists: true,
          readyState: (window as any).ws.readyState,
          readyStateStr: ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'][(window as any).ws.readyState],
          url: (window as any).ws.url
        };
      }
      return { exists: false };
    });
    console.log(JSON.stringify(wsState, null, 2));

    // Check 2: Three.js Scene
    console.log('\n=== CHECK 2: Three.js Scene ===');
    const sceneState = await page.evaluate(() => {
      return {
        sceneExists: !!(window as any).scene,
        rendererExists: !!(window as any).renderer,
        THREEExists: !!(window as any).THREE,
        canvasElement: document.querySelector('canvas') ? 'YES' : 'NO',
        canvasVisible: document.querySelector('canvas') ? 
          `${(document.querySelector('canvas') as any).offsetWidth}x${(document.querySelector('canvas') as any).offsetHeight}` : 
          'N/A'
      };
    });
    console.log(JSON.stringify(sceneState, null, 2));

    // Check 3: Entity Meshes
    console.log('\n=== CHECK 3: Entity Meshes ===');
    const meshState = await page.evaluate(() => {
      const app = (window as any)._stat7App;
      return {
        appExists: !!app,
        meshCount: app?.entityMeshes?.size || 0,
        sceneChildrenCount: (window as any).scene?.children.length || 0
      };
    });
    console.log(JSON.stringify(meshState, null, 2));

    // Check 4: Data Service
    console.log('\n=== CHECK 4: Data Service ===');
    const dataState = await page.evaluate(() => {
      return {
        configExists: !!(window as any).Config,
        mockModeEnabled: (document.getElementById('toggleMock') as any)?.checked || false,
        connectionState: 'Check HUD'
      };
    });
    console.log(JSON.stringify(dataState, null, 2));

    // Check 5: HUD Status
    console.log('\n=== CHECK 5: HUD Status ===');
    const hudState = await page.evaluate(() => {
      return {
        fps: document.getElementById('fps')?.textContent || 'N/A',
        msgs: document.getElementById('throughput')?.textContent || 'N/A',
        latency: document.getElementById('latency')?.textContent || 'N/A',
        entities: document.getElementById('entities')?.textContent || 'N/A',
        connection: document.getElementById('conn-state')?.textContent || 'N/A'
      };
    });
    console.log(JSON.stringify(hudState, null, 2));

    // Screenshot for visual inspection
    console.log('\n[DIAG] Taking screenshot...');
    const timestamp = Date.now();
    const screenshotPath = path.join(projectRoot, `diagnostic_${timestamp}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`[DIAG] Screenshot saved to: ${screenshotPath}`);

    // Keep browser open for 10 seconds for manual inspection
    console.log('\n[DIAG] Browser will stay open for 10 seconds...');
    await new Promise(r => setTimeout(r, 10000));

    await context.close();
  } finally {
    // Close browser
    if (browser) {
      await browser.close();
    }

    // Stop servers
    console.log('\n[DIAG] Stopping servers...');
    launcher.kill('SIGTERM');
  }
});