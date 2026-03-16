#!/usr/bin/env python3
"""
Simple HTTP server for the AI Learning Tutor Frontend
Run this to serve the HTML/CSS/JS frontend separately
"""
import http.server
import socketserver
import os
import sys

PORT = 3000
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"\n🎓 AI Learning Tutor Frontend")
        print(f"="*40)
        print(f"Server running at: http://localhost:{PORT}")
        print(f"Serving files from: {FRONTEND_DIR}")
        print(f"\nMake sure the FastAPI backend is running on port 8000")
        print(f"Press Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            sys.exit(0)

if __name__ == "__main__":
    main()
