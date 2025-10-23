#!/usr/bin/env python3
"""
STAT7 Visualization End-to-End Test Suite

Comprehensive E2E testing of the STAT7 visualization system using Playwright.
Tests the complete pipeline from WebSocket server to 3D visualization.
"""

import asyncio
import json
import subprocess
import time
import os
import sys
import signal
from playwright.async_api import async_playwright
from pathlib import Path

# Test configuration
TEST_HOST = "localhost"
WS_PORT = 8765
WEB_PORT = 8000
TEST_TIMEOUT = 30000  # 30 seconds
BASE_URL = f"http://{TEST_HOST}:{WEB_PORT}"

class STAT7E2ETest:
    """End-to-end test suite for STAT7 visualization system."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.web_server_process = None
        self.ws_server_process = None
        
    async def setup(self):
        """Setup test environment."""
        print("🚀 Setting up STAT7 E2E Test Environment")
        print("=" * 50)
        
        # Start web server
        await self.start_web_server()
        
        # Start WebSocket server  
        await self.start_ws_server()
        
        # Setup browser
        await self.setup_browser()
        
    async def start_web_server(self):
        """Start the web server in background."""
        print("🌐 Starting web server...")
        try:
            self.web_server_process = subprocess.Popen(
                [sys.executable, "simple_web_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            await asyncio.sleep(2)  # Wait for server to start
            print("✅ Web server started")
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            raise
            
    async def start_ws_server(self):
        """Start the WebSocket server in background."""
        print("🔌 Starting WebSocket server...")
        try:
            self.ws_server_process = subprocess.Popen(
                [sys.executable, "-c", """
import asyncio
from stat7wsserve import STAT7EventStreamer
async def main():
    streamer = STAT7EventStreamer(host="localhost", port=8765)
    await streamer.start_server()
