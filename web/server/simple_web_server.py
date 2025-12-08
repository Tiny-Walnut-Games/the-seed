#!/usr/bin/env python3
"""
Simple STAT7 Visualization Launcher - Fallback Solution

This version uses Python's built-in HTTP server and handles port conflicts gracefully.
"""

import os
import sys
import webbrowser
import time
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver
from pathlib import Path

class CustomHandler(SimpleHTTPRequestHandler):
    """Custom handler with CORS support."""

    def __init__(self, *args, **kwargs):
        # Serve from the web directory (parent of server directory)
        web_dir = os.path.dirname(os.path.dirname(__file__))
        super().__init__(*args, directory=web_dir, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/stat7threejs.html'
        return super().do_GET()

def find_free_port(start_port=8000):
    """Find a free port starting from start_port."""
    import socket
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def main():
    """Simple launcher."""
    print("🚀 STAT7 Visualization Launcher")
    print("=" * 40)

    # Change to web directory for file checks
    web_dir = os.path.dirname(os.path.dirname(__file__))
    os.chdir(web_dir)

    # Check if required files exist
    required_files = ['stat7threejs.html', 'server/stat7wsserve.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file not found: {file}")
            return

    # Find free port
    port = find_free_port()
    if not port:
        print("❌ Could not find a free port")
        return

    print(f"🌐 Starting web server on port {port}...")

    # Start HTTP server
    try:
        with socketserver.TCPServer(("", port), CustomHandler) as httpd:
            url = f"http://localhost:{port}/stat7threejs.html"
            print(f"✅ Web server started!")
            print(f"📊 Open your browser to: {url}")

            # Open browser
            try:
                webbrowser.open(url)
                print("🌐 Opening browser automatically...")
            except:
                print("⚠️ Could not open browser automatically")

            print("\n" + "=" * 40)
            print("📋 Next Steps:")
            print(f"1. Your browser should open to: {url}")
            print("2. In a SEPARATE terminal, run:")
            print("   python stat7wsserve.py")
            print("3. Then type 'exp01' or 'continuous' in the WebSocket server")
            print("4. Press Ctrl+C here to stop the web server")
            print("=" * 40)

            # Keep server running
            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n👋 Web server stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
