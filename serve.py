"""Serve the web app locally and open it in your browser.

Browsers block ES modules and model downloads when a page is opened by
double-clicking the file, so run this instead:   python serve.py
"""
import http.server
import os
import socketserver
import webbrowser

# Ensure working directory is the finshield directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".js": "text/javascript", ".mjs": "text/javascript"}

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}/index.html"
    print(f"FinShield running at {url}  (press Ctrl+C to stop)")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
