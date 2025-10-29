#!/usr/bin/env python3
import os
import sys
import socketserver
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

class CustomHandler(SimpleHTTPRequestHandler):
    """Custom handler with CORS support."""
    def __init__(self, *args, **kwargs):
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
    import socket
    for port in range(start_port, start_port + 20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

if __name__ == '__main__':
    port = find_free_port()
    if not port:
        print("ERROR: Could not find free port")
        sys.exit(1)
    
    print(f"Starting HTTP server on port {port}")
    print(f"Visit http://localhost:{port}/stat7threejs.html")
    
    try:
        with socketserver.TCPServer(("127.0.0.1", port), CustomHandler) as httpd:
            print(f"Server running on port {port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)