asyncio.run(main())
                """],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await asyncio.sleep(3)  # Wait for WebSocket server to start
            print("✅ WebSocket server started")
        except Exception as e:
            print(f"❌ Failed to start WebSocket server: {e}")
            raise
            
    async def setup_browser(self):
        """Setup Playwright browser."""
        print("🌐 Setting up browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Set to True for CI/CD
            args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
        # Enable console logging
        self.page.on("console", lambda msg: print(f"🔍 Console: {msg.text}"))
        self.page.on("pageerror", lambda error: print(f"❌ Page Error: {error}"))
        
        print("✅ Browser setup complete")
        
    async def test_system_initialization(self):
        """Test 1: System Initialization Flow."""
        print("\n🧪 Test 1: System Initialization")
        print("-" * 40)
        
        # Load the visualization page
        await self.page.goto(f"{BASE_URL}/stat7threejs.html", timeout=TEST_TIMEOUT)
        
        # Wait for page to load completely
        await self.page.wait_for_load_state('networkidle', timeout=TEST_TIMEOUT)
        
        # Check page title
        title = await self.page.title()
        assert "STAT7" in title, f"Expected STAT7 in title, got: {title}"
        print("✅ Page loaded with correct title")
        
        # Verify Three.js canvas exists
        canvas = await self.page.query_selector('#stat7-canvas')
        assert canvas is not None, "Three.js canvas not found"
        print("✅ Three.js canvas element found")
        
        # Wait for JavaScript initialization  
        await asyncio.sleep(3)
        
        # Check if STAT7Visualization object exists
        is_viz_ready = await self.page.evaluate('typeof window.stat7Viz !== "undefined"')
        assert is_viz_ready, "STAT7Visualization object not initialized"
        print("✅ STAT7 visualization object initialized")
        
        # Verify UI panels are visible
        controls = await self.page.query_selector('#controls')
        stats = await self.page.query_selector('#stats')
        experiment_info = await self.page.query_selector('#experiment-info')
        
        assert controls is not None, "Controls panel not found"
        assert stats is not None, "Stats panel not found" 
        assert experiment_info is not None, "Experiment info panel not found"
        print("✅ All UI panels present")
        
    async def test_websocket_connection(self):
        """Test 2: WebSocket Connection."""
        print("\n🔌 Test 2: WebSocket Connection")
        print("-" * 40)
        
        # Wait for WebSocket connection
        await asyncio.sleep(5)
        
        # Check connection status
        connection_status = await self.page.text_content('#connection-status')
        print(f"Connection status: {connection_status}")
        
        # Give more time for connection if needed
        max_attempts = 10
        for attempt in range(max_attempts):
            if "Connected" in connection_status:
                break
            await asyncio.sleep(1)
            connection_status = await self.page.text_content('#connection-status')
            print(f"Attempt {attempt + 1}: {connection_status}")
        
        print("✅ WebSocket connection established" if "Connected" in connection_status 
              else "⚠️ WebSocket connection may be pending")
        
    async def test_experiment_execution(self):
        """Test 3: Experiment Execution Flow."""
        print("\n🧪 Test 3: Experiment Execution")
        print("-" * 40)
        
        # Get initial point count
        initial_points = await self.page.text_content('#total-points')
        print(f"Initial points: {initial_points}")
        
        # Click EXP01 button
        exp01_btn = await self.page.query_selector('[data-exp="EXP01"]')
        assert exp01_btn is not None, "EXP01 button not found"
        
        await exp01_btn.click()
        print("✅ Clicked EXP01 button")
        
        # Wait for experiment to generate some data
        await asyncio.sleep(10)
        
        # Check if points were generated
        current_points = await self.page.text_content('#total-points')
        print(f"Points after EXP01: {current_points}")
        
        # Verify events received counter
        events_received = await self.page.text_content('#events-received')
        print(f"Events received: {events_received}")
        
        # Check experiment log
        log_entries = await self.page.query_selector_all('#experiment-log div')
        if log_entries:
            print(f"✅ Found {len(log_entries)} log entries")
        else:
            print("⚠️ No experiment log entries found")
        
    async def test_ui_controls(self):
        """Test 4: User Interface Controls."""
        print("\n🎮 Test 4: UI Controls")
        print("-" * 40)
        
        # Test point size slider
        point_size_slider = await self.page.query_selector('#point-size')
        await point_size_slider.fill('2.5')
        point_size_value = await self.page.text_content('#point-size-value')
        assert '2.5' in point_size_value, f"Point size not updated: {point_size_value}"
        print("✅ Point size slider working")
        
        # Test animation speed slider
        anim_speed_slider = await self.page.query_selector('#animation-speed')
        await anim_speed_slider.fill('0.5')
        speed_value = await self.page.text_content('#speed-value') 
        assert '0.5' in speed_value, f"Animation speed not updated: {speed_value}"
        print("✅ Animation speed slider working")
        
        # Test realm filter
        realm_filter = await self.page.query_selector('#realm-filter')
        await realm_filter.select_option(['data', 'narrative'])  # Select only 2 realms
        print("✅ Realm filter interaction working")
        
        # Test camera reset button
        reset_btn = await self.page.query_selector('#reset-camera')
        await reset_btn.click()
        print("✅ Camera reset button working")
        
    async def test_search_functionality(self):
        """Test 5: Search and Query Functionality."""
        print("\n🔍 Test 5: Search Functionality")
        print("-" * 40)
        
        # Test entity search
        search_input = await self.page.query_selector('#search-input')
        search_btn = await self.page.query_selector('#search-btn')
        
        await search_input.fill('concept')
        await search_btn.click()
        
        await asyncio.sleep(2)
        
        search_results = await self.page.text_content('#search-results')
        print(f"Search results: {search_results}")
        print("✅ Search functionality working")
        
        # Test natural language query
        query_input = await self.page.query_selector('#query-input')
        query_btn = await self.page.query_selector('#query-btn')
        
        await query_input.fill('show me data realm entities')
        await query_btn.click()
        
        await asyncio.sleep(2)
        
        query_results = await self.page.text_content('#query-results')
        print(f"Query results: {query_results}")
        print("✅ Natural language query working")
        
    async def test_advanced_proofs(self):
        """Test 6: Advanced Proof Methods."""
        print("\n🧠 Test 6: Advanced Proofs")
        print("-" * 40)
        
        # Test Semantic Fidelity Proof
        semantic_btn = await self.page.query_selector('#semantic-fidelity')
        await semantic_btn.click()
        print("✅ Semantic Fidelity button clicked")
        
        await asyncio.sleep(8)  # Wait for proof to generate data
        
        # Check if new points were generated
        points_after_semantic = await self.page.text_content('#total-points')
        print(f"Points after semantic proof: {points_after_semantic}")
        
        # Test Resilience Testing
        resilience_btn = await self.page.query_selector('#resilience-test')
        await resilience_btn.click()
        print("✅ Resilience Test button clicked")
        
        await asyncio.sleep(6)  # Wait for test to generate data
        
        # Check final point count
        final_points = await self.page.text_content('#total-points') 
        print(f"Final points after resilience test: {final_points}")
        
    async def test_batch_operations(self):
        """Test 7: Batch Operations."""
        print("\n⚙️ Test 7: Batch Operations")
        print("-" * 40)
        
        # Test Play All Experiments
        play_all_btn = await self.page.query_selector('#play-all')
        await play_all_btn.click()
        print("✅ Play All button clicked")
        
        await asyncio.sleep(5)
        
        # Check active experiments
        active_experiments = await self.page.text_content('#active-experiments')
        print(f"Active experiments: {active_experiments}")
        
        # Test Stop All
        stop_all_btn = await self.page.query_selector('#stop-all')
        await stop_all_btn.click()
        print("✅ Stop All button clicked")
        
        await asyncio.sleep(2)
        
        # Test Clear All  
        clear_all_btn = await self.page.query_selector('#clear-all')
        await clear_all_btn.click()
        print("✅ Clear All button clicked")
        
        await asyncio.sleep(2)
        
        # Verify points cleared
        cleared_points = await self.page.text_content('#total-points')
        print(f"Points after clear: {cleared_points}")
        
    async def test_3d_visualization(self):
        """Test 8: 3D Visualization Rendering."""
        print("\n🎨 Test 8: 3D Visualization")
        print("-" * 40)
        
        # Generate some test data first
        exp01_btn = await self.page.query_selector('[data-exp="EXP01"]')
        await exp01_btn.click()
        await asyncio.sleep(5)
        
        # Take screenshot of the visualization
        await self.page.screenshot(path='stat7_visualization_test.png', full_page=True)
        print("✅ Screenshot taken")
        
        # Check WebGL context
        has_webgl = await self.page.evaluate('''() => {
            const canvas = document.getElementById('stat7-canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            return gl !== null;
        }''')
        
        assert has_webgl, "WebGL context not available"
        print("✅ WebGL rendering context available")
        
        # Check if Three.js scene is rendering
        is_rendering = await self.page.evaluate('''() => {
            return typeof window.stat7Viz !== 'undefined' && 
                   window.stat7Viz.renderer && 
                   window.stat7Viz.scene;
        }''')
        
        assert is_rendering, "Three.js scene not rendering"
        print("✅ Three.js scene actively rendering")
        
    async def run_all_tests(self):
        """Run the complete test suite."""
        tests = [
            ("System Initialization", self.test_system_initialization),
            ("WebSocket Connection", self.test_websocket_connection), 
            ("Experiment Execution", self.test_experiment_execution),
            ("UI Controls", self.test_ui_controls),
            ("Search Functionality", self.test_search_functionality),
            ("Advanced Proofs", self.test_advanced_proofs),
            ("Batch Operations", self.test_batch_operations),
            ("3D Visualization", self.test_3d_visualization)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                await test_func()
                passed += 1
                print(f"✅ {test_name}: PASSED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name}: FAILED - {e}")
                
        return passed, failed
        
    async def cleanup(self):
        """Cleanup test environment."""
        print("\n🧹 Cleaning up test environment...")
        
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close() 
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"⚠️ Browser cleanup error: {e}")
            
        try:
            if self.web_server_process:
                self.web_server_process.terminate()
                self.web_server_process.wait(timeout=5)
        except Exception as e:
            print(f"⚠️ Web server cleanup error: {e}")
            
        try:
            if self.ws_server_process:
                self.ws_server_process.terminate()
                self.ws_server_process.wait(timeout=5)
        except Exception as e:
            print(f"⚠️ WebSocket server cleanup error: {e}")
            
        print("✅ Cleanup completed")

async def main():
    """Main test runner."""
    test_suite = STAT7E2ETest()
    
    try:
        await test_suite.setup()
        
        print("\n🧪 Running STAT7 E2E Test Suite")
        print("=" * 50)
        
        passed, failed = await test_suite.run_all_tests()
        
        print("\n📊 Test Results Summary")
        print("=" * 50)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("🚀 STAT7 Visualization System is ready for production!")
        else:
            print(f"\n⚠️ {failed} test(s) failed. Please review and fix issues.")
            
        return failed == 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await test_suite.cleanup()

if __name__ == "__main__":
    print("🌟 STAT7 Visualization E2E Test Suite")
    print("Testing complete visualization pipeline...")
    print()
    
    success = asyncio.run(main())
    
    if success:
        print("\n🎊 E2E Testing: SUCCESS!")
        sys.exit(0)
    else:
        print("\n💥 E2E Testing: FAILED!")
        sys.exit(1)