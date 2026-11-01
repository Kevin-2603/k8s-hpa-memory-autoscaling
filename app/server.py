from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import json
import threading

allocations = []
allocated_mb = 0
lock = threading.Lock()

MAX_HELD_MB = 100


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        global allocated_mb, allocations

        parsed = urlparse(self.path)

        if parsed.path == "/health":
            return self.respond(200, {"status": "healthy"})

        if parsed.path == "/allocate":
            params = parse_qs(parsed.query)

            try:
                mb = int(params.get("mb", ["10"])[0])
            except ValueError:
                return self.respond(400, {"error": "Invalid memory size"})

            if mb < 1 or mb > 10:
                return self.respond(400, {"error": "Use 1-10 MB per request"})

            with lock:
                if allocated_mb + mb > MAX_HELD_MB:
                    return self.respond(429, {
                        "error": "Memory allocation limit reached",
                        "allocated_mb": allocated_mb
                    })

                block = bytearray(mb * 1024 * 1024)

                for i in range(0, len(block), 4096):
                    block[i] = 1

                allocations.append(block)
                allocated_mb += mb

                return self.respond(200, {
                    "allocated_mb": allocated_mb,
                    "max_held_mb": MAX_HELD_MB
                })

        if parsed.path == "/reset":
            with lock:
                allocations.clear()
                allocated_mb = 0

            return self.respond(200, {"allocated_mb": 0})

        if parsed.path == "/":
            return self.respond(200, {
                "application": "kubernetes-memory-autoscaling",
                "endpoints": ["/health", "/allocate?mb=10", "/reset"]
            })

        return self.respond(404, {"error": "Not found"})


server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
print("Memory workload server listening on port 8080", flush=True)
server.serve_forever()
