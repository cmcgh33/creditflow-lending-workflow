"""Loopback-only local demonstration server; Python standard library only."""
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from .engine import evaluate, ValidationError, POLICY
from .storage import Store
WEB = Path(__file__).resolve().parent.parent / "web"

class Handler(BaseHTTPRequestHandler):
    def send_body(self, status, body, content_type="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = json.dumps(body, allow_nan=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/policy":
            return self.send_body(200, POLICY)
        if path == "/api/evaluations":
            return self.send_body(200, {"items": self.server.store.list(), "limit": 100})
        if path.startswith("/api/evaluations/"):
            record = self.server.store.get(path.rsplit("/", 1)[1])
            return self.send_body(200, record) if record else self.send_body(404, {"error": "Evaluation not found"})
        files = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8")}
        if path in files:
            name, mime = files[path]
            return self.send_body(200, (WEB / name).read_bytes(), mime)
        return self.send_body(404, {"error": "Not found"})
    def do_POST(self):
        if urlparse(self.path).path != "/api/evaluations":
            return self.send_body(404, {"error": "Not found"})
        # Block cross-origin browser writes; this demo has no authentication.
        if self.headers.get("Origin") and self.headers["Origin"] != f"http://{self.headers.get('Host')}":
            return self.send_body(403, {"error": "Cross-origin writes are not allowed"})
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            return self.send_body(415, {"error": "Use application/json"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                return self.send_body(413, {"error": "Provide a JSON body of 1–8192 bytes"})
            payload = json.loads(self.rfile.read(size), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        except (ValueError, UnicodeDecodeError):
            return self.send_body(400, {"error": "Malformed JSON"})
        try:
            record = self.server.store.save(evaluate(payload))
        except ValidationError as exc:
            return self.send_body(422, {"error": "Invalid application", "fields": exc.errors})
        return self.send_body(201, record)
    def log_message(self, fmt, *args):
        # Never log application bodies or borrower names.
        super().log_message(fmt, *args)

def make_server(port=8000, db_path="data/creditflow.sqlite3"):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.store = Store(db_path)
    return server

def main():
    parser = argparse.ArgumentParser(description="Run the local CreditFlow demo")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", default=os.environ.get("CREDITFLOW_DB", "data/creditflow.sqlite3"))
    args = parser.parse_args()
    server = make_server(args.port, args.db)
    print(f"CreditFlow → http://127.0.0.1:{server.server_port} (Ctrl+C to stop)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
