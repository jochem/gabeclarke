#!/usr/bin/env python3
"""
Simple HTTP server to preview the static export locally.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# Port: first CLI arg, else $PORT env, else 8000
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT', 8000))
OUTPUT_DIR = Path('output').resolve()

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(OUTPUT_DIR), **kwargs)
    
    def end_headers(self):
        # Add CORS headers for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == '__main__':
    if not OUTPUT_DIR.exists():
        print(f"Error: {OUTPUT_DIR} directory not found!")
        print("Please run export-static.py first to generate the static site.")
        exit(1)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Preview server running at http://localhost:{PORT}/")
        print(f"Serving files from {OUTPUT_DIR.absolute()}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")




