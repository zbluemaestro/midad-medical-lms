import os
import sys
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Ensure proper mime types
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/pdf", ".pdf")
mimetypes.add_type("video/mp4", ".mp4")

class MidadHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        elif self.path.startswith("/static/"):
            self.path = self.path[7:] # Strip /static
        return super().do_GET()

    def end_headers(self):
        # Add CORS and security headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

def run_server(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, MidadHTTPHandler)
    print("==========================================================")
    print(f" Midad Medical LMS - Modernized Preview Running!")
    print(f" Access URL: http://localhost:{port}")
    print(f" Static Dir: {STATIC_DIR}")
    print(" Press Ctrl+C to stop the preview server.")
    print("==========================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down Midad preview server.")
        httpd.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(p)
